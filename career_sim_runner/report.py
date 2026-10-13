"""Human-readable reporting helpers for the standalone runner."""

import json

from rich.console import Console
from rich.panel import Panel

from career_sim_runner.models import ScoreReport, ValidationReport


def format_validation_report(report: ValidationReport) -> str:
    """Render a validation report as plain text."""
    lines = [f"overall_ok={report.ok}"]
    for check in report.checks:
        status = "OK" if check.ok else "FAIL"
        lines.append(f"[{status}] {check.name}: {check.detail}")
    return "\n".join(lines)


def format_score_report(report: ScoreReport) -> str:
    """Render a score report as plain text."""
    score_report = f"\n{'=' * 60}\n"
    for k, v in report.ending_score.items():
        if not isinstance(v, list):
            score_report += f"{k}: {v}\n"
        else:
            fmt_v = "  - " + "\n  - ".join(
                f"{s['label']:4s} {s['weighted_score']:4.1f} (raw={s['raw_value']:g}, weight={s['weight']:g})"
                for s in v
            )
            score_report += f"{k}:\n{fmt_v}\n"
    score_report += f"{'=' * 60}"

    lines = [
        f"submission_name: {report.submission_name}",
        f"drive_session_id: {report.drive_session_id}",
        f"session_id: {report.session_id}",
        f"play_exit_code: {report.play_exit_code}",
        f"termination_reason: {report.termination_reason}",
        f"output_dir: {report.output_dir}",
        f"transcript_log: {report.transcript_log}",
        f"events_log: {report.events_log}",
        f"token_usage: {json.dumps(report.token_usage.to_dict(), ensure_ascii=False)}",
        f"ending_score: {score_report}",
    ]
    return "\n".join(lines)


def print_termination_error(report: ScoreReport, console: Console | None = None) -> None:
    """Print a rich diagnostic when a play run stops before game completion.

    :param report: Completed play report containing the termination reason.
    :param console: Rich console to print to; creates a stderr console if omitted.
    """
    if report.termination_reason != "max_continuations":
        return
    output = console or Console(stderr=True)
    output.print(
        Panel(
            "The agent completed the maximum number of continuation cycles, but the game did not reach a "
            "terminal state.\n\n"
            "Check the transcript for repeated tool-call failures. Increase MAX_CONTINUATIONS only if the run "
            "is making valid progress.",
            title="Continuation limit exhausted",
            border_style="bold red",
        )
    )
