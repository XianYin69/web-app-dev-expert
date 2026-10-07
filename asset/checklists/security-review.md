# Security review checklist

Applies to any change touching auth, data exposure, headers, or external calls.

## Identity and access

- [ ] Authentication checked at the handler, not only in the router/UI
- [ ] Authorisation is object-level, not just role-level (IDOR probe attempted)
- [ ] Privilege change rotates the session id; logout invalidates server-side
- [ ] Token validation pins the algorithm and checks `iss`, `aud`, `exp`, `nbf`
- [ ] Refresh tokens are hashed, single-use, with reuse detection

## Input surface

- [ ] Every external input is schema-validated with a size limit
- [ ] SQL uses bound parameters; dynamic identifiers come from an allow-list
- [ ] File paths normalised and confined to a base directory (traversal probe)
- [ ] Uploads: type allow-list, size cap, stored off the web root, served
      with `Content-Disposition` and `X-Content-Type-Options: nosniff`
- [ ] Redirect targets validated against an allow-list (`probe_open_redirect.py`)
- [ ] Outbound URLs from user input are SSRF-checked (`security-hardening` leaf)

## Output surface

- [ ] Encoding matches the sink (HTML / attribute / JS / URL / CSS)
- [ ] Rich HTML sanitised through an allow-list and re-serialised
- [ ] Error responses carry codes, not internals; no reflected user input

## Transport and headers

- [ ] HTTPS everywhere; HSTS set with a deliberate `max-age`
- [ ] `X-Frame-Options`/`frame-ancestors`, `nosniff`, `Referrer-Policy` present
- [ ] CSP has no `unsafe-inline`/`unsafe-eval` without a documented exception
- [ ] Cookies scoped by `Path`/`Domain` as narrowly as possible

## Data and logging

- [ ] No secrets, tokens, or full PII in logs (`observability` leaf)
- [ ] Log sampling cannot drop security-relevant events
- [ ] Backups and exports exclude credential columns

## Verdict

Record findings as `blocker / fix-now / follow-up` with the probe command that
reproduces each one. A `blocker` stops the merge — see
[resistance](../../resistance/resistance.md).
