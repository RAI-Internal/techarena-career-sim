"""CLI for the standalone participant runner."""

import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import TextIO

from career_sim_runner.constants import DEFAULT_TIMEOUT_S
from career_sim_runner.headless_play import (
    load_last_drive_session_id,
    load_last_output_dir,
)
from career_sim_runner.headless_play import (
    main as headless_play_main,
)
from career_sim_runner.install import install_submission, load_active_install
from career_sim_runner.models import TokenUsage
from career_sim_runner.paths import (
    default_db_path,
    ensure_runtime_dirs,
    latest_output_dir,
)
from career_sim_runner.replay import build_replay_report, print_replay_rich, write_replay_report
from career_sim_runner.replay.live import LiveReplayObserver
from career_sim_runner.report import format_score_report, format_validation_report, print_termination_error
from career_sim_runner.score import build_score_report, write_score_report
from career_sim_runner.setup import (
    ensure_instance_configured,
    resolve_instance_ws_url,
    setup_summary,
    tool_availability,
)
from career_sim_runner.validate import validate_submission


def configure_stdio(stream: TextIO, encoding: str = "utf-8") -> None:
    """Use UTF-8 for CLI output when the platform default cannot encode game text.

    On Windows, ``sys.stdout`` often defaults to a legacy code page (for example
    cp1252), which raises ``UnicodeEncodeError`` for non-ASCII event titles.
    """
    reconfigure = getattr(stream, "reconfigure", None)
    if callable(reconfigure):
        try:
            reconfigure(encoding=encoding, errors="replace")
        except (AttributeError, ValueError, OSError):
            pass


def _print_json(payload: object) -> None:
    """Pretty-print JSON."""
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def _find_latest(directory: Path, pattern: str) -> Path | None:
    """Return the most recently modified file matching *pattern* in *directory*."""
    matches = sorted(directory.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)
    return matches[0] if matches else None


def _load_token_usage_from_report(output_dir: Path) -> TokenUsage:
    """Load token usage from a previous score_report.json in *output_dir*."""
    report_path = output_dir / "score_report.json"
    if not report_path.is_file():
        return TokenUsage()
    try:
        data = json.loads(report_path.read_text(encoding="utf-8"))
        usage = data.get("token_usage", {})
        by_model = {k: v for k, v in usage.get("by_model", {}).items() if any(v.values())}
        return TokenUsage(
            input_tokens=int(usage.get("input_tokens", 0)),
            output_tokens=int(usage.get("output_tokens", 0)),
            total_tokens=int(usage.get("total_tokens", 0)),
            total_cost=float(usage.get("total_cost", 0)),
            by_model=by_model,
        )
    except (json.JSONDecodeError, KeyError, TypeError, ValueError):
        return TokenUsage()


def _parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description="Standalone participant runner for TechArena Career Survival Agent")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("setup", help="Show setup paths, tools, and recommended config")

    validate_parser = subparsers.add_parser("validate", help="Validate a submission directory")
    validate_parser.add_argument("--submission", required=True, help="Submission directory containing skills/")

    install_parser = subparsers.add_parser("install", help="Install submission into JiuwenSwarm")
    install_parser.add_argument("--submission", required=True, help="Submission directory containing skills/")

    play_parser = subparsers.add_parser("play", help="Install, run JiuwenSwarm, and score")
    play_parser.add_argument("--submission", default="", help="Submission directory containing skills/")
    play_parser.add_argument("--ws-url", default="")
    play_parser.add_argument("--db", default=str(default_db_path()))
    play_parser.add_argument("--timeout-s", type=float, default=DEFAULT_TIMEOUT_S)
    play_parser.add_argument(
        "--continue",
        dest="continue_run",
        action="store_true",
        help="Reuse the previous JiuwenSwarm conversation instead of starting a fresh one",
    )
    play_parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Do not output to the terminal as the game is played",
    )

    subparsers.add_parser("score", help="Re-read objective score from the last play run")

    replay_parser = subparsers.add_parser("replay", help="Render a readable markdown report from events JSONL")
    replay_parser.add_argument("--events", default="", help="Path to events-*.jsonl (defaults to last run)")
    replay_parser.add_argument(
        "--output",
        default="",
        help="Output markdown path (defaults to replay-<timestamp>.md beside the events log)",
    )
    replay_parser.add_argument(
        "--live",
        action="store_true",
        help="Render a rich live replay to the terminal instead of writing markdown",
    )
    replay_parser.add_argument(
        "--wait",
        type=float,
        default=None,
        help="Seconds to wait between turns in --live mode (default: None)",
    )

    return parser.parse_args()


