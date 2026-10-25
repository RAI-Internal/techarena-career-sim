"""Render replay decision turns into readable markdown reports."""

import json
import time
from pathlib import Path
from typing import Any

from rich.console import Console, Group
from rich.markdown import Markdown
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table
from rich.text import Text

from career_sim_runner.replay.models import DecisionTurn
from career_sim_runner.replay.parse import parse_events_log
from career_sim_runner.replay.usage import load_ending_score, load_token_usage, render_usage_rich

_STATUS_KEYS = ("level", "health", "dignity", "skill", "network", "output", "wealth", "energy")

_STATUS_STYLE_MAP: dict[str, str] = {
    "level": "bold white",
    "health": "green",
    "dignity": "magenta",
    "skill": "cyan",
    "network": "blue",
    "output": "yellow",
    "wealth": "bold yellow",
    "energy": "red",
}


def render_replay_markdown(
    events_path: Path,
    session_id: str | None,
    turns: list[DecisionTurn],
    misc_calls: list[str] | None = None,
    ending_score: dict[str, Any] | None = None,
) -> str:
    """Render a readable markdown battle report.

    :param events_path: Path to the source events log (shown in the header).
    :param session_id: Game session identifier, or ``None`` if unknown.
    :param turns: Ordered list of decision turns to render.
    :param misc_calls: Optional extra MCP tool names to list at the end.
    :param ending_score: Fallback ending score to append when no turn carries one.
    :return: The complete markdown string.
    """
    lines = [
        "# Career Survival Agent Replay",
        "",
        f"- Event log: `{events_path}`",
    ]
    if session_id:
        lines.append(f"- Game session: `{session_id}`")
    if turns:
        lines.append(f"- Decision steps: {len(turns)}")
        last = turns[-1].observe
        lines.append(
            f"- Last observation: Month {last.month} / Quarter {last.quarter} / Year {last.year} ({last.event_title})"
        )
    lines.append("")

    has_ending_score = False
    current_month: int | None = None
    for turn in turns:
        observe = turn.observe
        if observe.month_feed:
            lines.extend(["", "### Monthly feed", "", observe.month_feed.strip(), ""])

        if observe.month != current_month:
            current_month = observe.month
            lines.extend(
                [
                    "",
                    f"## Month {observe.month} · Quarter {observe.quarter} · Year {observe.year}",
                    "",
                ]
            )

        lines.append(f"### Turn {turn.step} · {observe.event_title}")
        if observe.event_description:
            lines.extend(["", observe.event_description.strip(), ""])
        if observe.choices:
            lines.append("**Choices:**")
            for option in observe.choices:
                suffix = f" — {option.description}" if option.description else ""
                lines.append(f"- [{option.choice}] {option.action}{suffix}")
        lines.append("")
        lines.append(f"**Status:** {_format_status(observe.status)}")
        if turn.choice is not None:
            action_label = turn.choice_action or "(unknown action)"
            lines.append(f"**Choice:** [{turn.choice}] {action_label}")
        if turn.notes:
            lines.append(f"**Reason:** {turn.notes}")
        lines.append("")

        if observe.ending_score:
            score_json = json.dumps(observe.ending_score, ensure_ascii=False, indent=2)
            lines.extend(["## Ending score", "", "```json", score_json, "```", ""])
            has_ending_score = True
        if observe.failed:
            reason = observe.failure_reason or "unknown reason"
            lines.extend(["", f"> **Eliminated:** {reason}", ""])

    if not has_ending_score and ending_score:
        score_json = json.dumps(ending_score, ensure_ascii=False, indent=2)
        lines.extend(["## Ending score", "", "```json", score_json, "```", ""])

    if misc_calls:
        unique_misc = sorted(set(misc_calls))
        lines.extend(["", "## Other MCP calls", "", ", ".join(unique_misc), ""])

    return "\n".join(lines).strip() + "\n"


