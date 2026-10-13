"""Tests for WebSocket transcript reconstruction."""

from career_sim_runner.transcript import StreamCollector


def test_stream_collector_reassembles_text_and_usage(tmp_path) -> None:
    """Collector should buffer text and aggregate usage."""

    collector = StreamCollector(log_dir=tmp_path)
    collector.feed_frame({"body": {"text": "SESSION_ID=abc123"}})
    collector.feed_frame(
        {
            "event_type": "chat.usage_summary",
            "usage": {"input_tokens": 10, "output_tokens": 5, "total_tokens": 15},
            "model": "demo-model",
            "is_final": True,
            "response_kind": "e2a.complete",
        }
    )
    collector.finalize()

    assert "SESSION_ID=abc123" in collector.transcript
    assert collector.totals.total_tokens == 15
    assert collector.events_path is not None and collector.events_path.is_file()
    assert collector.transcript_path is not None and collector.transcript_path.is_file()


def test_stream_collector_skips_reasoning_deltas(tmp_path) -> None:
    """E2A reasoning chunks must not appear in the transcript."""

    collector = StreamCollector(log_dir=tmp_path)
    collector.feed_frame({"body": {"delta_kind": "text", "delta": "visible "}})
    collector.feed_frame(
        {
            "response_kind": "e2a.chunk",
            "body": {
                "delta_kind": "reasoning",
                "delta": ("The system reminder is just runtime state (prompt-attachment), not related to the game."),
            },
        }
    )
    collector.feed_frame({"body": {"delta_kind": "text", "delta": "Health 5"}})
    collector.finalize()

    assert collector.transcript == "visible Health 5"
    assert "system reminder" not in collector.transcript
