"""_common: shared helpers for web-app-dev-expert scripts (stdlib only)."""
from __future__ import annotations
import os
import sys

SKILL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def skill_root():
    return SKILL_ROOT


def walk_text(root, suffixes=(".md", ".py", ".json")):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames
                       if d not in (".git", "tmp", "__pycache__", ".pytest_cache")]
        for name in filenames:
            if name.endswith(suffixes):
                yield os.path.join(dirpath, name)


def read_text(path):
    with open(path, "r", encoding="utf-8", errors="replace") as handle:
        return handle.read()


def emit(findings, header=""):
    """Uniform probe output: header, FINDING lines, RESULT line, exit code."""
    if header:
        print(header)
    for item in findings:
        print("FINDING: " + item)
    print("RESULT %s (%d)" % ("FAIL" if findings else "PASS", len(findings)))
    return 1 if findings else 0
