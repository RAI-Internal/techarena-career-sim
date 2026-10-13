"""Reassemble JiuwenSwarm WebSocket streams into readable logs."""

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from career_sim_runner.models import TokenUsage

EventCallback = Callable[[dict[str, Any]], None]


def _walk(obj: Any) -> list[dict[str, Any]]:
    """Walk nested JSON-like data and collect dictionaries."""
    found: list[dict[str, Any]] = []
    stack: list[Any] = [obj]
    while stack:
        node = stack.pop()
        if isinstance(node, dict):
            found.append(node)
            stack.extend(node.values())
        elif isinstance(node, list):
            stack.extend(node)
    return found


def _extract_text(frame: dict[str, Any]) -> str:
    """Extract visible text-like payload fragments from one frame.

    E2A ``e2a.chunk`` frames with ``delta_kind=reasoning`` are skipped so
    reasoning content is not written into the transcript.
    """
    for node in _walk(frame):
        if node.get("delta_kind") == "reasoning":
            continue
        for key in ("text", "content", "delta"):
            value = node.get(key)
            if isinstance(value, str) and value.strip():
                return value
    body = frame.get("body")
    if isinstance(body, str):
        return body
    if isinstance(body, dict):
        return _extract_text(body)
    return ""


@dataclass
class StreamCollector:
    """Structured collector for one agent session."""

    log_dir: Path
    on_event: EventCallback | None = None
    totals: TokenUsage = field(default_factory=TokenUsage)
    transcript: str = ""
    events_path: Path | None = None
    transcript_path: Path | None = None
    _text_buffer: str = ""
    _event_count: int = 0

    def __post_init__(self) -> None:
        """Initialize log file paths."""
        self.log_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        self.events_path = self.log_dir / f"events-{stamp}.jsonl"
        self.transcript_path = self.log_dir / f"transcript-{stamp}.log"

    def _append_event(self, kind: str, payload: dict[str, Any]) -> None:
        """Write one structured event."""
        self._event_count += 1
        record = {
            "seq": self._event_count,
            "ts": datetime.now(timezone.utc).isoformat(),
            "kind": kind,
            **payload,
        }
        assert self.events_path is not None
        with self.events_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
        if self.on_event is not None:
            self.on_event(record)

    def _absorb_usage(self, usage: dict[str, Any], model: str) -> None:
        """Add one usage block into running totals."""
        bucket = self.totals.by_model.setdefault(
            model,
            {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0, "total_cost": 0.0},
        )
        for key in ("input_tokens", "output_tokens", "total_tokens"):
            value = int(usage.get(key, 0) or 0)
            setattr(self.totals, key, getattr(self.totals, key) + value)
            bucket[key] += value
        cost = float(usage.get("total_cost") or 0)
        self.totals.total_cost += cost
        bucket["total_cost"] += cost

    def _flush_text(self, force: bool = False) -> None:
        """Flush buffered text into the transcript file."""
        if not self._text_buffer:
            return
        if not force and "\n" not in self._text_buffer and len(self._text_buffer) < 120:
            return
        chunk = self._text_buffer
        self._text_buffer = ""
        self.transcript += chunk
        assert self.transcript_path is not None
        with self.transcript_path.open("a", encoding="utf-8") as handle:
            handle.write(chunk)

    def feed_frame(self, frame: dict[str, Any]) -> None:
        """Ingest one decoded WebSocket frame."""
        kind = str(frame.get("response_kind") or "")
        status = str(frame.get("status") or "")

        for node in _walk(frame):
            event_type = node.get("event_type")
            if event_type == "chat.usage_summary":
                usage = node.get("usage") or {}
                model = str(node.get("model") or "unknown")
                if isinstance(usage, dict):
                    self._absorb_usage(usage, model)
                    self._append_event("usage", {"model": model, "usage": usage})
            elif event_type in {"chat.tool_call", "chat.tool_result"}:
                self._flush_text(force=True)
                self._append_event(str(event_type).replace("chat.", ""), {"payload": node})

        text = _extract_text(frame)
        if text:
            self._text_buffer += text

        if frame.get("is_final") or kind in {"e2a.complete", "e2a.error"}:
            self._flush_text(force=True)
            self._append_event(
                "frame_final",
                {"response_kind": kind, "status": status, "is_final": bool(frame.get("is_final"))},
            )
        elif "\n" in self._text_buffer:
            self._flush_text(force=True)

    def finalize(self) -> None:
        """Flush remaining buffered text."""
        self._flush_text(force=True)
