"""Tests for participant score extraction."""

from pathlib import Path

from career_sim_runner.score import extract_ending_score_from_transcript


def test_extract_ending_score_from_transcript(tmp_path: Path) -> None:
    """The transcript parser should recover the final JSON score block."""
    transcript = tmp_path / "transcript.log"
    transcript.write_text(
        """
Some earlier logs.

```json
{"broken": true
```

## Game over

```json
{
  "outcome": "eliminated",
  "survival_months": 6,
  "completed": false,
  "quantitative_score": 23.68,
  "competition_partial_score": 14.21
}
```
""".strip()
        + "\n",
        encoding="utf-8",
    )
    ending_score = extract_ending_score_from_transcript(transcript)
    assert ending_score["outcome"] == "eliminated"
    assert ending_score["competition_partial_score"] == 14.21
