# Leaf 9 — Performance budgets (Core Web Vitals, bundle, loading)

Parent: [asset](../asset.md) · Back: [observability-and-deployment](observability-and-deployment.md)

## Core Web Vitals

- **LCP** — largest contentful paint: dominated by TTFB, render-blocking
  resources and hero-image discovery. Fix order: reduce server time, preload
  the hero, inline critical CSS, avoid third-party iframes above the fold.
- **INP** — interaction to next paint (replaced FID): long tasks block the
  main thread. Yield with `scheduler.yield`/`setTimeout` chunks, move work to
  workers, and trim hydration cost on the route.
- **CLS** — cumulative layout shift: reserve space (`width`/`height` or
  `aspect-ratio`) for media, never inject banners above content, use `font-display: optional`
  or size-adjusted fallbacks to stop reflow on webfont swap.
- Thresholds are p75 of field data, not lab numbers. Lab runs validate a fix;
  field data proves it. Never quote a figure you did not measure.

## Budgets

- Declare per-route budgets in the repo: initial JS (compressed), CSS, fonts,
  images, total transfer, and a TTFB ceiling. Fail CI on regression.
- JS is the expensive asset: each framework-sized dependency needs a measured
  cost and a review sign-off before it enters the bundle.
- Split by route; lazy-load below-the-fold and rarely used features; prefetch
  only on high-confidence intent (hover/viewport), never blanket-prefetch.

## Images, fonts, caching

- Modern formats, responsive `srcset`, explicit dimensions, `loading="lazy"`
  except the LCP candidate (which gets `fetchpriority="high"` + preload).
- Fonts: subset, `font-display` chosen deliberately, max two families; preload
  only the critical face.
- Hashed asset filenames → `immutable` one-year cache; HTML → short TTL so a
  deploy is visible immediately.

## Measurement

- `scripts/sample_web_vitals.py` for field/lab sampling;
  `scripts/report_bundle_budget.py` for the budget gate;
  `scripts/test_cache_compression.py` for transfer size and cache hits.
- Regressions are triaged like bugs: bisect the deploy, revert the flag, then fix.
