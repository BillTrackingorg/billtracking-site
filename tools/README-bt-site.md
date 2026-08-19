# `bt-site.cjs` — the static site renderer

`tools/bt-site.cjs` renders `/p/`, `/b/`, their indexes, the sitemaps and the
published `view/` tree. It is **the app's own code, compiled** — not a program
written for this repo.

It replaces `tools/generate.py`, which PORTED the app's adapter, its id
derivation, the one date formatter, the D9 bucket map, the bill identity, the
path merge and the glyph table into Python. Two implementations of every product
rule were held equal by one check (`scripts/check-permalinks.js` in the app
repo), and that check earned its keep — it caught an id scheme that would have
404'd every share link ever copied. But a check that proves two implementations
equal has to be extended every time either one learns something. The answer to
two implementations is one (web-overhaul plan §12(1), `DECISIONS.md` D27).

**`generate.py` was deleted on 2026-08-19** (phase 2 of the cut-over) after the swap was
proven over the live corpus — page sets, canonicals, row orders and JSON-LD equal; the
HTML bodies differ only by the deltas listed below. Its history is in git.

---

## Where it comes from

It is built in the **private app repo**, never here:

```sh
# app repo (Projects/BillTracking/app)
npm run check          # everything must be green — the build refuses otherwise
npm run build:core     # → site-build/core/out/site/bt-site.cjs
```

`build:core` runs `npm run check` first and **refuses to emit a bundle if it
fails**. That is the whole point of compiling the app into the website: a bundle
built from a tree whose own checks are red would ship exactly the silent
divergence this architecture exists to prevent.

The resulting file is copied to `tools/bt-site.cjs` and committed here. The site
repo is public and is served whole, so what lands here is compiled, minified
JavaScript and its source map — the same posture the Expo export already had,
two orders of magnitude smaller. **No credentials, no secrets, nothing private:
the bundle is the app's DATA layer, not its screens.**

The bundle carries a build stamp (`appSha`, `builtAt`, `schemaV`). The workflow
logs it, so any generated page can be traced to the exact core that produced it —
skew is observable, never assumed.

---

## The contract

```sh
node tools/bt-site.cjs --feed feed --paths paths --out out
node tools/bt-site.cjs --feed feed --list-paths     # artifact filenames to fetch
node tools/bt-site.cjs --selftest                   # the fixture assertions
```

| flag | meaning |
|---|---|
| `--feed <dir\|file>` | repeatable. A directory contributes its `*.jsonl` sorted by name, minus `*-overrides.jsonl`. **Required.** |
| `--overrides <file>` | repeatable. Omitted ⇒ every `--feed` directory is scanned for `*-overrides.jsonl`, which is how the bots publish the corrections sheets. |
| `--paths <dir>` | the bill-path artifacts the workflow already fetched. Omitted ⇒ every bill renders posts-only, which is honest and is what the app shows when an artifact is missing. |
| `--out <dir>` | **required for a render.** Pages go to `<out>/p/`, `<out>/b/`, `<out>/view/`. There is no default: a bare run used to default to this repo and render sample fixtures into the deploy tree (adversarial review 2026-08-16). There is no sample corpus at all now. |
| `--sprite <file>` | defaults to `glyphs.svg` **beside this script**. The sprite is build input, inlined into every page that draws glyphs — never linked (`assets/js/README.md` §5). |
| `--list-paths` | print the artifact filenames the feed needs, one per line, and exit. |
| `--selftest` | run the fixture assertions compiled into the bundle and exit. |

**Exit codes.** `0` = the render is publishable. `1` = something would have made
a page untrustworthy, so the workflow commits nothing (loudness doctrine). `2` =
the arguments were wrong.

**Log lines.** Warnings and errors are printed at column 0 as `::warning::` /
`::error::`, which is where GitHub's annotation parser reads them. (The Python
logger prefixed its level name, pushing the marker off column 0 — a guard
finding from 2026-08-17 that needed a re-emit step in the workflow. That step is
gone.) Ordinary gaps are warnings: a record the app also drops, an artifact that
would not parse, a legislature this build does not carry.

### What it writes

