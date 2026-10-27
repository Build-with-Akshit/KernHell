"""Unit tests for the KernHell setup wizard and provider selection."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from kernhell.cli.app import app
from kernhell.cli.commands.setup import check_first_run_setup, run_setup_wizard
from kernhell.core.config import KernHellConfig

runner = CliRunner()


def test_cli_setup_help() -> None:
    result = runner.invoke(app, ["setup", "--help"])
    assert result.exit_code == 0
    assert "setup wizard" in result.output.lower()


def test_cli_init_alias() -> None:
    result = runner.invoke(app, ["init", "--help"])
    assert result.exit_code == 0
    assert "setup" in result.output.lower() or "wizard" in result.output.lower()


def test_setup_wizard_ollama_provider(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    # Choice '5' selects Ollama (Local Offline), model name "llama3.2", base URL default
    inputs = "5\nllama3.2\nhttp://localhost:11434\n"
    with patch("rich.console.Console.print"):
        result = runner.invoke(app, ["setup"], input=inputs)
        assert result.exit_code == 0

    marker = tmp_path / ".kernhell" / ".setup_done"
    assert marker.exists()
    assert "ollama" in marker.read_text(encoding="utf-8")

    config_file = tmp_path / ".kernhell" / ".kernhellrc.toml"
    assert config_file.exists()
    content = config_file.read_text(encoding="utf-8")
    assert 'provider = "ollama"' in content
    assert 'model = "ollama/llama3.2"' in content


def test_setup_wizard_skip_api_key(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    # Choice '1' (Gemini), empty API Key (skipped), Use default model (Y)
    inputs = "1\n\nY\n"
    with patch("rich.console.Console.print"):
        result = runner.invoke(app, ["setup"], input=inputs)
        assert result.exit_code == 0

    config_file = tmp_path / ".kernhell" / ".kernhellrc.toml"
    assert config_file.exists()
    content = config_file.read_text(encoding="utf-8")
    assert 'provider = "gemini"' in content


def test_setup_wizard_gemini_provider(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    # Choice '1' (Gemini), API Key "AIzaSyTestKey123", Use default model (Y)
    inputs = "1\nAIzaSyTestKey123\nY\n"
    with patch("rich.console.Console.print"):
        result = runner.invoke(app, ["setup"], input=inputs)
        assert result.exit_code == 0

    env_file = tmp_path / ".kernhell" / ".env"
    assert env_file.exists()
    assert "GEMINI_API_KEY=AIzaSyTestKey123" in env_file.read_text(encoding="utf-8")

    config_file = tmp_path / ".kernhell" / ".kernhellrc.toml"
    assert config_file.exists()
    content = config_file.read_text(encoding="utf-8")
    assert 'provider = "gemini"' in content
    assert 'model = "gemini-3.5-flash"' in content


def test_check_first_run_setup_skips_when_configured(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    setup_marker = tmp_path / ".kernhell" / ".setup_done"
    setup_marker.parent.mkdir(parents=True, exist_ok=True)
    setup_marker.touch()

    cfg = KernHellConfig()
    from rich.console import Console
    result_cfg = check_first_run_setup(Console(), cfg)
    assert result_cfg == cfg


def test_cli_llm_show() -> None:
    result = runner.invoke(app, ["llm", "show"])
    assert result.exit_code == 0
    assert "Active AI / LLM Engine" in result.output
    assert "Provider" in result.output


def test_cli_llm_set_command(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    result = runner.invoke(app, ["llm", "set", "openai", "-k", "sk-testkey123", "-m", "gpt-4o"])
    assert result.exit_code == 0
    assert "Successfully switched LLM to OpenAI" in result.output

    config_file = tmp_path / ".kernhell" / ".kernhellrc.toml"
    assert config_file.exists()
    content = config_file.read_text(encoding="utf-8")
    assert 'provider = "openai"' in content
    assert 'model = "gpt-4o"' in content

    env_file = tmp_path / ".kernhell" / ".env"
    assert env_file.exists()
    assert "OPENAI_API_KEY=sk-testkey123" in env_file.read_text(encoding="utf-8")


def test_cli_llm_set_invalid_provider() -> None:
    result = runner.invoke(app, ["llm", "set", "invalid_provider_xyz"])
    assert result.exit_code == 1
    assert "Unknown provider" in result.output


def test_cli_switch_llm_alias() -> None:
    result = runner.invoke(app, ["switch-llm", "--help"])
    assert result.exit_code == 0
    assert "switch" in result.output.lower()


def test_setup_wizard_invalid_choice_retry(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    # First '9' (out of range), then 'invalid' (non-numeric), then '1' (Gemini), empty key, default model
    inputs = "9\ninvalid\n1\n\nY\n"
    result = runner.invoke(app, ["setup"], input=inputs)
    assert result.exit_code == 0
    assert "Invalid choice '9'" in result.output
    assert "Invalid choice 'invalid'" in result.output

    config_file = tmp_path / ".kernhell" / ".kernhellrc.toml"
    assert config_file.exists()
    assert 'provider = "gemini"' in config_file.read_text(encoding="utf-8")


def test_setup_wizard_provider_name_input(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    # Types "ollama" by text instead of "5", model name "llama3.2", base URL default
    inputs = "ollama\nllama3.2\nhttp://localhost:11434\n"
    result = runner.invoke(app, ["setup"], input=inputs)
    assert result.exit_code == 0

    config_file = tmp_path / ".kernhell" / ".kernhellrc.toml"
    assert config_file.exists()
    assert 'provider = "ollama"' in config_file.read_text(encoding="utf-8")


