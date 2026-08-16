#!/usr/bin/env python3
"""
generate.py — BillTracking permalink page generator.

Turns the bots' append-only feed archive (feed/YYYY-MM.jsonl) into one static
HTML page per post at /p/<id>.html on billtracking.org, plus a sitemap and a
lightweight /p/ index.

Design (owner-agreed 2026-07-18; wired live 2026-08-16):
- The permalink id is SELF-OWNED, X-INDEPENDENT and IDENTICAL to the app's
  postPermalinkId: "<polity>-<YYYYMMDD>-<hash8(internal id)>" — see the identity
  block below; scripts/check-permalinks.js proves the parity against the real
  app code on every `npm run check`. It never depends on X's tweet_id, so it
  survives leaving X, X changing anything, and the delete-and-repost correction
  flow (each feed record keeps its own page).
- tweet_id is used ONLY for the quiet "View on X" link, never identity.
- Static output: no server, no JS, rich share cards (og:), works everywhere —
  the FALLBACK landing for share links the OS can't route to the app (desktop,
  email opens, an unpublished platform), with an honest funnel beneath the post.
- NOINDEX for now (the SEO decision is deferred by design — see Rendering).
- Robust: malformed lines are skipped (logged); ALL dynamic text is escaped.
- Overrides (the bots' PER-BOT us-overrides.jsonl + eu-overrides.jsonl, keyed by
  the app's INTERNAL post id — the root overrides.jsonl is a dead legacy) ride on
  top: remove-duplicate hides a page, correction stamps a public banner (D22
  date, source, link to our correction post), revision-link points to the update.
- Runner: .github/workflows/permalinks.yml in the app repo pulls the PUBLIC feed
  and pushes ONLY p/ into the site repo. The bots are never touched.

Usage:
    python generate.py --feed <dir-or-file> [--feed ...] \
                       --overrides <overrides.jsonl> \
                       --out <site-root>
--out is REQUIRED (pages go to <out>/p/). With no --feed it renders the bundled
SAMPLE fixtures — for a local preview into a THROWAWAY --out only; never point a
sample run at the site repo (fabricated bill pages). The workflow renders the
real feed.
"""
from __future__ import annotations

import argparse
import html
import json
import logging
import re
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
#  Identity — self-owned, X-independent, tied to the immutable feed record.
#
#  ⚠️ MUST EQUAL THE APP'S postPermalinkId, byte for byte. The app's "Copy
#  link" mints  <polity>-<YYYYMMDD>-<hash8(internalId)>  where internalId is
#  feed-adapter.ts deriveId():  <bot>-<ref normalized>-<posted_at digits[:14]>-
#  <hash8(bot|posted_at|text)>  and hash8 is FNV-1a over UTF-16 code units
#  (JS charCodeAt). This is a faithful port; the check script proves parity
#  against fixtures. The earlier sha256 scheme here predated the app's fixed
#  id (2026-07-22) and would have 404'd every link the app produces — found
#  the day the pages were first wired (2026-08-16). Never change one side
#  without the other: a divergence is a silent dead link on every share.
# --------------------------------------------------------------------------- #
def hash8(s: str) -> str:
    """FNV-1a 32-bit over the string's UTF-16 code units, exactly like the
    JS `charCodeAt` loop in posts.ts / feed-adapter.ts (astral chars = two
    surrogate units, so emoji hash identically on both sides)."""
    h = 2166136261
    data = s.encode("utf-16-le")
    for i in range(0, len(data), 2):
        unit = data[i] | (data[i + 1] << 8)
        h ^= unit
        h = (h * 16777619) & 0xFFFFFFFF
    return f"{h:08x}"


def internal_id(rec: dict) -> str:
    """feed-adapter.ts deriveId(), ported."""
    # JS `??` semantics, exactly: only null/undefined fall through — an EMPTY
    # STRING reference is kept (and normalizes to ""), it does NOT fall back to
    # `type`. Python `or` would, and diverge the id (adversarial pass 2026-08-16).
    ref = rec.get("reference")
    if ref is None:
        refs = rec.get("references")
        ref = refs[0] if isinstance(refs, list) and len(refs) > 0 else None
    if ref is None:
        ref = rec.get("type", "")
    ref = re.sub(r"[^a-z0-9]+", "", str(ref).lower())
    posted_at = rec.get("posted_at", "")
    stamp = re.sub(r"[^0-9]", "", posted_at)[:14]
    bot = rec.get("bot", "x")
    text = rec.get("text", "")
    return f"{bot}-{ref}-{stamp}-{hash8(f'{bot}|{posted_at}|{text}')}"


