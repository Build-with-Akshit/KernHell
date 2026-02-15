"""
Smart Patcher - Surgical Code Fix Engine.
Comments out broken lines and inserts AI-fixed lines below.
Uses difflib for accurate line-level patching.
"""
import re
import shutil
import difflib
from pathlib import Path
from typing import Optional, List
from kernhell.utils import log_info, log_success, log_error, log_warning


def create_backup(file_path: Path):
    """Creates a .bak copy before any surgery."""
    backup_path = file_path.with_suffix(file_path.suffix + ".bak")
    shutil.copy2(file_path, backup_path)


def apply_fix(file_path: str, fixed_code: str, stderr: str = "") -> bool:
    """
    Smart patcher using difflib.
    """
    path = Path(file_path)
    if not path.exists():
        log_error(f"File not found: {file_path}")
        return False

    try:
        create_backup(path)

        with open(path, "r", encoding="utf-8") as f:
            original_lines = f.readlines()

        if hasattr(fixed_code, 'strip'):
            fixed_lines = fixed_code.strip().splitlines(keepends=True)
        else:
            fixed_lines = []

        # Ensure newline consistency
        original_lines = [l if l.endswith('\n') else l + '\n' for l in original_lines]
        fixed_lines = [l if l.endswith('\n') else l + '\n' for l in fixed_lines]

        # Use difflib to calculate changes
        diff = list(difflib.ndiff(original_lines, fixed_lines))
        
        patched_lines = []
        
        # We need to reconstruct the file from the diff
        # - lines: remove (comment out) using # [KERNHELL-FIX-OLD]
        # + lines: add
        #   lines: keep
        
        for line in diff:
            code = line[2:]
            marker = line[0]
            
            if marker == ' ':
                # Unchanged
                patched_lines.append(code)
            elif marker == '-':
                # Remove -> Comment out
                indent = len(code) - len(code.lstrip())
                indent_str = code[:indent]
                commented = f"{indent_str}# [KERNHELL-FIX-OLD] {code.strip()}\n"
                patched_lines.append(commented)
            elif marker == '+':
                # Add -> Insert new line
                patched_lines.append(code)
            elif marker == '?':
                # Hints (ignore)
                pass

        with open(path, "w", encoding="utf-8") as f:
            f.writelines(patched_lines)

        log_success(f"Surgical patch applied to {path.name}")
        return True

    except Exception as e:
        log_error(f"Patch failed: {e}")
        return False
