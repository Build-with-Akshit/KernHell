"""Unit tests for the TestVerifier."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

from kernhell.core.config import KernHellConfig
from kernhell.core.exceptions import NoFailuresDetectedError
from kernhell.core.models import FailureContext, SelectorFix, SelectorStrategy
from kernhell.patcher.verifier import TestVerifier
from kernhell.utils.file_utils import backup_file, read_file, write_file


def test_verifier_pass(tmp_path: Path) -> None:
    cfg = KernHellConfig()
    verifier = TestVerifier(cfg)

    test_file = tmp_path / "test_sample.py"
    write_file(test_file, 'page.click("#healed-btn")')

    fix = SelectorFix(
        old_selector="#broken-btn",
        new_selector="#healed-btn",
        strategy=SelectorStrategy.CSS_FALLBACK,
        confidence=0.9,
    )

    # Scanner raising NoFailuresDetectedError means the test ran and PASSED!
    verifier.scanner.run = MagicMock(side_effect=NoFailuresDetectedError("Clean run"))

    passed = verifier.verify(test_file, fix)
    assert passed is True
    assert fix.verified is True


def test_verifier_fail_reverts_backup(tmp_path: Path) -> None:
    cfg = KernHellConfig()
    verifier = TestVerifier(cfg)

    test_file = tmp_path / "test_sample.py"
    # Create original
    write_file(test_file, 'page.click("#original-content")')
    # Create backup with original content
    backup_file(test_file)

    # Mutate test_file with broken patch
    write_file(test_file, 'page.click("#still-broken")')

    fix = SelectorFix(
        old_selector="#original-content",
        new_selector="#still-broken",
        confidence=0.5,
    )

    # Mock scanner returning ongoing failures
    mock_failure = FailureContext(
        test_file=test_file,
        line_number=1,
        broken_selector="#still-broken",
        error_message="Timeout exceeded",
    )
    verifier.scanner.run = MagicMock(return_value=[mock_failure])

    passed = verifier.verify(test_file, fix, revert_on_failure=True)
    assert passed is False
    assert fix.verified is False

    # Target file MUST have been restored from backup!
    restored_content = read_file(test_file)
    assert restored_content == 'page.click("#original-content")'
