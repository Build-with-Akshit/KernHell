"""Safe file I/O utilities for KernHell.

Every file write goes through these helpers so we can:
  - Create automatic backups before patching.
  - Handle encoding consistently (UTF-8 everywhere).
  - Provide atomic writes to prevent half-written files on crash.
"""

from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path

import structlog

logger = structlog.get_logger()


def read_file(path: Path) -> str:
    """Read a file as UTF-8 text.

    Raises
    ------
    FileNotFoundError
        If the file does not exist.
    """
    resolved = path.resolve()
    logger.debug("file.read", path=str(resolved))
    return resolved.read_text(encoding="utf-8")


def write_file(path: Path, content: str) -> None:
    """Write content to a file atomically.

    Writes to a temporary file in the same directory first, then
    atomically replaces the target.  This prevents data loss if the
    process crashes mid-write.
    """
    resolved = path.resolve()
    resolved.parent.mkdir(parents=True, exist_ok=True)

    # Write to a temp file in the same directory so os.replace is atomic.
    fd, tmp_path_str = tempfile.mkstemp(
        dir=str(resolved.parent),
        prefix=".kernhell_",
        suffix=".tmp",
    )
    # Important on Windows: close file descriptor immediately so file isn't locked
    os.close(fd)
    tmp_path = Path(tmp_path_str)
    try:
        tmp_path.write_text(content, encoding="utf-8")
        os.replace(str(tmp_path), str(resolved))
        logger.debug("file.write", path=str(resolved), size=len(content))
    except Exception:
        # Clean up the temp file on failure.
        tmp_path.unlink(missing_ok=True)
        raise


def backup_file(path: Path, suffix: str = ".kernhell.bak") -> Path:
    """Create a backup copy of a file before patching.

    Returns the path to the backup file.
    """
    resolved = path.resolve()
    backup_path = resolved.with_suffix(resolved.suffix + suffix)
    shutil.copy2(str(resolved), str(backup_path))
    logger.info("file.backup", original=str(resolved), backup=str(backup_path))
    return backup_path


def restore_from_backup(original: Path, suffix: str = ".kernhell.bak") -> bool:
    """Restore a file from its backup.  Returns True if successful."""
    resolved = original.resolve()
    backup_path = resolved.with_suffix(resolved.suffix + suffix)
    if backup_path.is_file():
        shutil.copy2(str(backup_path), str(resolved))
        logger.info("file.restore", path=str(resolved))
        return True
    logger.warning("file.restore.missing", backup=str(backup_path))
    return False


def extract_surrounding_lines(
    content: str,
    line_number: int,
    context: int = 10,
) -> str:
    """Extract ±context lines around a specific line number.

    Parameters
    ----------
    content:
        Full file content.
    line_number:
        1-indexed line number to centre on.
    context:
        Number of lines to include above and below.

    Returns
    -------
    str
        The extracted lines with line numbers prefixed.
    """
    lines = content.splitlines()
    start = max(0, line_number - 1 - context)
    end = min(len(lines), line_number + context)

    numbered: list[str] = []
    for i, line in enumerate(lines[start:end], start=start + 1):
        marker = " >>> " if i == line_number else "     "
        numbered.append(f"{i:4d}{marker}{line}")

    return "\n".join(numbered)
