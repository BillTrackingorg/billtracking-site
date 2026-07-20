#!/usr/bin/env python3
"""
generate.py — BillTracking permalink page generator.

Turns the bots' append-only feed archive (feed/YYYY-MM.jsonl) into one static
HTML page per post at /p/<id>.html on billtracking.org, plus a sitemap and a
lightweight /p/ index.

Design (owner-agreed 2026-07-18):
- The permalink id is SELF-OWNED and X-INDEPENDENT:  "<bot>-<YYYYMMDD>-<hash8>",
  derived only from immutable feed fields (bot + posted_at + text). It never
  depends on X's tweet_id, so it survives leaving X, X changing anything, and
  the delete-and-repost correction flow (each feed record keeps its own page).
- tweet_id is used ONLY for the optional "View on X" link-out, never identity.
- Static output: no server, rich share cards (og:), SEO, works with JS off.
- Robust: malformed lines are skipped (logged); ALL dynamic text is escaped.
- Overrides (feed/overrides.jsonl) ride on top: remove-duplicate hides a page,
  correction stamps a public banner, revision-link points to the update.

Usage:
    python generate.py --feed <dir-or-file> [--feed ...] \
                       --overrides <overrides.jsonl> \
                       --out <site-root>
Defaults run the bundled sample feed into ../p so you can preview locally.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger("generate")

SITE_URL = "https://billtracking.org"
HANDLES = {"us": "USBillTracker", "eu": "EUBillTracker"}
TRACKER = {"us": "US tracker", "eu": "EU tracker"}
# Official lookup ROOTS only (roots outlive paths — a reshuffled sub-page must
# never leave a dead link; the reference is the universal lookup key there).
SOURCE = {
    "us": ("Congress.gov", "https://www.congress.gov"),
    "eu": ("OEIL Legislative Observatory", "https://oeil.europarl.europa.eu"),
}


# --------------------------------------------------------------------------- #
#  Identity — self-owned, X-independent, tied to the immutable feed record
# --------------------------------------------------------------------------- #
def post_id(rec: dict) -> str:
    bot = rec.get("bot", "x")
    posted_at = rec.get("posted_at", "")
    date = posted_at[:10].replace("-", "") or "00000000"
    basis = f'{bot}|{posted_at}|{rec.get("text", "")}'
    h = hashlib.sha256(basis.encode("utf-8")).hexdigest()[:8]
    return f"{bot}-{date}-{h}"


# --------------------------------------------------------------------------- #
#  Loading
# --------------------------------------------------------------------------- #
def load_jsonl(path: Path) -> list[dict]:
    out = []
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError as e:
            log.warning("skipping bad line %s:%d — %s", path.name, n, e)
    return out


def gather_feed(paths: list[Path]) -> list[dict]:
    files: list[Path] = []
    for p in paths:
        if p.is_dir():
            files += sorted(f for f in p.glob("*.jsonl") if f.name != "overrides.jsonl")
        elif p.is_file():
            files.append(p)
        else:
            log.warning("feed path not found: %s", p)
    recs: list[dict] = []
    for f in files:
        recs += load_jsonl(f)
    return recs


# --------------------------------------------------------------------------- #
#  Rendering
# --------------------------------------------------------------------------- #
def esc(s: str) -> str:
    return html.escape(str(s), quote=True)


def text_html(text: str) -> str:
    # escape first, THEN restore line breaks — never trust the record's bytes
    return esc(text).replace("\n", "<br>\n")


def describe(rec: dict) -> tuple[str, str]:
    """(title, meta-description) for <title>/og — plain text, escaped later.

    The description feeds <meta name="description">, og:description and the
    Twitter card — i.e. Google snippets and every social preview.

    When it is drawn from `summary` it is AI-GENERATED TEXT, and it MUST carry
    the [AI-Generated] marker. The body of the page gets that label because the
    bot bakes it into the posted text; the summary field does not, so a preview
    built from it would show AI-written prose with nothing saying so — while the
    app and site both promise "AI is labeled".

    That is also the one EU AI Act Article 50(4) obligation within our control:
    a deployer publishing AI-generated text to inform the public on matters of
    public interest must disclose it as such. Applies from 2 August 2026.

    The `text` branch is NOT labelled: it is the bot's own composed post, drawn
    verbatim from the official record with no model involvement.
    """
    ref = rec.get("reference", "")
    label = rec.get("label", "")
    if ref and label:
        title = f"{ref} — {label}"
    elif ref:
        title = ref
    else:
        title = (rec.get("text", "").splitlines() or ["BillTracking post"])[0][:90]

    summary = rec.get("summary")
    if summary:
        # Truncate the summary itself, never the marker — the marker is the
        # part that must survive. 160-180 chars is the practical snippet limit.
        marker = " [AI-Generated]"
        body = " ".join(summary.split())
        if len(body) + len(marker) > 180:
            body = body[: 180 - len(marker) - 1].rstrip() + "…"
        desc = body + marker
    else:
        desc = " ".join(rec.get("text", "").split())[:180]
    return title, desc


NAV = """    <a class="wordmark" href="/index.html">BillTracking<span class="tld">.org</span></a>
    <nav class="site-nav" aria-label="Main">
      <a href="/us-process.html">US Process</a>
      <a href="/eu-process.html">EU Process</a>
      <a href="/educators.html">Educators</a>
      <a href="/accuracy.html">Accuracy</a>
      <a href="/about.html">About</a>
    </nav>"""

PAGE_CSS = """
    .post-wrap { max-width: 44rem; margin: 0 auto; padding: 2.5rem 1.25rem 4rem; }
    .post-kicker { font-family: var(--sans); font-weight: 700; font-size: .72rem;
      letter-spacing: .14em; text-transform: uppercase; color: var(--ink-faint); }
    .post-kicker .tk { color: var(--accent); }
    .post-ref { font-family: var(--serif); font-size: 1.9rem; line-height: 1.2;
      color: var(--navy-ink); margin: .5rem 0 .25rem; }
    .post-date { font-family: var(--sans); color: var(--ink-faint); font-size: .95rem;
      margin-bottom: 1.5rem; }
    .post-card { background: var(--card); border: 1px solid var(--line);
      border-bottom: 3px solid var(--accent); border-radius: var(--radius);
      padding: 1.4rem 1.5rem; font-size: 1.05rem; line-height: 1.75; }
    .post-corrected { background: var(--wash); border: 1px solid var(--line);
      border-left: 3px solid var(--gold); border-radius: 8px; padding: .8rem 1rem;
      margin-bottom: 1rem; font-size: .92rem; color: var(--ink-soft); }
    .post-corrected strong { color: var(--gold-text); }
    .post-actions { display: flex; flex-wrap: wrap; gap: .7rem; margin-top: 1.4rem; }
    .post-btn { display: inline-block; padding: .6rem 1.1rem; border-radius: 8px;
      font-family: var(--sans); font-weight: 600; font-size: .95rem;
      text-decoration: none; border: 1.5px solid var(--navy); color: var(--navy); }
    .post-btn.primary { background: var(--accent); border-color: var(--accent);
      color: #fff; }
    .post-note { margin-top: 2rem; font-size: .85rem; color: var(--ink-faint);
      line-height: 1.6; }
    .post-note a { color: var(--ink-soft); }
"""

PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} | BillTracking</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="article">
<meta property="og:url" content="{url}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="{SITE_URL}/assets/{bot}-banner.webp">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" type="image/png" sizes="32x32" href="/assets/favicon-32.png">
<link rel="stylesheet" href="/style.css">
<style>:root {{ --accent: {accent}; }}{PAGE_CSS}</style>
</head>
<body>
<header class="site-header">
  <div class="wrap">
{NAV}
  </div>
</header>

<main class="post-wrap">
  <p class="post-kicker"><span class="tk">{tracker}</span></p>
  <h1 class="post-ref">{h1}</h1>
  <p class="post-date">Posted {posted_human}</p>
{corrected}
  <article class="post-card">{body}</article>

  <div class="post-actions">
    <a class="post-btn" href="{source_url}">Look it up on {source_name}</a>
    {x_btn}
  </div>

  <p class="post-note">
    This is a permanent record of a post published by
    <a href="https://x.com/{handle}">@{handle}</a>. The facts are drawn from official
    sources; the reference above is the lookup key on {source_name}.
    Spotted an error? <a href="mailto:accuracy@billtracking.org">accuracy@billtracking.org</a>.
  </p>
</main>

<footer class="site-footer">
  <div class="wrap">
    <p>An independent project publishing a live, source-linked record of US and EU
    lawmaking. Not affiliated with, or endorsed by, any government body.</p>
    <p><a href="/index.html">billtracking.org</a></p>
  </div>
</footer>
</body>
</html>
"""


def render(rec: dict, id_: str, superseded_by: str | None) -> str:
    bot = rec.get("bot", "us")
    accent = "#0A3161" if bot == "us" else "#003399"
    title, desc = describe(rec)
    h1 = rec.get("reference") or title
    source_name, source_url = SOURCE.get(bot, SOURCE["us"])
    handle = HANDLES.get(bot, "USBillTracker")

    posted_human = rec.get("posted_at", "")[:10]

    x_btn = ""
    tid = rec.get("tweet_id")
    if tid:
        x_btn = f'<a class="post-btn primary" href="https://x.com/{handle}/status/{esc(tid)}">View on X</a>'

    corrected = ""
    c = rec.get("_correction")
    if c:
        reason = esc(c.get("reason", ""))
        date = esc(c.get("date", ""))
        src = c.get("sourceUrl")
        src_link = f' <a href="{esc(src)}">Source</a>.' if src else ""
        corrected = (f'  <div class="post-corrected"><strong>Corrected {date}.</strong> '
                     f'{reason}{src_link}</div>\n')
    elif superseded_by:
        corrected = (f'  <div class="post-corrected"><strong>Superseded.</strong> '
                     f'A newer post updates this one — '
                     f'<a href="/p/{superseded_by}.html">see the update</a>.</div>\n')

    return PAGE.format(
        title=esc(title), desc=esc(desc), url=f"{SITE_URL}/p/{id_}.html",
        SITE_URL=SITE_URL, bot=bot, accent=accent, PAGE_CSS=PAGE_CSS, NAV=NAV,
        tracker=esc(TRACKER.get(bot, "tracker")), h1=esc(h1),
        posted_human=esc(posted_human), corrected=corrected,
        body=text_html(rec.get("text", "")), source_url=source_url,
        source_name=esc(source_name), x_btn=x_btn, handle=esc(handle),
    )


SITEMAP = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n')


def build(feed_paths, overrides_path, out_root):
    recs = gather_feed(feed_paths)
    overrides = {}
    if overrides_path and overrides_path.is_file():
        for o in load_jsonl(overrides_path):
            if o.get("target"):
                overrides[o["target"]] = o
    log.info("loaded %d feed records, %d overrides", len(recs), len(overrides))

    # index by id + resolve tweet_id -> id (for revision-link) up front
    for r in recs:
        r["_id"] = post_id(r)
    tid_to_id = {r["tweet_id"]: r["_id"] for r in recs if r.get("tweet_id")}

    out_p = out_root / "p"
    out_p.mkdir(parents=True, exist_ok=True)

    pages, written = [], 0
    for r in recs:
        ov = overrides.get(r.get("tweet_id"))
        if ov and ov.get("kind") == "remove-duplicate":
            continue  # technical dup — no page (URL 404s by design)
        superseded = None
        if ov and ov.get("kind") == "correction":
            r["_correction"] = ov
        if ov and ov.get("kind") == "revision-link":
            superseded = tid_to_id.get(ov.get("supersededBy"))
        id_ = r["_id"]
        (out_p / f"{id_}.html").write_text(render(r, id_, superseded), encoding="utf-8")
        title, _ = describe(r)
        pages.append((id_, title, r.get("posted_at", "")[:10], r.get("bot", "us")))
        written += 1

    # sitemap for the permalink pages
    urls = "".join(
        f"  <url><loc>{SITE_URL}/p/{id_}.html</loc><lastmod>{lastmod}</lastmod></url>\n"
        for id_, _t, lastmod, _b in pages)
    (out_p / "sitemap.xml").write_text(SITEMAP.format(urls=urls), encoding="utf-8")

    # lightweight browse index at /p/
    rows = "".join(
        f'<li><a href="/p/{id_}.html">{esc(t)}</a> '
        f'<span class="pi-date">{esc(d)} · {esc(TRACKER.get(b, ""))}</span></li>\n'
        for id_, t, d, b in sorted(pages, key=lambda x: x[2], reverse=True))
    index = INDEX.format(rows=rows, n=written, SITE_URL=SITE_URL, NAV=NAV)
    (out_p / "index.html").write_text(index, encoding="utf-8")

    log.info("wrote %d pages + sitemap + index to %s", written, out_p)


INDEX = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Recent posts | BillTracking</title>
<link rel="icon" type="image/png" sizes="32x32" href="/assets/favicon-32.png">
<link rel="stylesheet" href="/style.css">
<style>
  .pi-wrap {{ max-width: 44rem; margin: 0 auto; padding: 2.5rem 1.25rem 4rem; }}
  .pi-wrap h1 {{ font-family: var(--serif); color: var(--navy-ink); }}
  .pi-wrap ul {{ list-style: none; padding: 0; }}
  .pi-wrap li {{ padding: .8rem 0; border-bottom: 1px solid var(--line-soft); }}
  .pi-date {{ display: block; color: var(--ink-faint); font-size: .85rem; }}
</style>
</head>
<body>
<header class="site-header"><div class="wrap">
{NAV}
</div></header>
<main class="pi-wrap">
  <h1>Recent posts</h1>
  <p>Every post the trackers publish gets a permanent page here. {n} indexed.</p>
  <ul>
{rows}  </ul>
</main>
</body>
</html>
"""


def main():
    here = Path(__file__).resolve().parent
    ap = argparse.ArgumentParser(description="Generate BillTracking permalink pages.")
    ap.add_argument("--feed", action="append", type=Path,
                    help="feed .jsonl file or directory (repeatable)")
    ap.add_argument("--overrides", type=Path, help="feed/overrides.jsonl")
    ap.add_argument("--out", type=Path, help="site root (pages go to <out>/p/)")
    a = ap.parse_args()

    feed = a.feed or [here / "sample-feed.jsonl"]
    overrides = a.overrides or (here / "sample-overrides.jsonl")
    out = a.out or here.parent  # default: the site root (../ from build/)
    build(feed, overrides if Path(overrides).exists() else None, out)


if __name__ == "__main__":
    main()
