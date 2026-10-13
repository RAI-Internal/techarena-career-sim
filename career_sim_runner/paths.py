"""Path helpers for the standalone participant runner."""

import os
from datetime import datetime, timezone
from pathlib import Path

from career_sim_runner.constants import (
    ACTIVE_INSTALL_FILE,
    DEFAULT_DB_PATH,
    DEFAULT_EMULATOR_LOG_DIR,
    DEFAULT_INSTANCE_NAME,
    DEFAULT_OUTPUT_ROOT,
    DEFAULT_RUNS_DIR,
    INSTANCE_ROOT,
    JWS_DATA_DIR_ENV,
    LAST_DRIVE_SESSION_FILE,
    LAST_OUTPUT_DIR_FILE,
    REPO_ROOT,
    RUNTIME_ROOT,
)


def repo_root() -> Path:
    """Return the repository root."""
    return REPO_ROOT


def runtime_root() -> Path:
    """Return the runner's state directory."""
    return RUNTIME_ROOT


def ensure_runtime_dirs() -> None:
    """Create runner-owned directories if missing."""
    runtime_root().mkdir(parents=True, exist_ok=True)
    default_runs_dir().mkdir(parents=True, exist_ok=True)
    default_output_root().mkdir(parents=True, exist_ok=True)
    default_emulator_log_dir().mkdir(parents=True, exist_ok=True)


def default_db_path() -> Path:
    """Return the default shared Career Emulator database path."""
    return DEFAULT_DB_PATH


def default_emulator_log_dir() -> Path:
    """Return the default Career Emulator log directory."""
    return DEFAULT_EMULATOR_LOG_DIR


def default_runs_dir() -> Path:
    """Return the directory used for runner-owned artifacts."""
    return DEFAULT_RUNS_DIR


def default_output_root() -> Path:
    """Return the directory used for participant-facing outputs."""
    return DEFAULT_OUTPUT_ROOT


def timestamped_output_dir(label: str) -> Path:
    """Return a unique output directory for one run."""
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return default_output_root() / label / stamp


def latest_output_dir(label: str) -> Path | None:
    """Return the most recent existing output directory for *label*, if any."""
    parent = default_output_root() / label
    if not parent.is_dir():
        return None
    candidates = sorted(
        (d for d in parent.iterdir() if d.is_dir()),
        key=lambda p: p.name,
        reverse=True,
    )
    return candidates[0] if candidates else None


def default_instance_name() -> str:
    """Return the supported JiuwenSwarm instance name."""
    return DEFAULT_INSTANCE_NAME


def instance_root() -> Path:
    """Return the configured JiuwenSwarm instance directory."""
    return INSTANCE_ROOT


def jiuwenswarm_data_dir() -> Path:
    """Return JiuwenSwarm's data directory."""
    override = os.environ.get(JWS_DATA_DIR_ENV, "").strip()
    if override:
        return Path(override).expanduser().resolve()
    return instance_root()


def jiuwenswarm_config_dir() -> Path:
    """Return JiuwenSwarm's config directory."""
    return jiuwenswarm_data_dir() / "config"


def jiuwenswarm_config_path() -> Path:
    """Return JiuwenSwarm's main config path."""
    return jiuwenswarm_config_dir() / "config.yaml"


def jiuwenswarm_env_path() -> Path:
    """Return JiuwenSwarm's environment file path."""
    return jiuwenswarm_config_dir() / ".env"


def jiuwenswarm_skills_dir() -> Path:
    """Return the active JiuwenSwarm skills directory."""
    return jiuwenswarm_data_dir() / "agent" / "workspace" / "skills"


def jiuwenswarm_skills_state_path() -> Path:
    """Return the instance-local skills registry file."""
    return jiuwenswarm_skills_dir() / "skills_state.json"


def active_install_path() -> Path:
    """Return the runner-managed active-install metadata path."""
    return runtime_root() / ACTIVE_INSTALL_FILE


def last_drive_session_path() -> Path:
    """Return the runner-managed JiuwenSwarm conversation id path."""
    return runtime_root() / LAST_DRIVE_SESSION_FILE


def last_output_dir_path() -> Path:
    """Return the runner-managed last output directory path."""
    return runtime_root() / LAST_OUTPUT_DIR_FILE
