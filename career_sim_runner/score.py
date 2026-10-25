"""Scoring helpers for participant-facing run reports."""

import json
from datetime import datetime, timezone
from pathlib import Path

from career_sim_runner.db import latest_session_id, read_ending_score
from career_sim_runner.models import InstallRecord, ScoreReport, TokenUsage


async def build_score_report(
    install_record: InstallRecord,
    db_path: Path,
    output_dir: Path,
    token_usage: TokenUsage,
    play_exit_code: int,
    termination_reason: str | None,
    transcript_path: Path | None,
    events_path: Path | None,
    drive_session_id: str = "",
    session_id: str = "",
) -> ScoreReport:
    """Build the final run report."""
    resolved_session_id = session_id.strip()
    if not resolved_session_id:
        fallback = await latest_session_id(db_path)
        if fallback:
            resolved_session_id = fallback
    ending_score = await read_ending_score(db_path, resolved_session_id) if resolved_session_id else {}
    if not ending_score and transcript_path and transcript_path.is_file():
        ending_score = extract_ending_score_from_transcript(transcript_path)
    return ScoreReport(
        submission_name=install_record.submission_name,
        submission_dir=install_record.submission_dir,
        skill_name=install_record.skill_name,
        drive_session_id=drive_session_id,
        session_id=resolved_session_id,
        play_exit_code=play_exit_code,
        termination_reason=termination_reason,
        token_usage=token_usage,
        ending_score=ending_score,
        output_dir=str(output_dir),
        events_log=str(events_path) if events_path else None,
        transcript_log=str(transcript_path) if transcript_path else None,
        scored_at=datetime.now(timezone.utc).isoformat(),
    )


def extract_ending_score_from_transcript(transcript_path: Path) -> dict[str, object]:
    """Extract the final ``ending_score`` JSON block from a transcript."""
    text = transcript_path.read_text(encoding="utf-8")
    for candidate in reversed(text.split("```json")):
        block = candidate.split("```", 1)[0].strip()
        if not block.startswith("{"):
            continue
        try:
            payload = json.loads(block)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict) and "outcome" in payload and "competition_partial_score" in payload:
            return payload
    return {}


def write_score_report(report: ScoreReport, output_dir: Path) -> Path:
    """Write the final report to disk."""
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / "score_report.json"
    report_path.write_text(json.dumps(report.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    return report_path
