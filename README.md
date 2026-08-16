# billtracking.org — static site

The public site for BillTracking. Plain HTML and CSS, no build step, no
dependencies, no JavaScript framework. `style.css` is the living style reference
that the mobile app's design tokens are translated from — when the two disagree,
this file wins.

Intended to be served by GitHub Pages at **billtracking.org**.

## ⚠️ This repo IS the live site — everything in it is public

GitHub Pages serves this repo whole at billtracking.org (live since 2026-07;
push = deploy). So **nothing goes in here that isn't meant to be read by
anyone**: no tooling, no notes, no fixtures. Since 2026-08-16 the site's
build tooling lives in the PRIVATE app repo at `app/site-build/` — the two
generators, the sample fixtures, and the launch-time deep-link files. This
repo holds only what is served: hand-written pages, `style.css`, `legal/`
(the D23 policy SOURCES — public on purpose), the app's web export
(`us.html`, `eu.html`, `bill/`, `_expo/`, `assets/`, `404.html`), and `p/`
once it is generated from the real feed.

**Two launch-time steps still pending (both driven from `app/site-build/`):**

1. **Deep-link association files.** `app/site-build/well-known-pending/` holds
   `apple-app-site-association` and `assetlinks.json` with placeholders
   (`REPLACE_TEAM_ID`, package, SHA-256). At store launch: fill them, then
   copy them to a served `/.well-known/` at THIS repo's root. Serving them
   malformed fails silently (links just open the browser). Full instructions:
   `app/site-build/well-known-pending/LAUNCH-README.md`.
2. **`p/` permalink pages** must be generated from the REAL feed, never from
   the sample fixtures. Publishing fabricated bill pages would be the single
   most damaging thing this repo could do, on a site whose pitch is accuracy.

## Permalink pages

`app/site-build/generate.py` renders one static page per delivered post at
`/p/<id>.html`, plus a sitemap and a browse index, from the bots' feed export.
No pipeline runs it yet (the live `/p/` is 404 today) — it is a launch-time
piece, wired when share links go live.

```bash
python ../app/site-build/generate.py --feed <feed.jsonl> --out .   # from this repo
```

Output lands in `p/`, which is **gitignored on purpose** — it is build output,
not source. Regenerate at deploy time; never commit it. The synthetic fixtures
(`sample-feed.jsonl`, `sample-overrides.jsonl`) live beside the generator in
the app repo and are for testing only.

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
