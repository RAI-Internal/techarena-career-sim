"""Data models used by the standalone participant runner."""

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class ValidationCheck:
    """One preflight validation result."""

    name: str
    ok: bool
    detail: str

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-safe dictionary."""
        return asdict(self)


@dataclass
class ValidationReport:
    """Collection of preflight validation results."""

    checks: list[ValidationCheck] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        """Return whether all checks passed."""
        return all(check.ok for check in self.checks)

    def add(self, name: str, ok: bool, detail: str) -> None:
        """Append one validation result."""
        self.checks.append(ValidationCheck(name=name, ok=ok, detail=detail))

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-safe dictionary."""
        return {
            "ok": self.ok,
            "checks": [check.to_dict() for check in self.checks],
        }


@dataclass
class TokenUsage:
    """Token usage summary for one run."""

    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    total_cost: float = 0.0
    by_model: dict[str, dict[str, int | float]] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-safe dictionary."""
        return asdict(self)


@dataclass
class InstallRecord:
    """Metadata for one installed participant submission."""

    submission_dir: str
    submission_name: str
    skill_dir: str
    skill_name: str
    manifest: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-safe dictionary."""
        return asdict(self)


@dataclass
class ScoreReport:
    """Final participant-facing score report."""

    submission_name: str
    submission_dir: str
    skill_name: str
    drive_session_id: str
    session_id: str
    play_exit_code: int
    termination_reason: str | None
    token_usage: TokenUsage
    ending_score: dict[str, Any]
    output_dir: str
    events_log: str | None
    transcript_log: str | None
    scored_at: str

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-safe dictionary."""
        payload = asdict(self)
        usage = self.token_usage.to_dict()
        usage["by_model"] = {k: v for k, v in usage.get("by_model", {}).items() if any(v.values())}
        payload["token_usage"] = usage
        return payload
