# billtracking.org — static site

The public site for BillTracking. Plain HTML and CSS, no framework, no
dependencies to install. `style.css` is the living style reference that the
mobile app's design tokens are translated from — when the two disagree, this
file wins.

The feed, vote and account pages additionally run **one first-party script,
`assets/js/bt-web.js`** — the app's own data layer, compiled. It is never
written or built here: see "The compiled core" below and
[`tools/README-bt-site.md`](tools/README-bt-site.md).

Intended to be served by GitHub Pages at **billtracking.org**.

## ⚠️ This repo IS the live site — everything in it is public

GitHub Pages serves this repo whole at billtracking.org (live since 2026-07;
push = deploy). So **nothing goes in here that isn't meant to be read by
anyone**: no notes, no fixtures, no secrets. This repo holds what is served
plus the compiled core: hand-written pages, `style.css`, `assets/css/feed.css`,
`legal/` (the D23 policy SOURCES — public on purpose), the feed/account/callback
shells (`us.html`, `eu.html`, `account.html`, `auth/callback.html`, `404.html`),
the workflow-rendered `p/`, `b/` and `view/` trees, and in `assets/js/` +
`tools/` the two compiled bundles (`bt-web.js` for the browser, `bt-site.cjs`
for the workflow — public by design so this repo's own workflow can run with no
credentials; the app's DATA layer, not its screens, and nothing secret in it).
The legal generator and the launch-time deep-link files live in the PRIVATE app
repo at `app/site-build/`.

⚠️ **Never copy a `*.map` in with the bundles.** esbuild's source maps embed the
whole of the app's private TypeScript, comments included.

**Two launch-time steps still pending:**

1. **Deep-link association files.** `app/site-build/well-known-pending/` holds
   `apple-app-site-association` and `assetlinks.json` with placeholders
   (`REPLACE_TEAM_ID`, package, SHA-256). At store launch: fill them, then
   copy them to a served `/.well-known/` at THIS repo's root. Serving them
   malformed fails silently (links just open the browser). Full instructions:
   `app/site-build/well-known-pending/LAUNCH-README.md`.
2. **Store URLs** once the listings exist — `STORE_URLS` now lives with the
   renderer, in the app repo's `src/site/chrome.ts`; fill it, rebuild, copy the
   bundle. The funnel under every post page then shows real store buttons (until
   then it truthfully says the app is coming, and a check fails if a button
   appears while the URLs are empty).

## The compiled core — `assets/js/bt-web.js` and `tools/bt-site.cjs`

Both are **compiled artefacts of the private app repo** (`DECISIONS.md` D28 there:
one packager, many renderers). They are never edited here and never built here —
the build refuses to emit unless the app's own `npm run check` is green, which is
the whole reason a compiled bundle is allowed to sit in a public repo. `bt-web.js`
is what the feed, account and callback pages load; `bt-site.cjs` is what the
workflow runs. Build-and-copy commands: [`assets/js/README.md`](assets/js/README.md)
§8. What the renderer writes and why: [`tools/README-bt-site.md`](tools/README-bt-site.md).

`tools/generate.py` is the retired Python renderer. **Nothing calls it.** It stays
in the tree only until the swap is proven byte-for-byte over the live pages —
deleting it early would remove the only thing the swap can be proven against.

## Permalink + bill pages

`tools/bt-site.cjs` renders, from the bots' PUBLISHED feed + per-bill path
artifacts, in one workflow run (`.github/workflows/permalinks.yml`, every 15 min
+ manual, built-in token — no credentials; the run starts by making the bundle
prove itself with `--selftest`):

- **`/p/<id>`** — one static page per delivered post (the shared artifact +
  funnel), plus `p/sitemap.xml` and a `/p/` browse index. Post pages are
  `noindex` and are the bill pages' citations.
- **`/b/<polity>/<slug>`** — the INDEXABLE unit: one page per bill (`/b/us/119-hr-3497`,
  `/b/eu/2023-0447-cod`), showing the same merged path the app's bill screen
  shows, plus a `/b/<polity>/` index and a root `bill-sitemap.xml`. Bill pages
  carry `noindex` until the owner's Gate-2 flip (`INDEX_BILL_PAGES`, in the app
  repo's `src/site/chrome.ts`). `/b/` is a SEPARATE tree from the app's web
  export `bill/[ref].html`.
- **`view/v1/`** — the same render, packaged as JSON (index, shaped months,
  per-bill views, the legislature registry). Published as data for a future
  surface; **nothing depends on it today.**

Every id and every bill row is the app's own, because the renderer IS the app's
own code — parity by construction rather than by a check holding two
implementations equal. Runbook + the IMMUTABLE slug law: `app/docs/PERMALINKS.md`.
SEO model: `app/docs/WEB.md` §SEO.

`p/`, `b/` and `view/` are tracked but written by that workflow ALONE
(stray-file + set-diff shrink guards refuse anything else). Never commit a
locally rendered copy, and never point `--out` at this repo — that is why `--out`
is required.

**Adding a legislature:** ⚠️ **this changed on 2026-08-19.** An unregistered
`bot` value no longer auto-renders generically — the app's registry is the one
definition of a legislature the build carries, so the app and this site are short
by exactly the same posts, and the workflow log `::warning::`s the id. The fix is
one entry in the app repo's `src/data/legislatures.ts` plus a rebuilt bundle.
Nothing changes in this repo.

## Deploying

Pages serves from the repository root on `main`. `.nojekyll` is present so files
are served as-is rather than run through Jekyll. **Push = deploy = live.**

Once Pages is enabled and the domain is pointed at it, the checklist for any
site change is: re-submit the sitemap in Search Console.

⚠️ **Pages serves cached HTML for about ten minutes.** So a push that lands new
HTML without the bundle it names gives every visitor a page stuck on "Loading…"
for at least that long. **The bundle ships in the same push as the HTML, or
before it** — never after. The same ten minutes is why removing the old Expo
export is three separate pushes (`app/docs/WEB.md`).

⚠️ **This site carries no analytics and no tracking of any kind, and no
third-party resources at all.** No GA, no pixel, no tag manager, no CDN, no
remote fonts — fonts are self-hosted woff2 (`style.css:8-28`). The feed, vote and
account pages run exactly ONE script, our own `assets/js/bt-web.js`, compiled from
the app's code and served from this origin; every other page runs none.

**This line used to say "no JavaScript at all"** (a full-file audit, 2026-07-19,
true when it was written). It stopped being true on 2026-08-14 and is corrected
here on 2026-08-19. It is also the exact failure `DECISIONS.md` D26 is about: a
description of how something happened to be built, written down as though it were
a promise, and then found steering architecture. **The promise is the outcome — no
analytics, no trackers, nothing recorded — and that one is intact.** Do not
re-promise a mechanism here or anywhere public.

An earlier version of this checklist said to "confirm the GA4 tag is still on
every page". That was imported in error from the YAP site, which is a different
property. **There is no
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