def render_replay_rich(
    events_path: Path,
    session_id: str | None,
    turns: list[DecisionTurn],
    misc_calls: list[str] | None = None,
    wait_s: float | None = 1.0,
    console: Console | None = None,
    ending_score: dict[str, Any] | None = None,
    token_usage: dict[str, Any] | None = None,
) -> None:
    """Render the replay report to the terminal using rich.

    Each turn is printed sequentially with a pause in between, producing a
    "live replay" effect.

    :param events_path: Path to the source events log (shown in the header).
    :param session_id: Game session identifier, or ``None`` if unknown.
    :param turns: Ordered list of decision turns to render.
    :param misc_calls: Optional extra MCP tool names to list at the end.
    :param wait_s: Seconds to wait between turns.  ``0`` disables the pause;
        ``None`` waits for the user to press Enter.
    :param console: Optional :class:`rich.console.Console` instance; a default
        one is created when ``None``.
    :param ending_score: Fallback ending score shown when no turn carries one.
    :param token_usage: Token-usage dict to display at the end.
    """
    if console is None:
        console = Console()

    console.print(Rule("Career Survival Agent Replay", style="bold magenta"))
    console.print(Text(f"Event log: {events_path}", style="dim"))
    if session_id:
        console.print(Text(f"Game session: {session_id}", style="dim"))
    if turns:
        last = turns[-1].observe
        console.print(Text(f"Decision steps: {len(turns)}", style="dim"))
        console.print(
            Text(
                f"Last observation: Month {last.month} / Quarter {last.quarter} / Year {last.year} ({last.event_title})",
                style="dim",
            )
        )
    console.print()

    has_ending_score = False
    current_month: int | None = None
    for i, turn in enumerate(turns):
        observe = turn.observe
        if observe.month != current_month:
            current_month = observe.month
            console.print(
                Rule(
                    f"Month {observe.month} · Quarter {observe.quarter} · Year {observe.year}",
                    style="bold blue",
                )
            )
            console.print()

        _render_turn_rich(console, turn)
        if turn.observe.ending_score:
            has_ending_score = True
        console.print()

        if i < len(turns) - 1:
            if wait_s is None:
                prompt = "Press Enter to continue, or type wait seconds (e.g. 1.2) >>> "
                console.print(Text(prompt, style="dim italic"), end="")
                user_input = input().strip()
                if user_input:
                    if user_input.replace(".", "").isdecimal():
                        wait_s = float(user_input)
                    elif user_input.lower().removesuffix("()") in ["q", "quit", "exit"]:
                        return
                    else:
                        console.print(Text(f'Invalid input: "{user_input}"', style="red bold"))
            elif wait_s > 0:
                time.sleep(wait_s)

    if not has_ending_score and ending_score:
        _render_ending_score_rich(console, ending_score)
        console.print()

    if misc_calls:
        unique_misc = sorted(set(misc_calls))
        console.print(Rule("Other MCP calls", style="dim"))
        console.print(Text(", ".join(unique_misc), style="dim"))
        console.print()

    if token_usage:
        render_usage_rich(console, token_usage)
        console.print()


def build_replay_report(events_path: Path) -> str:
    """Parse one events log and return markdown.

    Falls back to ``score_report.json`` for the ending score when missing
    from the events stream.

    :param events_path: Path to the events ``.jsonl`` log file.
    :return: Rendered markdown report string.
    """
    session_id, turns, misc_calls = parse_events_log(events_path)
    fallback_score = load_ending_score(events_path)
    return render_replay_markdown(events_path, session_id, turns, misc_calls, ending_score=fallback_score)


def print_replay_rich(
    events_path: Path,
    wait_s: float | None = 1.0,
    console: Console | None = None,
) -> Path:
    """Parse one events log and render it to the terminal with rich.

    :param events_path: Path to the events ``.jsonl`` log file.
    :param wait_s: Seconds to wait between turns; ``None`` for press-Enter mode.
    :param console: Optional :class:`rich.console.Console` instance.
    :return: The path to the written markdown replay file.
    """
    if console is None:
        console = Console()

    session_id, turns, misc_calls = parse_events_log(events_path)
    fallback_score = load_ending_score(events_path)
    token_usage = load_token_usage(events_path)

    render_replay_rich(
        events_path,
        session_id,
        turns,
        misc_calls,
        wait_s=wait_s,
        console=console,
        ending_score=fallback_score,
        token_usage=token_usage,
    )

    report_path = write_replay_report(events_path)
    console.print(Text(f"replay_path: {report_path}", style="dim"))
    return report_path


def write_replay_report(events_path: Path, output_path: Path | None = None) -> Path:
    """Write a replay markdown file next to the events log by default.

    :param events_path: Path to the events ``.jsonl`` log file.
    :param output_path: Destination path; defaults to a sibling file derived from *events_path*.
    :return: The path the report was written to.
    """
    markdown = build_replay_report(events_path)
    if output_path is None:
        output_path = events_path.with_name(events_path.name.replace("events-", "replay-").replace(".jsonl", ".md"))
    output_path.write_text(markdown, encoding="utf-8")
    return output_path


