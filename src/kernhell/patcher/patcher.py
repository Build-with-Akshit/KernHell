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


def _extract_testid_value(selector: str) -> Optional[str]:
    """Extract raw test id from [data-testid="..."], data-testid=..., or getByTestId('...')."""
    m = re.search(
        r"""(?:\[?data-testid[=:]\s*["']?|(?:get_by_test_id|getByTestId)\(\s*["']?)([^"'\]\)]+)""",
        selector,
    )
    if m:
        return m.group(1).strip().strip("'\"")
    return None


def _extract_role_parts(selector: str) -> tuple[Optional[str], Optional[str]]:
    """Extract role and name from role=button[name="..."] or getByRole('button', { name: '...' })."""
    m = re.search(
        r"""(?:role=|(?:get_by_role|getByRole)\(\s*["']?)(\w+)["']?(?:\s*,\s*(?:\{\s*name:\s*|name\s*=\s*)["']([^"']+)["']\s*\}?|\[name=["']([^"']+)["']\])?""",
        selector,
    )
    if m:
        return m.group(1), m.group(2) or m.group(3)
    return None, None


def _extract_text_value(selector: str) -> Optional[str]:
    """Extract text from text="..." or getByText('...')."""
    m = re.search(
        r"""(?:text=|(?:get_by_text|getByText)\(\s*)["']?([^"'\)]+)["']?\s*\)?""",
        selector,
    )
    if m:
        return m.group(1).strip().strip("'\"")
    return None


def _extract_placeholder_value(selector: str) -> Optional[str]:
    """Extract placeholder from [placeholder="..."] or getByPlaceholder('...')."""
    m = re.search(
        r"""(?:\[?placeholder[=:]\s*["']?|(?:get_by_placeholder|getByPlaceholder)\(\s*["']?)([^"'\]\)]+)""",
        selector,
    )
    if m:
        return m.group(1).strip().strip("'\"")
    return None


