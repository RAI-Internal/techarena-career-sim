"""Parse structured events logs into replay decision turns."""

import json
from pathlib import Path
from typing import Any

from career_sim_runner.replay.models import DecisionTurn, GameChoice, ObserveSnapshot

from career_sim_runner.constants import EMULATOR_MCP_SERVER_NAME, EMULATOR_MCP_TOOL_PREFIX

_CAREER_MCP_PREFIX = EMULATOR_MCP_TOOL_PREFIX


def _payload_node(payload: dict[str, Any]) -> dict[str, Any]:
    """Return the inner event node from one collector payload."""
    if "tool_call" in payload:
        return payload
    delta = payload.get("delta")
    if isinstance(delta, dict):
        return delta
    return payload


def _parse_tool_result_json(payload: dict[str, Any]) -> dict[str, Any] | None:
    """Parse career-emulator JSON from a tool_result payload."""
    raw_output = payload.get("raw_output")
    if not isinstance(raw_output, dict):
        return None
    result = raw_output.get("result")
    if isinstance(result, str):
        try:
            parsed = json.loads(result)
        except json.JSONDecodeError:
            return None
        return parsed if isinstance(parsed, dict) else None
    if isinstance(result, dict):
        return result
    return None


def _parse_observe_snapshot(ts: str, payload: dict[str, Any]) -> ObserveSnapshot | None:
    """Parse one observe tool_result into a snapshot."""
    data = _parse_tool_result_json(payload)
    if data is None:
        return None

    ending_score = data.get("ending_score")
    if isinstance(ending_score, dict) and ending_score:
        state = data.get("current_state", {})
        time_info = state.get("time", {}) if isinstance(state, dict) else {}
        status = state.get("status", {}) if isinstance(state, dict) else {}
        flags = state.get("simulation_flags", {}) if isinstance(state, dict) else {}
        return ObserveSnapshot(
            ts=ts,
            month=int(time_info.get("current_month", 0) or 0),
            quarter=int(time_info.get("current_quarter", 0) or 0),
            year=int(time_info.get("current_year", 0) or 0),
            status=dict(status) if isinstance(status, dict) else {},
            event_title="Game over",
            event_description="",
            month_feed="",
            ending_score=ending_score,
            alive=bool(flags.get("alive", True)),
            failed=bool(flags.get("failed", False)),
            failure_reason=flags.get("failure_reason"),
        )

    state = data.get("current_state", {})
    if not isinstance(state, dict):
        return None
    time_info = state.get("time", {})
    status = state.get("status", {})
    flags = state.get("simulation_flags", {})
    event = data.get("current_event", {})
    if not isinstance(time_info, dict) or not isinstance(status, dict) or not isinstance(event, dict):
        return None

    choices: list[GameChoice] = []
    for item in data.get("choices", []):
        if not isinstance(item, dict):
            continue
        choices.append(
            GameChoice(
                choice=int(item.get("choice", 0) or 0),
                action=str(item.get("action", "")),
                description=str(item.get("description", "") or ""),
            )
        )

    return ObserveSnapshot(
        ts=ts,
        month=int(time_info.get("current_month", 0) or 0),
        quarter=int(time_info.get("current_quarter", 0) or 0),
        year=int(time_info.get("current_year", 0) or 0),
        status=dict(status),
        event_title=str(event.get("title", "")),
        event_description=str(event.get("description", "")),
        month_feed=str(data.get("events", "") or ""),
        choices=choices,
        alive=bool(flags.get("alive", True)),
        failed=bool(flags.get("failed", False)),
        failure_reason=flags.get("failure_reason"),
    )


def _parse_take_action_call(payload: dict[str, Any]) -> tuple[int, str] | None:
    """Parse choice number and notes from one take_action tool_call."""
    node = _payload_node(payload)
    tool_call = node.get("tool_call")
    if not isinstance(tool_call, dict):
        return None
    name = str(tool_call.get("name", ""))
    if not name.endswith("take_action"):
        return None
    arguments = tool_call.get("arguments", "{}")
    if isinstance(arguments, dict):
        args = arguments
    else:
        try:
            args = json.loads(str(arguments))
        except json.JSONDecodeError:
            return None
    choice = int(args.get("choice", 0) or 0)
    notes = str(args.get("notes", "") or "")
    return choice, notes


def parse_events_log(events_path: Path) -> tuple[str | None, list[DecisionTurn], list[str]]:
    """Parse one events JSONL file into session metadata and decision turns.

    :param events_path: Path to the events ``.jsonl`` log file.
    :return: A tuple of ``(session_id, turns, misc_calls)``.
    """
    session_id: str | None = None
    turns: list[DecisionTurn] = []
    misc_calls: list[str] = []
    seen_result_ids: set[str] = set()
    seen_call_ids: set[str] = set()
    pending_observe: ObserveSnapshot | None = None

    for line in events_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        record = json.loads(line)
        kind = str(record.get("kind", ""))
        ts = str(record.get("ts", ""))
        payload = record.get("payload", {})
        if not isinstance(payload, dict):
            continue

        if kind == "tool_result":
            tool_call_id = str(payload.get("tool_call_id", "") or "")
            if not tool_call_id or tool_call_id in seen_result_ids:
                continue
            tool_name = str(payload.get("tool_name", "") or "")
            if _CAREER_MCP_PREFIX not in tool_name and EMULATOR_MCP_SERVER_NAME not in tool_name:
                node = payload.get("delta", payload)
                if isinstance(node, dict):
                    tool_name = str(node.get("tool_name", "") or tool_name)
            if "new_game" in tool_name:
                data = _parse_tool_result_json(payload)
                if isinstance(data, dict) and data.get("session_id"):
                    session_id = str(data["session_id"])
                seen_result_ids.add(tool_call_id)
                continue
            if "observe" in tool_name:
                snapshot = _parse_observe_snapshot(ts, payload)
                if snapshot is not None:
                    pending_observe = snapshot
                seen_result_ids.add(tool_call_id)
            continue

        if kind == "tool_call":
            node = _payload_node(payload)
            tool_call = node.get("tool_call")
            if not isinstance(tool_call, dict):
                continue
            tool_call_id = str(tool_call.get("tool_call_id", "") or "")
            if not tool_call_id or tool_call_id in seen_call_ids:
                continue
            name = str(tool_call.get("name", ""))
            if "take_action" in name:
                parsed = _parse_take_action_call(payload)
                if parsed is None or pending_observe is None:
                    seen_call_ids.add(tool_call_id)
                    continue
                choice, notes = parsed
                choice_action = ""
                for option in pending_observe.choices:
                    if option.choice == choice:
                        choice_action = option.action
                        break
                turns.append(
                    DecisionTurn(
                        step=len(turns) + 1,
                        observe=pending_observe,
                        choice=choice,
                        choice_action=choice_action,
                        notes=notes,
                    )
                )
                pending_observe = None
                seen_call_ids.add(tool_call_id)
                continue
            if name.startswith(_CAREER_MCP_PREFIX) or EMULATOR_MCP_SERVER_NAME in name:
                short_name = name.removeprefix(_CAREER_MCP_PREFIX)
                if short_name not in {"observe", "take_action", "new_game", "show_employee_handbook"}:
                    misc_calls.append(short_name)
                seen_call_ids.add(tool_call_id)

    if pending_observe is not None and (pending_observe.ending_score or pending_observe.failed):
        turns.append(
            DecisionTurn(
                step=len(turns) + 1,
                observe=pending_observe,
            )
        )

    return session_id, turns, misc_calls