def post_id(rec: dict) -> str:
    """posts.ts postPermalinkId(), ported: polity-YYYYMMDD-hash8(internalId).
    sortKey's date == posted_at's date (toSortKey keeps the ISO date prefix)."""
    bot = rec.get("bot", "x")
    date = rec.get("posted_at", "")[:10].replace("-", "") or "00000000"
    return f"{bot}-{date}-{hash8(internal_id(rec))}"


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
            files += sorted(f for f in p.glob("*.jsonl") if not f.name.endswith("overrides.jsonl"))
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
#
#  ⚠️ NOINDEX ON EVERY PAGE (2026-08-16): these pages exist as share-link
#  landings + OG cards, both of which work unindexed. Making them crawlable
#  is the deferred "SEO Phase 2" decision (a permanent-retention feed =
#  unbounded page accumulation; the owner wants that designed, not defaulted
#  into). Flip when that decision is taken — and drop the noindex on the
#  index page + revisit the sitemap listing in the same commit.
# --------------------------------------------------------------------------- #
def esc(s: str) -> str:
    return html.escape(str(s), quote=True)


def text_html(text: str) -> str:
    # escape first, THEN restore line breaks — never trust the record's bytes
    return esc(text).replace("\n", "<br>\n")


_MONTHS = (
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
)


def human_date(posted_at: str) -> str:
    """ISO `2026-07-13T…` -> `13 July 2026` — the app's D22 display format (day
    without a leading zero, spelled-out month), so the site, the app and the
    posts all read the same date. Falls back to the raw `YYYY-MM-DD` prefix on
    anything that is not a REAL date — bad shape, out-of-range month OR day —
    and never guesses a wrong one (mirrors lib/format-date.ts's leap-aware
    refusal; posted_at is always a valid bot timestamp, so this is a belt)."""
    iso = (posted_at or "")[:10]
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})$", iso)
    if not m:
        return iso
    y, month, day = int(m.group(1)), int(m.group(2)), int(m.group(3))
    try:
        datetime(y, month, day)      # rejects 00/13 months AND impossible days (leap-aware)
    except ValueError:
        return iso
    return f"{day} {_MONTHS[month - 1]} {y}"


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

    # A corrected post keeps its ORIGINAL label in the title — the generator
    # never rewrites the archived record — so the <title>, og:title and
    # description (the share card and Google snippet, seen BEFORE the in-page
    # "Corrected" banner) would otherwise present the SUPERSEDED figure as fact.
    # Flag it in the title, and lead the description with the correction itself
    # (its reason usually carries the corrected figure, which is human-written —
    # no AI marker needed), so the preview can never show the old number uncued.
    # `_correction` is set on the record in build() before render()/describe().
    correction = rec.get("_correction")
    revision = rec.get("_revision")
    if correction:
        title = f"[Corrected] {title}"
        reason = " ".join(str(correction.get("reason", "")).split())
        if reason:
            date = human_date(str(correction.get("date", "")).strip())
            desc = f"Corrected {date}: {reason}".strip()
            # The corrected VALUE when the sheet carries one — a card that says
            # only "corrected" leaves the reader with the old number in the
            # body; say what it now reads (app's "Now reads:" / PATCHABLE).
            patch = correction.get("patch") or {}
            now = " ".join(str(patch.get(k, "")) for k in ("label", "tally") if patch.get(k)).strip()
            if now:
                desc += f" Now reads: {now}."
            desc = desc[:180]
    elif revision:
        # D19 automatic revision (the record was amended): same posture.
        title = f"[Corrected] {title}"
        d = human_date(revision.get("date", ""))
        fig = revision.get("figure", "")
        desc = (f"Corrected {d}: the official record was later amended."
                + (f" Now reads: {fig}." if fig else ""))[:180]
    return title, desc


