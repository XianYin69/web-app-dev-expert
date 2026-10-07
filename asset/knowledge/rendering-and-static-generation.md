# Leaf 5 — Server rendering and static generation

Parent: [asset](../asset.md) · Next: [data-access-and-migrations](data-access-and-migrations.md)

## Choosing a rendering model

- Static generation (SSG): content known at build; cheapest, cacheable by CDN,
  but every edit needs a rebuild or on-demand revalidation.
- SSR: per-request personalisation or high-churn data; costs origin latency and
  needs a timeout/degradation path when the data source is slow.
- ISR / stale-while-revalidate: serve the cached page, refresh in the background
  — best default for semi-dynamic pages; define the acceptable staleness window.
- Client-only rendering: last resort for SEO-visible or above-the-fold content.

## Hydration discipline

- Ship HTML first, then the minimum JS needed to make it interactive; prefer
  islands/partial hydration over one monolithic root.
- Server and client must render identical markup — mismatches (dates, locale,
  random ids, `window` access) cause re-render storms.
- Keep first-party JS budgets per route; measure the cost of each dependency
  before adding it (see [performance-budgets](performance-budgets.md)).

## Caching rendered output

- Separate cache keys by cookie presence: anonymous traffic should be
  `public, s-maxage` cacheable; personalise at the edge, not at the origin.
- Emit `Vary` for every request header the renderer actually reads.
- Purge on publish events, and keep a short TTL as a safety net.

## Failure modes

- Renderer must degrade: cached shell plus a "data unavailable" slot beats a
  500 page. Set explicit upstream timeouts and retry only idempotent fetches.
- Bots and crawlers: respect `If-Modified-Since`/`ETag`; avoid rendering
  infinite calendar/pagination surfaces.
- Streaming responses: flush the shell early, but never stream a partial page
  that will later 500 — buffer the head.

## Probes

`scripts/sample_web_vitals.py` · `scripts/report_bundle_budget.py`
