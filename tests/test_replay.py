"""Tests for events-log replay rendering."""

import json
from pathlib import Path

from career_sim_runner.replay import build_replay_report, parse_events_log, write_replay_report


def _write_events(path: Path, records: list[dict[str, object]]) -> None:
    path.write_text(
        "\n".join(json.dumps(record, ensure_ascii=False) for record in records) + "\n",
        encoding="utf-8",
    )


def test_parse_events_log_pairs_observe_and_take_action(tmp_path: Path) -> None:
    """Replay parser should pair one observe result with the next take_action call."""
    observe_payload = {
        "tool_name": "mcp_career-emulator-engine_observe",
        "tool_call_id": "observe-1",
        "raw_output": {
            "result": json.dumps(
                {
                    "current_state": {
                        "time": {"current_month": 1, "current_quarter": 1, "current_year": 1},
                        "status": {
                            "health": 5,
                            "dignity": 5,
                            "skill": 1,
                            "network": 1,
                            "level": "L1",
                            "output": 0,
                            "wealth": 1,
                            "energy": 3,
                        },
                        "simulation_flags": {"alive": True, "failed": False, "failure_reason": None},
                    },
                    "current_event": {
                        "title": "Test event",
                        "description": "A choice is required.",
                    },
                    "choices": [
                        {"choice": 1, "action": "Option A"},
                        {"choice": 2, "action": "Option B"},
                    ],
                    "events": "",
                },
                ensure_ascii=False,
            )
        },
    }
    take_action_payload = {
        "tool_call": {
            "name": "mcp_career-emulator-engine_take_action",
            "tool_call_id": "action-1",
            "arguments": json.dumps(
                {"session_id": "abc", "choice": 2, "notes": "Option B is safer"},
                ensure_ascii=False,
            ),
        }
    }
    events_path = tmp_path / "events-test.jsonl"
    _write_events(
        events_path,
        [
            {"kind": "tool_result", "ts": "2026-01-01T00:00:00+00:00", "payload": observe_payload},
            {"kind": "tool_call", "ts": "2026-01-01T00:00:01+00:00", "payload": take_action_payload},
        ],
    )

    session_id, turns, misc_calls = parse_events_log(events_path)

    assert session_id is None
    assert misc_calls == []
    assert len(turns) == 1
    assert turns[0].choice == 2
    assert turns[0].choice_action == "Option B"
    assert turns[0].notes == "Option B is safer"
    assert turns[0].observe.event_title == "Test event"


def test_build_replay_report_renders_markdown(tmp_path: Path) -> None:
    """Replay markdown should include event title, choices, and decision."""
    observe_payload = {
        "tool_name": "mcp_career-emulator-engine_observe",
        "tool_call_id": "observe-1",
        "raw_output": {
            "result": json.dumps(
                {
                    "current_state": {
                        "time": {"current_month": 2, "current_quarter": 1, "current_year": 1},
                        "status": {
                            "level": "L1",
                            "health": 4,
                            "dignity": 6,
                            "skill": 2,
                            "network": 1,
                            "output": 0,
                            "wealth": 1,
                            "energy": 3,
                        },
                        "simulation_flags": {"alive": True, "failed": False, "failure_reason": None},
                    },
                    "current_event": {"title": "Quarterly review", "description": "Executives are present."},
                    "choices": [{"choice": 1, "action": "Lead with the conclusion"}],
                    "events": "Base salary this month: +0.3 (L1)",
                },
                ensure_ascii=False,
            )
        },
    }
    take_action_payload = {
        "tool_call": {
            "name": "mcp_career-emulator-engine_take_action",
            "tool_call_id": "action-1",
            "arguments": json.dumps({"session_id": "abc", "choice": 1, "notes": "Lead with the conclusion"}, ensure_ascii=False),
        }
    }
    events_path = tmp_path / "events-test.jsonl"
    _write_events(
        events_path,
        [
            {"kind": "tool_result", "ts": "2026-01-01T00:00:00+00:00", "payload": observe_payload},
            {"kind": "tool_call", "ts": "2026-01-01T00:00:01+00:00", "payload": take_action_payload},
        ],
    )

    markdown = build_replay_report(events_path)

    assert "Month 2" in markdown
    assert "Quarterly review" in markdown
    assert "[1] Lead with the conclusion" in markdown
    assert "Lead with the conclusion" in markdown
    assert "Base salary this month" in markdown

    replay_path = write_replay_report(events_path)
    assert replay_path.is_file()
    assert replay_path.name == "replay-test.md"
