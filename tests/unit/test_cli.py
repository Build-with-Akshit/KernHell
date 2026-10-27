"""Unit tests for the KernHell Typer CLI."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from kernhell import __version__
from kernhell.cli.app import app
from kernhell.core.models import FailureContext, HealingReport, HealingResult, SelectorType

runner = CliRunner()


def test_cli_version() -> None:
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.output


def test_cli_help() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "KernHell" in result.output
    assert "scan" in result.output
    assert "heal" in result.output


def test_cli_scan_non_existent_file() -> None:
    result = runner.invoke(app, ["scan", "non_existent_file_123.py"])
    assert result.exit_code == 1
    assert "not found" in result.output.lower()


def test_cli_heal_non_existent_file() -> None:
    result = runner.invoke(app, ["heal", "non_existent_file_123.py"])
    assert result.exit_code == 1
    assert "not found" in result.output.lower()


def test_cli_scan_with_mocked_orchestrator(sample_test_path: Path) -> None:
    mock_failure = FailureContext(
        test_file=sample_test_path,
        line_number=15,
        broken_selector="#buy-now",
        selector_type=SelectorType.CSS,
        error_message="Timeout exceeded",
    )

    with patch("kernhell.cli.commands.scan.HealingOrchestrator") as mock_orch_cls:
        mock_instance = MagicMock()
        mock_instance.scan.return_value = [(mock_failure, None)]
        mock_orch_cls.return_value = mock_instance

        result = runner.invoke(app, ["scan", str(sample_test_path)])
        assert result.exit_code == 0
        assert "#buy-now" in result.output


def test_cli_heal_with_mocked_orchestrator(sample_test_path: Path) -> None:
    mock_failure = FailureContext(
        test_file=sample_test_path,
        line_number=15,
        broken_selector="#buy-now",
        selector_type=SelectorType.CSS,
        error_message="Timeout exceeded",
    )
    report = HealingReport(test_file=sample_test_path)
    report.results = [HealingResult(failure=mock_failure, skipped=True)]

    with patch("kernhell.cli.commands.heal.HealingOrchestrator") as mock_orch_cls:
        mock_instance = MagicMock()
        mock_instance.heal.return_value = report
        mock_orch_cls.return_value = mock_instance

        result = runner.invoke(app, ["heal", str(sample_test_path)])
        assert result.exit_code == 0
        assert "#buy-now" in result.output
        assert "Healing Report" in result.output


def test_cli_cache_list_does_not_import_litellm() -> None:
    """Ensure lightweight local cache commands do not eagerly import heavy LLM packages."""
    import subprocess
    import sys

    code = (
        "import sys\n"
        "from typer.testing import CliRunner\n"
        "from kernhell.cli.app import app\n"
        "runner = CliRunner()\n"
        "res = runner.invoke(app, ['cache', 'list'])\n"
        "assert 'litellm' not in sys.modules, 'litellm was eagerly imported by cache list'\n"
    )
    proc = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    assert proc.returncode == 0, f"Subprocess validation failed:\n{proc.stderr}\n{proc.stdout}"


def test_cli_dashboard_dual_orchestration() -> None:
    """Ensure dashboard command orchestrates both FastAPI and Next.js UI subprocesses."""
    with patch("uvicorn.run") as mock_uvicorn_run, \
         patch("subprocess.Popen") as mock_popen, \
         patch("kernhell.cli.commands.dashboard._terminate_process_tree") as mock_cleanup:

        mock_proc = MagicMock()
        mock_popen.return_value = mock_proc

        result = runner.invoke(app, ["dashboard", "--no-open"])
        assert result.exit_code == 0
        assert "Mission Control Active" in result.output
        assert "Web Dashboard UI" in result.output
        mock_uvicorn_run.assert_called_once()
        mock_cleanup.assert_called_once()