NAV = """    <a class="wordmark" href="/index.html">BillTracking<span class="tld">.org</span></a>
    <nav class="site-nav" aria-label="Main">
      <a href="/index.html">Home</a>
      <a href="/us">US Process</a>
      <a href="/eu">EU Process</a>
      <a href="/educators.html">Educators</a>
      <a href="/accuracy.html">Accuracy</a>
      <a href="/about.html">About</a>
    </nav>"""

# --------------------------------------------------------------------------- #
#  The funnel block under every post (owner design 2026-08-16): a share link
#  is meant to open the APP when installed and the STORE when not — this page
#  is the fallback for everyone the OS can't route (desktop browsers, email
#  opens, a platform not yet published). So the post sits at the top as proof,
#  and directly beneath it the honest call to action.
#
#  ⚠️ NO FABRICATED AFFORDANCES (accuracy law): store buttons render ONLY when
#  a real listing URL is set below. Until then the block tells the truth — the
#  app is coming, the full feed is on the site meanwhile. Fill STORE_URLS at
#  launch (STORE-READINESS launch-day checklist) and the buttons switch on.
# --------------------------------------------------------------------------- #
STORE_URLS = {
    # "android": "https://play.google.com/store/apps/details?id=org.billtracking.application",
    # "ios": "https://apps.apple.com/app/id<APP_ID>",
}


