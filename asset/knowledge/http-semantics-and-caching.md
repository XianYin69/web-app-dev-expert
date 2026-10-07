# Leaf 1 — HTTP semantics, idempotency, caching

Parent: [asset](../asset.md) · Next: [server-api-patterns](server-api-patterns.md)

## Methods and status codes

- `GET`/`HEAD` are safe; `PUT`/`DELETE` are idempotent by definition;
  `POST` is neither. Never overload `GET` with side effects.
- 2xx success · 3xx redirection · 4xx client fault · 5xx server fault.
- Use `409 Conflict` for state clashes, `422` for semantic validation,
  `429` with `Retry-After` for rate limits, `503` for overload/shedding.
- `202` means accepted, not done — pair it with a status resource or `Location`.

## Idempotency

- Client supplies `Idempotency-Key`; server stores key → response for a TTL
  (≥ the longest retry window) and replays it on duplicate delivery.
- Retries must be safe: dedupe on the key, not on wall-clock equality.
- Non-idempotent mutations behind a queue need a DLQ, a reconciliation job and the key logged per attempt.

## Conditional requests

- `ETag`: strong validator for cache revalidation and `If-Match` concurrency
  control. Emit it for every representation that can change.
- `Last-Modified` is second-granular — prefer `ETag` when sub-second edits exist.
- `304 Not Modified` must carry no body and repeat cache-relevant headers.

## Cache-Control

- Private, per-user responses: `private, max-age=0, must-revalidate` or
  `no-store` when the response contains secrets.
- Public, immutable assets: `public, max-age=31536000, immutable` with a
  content hash in the filename.
- Shared caches: `s-maxage` overrides `max-age` for CDNs; use
  `stale-while-revalidate` to hide origin latency on slow-changing data.
- Never cache `Authorization`-bearing responses unless `public` is explicit.
- Invalidation: prefer short TTLs plus revalidation over purge broadcasts.

## Pitfalls

- Compression negotiated per request: `Vary: Accept-Encoding` must accompany
  any cached `Content-Encoding` variant, or clients get wrong bytes.
- `no-cache` ≠ `no-store`: it allows storage but requires revalidation.
- Range requests, partial uploads and streaming responses bypass ETag reuse —
  handle `Accept-Ranges`/`Content-Range` explicitly.

## Probes

`scripts/check_response_headers.py` · `scripts/test_cache_compression.py` ·
`scripts/check_idempotency.py`
