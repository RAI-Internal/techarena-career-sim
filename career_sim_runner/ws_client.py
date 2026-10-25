"""Drive JiuwenSwarm AgentServer over WebSocket."""

import asyncio
import json
import re
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import websockets

from career_sim_runner.constants import EMULATOR_MCP_SERVER_NAME, EMULATOR_MCP_TOOL_PREFIX, SUPPORTED_RUN_MODES
from career_sim_runner.models import InstallRecord, TokenUsage
from career_sim_runner.skill_contract import SubmissionError
from career_sim_runner.transcript import EventCallback, StreamCollector, _walk

SESSION_ID_RE = re.compile(r"SESSION_ID=([0-9a-fA-F]{8,})")
MAX_CONTINUATIONS = 20
_CAREER_MCP_PREFIX = EMULATOR_MCP_TOOL_PREFIX
_GAME_OVER_PREFIX = "GAME OVER:"


@dataclass
class DriveResult:
    """Outcome of one WebSocket play session."""

    exit_code: int
    termination_reason: str | None
    session_id: str | None
    token_usage: TokenUsage
    transcript: str
    events_path: Path
    transcript_path: Path


@dataclass
class _GameState:
    """Accumulated game state extracted from structured MCP tool results."""

    session_id: str | None = None
    alive: bool = True
    failed: bool = False
    game_over: bool = False
    last_month: int | None = None
    last_year: int | None = None

    @property
    def ended(self) -> bool:
        """Return whether the game has reached a terminal state."""
        return self.game_over or not self.alive or self.failed


def _parse_tool_result_payload(raw_output: dict[str, Any]) -> dict[str, Any] | None:
    """Parse the inner JSON result from a tool's raw_output."""
    result_str = raw_output.get("result")
    if isinstance(result_str, str):
        try:
            return json.loads(result_str)
        except (json.JSONDecodeError, ValueError):
            return None
    if isinstance(result_str, dict):
        return result_str
    return None


def _extract_game_signals(frame: dict[str, Any], state: _GameState) -> None:
    """Walk a frame and update game state from MCP tool result payloads."""
    for node in _walk(frame):
        if node.get("event_type") != "chat.tool_result":
            continue
        tool_name = str(node.get("tool_name") or "")
        if not tool_name.startswith(_CAREER_MCP_PREFIX):
            continue
        raw_output = node.get("raw_output")
        if not isinstance(raw_output, dict):
            continue
        parsed = _parse_tool_result_payload(raw_output)
        if parsed is None:
            continue

        action = tool_name[len(_CAREER_MCP_PREFIX) :]

        if action == "new_game":
            sid = parsed.get("session_id")
            if isinstance(sid, str) and sid:
                state.session_id = sid

        elif action == "observe":
            current_state = parsed.get("current_state") or {}
            sid = current_state.get("session_id") or parsed.get("session_id")
            if isinstance(sid, str) and sid:
                state.session_id = sid
            time_info = current_state.get("time") or {}
            if isinstance(time_info.get("current_month"), int):
                state.last_month = time_info["current_month"]
            if isinstance(time_info.get("current_year"), int):
                state.last_year = time_info["current_year"]
            flags = current_state.get("simulation_flags") or {}
            if (flags.get("alive") is False) or (flags.get("failed") is True):
                state.game_over = True

        elif action == "take_action":
            if parsed.get("success") is False:
                error_msg = str(parsed.get("error") or "")
                if error_msg.startswith(_GAME_OVER_PREFIX):
                    state.game_over = True

        if state.game_over:
            state.failed = True
            state.alive = False


def build_play_prompt() -> str:
    """Build the prompt used for one headless playthrough."""
    return _load_prompt_template("play_headless.md")


def build_continue_prompt(game: _GameState | None = None) -> str:
    """Build the prompt used to resume an interrupted playthrough."""
    template = _load_prompt_template("play_headless_continue.md")
    if game is None or game.session_id is None:
        return template.replace("{session_id}", "unknown")
    month_str = str(game.last_month) if game.last_month is not None else "?"
    year_str = str(game.last_year) if game.last_year is not None else "?"
    return template.format(
        session_id=game.session_id,
        month=month_str,
        year=year_str,
    )


def _load_prompt_template(name: str) -> str:
    """Load a markdown prompt template shipped with the runner."""
    prompt_path = Path(__file__).resolve().parent / "prompts" / name
    return prompt_path.read_text(encoding="utf-8").strip()


def resolve_run_mode(install_record: InstallRecord) -> str:
    """Return the JiuwenSwarm execution mode requested by the manifest."""
    mode = str(install_record.manifest.get("mode") or "NOT GIVEN").strip()
    if mode in SUPPORTED_RUN_MODES:
        return mode
    raise SubmissionError(
        f"Unsupported JiuwenSwarm agent mode: \033[41m{mode}\033[0m\nSupported modes: {SUPPORTED_RUN_MODES}"
    )


