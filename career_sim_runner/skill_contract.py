"""Submission layout and skill contract helpers."""

import json
from pathlib import Path
from typing import Any

import yaml

from career_sim_runner.constants import (
    SUBMISSION_MODE_SKILL_BUNDLE,
    SUPPORTED_RUN_MODES,
)

_PLACEHOLDER_TEAM_NAMES: frozenset[str] = frozenset(
    {
        "",
        "enter your team name here",
        "your-team-name",
    }
)

REQUIRED_SUBMISSION_FILES: tuple[str, ...] = (
    "manifest.json",
    "README.md",
    "presentation.mp4",
    "design/skills_design.md",
    "design/decision_report.md",
)


class SubmissionError(ValueError):
    """Raised when a submission does not match the expected contract."""


def resolve_skills_root(submission_dir: Path) -> Path:
    """Return the root directory for a supported submission."""
    root = submission_dir.expanduser().resolve()
    if _is_skill_bundle(root):
        return root
    msg = "Expected a submission like `solution/` with `skills/*/SKILL.md`."
    raise SubmissionError(msg)


def load_manifest(submission_dir: Path) -> dict[str, Any]:
    """Load submission metadata from ``manifest.json``."""
    manifest_path = submission_dir / "manifest.json"
    if manifest_path.is_file():
        return json.loads(manifest_path.read_text(encoding="utf-8"))
    return {}


def submission_name(submission_dir: Path, manifest: dict[str, Any]) -> str:
    """Derive a stable short label for logs and reports."""
    if manifest.get("team") or manifest.get("name"):
        return str(manifest.get("team") or manifest.get("name"))
    return submission_dir.resolve().name


def validate_manifest(manifest: dict[str, Any]) -> list[str]:
    """Return error messages for invalid manifest fields.

    Checks the ``team`` name (must not be blank or a known placeholder) and
    the ``mode`` field (must be ``agent``). ``team`` mode is prohibited.
    Returns an empty list when everything is valid.
    """
    errors: list[str] = []
    team = str(manifest.get("team") or "").strip()
    if team.lower() in _PLACEHOLDER_TEAM_NAMES:
        errors.append(f"manifest.json 'team' is {team!r} — replace it with your actual team name")
    mode = str(manifest.get("mode") or "").strip()
    if mode not in SUPPORTED_RUN_MODES:
        errors.append(
            f'manifest.json \'mode\' is {mode!r} — must be "agent". Any other mode, including "team", is prohibited.'
        )
    return errors


def validate_submission_structure(submission_dir: Path, *, require_presentation: bool = True) -> list[str]:
    """Return errors for required submission files or folders that are missing.

    The required final-submission layout is ``manifest.json``, ``README.md``,
    ``presentation.mp4``, ``design/skills_design.md``,
    ``design/decision_report.md``, a ``design/`` directory, a ``skills/``
    directory, and at least one ``skills/<skill-name>/SKILL.md``. Presence is
    checked here. A zero-byte ``presentation.mp4`` is also reported when the
    final-submission check requires that file. Manifest fields and
    ``SKILL.md`` front matter are validated separately.

    :param require_presentation: When false, a missing ``presentation.mp4``
        is not an error. Local play uses that so a run can start before the
        video exists. The final-submission check keeps the default, true.
    """
    root = submission_dir.expanduser().resolve()
    errors: list[str] = []
    design_dir = root / "design"
    if not design_dir.is_dir():
        errors.append(f"Missing required folder: {design_dir}")
    required_files = REQUIRED_SUBMISSION_FILES
    if not require_presentation:
        required_files = tuple(path for path in REQUIRED_SUBMISSION_FILES if path != "presentation.mp4")
    for relative_path in required_files:
        required_path = root / relative_path
        if not required_path.is_file():
            errors.append(f"Missing required file: {required_path}")
        elif relative_path == "presentation.mp4" and required_path.stat().st_size == 0:
            errors.append("presentation.mp4 is empty — replace it with the team's English video")
    skills_dir = root / "skills"
    if not skills_dir.is_dir():
        errors.append(f"Missing required folder: {skills_dir}")
    elif not list_bundle_skill_ids(root):
        errors.append(f"No skill directory under {skills_dir} contains a SKILL.md file")
    return errors


def validate_skill_frontmatter(skill_dir: Path) -> list[str]:
    """Return error messages for a SKILL.md with missing or malformed frontmatter.

    A valid SKILL.md must open with a YAML front-matter block (``--- ... ---``)
    that contains at least a ``name:`` and a ``description:`` field.  Returns
    an empty list when everything is valid.
    """
    skill_md = skill_dir / "SKILL.md"
    skill_name = skill_dir.name
    if not skill_md.is_file():
        return [f"{skill_name}/SKILL.md: file not found"]
    text = skill_md.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return [f"{skill_name}/SKILL.md: missing YAML frontmatter (file must start with ---)"]
    parts = text.split("---", 2)
    if len(parts) < 3:
        return [f"{skill_name}/SKILL.md: malformed frontmatter (no closing ---)"]
    raw_fm = parts[1]
    try:
        fm = yaml.safe_load(raw_fm)
    except yaml.YAMLError:
        return [f"{skill_name}/SKILL.md: frontmatter is not valid YAML"]
    if not isinstance(fm, dict):
        fm = {}
    errors: list[str] = []
    if not fm.get("name"):
        errors.append(f"{skill_name}/SKILL.md: frontmatter missing required 'name' field")
    if not fm.get("description"):
        errors.append(f"{skill_name}/SKILL.md: frontmatter missing required 'description' field")
    return errors


def validate_submission_contract(submission_dir: Path, *, require_presentation: bool = True) -> dict[str, Any]:
    """Validate layout and return normalized submission metadata.

    :param require_presentation: When false, ``presentation.mp4`` may be
        absent. Local play and install use that. Final validation does not.
    """
    root = resolve_skills_root(submission_dir)
    manifest = load_manifest(root)
    mode = detect_submission_mode(root)
    details: dict[str, Any] = {
        "submission_dir": str(root),
        "submission_name": submission_name(root, manifest),
        "manifest": manifest,
        "submission_mode": mode,
    }
    skill_ids = list_bundle_skill_ids(root)
    _validate_skill_bundle(root, require_presentation=require_presentation)
    details["skill_ids"] = skill_ids
    return details


def detect_submission_mode(submission_dir: Path) -> str:
    """Detect the supported submission mode for ``submission_dir``."""
    root = submission_dir.expanduser().resolve()
    if _is_skill_bundle(root):
        return SUBMISSION_MODE_SKILL_BUNDLE
    msg = f"Unsupported submission format at {root}"
    raise SubmissionError(msg)


def list_bundle_skill_ids(submission_dir: Path) -> list[str]:
    """Return sorted skill ids from a SKILL.md bundle submission."""
    skills_root = submission_dir.expanduser().resolve() / "skills"
    if not skills_root.is_dir():
        return []
    skill_ids = [child.name for child in skills_root.iterdir() if child.is_dir() and (child / "SKILL.md").is_file()]
    return sorted(skill_ids)


def _is_skill_bundle(root: Path) -> bool:
    """Return whether ``root`` looks like a real competition skill bundle."""
    return bool(list_bundle_skill_ids(root))


def _validate_skill_bundle(root: Path, *, require_presentation: bool = True) -> None:
    """Validate the real SKILL.md-based submission bundle.

    :param require_presentation: When false, ``presentation.mp4`` may be absent.
    """
    errors = validate_submission_structure(root, require_presentation=require_presentation)
    if errors:
        raise SubmissionError("; ".join(errors))
