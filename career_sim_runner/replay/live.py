"""Incremental live-replay observer for streaming game events."""

from typing import Any

from rich.console import Console
from rich.rule import Rule

from career_sim_runner.replay.models import DecisionTurn, ObserveSnapshot
from career_sim_runner.replay.parse import _parse_observe_snapshot, _parse_take_action_call, _payload_node
from career_sim_runner.replay.render import _render_turn_rich

from career_sim_runner.constants import EMULATOR_MCP_SERVER_NAME, EMULATOR_MCP_TOOL_PREFIX

_CAREER_MCP_PREFIX = EMULATOR_MCP_TOOL_PREFIX


class LiveReplayObserver:
    """Receive structured event records and render turns to the console live.

    Pass :meth:`feed` as the ``on_event`` callback to
    :func:`~career_sim_runner.ws_client.drive` or
    :class:`~career_sim_runner.transcript.StreamCollector`.
    """

    def __init__(self, console: Console | None = None) -> None:
        """Initialize a live-replay observer.

        :param console: Rich console to print to; creates a default one if ``None``.
        """
        self._console = console or Console()
        self._pending_observe: ObserveSnapshot | None = None
        self._current_month: int | None = None
        self._step: int = 0
        self._seen_result_ids: set[str] = set()
        self._seen_call_ids: set[str] = set()
        self._header_printed: bool = False

    def feed(self, record: dict[str, Any]) -> None:
        """Ingest one structured event record.

        :param record: A single event dict as written by
            :class:`~career_sim_runner.transcript.StreamCollector`.
        """
        kind = str(record.get("kind", ""))
        ts = str(record.get("ts", ""))
        payload = record.get("payload", {})
        if not isinstance(payload, dict):
            return

        if kind == "tool_result":
            self._handle_tool_result(ts, payload)
        elif kind == "tool_call":
            self._handle_tool_call(payload)

    def finish(self) -> None:
        """Render any trailing observe that was never followed by a take_action.

        Call this after all events have been fed (e.g. after the drive loop
        ends) to ensure the game-over screen is shown.
        """
        if self._pending_observe is None:
            return
        obs = self._pending_observe
        if not (obs.ending_score or obs.failed):
            return
        self._pending_observe = None
        self._step += 1
        turn = DecisionTurn(step=self._step, observe=obs)
        self._emit_turn(turn)

    # ------------------------------------------------------------------

    def _ensure_header(self) -> None:
        if self._header_printed:
            return
        self._header_printed = True
        self._console.print(Rule("Career Survival Agent Replay (live)", style="bold magenta"))
        self._console.print()

    def _emit_turn(self, turn: DecisionTurn) -> None:
        self._ensure_header()
        observe = turn.observe
        if observe.month != self._current_month:
            self._current_month = observe.month
            self._console.print(
                Rule(
                    f"Month {observe.month} · Quarter {observe.quarter} · Year {observe.year}",
                    style="bold blue",
                )
            )
            self._console.print()

        _render_turn_rich(self._console, turn)
        self._console.print()

    def _handle_tool_result(self, ts: str, payload: dict[str, Any]) -> None:
        tool_call_id = str(payload.get("tool_call_id", "") or "")
        if not tool_call_id or tool_call_id in self._seen_result_ids:
            return

        tool_name = str(payload.get("tool_name", "") or "")
        if _CAREER_MCP_PREFIX not in tool_name and EMULATOR_MCP_SERVER_NAME not in tool_name:
            node = payload.get("delta", payload)
            if isinstance(node, dict):
                tool_name = str(node.get("tool_name", "") or tool_name)

        if "new_game" in tool_name:
            self._seen_result_ids.add(tool_call_id)
            return

        if "observe" in tool_name:
            snapshot = _parse_observe_snapshot(ts, payload)
            if snapshot is not None:
                self._pending_observe = snapshot
            self._seen_result_ids.add(tool_call_id)

    def _handle_tool_call(self, payload: dict[str, Any]) -> None:
        node = _payload_node(payload)
        tool_call = node.get("tool_call")
        if not isinstance(tool_call, dict):
            return
        tool_call_id = str(tool_call.get("tool_call_id", "") or "")
        if not tool_call_id or tool_call_id in self._seen_call_ids:
            return

        name = str(tool_call.get("name", ""))
        if "take_action" not in name:
            self._seen_call_ids.add(tool_call_id)
            return

        parsed = _parse_take_action_call(payload)
        if parsed is None or self._pending_observe is None:
            self._seen_call_ids.add(tool_call_id)
            return

        choice, notes = parsed
        choice_action = ""
        for option in self._pending_observe.choices:
            if option.choice == choice:
                choice_action = option.action
                break

        self._step += 1
        turn = DecisionTurn(
            step=self._step,
            observe=self._pending_observe,
            choice=choice,
            choice_action=choice_action,
            notes=notes,
        )
        self._pending_observe = None
        self._seen_call_ids.add(tool_call_id)
        self._emit_turn(turn)
