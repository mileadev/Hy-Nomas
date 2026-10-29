#!/usr/bin/env python3
"""Fail CI when tracked text contains CJK-language characters."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys

TEXT_SUFFIXES = {
    ".py", ".js", ".mjs", ".ts", ".tsx", ".md", ".rst", ".txt",
    ".html", ".css", ".json", ".yaml", ".yml", ".toml", ".sh", ".svg",
}
EXCLUDED_NAMES = {"LICENSE"}  # Preserve third-party legal notices unchanged.


def find_cjk(root: Path) -> list[str]:
    paths = subprocess.check_output(["git", "ls-files", "-z"], cwd=root).split(b"\0")
    violations = []
    for raw in paths:
        if not raw:
            continue
        name = raw.decode("utf-8")
        file = root / name
        if file.name in EXCLUDED_NAMES or file.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            content = file.read_text(encoding="utf-8")
        except (UnicodeError, OSError):
            continue  # Binary assets are not text artifacts.
        for line_number, line in enumerate(content.splitlines(), 1):
            if any("\u3400" <= char <= "\u9fff" for char in line):
                violations.append(f"{name}:{line_number}: CJK-language characters found")
    return violations


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[2]
    problems = find_cjk(root)
    print("\n".join(problems) if problems else "English-language text check passed.")
    sys.exit(int(bool(problems)))
