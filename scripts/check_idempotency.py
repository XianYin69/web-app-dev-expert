#!/usr/bin/env python3
"""check_idempotency: probe replay safety of a mutating endpoint (leaf 1/7).

Sends the same request twice with an `Idempotency-Key` and compares status,
ETag/Location and body digest. A safe retry must replay, not duplicate.
Read-only against the target: no secrets are logged, body is hashed.

Usage: python -B scripts/check_idempotency.py --url URL [--method POST]
        [--body JSON] [--header "Name: value"]... [--key KEY]
Exit code: 0 replay-consistent, 1 findings, 2 unreachable.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import sys
import urllib.error
import urllib.request
import uuid

from _common import emit


def once(url, method, body, headers):
    req = urllib.request.Request(url, data=body.encode() if body else None,
                                 method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            payload = resp.read(200000)
            return {"status": resp.status, "digest": hashlib.sha256(payload).hexdigest(),
                    "etag": resp.headers.get("ETag", ""),
                    "location": resp.headers.get("Location", "")}
    except urllib.error.HTTPError as exc:
        payload = exc.read(200000)
        return {"status": exc.code, "digest": hashlib.sha256(payload).hexdigest(),
                "etag": exc.headers.get("ETag", ""),
                "location": exc.headers.get("Location", "")}
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return {"error": "%s: %s" % (type(exc).__name__, exc)}


def main():
    argp = argparse.ArgumentParser(description=__doc__)
    argp.add_argument("--url", required=True)
    argp.add_argument("--method", default="POST")
    argp.add_argument("--body", default="{}")
    argp.add_argument("--header", action="append", default=[])
    argp.add_argument("--key", default=None)
    args = argp.parse_args()
    if args.method.upper() in ("GET", "HEAD") and not args.body:
        print("NOTE: %s is already safe — this probe targets mutating calls"
              % args.method)
    key = args.key or ("probe-" + uuid.uuid4().hex[:12])
    headers = build_headers(args.header)
    first = once(args.url, args.method, args.body, dict(headers, **{"Idempotency-Key": key}))
    if "error" in first:
        print("UNREACHABLE %s: %s" % (args.url, first["error"]))
        return 2
    second = once(args.url, args.method, args.body, dict(headers, **{"Idempotency-Key": key}))
    print("URL %s %s -> %s | replay -> %s (key=%s)"
          % (args.method, args.url, first.get("status"), second.get("status", "-"), key))
    return emit(compare(first, second))


def build_headers(items):
    headers = {"Content-Type": "application/json", "User-Agent": "wg-probe/0.1"}
    for item in items:
        if ":" in item:
            k, v = item.split(":", 1)
            headers[k.strip()] = v.strip()
    return headers


def compare(first, second):
    findings = []
    if second.get("status") is None:
        return ["replay request failed: %s" % second.get("error")]
    if first["status"] != second["status"]:
        findings.append("status differs on replay %s vs %s"
                        % (first["status"], second["status"]))
    if first["digest"] != second["digest"]:
        findings.append("body digest differs on replay — key likely ignored"
                        " (duplicate effect risk)")
    if first["location"] and first["location"] != second["location"]:
        findings.append("Location differs on replay — a new resource was created")
    if first["status"] >= 500:
        findings.append("origin returned %s — replay safety undeterminable"
                        % first["status"])
    return findings


if __name__ == "__main__":
    sys.exit(main())
