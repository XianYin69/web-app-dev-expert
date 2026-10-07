#!/usr/bin/env python3
"""check_api_contract: compare live endpoints with a declared contract (leaf 2).

Contract = a plain text/JSON list of endpoints, one per line: `METHOD /path`
(or JSON {"endpoints":[{"method":"GET","path":"/x"}]}). Each endpoint is
requested and matched against the expected status set. Spec-driven linters
(OpenAPI) are delegated to `interface-design-expert` — this probe only checks
that the surface exists and behaves as declared, with invented statuses never
assumed.

Usage: python -B scripts/check_api_contract.py --spec contract.txt --base URL
        [--expect "200,204,301"] [--header "Name: value"]...
Exit code: 0 all matched, 1 findings, 2 unreachable/base invalid.
"""
from __future__ import annotations
import argparse
import json
import re
import sys
import urllib.error
import urllib.request

from _common import emit

LINE = re.compile(r"^\s*(GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)\s+(\S+)", re.I)


def load(path):
    text = open(path, "r", encoding="utf-8").read()
    if path.endswith(".json"):
        doc = json.loads(text)
        items = doc.get("endpoints", doc if isinstance(doc, list) else [])
        return [(str(i.get("method", "GET")).upper(), str(i.get("path", "/"))) for i in items]
    return [(m.group(1).upper(), m.group(2)) for m in
            (LINE.search(l) for l in text.splitlines()) if m]


def probe(base, method, path, headers):
    url = base.rstrip("/") + (path if path.startswith("/") else "/" + path)
    req = urllib.request.Request(url, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return resp.status
    except urllib.error.HTTPError as exc:
        return exc.code
    except (urllib.error.URLError, OSError):
        return None


def main():
    argp = argparse.ArgumentParser(description=__doc__)
    argp.add_argument("--spec", required=True)
    argp.add_argument("--base", required=True)
    argp.add_argument("--expect", default="200,201,204,301,302,304,401,403")
    argp.add_argument("--header", action="append", default=[])
    args = argp.parse_args()
    endpoints = load(args.spec)
    if not endpoints:
        print("error: no `METHOD /path` entries parsed from %s" % args.spec)
        return 2
    accepted = {int(x) for x in args.expect.split(",") if x.strip().isdigit()}
    headers = {"User-Agent": "wg-probe/0.1"}
    for item in args.header:
        if ":" in item:
            k, v = item.split(":", 1)
            headers[k.strip()] = v.strip()
    findings, dead = [], 0
    for method, path in endpoints:
        status = probe(args.base, method, path, headers)
        if status is None:
            dead += 1
            findings.append("%s %s unreachable" % (method, path))
        elif status not in accepted:
            findings.append("%s %s -> %s not in expected set %s" % (
                method, path, status, sorted(accepted)))
        else:
            print("OK   %s %s -> %s" % (method, path, status))
    print("contract: %d endpoints | spec: %s" % (len(endpoints), args.spec))
    if dead == len(endpoints):
        print("UNREACHABLE base %s" % args.base)
        return 2
    return emit(findings)


if __name__ == "__main__":
    sys.exit(main())
