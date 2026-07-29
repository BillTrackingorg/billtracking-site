# billtracking.org — static site

The public site for BillTracking. Plain HTML and CSS, no build step, no
dependencies, no JavaScript framework. `style.css` is the living style reference
that the mobile app's design tokens are translated from — when the two disagree,
this file wins.

Intended to be served by GitHub Pages at **billtracking.org**.

## ⚠️ Before enabling GitHub Pages

Pages is deliberately **not** enabled yet. Two things must be true first.

**1. `.well-known/` still contains placeholders.**
`apple-app-site-association` reads `REPLACE_TEAM_ID.REPLACE_IOS_BUNDLE_ID`, and
`assetlinks.json` has no Android package or signing SHA-256. These are the files
iOS and Android fetch to decide whether a `billtracking.org/p/...` link may open
the app. Serving them malformed doesn't produce an error anyone sees — universal
links just silently fail. The real values only exist once the app is registered
with the stores. See [`.well-known/LAUNCH-README.md`](.well-known/LAUNCH-README.md).

**2. `p/` must be regenerated from the real feed.**
It is gitignored, and the copy currently on disk was built from *synthetic
sample data*. Publishing fabricated bill pages would be the single most damaging
thing this repo could do, on a site whose entire pitch is accuracy.

## Permalink pages

`build/generate.py` renders one static page per delivered post at
`/p/<id>.html`, plus a sitemap and a browse index, from the bots' feed export.

```bash
python build/generate.py --feed <feed.jsonl> --out .
```

Output lands in `p/`, which is **gitignored on purpose** — it is build output,
not source. Regenerate at deploy time; never commit it.

`build/sample-feed.jsonl` and `build/sample-overrides.jsonl` are synthetic
fixtures for testing the generator, not real data.

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

If analytics is ever added, see `ANALYTICS-DECISION.md` and add the check back.

## Legal pages (privacy / terms)

`privacy.html` and `terms.html` are **generated**, not hand-edited. Their single
source of truth is `legal/privacy.md` / `legal/terms.md`, and one generator
renders each into both this site and the app's in-app screen:

```bash
python build/generate_legal.py        # writes *.html here + *.generated.ts in the app repo
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
