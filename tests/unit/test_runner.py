"""Unit tests for the scanner test runner."""

from __future__ import annotations

from pathlib import Path
import pytest

from kernhell.core.config import KernHellConfig
from kernhell.core.exceptions import TestFileNotFoundError as FileNotFoundErr
from kernhell.scanner.runner import ScannerRunner, _extract_url_or_content_from_test


def test_extract_url_or_content_python(tmp_path: Path) -> None:
    py_file = tmp_path / "test_inline.py"
    py_file.write_text(
        'page.set_content("<button id=\\"btn\\">Submit</button>")\npage.click("#btn")\n',
        encoding="utf-8",
    )
    url, dom = _extract_url_or_content_from_test(py_file)
    assert url is None
    assert '<button id="btn">Submit</button>' in (dom or "")


def test_extract_url_or_content_typescript_set_content(tmp_path: Path) -> None:
    ts_file = tmp_path / "test_inline.spec.ts"
    ts_file.write_text(
        'await page.setContent("<button id=\\"ts-btn\\">Click</button>");\nawait page.click("#ts-btn");\n',
        encoding="utf-8",
    )
    url, dom = _extract_url_or_content_from_test(ts_file)
    assert url is None
    assert '<button id="ts-btn">Click</button>' in (dom or "")


def test_extract_url_or_content_typescript_template_literals(tmp_path: Path) -> None:
    ts_file = tmp_path / "test_template.spec.ts"
    ts_file.write_text(
        "await page.setContent(`\n  <div id=\"app\"><button id=\"buy\">Buy</button></div>\n`);\n",
        encoding="utf-8",
    )
    url, dom = _extract_url_or_content_from_test(ts_file)
    assert url is None
    assert '<button id="buy">Buy</button>' in (dom or "")


def test_extract_url_or_content_goto(tmp_path: Path) -> None:
    py_file = tmp_path / "test_nav.py"
    py_file.write_text('page.goto("https://store.example.com/checkout")\n', encoding="utf-8")
    url, dom = _extract_url_or_content_from_test(py_file)
    assert url == "https://store.example.com/checkout"
    assert dom is None

    ts_file = tmp_path / "test_nav.spec.ts"
    ts_file.write_text("await page.goto('https://ts-store.example.com/checkout');\n", encoding="utf-8")
    url, dom = _extract_url_or_content_from_test(ts_file)
    assert url == "https://ts-store.example.com/checkout"
    assert dom is None


def test_runner_file_not_found(tmp_path: Path) -> None:
    runner = ScannerRunner(KernHellConfig())
    missing = tmp_path / "does_not_exist.spec.ts"
    with pytest.raises(FileNotFoundErr):
        runner.run(missing)
