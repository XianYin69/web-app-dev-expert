#!/usr/bin/env python3
"""scan_dependency_vulns: offline lockfile audit against OSV (leaf 6/8).

Parses package-lock.json / requirements.txt / poetry.lock / go.mod / Gemfile.lock
into (name, version, ecosystem) tuples, then queries the OSV vulnerability API
(https://api.osv.dev) for each. No secrets leave the machine beyond the package
name/version. With --offline the parse and hygiene report still runs (unaudited
list is emitted so nothing is silently passed).

Usage: python -B scripts/scan_dependency_vulns.py --lock <file> [--offline]
        [--top N] [--format text|json]
Exit code: 0 no advisories, 1 advisories/hygiene findings, 2 lockfile missing.
"""
from __future__ import annotations
import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request

from _common import emit

NAME_LINE = re.compile(r"^\s*([A-Za-z0-9_.\-]+)\s*==\s*([^\s;#]+)")
GEM_LINE = re.compile(r"^\s*([A-Za-z0-9_.\-]+)\s+\(([^)]+)\)")


def parse(lock):
    base = os.path.basename(lock).lower()
    text = open(lock, "r", encoding="utf-8", errors="replace").read()
    items = []
    if base.endswith((".json",)):
        try:
            doc = json.loads(text)
        except ValueError:
            return items, "parse-skipped: not valid JSON"
        for name, pkg in (doc.get("packages") or doc.get("dependencies") or {}).items():
            name = name.split("node_modules/")[-1]
            ver = pkg.get("version", "")
            if name and ver:
                items.append((name, ver, "npm"))
    elif base.startswith("requirements") or lock.endswith(".txt"):
        items += [(n, v, "PyPI") for n, v in NAME_LINE.findall(text)]
    elif base.startswith("poetry.lock") or base.endswith(".lock") and "[[package]]" in text:
        name = re.findall(r'name = "([^"]+)"', text)
        ver = re.findall(r'version = "([^"]+)"', text)
        items += [(n, v, "PyPI") for n, v in zip(name, ver)]
    elif base.startswith("gemfile"):
        items += [(n, v, "RubyGems") for n, v in GEM_LINE.findall(text)]
    elif base.endswith(".mod"):
        for m in re.finditer(r"^\s*([^\s]+)\s+(v[0-9][^\s]*)", text, re.M):
            items.append((m.group(1), m.group(2), "Go"))
    else:
        return items, "parse-skipped: unknown lockfile format"
    return items, ""


def osv(name, version, ecosystem):
    body = json.dumps({"query": {"package": {"name": name, "ecosystem": ecosystem},
                                 "version": version}}).encode()
    req = urllib.request.Request("https://api.osv.dev/v1/query", data=body,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            doc = json.loads(resp.read().decode("utf-8", "replace"))
    except (urllib.error.URLError, OSError, ValueError) as exc:
        return None, str(exc)
    return [v.get("id", "?") for v in doc.get("vulns", [])], ""


def main():
    argp = argparse.ArgumentParser(description=__doc__)
    argp.add_argument("--lock", required=True)
    argp.add_argument("--offline", action="store_true")
    argp.add_argument("--top", type=int, default=200, help="max packages queried")
    argp.add_argument("--format", choices=("text", "json"), default="text")
    args = argp.parse_args()
    if not os.path.isfile(args.lock):
        print("error: lockfile not found: %s" % args.lock)
        return 2
    items, skip = parse(args.lock)
    if skip:
        print("error: %s (%s)" % (skip, args.lock))
        return 2
    findings, advisories, errored = [], [], 0
    if len(items) > args.top:
        findings.append("%d packages exceeds --top %d — audit truncated" % (len(items), args.top))
    for name, version, eco in items[: args.top]:
        if args.offline:
            continue
        ids, err = osv(name, version, eco)
        if ids is None:
            errored += 1
            continue
        if ids:
            advisories.append({"name": name, "version": version, "osv": ids})
            findings.append("%s@%s (%s): %s" % (name, version, eco, ", ".join(ids)))
    if args.offline:
        findings.append("offline mode: %d packages parsed but NOT audited upstream" % len(items))
    if errored:
        findings.append("%d queries failed — treated as unaudited, not as pass" % errored)
    if args.format == "json":
        print(json.dumps({"lockfile": args.lock, "packages": len(items),
                          "advisories": advisories, "findings": findings}, ensure_ascii=False))
        return 1 if findings else 0
    print("packages parsed: %d | advisories: %d | lockfile: %s" % (len(items), len(advisories), args.lock))
    return emit(findings)


if __name__ == "__main__":
    sys.exit(main())
