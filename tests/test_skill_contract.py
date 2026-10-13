"""Tests for submission validation helpers."""

from pathlib import Path

import pytest

from career_sim_runner.constants import SUBMISSION_MODE_SKILL_BUNDLE
from career_sim_runner.skill_contract import (
    validate_manifest,
    validate_skill_frontmatter,
    validate_submission_contract,
)


def fixture_submission() -> Path:
    """Return the real sample submission path."""
    return Path(__file__).resolve().with_name("fixtures") / "solution"


def test_validate_submission_contract_fixture() -> None:
    """The real sample submission should validate successfully."""
    details = validate_submission_contract(fixture_submission())
    assert details["submission_mode"] == SUBMISSION_MODE_SKILL_BUNDLE
    assert details["submission_name"] == "flash-tomato"


# ---------------------------------------------------------------------------
# validate_manifest
# ---------------------------------------------------------------------------


def test_validate_manifest_valid() -> None:
    """A well-formed manifest should produce no errors."""
    errors = validate_manifest({"team": "my-team", "mode": "agent"})
    assert errors == []


@pytest.mark.parametrize(
    "team",
    [
        "",
        "enter your team name here",
        # case-insensitive
        "Enter Your Team Name Here",
    ],
)
def test_validate_manifest_rejects_placeholder_team(team: str) -> None:
    """Placeholder team names must be flagged."""
    errors = validate_manifest({"team": team, "mode": "agent"})
    assert any("team" in e for e in errors), f"expected team error for {team!r}, got {errors}"


def test_validate_manifest_rejects_invalid_mode() -> None:
    """An unrecognised mode must be flagged."""
    errors = validate_manifest({"team": "my-team", "mode": "unknown-mode"})
    assert any("mode" in e for e in errors)


def test_validate_manifest_multiple_errors() -> None:
    """Both a bad team and a bad mode should each produce an error."""
    errors = validate_manifest({"team": "", "mode": "bad-mode"})
    assert len(errors) == 2


@pytest.mark.parametrize("mode", ["agent", "team"])
def test_validate_manifest_all_supported_modes(mode: str) -> None:
    """Every documented mode should pass validation."""
    errors = validate_manifest({"team": "my-team", "mode": mode})
    assert errors == []


# ---------------------------------------------------------------------------
# validate_skill_frontmatter
# ---------------------------------------------------------------------------


def test_validate_skill_frontmatter_valid(tmp_path: Path) -> None:
    """A SKILL.md with proper frontmatter should produce no errors."""
    skill_dir = tmp_path / "my-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        "---\nname: my-skill\ndescription: Does something useful.\n---\n\nBody text.\n",
        encoding="utf-8",
    )
    assert validate_skill_frontmatter(skill_dir) == []


def test_validate_skill_frontmatter_missing_file(tmp_path: Path) -> None:
    """A directory without SKILL.md should be flagged."""
    skill_dir = tmp_path / "empty-skill"
    skill_dir.mkdir()
    errors = validate_skill_frontmatter(skill_dir)
    assert errors and "not found" in errors[0]


def test_validate_skill_frontmatter_no_frontmatter(tmp_path: Path) -> None:
    """A SKILL.md that does not start with --- should be flagged."""
    skill_dir = tmp_path / "bad-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("Just some text without frontmatter.\n", encoding="utf-8")
    errors = validate_skill_frontmatter(skill_dir)
    assert errors and "frontmatter" in errors[0]


def test_validate_skill_frontmatter_missing_name(tmp_path: Path) -> None:
    """A frontmatter block without 'name:' should be flagged."""
    skill_dir = tmp_path / "no-name-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        "---\ndescription: A skill without a name field.\n---\n",
        encoding="utf-8",
    )
    errors = validate_skill_frontmatter(skill_dir)
    assert any("name" in e for e in errors)
    assert not any("description" in e for e in errors)


def test_validate_skill_frontmatter_missing_description(tmp_path: Path) -> None:
    """A frontmatter block without 'description:' should be flagged."""
    skill_dir = tmp_path / "no-desc-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        "---\nname: no-desc-skill\n---\n",
        encoding="utf-8",
    )
    errors = validate_skill_frontmatter(skill_dir)
    assert any("description" in e for e in errors)
    assert len(errors) == 1


def test_validate_skill_frontmatter_missing_both(tmp_path: Path) -> None:
    """A frontmatter block missing both fields should produce two errors."""
    skill_dir = tmp_path / "empty-fm-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("---\n---\n", encoding="utf-8")
    errors = validate_skill_frontmatter(skill_dir)
    assert len(errors) == 2


def test_validate_skill_frontmatter_invalid_yaml(tmp_path: Path) -> None:
    """A frontmatter block with invalid YAML should be flagged."""
    skill_dir = tmp_path / "bad-yaml-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        "---\n: :\n  bad:\n    - [\n---\n",
        encoding="utf-8",
    )
    errors = validate_skill_frontmatter(skill_dir)
    assert errors and "not valid YAML" in errors[0]


def test_validate_skill_frontmatter_unclosed_block(tmp_path: Path) -> None:
    """A frontmatter block that never closes should be flagged."""
    skill_dir = tmp_path / "unclosed-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("---\nname: x\ndescription: y\n", encoding="utf-8")
    errors = validate_skill_frontmatter(skill_dir)
    assert errors and "malformed" in errors[0]


def test_validate_skill_frontmatter_fixture() -> None:
    """The real fixture skill should pass frontmatter validation."""
    skill_dir = fixture_submission() / "skills" / "dummy-skill"
    assert validate_skill_frontmatter(skill_dir) == []
