# billtracking.org — static site

The public site for BillTracking. Plain HTML and CSS, no build step, no
dependencies, no JavaScript framework. `style.css` is the living style reference
that the mobile app's design tokens are translated from — when the two disagree,
this file wins.

Intended to be served by GitHub Pages at **billtracking.org**.

## ⚠️ This repo IS the live site — everything in it is public

GitHub Pages serves this repo whole at billtracking.org (live since 2026-07;
push = deploy). So **nothing goes in here that isn't meant to be read by
anyone**: no notes, no fixtures, no secrets. This repo holds what is served
plus ONE tool: hand-written pages, `style.css`, `legal/` (the D23 policy
SOURCES — public on purpose), the app's web export (`us.html`, `eu.html`,
`bill/`, `_expo/`, `assets/`, `404.html`), the workflow-rendered `p/` pages,
and `tools/generate.py` (the permalink generator — public by design so this
repo's own workflow can run it with no credentials; a page renderer, nothing
secret in it). The legal generator, the sample fixtures and the launch-time
deep-link files live in the PRIVATE app repo at `app/site-build/`.

**Two launch-time steps still pending:**

1. **Deep-link association files.** `app/site-build/well-known-pending/` holds
   `apple-app-site-association` and `assetlinks.json` with placeholders
   (`REPLACE_TEAM_ID`, package, SHA-256). At store launch: fill them, then
   copy them to a served `/.well-known/` at THIS repo's root. Serving them
   malformed fails silently (links just open the browser). Full instructions:
   `app/site-build/well-known-pending/LAUNCH-README.md`.
2. **Store URLs** in `tools/generate.py` `STORE_URLS` once the listings exist —
   the funnel under every post page then shows real store buttons (until then
   it truthfully says the app is coming).

## Permalink pages

`tools/generate.py` renders one static page per delivered post at `/p/<id>`,
plus a sitemap and a browse index, from the bots' PUBLISHED feed. It is run
by this repo's own workflow (`.github/workflows/permalinks.yml`, every 2 h +
manual) with the built-in workflow token — no credentials — which commits
ONLY `p/`. Every id equals the app's "Copy link" id (proven by the app repo's
`check:permalinks`). Runbook: `app/docs/PERMALINKS.md`.

`p/` is tracked but written by that workflow ALONE. Never commit a locally
generated `p/`: a sample-fed run (the fixtures live in `app/site-build/`)
renders FABRICATED bills — publishing those would be the single most damaging
thing this repo could do. `--out` is required precisely so a bare run cannot
land here.

## Deploying

Pages serves from the repository root on `main`. `.nojekyll` is present so files
are served as-is rather than run through Jekyll.

Once Pages is enabled and the domain is pointed at it, the checklist for any
site change is: re-submit the sitemap in Search Console.

⚠️ **This site carries no analytics and no JavaScript at all** — verified
2026-07-19 by a full audit of every HTML, CSS and JS file. Zero third-party
resources; fonts are self-hosted woff2 (`style.css:8-28`). An earlier version of
this checklist said to "confirm the GA4 tag is still on every page". That was
imported in error from the YAP site, which is a different property. **There is no
GA4 tag here and there never was.** Do not add one, and do not carry YAP's
analytics disclosure into this project's privacy policy — it would make the
policy false on its first day.

If analytics is ever added, see `ANALYTICS-DECISION.md` (it lives in the **app** repo, under
`app/legal/`) and add the check back — but change `legal/privacy.md` and regenerate FIRST (D23),
or the published policy becomes false on day one.

## Legal pages (privacy / terms)

`privacy.html` and `terms.html` are **generated**, not hand-edited. Their single
source of truth is `legal/privacy.md` / `legal/terms.md`, and one generator
renders each into both this site and the app's in-app screen:

```bash
python ../app/site-build/generate_legal.py   # writes *.html here + *.generated.ts in the app repo
```

So updating a policy is: edit the `.md`, run that, commit both repos. Grammar
and the full workflow are in [`legal/LEGAL-SPEC.md`](legal/LEGAL-SPEC.md); the
app side is in the app repo's `DECISIONS.md` D23. `delete-account.html` is still
hand-authored (not yet on this pipeline).

## Consistency with the app

Any promise or claim made here must match the app, and vice versa —
`accuracy.html` mirrors the app's accuracy screen. If you soften a commitment in
one, soften it in the other in the same change. The privacy/terms text can no
longer drift: both surfaces render from the one `legal/*.md` source (see above).