def _format_status(status: dict[str, Any]) -> str:
    """Render the player-visible status block."""
    parts = [f"{key}={status.get(key)}" for key in _STATUS_KEYS if key in status]
    return ", ".join(parts)


def _rich_status_table(status: dict[str, Any]) -> Table:
    """Build a compact Rich table showing the player's status bar."""
    table = Table(show_header=True, header_style="bold", box=None, padding=(0, 1))
    for key in _STATUS_KEYS:
        if key in status:
            table.add_column(key, style=_STATUS_STYLE_MAP.get(key, ""))
    row = [str(status[key]) for key in _STATUS_KEYS if key in status]
    table.add_row(*row)
    return table


def _render_ending_score_rich(console: Console, score: dict[str, Any]) -> None:
    """Render the ending score panel with a dimensions breakdown table."""
    parts: list[Text] = []

    outcome = score.get("outcome", "")
    q_score = score.get("quantitative_score")
    survival = score.get("survival_months")

    meta_line = Text()
    if outcome:
        meta_line.append(f"Outcome: {outcome}", style="bold")
    if survival is not None:
        meta_line.append(f"  Survival months: {survival}")
    if q_score is not None:
        meta_line.append(f"  Quantitative score: {q_score}/100", style="bold cyan")
    if meta_line:
        parts.append(meta_line)

    dimensions = score.get("dimensions")
    dim_table = None
    if isinstance(dimensions, list) and dimensions:
        dim_table = Table(show_header=True, header_style="bold", box=None, padding=(0, 1))
        dim_table.add_column("Dimension", style="bold")
        dim_table.add_column("Raw", justify="right")
        dim_table.add_column("Normalized", justify="right")
        dim_table.add_column("Weight", justify="right")
        dim_table.add_column("Weighted", justify="right", style="cyan")
        for dim in dimensions:
            if not isinstance(dim, dict):
                continue
            dim_table.add_row(
                str(dim.get("label", dim.get("name", ""))),
                str(dim.get("raw_value", "")),
                str(dim.get("normalized_score", "")),
                str(dim.get("weight", "")),
                str(dim.get("weighted_score", "")),
            )

    renderables: list[Table | Text] = list(parts)
    if dim_table is not None:
        renderables.append(Text(""))
        renderables.append(dim_table)

    console.print(Panel(Group(*renderables), title="Ending score", border_style="bold yellow"))


def _render_turn_rich(console: Console, turn: DecisionTurn) -> None:
    """Render a single decision turn to the rich console."""
    observe = turn.observe

    if observe.month_feed:
        console.print(
            Panel(
                Markdown(observe.month_feed.strip()),
                title="Monthly feed",
                border_style="dim",
            )
        )

    title = f"Turn {turn.step} · {observe.event_title}"
    subtitle = f"Month {observe.month} · Quarter {observe.quarter} · Year {observe.year}"
    console.print(Rule(title, style="bold cyan"))
    console.print(Text(subtitle, style="dim italic"), justify="center")
    console.print()

    if observe.event_description:
        console.print(Markdown(observe.event_description.strip()))
        console.print()

    if observe.choices:
        console.print(Text("Choices:", style="bold"))
        for option in observe.choices:
            highlight = option.choice == turn.choice
            marker = ">>>" if highlight else "   "
            style = "bold green" if highlight else ""
            desc = f" — {option.description}" if option.description else ""
            console.print(Text(f"  {marker} [{option.choice}] {option.action}{desc}", style=style))
        console.print()

    console.print(_rich_status_table(observe.status))
    console.print()

    if turn.choice is not None:
        action_label = turn.choice_action or "(unknown action)"
        console.print(Text(f"Choice: [{turn.choice}] {action_label}", style="bold green"))
    if turn.notes:
        console.print(Text(f"Reason: {turn.notes}", style="italic"))

    if observe.ending_score:
        _render_ending_score_rich(console, observe.ending_score)

    if observe.failed:
        reason = observe.failure_reason or "unknown reason"
        console.print(Panel(Text(f"Eliminated: {reason}", style="bold red"), border_style="red"))