| path | what |
|---|---|
| `p/<id>.html` | one page per POST — the share-link landing and OG card |
| `p/index.html`, `p/sitemap.xml` | the post index and its sitemap (noindex) |
| `b/<polity>/<slug>.html` | one page per BILL — the indexable unit |
| `b/<polity>/index.html` | the per-legislature bill index |
| `bill-sitemap.xml` | the bill sitemap (listed in `robots.txt` only at Gate 2) |
| `view/v1/…` | the published packaged form: `index.json`, `<polity>-<month>.json`, `bills/<polity>/<slug>.json`, `registry.json` |
| `.suppressed-pages`, `.suppressed-bills` | the workflow's set-diff shrink guards read these; they are never published |

`p/`, `b/` and `view/` are **workflow-owned trees**. Never hand-edit them, and
never commit a locally rendered copy.

---

## What is the app's, and what is this repo's

Everything a reader can read about a record comes from a module the phone also
runs: which records exist at all (the adapter's drop-never-guess), corrections
and automatic revisions, which bill a post is about, the merged path, the
artifact's schema gate and Congress belt, what a card and a bill page SAY (the
two content models), and how they are drawn (`render/card.ts`,
`render/bill-path.ts`).

What the site owns is its own chrome: the header, the nav, the footer, the
funnel, the page CSS, the `<head>`, the JSON-LD, the indexes and the sitemaps.
None of it decides anything a reader could compare against the app.

**The page set is the app's minted set, exactly.** A record the app drops gets no
page; a bill the app cannot honestly identify gets no bill page. That parity used
to be asserted across two languages; it is now true by construction.

---

## Deltas from `generate.py` (deliberate, and worth knowing before the swap)

1. **`/p/` shows the COMPOSED CARD** — the same card the app and the feed pages
   draw — with the archived post text beneath it in a collapsed
   "As published" block (owner call). The Python page showed the archived text
   alone. The card ships open and draws no expander: a static page has no script
   to operate one, and a dead control is a fabricated affordance.
2. **Bill pages collapse routine runs** in `<details>` with the app's own
   "N more actions" wording, and carry **What's next** on the tip.
3. **Glyphs are always SVG.** The `--glyphs emoji|svg` switch is gone; the emoji
   survives wherever the app's own table does not know a prefix (the BELT).
4. **`view/`** is published. Nothing depends on it today — the app and the live
   web feed fetch the bots' record directly, which is the stronger honesty
   story — but it is the designated path for the next surface, and it publishes
   the core's OWN shapes rather than a hand-shaped projection.
5. **An UNREGISTERED legislature is dropped, not auto-adopted.** The Python
   generator rendered an unknown `bot` value generically. The app's registry
   (`data/legislatures.ts`) is now the one definition of a legislature this build
   carries, and the adapter drops what it has no grammar, no colours and no words
   for — so the app and the site are short by the same posts. It is a `::warning::`
   naming the id, never silent, and the fix is one registry entry plus a rebuilt
   bundle.
6. **Copy that now comes from the app's content model**: the bill page's kicker
   is the legislature as a place ("United States"), the honesty box is the app's
   tri-state, and the correction banner is the app's own stamp
   (`Corrected <date>. <reason> — originally "…"`) rather than a second wording.
   A `revision-link` override no longer renders a "Superseded" banner: the app
   has never shown one, and D19's automatic linking does that job.
7. **The page accent is `var(--navy)` / `var(--royal)`**, the token the registry
   already names, instead of a hex written into the generator. The palette stays
   in `style.css`, where it lives.
8. **The chrome is the site's chrome**: the four-column footer the hand-authored
   pages carry, and the same `<meta>` CSP.

---

## Verifying a change before it ships

In the app repo:

```sh
npm run check:site        # the same assertions the bundle carries, over fixtures
npm run check             # everything, including check:permalinks (still Python)
```

Here, before the swap:

```sh
# the swap gate that was run on 2026-08-19 (kept for the record; generate.py is gone):
#   python tools/generate.py --feed feed --paths paths --out /tmp/py   (git show 2dd10e6:tools/generate.py)
#   node   tools/bt-site.cjs  --feed feed --paths paths --out /tmp/ts
#   diff -r /tmp/py/p /tmp/ts/p  — only the deltas listed above
node tools/bt-site.cjs --selftest
```

## The Gate-2 flip

**Flipped 2026-08-19.** Bill pages and the `/b/` indexes are indexable and
`bill-sitemap.xml` is listed in `robots.txt`; `/p/` pages stay `noindex` forever (they
are the bill's citations). The switch is ONE constant — `INDEX_BILL_PAGES` in the app
repo's `src/site/chrome.ts` — and the renderer's selftest follows it. The remaining step
is the owner's: submit the bill sitemap in Search Console.
