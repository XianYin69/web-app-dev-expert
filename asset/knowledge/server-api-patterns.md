# Leaf 2 — Server API patterns (REST / GraphQL / WS / SSE)

Parent: [asset](../asset.md) · Prev: [http-semantics-and-caching](http-semantics-and-caching.md)

## Choosing a protocol

- REST: resource-shaped data, cacheable by HTTP intermediaries, cheapest ops.
- GraphQL: many heterogeneous clients needing field selection; costs you
  HTTP caching, so add persisted queries and a query-depth/complexity budget.
- WebSocket: bidirectional, low-latency, stateful — needs fan-out and
  connection affinity; not cacheable, not proxy-friendly by default.
- SSE: one-way server events over HTTP; survives proxies, auto-reconnects via
  `Last-Event-ID`; prefer it for notifications before reaching for WS.

## REST shape

- Nouns for resources, plural collections; nesting ≤ 2 levels, filter by query.
- Pagination: cursor-based for mutable/large sets, offset only for stable small
  sets. Return the cursor in a `Link` header or an explicit `next` field.
- Errors: one machine-readable envelope (`type`, `title`, `status`, `code`,
  `details[]`), stable `code` strings, no stack traces in the body.
- Partial updates: `PATCH` with `application/merge-patch+json` semantics
  documented; `null` meaning "clear" must be stated, not assumed.

## Versioning and compatibility

- Version at the contract boundary (header or path), never per-field.
- Additive changes only within a version: new optional fields, new enum values
  require a client tolerance rule — unknown values must be ignorable.
- Publish a deprecation window with `Deprecation`/`Sunset` headers and a
  measured adoption floor before removal.

## Realtime plumbing

- Heartbeat interval below the shortest idle timeout on the path (LB/proxy).
- Backpressure: drop or coalesce per-topic, never block the writer loop.
- Reconnect with exponential backoff plus jitter; resume from a sequence number.
- Fan-out: single-writer per connection queue; broadcast via pub/sub, not loops.

## Contract hygiene

- Generate server stubs and client types from one source of truth.
- Lint the live surface against the spec: `scripts/check_api_contract.py`.
