"""JiuwenSwarm MCP configuration helpers."""

from pathlib import Path


def config_mentions_career_emulator(config_path: Path) -> bool:
    """Return whether the JiuwenSwarm config mentions the game MCP server."""
    if not config_path.is_file():
        return False
    text = config_path.read_text(encoding="utf-8")
    from career_sim_runner.constants import EMULATOR_MCP_COMMAND, EMULATOR_MCP_SERVER_NAME

    return EMULATOR_MCP_SERVER_NAME in text and EMULATOR_MCP_COMMAND in text


def env_mentions_db(config_path: Path, db_path: Path) -> bool:
    """Return whether the config mentions the configured database path."""
    if not config_path.is_file():
        return False
    text = config_path.read_text(encoding="utf-8")
    return str(db_path) in text