def _build_envelope(prompt: str, session_id: str, mode: str) -> dict[str, Any]:
    """Build one E2A-like WebSocket envelope."""
    return {
        "request_id": f"ws_{uuid.uuid4().hex[:12]}",
        "session_id": session_id,
        "channel": "web",
        "method": "chat.send",
        "params": {
            "content": prompt,
            "query": prompt,
            "mode": mode,
            "work_mode": "work",  # Omitting this may activate legacy code in JiuwenSwarm in rare cases
        },
        "is_stream": True,
    }


async def check_backend(ws_url: str, timeout_s: float = 5.0) -> bool:
    """Return whether the AgentServer WebSocket is reachable."""
    try:
        async with websockets.connect(ws_url, open_timeout=timeout_s, close_timeout=1):
            return True
    except Exception:  # pylint: disable=broad-exception-caught
        return False


async def reload_agent_config(ws_url: str, timeout_s: float = 15.0) -> bool:
    """Send agent.reload_config to trigger skill hot-reload on the running instance."""
    envelope = {
        "request_id": f"reload_{uuid.uuid4().hex[:12]}",
        "session_id": "",
        "channel": "web",
        "method": "agent.reload_config",
        "params": {},
    }
    try:
        async with websockets.connect(ws_url, max_size=None, open_timeout=10) as ws:
            try:
                await asyncio.wait_for(ws.recv(), timeout=3)
            except asyncio.TimeoutError:
                pass
            await ws.send(json.dumps(envelope, ensure_ascii=False))
            deadline = asyncio.get_event_loop().time() + timeout_s
            while asyncio.get_event_loop().time() < deadline:
                try:
                    raw = await asyncio.wait_for(ws.recv(), timeout=timeout_s)
                except asyncio.TimeoutError:
                    break
                try:
                    frame = json.loads(raw)
                except json.JSONDecodeError:
                    continue
                if frame.get("request_id") == envelope["request_id"]:
                    body = frame.get("body", frame)
                    result = body.get("result", body)
                    return bool(str(result.get("reloaded")).lower() in ["true", "1", "yes", "ok"])
    except Exception as e:  # pylint: disable=broad-exception-caught
        raise ConnectionError(
            "\033[41mFailed to reload JiuwenSwarm agent config, is the service started?\033[0m"
        ) from e
    return False


def _has_ended(game: _GameState) -> bool:
    """Return whether the game has reached a terminal state.

    Only structured MCP signals (via ``_GameState``) are authoritative.
    Transcript text is agent-controlled and must not be trusted.
    """
    return game.ended


async def drive(
    ws_url: str,
    prompt: str,
    session_id: str,
    mode: str,
    timeout_s: float,
    log_dir: Path,
    on_event: EventCallback | None = None,
) -> DriveResult:
    """Send one streaming play prompt and collect structured logs.

    :param on_event: Optional callback invoked for each structured event
        record written by the collector (tool_call, tool_result, usage, etc.).
    """
    collector = StreamCollector(log_dir=log_dir, on_event=on_event)
    game = _GameState()
    exit_code = 0
    termination_reason: str | None = None
    skip_next_e2a_complete = False

    async with websockets.connect(ws_url, max_size=None, open_timeout=10) as ws:
        try:
            await asyncio.wait_for(ws.recv(), timeout=5)
        except asyncio.TimeoutError:
            pass

        envelope = _build_envelope(prompt, session_id, mode)
        await ws.send(json.dumps(envelope, ensure_ascii=False))

        loop = asyncio.get_event_loop()
        deadline = loop.time() + timeout_s
        continuations = 0

        while loop.time() < deadline:
            try:
                raw = await asyncio.wait_for(ws.recv(), timeout=min(60.0, deadline - loop.time()))
            except asyncio.TimeoutError:
                continue

            try:
                frame = json.loads(raw)
            except json.JSONDecodeError:
                collector.feed_frame({"body": {"text": raw}})
                continue

            collector.feed_frame(frame)
            _extract_game_signals(frame, game)

            kind = str(frame.get("response_kind") or "")
            status = str(frame.get("status") or "")
            is_final = bool(frame.get("is_final"))

            if kind == "e2a.error" or status == "failed":
                exit_code = 1
                break

            if is_final and kind in {"e2a.complete", "e2a.error"}:
                if skip_next_e2a_complete:
                    skip_next_e2a_complete = False
                    continue
                if _has_ended(game):
                    break
                if continuations >= MAX_CONTINUATIONS:
                    termination_reason = "max_continuations"
                    break
                continuations += 1
                cont_prompt = build_continue_prompt(game)
                cont_envelope = _build_envelope(cont_prompt, session_id, mode)
                await ws.send(json.dumps(cont_envelope, ensure_ascii=False))
                skip_next_e2a_complete = True
            else:
                skip_next_e2a_complete = False

    collector.finalize()
    game_session_id = game.session_id
    if game_session_id is None:
        match = SESSION_ID_RE.search(collector.transcript)
        if match:
            game_session_id = match.group(1)

    if exit_code == 0 and not _has_ended(game):
        exit_code = 1

    assert collector.events_path is not None
    assert collector.transcript_path is not None
    return DriveResult(
        exit_code=exit_code,
        termination_reason=termination_reason,
        session_id=game_session_id,
        token_usage=collector.totals,
        transcript=collector.transcript,
        events_path=collector.events_path,
        transcript_path=collector.transcript_path,
    )
