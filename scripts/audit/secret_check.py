#!/usr/bin/env python3
"""Search tracked text for credential shapes; never emit secret values."""

from __future__ import annotations

from pathlib import Path
import re
import subprocess
import sys

PATTERNS = {
    "AWS access key ID": re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"),
    "GitHub token": re.compile(r"\b(?:ghp|gho|ghs|ghu|ghr)_[A-Za-z0-9]{30,}\b"),
    "GitHub fine-grained token": re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"),
    "OpenAI secret": re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{24,}\b"),
    "Private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "Hugging Face token": re.compile(r"\bhf_[A-Za-z0-9]{30,}\b"),
}

TEXT_EXT = {
    ".py", ".md", ".sh", ".toml", ".yml", ".yaml", ".json",
    ".js", ".mjs", ".ts", ".tsx", ".html", ".css", ".txt",
}


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    names = subprocess.check_output(["git", "ls-files", "-z"], cwd=root).split(b"\0")
    issues = []
    for raw in names:
        if not raw:
            continue
        name = raw.decode("utf-8")
        path = root / name
        if path.suffix not in TEXT_EXT:
            continue
        try:
            lines = path.read_text("utf-8").splitlines()
        except (UnicodeError, OSError):
            continue
        for lineno, value in enumerate(lines, 1):
            for label, pattern in PATTERNS.items():
                if pattern.search(value):
                    issues.append(f"{name}:{lineno}: {label} candidate")
    print("\n".join(issues) if issues else "No known credential patterns detected.")
    return int(bool(issues))


if __name__ == "__main__":
    sys.exit(main())
