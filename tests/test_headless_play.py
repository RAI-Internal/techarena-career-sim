"""Tests for JiuwenSwarm conversation session selection."""

import asyncio
from pathlib import Path

import pytest

from career_sim_runner import headless_play
from tests.test_skill_contract import build_complete_submission


def test_resolve_drive_session_id_defaults_to_fresh_session() -> None:
    """Fresh runs should use a unique JiuwenSwarm conversation id."""
    session_id = headless_play.resolve_drive_session_id(continue_run=False)
    assert session_id.startswith("career-sim-runner-")


def test_resolve_drive_session_id_continue_uses_last_session(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Continue mode should reuse the last stored JiuwenSwarm conversation id."""
    state_path = tmp_path / "last_drive_session.txt"
    state_path.write_text("career-sim-runner-prev\n", encoding="utf-8")
    monkeypatch.setattr(headless_play, "last_drive_session_path", lambda: state_path)
    assert headless_play.resolve_drive_session_id(continue_run=True) == "career-sim-runner-prev"


def test_play_allows_missing_presentation(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A local play run must reach install when the video file is absent."""
    root = build_complete_submission(tmp_path)
    (root / "presentation.mp4").unlink()

    def fake_install(*args, **kwargs) -> None:
        assert kwargs.get("require_presentation") is False
        raise RuntimeError("reached-install")

    monkeypatch.setattr(headless_play, "install_submission", fake_install)
    monkeypatch.setattr(headless_play, "store_last_drive_session_id", lambda session_id: None)
    with pytest.raises(RuntimeError, match="reached-install"):
        asyncio.run(headless_play.play_headless(root, ws_url="ws://127.0.0.1:1"))


def test_resolve_drive_session_id_continue_requires_previous_session(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Continue mode should fail clearly when no prior session exists."""
    state_path = tmp_path / "missing.txt"
    monkeypatch.setattr(headless_play, "last_drive_session_path", lambda: state_path)
    with pytest.raises(RuntimeError, match="Run without --continue first"):
        headless_play.resolve_drive_session_id(continue_run=True)
