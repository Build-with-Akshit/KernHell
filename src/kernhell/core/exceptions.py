"""KernHell custom exception hierarchy.

Every module raises typed exceptions so the Orchestrator can decide
whether to retry, skip, or abort cleanly.
"""

from __future__ import annotations


class KernHellError(Exception):
    """Base exception for all KernHell errors."""


# ---------------------------------------------------------------------------
# Scanner Errors
# ---------------------------------------------------------------------------


class ScannerError(KernHellError):
    """Raised when the Scanner fails to execute or parse a test run."""


class PlaywrightNotInstalledError(ScannerError):
    """Playwright or its browsers are not installed."""


class TestFileNotFoundError(ScannerError):
    """The specified test file does not exist."""


class NoFailuresDetectedError(ScannerError):
    """The test run completed without any selector failures — nothing to heal."""


# ---------------------------------------------------------------------------
# Pruner Errors
# ---------------------------------------------------------------------------


class PrunerError(KernHellError):
    """Raised when DOM pruning fails (e.g. malformed HTML)."""


# ---------------------------------------------------------------------------
# Analyzer / Healer Errors
# ---------------------------------------------------------------------------


class AnalyzerError(KernHellError):
    """Raised when the LLM analysis step fails."""


class HealerError(KernHellError):
    """Raised when the LLM cannot produce a valid selector fix."""


class LLMConnectionError(AnalyzerError):
    """Cannot reach the configured LLM provider."""


class LowConfidenceError(HealerError):
    """The proposed fix has a confidence score below the threshold."""

    def __init__(self, confidence: float, threshold: float) -> None:
        self.confidence = confidence
        self.threshold = threshold
        super().__init__(
            f"Confidence {confidence:.2f} is below threshold {threshold:.2f}"
        )


# ---------------------------------------------------------------------------
# Patcher Errors
# ---------------------------------------------------------------------------


class PatcherError(KernHellError):
    """Raised when AST patching fails."""


class SelectorNotFoundInASTError(PatcherError):
    """The broken selector string was not found in the test file's AST."""


class VerificationFailedError(PatcherError):
    """The patched test still fails after applying the fix."""


# ---------------------------------------------------------------------------
# Cache Errors
# ---------------------------------------------------------------------------


class CacheError(KernHellError):
    """Raised when the semantic cache encounters an error."""


# ---------------------------------------------------------------------------
# Config Errors
# ---------------------------------------------------------------------------


class ConfigError(KernHellError):
    """Raised when configuration is invalid or missing."""
