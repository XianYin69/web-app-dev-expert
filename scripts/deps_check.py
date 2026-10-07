#!/usr/bin/env python3
"""deps_check: validate dependence/deps.json against the source_url red line.

Rules (every entry): name / source_url / license / version / install / checked_at
must be non-empty; `source_url` must be an http(s) upstream URL (GitHub/GitLab/
official repo or release page) or a `local://<skill-id>` reference whose target
directory exists next to this skill. Also warns when a declared local skill is
absent, and when `checked_at` is older than --max-age days.

Usage: python -B scripts/deps_check.py [--file dependence/deps.json]
                                       [--max-age 180] [--format text|json]
Exit code: 0 clean, 1 violations, 2 file not found.
"""
from __future__ import annotations
import argparse
import datetime as dt
import json
import os
import sys

from _common import emit, skill_root

REQUIRED = ("name", "source_url", "license", "version", "install", "checked_at")
UPSTREAM = ("http://", "https://", "ftp://", "git@", "ssh://")


def skills_root(override=None):
    if override:
        return os.path.abspath(override)
    return os.path.normpath(os.path.join(skill_root(), os.pardir))


def entries(doc):
    if isinstance(doc, dict):
        return doc.get("dependencies", doc.get("deps", []))
    return doc if isinstance(doc, list) else []


def validate(entry, max_age, root):
    problems = []
    name = str(entry.get("name", "")).strip() or "<unnamed>"
    for field in REQUIRED:
        if not str(entry.get(field, "")).strip():
            problems.append("%s: missing-field:%s" % (name, field))
    url = str(entry.get("source_url", "")).strip()
    if url.startswith("local://"):
        target = os.path.join(root, url[len("local://"):])
        if not os.path.isdir(target):
            problems.append("%s: local-skill-absent:%s" % (name, url))
    elif not url.startswith(UPSTREAM):
        problems.append("%s: source_url-needs-upstream-link:%r" % (name, url))
    stamp = str(entry.get("checked_at", "")).strip()
    if stamp:
        try:
            day = dt.date.fromisoformat(stamp[:10])
        except ValueError:
            problems.append("%s: checked_at-not-ISO-date:%s" % (name, stamp))
        else:
            age = (dt.date.today() - day).days
            if age > max_age:
                problems.append("%s: checked_at-stale:%d days" % (name, age))
    return problems


def main():
    argp = argparse.ArgumentParser(description=__doc__)
    argp.add_argument("--file", default=os.path.join(skill_root(), "dependence",
                                                     "deps.json"))
    argp.add_argument("--max-age", type=int, default=180)
    argp.add_argument("--skills-root", dest="skills_root",
                        help="directory holding local skills")
    argp.add_argument("--dry-run", action="store_true", help="report only (default)")
    argp.add_argument("--format", choices=("text", "json"), default="text")
    args = argp.parse_args()
    if not os.path.exists(args.file):
        print("error: deps.json not found at %s" % args.file)
        return 2
    with open(args.file, "r", encoding="utf-8") as handle:
        doc = json.load(handle)
    items = entries(doc)
    root = skills_root(args.skills_root)
    bad = []
    if not items:
        bad.append("deps.json declares zero dependencies (check the schema)")
    for entry in items:
        bad += validate(entry, args.max_age, root)
    if args.format == "json":
        print(json.dumps({"file": args.file, "entries": len(items),
                          "violations": bad}, ensure_ascii=False))
        return 1 if bad else 0
    print("deps checked: %d | file: %s" % (len(items), args.file))
    return emit(bad)


if __name__ == "__main__":
    sys.exit(main())
