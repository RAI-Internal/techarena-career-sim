"""Environment setup helpers for the standalone participant runner."""

import re
import shutil
import subprocess
from functools import lru_cache
from pathlib import Path

from ruamel.yaml import YAML

from career_sim_runner.constants import (
    CAREER_EMULATOR_ACTIVE_LONG_CHAIN_LIMIT,
    CAREER_EMULATOR_MAX_NOTE_LENGTH,
    CAREER_EMULATOR_MONTHLY_EVENT_LIMIT,
    EMULATOR_MCP_COMMAND,
    EMULATOR_MCP_SERVER_NAME,
)
from career_sim_runner.paths import (
    default_db_path,
    default_emulator_log_dir,
    default_instance_name,
    instance_root,
    jiuwenswarm_config_dir,
    jiuwenswarm_config_path,
    jiuwenswarm_env_path,
    repo_root,
)

WINDOWS_BINARY_EXT = re.compile(r"\.(bat|ps1|exe)$", flags=re.IGNORECASE)


def ensure_instance_initialized() -> Path:
    """Create the named JiuwenSwarm instance if needed."""
    root = instance_root()
    if root.exists():
        return root
    subprocess.run(
        ["jiuwenswarm-init", "--name", default_instance_name()],
        check=True,
    )
    return root


def ensure_instance_configured() -> Path:
    """Write the required MCP server entry into the named instance config."""
    ensure_instance_initialized()
    config_path = jiuwenswarm_config_path()
    yaml = YAML()
    yaml.preserve_quotes = True
    with config_path.open("r", encoding="utf-8") as handle:
        data = yaml.load(handle) or {}
    mcp = data.setdefault("mcp", {})
    is_available = tool_availability()
    cwd = is_available["path"]
    if not is_available[EMULATOR_MCP_COMMAND]:
        raise RuntimeError(
            f"\033[41mcareer-emulator-engine[mcp]\033[0m is not installed in the same environment as JiuwenSwarm: {cwd}"
        )
    mcp["servers"] = [
        {
            "name": EMULATOR_MCP_SERVER_NAME,
            "enabled": True,
            "transport": "stdio",
            "command": EMULATOR_MCP_COMMAND,
            "args": ["--update", "skip"],
            "cwd": cwd,
            "env": {
                "CAREER_EMULATOR_DB": str(default_db_path()),
                "CAREER_EMULATOR_LOG_DIR": str(default_emulator_log_dir()),
                "CAREER_EMULATOR_ACTIVE_LONG_CHAIN_LIMIT": str(CAREER_EMULATOR_ACTIVE_LONG_CHAIN_LIMIT),
                "CAREER_EMULATOR_MONTHLY_EVENT_LIMIT": str(CAREER_EMULATOR_MONTHLY_EVENT_LIMIT),
                "CAREER_EMULATOR_MAX_NOTE_LENGTH": str(CAREER_EMULATOR_MAX_NOTE_LENGTH),
            },
        }
    ]
    with config_path.open("w", encoding="utf-8") as handle:
        yaml.dump(data, handle)
    ensure_instance_env_overlay()
    return config_path


# Only competition LLM credentials are copied from the repo ``.env``.
# Provider routing is organiser-controlled in official scoring and must not
# be introduced through participant environment overlays.
INSTANCE_ENV_OVERLAY_KEYS = frozenset({"API_BASE", "API_KEY", "MODEL_NAME"})


def ensure_instance_env_overlay() -> Path:
    """Overlay repo-level ``.env`` values onto the named instance env file."""
    ensure_instance_initialized()
    overlay_path = repo_root() / ".env"
    instance_env_path = jiuwenswarm_env_path()
    if not overlay_path.is_file():
        return instance_env_path
    overlay_values = _read_env_values(overlay_path)
    _apply_env_values(instance_env_path, overlay_values)
    return instance_env_path


def _apply_env_values(path: Path, overlay_values: dict[str, str]) -> None:
    """Apply env overrides in place while preserving unrelated keys."""
    allowed = {
        key: value
        for key, value in overlay_values.items()
        if key in INSTANCE_ENV_OVERLAY_KEYS
    }
    raw_lines = path.read_text(encoding="utf-8").splitlines()
    updated_lines: list[str] = []
    seen: set[str] = set()
    for line in raw_lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in line:
            updated_lines.append(line)
            continue
        key = line.split("=", 1)[0].strip()
        if key in allowed:
            updated_lines.append(f"{key}={allowed[key]}")
            seen.add(key)
        else:
            updated_lines.append(line)
    for key, value in allowed.items():
        if key not in seen:
            updated_lines.append(f"{key}={value}")
    path.write_text("\n".join(updated_lines) + "\n", encoding="utf-8")


def _read_env_values(path: Path) -> dict[str, str]:
    """Parse simple ``KEY=value`` assignments from an env file."""
    values: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def setup_summary() -> dict[str, str]:
    """Return a participant-facing setup summary."""
    ensure_instance_initialized()
    return {
        "instance_name": default_instance_name(),
        "instance_root": str(instance_root()),
        "jiuwenswarm_config_dir": str(jiuwenswarm_config_dir()),
        "jiuwenswarm_config_path": str(jiuwenswarm_config_path()),
        "jiuwenswarm_env_path": str(jiuwenswarm_env_path()),
        "repo_env_overlay_path": str(repo_root() / ".env"),
        "recommended_db_path": str(default_db_path()),
    }


@lru_cache(maxsize=1)
def tool_availability() -> dict[str, bool | str]:
    """Return whether key local commands are available."""
    jiuwenswarm_path = shutil.which("jiuwenswarm-start")
    if isinstance(jiuwenswarm_path, str):
        cwd = WINDOWS_BINARY_EXT.sub("", jiuwenswarm_path, count=1).removesuffix("jiuwenswarm-start")
    else:
        cwd = ""
    return {
        EMULATOR_MCP_COMMAND: bool(
            list(Path(cwd).glob(f"{EMULATOR_MCP_COMMAND}*")) and list(Path(cwd).glob("fastmcp*"))
        ),
        "jiuwenswarm-start": jiuwenswarm_path is not None,
        "path": cwd,
    }


def resolve_instance_ws_url() -> str:
    """Resolve the AgentServer websocket URL from ``jiuwenswarm-start --list`` output."""
    result = subprocess.run(
        ["jiuwenswarm-start", "--list"],
        check=True,
        capture_output=True,
        text=True,
    )
    instance = default_instance_name()
    for line in result.stdout.splitlines():
        parts = line.split()
        if len(parts) >= 5 and parts[0] == instance:
            ports = parts[-1]
            agent_server_port = ports.split("/", 1)[0]
            return f"ws://127.0.0.1:{agent_server_port}"
    raise RuntimeError(f"JiuwenSwarm does not seem to have instance '{instance}'")
