"""Load and render token-usage and score data from score_report.json."""

import json
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text


def load_score_report(events_path: Path) -> dict[str, Any] | None:
    """Try to load ``score_report.json`` from the same directory as *events_path*.

    :param events_path: Path to the events ``.jsonl`` log file.
    :return: Parsed JSON dict, or ``None`` when not found / unparseable.
    """
    report_path = events_path.parent / "score_report.json"
    if not report_path.is_file():
        return None
    try:
        return json.loads(report_path.read_text(encoding="utf-8"))  # type: ignore[no-any-return]
    except (json.JSONDecodeError, OSError):
        return None


def load_ending_score(events_path: Path) -> dict[str, Any] | None:
    """Load ``ending_score`` from the sibling ``score_report.json``.

    :param events_path: Path to the events ``.jsonl`` log file.
    :return: The ending-score dict, or ``None``.
    """
    report = load_score_report(events_path)
    if report is None:
        return None
    score = report.get("ending_score")
    return score if isinstance(score, dict) and score else None


def load_token_usage(events_path: Path) -> dict[str, Any] | None:
    """Load ``token_usage`` from the sibling ``score_report.json``.

    :param events_path: Path to the events ``.jsonl`` log file.
    :return: The token-usage dict, or ``None``.
    """
    report = load_score_report(events_path)
    if report is None:
        return None
    usage = report.get("token_usage")
    return usage if isinstance(usage, dict) and usage else None


def render_usage_rich(console: Console, usage: dict[str, Any]) -> None:
    """Print a token-usage summary panel to the rich *console*.

    :param console: The :class:`rich.console.Console` to print to.
    :param usage: Token-usage dict (``input_tokens``, ``output_tokens``,
        ``total_tokens``, optional ``by_model``).
    """
    input_t = usage.get("input_tokens", 0)
    output_t = usage.get("output_tokens", 0)
    total_t = usage.get("total_tokens", 0)

    summary = Text()
    summary.append("Input tokens: ", style="dim")
    summary.append(f"{input_t:,}", style="cyan")
    summary.append("  Output tokens: ", style="dim")
    summary.append(f"{output_t:,}", style="green")
    summary.append("  Total: ", style="dim")
    summary.append(f"{total_t:,}", style="bold")

    by_model: dict[str, Any] = usage.get("by_model", {})
    if by_model:
        table = Table(show_header=True, header_style="bold", box=None, padding=(0, 1))
        table.add_column("Model", style="bold")
        table.add_column("Input", justify="right", style="cyan")
        table.add_column("Output", justify="right", style="green")
        table.add_column("Total", justify="right")
        for model_name, counts in sorted(by_model.items()):
            if not isinstance(counts, dict):
                continue
            table.add_row(
                model_name,
                f"{counts.get('input_tokens', 0):,}",
                f"{counts.get('output_tokens', 0):,}",
                f"{counts.get('total_tokens', 0):,}",
            )
        from rich.console import Group

        console.print(Panel(Group(summary, Text(""), table), title="Token usage", border_style="dim"))
    else:
        console.print(Panel(summary, title="Token usage", border_style="dim"))