def _extract_label_value(selector: str) -> Optional[str]:
    """Extract label from label="..." or getByLabel('...')."""
    m = re.search(
        r"""(?:label=|(?:get_by_label|getByLabel)\(\s*["']?)([^"'\]\)]+)""",
        selector,
    )
    if m:
        return m.group(1).strip().strip("'\"")
    return None


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
            file_path=resolved,
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
        file_path: Optional[Path | str] = None,
    ) -> str:
        """Apply surgical replacement to source code string.

        For TypeScript/JavaScript files, directly uses high-precision surgical line transform.
        For Python files, tries LibCST first, falling back to surgical line transform.
        """
        is_ts = False
        if file_path is not None:
            suffix = Path(file_path).suffix.lower()
            if suffix in (".ts", ".js", ".tsx", ".jsx", ".mjs", ".cjs"):
                is_ts = True

        if is_ts:
            return self._surgical_line_transform(
                source_code=source_code,
                old_selector=old_selector,
                new_selector=new_selector,
                target_line=target_line,
            )

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
                    raw_new = new_selector.strip("'\"")
                    # Safe quoting: prevent clashing with inner quotes (e.g. [data-testid="..."])
                    if '"' in raw_new and "'" not in raw_new:
                        new_val = f"'{raw_new}'"
                    elif "'" in raw_new and '"' not in raw_new:
                        new_val = f'"{raw_new}"'
                    else:
                        quote = original_node.value[0]
                        if quote in raw_new:
                            alt_quote = "'" if quote == '"' else '"'
                            if alt_quote not in raw_new:
                                new_val = f"{alt_quote}{raw_new}{alt_quote}"
                            else:
                                escaped = raw_new.replace(quote, f"\\{quote}")
                                new_val = f"{quote}{escaped}{quote}"
                        else:
                            new_val = f"{quote}{raw_new}{quote}"
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
        Preserves indentation, comments, semicolons, and spacing.
        Supports both Python (snake_case) and TypeScript (camelCase).
        """
        raw_old = old_selector.strip("'\"")
        raw_new = new_selector.strip("'\"")

        def _replace_in_line(line: str, old_sel: str, new_sel: str) -> tuple[str, bool]:
            # 1. getByTestId / get_by_test_id
            m_testid = re.search(r"""((?:[\w.]+\.)?)(getByTestId|get_by_test_id)\(\s*(["'`])(.+?)\3\s*\)""", line)
            if m_testid:
                prefix = m_testid.group(1)
                fn_name = m_testid.group(2)
                quote = m_testid.group(3)
                cur_id = m_testid.group(4)
                old_testid = _extract_testid_value(old_sel) or old_sel.strip("'\"")
                if old_testid == cur_id or cur_id in old_sel or "testid" in old_sel.lower():
                    new_testid = _extract_testid_value(new_sel)
                    if new_testid:
                        replacement = f"{prefix}{fn_name}({quote}{new_testid}{quote})"
                        return line.replace(m_testid.group(0), replacement), True
                    else:
                        safe_new = new_sel.strip("'\"")
                        q = quote if quote in ("'", '"') and quote not in safe_new else ("'" if '"' in safe_new else '"')
                        replacement = f"{prefix}locator({q}{safe_new}{q})"
                        return line.replace(m_testid.group(0), replacement), True

            # 2. getByRole / get_by_role
            m_role = re.search(
                r"""((?:[\w.]+\.)?)(getByRole|get_by_role)\(\s*(["'`])(\w+)\3(?:\s*,\s*(?:\{\s*name:\s*|name\s*=\s*)(["'`])([^"'`]+)\5\s*\}?)?\s*\)""",
                line,
            )
            if m_role:
                cur_role = m_role.group(4)
                cur_name = m_role.group(6)
                old_role, old_name = _extract_role_parts(old_sel)
                role_matches = False
                if old_role and old_role.lower() == cur_role.lower():
                    if not old_name or not cur_name or old_name.lower() in cur_name.lower():
                        role_matches = True
                elif cur_name and cur_name in old_sel:
                    role_matches = True
                elif "role=" in old_sel.lower() or "getbyrole" in old_sel.lower() or "get_by_role" in old_sel.lower():
                    role_matches = True

                if role_matches:
                    prefix = m_role.group(1)
                    fn_name = m_role.group(2)
                    new_role, new_name = _extract_role_parts(new_sel)
                    if new_role:
                        if "getByRole" in fn_name:
                            replacement = (
                                f'{prefix}getByRole("{new_role}", {{ name: "{new_name}" }})'
                                if new_name
                                else f'{prefix}getByRole("{new_role}")'
                            )
                        else:
                            replacement = (
                                f'{prefix}get_by_role("{new_role}", name="{new_name}")'
                                if new_name
                                else f'{prefix}get_by_role("{new_role}")'
                            )
                        return line.replace(m_role.group(0), replacement), True
                    else:
                        safe_new = new_sel.strip("'\"")
                        q = "'" if '"' in safe_new else '"'
                        replacement = f"{prefix}locator({q}{safe_new}{q})"
                        return line.replace(m_role.group(0), replacement), True

            # 3. getByText / get_by_text
            m_text = re.search(r"""((?:[\w.]+\.)?)(getByText|get_by_text)\(\s*(["'`])(.+?)\3\s*\)""", line)
            if m_text:
                cur_text = m_text.group(4)
                old_text = _extract_text_value(old_sel) or old_sel.strip("'\"")
                if old_text == cur_text or cur_text in old_sel or "text=" in old_sel.lower() or "getbytext" in old_sel.lower() or "get_by_text" in old_sel.lower():
                    prefix = m_text.group(1)
                    fn_name = m_text.group(2)
                    quote = m_text.group(3)
                    new_text = _extract_text_value(new_sel)
                    if new_text:
                        replacement = f"{prefix}{fn_name}({quote}{new_text}{quote})"
                        return line.replace(m_text.group(0), replacement), True
                    else:
                        safe_new = new_sel.strip("'\"")
                        q = quote if quote in ("'", '"') and quote not in safe_new else ("'" if '"' in safe_new else '"')
                        replacement = f"{prefix}locator({q}{safe_new}{q})"
                        return line.replace(m_text.group(0), replacement), True

            # 4. getByPlaceholder / get_by_placeholder
            m_ph = re.search(r"""((?:[\w.]+\.)?)(getByPlaceholder|get_by_placeholder)\(\s*(["'`])(.+?)\3\s*\)""", line)
            if m_ph:
                cur_ph = m_ph.group(4)
                old_ph = _extract_placeholder_value(old_sel) or old_sel.strip("'\"")
                if old_ph == cur_ph or cur_ph in old_sel or "placeholder" in old_sel.lower():
                    prefix = m_ph.group(1)
                    fn_name = m_ph.group(2)
                    quote = m_ph.group(3)
                    new_ph = _extract_placeholder_value(new_sel)
                    if new_ph:
                        replacement = f"{prefix}{fn_name}({quote}{new_ph}{quote})"
                        return line.replace(m_ph.group(0), replacement), True
                    else:
                        safe_new = new_sel.strip("'\"")
                        q = quote if quote in ("'", '"') and quote not in safe_new else ("'" if '"' in safe_new else '"')
                        replacement = f"{prefix}locator({q}{safe_new}{q})"
                        return line.replace(m_ph.group(0), replacement), True

            # 5. getByLabel / get_by_label
            m_lbl = re.search(r"""((?:[\w.]+\.)?)(getByLabel|get_by_label)\(\s*(["'`])(.+?)\3\s*\)""", line)
            if m_lbl:
                cur_lbl = m_lbl.group(4)
                old_lbl = _extract_label_value(old_sel) or old_sel.strip("'\"")
                if old_lbl == cur_lbl or cur_lbl in old_sel or "label" in old_sel.lower():
                    prefix = m_lbl.group(1)
                    fn_name = m_lbl.group(2)
                    quote = m_lbl.group(3)
                    new_lbl = _extract_label_value(new_sel)
                    if new_lbl:
                        replacement = f"{prefix}{fn_name}({quote}{new_lbl}{quote})"
                        return line.replace(m_lbl.group(0), replacement), True
                    else:
                        safe_new = new_sel.strip("'\"")
                        q = quote if quote in ("'", '"') and quote not in safe_new else ("'" if '"' in safe_new else '"')
                        replacement = f"{prefix}locator({q}{safe_new}{q})"
                        return line.replace(m_lbl.group(0), replacement), True

            # 6. Standard quoted selector replacement
            # Double-quoted selector
            if f'"{old_sel}"' in line:
                if '"' in new_sel and "'" not in new_sel:
                    return line.replace(f'"{old_sel}"', f"'{new_sel}'"), True
                elif '"' in new_sel and "'" in new_sel:
                    escaped = new_sel.replace('"', '\\"')
                    return line.replace(f'"{old_sel}"', f'"{escaped}"'), True
                else:
                    return line.replace(f'"{old_sel}"', f'"{new_sel}"'), True

            # Single-quoted selector
            if f"'{old_sel}'" in line:
                if "'" in new_sel and '"' not in new_sel:
                    return line.replace(f"'{old_sel}'", f'"{new_sel}"'), True
                elif "'" in new_sel and '"' in new_sel:
                    escaped = new_sel.replace("'", "\\'")
                    return line.replace(f"'{old_sel}'", f"'{escaped}'"), True
                else:
                    return line.replace(f"'{old_sel}'", f"'{new_sel}'"), True

            # Backtick-quoted selector
            if f"`{old_sel}`" in line:
                return line.replace(f"`{old_sel}`", f"`{new_sel}`"), True

            # Raw unquoted replacement fallback
            if old_sel in line:
                return line.replace(old_sel, new_sel), True

            return line, False

        lines = source_code.splitlines(keepends=True)
        replaced = False

        if target_line is not None and 1 <= target_line <= len(lines):
            # Try target line first
            idx = target_line - 1
            new_line, did_replace = _replace_in_line(lines[idx], raw_old, raw_new)
            if did_replace:
                lines[idx] = new_line
                replaced = True
            else:
                # Search window of ±5 lines around target_line
                start = max(0, idx - 5)
                end = min(len(lines), idx + 6)
                for i in range(start, end):
                    new_line, did_replace = _replace_in_line(lines[i], raw_old, raw_new)
                    if did_replace:
                        lines[i] = new_line
                        replaced = True
                        break

        # Fallback: replace first occurrence across whole file
        if not replaced:
            for i, line in enumerate(lines):
                new_line, did_replace = _replace_in_line(line, raw_old, raw_new)
                if did_replace:
                    lines[i] = new_line
                    replaced = True
                    break

        if not replaced:
            raise SelectorNotFoundInASTError(
                f"Broken selector '{old_selector}' could not be located in test file."
            )

        return "".join(lines)
