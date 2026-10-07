"""Probe a CORS preflight response (leaf 4).

Usage: python -B scripts/probe_cors_preflight.py --url URL --origin ORIGIN
       [--method POST] [--headers "content-type,x-api-key"]
Exit code: 0 clean, 1 findings, 2 unreachable.
"""
import argparse
import sys
import urllib.error
import urllib.request


def options(url, origin, method, headers):
    req = urllib.request.Request(url, method="OPTIONS", headers={
        "Origin": origin,
        "Access-Control-Request-Method": method,
        "Access-Control-Request-Headers": headers,
        "User-Agent": "wg-probe/0.1",
    })
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return resp.status, dict(resp.headers)
    except urllib.error.HTTPError as exc:
        return exc.code, dict(exc.headers)
    except (urllib.error.URLError, OSError) as exc:
        return None, {"error": str(exc)}


def audit(status, hdr, origin):
    low = {k.lower(): v for k, v in hdr.items()}
    findings = []
    acao = low.get("access-control-allow-origin")
    if status is None:
        return ["no response"]
    if status >= 400:
        findings.append("preflight rejected with status %s" % status)
    if acao is None:
        findings.append("no Access-Control-Allow-Origin: browser will block it")
    elif acao == "*" and low.get("access-control-allow-credentials") == "true":
        findings.append("wildcard origin with credentials=true (invalid combo)")
    elif acao not in (origin, "*"):
        findings.append("ACAO %r does not match request origin %r" % (acao, origin))
    if acao and acao != "*" and "vary" not in low:
        findings.append("missing Vary: Origin on a per-origin ACAO (cache poisoning)")
    if "access-control-allow-methods" not in low:
        findings.append("no Access-Control-Allow-Methods header")
    if "access-control-max-age" not in low:
        findings.append("no Access-Control-Max-Age: every call re-preflights")
    return findings


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True)
    parser.add_argument("--origin", required=True)
    parser.add_argument("--method", default="POST")
    parser.add_argument("--headers", default="content-type")
    args = parser.parse_args()
    status, hdr = options(args.url, args.origin, args.method, args.headers)
    if status is None:
        print("UNREACHABLE %s: %s" % (args.url, hdr.get("error")))
        return 2
    findings = audit(status, hdr, args.origin)
    print("OPTIONS %s (Origin: %s) -> %s" % (args.url, args.origin, status))
    for f in findings:
        print("FINDING: " + f)
    print("RESULT %s" % ("FAIL" if findings else "PASS"))
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
