"""Tests for participant-facing report rendering."""

from rich.console import Console

from career_sim_runner.models import ScoreReport, TokenUsage
from career_sim_runner.report import print_termination_error


def _score_report(termination_reason: str | None) -> ScoreReport:
    """Return a minimal score report for rendering tests."""
    return ScoreReport(
        submission_name="test",
        submission_dir="/tmp/submission",
        skill_name="test-skill",
        drive_session_id="drive-session",
        session_id="game-session",
        play_exit_code=1,
        termination_reason=termination_reason,
        token_usage=TokenUsage(),
        ending_score={},
        output_dir="/tmp/output",
        events_log=None,
        transcript_log=None,
        scored_at="2026-08-13T00:00:00+00:00",
    )


def test_print_termination_error_for_continuation_limit() -> None:
    """Continuation exhaustion should produce an explicit rich diagnostic."""
    console = Console(record=True, width=120)
    print_termination_error(_score_report("max_continuations"), console)
    output = console.export_text()
    assert "Continuation limit exhausted" in output
    assert "terminal state" in output


def test_print_termination_error_ignores_other_reasons() -> None:
    """Other termination outcomes should not print this diagnostic."""
    console = Console(record=True)
    print_termination_error(_score_report(None), console)
    assert console.export_text() == ""
