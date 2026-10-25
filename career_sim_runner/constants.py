"""Shared constants for the standalone participant runner."""

from pathlib import Path

RUNNER_PACKAGE_DIR: Path = Path(__file__).resolve().parent
REPO_ROOT: Path = RUNNER_PACKAGE_DIR.parent
DEFAULT_INSTANCE_NAME: str = "career_emu"
INSTANCES_ROOT: Path = Path.home() / ".jiuwenswarm-instances"
INSTANCE_ROOT: Path = INSTANCES_ROOT / DEFAULT_INSTANCE_NAME
RUNTIME_ROOT: Path = REPO_ROOT / ".career_sim_runner" / DEFAULT_INSTANCE_NAME
DEFAULT_DB_PATH: Path = RUNTIME_ROOT / "career_emulator.sqlite3"
DEFAULT_EMULATOR_LOG_DIR: Path = RUNTIME_ROOT / "emulator_logs"
DEFAULT_RUNS_DIR: Path = RUNTIME_ROOT / "runs"
DEFAULT_OUTPUT_ROOT: Path = RUNTIME_ROOT / "outputs"
DRIVE_SESSION_PREFIX: str = "career-sim-runner"
DEFAULT_TIMEOUT_S: float = 7200.0

JWS_DATA_DIR_ENV: str = "JIUWENSWARM_DATA_DIR"
ACTIVE_INSTALL_FILE: str = "active_install.json"
LAST_DRIVE_SESSION_FILE: str = "last_drive_session.txt"
LAST_OUTPUT_DIR_FILE: str = "last_output_dir.txt"

EMULATOR_MCP_SERVER_NAME: str = "career-emulator-engine"
EMULATOR_MCP_COMMAND: str = "career-emulator-engine-mcp"
EMULATOR_MCP_TOOL_PREFIX: str = "mcp_career-emulator-engine_"
EMULATOR_CLI: str = "career-emulator-engine"

CAREER_EMULATOR_ACTIVE_LONG_CHAIN_LIMIT: int = 1
CAREER_EMULATOR_MONTHLY_EVENT_LIMIT: int = 3
CAREER_EMULATOR_MAX_NOTE_LENGTH: int = 1000
SUBMISSION_MODE_SKILL_BUNDLE: str = "skill_bundle"
# This competition permits JiuwenSwarm single-agent mode only.
SUPPORTED_RUN_MODES: frozenset[str] = frozenset({"agent"})

MEMORY_MD_CONTENT = """
### Long-term memory

### What to store here

Save anything that helps you work more efficiently. This is your persistent reference.

For example:

- Project information
- User settings and preferences related to skill execution
""".strip()
