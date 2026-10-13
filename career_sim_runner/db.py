"""Database helpers for Career Emulator session results."""

import json
import os
from pathlib import Path
from typing import Any

import aiosqlite


async def latest_session_id(db_path: Path) -> str | None:
    """Return the most recently updated session id."""
    if not db_path.is_file():
        return None
    async with aiosqlite.connect(db_path) as database:
        cursor = await database.execute("SELECT session_id FROM sessions ORDER BY updated_at DESC LIMIT 1")
        row = await cursor.fetchone()
        if row is None:
            return None
        return str(row[0])


async def read_session_payload(db_path: Path, session_id: str) -> dict[str, Any]:
    """Load one persisted raw session payload."""
    if not db_path.is_file():
        return {}
    async with aiosqlite.connect(db_path) as database:
        cursor = await database.execute("SELECT payload FROM sessions WHERE session_id = ?", (session_id,))
        row = await cursor.fetchone()
        if row is None:
            return {}
        return json.loads(str(row[0]))


async def read_ending_score(db_path: Path, session_id: str) -> dict[str, Any]:
    """Read the objective ending score for one session."""
    payload = await read_session_payload(db_path, session_id)
    ending_score = payload.get("ending_score")
    if isinstance(ending_score, dict) and ending_score:
        return ending_score
    import career_emulator.game  # pylint: disable=import-outside-toplevel

    os.environ["CAREER_EMULATOR_DB"] = str(db_path)
    engine = career_emulator.game.GameEngine()
    observation = (await engine.observe(session_id)).to_mcp_dict()
    return observation.get("ending_score") or {}
