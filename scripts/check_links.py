#!/usr/bin/env python3
"""check_links: red-line self-check for this skill (stdlib only, read-only).

Checks, over every markdown file under the skill root:
1. every relative link target resolves to a real file/dir (dangling must be 0);
2. every inline `scripts/<name>.py` or `asset/<...>` prose reference exists;
3. every .md is <= --max-lines lines (default 50);
4. with --strict-url, angle-bracket URLs are syntactically valid (no network).

Usage: python -B scripts/check_links.py [--root DIR] [--max-lines 50]
                                        [--strict-url] [--format text|json]
Exit code: 0 clean, 1 violations found, 2 root not found.
"""
from __future__ import annotations
import argparse
import json
import os
import re
import sys

from _common import emit, read_text, skill_root, walk_text

LINK = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")
PROSE = re.compile(r"(?<![\w/])((?:scripts|asset|references|resistance|branch|dependence|planned_tasks)/[\w\-./]+\.(?:py|ps1|md|json))")
URL = re.compile(r"<(https?://[^\s<>]+)>")
BAD_URL = re.compile(r"https?://(?:\s|//)", re.I)
SKIP_PREFIX = ("http://", "https://", "mailto:", "#", "local://", "sms:")


def check(root, max_lines, strict_url):
    bad, total, md_count = [], 0, 0
    for path in walk_text(root, (".md",)):
        md_count += 1
        rel = os.path.relpath(path, root)
        text = read_text(path)
        count = len(text.splitlines())
        if count > max_lines:
            bad.append("%s: %d lines > %d (md length red line)" % (rel, count, max_lines))
        for _, target in LINK.findall(text):
            clean = target.split(" ", 1)[0].strip()
            if not clean or clean.startswith(SKIP_PREFIX):
                continue
            total += 1
            frag = clean.split("#", 1)[0]
            if not frag:
                continue
            resolved = os.path.normpath(os.path.join(os.path.dirname(path), frag))
            if not os.path.exists(resolved):
                bad.append("%s: dangling link -> %s" % (rel, target))
        for ref in PROSE.findall(text):
            total += 1
            if not os.path.exists(os.path.normpath(os.path.join(root, ref))):
                bad.append("%s: dangling prose ref -> %s" % (rel, ref))
        if strict_url:
            for url in URL.findall(text):
                if BAD_URL.search(url) or url.rstrip("/").endswith((".", "-")):
                    bad.append("%s: malformed url -> %s" % (rel, url))
    return md_count, total, bad


def main():
    argp = argparse.ArgumentParser(description=__doc__)
    argp.add_argument("--root", default=skill_root())
    argp.add_argument("--max-lines", type=int, default=50)
    argp.add_argument("--strict-url", action="store_true")
    argp.add_argument("--dry-run", action="store_true", help="report only (default)")
    argp.add_argument("--format", choices=("text", "json"), default="text")
    args = argp.parse_args()
    root = os.path.abspath(args.root)
    if not os.path.isdir(root):
        print("error: root not found: %s" % root)
        return 2
    md_count, total, bad = check(root, args.max_lines, args.strict_url)
    if args.format == "json":
        print(json.dumps({"root": root, "markdown": md_count, "links": total,
                         "dangling": len(bad), "findings": bad}, ensure_ascii=False))
        return 1 if bad else 0
    print("markdown files: %d | links checked: %d" % (md_count, total))
    return emit(bad, "check_links on %s" % root)


if __name__ == "__main__":
    sys.exit(main())
