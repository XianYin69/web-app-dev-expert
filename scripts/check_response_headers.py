"""Probe HTTP security response headers of a URL (leaf 4).

Usage: python -B scripts/check_response_headers.py --url https://host/path
Exit code: 0 no findings, 1 findings present, 2 target unreachable.
"""
import argparse
import sys
import urllib.error
import urllib.request

REQUIRED = {
    "x-content-type-options": "nosniff",
    "referrer-policy": None,
}
RISKY_VALUE = ("unsafe-inline", "unsafe-eval")
LEAKY = ("server", "x-powered-by", "x-aspnet-version", "x-runtime", "x-version")


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "wg-probe/0.1"})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return resp.status, dict(resp.headers)
    except urllib.error.HTTPError as exc:
        return exc.code, dict(exc.headers)
    except (urllib.error.URLError, OSError) as exc:
        return None, {"error": str(exc)}


def audit(status, headers, secure):
    low = {k.lower(): v for k, v in headers.items()}
    findings = []
    for name, expect in REQUIRED.items():
        if name not in low:
            findings.append("missing header: %s" % name)
        elif expect and expect not in low[name].lower():
            findings.append("%s should contain %r (got %r)" % (name, expect, low[name]))
    csp = low.get("content-security-policy")
    if not csp:
        findings.append("missing header: content-security-policy")
    else:
        for risky in RISKY_VALUE:
            if risky in csp.lower():
                findings.append("CSP allows %s" % risky)
    if status and status >= 400:
        findings.append("target returned status %s" % status)
    if secure and "strict-transport-security" not in low:
        findings.append("missing header: strict-transport-security")
    for name in LEAKY:
        if name in low:
            findings.append("information disclosure header: %s: %s" % (name, low[name]))
    if "set-cookie" in low:
        findings.append("Set-Cookie echoed; see check_cookie_attrs.py")
    return findings


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True)
    args = parser.parse_args()
    status, headers = fetch(args.url)
    if status is None:
        print("UNREACHABLE %s: %s" % (args.url, headers.get("error")))
        return 2
    secure = args.url.lower().startswith("https://")
    findings = audit(status, headers, secure)
    print("URL %s -> %s" % (args.url, status))
    for item in findings:
        print("FINDING %s" % item)
    print("RESULT %s (%d findings)" % ("FAIL" if findings else "PASS", len(findings)))
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
