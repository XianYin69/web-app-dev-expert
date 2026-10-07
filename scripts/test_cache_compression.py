"""Test compression and cache revalidation behaviour of a URL (leaf 1).

Usage: python -B scripts/test_cache_compression.py --url URL
Exit code: 0 clean, 1 findings, 2 unreachable.
"""
import argparse
import gzip
import sys
import urllib.error
import urllib.request


def get(url, headers=None, method="GET"):
    req = urllib.request.Request(url, headers=headers or {}, method=method)
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            body = resp.read()
            return resp.status, dict(resp.headers), body
    except urllib.error.HTTPError as exc:
        return exc.code, dict(exc.headers), b""
    except (urllib.error.URLError, OSError) as exc:
        return None, {"error": str(exc)}, b""


def audit(url, enc_status, enc_hdr, enc_body, plain_body):
    findings = []
    low = {k.lower(): v for k, v in enc_hdr.items()}
    encoding = low.get("content-encoding", "")
    if not encoding and len(plain_body) > 1400:
        findings.append("no Content-Encoding on a %d-byte body" % len(plain_body))
    if encoding and "vary" not in low:
        findings.append("Content-Encoding %s without Vary: Accept-Encoding" % encoding)
    cc = low.get("cache-control", "")
    etag = low.get("etag")
    if not cc:
        findings.append("no Cache-Control: intermediaries may use heuristic freshness")
    if "immutable" in cc and "max-age=31536000" not in cc.replace(" ", ""):
        findings.append("'immutable' without a one-year max-age")
    if "no-store" not in cc and "no-cache" not in cc and not etag:
        findings.append("cacheable response without an ETag (no revalidation path)")
    if etag:
        status2, hdr2, _ = get(url, {"If-None-Match": etag})
        if status2 != 304:
            findings.append("If-None-Match returned %s, expected 304" % status2)
    if encoding in ("gzip", "x-gzip"):
        try:
            gzip.decompress(enc_body)
        except (OSError, EOFError) as exc:
            findings.append("gzip body failed to decode: %s" % exc)
    return findings


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True)
    args = parser.parse_args()
    status, enc_hdr, enc_body = get(args.url, {"Accept-Encoding": "gzip"})
    if status is None:
        print("UNREACHABLE %s: %s" % (args.url, enc_hdr.get("error")))
        return 2
    _, _, plain_body = get(args.url, {"Accept-Encoding": "identity"})
    findings = audit(args.url, status, enc_hdr, enc_body, plain_body)
    print("URL %s -> %s | encoded=%d identity=%d" % (args.url, status,
                                                     len(enc_body), len(plain_body)))
    for f in findings:
        print("FINDING: " + f)
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
