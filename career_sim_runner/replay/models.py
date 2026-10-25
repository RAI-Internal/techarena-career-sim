"""Dataclass models for replay event parsing."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class GameChoice:
    """One selectable action offered by the emulator."""

    choice: int
    action: str
    description: str = ""


@dataclass
class ObserveSnapshot:
    """Parsed observation returned by career-emulator observe."""

    ts: str
    month: int
    quarter: int
    year: int
    status: dict[str, Any]
    event_title: str
    event_description: str
    month_feed: str
    choices: list[GameChoice] = field(default_factory=list)
    ending_score: dict[str, Any] | None = None
    alive: bool = True
    failed: bool = False
    failure_reason: str | None = None


@dataclass
class DecisionTurn:
    """One observe → take_action pair."""

    step: int
    observe: ObserveSnapshot
    choice: int | None = None
    choice_action: str = ""
    notes: str = ""
