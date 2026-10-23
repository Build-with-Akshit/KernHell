"""Unit tests for the FailureAnalyzer."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

from kernhell.analyzer.analyzer import FailureAnalyzer, _clean_json_response
from kernhell.core.config import KernHellConfig
from kernhell.core.models import FailureContext, FailureType, PrunedDOM, SelectorType


def test_clean_json_response_with_markdown_fences() -> None:
    raw_markdown = """```json
    {
      "failure_type": "rename",
      "explanation": "Selector renamed",
      "confidence": 0.9
    }
    ```"""
    cleaned = _clean_json_response(raw_markdown)
    data = json.loads(cleaned)
    assert data["failure_type"] == "rename"
    assert data["confidence"] == 0.9


def test_clean_json_response_plain() -> None:
    raw_json = '{"failure_type": "missing", "explanation": "Not found", "confidence": 0.8}'
    cleaned = _clean_json_response(raw_json)
    assert cleaned == raw_json


def test_diagnose_rename_with_heuristic(sample_test_path: Path, sample_dom_renamed_html: str) -> None:
    cfg = KernHellConfig()
    analyzer = FailureAnalyzer(cfg)

    failure = FailureContext(
        test_file=sample_test_path,
        line_number=15,
        broken_selector="#buy-now",
        selector_type=SelectorType.CSS,
        error_message="Timeout 5000ms exceeded waiting for locator('#buy-now')",
        live_dom=sample_dom_renamed_html,
        surrounding_code='page.click("#buy-now")',
    )

    pruned = PrunedDOM(html=sample_dom_renamed_html, original_size=len(sample_dom_renamed_html), pruned_size=len(sample_dom_renamed_html))
    diagnosis = analyzer.diagnose(failure, pruned)

    assert diagnosis.failure_type == FailureType.RENAME
    assert diagnosis.confidence >= 0.8
    assert "refactor" in diagnosis.explanation.lower() or "rename" in diagnosis.explanation.lower() or "button" in diagnosis.explanation.lower()


def test_diagnose_missing_element_guardrail(sample_test_path: Path, sample_dom_missing_html: str) -> None:
    cfg = KernHellConfig()
    analyzer = FailureAnalyzer(cfg)

    failure = FailureContext(
        test_file=sample_test_path,
        line_number=15,
        broken_selector="#buy-now",
        selector_type=SelectorType.CSS,
        error_message="Timeout 5000ms exceeded waiting for locator('#buy-now')",
        live_dom=sample_dom_missing_html,
        surrounding_code='page.click("#buy-now")',
    )

    pruned = PrunedDOM(html=sample_dom_missing_html, original_size=len(sample_dom_missing_html), pruned_size=len(sample_dom_missing_html))
    diagnosis = analyzer.diagnose(failure, pruned)

    # Must classify as MISSING so it is not healed
    assert diagnosis.failure_type == FailureType.MISSING
    assert diagnosis.confidence >= 0.8


def test_diagnose_empty_dom(sample_test_path: Path) -> None:
    cfg = KernHellConfig()
    analyzer = FailureAnalyzer(cfg)

    failure = FailureContext(
        test_file=sample_test_path,
        line_number=15,
        broken_selector="#buy-now",
        error_message="Timeout",
        live_dom="",
    )

    diagnosis = analyzer.diagnose(failure, None)
    assert diagnosis.failure_type == FailureType.UNKNOWN
    assert diagnosis.confidence == 0.0
