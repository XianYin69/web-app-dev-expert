"""Inspect Set-Cookie attributes on a response (leaf 3).

Usage: python -B scripts/check_cookie_attrs.py --url URL
Exit code: 0 clean, 1 findings, 2 unreachable.
"""
import argparse
import sys
import urllib.error
import urllib.request

SESSION_HINTS = ("session", "sid", "auth", "csrf", "token")


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "wg-probe/0.1"})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return resp.status, resp.headers.get_all("Set-Cookie") or []
    except urllib.error.HTTPError as exc:
        return exc.code, exc.headers.get_all("Set-Cookie") or []
    except (urllib.error.URLError, OSError) as exc:
        return None, [str(exc)]


def parse(raw):
    parts = [p.strip() for p in raw.split(";")]
    name, _, value = parts[0].partition("=")
    attrs = {}
    for item in parts[1:]:
        key, _, val = item.partition("=")
        attrs[key.strip().lower()] = val.strip()
    return name.strip(), value, attrs


def audit(raw_cookies, secure_transport):
    findings = []
    for raw in raw_cookies:
        name, value, attrs = parse(raw)
        low = {k.lower() for k in attrs}
        sensitive = any(h in name.lower() for h in SESSION_HINTS)
        if not value:
            findings.append("%s: empty value (deletion cookie, ignore if logout)" % name)
        if sensitive and "httponly" not in low:
            findings.append("%s: session-ish cookie without HttpOnly" % name)
        if sensitive and "secure" not in low and secure_transport:
            findings.append("%s: missing Secure attribute" % name)
        if "samesite" not in low:
            findings.append("%s: no SameSite (browser default applies)" % name)
        elif attrs["samesite"].lower() == "none" and "secure" not in low:
            findings.append("%s: SameSite=None without Secure is rejected by browsers" % name)
        if "domain" in low and attrs["domain"].startswith("."):
            findings.append("%s: leading-dot Domain widens scope to all subdomains" % name)
        if len(value) > 256:
            findings.append("%s: value longer than 256 chars (header-size risk)" % name)
    return findings


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True)
    args = parser.parse_args()
    status, cookies = get(args.url)
    if status is None:
        print("UNREACHABLE %s: %s" % (args.url, cookies[0] if cookies else "?"))
        return 2
    if not cookies:
        print("URL %s -> %s | no Set-Cookie headers" % (args.url, status))
        return 0
    findings = audit(cookies, args.url.lower().startswith("https://"))
    print("URL %s -> %s | %d cookie(s)" % (args.url, status, len(cookies)))
    for f in findings:
        print("FINDING: " + f)
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
