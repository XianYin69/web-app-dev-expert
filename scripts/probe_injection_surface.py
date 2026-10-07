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
SIGS = [
    ("sql-error", re.compile(
        r"(?:you have an error in your sql syntax|sqlite3\.|psycopg2\."
        r"|ORA-\d{5})", re.I)),
    ("template-reflection", re.compile(r"\{\{7\*7\}\}")),
    ("xss-reflection", re.compile(r"<svg onload=x>", re.I)),
    ("stack-trace", re.compile(
        r"(?:Traceback \(most recent call last\)"
        r"|at [A-Za-z$.]+\([A-Za-z]+\.java:\d+\))")),
    ("path-disclosure", re.compile(r"/etc/passwd")),
]

SRC_SIGS = [("string-sql", re.compile(
    r'(execute|query)\s*\(\s*f["\']|["\']\s*\+\s*\w+\s*\+\s*["\']', re.I)),
             ("string-shell", re.compile(r"os\.system|subprocess\.\w+\(.*shell=True|eval\(", re.I)),
             ("unsafe-html", re.compile(r"dangerouslySetInnerHTML|innerHTML\s*=", re.I))]


def fetch(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": "wg-probe/0.1"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read(300000).decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read(300000).decode("utf-8", "replace")
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return None, "%s: %s" % (type(exc).__name__, exc)


def http_probe(url, param, findings):
    parts = urllib.parse.urlsplit(url)
    query = dict(urllib.parse.parse_qsl(parts.query))
    for canary in CANARIES:
        merged = dict(query, **{param: canary})
        probe_url = urllib.parse.urlunsplit(
            parts._replace(query=urllib.parse.urlencode(merged)))
        status, body = fetch(probe_url)
        if status is None:
            print("UNREACHABLE %s: %s" % (probe_url, body))
            return 2
        for label, pattern in SIGS:
            if pattern.search(body):
                findings.append("%s: %s matched (HTTP %s)" % (label, param, status))
    print("http: %d canary request(s) against %s" % (len(CANARIES), url))
    return 0


def src_probe(root, findings):
    exts = (".py", ".js", ".ts", ".tsx", ".jsx", ".php", ".rb", ".go", ".java")
    scanned = 0
    for path in walk_text(root, exts):
        scanned += 1
        rel = os.path.relpath(path, root)
        for start, line in enumerate(read_text(path).splitlines(), 1):
            stripped = line.lstrip()
            # declaration lines of this probe's own signature table are not hits
            if stripped.startswith("#") or "re.compile(" in line:
                continue
            for label, pattern in SRC_SIGS:
                if pattern.search(line):
                    findings.append("%s at %s:%d" % (label, rel, start))
    print("src: %d files scanned under %s" % (scanned, root))


def main():
    argp = argparse.ArgumentParser(description=__doc__)
    argp.add_argument("--url")
    argp.add_argument("--param", default="q")
    argp.add_argument("--src")
    argp.add_argument("--skip-http", action="store_true")
    args = argp.parse_args()
    findings = []
    rc = 0
    if args.url and not args.skip_http:
        rc = http_probe(args.url, args.param, findings)
    if args.src:
        src_probe(args.src, findings)
    if not findings and not args.url and not args.src:
        print("error: nothing to do — pass --url and/or --src")
        return 2
    if rc == 2:
        return 2
    return emit(findings)


if __name__ == "__main__":
    sys.exit(main())
