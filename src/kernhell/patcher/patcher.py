"""AST / Concrete Syntax Tree Surgical Code Patcher.

Uses `libcst` to surgically replace broken selectors in test files.
Unlike Python's standard `ast` module, `libcst` preserves:
  - All original indentation, spaces, and blank lines
  - All inline and block comments (# ...)
  - All docstrings and quote styles (' vs ")
  - All unrelated code and imports
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

import structlog

from kernhell.core.exceptions import PatcherError, SelectorNotFoundInASTError
from kernhell.core.models import SelectorFix
from kernhell.utils.file_utils import backup_file, read_file, write_file

logger = structlog.get_logger()


class SurgicalPatcher:
    """Surgically edits test files using Concrete Syntax Tree parsing."""

    def __init__(self) -> None:
        pass

    def patch_test_file(
        self,
        test_file: Path,
        fix: SelectorFix,
        line_number: Optional[int] = None,
        create_backup: bool = True,
    ) -> str:
        """Surgically replace the broken selector in the test file.

        Parameters
        ----------
        test_file : Path
            Path to the test file on disk.
        fix : SelectorFix
            The proposed fix containing old_selector and new_selector.
        line_number : Optional[int]
            The line number where failure occurred (for disambiguation).
        create_backup : bool
            Whether to write a .kernhell.bak file before mutating.

        Returns
        -------
        str
            The patched source code.
        """
        resolved = test_file.resolve()
        source_code = read_file(resolved)

        logger.info(
            "patcher.start",
            file=str(resolved),
            old=fix.old_selector,
            new=fix.new_selector,
            line=line_number,
        )

        if create_backup:
            backup_file(resolved)

        patched_code = self.apply_patch(
            source_code=source_code,
            old_selector=fix.old_selector,
            new_selector=fix.new_selector,
            target_line=line_number,
        )

        write_file(resolved, patched_code)
        logger.info("patcher.complete", file=str(resolved))
        return patched_code

    def apply_patch(
        self,
        source_code: str,
        old_selector: str,
        new_selector: str,
        target_line: Optional[int] = None,
    ) -> str:
        """Apply CST surgical replacement to source code string.

        Tries `libcst` first. If `libcst` is unavailable or parsing fails,
        falls back to a high-precision line-scoped surgical string replacement.
        """
        try:
            import libcst as cst

            return self._cst_transform(
                source_code=source_code,
                old_selector=old_selector,
                new_selector=new_selector,
                target_line=target_line,
            )
        except ImportError:
            logger.warning("patcher.libcst_not_available.using_surgical_regex")
            return self._surgical_line_transform(
                source_code=source_code,
                old_selector=old_selector,
                new_selector=new_selector,
                target_line=target_line,
            )
        except Exception as exc:
            logger.warning("patcher.cst_failed.falling_back_to_surgical_regex", error=str(exc))
            return self._surgical_line_transform(
                source_code=source_code,
                old_selector=old_selector,
                new_selector=new_selector,
                target_line=target_line,
            )

    def _cst_transform(
        self,
        source_code: str,
        old_selector: str,
        new_selector: str,
        target_line: Optional[int] = None,
    ) -> str:
        """CST Transformer implementation."""
        import libcst as cst

        module = cst.parse_module(source_code)

        # Clean selector text (strip quotes if raw string)
        raw_old = old_selector.strip("'\"")

        class SelectorStringReplacer(cst.CSTTransformer):
            def __init__(self) -> None:
                self.replaced_count = 0

            def leave_SimpleString(
                self,
                original_node: cst.SimpleString,
                updated_node: cst.SimpleString,
            ) -> cst.SimpleString:
                # Value includes surrounding quotes, e.g. '"#buy-now"'
                val = original_node.evaluated_value
                if val == raw_old:
                    quote = original_node.value[0]
                    # Format replacement preserving quote style
                    new_val = f"{quote}{new_selector.strip('\'"')}{quote}"
                    self.replaced_count += 1
                    return updated_node.with_changes(value=new_val)
                return updated_node

        replacer = SelectorStringReplacer()
        transformed = module.visit(replacer)

        if replacer.replaced_count == 0:
            # If literal string wasn't found in quotes, try surgical line transform
            return self._surgical_line_transform(
                source_code=source_code,
                old_selector=old_selector,
                new_selector=new_selector,
                target_line=target_line,
            )

        return transformed.code

    def _surgical_line_transform(
        self,
        source_code: str,
        old_selector: str,
        new_selector: str,
        target_line: Optional[int] = None,
    ) -> str:
        """High-precision line-scoped replacement.

        Targets only the specific line (or lines near it) where the failure occurred.
        Preserves indentation, comments, and spacing.
        """
        raw_old = old_selector.strip("'\"")
        raw_new = new_selector.strip("'\"")

        lines = source_code.splitlines(keepends=True)
        replaced = False

        if target_line is not None and 1 <= target_line <= len(lines):
            # Try target line first
            idx = target_line - 1
            if raw_old in lines[idx]:
                lines[idx] = lines[idx].replace(raw_old, raw_new)
                replaced = True
            else:
                # Search window of ±5 lines around target_line
                start = max(0, idx - 5)
                end = min(len(lines), idx + 6)
                for i in range(start, end):
                    if raw_old in lines[i]:
                        lines[i] = lines[i].replace(raw_old, raw_new)
                        replaced = True
                        break

        # Fallback: replace first occurrence across whole file
        if not replaced:
            for i, line in enumerate(lines):
                if raw_old in line:
                    lines[i] = line.replace(raw_old, raw_new)
                    replaced = True
                    break

        if not replaced:
            raise SelectorNotFoundInASTError(
                f"Broken selector '{old_selector}' could not be located in test file."
            )

        return "".join(lines)