def funnel_html(bot: str) -> str:
    feed = "/us" if bot == "us" else "/eu"
    buttons = []
    if STORE_URLS.get("android"):
        buttons.append(f'<a class="btn btn-gold" href="{esc(STORE_URLS["android"])}">Get it on Google Play</a>')
    if STORE_URLS.get("ios"):
        buttons.append(f'<a class="btn btn-gold" href="{esc(STORE_URLS["ios"])}">Download on the App Store</a>')
    # Claim-checked (polity-feed-page.tsx HOW law): no "every step" / "complete
    # history" — the feed posts the steps that matter plus the routine ones,
    # from the official record; introductions are deliberately not posted.
    if buttons:
        lead = ("This post is from the BillTracking app — legislation as it moves, drawn "
                "from the official record, with the bills you follow one tap away.")
        btns = "\n      ".join(buttons)
    else:
        lead = ("This post is from BillTracking — legislation as it moves, drawn from the "
                "official record. The app is coming to Android and iOS; the full live feed "
                "is on this site meanwhile.")
        btns = ""
    return f"""  <section class="post-funnel" aria-label="About BillTracking">
    <p class="post-funnel-lead">{lead}</p>
    <div class="post-actions">
      {btns}
      <a class="btn btn-navy" href="{feed}">Open the live feed</a>
    </div>
  </section>
"""

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
    .post-actions { display: flex; flex-wrap: wrap; gap: .7rem; margin-top: 1rem; }
    .post-funnel { margin-top: 1.6rem; padding: 1.2rem 1.4rem; background: var(--wash);
      border: 1px solid var(--line); border-radius: var(--radius); }
    .post-funnel-lead { margin: 0; font-size: .98rem; line-height: 1.6; color: var(--ink); }
    .post-links { display: flex; flex-wrap: wrap; gap: 1.2rem; margin-top: 1.4rem;
      font-family: var(--sans); font-size: .9rem; }
    .post-links a { color: var(--ink-soft); }
    .post-note { margin-top: 1.6rem; font-size: .85rem; color: var(--ink-faint);
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
<meta name="robots" content="noindex">
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
  <p class="post-date">{dateline}</p>
{corrected}
  <article class="post-card">{body}</article>

{funnel}
  <p class="post-links">
    <a href="{source_url}">Look it up on {source_name}</a>
    {x_link}
  </p>

  <p class="post-note">
    A permanent record of a post published by BillTracking's {tracker}. The facts are
    drawn from the official record; the reference above is the lookup key on
    {source_name}. Spotted an error?
    <a href="mailto:accuracy@billtracking.org">accuracy@billtracking.org</a>.
  </p>
</main>

<footer class="site-footer">
  <div class="wrap">
    <div class="footer-grid">
      <div>
        <a class="wordmark" href="/index.html">BillTracking<span class="tld">.org</span></a>
        <p>An independent project publishing a live, source-linked record of US and EU
        lawmaking. No sponsors, no advertisers, no paid placements. Not affiliated with,
        or endorsed by, the United States Congress, the European Union, or any government
        body.</p>
      </div>
      <div>
        <h5>Pages</h5>
        <ul>
          <li><a href="/us">The US feed</a></li>
          <li><a href="/eu">The EU feed</a></li>
          <li><a href="/us-process.html">The US process</a></li>
          <li><a href="/eu-process.html">The EU process</a></li>
          <li><a href="/accuracy.html">Accuracy</a></li>
          <li><a href="/about.html">About</a></li>
        </ul>
      </div>
      <div>
        <h5>Legal</h5>
        <ul>
          <li><a href="/privacy.html">Privacy</a></li>
          <li><a href="/terms.html">Terms</a></li>
        </ul>
      </div>
    </div>
  </div>
</footer>
</body>
</html>
"""


def render(rec: dict, id_: str, superseded_by: str | None) -> str:
    bot = rec.get("bot", "us")
    accent = "#0A3161" if bot == "us" else "#003399"
    title, desc = describe(rec)
    # H1: a bill post is headed by its reference (the lookup key); a franchise
    # post (agenda, roundup, markup event) has no reference and its headline
    # already opens the card, so heading it with the same line printed it twice
    # (seen on the first live render, 2026-08-16) — use a plain type heading.
    FRANCHISE_H1 = {
        "today": "Today in Congress" if bot == "us" else "Today in the EU",
        "week": "The week ahead",
        "calendar_batch": "Added to the congressional calendars",
        "event": "Committee markup",
        "digest": "EU digest",
        "preview": "The week ahead in the EU",
        "correction": "Correction",
    }
    h1 = rec.get("reference") or FRANCHISE_H1.get(rec.get("type", ""), title)
    source_name, source_url = SOURCE.get(bot, SOURCE["us"])
    handle = HANDLES.get(bot, "USBillTracker")

    # Dateline: the EVENT date when the record carries one (D22 display form —
    # the app shows exactly this), plus when we posted it. Both are facts from
    # the record; the event date is the one that matters to a reader.
    posted_human = human_date(rec.get("posted_at", ""))
    event_iso = rec.get("event_date") or ""
    # Archived pre-D22 records carry "DD-MM-YYYY" — reorder to ISO for display
    # (the app's feed-adapter does the same; format-date refuses non-ISO).
    event_iso = re.sub(r"^(\d{2})-(\d{2})-(\d{4})$", r"\3-\2-\1", event_iso)
    event_human = human_date(event_iso) if event_iso else ""
    if event_human and event_human != posted_human:
        dateline = f"{event_human} · posted {posted_human}"
    else:
        dateline = f"Posted {posted_human}"

    # X is the tertiary surface: a quiet link, not the primary button.
    x_link = ""
    tid = str(rec.get("tweet_id") or "")
    if re.fullmatch(r"\d{1,25}", tid):   # a tweet id is digits only — anything else, no link
        x_link = f'<a href="https://x.com/{handle}/status/{tid}">View on X</a>'

    corrected = ""
    c = rec.get("_correction")
    if c:
        reason = esc(c.get("reason", ""))
        # overrides.ts: `date` is ISO YYYY-MM-DD → render in the D22 display
        # form like every other date on the page (never the raw ISO — it would
        # be the one date on screen disagreeing with all the others).
        date = esc(human_date(c.get("date", "")))
        src = c.get("sourceUrl")
        # href hardening: only http(s) URLs become links (a javascript: or
        # data: value from a compromised sheet renders as no link at all).
        src_link = (f' <a href="{esc(src)}">Source</a>.'
                    if src and re.match(r"^https?://", str(src)) else "")
        # Our own public correction post, when it exists — the same two-way
        # link the app's Inaccurate flag makes (correctionPostId = internal id).
        cp = rec.get("_correction_page")
        cp_link = f' <a href="/p/{esc(cp)}">Read the correction</a>.' if cp else ""
        # The corrected VALUE when the sheet carries a patch — the archive text
        # above still shows the old number (D17, never rewritten), so the banner
        # says what it now reads (mirrors the app's "Now reads:" clause).
        patch = c.get("patch") or {}
        now = esc(" ".join(str(patch.get(k, "")) for k in ("label", "tally") if patch.get(k)).strip())
        now_txt = f" Now reads: {now}." if now else ""
        corrected = (f'  <div class="post-corrected"><strong>Corrected {date}.</strong> '
                     f'{reason}{now_txt}{src_link}{cp_link}</div>\n')
    elif rec.get("_revision"):
        # D19: the bots' automatic correction — same words as the app card
        # (RECORD_REVISION_REASON), the HEAD's date and figure, a link to it.
        rv = rec["_revision"]
        d = esc(human_date(rv.get("date", "")))
        fig = esc(rv.get("figure", ""))
        now_txt = f" Now reads: {fig}." if fig else ""
        corrected = (f'  <div class="post-corrected"><strong>Corrected {d}.</strong> '
                     f'The official record was later amended.{now_txt} '
                     f'<a href="/p/{esc(rv["page"])}">Read the correction</a>.</div>\n')
    elif superseded_by:
        corrected = (f'  <div class="post-corrected"><strong>Superseded.</strong> '
                     f'A newer post updates this one — '
                     f'<a href="/p/{superseded_by}">see the update</a>.</div>\n')

    return PAGE.format(
        title=esc(title), desc=esc(desc), url=f"{SITE_URL}/p/{id_}",
        SITE_URL=SITE_URL, bot=bot, accent=accent, PAGE_CSS=PAGE_CSS, NAV=NAV,
        tracker=esc(TRACKER.get(bot, "tracker")), h1=esc(h1),
        dateline=esc(dateline), corrected=corrected,
        body=text_html(rec.get("text", "")), funnel=funnel_html(bot),
        source_url=source_url, source_name=esc(source_name), x_link=x_link,
    )


SITEMAP = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n')


_ID_SHAPE = re.compile(r"^(us|eu)-\d{8}-[0-9a-f]{8}$")


def build(feed_paths, overrides_paths, out_root):
    recs = gather_feed(feed_paths)
    # The id becomes a FILENAME under p/ — every component comes from the
    # record (bot, posted_at). Only records producing a well-formed id are
    # rendered; anything else is skipped LOUDLY. Fail-closed by shape: a
    # crafted or corrupt record can never write outside p/ or overwrite the
    # index/sitemap, and the app would refuse the same record anyway (its
    # adapter drops unknown bots / unparseable dates).
    kept = []
    for r in recs:
        if _ID_SHAPE.match(post_id(r)):
            kept.append(r)
        else:
            log.warning("skipping record with malformed id (bot=%r posted_at=%r)",
                        r.get("bot"), r.get("posted_at"))
    recs = kept
    # Duplicate lines (a re-published month file can repeat a record) collapse
    # to one page — same id, same bytes; without this the index/sitemap listed
    # them twice.
    seen: set[str] = set()
    recs = [r for r in recs if not (post_id(r) in seen or seen.add(post_id(r)))]
    overrides = {}
    for op in overrides_paths or []:
        for o in load_jsonl(op):
            if o.get("target"):
                overrides[o["target"]] = o
    log.info("loaded %d feed records, %d overrides", len(recs), len(overrides))

    # Overrides target the app's INTERNAL post id (overrides.ts `target`), the
    # same id the app keys corrections by — one identity, both renderers.
    # (The sample-era version keyed by tweet_id; the real sheet never did.)
    for r in recs:
        r["_iid"] = internal_id(r)
        r["_id"] = post_id(r)
    iid_to_id = {r["_iid"]: r["_id"] for r in recs}

    # D19 RECORD REVISIONS — the bots' automatic corrections (a tally the
    # official record later amended). Faithful port of posts.ts
    # linkRecordRevisions: the target is found by tweet_id FIRST, then by the
    # natural-key hash (the fallback for an X success whose shape hid the tweet
    # id); a revision never crosses polities; the LATEST revision of a target
    # wins; and the stamp follows the chain to its HEAD (A←B←C stamps A with
    # C's figure — reporting the middle figure would assert a stale number as
    # current truth). Renders as the same "Corrected <head date>" banner the
    # app card shows, with the head's figure and a link to the head page.
    by_tid = {str(r["tweet_id"]): r for r in recs if r.get("tweet_id")}
    by_key = {hash8(f'{r.get("bot", "")}|{r.get("posted_at", "")}|{r.get("text", "")}'): r for r in recs}
    stamp_for: dict[str, dict] = {}   # target internal id → revision record
    for r in recs:
        tid, key = r.get("supersedes_tweet_id"), r.get("supersedes_post_key")
        target = (by_tid.get(str(tid)) if tid else None) or (by_key.get(hash8(key)) if key else None)
        if not target or target is r or target.get("bot") != r.get("bot"):
            continue
        prev = stamp_for.get(target["_iid"])
        if not prev or prev.get("posted_at", "") < r.get("posted_at", ""):
            stamp_for[target["_iid"]] = r
    for r in recs:
        stamp = stamp_for.get(r["_iid"])
        if not stamp:
            continue
        head, seen = stamp, {r["_iid"], stamp["_iid"]}
        nxt = stamp_for.get(head["_iid"])
        while nxt and nxt["_iid"] not in seen:
            head = nxt; seen.add(head["_iid"]); nxt = stamp_for.get(head["_iid"])
        figure = f'{head.get("label") or ""} {head.get("tally") or ""}'.strip()
        r["_revision"] = {"date": head.get("posted_at", "")[:10], "figure": figure, "page": head["_id"]}

    out_p = out_root / "p"
    out_p.mkdir(parents=True, exist_ok=True)

    pages, written = [], 0
    for r in recs:
        ov = overrides.get(r["_iid"])
        if ov and ov.get("kind") == "remove-duplicate":
            continue  # technical dup — no page (URL 404s by design)
        superseded = None
        if ov and ov.get("kind") == "correction":
            r["_correction"] = ov
            cp = ov.get("correctionPostId")
            if cp:
                r["_correction_page"] = iid_to_id.get(cp)
        if ov and ov.get("kind") == "revision-link":
            superseded = iid_to_id.get(ov.get("supersededBy"))
        id_ = r["_id"]
        (out_p / f"{id_}.html").write_text(render(r, id_, superseded), encoding="utf-8")
        title, _ = describe(r)
        pages.append((id_, title, r.get("posted_at", "")[:10], r.get("bot", "us")))
        written += 1

    # sitemap for the permalink pages
    urls = "".join(
        f"  <url><loc>{SITE_URL}/p/{id_}</loc><lastmod>{lastmod}</lastmod></url>\n"
        for id_, _t, lastmod, _b in pages)
    (out_p / "sitemap.xml").write_text(SITEMAP.format(urls=urls), encoding="utf-8")

    # lightweight browse index at /p/
    rows = "".join(
        f'<li><a href="/p/{id_}">{esc(t)}</a> '
        f'<span class="pi-date">{esc(human_date(d))} · {esc(TRACKER.get(b, ""))}</span></li>\n'
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
<meta name="robots" content="noindex">
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
    ap.add_argument("--overrides", action="append", type=Path,
                    help="an overrides .jsonl (repeatable: the bots write ONE PER BOT — "
                         "us-overrides.jsonl + eu-overrides.jsonl — and the app reads both; "
                         "a directory passed to --feed is also scanned for *-overrides.jsonl)")
    ap.add_argument("--out", type=Path, required=True,
                    help="output root (pages go to <out>/p/). REQUIRED — a bare run "
                         "used to default to the sibling PUBLIC site repo and rendered the "
                         "SAMPLE fixtures into the deploy tree (adversarial review 2026-08-16); "
                         "the sample-fed local preview must be pointed at a throwaway dir.")
    a = ap.parse_args()

    feed = a.feed or [here / "sample-feed.jsonl"]
    overrides = list(a.overrides or [])
    if not a.overrides:
        # feed dirs: pick up the per-bot sheets the bots publish; the sample
        # run: its own fixture.
        for p in feed:
            if p.is_dir():
                overrides += sorted(p.glob("*-overrides.jsonl"))
        if not a.feed:
            overrides = [here / "sample-overrides.jsonl"]
    build(feed, [o for o in overrides if o.is_file()], a.out)


if __name__ == "__main__":
    main()
