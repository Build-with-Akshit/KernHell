"""KernHell configuration management.

Loads settings from (in priority order):
  1. Environment variables  (KERNHELL_LLM__PROVIDER, etc.)
  2. .kernhellrc.toml in the current directory
  3. ~/.kernhellrc.toml in the user's home directory
  4. Built-in defaults
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib  # type: ignore[import-untyped]


# ---------------------------------------------------------------------------
# Config Sub-Sections
# ---------------------------------------------------------------------------


class LLMConfig(BaseModel):
    """LLM provider settings."""

    provider: str = "gemini"
    model: str = "gemini-1.5-flash"
    api_key: Optional[str] = None
    api_base: Optional[str] = None
    temperature: float = 0.1
    max_tokens: int = 2048

    def get_resolved_api_key(self) -> Optional[str]:
        """Resolve API key from explicit config or standard provider environment variables."""
        if self.api_key:
            return self.api_key

        import os

        prov = self.provider.lower()
        if prov == "gemini":
            return os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        elif prov == "groq":
            return os.environ.get("GROQ_API_KEY")
        elif prov == "openai":
            return os.environ.get("OPENAI_API_KEY")
        elif prov == "anthropic":
            return os.environ.get("ANTHROPIC_API_KEY")
        elif prov == "mistral":
            return os.environ.get("MISTRAL_API_KEY")
        elif prov in ("ollama", "local"):
            return "local-no-key-required"
        return None

    def get_litellm_model_name(self) -> str:
        """Format the model name appropriately for litellm."""
        prov = self.provider.lower()
        model = self.model.strip()
        if prov == "openai":
            return model
        elif prov == "gemini":
            return model if model.startswith("gemini/") else f"gemini/{model}"
        return model if model.startswith(f"{prov}/") else f"{prov}/{model}"


class HealingConfig(BaseModel):
    """Healing behavior settings."""

    confidence_threshold: float = 0.85
    max_heals_per_file: int = 5
    dry_run: bool = False
    auto_commit: bool = False


class CacheConfig(BaseModel):
    """Semantic vector cache settings."""

    enabled: bool = True
    similarity_threshold: float = 0.92
    cache_dir: str = "~/.kernhell/cache"
    embedding_model: str = "all-MiniLM-L6-v2"


class ScannerConfig(BaseModel):
    """Playwright scanner settings."""

    timeout_ms: int = 30000
    capture_screenshot: bool = True
    browser: str = "chromium"
    headless: bool = True


class LoggingConfig(BaseModel):
    """Logging settings."""

    level: str = "INFO"
    json_output: bool = False


# ---------------------------------------------------------------------------
# Root Config
# ---------------------------------------------------------------------------


class KernHellConfig(BaseSettings):
    """Root configuration for KernHell.

    Merges TOML file settings with environment variable overrides.
    Env vars use the prefix ``KERNHELL_`` with double-underscore nesting
    (e.g. ``KERNHELL_LLM__PROVIDER=openai``).
    """

    model_config = SettingsConfigDict(
        env_prefix="KERNHELL_",
        env_nested_delimiter="__",
        case_sensitive=False,
    )

    llm: LLMConfig = Field(default_factory=LLMConfig)
    healing: HealingConfig = Field(default_factory=HealingConfig)
    cache: CacheConfig = Field(default_factory=CacheConfig)
    scanner: ScannerConfig = Field(default_factory=ScannerConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)


# ---------------------------------------------------------------------------
# Config Loading
# ---------------------------------------------------------------------------

_CONFIG_FILENAMES = [".kernhellrc.toml", "kernhell.toml"]


def _find_config_file() -> Optional[Path]:
    """Search current dir, ~/.kernhell, then home dir for a config file."""
    search_dirs = [
        Path.cwd(),
        Path.home() / ".kernhell",
        Path.home(),
    ]
    for directory in search_dirs:
        for name in _CONFIG_FILENAMES:
            candidate = directory / name
            if candidate.is_file():
                return candidate
    return None


def _extract_env_overrides() -> dict:
    """Extract and nest environment variables starting with KERNHELL_."""
    import os

    overrides: dict = {}
    prefix = "KERNHELL_"
    for key, value in os.environ.items():
        if key.upper().startswith(prefix):
            remainder = key[len(prefix):].lower()
            parts = remainder.split("__")
            d = overrides
            for p in parts[:-1]:
                d = d.setdefault(p, {})
            d[parts[-1]] = value
    return overrides


def _deep_merge(base: dict, overlay: dict) -> dict:
    """Recursively merge overlay dict on top of base dict."""
    merged = dict(base)
    for k, v in overlay.items():
        if k in merged and isinstance(merged[k], dict) and isinstance(v, dict):
            merged[k] = _deep_merge(merged[k], v)
        else:
            merged[k] = v
    return merged


def _load_env_file() -> None:
    """Load key-value pairs from .env file into os.environ if present."""
    import os

    for env_file in [Path.cwd() / ".env", Path.home() / ".kernhell" / ".env"]:
        if env_file.is_file():
            try:
                for line in env_file.read_text(encoding="utf-8").splitlines():
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        k = k.strip()
                        v = v.strip().strip("'\"")
                        if k and k not in os.environ:
                            os.environ[k] = v
            except Exception:
                pass


def load_config(config_path: Optional[Path] = None) -> KernHellConfig:
    """Load and return the merged KernHell configuration.

    Parameters
    ----------
    config_path:
        Explicit path to a TOML config file.  When *None*, the function
        searches the current directory and then ``$HOME`` for
        ``.kernhellrc.toml``.

    Returns
    -------
    KernHellConfig
        Fully resolved configuration with TOML → env-var priority.
    """
    _load_env_file()
    file_settings: dict = {}

    path = config_path or _find_config_file()
    if path and path.is_file():
        with open(path, "rb") as f:
            file_settings = tomllib.load(f)

    # Environment variables have highest priority over file settings
    env_overrides = _extract_env_overrides()
    merged_settings = _deep_merge(file_settings, env_overrides)

    return KernHellConfig(**merged_settings)
