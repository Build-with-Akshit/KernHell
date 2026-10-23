"""Test Verifier — re-runs tests to confirm that patches actually heal the test.

If verification succeeds: marks fix as verified and cleans up backups.
If verification fails: reverts the test file from backup to prevent corruption.
"""

from __future__ import annotations

from pathlib import Path

import structlog

from kernhell.core.config import KernHellConfig
from kernhell.core.exceptions import NoFailuresDetectedError, VerificationFailedError
from kernhell.core.models import SelectorFix
from kernhell.scanner.runner import ScannerRunner
from kernhell.utils.file_utils import restore_from_backup

logger = structlog.get_logger()


class TestVerifier:
    """Verifies that an applied patch successfully allows the test to pass."""

    __test__ = False

    def __init__(self, config: KernHellConfig) -> None:
        self.config = config
        self.scanner = ScannerRunner(config)

    def verify(
        self,
        test_file: Path,
        fix: SelectorFix,
        revert_on_failure: bool = True,
    ) -> bool:
        """Re-run the test to verify whether the fix resolved the failure.

        Parameters
        ----------
        test_file : Path
            Path to the patched test file.
        fix : SelectorFix
            The fix that was applied.
        revert_on_failure : bool
            Whether to automatically restore the file from backup on failure.

        Returns
        -------
        bool
            True if verification passed (all tests clean).
        """
        logger.info(
            "verifier.start",
            file=str(test_file),
            new_selector=fix.new_selector,
        )

        try:
            # Re-running the test. If NoFailuresDetectedError is raised, it PASSED!
            self.scanner.run(test_file)

            # If scanner.run returned a list of failures without raising NoFailuresDetectedError,
            # then there are still failures remaining.
            logger.warning("verifier.still_failing", file=str(test_file))
            if revert_on_failure:
                restore_from_backup(test_file)
            fix.verified = False
            return False

        except NoFailuresDetectedError:
            # The test passed cleanly! Fix verified.
            logger.info("verifier.passed", file=str(test_file))
            fix.verified = True
            return True

        except Exception as exc:
            logger.warning("verifier.exception", file=str(test_file), error=str(exc))
            if revert_on_failure:
                restore_from_backup(test_file)
            fix.verified = False
            return False
