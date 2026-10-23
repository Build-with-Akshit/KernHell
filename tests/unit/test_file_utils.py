"""Unit tests for file utility functions."""

from __future__ import annotations

from pathlib import Path
import pytest

from kernhell.utils.file_utils import (
    backup_file,
    extract_surrounding_lines,
    read_file,
    restore_from_backup,
    write_file,
)


def test_atomic_write_and_read(tmp_path: Path) -> None:
    target = tmp_path / "sub" / "test.txt"
    content = "Hello KernHell Engine"

    write_file(target, content)
    assert target.is_file()
    assert read_file(target) == content


def test_backup_and_restore(tmp_path: Path) -> None:
    original = tmp_path / "script.py"
    original.write_text("print('version 1')", encoding="utf-8")

    backup = backup_file(original)
    assert backup.is_file()
    assert backup.read_text(encoding="utf-8") == "print('version 1')"

    # Mutate original
    original.write_text("print('version 2 - corrupted')", encoding="utf-8")

    # Restore
    restored = restore_from_backup(original)
    assert restored is True
    assert original.read_text(encoding="utf-8") == "print('version 1')"


def test_extract_surrounding_lines() -> None:
    code = "\n".join(f"line {i}" for i in range(1, 31))

    surrounding = extract_surrounding_lines(code, line_number=15, context=2)
    lines = surrounding.splitlines()

    # Context=2 means lines 13, 14, 15, 16, 17
    assert len(lines) == 5
    assert ">>>" in lines[2]  # Target line marked
    assert "15 >>> line 15" in lines[2]
    assert "13     line 13" in lines[0]
