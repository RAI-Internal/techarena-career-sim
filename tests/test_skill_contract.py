"""Tests for submission validation helpers."""

import json
import sys
from pathlib import Path

import pytest

from career_sim_runner.constants import SUBMISSION_MODE_SKILL_BUNDLE
from career_sim_runner.skill_contract import (
    REQUIRED_SUBMISSION_FILES,
    SubmissionError,
    validate_manifest,
    validate_skill_frontmatter,
    validate_submission_contract,
    validate_submission_structure,
)
from career_sim_runner.validate import validate_submission


def fixture_submission() -> Path:
    """Return the real sample submission path."""
    return Path(__file__).resolve().with_name("fixtures") / "solution"


def test_validate_submission_contract_fixture() -> None:
    """The real sample submission should validate successfully."""
    details = validate_submission_contract(fixture_submission())
    assert details["submission_mode"] == SUBMISSION_MODE_SKILL_BUNDLE
    assert details["submission_name"] == "flash-tomato"


def build_complete_submission(root: Path) -> Path:
    """Create a minimal submission with every required file and folder."""
    (root / "design").mkdir(parents=True)
    (root / "skills" / "dummy-skill").mkdir(parents=True)
    (root / "manifest.json").write_text(
        '{"team": "my-team", "name": "my-submission", "mode": "agent", "instruction": ""}',
        encoding="utf-8",
    )
    (root / "README.md").write_text("# My Submission\n", encoding="utf-8")
    (root / "presentation.mp4").write_bytes(b"placeholder")
    (root / "design" / "skills_design.md").write_text("# Skills Design\n", encoding="utf-8")
    (root / "design" / "decision_report.md").write_text("# Decision Report\n", encoding="utf-8")
    (root / "skills" / "dummy-skill" / "SKILL.md").write_text(
        "---\nname: dummy-skill\ndescription: A dummy skill.\n---\n\nBody text.\n",
        encoding="utf-8",
    )
    return root


# ---------------------------------------------------------------------------
# validate_submission_structure
# ---------------------------------------------------------------------------


def test_validate_submission_structure_complete(tmp_path: Path) -> None:
    """A submission with every required item should produce no errors."""
    assert validate_submission_structure(build_complete_submission(tmp_path)) == []


def test_validate_submission_structure_fixture() -> None:
    """The real sample submission should contain the full required structure."""
    assert validate_submission_structure(fixture_submission()) == []


@pytest.mark.parametrize("relative_path", REQUIRED_SUBMISSION_FILES)
def test_validate_submission_structure_missing_required_file(tmp_path: Path, relative_path: str) -> None:
    """Removing any one required file should be reported by name."""
    root = build_complete_submission(tmp_path)
    (root / relative_path).unlink()
    errors = validate_submission_structure(root)
    assert any(relative_path in err for err in errors), f"expected error for {relative_path}, got {errors}"


def test_validate_submission_structure_missing_design_folder(tmp_path: Path) -> None:
    """A missing design/ folder should be reported together with its documents."""
    root = build_complete_submission(tmp_path)
    (root / "design" / "skills_design.md").unlink()
    (root / "design" / "decision_report.md").unlink()
    (root / "design").rmdir()
    errors = validate_submission_structure(root)
    assert any("design" in err for err in errors)


def test_validate_submission_structure_no_skill_file(tmp_path: Path) -> None:
    """An empty skills/ tree without any SKILL.md should be reported."""
    root = build_complete_submission(tmp_path)
    (root / "skills" / "dummy-skill" / "SKILL.md").unlink()
    errors = validate_submission_structure(root)
    assert any("SKILL.md" in err for err in errors)


def test_validate_submission_contract_rejects_missing_design_document(tmp_path: Path) -> None:
    """The submission contract should reject a missing design document."""
    root = build_complete_submission(tmp_path)
    (root / "design" / "decision_report.md").unlink()
    with pytest.raises(SubmissionError, match="decision_report"):
        validate_submission_contract(root)


def test_validate_submission_reports_missing_structure(tmp_path: Path) -> None:
    """The validate command should fail the structure check for a missing file."""
    root = build_complete_submission(tmp_path)
    (root / "README.md").unlink()
    report = validate_submission(root)
    assert not report.ok
    structure_checks = [check for check in report.checks if check.name == "submission-structure"]
    assert structure_checks and not any(check.ok for check in structure_checks)
    assert any("README.md" in check.detail for check in structure_checks)


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
        "your-team-name",
        # case-insensitive
        "Enter Your Team Name Here",
        "Your-Team-Name",
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


def test_validate_manifest_rejects_team_mode() -> None:
    """JiuwenSwarm team mode is prohibited and must fail validation."""
    errors = validate_manifest({"team": "my-team", "mode": "team"})
    assert any("mode" in error and "team" in error for error in errors)


def test_validate_submission_structure_rejects_empty_presentation(tmp_path: Path) -> None:
    """A zero-byte presentation.mp4 fails the final check and is ignored for local play."""
    root = build_complete_submission(tmp_path)
    (root / "presentation.mp4").write_bytes(b"")
    errors = validate_submission_structure(root)
    assert any("empty" in error for error in errors)
    assert validate_submission_structure(root, require_presentation=False) == []


def test_validate_submission_structure_local_run_allows_missing_presentation(tmp_path: Path) -> None:
    """A local run may omit presentation.mp4; the final check still requires it."""
    root = build_complete_submission(tmp_path)
    (root / "presentation.mp4").unlink()
    assert validate_submission_structure(root, require_presentation=False) == []
    errors = validate_submission_structure(root)
    assert any("presentation.mp4" in error for error in errors)


def test_validate_submission_contract_local_run_allows_missing_presentation(tmp_path: Path) -> None:
    """Installing a local run must accept a submission that has no video yet."""
    root = build_complete_submission(tmp_path)
    (root / "presentation.mp4").unlink()
    details = validate_submission_contract(root, require_presentation=False)
    assert details["submission_mode"] == SUBMISSION_MODE_SKILL_BUNDLE
    with pytest.raises(SubmissionError, match="presentation.mp4"):
        validate_submission_contract(root)


def test_validate_command_checks_submission_only(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The validate command must pass without contacting JiuwenSwarm."""
    root = build_complete_submission(tmp_path)
    monkeypatch.setattr(sys, "argv", ["career_sim_runner", "validate", "--submission", str(root)])

    def fail_if_called(*args, **kwargs) -> None:
        raise AssertionError("JiuwenSwarm should not be contacted")

    monkeypatch.setattr("career_sim_runner.cli.resolve_instance_ws_url", fail_if_called)
    monkeypatch.setattr("career_sim_runner.validate.validate_environment", fail_if_called)
    from career_sim_runner.cli import main

    assert main() == 0


def test_validate_command_rejects_team_mode(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """The validate command must fail when the manifest requests team mode."""
    root = build_complete_submission(tmp_path)
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    manifest["mode"] = "team"
    (root / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["career_sim_runner", "validate", "--submission", str(root)])
    from career_sim_runner.cli import main

    assert main() == 1
    assert "team" in capsys.readouterr().out


def test_validate_command_still_requires_presentation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """The final-submission check must still report a missing video."""
    root = build_complete_submission(tmp_path)
    (root / "presentation.mp4").unlink()
    monkeypatch.setattr(sys, "argv", ["career_sim_runner", "validate", "--submission", str(root)])
    from career_sim_runner.cli import main

    assert main() == 1
    assert "presentation.mp4" in capsys.readouterr().out


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
