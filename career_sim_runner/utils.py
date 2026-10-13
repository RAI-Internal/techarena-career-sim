"""Utility helper functions."""

import re
import string
import unicodedata


def normalize_text(raw: str) -> str:
    """Normalize input text for prompts."""
    filtered = "".join(
        ch
        for ch in SPECIAL_TOKEN_PATTERN.sub("", raw)
        if (NORMAL_CHAR_PATTERN.match(ch) or ch in ENGLISH_PUNCT_SET or unicodedata.category(ch).startswith("P"))
    )
    return FOLD_CODEBLOCKS.sub("```", filtered)


SPECIAL_TOKEN_REGEXES = [
    # ChatML / OpenAI-like
    r"<\|\W*im_start\W*\|>",
    r"<\|\W*im_end\W*\|>",
    # Llama
    r"\[\W*INST\W*\]",
    r"<<\W*SYS\W*>>",
    r"<\W*s\W*>",
    r"<\|\W*begin_of_text\W*\|>",
    r"<\|\W*end_of_text\W*\|>",
    r"<\|\W*start_header_id\W*\|>",
    r"<\|\W*end_header_id\W*\|>",
    r"<\|\W*eot_id\W*\|>",
    # Tool / function-call wrappers
    r"<\W*tool_call\W*>",
    r"<\W*tool_response\W*>",
    # DeepSeek / Qwen reasoning mode
    r"<\W*think\W*>",
    # Other tokenizer specials
    r"<\W*pad\W*>",
    r"<\W*unk\W*>",
    r"<\W*mask\W*>",
    r"<\|\W*endoftext\W*\|>",
    r"<\|\W*system\W*\|>",
    r"<\|\W*user\W*\|>",
    r"<\|\W*assistant\W*\|>",
]

SPECIAL_TOKEN_PATTERN = re.compile(
    r"|".join(rf"(?:{pattern})" for pattern in SPECIAL_TOKEN_REGEXES),
    flags=re.IGNORECASE,
)

NORMAL_CHAR_PATTERN = re.compile(r"[\w\t\n ]")
ENGLISH_PUNCT_SET = set(string.punctuation)
FOLD_CODEBLOCKS = re.compile(r"`{4,}")

if __name__ == "__main__":
    _NORMALIZE_TEXT_CASES: list[tuple[str, str]] = [
        # empty and plain ASCII
        ("", ""),
        ("hello", "hello"),
        ("Hello World", "Hello World"),
        ("ABC123", "ABC123"),
        ("snake_case", "snake_case"),
        # whitespace kept by is_normal_char
        ("\t", "\t"),
        ("\n", "\n"),
        ("a\tb", "a\tb"),
        ("a\nb", "a\nb"),
        ("  trim  ", "  trim  "),
        ("line1\nline2", "line1\nline2"),
        ("a\r\nb", "a\nb"),  # \\r is Cc, not kept
        # English punctuation (string.punctuation and/or P*)
        ("!", "!"),
        ("?", "?"),
        ("(parens)", "(parens)"),
        ("a-b_c.d", "a-b_c.d"),
        ("@#$%", "@#$%"),
        ("quote\"tick'", "quote\"tick'"),
        ("[brackets]{braces}", "[brackets]{braces}"),
        ("path/to\\file", "path/to\\file"),
        ("a:b;c", "a:b;c"),
        # CJK and other letters matched by \\w
        ("café", "café"),
        ("日本語", "日本語"),
        ("Привет", "Привет"),
        ("mixedLatinAndEnglish", "mixedLatinAndEnglish"),
        # Unicode punctuation (category P*) not in ASCII punct set
        ("«»!? ", "«»!? "),
        ("«guillemets»", "«guillemets»"),
        ("—em dash—", "—em dash—"),
        ("…", "…"),
        ("• bullet", "• bullet"),
        ("\uff01", "\uff01"),  # fullwidth exclamation
        # symbols and controls removed
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
        ("\u00ad", ""),  # soft hyphen (Cf)
        # invisible / alternate spaces stripped
        ("a\u00a0b", "ab"),
        ("a\u200bb", "ab"),
        ("\u3000", ""),  # ideographic space (Zs)
        # combining marks without base word char
        ("e\u0301", "e"),
        ("é", "é"),  # precomposed Latin-1 letter
        # realistic mixed payloads
        ("Task-1: finish report (due Friday)!", "Task-1: finish report (due Friday)!"),
        ("Version 2.0—released; see README.", "Version 2.0—released; see README."),
        ("email@user.name\t+\temoji🔥end", "email@user.name\t+\temojiend"),
        # collapse runs of 4+ backticks to exactly 3
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

    _failures: list[str] = []
    for index, (raw_str, expected) in enumerate(_NORMALIZE_TEXT_CASES, start=1):
        actual = normalize_text(raw_str)
        if actual != expected:
            _failures.append(f"case {index}: raw={raw_str!r} expected={expected!r} got={actual!r}")

    if _failures:
        raise AssertionError(f"{len(_failures)} of {len(_NORMALIZE_TEXT_CASES)} cases failed:\n" + "\n".join(_failures))
    print(f"All {len(_NORMALIZE_TEXT_CASES)} normalize_text cases passed.")
