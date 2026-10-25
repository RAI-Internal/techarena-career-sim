"""Install a participant submission into JiuwenSwarm's skill workspace."""

import json
import os
import shutil
from itertools import chain
from pathlib import Path
from typing import Any

from career_sim_runner.constants import MEMORY_MD_CONTENT, SUBMISSION_MODE_SKILL_BUNDLE
from career_sim_runner.models import InstallRecord
from career_sim_runner.paths import (
    active_install_path,
    ensure_runtime_dirs,
    jiuwenswarm_data_dir,
    jiuwenswarm_skills_dir,
    jiuwenswarm_skills_state_path,
)
from career_sim_runner.setup import ensure_instance_initialized
from career_sim_runner.skill_contract import (
    list_bundle_skill_ids,
    load_manifest,
    resolve_skills_root,
    validate_submission_contract,
)
from career_sim_runner.utils import normalize_text


def install_submission(
    submission_dir: Path,
    skills_dir: Path | None = None,
    *,
    require_presentation: bool = True,
) -> InstallRecord:
    """Install a participant submission into JiuwenSwarm.

    :param require_presentation: When false, ``presentation.mp4`` may be
        absent. Local play passes false. Final validation does not install
        through this flag.
    """
    ensure_runtime_dirs()
    ensure_instance_initialized()
    root = resolve_skills_root(submission_dir)
    details = validate_submission_contract(root, require_presentation=require_presentation)
    mode = str(details["submission_mode"])
    manifest = load_manifest(root)
    label = str(details["submission_name"])
    resolved_skills_dir = skills_dir or jiuwenswarm_skills_dir()

    # Clean up
    todo_dir = resolved_skills_dir.with_name("todo")
    hist_dir = resolved_skills_dir.with_name(".agent_history")
    session_dir = resolved_skills_dir.parent.with_name("sessions")
    team_dir = session_dir.parent.with_name(".agent_teams")
    mem_dir = resolved_skills_dir.with_name("memory")
    for file in chain(
        todo_dir.glob("*"), hist_dir.glob("*"), session_dir.glob("*"), team_dir.glob("*"), mem_dir.glob("*.md")
    ):
        if file.is_file():
            os.remove(file)
        elif file.is_dir():
            shutil.rmtree(file)
    (mem_dir / "MEMORY.md").write_text(MEMORY_MD_CONTENT)

    _reset_skills_workspace(resolved_skills_dir)
    if mode != SUBMISSION_MODE_SKILL_BUNDLE:
        msg = f"Unsupported submission mode: {mode}"
        raise RuntimeError(msg)
    participant_skill_names = _install_skill_bundle(root, resolved_skills_dir)

    record = InstallRecord(
        submission_dir=str(root),
        submission_name=label,
        skill_dir=str(resolved_skills_dir),
        skill_name="submission-skills",
        manifest={
            **manifest,
            "submission_mode": mode,
            "participant_skill_names": participant_skill_names,
        },
    )
    _write_skills_state(
        skills={
            name: resolved_skills_dir / name
            for name in participant_skill_names
            if (resolved_skills_dir / name).is_dir()
        }
    )
    _write_identity_md(participant_skill_names, manifest)
    active_install_path().write_text(json.dumps(record.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    return record


def load_active_install() -> InstallRecord | None:
    """Load the last installed participant submission, if any."""
    path = active_install_path()
    if not path.is_file():
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))
    return InstallRecord(**payload)


def _reset_skills_workspace(skills_dir: Path) -> None:
    """Reset the named-instance skills workspace before each run."""
    skills_dir.mkdir(parents=True, exist_ok=True)
    for child in skills_dir.iterdir():
        if child.name == "skills_state.json":
            continue
        if child.is_dir():
            shutil.rmtree(child)
        else:
            child.unlink()


def _write_skills_state(skills: dict[str, Path]) -> None:
    """Register installed local skills in skills_state.json."""
    state_path = jiuwenswarm_skills_state_path()
    state: dict[str, Any] = {"marketplaces": [], "installed_plugins": [], "local_skills": []}
    if state_path.is_file():
        state = json.loads(state_path.read_text(encoding="utf-8"))
    state.setdefault("marketplaces", [])
    state["installed_plugins"] = []
    state["local_skills"] = [
        {
            "name": skill_name,
            "origin": str(skill_dir),
            "source": "project",
            "enabled": True,
        }
        for skill_name, skill_dir in sorted(skills.items())
    ]
    state["skill_configs"] = {skill_name: {"enabled": True} for skill_name in skills}
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def _install_skill_bundle(submission_root: Path, resolved_skills_dir: Path) -> list[str]:
    """Install the real ``SKILL.md`` bundle into JiuwenSwarm."""
    participant_skill_names = list_bundle_skill_ids(submission_root)
    for skill_name in participant_skill_names:
        shutil.copytree(submission_root / "skills" / skill_name, resolved_skills_dir / skill_name)
    return participant_skill_names


def _write_identity_md(participant_skill_names: list[str], manifest: dict[str, Any]) -> None:
    """Render and write IDENTITY.md to the agent workspace.

    The content persists in the system prompt on every model call via
    ContextAssembleRail, surviving context compression.
    """
    template_path = Path(__file__).resolve().parent / "prompts" / "identity.md"
    template = template_path.read_text(encoding="utf-8")
    skills_text = "- " + "\n- ".join(normalize_text(str(name)) for name in participant_skill_names)
    raw_instruction = str(manifest.get("instruction") or "").strip()
    instruction = normalize_text(raw_instruction) if raw_instruction else "(no extra strategy instructions provided)"
    content = template.format(
        participant_skills=skills_text,
        instruction=instruction,
    )
    dest = jiuwenswarm_data_dir() / "agent" / "workspace" / "IDENTITY.md"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(content, encoding="utf-8")
