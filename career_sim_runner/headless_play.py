"""Headless JiuwenSwarm play orchestration."""

import asyncio
import uuid
from pathlib import Path

from career_sim_runner.constants import DEFAULT_TIMEOUT_S, DRIVE_SESSION_PREFIX
from career_sim_runner.install import install_submission, load_active_install
from career_sim_runner.models import ScoreReport
from career_sim_runner.paths import (
    default_db_path,
    ensure_runtime_dirs,
    jiuwenswarm_skills_dir,
    last_drive_session_path,
    last_output_dir_path,
    latest_output_dir,
    timestamped_output_dir,
)
from career_sim_runner.score import build_score_report, write_score_report
from career_sim_runner.setup import resolve_instance_ws_url
from career_sim_runner.transcript import EventCallback
from career_sim_runner.validate import validate_environment, validate_submission
from career_sim_runner.ws_client import (
    build_continue_prompt,
    build_play_prompt,
    drive,
    reload_agent_config,
    resolve_run_mode,
)


def new_drive_session_id() -> str:
    """Return a fresh JiuwenSwarm conversation id for one run."""
    return f"{DRIVE_SESSION_PREFIX}-{uuid.uuid4().hex[:12]}"


def load_last_drive_session_id() -> str | None:
    """Return the last JiuwenSwarm conversation id, if any."""
    path = last_drive_session_path()
    if not path.is_file():
        return None
    session_id = path.read_text(encoding="utf-8").strip()
    return session_id or None


def store_last_drive_session_id(session_id: str) -> None:
    """Persist the most recent JiuwenSwarm conversation id."""
    last_drive_session_path().write_text(session_id.strip() + "\n", encoding="utf-8")


def load_last_output_dir() -> Path | None:
    """Return the last output directory, if persisted."""
    path = last_output_dir_path()
    if not path.is_file():
        return None
    stored = path.read_text(encoding="utf-8").strip()
    if not stored:
        return None
    candidate = Path(stored)
    if candidate.is_dir():
        return candidate
    return None


def store_last_output_dir(output_dir: Path) -> None:
    """Persist the output directory for a run."""
    last_output_dir_path().write_text(str(output_dir) + "\n", encoding="utf-8")


def resolve_drive_session_id(continue_run: bool) -> str:
    """Choose a fresh or persisted JiuwenSwarm conversation id."""
    if not continue_run:
        return new_drive_session_id()
    session_id = load_last_drive_session_id()
    if session_id is None:
        msg = "No previous JiuwenSwarm conversation found. Run without --continue first."
        raise RuntimeError(msg)
    return session_id


async def play_headless(
    submission_dir: Path | None,
    ws_url: str | None = None,
    db_path: Path | None = None,
    timeout_s: float = DEFAULT_TIMEOUT_S,
    continue_run: bool = False,
    on_event: EventCallback | None = None,
) -> tuple[ScoreReport, Path]:
    """Install, drive, and score one participant submission.

    :param on_event: Optional callback invoked for each structured event
        as it is written during the play session.  Pass
        :meth:`LiveReplayObserver.feed` for real-time rich output.
    """
    ensure_runtime_dirs()
    resolved_ws_url = ws_url or resolve_instance_ws_url()
    resolved_db_path = db_path or default_db_path()
    drive_session_id = resolve_drive_session_id(continue_run=continue_run)
    store_last_drive_session_id(drive_session_id)

    if submission_dir is not None:
        submission_report = validate_submission(submission_dir)
        if not submission_report.ok:
            details = "; ".join(check.detail for check in submission_report.checks if not check.ok)
            raise RuntimeError(details)
        install_record = install_submission(submission_dir=submission_dir, skills_dir=jiuwenswarm_skills_dir())
        assert await reload_agent_config(resolved_ws_url), "Failed to reload JiuwenSwarm agent config!"
    else:
        loaded_install = load_active_install()
        if loaded_install is None:
            msg = "No active install found. Pass --submission or run install first."
            raise RuntimeError(msg)
        install_record = loaded_install

    environment_report = await validate_environment(ws_url=resolved_ws_url, db_path=resolved_db_path)
    backend_failures = [
        check.detail for check in environment_report.checks if not check.ok and check.name == "backend-reachable"
    ]
    if backend_failures:
        raise RuntimeError(backend_failures[0])

    if continue_run:
        output_dir = (
            load_last_output_dir()
            or latest_output_dir(install_record.submission_name)
            or timestamped_output_dir(install_record.submission_name)
        )
        prompt = build_continue_prompt(None)
    else:
        output_dir = timestamped_output_dir(install_record.submission_name)
        prompt = build_play_prompt()

    store_last_output_dir(output_dir)
    mode = resolve_run_mode(install_record)
    drive_result = await drive(
        ws_url=resolved_ws_url,
        prompt=prompt,
        session_id=drive_session_id,
        mode=mode,
        timeout_s=timeout_s,
        log_dir=output_dir,
        on_event=on_event,
    )
    report = await build_score_report(
        install_record=install_record,
        db_path=resolved_db_path,
        output_dir=output_dir,
        token_usage=drive_result.token_usage,
        play_exit_code=drive_result.exit_code,
        termination_reason=drive_result.termination_reason,
        transcript_path=drive_result.transcript_path,
        events_path=drive_result.events_path,
        drive_session_id=drive_session_id,
        session_id=drive_result.session_id or "",
    )
    report_path = write_score_report(report, output_dir)
    return report, report_path


def main(
    submission_dir: Path | None,
    ws_url: str | None = None,
    db_path: Path | None = None,
    timeout_s: float = DEFAULT_TIMEOUT_S,
    continue_run: bool = False,
    on_event: EventCallback | None = None,
) -> tuple[ScoreReport, Path]:
    """Sync entrypoint for headless play."""
    return asyncio.run(
        play_headless(
            submission_dir=submission_dir,
            ws_url=ws_url,
            db_path=db_path,
            timeout_s=timeout_s,
            continue_run=continue_run,
            on_event=on_event,
        )
    )