def main() -> int:
    """CLI entrypoint."""
    for name in ("stdout", "stderr"):
        stream = getattr(sys, name, None)
        if stream is not None:
            configure_stdio(stream)

    ensure_runtime_dirs()
    args = _parse_args()

    if args.command == "setup":
        config_path = ensure_instance_configured()
        _print_json(
            {
                "summary": setup_summary(),
                "configured_instance_config": str(config_path),
                "tools": tool_availability(),
            }
        )
        return 0

    if args.command == "validate":
        validation_report = validate_submission(Path(args.submission))
        print(format_validation_report(validation_report))
        return 0 if validation_report.ok else 1

    if args.command == "install":
        record = install_submission(Path(args.submission), require_presentation=False)
        _print_json(record.to_dict())
        return 0

    if args.command == "play":
        submission = Path(args.submission) if args.submission else None
        resolved_ws_url = args.ws_url or resolve_instance_ws_url()
        observer: LiveReplayObserver | None = None
        if not args.quiet:
            observer = LiveReplayObserver()
        play_report, report_path = headless_play_main(
            submission_dir=submission,
            ws_url=resolved_ws_url,
            db_path=Path(args.db),
            timeout_s=args.timeout_s,
            continue_run=args.continue_run,
            on_event=observer.feed if observer else None,
        )
        if observer is not None:
            observer.finish()
        print_termination_error(play_report)
        print(format_score_report(play_report))
        print(f"report_path: {report_path}")
        return 0 if play_report.play_exit_code == 0 else 1

    if args.command == "score":
        install_record = load_active_install()
        if install_record is None:
            print("No active install found. Run install or play first.")
            return 1
        output_dir = load_last_output_dir() or latest_output_dir(install_record.submission_name)
        if output_dir is None:
            print("No previous output directory found. Run play first.")
            return 1
        drive_session_id = load_last_drive_session_id() or ""
        transcript_path = _find_latest(output_dir, "transcript-*.log")
        events_path = _find_latest(output_dir, "events-*.jsonl")
        token_usage = _load_token_usage_from_report(output_dir)
        score_report = asyncio.run(
            build_score_report(
                install_record=install_record,
                db_path=default_db_path(),
                output_dir=output_dir,
                token_usage=token_usage,
                play_exit_code=0,
                termination_reason=None,
                transcript_path=transcript_path,
                events_path=events_path,
                drive_session_id=drive_session_id,
                session_id="",
            )
        )
        report_path = write_score_report(score_report, output_dir)
        print(format_score_report(score_report))
        print(f"report_path: {report_path}")
        return 0

    if args.command == "replay":
        if args.events:
            events_path = Path(args.events)
        else:
            install_record = load_active_install()
            output_dir = load_last_output_dir()
            if output_dir is None and install_record is not None:
                output_dir = latest_output_dir(install_record.submission_name)
            events_path = _find_latest(output_dir, "events-*.jsonl") if output_dir else None
        if events_path is None or not events_path.is_file():
            print("No events log found. Run play first or pass --events.")
            return 1
        if args.live:
            print_replay_rich(events_path, wait_s=args.wait)
            return 0
        output_path = Path(args.output) if args.output else None
        report_path = write_replay_report(events_path, output_path)
        print(build_replay_report(events_path))
        print(f"replay_path: {report_path}")
        return 0

    return 1
