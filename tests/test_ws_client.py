"""Tests for headless JiuwenSwarm websocket helpers."""

from pathlib import Path

import pytest

from career_sim_runner.models import InstallRecord
from career_sim_runner.skill_contract import SubmissionError
from career_sim_runner.ws_client import _build_envelope, build_play_prompt, resolve_run_mode


def _install_record(*, mode: str = "agent", instruction: str = "") -> InstallRecord:
    """Return an install record fixture for websocket tests."""
    return InstallRecord(
        submission_dir="/tmp/submission",
        submission_name="fixture-team",
        skill_dir="/tmp/skills",
        skill_name="submission-skills",
        manifest={
            "mode": mode,
            "instruction": instruction,
            "participant_skill_names": ["monthly-action-decision", "report-generation"],
        },
    )


def test_build_play_prompt() -> None:
    """Play prompt is now static; skills/instruction live in IDENTITY.md."""
    prompt = build_play_prompt()
    static_prompt_file = Path(__file__).parent.with_name("career_sim_runner") / "prompts" / "play_headless.md"
    assert prompt.strip() == static_prompt_file.read_text(encoding="utf-8").strip()


def test_resolve_run_mode_uses_manifest_value() -> None:
    """Supported manifest modes should flow through to the websocket payload."""
    assert resolve_run_mode(_install_record(mode="team")) == "team"


def test_resolve_run_mode_rejects_unsupported() -> None:
    """Unsupported manifest modes should raise SubmissionError."""
    with pytest.raises(SubmissionError):
        resolve_run_mode(_install_record(mode="unsupported-mode"))


def test_build_envelope_uses_selected_mode() -> None:
    """Envelope generation should send the resolved JiuwenSwarm mode."""
    envelope = _build_envelope("prompt", "drive-session", "agent")
    assert envelope["params"]["mode"] == "agent"
    assert envelope["params"]["work_mode"] == "work"
