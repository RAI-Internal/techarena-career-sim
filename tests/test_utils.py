"""Tests for prompt text normalization."""

import pytest

from career_sim_runner.utils import normalize_text

_CASES: list[tuple[str, str]] = [
    ("", ""),
    ("hello", "hello"),
    ("Hello World", "Hello World"),
    ("ABC123", "ABC123"),
    ("snake_case", "snake_case"),
    ("\t", "\t"),
    ("\n", "\n"),
    ("a\tb", "a\tb"),
    ("a\nb", "a\nb"),
    ("  trim  ", "  trim  "),
    ("line1\nline2", "line1\nline2"),
    ("a\r\nb", "a\nb"),
    ("!", "!"),
    ("?", "?"),
    ("(parens)", "(parens)"),
    ("a-b_c.d", "a-b_c.d"),
    ("@#$%", "@#$%"),
    ("quote\"tick'", "quote\"tick'"),
    ("[brackets]{braces}", "[brackets]{braces}"),
    ("path/to\\file", "path/to\\file"),
    ("a:b;c", "a:b;c"),
    ("café", "café"),
    ("日本語", "日本語"),
    ("Привет", "Привет"),
    ("mixedLatinAndEnglish", "mixedLatinAndEnglish"),
    ("«»!? ", "«»!? "),
    ("«guillemets»", "«guillemets»"),
    ("—em dash—", "—em dash—"),
    ("…", "…"),
    ("• bullet", "• bullet"),
    ("\uff01", "\uff01"),
    ("😀", ""),
    ("hello😀world", "helloworld"),
    ("🎉party🎊", "party"),
    ("©®™", ""),
    ("°±", ""),
    ("\x00", ""),
    ("\x01\x02", ""),
    ("a\x00b", "ab"),
    ("\x0b", ""),
    ("\u2028", ""),
    ("\u00ad", ""),
    ("a\u00a0b", "ab"),
    ("a\u200bb", "ab"),
    ("\u3000", ""),
    ("e\u0301", "e"),
    ("é", "é"),
    ("Task-1: finish report (due Friday)!", "Task-1: finish report (due Friday)!"),
    ("Version 2.0—released; see README.", "Version 2.0—released; see README."),
    ("email@user.name\t+\temoji🔥end", "email@user.name\t+\temojiend"),
    ("`", "`"),
    ("``", "``"),
    ("```", "```"),
    ("````", "```"),
    ("`````", "```"),
    ("``````````", "```"),
    ("pre``````post", "pre```post"),
    ("````a````", "```a```"),
    ("</think>````a````", "```a```"),
]


@pytest.mark.parametrize(("raw", "expected"), _CASES)
def test_normalize_text(raw: str, expected: str) -> None:
    """Prompt text keeps readable characters and drops special tokens."""
    assert normalize_text(raw) == expected
