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
