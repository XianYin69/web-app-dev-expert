# Leaf 3 — Authentication and session management

Parent: [asset](../asset.md) · Next: [security-hardening](security-hardening.md)

## Cookie attributes (server-rendered / cookie-session apps)

- `HttpOnly` — blocks script read access; mandatory for session cookies.
- `Secure` — HTTPS only; set it unconditionally in production.
- `SameSite` — `Lax` default for session cookies; `Strict` when no external
  referrer flow; `None` requires `Secure` and is only for cross-site embeds.
- `Path`/`Domain` scoped as narrowly as the use case allows; never widen `Domain`.
- Session cookie ≠ CSRF token: the double-submit or synchroniser token pattern
  is still required for state-changing requests.

## Sessions

- Server-side session store with an idle timeout plus an absolute timeout.
- Rotate the session id on privilege change (login, role elevation) — prevents
  session fixation.
- Invalidate on logout server-side; a client-side cookie delete is not a logout.
- Concurrent-session policy (allow-list of devices vs single-session) must be
  explicit; store the reason for revocation for support triage.

## Tokens (JWT)

- Prefer short-lived access tokens (5–15 min) with refresh-token rotation.
- Validate `iss`, `aud`, `exp`, `nbf`, and pin the algorithm — never trust
  `alg` from the token; reject `none`.
- JWTs are not encrypted: no PII or secrets in claims; keep the payload small
  to stay under header size limits.
- Revocation needs a denylist or short TTL — a stateless token cannot be
  un-issued. Store refresh tokens hashed, one-time-use, with reuse detection.

## OAuth2 / OIDC

- Use Authorization Code + PKCE for browser and mobile; implicit flow is
  deprecated. Validate `state` (CSRF) and `nonce` (id-token replay).
- Match `redirect_uri` by exact string, not prefix; reject open matchers.
- Verify ID-token signature against the issuer JWKS with cache rotation;
  never accept a token signed by an unrelated `aud`.
- Map external identity → local principal at first login, and store the link
  so a provider outage does not orphan the account.

## Probes

`scripts/check_cookie_attrs.py` · `scripts/probe_open_redirect.py`
