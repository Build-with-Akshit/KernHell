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


def test_setup_wizard_offline_mode(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    # Choice '6' selects Free Offline Heuristic Mode
    inputs = "6\n"
    with patch("rich.console.Console.print"):
        result = runner.invoke(app, ["setup"], input=inputs)
        assert result.exit_code == 0

    marker = tmp_path / ".kernhell" / ".setup_done"
    assert marker.exists()
    assert "local" in marker.read_text(encoding="utf-8")

    config_file = tmp_path / ".kernhell" / ".kernhellrc.toml"
    assert config_file.exists()
    assert 'provider = "local"' in config_file.read_text(encoding="utf-8")


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
    assert 'model = "gemini-2.5-flash"' in content


def test_check_first_run_setup_skips_when_configured(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    setup_marker = tmp_path / ".kernhell" / ".setup_done"
    setup_marker.parent.mkdir(parents=True, exist_ok=True)
    setup_marker.touch()

    cfg = KernHellConfig()
    from rich.console import Console
    result_cfg = check_first_run_setup(Console(), cfg)
    assert result_cfg == cfg
