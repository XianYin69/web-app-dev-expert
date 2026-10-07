"""Sample Core Web Vitals risk factors for a URL (leaf 9).

Static mode inspects the HTML for known LCP/CLS/INP risk patterns.
Field mode reads a JSON file of measured values (p75) and checks thresholds.
This probe never invents numbers: without --field it reports risk factors only.

Usage: python -B scripts/sample_web_vitals.py --url URL [--field metrics.json]
Exit code: 0 clean, 1 findings, 2 unreachable.
"""
import argparse
import json
import re
import sys
import urllib.error
import urllib.request

THRESHOLDS = {"lcp_ms": (2500, 4000), "inp_ms": (200, 500), "cls": (0.1, 0.25)}


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "wg-probe/0.1"})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return resp.status, resp.read(400000).decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read(400000).decode("utf-8", "replace")
    except (urllib.error.URLError, OSError) as exc:
        return None, str(exc)


def static_findings(html):
    findings = []
    blocking = re.findall(r'<link[^>]+rel="stylesheet"[^>]*>', html)
    if len(blocking) > 2:
        findings.append("%d render-blocking stylesheets" % len(blocking))
    sync_scripts = re.findall(r'<script[^>]+src=[^>]*>(?!</script>)', html)
    if sync_scripts:
        findings.append("%d script tag(s) without async/defer" % len(sync_scripts))
    imgs = re.findall(r"<img\b[^>]*>", html)
    unsized = [i for i in imgs if "width" not in i or "height" not in i]
    if unsized:
        findings.append("%d <img> without width/height or aspect-ratio (CLS risk)" % len(unsized))
    if re.search(r"(?s)<img[^>]+src=[^>]*>.*?<h1", html, re.I):
        findings.append("possible hero image discovered after content start")
    if "fetchpriority" not in html:
        findings.append("no fetchpriority hint on any resource (LCP discovery)")
    if "preload" not in html:
        findings.append("no <link rel=preload> for likely LCP candidate")
    if html.count("iframe") > 2:
        findings.append("multiple iframes above the fold (INP/LCP contention)")
    return findings


def field_findings(path):
    data = json.load(open(path, encoding="utf-8"))
    findings = []
    for key, (good, poor) in THRESHOLDS.items():
        value = data.get(key)
        if value is None:
            findings.append("%s missing from field data" % key)
        elif value > poor:
            findings.append("%s=%s exceeds poor threshold %s" % (key, value, poor))
        elif value > good:
            findings.append("%s=%s is needs-improvement (good <= %s)" % (key, value, good))
    return findings


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url")
    parser.add_argument("--field")
    args = parser.parse_args()
    findings = []
    if args.url:
        status, html = fetch(args.url)
        if status is None:
            print("UNREACHABLE %s: %s" % (args.url, html))
            return 2
        print("URL %s -> %s (static risk analysis)" % (args.url, status))
        findings += static_findings(html)
    if args.field:
        findings += field_findings(args.field)
    for f in findings:
        print("FINDING: " + f)
    print("RESULT %s (%d)" % ("FAIL" if findings else "PASS", len(findings)))
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
