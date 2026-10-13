"""Tests for participant submission installation."""

from pathlib import Path

from career_sim_runner.install import install_submission


def fixture_submission() -> Path:
    """Return the real sample submission path."""
    return Path(__file__).resolve().with_name("fixtures") / "solution"


def test_install_submission_generates_skill(tmp_path: Path) -> None:
    """Installing a real submission should mirror only participant skills."""
    skills_dir = tmp_path / "skills"
    (tmp_path / "memory").mkdir()
    record = install_submission(fixture_submission(), skills_dir=skills_dir)

    assert Path(record.skill_dir) == skills_dir
    assert record.submission_name == "flash-tomato"
    assert record.manifest["submission_mode"] == "skill_bundle"
    assert sorted(record.manifest["participant_skill_names"]) == ["dummy-skill"]
    assert record.skill_name == "submission-skills"
    assert not (skills_dir / "career-emulator-player").exists()
    assert (skills_dir / "dummy-skill" / "SKILL.md").is_file()
