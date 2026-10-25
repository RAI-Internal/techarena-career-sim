"""Preflight validation for the standalone participant runner."""

import asyncio
import inspect
from pathlib import Path
from typing import cast

from career_sim_runner.constants import EMULATOR_CLI, EMULATOR_MCP_COMMAND, EMULATOR_MCP_SERVER_NAME
from career_sim_runner.mcp_config import config_mentions_career_emulator, env_mentions_db
from career_sim_runner.models import ValidationReport
from career_sim_runner.paths import (
    default_db_path,
    default_instance_name,
    ensure_runtime_dirs,
    instance_root,
    jiuwenswarm_config_path,
    jiuwenswarm_env_path,
    jiuwenswarm_skills_dir,
)
from career_sim_runner.setup import (
    ensure_instance_env_overlay,
    ensure_instance_initialized,
    resolve_instance_ws_url,
    tool_availability,
)
from career_sim_runner.skill_contract import (
    list_bundle_skill_ids,
    load_manifest,
    validate_manifest,
    validate_skill_frontmatter,
    validate_submission_contract,
    validate_submission_structure,
)
from career_sim_runner.ws_client import check_backend


def _check_db_writable(db_path: Path) -> tuple[bool, str]:
    """Return whether the configured DB path is writable."""
    parent = db_path.parent
    try:
        parent.mkdir(parents=True, exist_ok=True)
        probe = parent / ".write_probe"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink()
        return True, f"Writable DB parent directory: {parent}"
    except OSError as exc:
        return False, f"Cannot write DB parent directory {parent}: {exc}"


def _check_dataset_ready() -> tuple[bool, str]:
    """Return whether the installed Career Emulator dataset is present."""
    import career_emulator.failure_conditions  # pylint: disable=import-outside-toplevel

    package_root = Path(inspect.getfile(career_emulator.failure_conditions)).resolve().parent
    condition_dir = package_root / "data" / "dataset" / "failure_conditions"
    if list(condition_dir.glob("*.json")) + list(condition_dir.glob("*.data")):
        return True, f"Installed {EMULATOR_CLI} dataset is available at {condition_dir}"
    return False, (
        f"Installed {EMULATOR_CLI} dataset is missing under {condition_dir}. "
        f"Run `uv run {EMULATOR_CLI} update --source distribution`."
    )


async def validate_environment(ws_url: str | None = None, db_path: Path | None = None) -> ValidationReport:
    """Validate the local runtime environment."""
    ensure_runtime_dirs()
    ensure_instance_initialized()
    ensure_instance_env_overlay()
    resolved_ws_url = ws_url or resolve_instance_ws_url()
    resolved_db_path = db_path or default_db_path()
    report = ValidationReport()
    tool_is_available = tool_availability()

    report.add(
        EMULATOR_MCP_COMMAND,
        cast(bool, tool_is_available[EMULATOR_MCP_COMMAND]),
        f"{EMULATOR_MCP_COMMAND} is available on PATH"
        if tool_is_available[EMULATOR_MCP_COMMAND]
        else f"{EMULATOR_MCP_COMMAND} is not on PATH",
    )
    report.add(
        "jiuwenswarm-start",
        cast(bool, tool_is_available["jiuwenswarm-start"]),
        "jiuwenswarm-start is available on PATH"
        if tool_is_available["jiuwenswarm-start"]
        else "jiuwenswarm-start is not on PATH",
    )
    dataset_ok, dataset_detail = _check_dataset_ready()
    report.add(f"{EMULATOR_CLI}-dataset", dataset_ok, dataset_detail)
    report.add(
        "jiuwenswarm-instance",
        instance_root().is_dir(),
        f"Found named instance {default_instance_name()} at {instance_root()}"
        if instance_root().is_dir()
        else f"Missing named instance {default_instance_name()} at {instance_root()}",
    )

    config_path = jiuwenswarm_config_path()
    env_path = jiuwenswarm_env_path()
    report.add(
        "jiuwenswarm-config",
        config_path.is_file(),
        f"Found JiuwenSwarm config at {config_path}"
        if config_path.is_file()
        else f"Missing JiuwenSwarm config at {config_path}",
    )
    report.add(
        "jiuwenswarm-env",
        env_path.is_file(),
        f"Found JiuwenSwarm env at {env_path}" if env_path.is_file() else f"Missing JiuwenSwarm env at {env_path}",
    )
    report.add(
        "mcp-server-configured",
        config_mentions_career_emulator(config_path),
        f"JiuwenSwarm config mentions the {EMULATOR_MCP_SERVER_NAME} MCP server"
        if config_mentions_career_emulator(config_path)
        else f"JiuwenSwarm config does not mention the {EMULATOR_MCP_SERVER_NAME} MCP server",
    )
    report.add(
        "db-config-aligned",
        env_mentions_db(config_path, resolved_db_path),
        f"JiuwenSwarm config mentions {resolved_db_path}"
        if env_mentions_db(config_path, resolved_db_path)
        else f"JiuwenSwarm config does not mention {resolved_db_path}",
    )

    db_ok, db_detail = _check_db_writable(resolved_db_path)
    report.add("db-writable", db_ok, db_detail)
    report.add(
        "skills-dir",
        jiuwenswarm_skills_dir().parent.exists(),
        f"JiuwenSwarm skill root is {jiuwenswarm_skills_dir()}"
        if jiuwenswarm_skills_dir().parent.exists()
        else "JiuwenSwarm skill root does not exist yet",
    )

    backend_ok = await check_backend(resolved_ws_url)
    report.add(
        "backend-reachable",
        backend_ok,
        f"AgentServer reachable at {resolved_ws_url}"
        if backend_ok
        else f"AgentServer not reachable at {resolved_ws_url}",
    )
    return report


