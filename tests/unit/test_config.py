"""Unit tests for configuration loading and environment overrides."""

from __future__ import annotations

import os
from pathlib import Path
import pytest

from kernhell.core.config import KernHellConfig, load_config


def test_default_config() -> None:
    cfg = KernHellConfig()
    assert cfg.llm.provider == "gemini"
    assert cfg.llm.model == "gemini-1.5-flash"
    assert cfg.healing.confidence_threshold == 0.85
    assert cfg.cache.enabled is True
    assert cfg.scanner.browser == "chromium"
    assert cfg.logging.level == "INFO"


def test_gemini_api_key_resolution(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GEMINI_API_KEY", "test-gemini-key-12345")
    cfg = KernHellConfig()
    assert cfg.llm.get_resolved_api_key() == "test-gemini-key-12345"
    assert cfg.llm.get_litellm_model_name() == "gemini/gemini-1.5-flash"


def test_gemini_custom_model_preserved() -> None:
    cfg = KernHellConfig(llm={"provider": "gemini", "model": "gemini-2.5-flash"})
    assert cfg.llm.get_litellm_model_name() == "gemini/gemini-2.5-flash"


def test_load_config_with_env_overrides(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KERNHELL_LLM__PROVIDER", "anthropic")
    monkeypatch.setenv("KERNHELL_LLM__MODEL", "claude-3-5-sonnet-20241022")
    monkeypatch.setenv("KERNHELL_HEALING__CONFIDENCE_THRESHOLD", "0.95")

    cfg = load_config()
    assert cfg.llm.provider == "anthropic"
    assert cfg.llm.model == "claude-3-5-sonnet-20241022"
    assert cfg.healing.confidence_threshold == 0.95


def test_load_config_from_explicit_file(tmp_path: Path) -> None:
    custom_toml = tmp_path / "custom.toml"
    custom_toml.write_text(
        """
        [llm]
        provider = "openai"
        model = "gpt-4o"

        [scanner]
        browser = "firefox"
        timeout_ms = 8000
        """,
        encoding="utf-8",
    )

    cfg = load_config(custom_toml)
    assert cfg.llm.provider == "openai"
    assert cfg.llm.model == "gpt-4o"
    assert cfg.scanner.browser == "firefox"
    assert cfg.scanner.timeout_ms == 8000
