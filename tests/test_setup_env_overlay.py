"""Tests for participant ``.env`` overlay onto the JiuwenSwarm instance."""

from pathlib import Path

from career_sim_runner.setup import _apply_env_values


def test_apply_env_values_only_overlays_api_credentials(tmp_path: Path) -> None:
    instance_env = tmp_path / ".env"
    instance_env.write_text(
        "KEEP_ME=1\nAPI_BASE=old-base\nMODEL_NAME=old-model\n",
        encoding="utf-8",
    )
    _apply_env_values(
        instance_env,
        {
            "API_BASE": "https://openrouter.ai/api/v1",
            "API_KEY": "sk-test",
            "MODEL_NAME": "deepseek-v4-flash",
            "LLM_PROVIDER_ORDER": "gmicloud,siliconflow",
            "LLM_PROVIDER_ONLY": "gmicloud",
            "UNRELATED": "nope",
        },
    )
    text = instance_env.read_text(encoding="utf-8")
    assert "API_BASE=https://openrouter.ai/api/v1" in text
    assert "API_KEY=sk-test" in text
    assert "MODEL_NAME=deepseek-v4-flash" in text
    assert "KEEP_ME=1" in text
    assert "LLM_PROVIDER_ORDER" not in text
    assert "LLM_PROVIDER_ONLY" not in text
    assert "UNRELATED" not in text