def validate_submission(submission_dir: Path, *, require_presentation: bool = True) -> ValidationReport:
    """Validate one participant submission.

    :param require_presentation: When false, ``presentation.mp4`` may be
        absent. Local play uses that. The ``validate`` command keeps the
        default so a final submission without the video still fails.
    """
    report = ValidationReport()

    # Required-structure check: every mandatory file and folder in the final
    # submission layout (manifest, README, design documents, and Skills).
    structure_errors = validate_submission_structure(submission_dir, require_presentation=require_presentation)
    if structure_errors:
        for err in structure_errors:
            report.add("submission-structure", False, err)
    else:
        if require_presentation:
            structure_detail = (
                "Required submission structure is present: manifest.json, README.md, "
                "presentation.mp4, design/skills_design.md, design/decision_report.md, "
                "and at least one skills/*/SKILL.md"
            )
        else:
            structure_detail = (
                "Required local-run structure is present: manifest.json, README.md, "
                "design/skills_design.md, design/decision_report.md, "
                "and at least one skills/*/SKILL.md"
            )
        report.add("submission-structure", True, structure_detail)

    # Layout check: the submission can be loaded as a supported bundle.
    try:
        details = validate_submission_contract(submission_dir, require_presentation=require_presentation)
    except Exception as exc:  # pylint: disable=broad-exception-caught
        if not structure_errors:
            report.add("submission-layout", False, str(exc))
        return report
    report.add("submission-layout", True, f"Submission layout valid: {details['submission_name']}")

    # Manifest field checks: team name and mode.
    manifest = load_manifest(submission_dir)
    manifest_errors = validate_manifest(manifest)
    if manifest_errors:
        for err in manifest_errors:
            report.add("manifest-fields", False, err)
    else:
        report.add("manifest-fields", True, "manifest.json team and mode fields are valid")

    # Per-skill SKILL.md frontmatter checks.
    skill_ids = list_bundle_skill_ids(submission_dir)
    frontmatter_errors: list[str] = []
    for skill_id in skill_ids:
        frontmatter_errors.extend(validate_skill_frontmatter(submission_dir / "skills" / skill_id))
    if frontmatter_errors:
        for err in frontmatter_errors:
            report.add("skill-frontmatter", False, err)
    else:
        report.add(
            "skill-frontmatter",
            True,
            f"All {len(skill_ids)} skill(s) have valid SKILL.md frontmatter",
        )

    return report


def validate_all(submission_dir: Path, ws_url: str | None = None, db_path: Path | None = None) -> ValidationReport:
    """Run submission and environment validation together.

    The participant ``validate`` command does not call this. That command
    checks the submission directory only, so a stopped JiuwenSwarm instance
    does not fail it.
    """
    submission_report = validate_submission(submission_dir)
    environment_report = asyncio.run(validate_environment(ws_url=ws_url, db_path=db_path))
    return ValidationReport(checks=submission_report.checks + environment_report.checks)
