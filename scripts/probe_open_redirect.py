#!/usr/bin/env python3
"""probe_open_redirect: redirect targets vs an allow-list (leaf 3).

Requests the URL carrying an absolute off-site target in --param (and a scheme
variant), then inspects the returned Location header. Any redirect leaving the
allow-list is a finding. Only self-hosted endpoints are probed — never a real
user-facing campaign link.

Usage: python -B scripts/probe_open_redirect.py --url URL [--param next]
        [--allow "example.com,cdn.example.com"] [--redirects 0]
Exit code: 0 clean, 1 findings, 2 unreachable.
"""
from __future__ import annotations
import argparse
import sys
import urllib.error
import urllib.parse
import urllib.request
import re

from _common import emit


def target_host(base, location):
    """Resolve a Location header to a host, treating /\\host and //host as
    protocol-relative (browsers do) instead of same-site paths."""
    raw = location.strip()
    if raw.startswith("/") and len(raw) > 1 and raw[1] in "/\\":
        raw = "https://" + raw.lstrip("/\\")
    elif raw.startswith("/"):
        return urllib.parse.urlsplit(base).netloc.split(":")[0].lower()
    if not re.match(r"^[A-Za-z][A-Za-z0-9+.\-]*:", raw):
        raw = urllib.parse.urljoin(base, raw)
    split = urllib.parse.urlsplit(raw)
    if split.netloc and not split.scheme:
        raw = "https:" + raw.lstrip("/")
    elif split.scheme and not split.netloc:
        # `https:/host` and `javascript:` style values: browsers fold a
        # single-slash absolute URI onto the host, so treat that as cross-site.
        rest = split.path.lstrip("/")
        raw = "https://" + rest if rest else raw
    return urllib.parse.urlsplit(raw).netloc.split(":")[0].lower()


PAYLOADS = ["https://evil.invalid/__T__", "//evil.invalid/__T__", "/\\evil.invalid/__T__",
            "https:/evil.invalid/__T__", "/__P__evil.invalid"]


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def probe(url, target, handler):
    opener = urllib.request.build_opener(handler)
    req = urllib.request.Request(url, headers={"User-Agent": "wg-probe/0.1"})
    try:
        with opener.open(req, timeout=15) as resp:
            return resp.status, resp.headers.get("Location", "")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.headers.get("Location", "")
    except urllib.error.URLError as exc:
        return None, str(exc.reason)


def main():
    argp = argparse.ArgumentParser(description=__doc__)
    argp.add_argument("--url", required=True)
    argp.add_argument("--param", default="next")
    argp.add_argument("--allow", default="")
    argp.add_argument("--redirects", type=int, default=0, help="max hops to follow (0 = none)")
    args = argp.parse_args()
    parts = urllib.parse.urlsplit(args.url)
    host = parts.netloc.split(":")[0].lower()
    allow = {a.strip().lower() for a in args.allow.split(",") if a.strip()}
    if host:
        allow.add(host)
    base = dict(x for x in urllib.parse.parse_qsl(parts.query) if x[0] != args.param)
    findings = []
    handler = NoRedirect() if args.redirects == 0 else urllib.request.HTTPRedirectHandler()
    for payload in PAYLOADS:
        target = payload.replace("__T__", urllib.parse.quote(args.param))
        target = target.replace("__P__", "%2f%2f")
        probe_url = urllib.parse.urlunsplit(
            parts._replace(query=urllib.parse.urlencode(dict(base, **{args.param: target}))))
        status, location = probe(probe_url, target, handler)
        if status is None:
            print("UNREACHABLE %s: %s" % (probe_url, location))
            return 2
        if status not in (301, 302, 303, 307, 308) or not location:
            print("OK   %s -> %s (no redirect honoured)" % (target, status))
            continue
        dest_host = target_host(probe_url, location)
        if dest_host and dest_host not in allow:
            findings.append("open redirect: %s -> Location=%s host=%s not in allow-list"
                                % (target, location, dest_host))
        else:
            print("OK   %s -> in-allow-list (%s)" % (target, dest_host or "relative"))
    print("redirects probed: %d | allow-list: %s" % (len(PAYLOADS), sorted(allow)))
    return emit(findings)


if __name__ == "__main__":
    sys.exit(main())
