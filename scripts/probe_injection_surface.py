#!/usr/bin/env python3
"""probe_injection_surface: black-box check for reflection of user input (leaf 4).

Fetches the URL with benign canary payloads appended to the query string, then
looks for raw reflection, unescaped quotes, and injection-relevant error
signatures in the response body. Static analysis of the source tree: pass
--src DIR to flag string-built SQL/shell/HTML patterns in code files.

Nothing destructive is sent: payloads are detection strings, never exploit code.

Usage: python -B scripts/probe_injection_surface.py --url URL [--param q]
        [--src DIR] [--skip-http]
Exit code: 0 clean, 1 findings, 2 unreachable.
"""
from __future__ import annotations
import argparse
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

from _common import emit, read_text, walk_text

CANARIES = ['"><svg onload=x>', "1' OR '1'='1", "{{7*7}}", "$(7777777)", "../../etc/passwd"]
SIGS = [("sql-error", re.compile(r"(you have an error in your sql syntax|sqlite3\.|psycopg2\.|ORA-\d{5})", re.I)),
        ("template-reflection", re.compile(r"\{\{7\*7\}\}")),
        ("xss-reflection", re.compile(r"<svg onload=x>", re.I)),
        ("stack-trace", re.compile(r"(Traceback \(most recent call last\)|at [A-Za-z$.]+\([A-Za-z]+\.java:\d+\))")),
        ("path-disclosure", re.compile(r"/etc/passwd"))]
SRC_SIGS = [("string-sql", re.compile(r'(execute|query)\s*\(\s*f["\']|["\']\s*\+\s*\w+\s*\+\s*["\']', re.I)),
             ("string-shell", re.compile(r"os\.system|subprocess\.\w+\(.*shell=True|eval\(", re.I)),
             ("unsafe-html", re.compile(r"dangerouslySetInnerHTML|innerHTML\s*=", re.I))]


def fetch(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": "wg-probe/0.1"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read(300000).decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read(300000).decode("utf-8", "replace")
    except (urllib.error.URLError, OSError) as exc:
        return None, str(exc)


def main():
    argp = argparse.ArgumentParser(description=__doc__)
    argp.add_argument("--url")
    argp.add_argument("--param", default="q")
    argp.add_argument("--src")
    argp.add_argument("--skip-http", action="store_true")
    args = argp.parse_args()
    findings = []
    if args.url and not args.skip_http:
        parts = urllib.parse.urlsplit(args.url)
        query = dict(urllib.parse.parse_qsl(parts.query))
        for canary in CANARIES:
            probe = urllib.parse.urlunsplit(parts._replace(
                query=urllib.parse.urlencode(dict(query, **{args.param: canary}))))
            status, body = fetch(probe)
            if status is None:
                print("UNREACHABLE %s: %s" % (probe, body))
                return 2
            for label, pattern in SIGS:
                if pattern.search(body):
                    findings.append("%s: %s matched (HTTP %s)" % (label, args.param, status))
        print("http: %d canary request(s) against %s" % (len(CANARIES), args.url))
    if args.src:
        hits, scanned = 0, 0
        for path in walk_text(args.src, (".py", ".js", ".ts", ".tsx", ".jsx", ".php", ".rb", ".go", ".java")):
            scanned += 1
            for start, line in enumerate(read_text(path).splitlines(), 1):
                if line.lstrip().startswith("#"):
                    continue
                for label, pattern in SRC_SIGS:
                    if pattern.search(line):
                        hits += 1
                        findings.append("%s at %s:%d" % (label, os.path.relpath(path, args.src), start))
        print("src: %d files scanned under %s" % (scanned, args.src))
    if not findings and not args.url and not args.src:
        print("error: nothing to do — pass --url and/or --src")
        return 2
    return emit(findings)


if __name__ == "__main__":
    sys.exit(main())
