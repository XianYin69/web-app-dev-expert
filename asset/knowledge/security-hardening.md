# Leaf 4 — Security hardening (headers, injection, SSRF, CORS)

Parent: [asset](../asset.md) · Next: [rendering-and-static-generation](rendering-and-static-generation.md)

## Response headers

- `Content-Security-Policy`: start from `default-src 'self'`; avoid
  `unsafe-inline`/`unsafe-eval`; use nonces or hashes for inline scripts and
  rotate the nonce per response. Ship `report-to`/`Report-To` reporting before
  enforcing, and keep `frame-ancestors 'none'` (or explicit allow-list).
- `X-Content-Type-Options: nosniff`, `Referrer-Policy: strict-origin-when-cross-origin`,
  `Cross-Origin-Opener-Policy`/`Cross-Origin-Resource-Policy` as needed.
- `Strict-Transport-Security`: `max-age≥31536000; includeSubDomains` on HTTPS
  origins; preload only after every subdomain is HTTPS-safe (hard to reverse).
- `Permissions-Policy`: deny geolocation, camera, microphone, payment unless used.
- Do not leak `Server`, `X-Powered-By`, stack traces, or internal hostnames.

## XSS and output handling

- Encode at the sink (HTML attr, JS string, URL, CSS) — context-aware, not
  blanket escaping. Sanitise rich HTML with an allow-list, then re-serialise.
- Auto-escaping templates are not a licence to use `|safe`/`dangerouslySetInnerHTML`.
- User-controlled URLs: force `https:`/`http:`/`mailto:` schemes; block
  `javascript:` and `data:`; validate redirect targets against an allow-list.

## Injection

- Parameterised queries only; identifiers (table/column names) come from an
  enum, never from concatenation.
- Shell/`exec`: pass argv arrays, never build strings; validate paths to stop
  traversal; treat archive extraction as untrusted input (zip-slip).
- Deserialisation: no unsafe object loading from network or queue payloads.

## SSRF

- Resolve then validate the IP (block RFC1918, loopback, link-local, metadata
  `169.254.169.254`); re-check after redirect, or disable redirects.
- Allow-list hosts/schemes; egress via a proxy with per-destination policy.

## CORS

- Exact-origin allow-list; `Access-Control-Allow-Credentials: true` never with
  `*`. Cover preflight: method, headers, `Max-Age`, and `Vary: Origin`.
- CORS is not an authorisation mechanism — the server must still check identity.

## Probes

`scripts/check_response_headers.py` · `scripts/probe_cors_preflight.py` ·
`scripts/probe_injection_surface.py` · `scripts/check_tls_chain.py`
