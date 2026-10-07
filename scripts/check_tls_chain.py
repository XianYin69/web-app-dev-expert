"""Verify TLS certificate chain, expiry and protocol of a host (leaf 4/8).

Usage: python -B scripts/check_tls_chain.py --host example.com [--port 443]
Exit code: 0 clean, 1 findings, 2 connect error.
"""
import argparse
import socket
import ssl
import sys
from datetime import datetime, timezone

WARN_DAYS = 30


def connect(host, port, timeout=15):
    ctx = ssl.create_default_context()
    with socket.create_connection((host, port), timeout=timeout) as sock:
        with ctx.wrap_socket(sock, server_hostname=host) as tls:
            cert = tls.getpeercert()
            return tls.version(), tls.cipher(), cert


def parse_date(value):
    fmt = "%b %d %H:%M:%S %Y %Z"
    return datetime.strptime(value, fmt).replace(tzinfo=timezone.utc)


def audit(host, version, cipher, cert):
    findings = []
    if version not in ("TLSv1.2", "TLSv1.3"):
        findings.append("weak protocol negotiated: %s" % version)
    if cipher:
        name, bits = cipher[0], cipher[2]
        if "CBC" in name and version == "TLSv1.3":
            findings.append("unexpected CBC suite on TLS1.3: %s" % name)
        if bits < 128:
            findings.append("cipher strength below 128 bit: %s" % name)
    not_after = parse_date(cert["notAfter"])
    not_before = parse_date(cert["notBefore"])
    now = datetime.now(timezone.utc)
    days = (not_after - now).days
    if days < 0:
        findings.append("certificate EXPIRED on %s" % cert["notAfter"])
    elif days < WARN_DAYS:
        findings.append("certificate expires in %d days (%s)" % (days, cert["notAfter"]))
    if not_before > now:
        findings.append("certificate not yet valid")
    subjects = dict(x for x in cert["subject"])
    cn = subjects.get("commonName", "")
    sans = [v for k, v in cert.get("subjectAltName", ()) if k == "DNS"]
    if host not in sans and not (cn == host):
        findings.append("host %s not in SAN list %s" % (host, sans or cn))
    chain_len = len(cert.get("issuer", ()))
    return findings, {"version": version, "cipher": cipher[0] if cipher else None,
                      "not_after": cert["notAfter"], "san_count": len(sans),
                      "issuer_depth": chain_len}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", required=True)
    parser.add_argument("--port", type=int, default=443)
    args = parser.parse_args()
    try:
        version, cipher, cert = connect(args.host, args.port)
    except (ssl.SSLError, socket.gaierror, OSError) as exc:
        print("CONNECT-ERROR %s:%s %s" % (args.host, args.port, exc))
        return 2
    findings, info = audit(args.host, version, cipher, cert)
    print("TLS %s %s | notAfter=%s | SANs=%s" % (args.host, info["version"],
                                                 info["not_after"], info["san_count"]))
    for f in findings:
        print("FINDING: " + f)
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
