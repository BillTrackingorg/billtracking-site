#!/usr/bin/env python3
"""
generate.py — BillTracking permalink + bill page generator.

Turns the bots' append-only feed archive (feed/YYYY-MM.jsonl) + the per-bill path
artifacts (paths/*.json) into static HTML on billtracking.org:
  • /p/<id>.html   — one page per POST (the share-link fallback + OG card), a
                     sitemap, and a lightweight /p/ index. NOINDEX (citations).
  • /b/<polity>/<slug>.html — one page per BILL (the INDEXABLE unit; SEO plan),
                     mirroring the app's own bill screen (identity + dated latest
                     status + the full merged post/record path), with JSON-LD, a
                     per-polity index, and bill-sitemap.xml. A bill-bearing post's
                     /p/ canonical points here. Bill pages carry NOINDEX until the
                     owner's Gate-2 flip (INDEX_BILL_PAGES). See docs/WEB.md §SEO.

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
- /p/ pages are NOINDEX forever (citations). Bill pages are the SEO surface and
  carry NOINDEX only until the owner's Gate-2 flip (INDEX_BILL_PAGES) — the SEO
  model is BUILT & STAGED, not "deferred" (docs/WEB.md §SEO).
- Robust: malformed lines are skipped (logged); ALL dynamic text is escaped.
- Overrides (the bots' PER-BOT us-overrides.jsonl + eu-overrides.jsonl, keyed by
  the app's INTERNAL post id — the root overrides.jsonl is a dead legacy) ride on
  top: remove-duplicate hides a page, correction stamps a public banner (D22
  date, source, link to our correction post), revision-link points to the update.
- Runner: .github/workflows/permalinks.yml IN THIS (SITE) repo (moved out of the
  app repo 2026-08-16, built-in token, no credentials) pulls the PUBLIC feed +
  path artifacts and commits ONLY p/ + b/ + bill-sitemap.xml. The bots are never
  touched.

Usage:
    python generate.py --feed <dir-or-file> [--feed ...] \
                       --overrides <overrides.jsonl> --paths <paths-dir> \
                       --out <site-root> [--glyphs emoji|svg]
--out is REQUIRED (pages go to <out>/p/ and <out>/b/). --list-paths prints the
path-artifact filenames the feed needs, then exits. With no --feed it renders the
bundled SAMPLE fixtures — for a local preview into a THROWAWAY --out only; never
point a sample run at the site repo (fabricated bill pages). The workflow renders
the real feed.
"""
from __future__ import annotations

import argparse
import html
import json
import logging
import re
from bisect import bisect_right
from datetime import datetime, timezone
from functools import cmp_to_key
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


# =========================================================================== #
#  BILL-PAGE PARITY CORE — a faithful port of the app's adapter + path merge.
#
#  ⚠️ EVERYTHING BELOW MIRRORS REAL APP CODE, LINE FOR LINE. A bill page shows
#  "the same record the app's bill screen shows" (SEO plan §1, D24 one-renderer
#  law), so the join that builds it must be the app's join, not a second
#  interpretation. The parity is PROVEN, not asserted: scripts/check-permalinks.js
#  runs the app's REAL timelineFor/mergeRecord/billInfo against these functions
#  over the same fixtures and requires identical row sets. When the app's code
#  changes, that check fails until these match — the failure is the point.
#
#  Sources (app repo, sibling checkout Projects/BillTracking/app):
#    src/lib/format-date.ts        formatDisplayDate  → format_display_date
#    src/data/feed-adapter.ts      adaptOne/deriveId  → adapt_post
#    src/data/feed-schema.ts       D9 maps            → FAMILY_BUCKET/POST_TYPE_MAP
#    src/data/path-client.ts       parse*/fetchBillPath → parse_*_ref/load_path_artifact
#    src/data/posts.ts             mergeRecord/billInfo → merge_record/bill_info
# =========================================================================== #

_MONTHS_FULL = (
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
)
_DAYS_IN_MONTH = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)


def format_display_date(iso: str) -> str | None:
    """lib/format-date.ts formatDisplayDate(): clean ISO `YYYY-MM-DD` → `20 July
    2026`, else None. Leap-aware; refuses an impossible day rather than print a
    plausible-looking wrong date. This is a JOIN KEY (mergeRecord matches on
    `${eventDate}|${label}`), so it must be byte-identical to the app's."""
    # ASCII digits ([0-9], not \d) throughout the ported regexes: JS `\d` is
    # ASCII-only, Python `\d` is every Unicode decimal digit — a fullwidth/Arabic
    # digit would parse here but not in the app, diverging the port (guard finding,
    # 2026-08-17). `\s` stays Unicode (JS `\s` matches Unicode whitespace too).
    m = re.match(r"^([0-9]{4})-([0-9]{2})-([0-9]{2})$", iso or "")
    if not m:
        return None
    year, month_num, day = int(m.group(1)), int(m.group(2)), int(m.group(3))
    if month_num < 1 or month_num > 12:
        return None
    leap = (year % 4 == 0 and year % 100 != 0) or year % 400 == 0
    max_day = 29 if (month_num == 2 and leap) else _DAYS_IN_MONTH[month_num - 1]
    if day < 1 or day > max_day:
        return None
    return f"{day} {_MONTHS_FULL[month_num - 1]} {year}"


def to_sort_key(posted_at: str) -> str | None:
    """feed-adapter.ts toSortKey(): `2026-07-17T18:22:00+00:00` → `2026-07-17T18:22`."""
    m = re.match(r"^([0-9]{4}-[0-9]{2}-[0-9]{2})T([0-9]{2}:[0-9]{2})", posted_at or "")
    return f"{m.group(1)}T{m.group(2)}" if m else None


US_BILL_TYPES = frozenset((
    "hr", "s", "hres", "sres", "hjres", "sjres", "hconres", "sconres",
))


def parse_us_ref(reference: str) -> dict | None:
    """path-client.ts parseUsRef(): "H.R. 3497" → {type:'hr', num:'3497'};
    None for anything that is not a US bill reference."""
    compact = re.sub(r"[.\s]", "", reference or "").lower()
    m = re.match(r"^([a-z]+)([0-9]+)$", compact)
    if not m or m.group(1) not in US_BILL_TYPES:
        return None
    return {"type": m.group(1), "num": m.group(2)}


def parse_eu_ref(reference: str) -> dict | None:
    """path-client.ts parseEuRef(): "2025/0407(COD)" → {year,num,type}; None else.
    EXACTLY the bot's parse_eu_reference grammar (4/4-digit, 2–4 letter type)."""
    m = re.match(r"^([0-9]{4})/([0-9]{4})\(([A-Z]{2,4})\)$", (reference or "").strip())
    return {"year": m.group(1), "num": m.group(2), "type": m.group(3).lower()} if m else None


# The Congress every un-stamped legacy US record belongs to — a FIXED constant,
# never the calendar year (path-client.ts LEGACY_CONGRESS; the feed is permanent
# so a 119th post opened in 2027 must still resolve the 119th, never derive the
# 120th's same-numbered artifact, which is ANOTHER BILL).
LEGACY_CONGRESS = 119
# The path-artifact schema this build understands (path-client.ts
# PATH_SCHEMA_SUPPORTED). A higher/absent `v` means the bot knows a field or rule
# this port does not → fail closed (render posts-only, never a guessed row).
PATH_SCHEMA_SUPPORTED = 1
# The FEED-record schema this build understands (feed-adapter.ts SCHEMA_SUPPORTED).
# A record with any other `v` is DROPPED, exactly as the app drops it.
SCHEMA_SUPPORTED = 1

# --------------------------------------------------------------------------- #
#  D9 — family → notification bucket (feed-schema.ts). The adapter DROPS a status
#  record whose family is unmapped (guessing a bucket is the one thing D9 forbids),
#  so the bill page's post set must drop the same records or it would render a row
#  the app never shows. Copied verbatim; a divergence is caught by the parity
#  check the first time a real family is missing here. Keep in lockstep with
#  feed-schema.ts FAMILY_BUCKET / POST_TYPE_MAP.
# --------------------------------------------------------------------------- #
FAMILY_BUCKET = {
    # US
    "signed": "milestones", "became_law": "milestones", "became_private_law": "milestones",
    "vetoed": "milestones", "pocket_vetoed": "milestones", "override_passed": "milestones",
    "override_failed": "milestones", "passed_house": "milestones", "passed_senate": "milestones",
    "passed_house_amended": "milestones", "passed_senate_amended": "milestones",
    "failed_passage": "milestones", "res_adopted": "milestones", "res_failed": "milestones",
    "concur_clean": "milestones", "concur_amended": "milestones",
    "conference_report_agreed": "milestones", "presented": "milestones", "tabled": "milestones",
    "postponed": "milestones",
    "cloture_invoked": "procedural", "cloture_invoked_mtp": "procedural",
    "cloture_failed": "procedural", "cloture_filed": "procedural",
    "cloture_invoked_amendment": "procedural", "cloture_failed_amendment": "procedural",
    "cloture_filed_amendment": "procedural", "mtp_rejected": "procedural",
    "motion_to_proceed": "procedural", "mtp_pending": "procedural", "reported": "procedural",
    "reported_adverse": "procedural", "discharged": "procedural", "recommitted": "procedural",
    "conference_requested": "procedural",
    "calendar_placement": "roundups",
    # EU
    "ep_r2_approved": "milestones", "council_adoption": "milestones", "oj_published": "milestones",
    "withdrawn": "milestones", "rejected": "milestones", "ep_plenary_vote_r1": "milestones",
    "ep_plenary_vote_r2": "milestones", "ep_rejects_proposal": "milestones",
    "ep_consent": "milestones", "ep_consent_refused": "milestones",
    "provisional_agreement": "milestones", "joint_text": "milestones",
    "third_reading_decision": "milestones", "proposed": "milestones",
    "committee_confirms_deal": "milestones", "deal_rejected_committee": "milestones",
    "committee_vote": "procedural", "committee_recommendation_r2": "procedural",
    "mandate": "procedural", "council_general_approach": "procedural",
    "council_general_approach_partial": "procedural", "ep_opinion_cns": "procedural",
    "referred_back": "procedural", "council_position_r1": "procedural",
    "council_political_agreement": "procedural", "conciliation_convened": "procedural",
    "ep_resolution": "procedural",
}
POLITY_BUCKET: dict = {}  # feed-schema.ts POLITY_BUCKET — empty today, checked first.
# post_type → app postType + fixed bucket where the type alone determines it.
POST_TYPE_MAP = {
    "action": {"postType": "status"},
    "today": {"postType": "agenda", "bucket": "agenda"},
    "week": {"postType": "roundup", "bucket": "roundups"},
    "calendar_batch": {"postType": "roundup", "bucket": "roundups"},
    "event": {"postType": "roundup", "bucket": "roundups"},
    "digest": {"postType": "roundup", "bucket": "roundups"},
    "preview": {"postType": "roundup", "bucket": "roundups"},
    "correction": {"postType": "roundup", "bucket": "milestones"},
}


def bucket_for(polity: str, family: str) -> str | None:
    return POLITY_BUCKET.get(polity, {}).get(family) or FAMILY_BUCKET.get(family)


# feed-adapter.ts LEADING_EMOJI is `[\p{Extended_Pictographic}️‍\s]+`.
# Python's stdlib `re` has no \p{}, and a hand-rolled range approximation was BOTH
# a superset AND a subset of the real property (guard finding, 2026-08-17: it
# stripped ★/♫/chess/keycap-base which are NOT Extended_Pictographic, so it could
# DROP a franchise post the app keeps → a minted /p/ link that 404s). So embed the
# EXACT Extended_Pictographic set, generated from the SAME engine the app runs
# (`/\p{Extended_Pictographic}/u`, i.e. V8) — 156 ranges, BMP + astral. Note it
# EXCLUDES regional-indicator flags (0x1F1E6-0x1F1FF), which the app keeps.
# scripts/check-permalinks.js re-derives this from Node's regex and requires exact
# equality with _is_leading_emoji, so any Unicode drift fails the check.
_EXT_PICT = (
    (0xa9,0xa9), (0xae,0xae), (0x203c,0x203c), (0x2049,0x2049), (0x2122,0x2122), (0x2139,0x2139),
    (0x2194,0x2199), (0x21a9,0x21aa), (0x231a,0x231b), (0x2328,0x2328), (0x23cf,0x23cf), (0x23e9,0x23f3),
    (0x23f8,0x23fa), (0x24c2,0x24c2), (0x25aa,0x25ab), (0x25b6,0x25b6), (0x25c0,0x25c0), (0x25fb,0x25fe),
    (0x2600,0x2604), (0x260e,0x260e), (0x2611,0x2611), (0x2614,0x2615), (0x2618,0x2618), (0x261d,0x261d),
    (0x2620,0x2620), (0x2622,0x2623), (0x2626,0x2626), (0x262a,0x262a), (0x262e,0x262f), (0x2638,0x263a),
    (0x2640,0x2640), (0x2642,0x2642), (0x2648,0x2653), (0x265f,0x2660), (0x2663,0x2663), (0x2665,0x2666),
    (0x2668,0x2668), (0x267b,0x267b), (0x267e,0x267f), (0x2692,0x2697), (0x2699,0x2699), (0x269b,0x269c),
    (0x26a0,0x26a1), (0x26a7,0x26a7), (0x26aa,0x26ab), (0x26b0,0x26b1), (0x26bd,0x26be), (0x26c4,0x26c5),
    (0x26c8,0x26c8), (0x26ce,0x26cf), (0x26d1,0x26d1), (0x26d3,0x26d4), (0x26e9,0x26ea), (0x26f0,0x26f5),
    (0x26f7,0x26fa), (0x26fd,0x26fd), (0x2702,0x2702), (0x2705,0x2705), (0x2708,0x270d), (0x270f,0x270f),
    (0x2712,0x2712), (0x2714,0x2714), (0x2716,0x2716), (0x271d,0x271d), (0x2721,0x2721), (0x2728,0x2728),
    (0x2733,0x2734), (0x2744,0x2744), (0x2747,0x2747), (0x274c,0x274c), (0x274e,0x274e), (0x2753,0x2755),
    (0x2757,0x2757), (0x2763,0x2764), (0x2795,0x2797), (0x27a1,0x27a1), (0x27b0,0x27b0), (0x27bf,0x27bf),
    (0x2934,0x2935), (0x2b05,0x2b07), (0x2b1b,0x2b1c), (0x2b50,0x2b50), (0x2b55,0x2b55), (0x3030,0x3030),
    (0x303d,0x303d), (0x3297,0x3297), (0x3299,0x3299), (0x1f004,0x1f004), (0x1f02c,0x1f02f), (0x1f094,0x1f09f),
    (0x1f0af,0x1f0b0), (0x1f0c0,0x1f0c0), (0x1f0cf,0x1f0d0), (0x1f0f6,0x1f0ff), (0x1f170,0x1f171), (0x1f17e,0x1f17f),
    (0x1f18e,0x1f18e), (0x1f191,0x1f19a), (0x1f1ae,0x1f1e5), (0x1f201,0x1f20f), (0x1f21a,0x1f21a), (0x1f22f,0x1f22f),
    (0x1f232,0x1f23a), (0x1f23c,0x1f23f), (0x1f249,0x1f25f), (0x1f266,0x1f321), (0x1f324,0x1f393), (0x1f396,0x1f397),
    (0x1f399,0x1f39b), (0x1f39e,0x1f3f0), (0x1f3f3,0x1f3f5), (0x1f3f7,0x1f3fa), (0x1f400,0x1f4fd), (0x1f4ff,0x1f53d),
    (0x1f549,0x1f54e), (0x1f550,0x1f567), (0x1f56f,0x1f570), (0x1f573,0x1f57a), (0x1f587,0x1f587), (0x1f58a,0x1f58d),
    (0x1f590,0x1f590), (0x1f595,0x1f596), (0x1f5a4,0x1f5a5), (0x1f5a8,0x1f5a8), (0x1f5b1,0x1f5b2), (0x1f5bc,0x1f5bc),
    (0x1f5c2,0x1f5c4), (0x1f5d1,0x1f5d3), (0x1f5dc,0x1f5de), (0x1f5e1,0x1f5e1), (0x1f5e3,0x1f5e3), (0x1f5e8,0x1f5e8),
    (0x1f5ef,0x1f5ef), (0x1f5f3,0x1f5f3), (0x1f5fa,0x1f64f), (0x1f680,0x1f6c5), (0x1f6cb,0x1f6d2), (0x1f6d5,0x1f6e5),
    (0x1f6e9,0x1f6e9), (0x1f6eb,0x1f6f0), (0x1f6f3,0x1f6ff), (0x1f7da,0x1f7ff), (0x1f80c,0x1f80f), (0x1f848,0x1f84f),
    (0x1f85a,0x1f85f), (0x1f888,0x1f88f), (0x1f8ae,0x1f8af), (0x1f8bc,0x1f8bf), (0x1f8c2,0x1f8cf), (0x1f8d9,0x1f8ff),
    (0x1f90c,0x1f93a), (0x1f93c,0x1f945), (0x1f947,0x1f9ff), (0x1fa58,0x1fa5f), (0x1fa6e,0x1faff), (0x1fc00,0x1fffd),
)
_EXT_PICT_LO = tuple(lo for lo, _hi in _EXT_PICT)
# The EXACT JS `\s` set (ECMAScript WhiteSpace + LineTerminator), which is what
# LEADING_EMOJI's `\s` matches — NOT Python's str.isspace(), which differs at
# \x1c-\x1f, \x85 (Python-only) and ﻿ (JS-only). Byte-parity with the app.
_JS_WS = frozenset(
    chr(c) for c in (
        0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x20, 0xa0, 0x1680,
        0x2028, 0x2029, 0x202f, 0x205f, 0x3000, 0xfeff,
        *range(0x2000, 0x200b),
    )
)


def _is_leading_emoji(c: str) -> bool:
    """One char of feed-adapter.ts LEADING_EMOJI: JS whitespace, the FE0F variation
    selector, the ZWJ, or an EXACT Extended_Pictographic code point. Byte-faithful
    to the app (check-proven), so the franchise no-headline drop matches exactly —
    no orphan, and never a dropped-but-app-kept post."""
    if c in _JS_WS or c in "️‍":
        return True
    o = ord(c)
    i = bisect_right(_EXT_PICT_LO, o) - 1
    return i >= 0 and o <= _EXT_PICT[i][1]


def _franchise_headline(text: str) -> str:
    """feed-adapter.ts splitFranchise headline: the first non-empty line with its
    LEADING_EMOJI run stripped. The app drops a franchise post whose headline is
    then empty ("franchise post with no headline"); mirror that so the /p/ gate
    never publishes an orphan page. Never strips a LETTER/DIGIT, so a real headline
    is always kept."""
    first = next((ln.strip() for ln in (text or "").split("\n") if ln.strip()), "")
    i = 0
    while i < len(first) and _is_leading_emoji(first[i]):
        i += 1
    return first[i:].strip()


def adapt_post(rec: dict) -> dict | None:
    """feed-adapter.ts adaptOne(), ported to the subset a bill page needs.

    For the legislatures the app knows (us/eu) this returns None for EXACTLY the
    records the app drops, so the bill's post set matches the app's timelineFor —
    a dropped record is a gap; an invented one is a lie.

    For a BRAND-NEW legislature (a bot value the app hasn't been taught yet) it is
    deliberately more permissive: the D9 bucket map is us/eu-only, and dropping an
    unknown legislature's posts would mean "a new legislature silently gets no
    pages" — the exact opposite of the auto-adoption the machine promises. So an
    unknown bot skips the D9 gate and is rendered generically (with the LOUD
    legislature() warning at render time). The app, which drops unknown bots,
    simply hasn't caught up — parity is asserted for us/eu, robustness for the
    rest (SEO plan §2a + final addendum §3)."""
    if rec.get("v") != SCHEMA_SUPPORTED:
        return None
    bot = rec.get("bot")
    if not bot:
        return None
    if not rec.get("text"):
        return None
    type_map = POST_TYPE_MAP.get(rec.get("type"))
    if not type_map:
        return None
    known = bot in ("us", "eu")
    if known and not type_map.get("bucket"):
        # An 'action' post carries no fixed bucket → it needs a family that maps
        # in D9, or the app drops it. Mirror that drop, us/eu only.
        family = rec.get("family")
        if not family or not bucket_for(bot, family):
            return None
    sort_key = to_sort_key(rec.get("posted_at", ""))
    if not sort_key:
        return None
    # ?? semantics, NOT `or`: the app is `rec.event_date ?? rec.posted_at.slice(...)`,
    # so a PRESENT-but-EMPTY event_date ("") is KEPT ("" → formatDisplayDate → null
    # → drop), never replaced by the posting date. Python `or` would fall through
    # and fabricate a bill dated on the posting day for a record the app refuses
    # (guard finding, 2026-08-17). Mirror the internal_id block's `is None` fix.
    ev = rec.get("event_date")
    ev = ev if ev is not None else rec.get("posted_at", "")[:10]
    event_iso = re.sub(r"^([0-9]{2})-([0-9]{2})-([0-9]{4})$", r"\3-\2-\1", ev)
    event_date = format_display_date(event_iso)
    if not event_date:
        return None
    post_type = type_map["postType"]
    # A franchise post with no headline is DROPPED by the app (adaptOne) — mirror
    # it, or the /p/ gate publishes an orphan page for a record the app never mints
    # (guard finding, 2026-08-17). Status posts have no headline concept.
    if post_type != "status" and not _franchise_headline(rec.get("text", "")):
        return None
    p: dict = {
        "id": internal_id(rec),
        "permalink_id": post_id(rec),
        "polity": bot,
        "postType": post_type,
        "sortKey": sort_key,
        "eventDate": event_date,
        "eventDay": event_iso,
        "_rec": rec,
    }
    if post_type == "status":
        p["reference"] = rec.get("reference")
        # congress becomes part of a FILENAME (the /b/ slug + the path-artifact
        # name), so it must be a clean non-negative int. A corrupt/hostile value
        # ("../../x") would traverse OUT of the --out tree and brick the workflow
        # (guard finding, 2026-08-17). A non-int is treated as ABSENT (→ the
        # LEGACY_CONGRESS fallback) — the safe choice; the app trusts its typed
        # `number` field, the generator must not.
        cong = rec.get("congress")
        if isinstance(cong, int) and not isinstance(cong, bool) and 0 <= cong < 1000:
            p["congress"] = cong
        if rec.get("title"):
            p["title"] = rec.get("title")
        label = rec.get("label")
        if label:
            p["label"] = f'{rec["emoji"]} {label}' if rec.get("emoji") else label
        tally = rec.get("tally")
        if tally and tally not in (rec.get("label") or ""):
            p["tally"] = tally
        if rec.get("chamber"):
            p["chamber"] = rec.get("chamber")
        if rec.get("summary"):
            p["summary"] = rec.get("summary")
        # ?? semantics + filter(Boolean), NOT `or`: the app is
        # [rec.committee ?? rec.committees, rec.rapporteur ?? rec.sponsor].filter(Boolean).
        # A present-but-empty committee ("") must NOT fall through to committees
        # (`or` would; `??` keeps "" and filter drops it) — guard finding.
        committee = rec.get("committee")
        committee = committee if committee is not None else rec.get("committees")
        person = rec.get("rapporteur")
        person = person if person is not None else rec.get("sponsor")
        meta = " · ".join(x for x in (committee, person) if x)
        if meta:
            p["meta"] = meta
        if rec.get("whats_next"):
            p["whatsNext"] = rec.get("whats_next")
    return p


# --------------------------------------------------------------------------- #
#  The path merge (posts.ts mergeRecord + helpers). Byte-faithful; every ⚠️ in
#  the app's source marks a spot bought with a real failure — do not "simplify".
# --------------------------------------------------------------------------- #
def bare_label(l: str | None) -> str:
    """posts.ts bareLabel(): strip the leading emoji run and the trailing vote
    descriptor so a POST label and its bare path-artifact twin compare equal.
    Keeps a chamber qualifier ("(House)") — that separates two real events."""
    s = l or ""
    s = re.sub(r"^[^A-Za-z]+", "", s)                       # leading emoji / VS / space
    s = re.sub(r"\s*\((?:voice vote|unanimous consent)\)$", "", s, flags=re.I)  # method, no digit
    s = re.sub(r"\s*\(?[0-9][0-9\s()+–—-]*\)?$", "", s)  # trailing numeric tally ([0-9]=JS \d)
    return s.strip()


_TRAILING_TALLY = re.compile(r"[0-9][0-9\s]*[-–—][0-9\s]*[0-9]\)?\s*$")


def carries_tally(r: dict) -> bool:
    """posts.ts carriesTally(): a structured tally OR a count baked into the label."""
    return bool(r.get("tally")) or bool(_TRAILING_TALLY.search(r.get("label") or ""))


def _by_day_milestone_first(a: dict, b: dict) -> int:
    """posts.ts byDayMilestoneFirst comparator: newest EVENT day first; on a
    shared day a spine (milestone) leads its details; then newest posting instant."""
    da, db = a["dayKey"], b["dayKey"]
    if da != db:
        return 1 if da < db else -1
    if a["spine"] != b["spine"]:
        return -1 if a["spine"] else 1
    if a["sortKey"] == b["sortKey"]:
        return 0
    return 1 if a["sortKey"] < b["sortKey"] else -1


def _reorder_same_day_posts(rows: list[dict], post_order: dict) -> list[dict]:
    """posts.ts reorderSameDayPosts(): within each maximal run of consecutive
    same-day POST rows, sort ONLY the twinned rows by artifact order (desc), back
    into their own slots. Untwinned posts and all record rows never move."""
    out = rows[:]
    i = 0
    while i < len(out):
        if not out[i].get("post"):
            i += 1
            continue
        day = out[i]["dayKey"]
        j = i
        while j < len(out) and out[j].get("post") and out[j]["dayKey"] == day:
            j += 1
        slots, ordered = [], []
        for k in range(i, j):
            if id(out[k]) in post_order:
                slots.append(k)
                ordered.append(out[k])
        if len(ordered) > 1:
            ordered.sort(key=lambda r: post_order[id(r)], reverse=True)  # order desc = newer first
            for m, slot in enumerate(slots):
                out[slot] = ordered[m]
        i = j
    return out


def merge_record(reference: str, posts: list[dict], entries: list[dict]) -> list[dict]:
    """posts.ts mergeRecord(): posts + never-posted record rows, newest-first,
    posts winning on collision, same-day reorder + detail attachment (Stage 2)."""
    post_rows: list[dict] = [{
        "key": p["id"],
        "eventDate": p["eventDate"],
        "dayKey": p.get("eventDay") or p["sortKey"][:10],
        "sortKey": p["sortKey"],
        "label": p.get("label"),
        "tally": p.get("tally"),
        "spine": True,
        "post": p,
    } for p in posts]

    # order-by-key (claim-map keyed) → twin order, for the same-day reorder.
    order_by_key: dict = {}
    for e in entries:
        k = f'{format_display_date(e["date"]) or e["date"]}|{bare_label(e.get("label"))}'
        sub = e.get("subordinate") is True
        prev = order_by_key.get(k)
        if not prev:
            order_by_key[k] = {"order": e["order"], "sub": sub, "ambiguous": False}
        elif prev["ambiguous"]:
            continue
        elif prev["sub"] and not sub:
            order_by_key[k] = {"order": e["order"], "sub": False, "ambiguous": False}
        elif not prev["sub"] and sub:
            continue
        elif prev["order"] != e["order"]:
            order_by_key[k] = {**prev, "ambiguous": True}

    def twin_order(p: dict):
        base = f'{p["eventDate"]}|{bare_label(p.get("label"))}'
        if p.get("chamber"):
            hit = order_by_key.get(f'{base} ({p["chamber"]})') or order_by_key.get(base)
        else:
            hit = order_by_key.get(base)
        return hit["order"] if hit and not hit["ambiguous"] else None

    post_order: dict = {}
    for r in post_rows:
        o = twin_order(r["post"]) if r.get("post") else None
        if o is not None:
            post_order[id(r)] = o

    # claim map: a post claims its record twin by (date, bareLabel); keep a twin
    # carrying a recorded tally no claiming post carries (never omit a roll-call).
    claimed: dict = {}

    def claim(k: str, post_has_tally: bool) -> None:
        claimed[k] = bool(claimed.get(k)) or post_has_tally

    for r in post_rows:
        post_has_tally = carries_tally(r)
        base = f'{r["eventDate"]}|{bare_label(r.get("label"))}'
        claim(base, post_has_tally)
        ch = r["post"].get("chamber") if r.get("post") else None
        if ch:
            claim(f"{base} ({ch})", post_has_tally)

    record_rows: list[dict] = []
    for e in entries:
        if e.get("subordinate") is True:
            continue
        ev_date = format_display_date(e["date"]) or e["date"]
        row = {
            "key": f'rec-{reference}-{e["order"]}',
            "eventDate": ev_date,
            "dayKey": e["date"],
            "sortKey": f'{e["date"]}T{e["order"] // 60:02d}:{e["order"] % 60:02d}',
            "label": e.get("label"),
            "tally": e.get("tally"),
            "methodNote": e.get("method_note"),
            "reviewNote": e.get("review_note"),
            "text": e.get("text"),
            "spine": e.get("spine") is True,
            "post": None,
        }
        post_has_tally = claimed.get(f'{ev_date}|{bare_label(row.get("label"))}')
        if post_has_tally is None:
            record_rows.append(row)          # not a posted twin → keep
        elif bool(row.get("tally")) and not post_has_tally:
            record_rows.append(row)          # tally-bearing twin no post covers → keep
        # else: redundant twin of a post that carries at least as much → drop

    merged = sorted(post_rows + record_rows, key=cmp_to_key(_by_day_milestone_first))
    final = _reorder_same_day_posts(merged, post_order)

    # Stage 2 Part A: attach each DETAIL row to its TRUE same-day milestone by
    # artifact order (the largest surviving spine order ≤ the detail's order),
    # never to whichever spine sits above it. Never infers an order not given.
    row_order: dict = dict(post_order)  # twinned posts carry their dropped twin's order
    rec_prefix = f"rec-{reference}-"
    for r in final:
        if not r["key"].startswith(rec_prefix):
            continue
        try:
            row_order[id(r)] = int(r["key"][len(rec_prefix):])
        except ValueError:
            pass
    for d in final:
        if d["spine"]:
            continue
        d_order = row_order.get(id(d))
        if d_order is None:
            continue
        best, best_order = None, None
        for s in final:
            if not s["spine"] or s["dayKey"] != d["dayKey"]:
                continue
            s_order = row_order.get(id(s))
            if s_order is None or s_order > d_order:
                continue
            if best_order is None or s_order > best_order:
                best_order, best = s_order, s
        if best:
            d["parentKey"] = best["key"]
    return final


# --------------------------------------------------------------------------- #
#  Path artifacts (path-client.ts fetchBillPath, ported to a local file read).
# --------------------------------------------------------------------------- #
def load_path_artifact(paths_dir, bot: str, reference: str,
                       congress: int | None) -> dict:
    """Returns {status, entries, holds_full_record}. status is 'ok' | 'none' |
    'error'/'schema'. 'none' = no artifact (render posts-only — normal, the app
    does the same); 'schema' = an unsupported `v` (fail closed, posts-only + a
    LOUD warning, never a guessed row); a US congress mismatch = a DIFFERENT bill
    sharing a number → 'none' (never another bill's record)."""
    ident = bill_identity(bot, reference, congress)
    if not ident or not ident.get("path_file") or paths_dir is None:
        return {"status": "none", "entries": [], "holds_full_record": None}
    f = paths_dir / ident["path_file"]
    if not f.is_file():
        return {"status": "none", "entries": [], "holds_full_record": None}
    try:
        art = json.loads(f.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        # ::warning:: prefix (like the schema-v case below) so the workflow's log
        # scan surfaces it — a 200-but-corrupt artifact from the feed host is an
        # operational signal, not a silent posts-only degrade (guard finding).
        log.warning("::warning::path artifact %s is unreadable (%s) — rendering "
                    "posted milestones only", f.name, e)
        return {"status": "error", "entries": [], "holds_full_record": None}
    if art.get("v") != PATH_SCHEMA_SUPPORTED:
        # Fail closed, exactly like the app: there IS a record here, we just can't
        # safely read this shape — posts-only, and say so, never "that's all".
        log.warning("::warning::unsupported path artifact schema v%s in %s — "
                    "rendering posted milestones only", art.get("v"), f.name)
        return {"status": "schema", "entries": [], "holds_full_record": None}
    if ident["grammar"] == "us":
        expected = congress if congress is not None else LEGACY_CONGRESS
        if art.get("congress") != expected:
            return {"status": "none", "entries": [], "holds_full_record": None}
    entries = [{
        "order": e.get("order"),
        "date": e.get("date"),
        "text": e.get("text"),
        "label": e.get("label"),
        "tally": e.get("tally"),
        "method_note": e.get("method_note"),
        "review_note": e.get("review_note"),
        "spine": e.get("spine") is True,
        "subordinate": e.get("subordinate") is True,
    } for e in (art.get("entries") or [])]
    hfr = art.get("holds_full_record")
    return {
        "status": "ok",
        "entries": entries,
        "holds_full_record": True if hfr is True else (False if hfr is False else None),
    }


# --------------------------------------------------------------------------- #
#  Bill identity + the FROZEN slug rule (SEO plan Gate 1 + final addendum §1b).
#
#  ⚠️ THE SLUG IS IMMUTABLE ONCE PUBLISHED. Google keeps ONE canonical URL per
#  bill forever; changing a slug owes a 301 for every old URL. So the slug is
#  derived ONLY from stable identity — polity, Congress (US), the reference —
#  NEVER from a mutable field (title, latest label). US carries the Congress
#  (H.R. 3497 in the 119th ≠ the 120th; mirrors the artifact key). EU is
#  self-identifying by year. An unknown reference grammar (a future legislature)
#  gets a deterministic generic slug + a LOUD warning — never "no page", never a
#  crash. Recorded as law in docs/PERMALINKS.md.
# --------------------------------------------------------------------------- #
# A slug becomes a FILE PATH under /b/<polity>/ — it must be filename-safe (no
# slash, dot, or traversal) AND collision-free (two DISTINCT bills must never map
# to one URL). This is the belt: every returned slug is asserted against it.
_SLUG_SAFE = re.compile(r"^[a-z0-9][a-z0-9-]*$")


def bill_identity(bot: str, reference: str, congress: int | None) -> dict | None:
    """(polity, frozen slug, path-artifact filename, grammar). None only when
    there is no bot to file it under."""
    if not bot:
        return None
    us = parse_us_ref(reference or "")
    if us:
        c = congress if congress is not None else LEGACY_CONGRESS
        stem = f'{c}-{us["type"]}-{us["num"]}'
        if _SLUG_SAFE.match(stem):
            return {"polity": bot, "slug": stem, "path_file": f"{stem}.json",
                    "grammar": "us", "congress": c}
    eu = parse_eu_ref(reference or "")
    if eu:
        stem = f'{eu["year"]}-{eu["num"]}-{eu["type"]}'
        if _SLUG_SAFE.match(stem):
            return {"polity": bot, "slug": stem, "path_file": f"eu-{stem}.json",
                    "grammar": "eu", "congress": None}
    # Generic branch: a legislature whose reference grammar neither parser knows.
    # Deterministic + frozen. The normalized text ALONE is lossy — "!!", "a.b" and
    # "a-b" all collapse to the same string and would MERGE distinct bills onto one
    # canonical URL (guard finding, 2026-08-17). So append a short hash of the
    # EXACT reference: two distinct references can never share a slug, while the
    # readable prefix survives. Still derived only from the (stable) reference.
    norm = re.sub(r"[^a-z0-9]+", "-", (reference or "").lower()).strip("-")
    tag = hash8(reference or "")[:6]
    slug = f"{bot}-{norm}-{tag}" if norm else f"{bot}-{tag}"
    return {"polity": bot, "slug": slug, "path_file": None,
            "grammar": "generic", "congress": None}


def derive_congress(steps: list[dict]) -> int | None:
    """bill/[ref].tsx: the bill's Congress = the newest step that carries a stamp;
    None if none do (path-client then falls back to LEGACY_CONGRESS). `steps` is
    newest-first (timelineFor order)."""
    for p in steps:
        if p.get("congress") is not None:
            return p["congress"]
    return None


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
#  ⚠️ /p/ POST PAGES ARE NOINDEX FOREVER (2026-08-16, settled by the SEO plan
#  2026-08-17): they are the bill pages' CITATIONS — share-link landings + OG
#  cards that work unindexed, and a bill-bearing post canonicalises to its /b/
#  bill page. The INDEXABLE unit is the BILL (/b/), bounded by bills that move —
#  NOT the per-post page, whose permanent-retention set would accumulate without
#  bound. So this noindex never lifts; the SEO surface is /b/ (INDEX_BILL_PAGES).
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
    m = re.match(r"^([0-9]{4})-([0-9]{2})-([0-9]{2})$", iso)
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

FOOTER = """<footer class="site-footer">
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
</footer>"""


PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} | BillTracking</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canonical}">
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
    {bill_link}
    {x_link}
  </p>

  <p class="post-note">
    A permanent record of a post published by BillTracking's {tracker}. The facts are
    drawn from the official record; the reference above is the lookup key on
    {source_name}. Spotted an error?
    <a href="mailto:accuracy@billtracking.org">accuracy@billtracking.org</a>.
  </p>
</main>

{FOOTER}
</body>
</html>
"""


def render(rec: dict, id_: str, superseded_by: str | None,
           canonical: str | None = None, bill_url: str | None = None) -> str:
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
    event_iso = re.sub(r"^([0-9]{2})-([0-9]{2})-([0-9]{4})$", r"\3-\2-\1", event_iso)
    event_human = human_date(event_iso) if event_iso else ""
    if event_human and event_human != posted_human:
        dateline = f"{event_human} · posted {posted_human}"
    else:
        dateline = f"Posted {posted_human}"

    # X is the tertiary surface: a quiet link, not the primary button.
    x_link = ""
    tid = str(rec.get("tweet_id") or "")
    if re.fullmatch(r"[0-9]{1,25}", tid):   # a tweet id is digits only — anything else, no link
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

    url = f"{SITE_URL}/p/{id_}"
    # CANONICAL DISCIPLINE (SEO plan final addendum §1a): a post that belongs to a
    # bill points its canonical at THE BILL PAGE, so this thin per-post page never
    # competes with the bill for the same query — its crawl equity consolidates
    # onto the bill (noindex + canonical-to-bill is how that is done). A franchise
    # post (no bill) stays self-canonical. `bill_url` is passed only for the former.
    canonical_url = bill_url or canonical or url
    bill_link = (f'<a href="{esc(bill_url)}">See the full path of {esc(rec.get("reference", ""))}</a>'
                 if bill_url else "")
    return PAGE.format(
        title=esc(title), desc=esc(desc), url=url, canonical=esc(canonical_url),
        SITE_URL=SITE_URL, bot=bot, accent=accent, PAGE_CSS=PAGE_CSS, NAV=NAV,
        FOOTER=FOOTER, bill_link=bill_link,
        tracker=esc(TRACKER.get(bot, "tracker")), h1=esc(h1),
        dateline=esc(dateline), corrected=corrected,
        body=text_html(rec.get("text", "")), funnel=funnel_html(bot),
        source_url=source_url, source_name=esc(source_name), x_link=x_link,
    )


# =========================================================================== #
#  BILL PAGES — /b/<polity>/<slug>  (SEO plan §1–3). The indexable unit is THE
#  BILL, never the post: a set bounded by bills that MOVE, not by time. Post
#  pages (/p/*) stay noindex and become the bill's citations. Bill pages carry
#  the same merged record the app's bill screen shows (one-renderer law) — proven
#  by scripts/check-permalinks.js against the app's real code.
#
#  ⚠️ NOT INDEXABLE UNTIL GATE 2. Bill pages carry `noindex` and the bill sitemap
#  is NOT listed in robots.txt until the owner litigates the unit + copy and
#  approves the flip (SEO plan Gate 2). Flipping is deliberately ONE switch:
#  INDEX_BILL_PAGES = True + list bill-sitemap.xml in robots.txt + submit it.
# =========================================================================== #
INDEX_BILL_PAGES = False

# The one small per-legislature table the machine can't derive from the feed
# (SEO plan §2a). Everything else — WHICH legislatures exist — comes from the
# distinct `bot` values present in the feed, so a new legislature is auto-adopted
# the moment its bot value appears. An unknown bot renders with a generic name
# and a LOUD ::warning:: (below) — never silently skipped, never blocking.
LEGISLATURES = {
    "us": {
        "name": "United States Congress", "bills_label": "US bills", "noun": "bill",
        "jurisdiction": "United States", "accent": "#0A3161",
        "source_name": "Congress.gov", "source_url": "https://www.congress.gov",
        "source_note": "the actions Congress.gov has recorded for it",
        "feed_path": "/us",
    },
    "eu": {
        "name": "European Union", "bills_label": "EU files", "noun": "file",
        "jurisdiction": "European Union", "accent": "#003399",
        "source_name": "OEIL Legislative Observatory", "source_url": "https://oeil.europarl.europa.eu",
        "source_note": "OEIL's key events, in OEIL's own order and OEIL's own words",
        "feed_path": "/eu",
    },
}


def legislature(bot: str) -> dict:
    """Display metadata for a legislature. An unknown bot (a legislature added to
    the feed but not yet to this table) gets a generic card + a LOUD warning, so
    the machine keeps working and a human knows the ONE line to add."""
    L = LEGISLATURES.get(bot)
    if L:
        return L
    log.warning("::warning::legislature %r is not in LEGISLATURES — rendering with a "
                "generic display name; add it (name, jurisdiction, source, feed path) "
                "to tools/generate.py LEGISLATURES", bot)
    up = (bot or "").upper() or "Legislature"
    return {
        "name": up, "bills_label": f"{up} bills", "noun": "bill",
        "jurisdiction": up, "accent": "#0A3161",
        "source_name": "the official record", "source_url": "",
        "source_note": "the actions recorded for it", "feed_path": "/",
    }


# --------------------------------------------------------------------------- #
#  Status glyphs (Gate-2 option). Emoji is the default; --glyphs svg swaps the
#  archived emoji for the app's own SVG icon language on this COMPOSED surface
#  (the /p/ post pages keep the emoji verbatim — D17, the artifact as published).
#  Ports label-icon.tsx: same ordered prefix table (longest first), same BELT
#  (an unknown prefix keeps the emoji it always was). Tabler stroke paths, MIT.
# --------------------------------------------------------------------------- #
GLYPH_ICON_PATHS = {
    "capitol": ["M4 8l8 -5l8 5l-16 0", "M7 11v6", "M10.35 11v6", "M13.65 11v6", "M17 11v6", "M5 17h14", "M3 20h18"],
    "circle-check": ["M3 12a9 9 0 1 0 18 0a9 9 0 0 0 -18 0", "M9 12l2 2l4 -4"],
    "ballot": ["M9 12l2 2l4 -4", "M5 7c0 -1.1 .9 -2 2 -2h10a2 2 0 0 1 2 2v12h-14z", "M22 19h-20"],
    "clipboard-text": ["M9 5h-2a2 2 0 0 0 -2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2 -2v-12a2 2 0 0 0 -2 -2h-2", "M9 5a2 2 0 0 1 2 -2h2a2 2 0 0 1 2 2a2 2 0 0 1 -2 2h-2a2 2 0 0 1 -2 -2", "M9 12h6", "M9 16h6"],
    "clock": ["M3 12a9 9 0 1 0 18 0a9 9 0 0 0 -18 0", "M12 7v5l3 3"],
    "calendar-event": ["M4 7a2 2 0 0 1 2 -2h12a2 2 0 0 1 2 2v12a2 2 0 0 1 -2 2h-12a2 2 0 0 1 -2 -2l0 -12", "M16 3l0 4", "M8 3l0 4", "M4 11l16 0", "M8 15h2v2h-2l0 -2"],
    "send": ["M10 14l11 -11", "M21 3l-6.5 18a.55 .55 0 0 1 -1 0l-3.5 -7l-7 -3.5a.55 .55 0 0 1 0 -1l18 -6.5"],
    "compass": ["M8 16l2 -6l6 -2l-2 6l-6 2", "M3 12a9 9 0 1 0 18 0a9 9 0 1 0 -18 0"],
    "handshake": ["M11 17l2 2a1 1 0 1 0 3 -3", "M14 14l2.5 2.5a1 1 0 1 0 3 -3l-3.88 -3.88a3 3 0 0 0 -4.24 0l-.88 .88a1 1 0 1 1 -3 -3l2.81 -2.81a5.79 5.79 0 0 1 7.06 -.87l.47 .28a2 2 0 0 0 1.42 .25l1.74 -.35", "M21 3l1 11h-2", "M3 3l-1 11l6.5 6.5a1 1 0 1 0 3 -3", "M3 4h8"],
    "signature": ["M3 17c3.333 -3.333 5 -6 5 -8c0 -3 -1 -3 -2 -3s-2.032 1.085 -2 3c.034 2.048 1.658 4.877 2.5 6c1.5 2 2.5 2.5 3.5 1l2 -3c.333 2.667 1.333 4 3 4c.53 0 2.639 -2 3 -2c.517 0 1.517 .667 3 2"],
    "scroll": ["M15 12h-5", "M15 8h-5", "M19 17V5a2 2 0 0 0 -2 -2H4", "M8 21h12a2 2 0 0 0 2 -2v-1a1 1 0 0 0 -1 -1H11a1 1 0 0 0 -1 1v1a2 2 0 1 1 -4 0V5a2 2 0 1 0 -4 0v2a1 1 0 0 0 1 1h3"],
    "x": ["M18 6l-12 12", "M6 6l12 12"],
    "arrow-back-up": ["M9 14l-4 -4l4 -4", "M5 10h11a4 4 0 1 1 0 8h-1"],
    "scale": ["M7 20l10 0", "M6 6l6 -1l6 1", "M12 3l0 17", "M9 12l-3 -6l-3 6a3 3 0 0 0 6 0", "M21 12l-3 -6l-3 6a3 3 0 0 0 6 0"],
    "file-off": ["M3 3l18 18", "M7 3h7l5 5v7m0 4a2 2 0 0 1 -2 2h-10a2 2 0 0 1 -2 -2v-14"],
    "edit": ["M7 7h-1a2 2 0 0 0 -2 2v9a2 2 0 0 0 2 2h9a2 2 0 0 0 2 -2v-1", "M20.385 6.585a2.1 2.1 0 0 0 -2.97 -2.97l-8.415 8.385v3h3l8.385 -8.415", "M16 5l3 3"],
}
# (prefix, icon, green, badge) — SAME ORDER as label-icon.tsx GLYPHS (longest
# prefix first, so '✅🏛️' wins over '✅'). green = whole glyph green; badge = a
# small green check at the corner (passed a chamber / became law).
LABEL_GLYPHS = [
    ("✅🏛️", "capitol", False, True), ("✅", "circle-check", True, False),
    ("🗳️", "ballot", False, False), ("🗳", "ballot", False, False),
    ("📋", "clipboard-text", False, False), ("⏱️", "clock", False, False), ("⏱", "clock", False, False),
    ("📅", "calendar-event", False, False), ("🗓️", "calendar-event", False, False), ("🗓", "calendar-event", False, False),
    ("📌", "send", False, False), ("🧭", "compass", False, False), ("🤝", "handshake", False, False),
    ("🖋️", "signature", False, False), ("🖋", "signature", False, False),
    ("📜✍️", "scroll", False, True), ("📜", "scroll", False, True),
    ("✍️", "signature", False, False), ("✍", "signature", False, False),
    ("🏛️", "capitol", False, False), ("🏛", "capitol", False, False),
    ("❌", "x", False, False), ("↩️", "arrow-back-up", False, False), ("↩", "arrow-back-up", False, False),
    ("⚖️", "scale", False, False), ("⚖", "scale", False, False),
    ("🗑️", "file-off", False, False), ("🗑", "file-off", False, False), ("📝", "edit", False, False),
]


def split_label_glyph(label: str):
    """label-icon.tsx splitLabel(): longest-prefix-first; the BELT returns
    (None, label) for an unknown prefix so it renders as the emoji it always was."""
    for prefix, icon, green, badge in LABEL_GLYPHS:
        if label.startswith(prefix):
            return (icon, green, badge), label[len(prefix):].strip()
    return None, label


def _glyph_sprite() -> str:
    syms = []
    for name, paths in GLYPH_ICON_PATHS.items():
        d = "".join(f'<path d="{p}"/>' for p in paths)
        syms.append(f'<symbol id="ic-{name}" viewBox="0 0 24 24" fill="none" '
                    f'stroke="currentColor" stroke-width="1.8" stroke-linecap="round" '
                    f'stroke-linejoin="round">{d}</symbol>')
    return ('<svg width="0" height="0" style="position:absolute" aria-hidden="true">'
            + "".join(syms) + "</svg>")


def glyph_label_html(label: str, mode: str) -> str:
    """Render a status label. `emoji` (default) keeps the archived text verbatim;
    `svg` swaps a known leading emoji for the app's glyph, unknown → emoji BELT."""
    if mode != "svg":
        return esc(label)
    glyph, text = split_label_glyph(label)
    if not glyph:
        return esc(label)
    icon, green, badge = glyph
    cls = "glyph" + (" glyph-green" if green else "")
    badge_svg = ('<span class="glyph-badge"><svg viewBox="0 0 24 24"><use href="#ic-circle-check"/></svg></span>'
                 if badge else "")
    return (f'<span class="glyph-wrap">'
            f'<svg class="{cls}" aria-hidden="true"><use href="#ic-{icon}"/></svg>{badge_svg}'
            f'</span>{esc(text)}')


# --------------------------------------------------------------------------- #
#  JSON-LD — Schema.org Legislation + BreadcrumbList. ONLY fields we HAVE; never
#  a value invented to fill a slot (SEO plan §3). Dates are dated, never bare
#  (final addendum §2): legislationDate = the earliest recorded action; a stale
#  Google cache is then a dated snapshot, not a false claim.
# --------------------------------------------------------------------------- #
_US_LEG_TYPE = {
    "hr": "Bill", "s": "Bill",
    "hres": "Resolution", "sres": "Resolution",
    "hjres": "Joint Resolution", "sjres": "Joint Resolution",
    "hconres": "Concurrent Resolution", "sconres": "Concurrent Resolution",
}


def _jsonld(bill: dict) -> str:
    L, ident = bill["leg"], bill["ident"]
    canonical = bill["canonical"]
    record = bill["info"]["record"]
    days = [r["dayKey"] for r in record if re.match(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$", r.get("dayKey") or "")]
    leg = {
        "@context": "https://schema.org",
        "@type": "Legislation",
        "name": bill["info"].get("title") or bill["reference"],
        "legislationIdentifier": bill["reference"],
        "inLanguage": "en",
        "url": canonical,
    }
    # legislationType only where the reference grammar tells us unambiguously —
    # US bill vs resolution. An EU procedure code (COD/APP/…) names the PROCEDURE,
    # not the instrument (regulation vs directive vs decision), so we do NOT guess.
    if ident["grammar"] == "us":
        us = parse_us_ref(bill["reference"])
        if us and us["type"] in _US_LEG_TYPE:
            leg["legislationType"] = _US_LEG_TYPE[us["type"]]
    if L.get("jurisdiction"):
        leg["jurisdiction"] = L["jurisdiction"]
    if L.get("source_url"):
        leg["isBasedOn"] = {"@type": "WebPage", "url": L["source_url"]}
    if days:
        leg["legislationDate"] = min(days)      # earliest recorded action (dated)
        leg["dateModified"] = max(days)         # latest recorded action (the "as of")
    crumbs = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE_URL}/"},
            {"@type": "ListItem", "position": 2, "name": L["bills_label"],
             "item": f"{SITE_URL}/b/{ident['polity']}/"},
            {"@type": "ListItem", "position": 3, "name": bill["reference"], "item": canonical},
        ],
    }
    payload = json.dumps([leg, crumbs], ensure_ascii=False, separators=(",", ":"))
    # Escape EVERY `<` as its JSON < escape (decodes back to `<` for any JSON-LD
    # consumer, identical semantics). A `</`-only replace was defeated by a hostile
    # `<!--<script` in a record title, which drives the HTML5 script-data state
    # machine into double-escaped mode so the real </script> no longer closes the
    # element — swallowing the whole page body (guard finding, 2026-08-17). No raw
    # `<` in the script text means the HTML parser can never mis-tokenise it.
    payload = payload.replace("<", "\\u003c")
    return f'<script type="application/ld+json">{payload}</script>'


def needed_path_files(feed_paths) -> list[str]:
    """The artifact filenames the bill pages need, derived from the feed alone —
    so the workflow fetches EXACTLY those from the feed host (GitHub Pages gives
    no directory listing). One source for the derivation: the same bill_identity
    the render uses. A per-post identity yields the same filename as the bill's
    (single-Congress bills share their Congress), and the set dedups the rest."""
    recs = [r for r in gather_feed(feed_paths) if _ID_SHAPE.match(post_id(r))]
    files: set = set()
    for r in recs:
        p = adapt_post(r)
        if not p or p["postType"] != "status" or not p.get("reference"):
            continue
        ident = bill_identity(p["polity"], p["reference"], p.get("congress"))
        if ident and ident.get("path_file"):
            files.add(ident["path_file"])
    return sorted(files)


def bill_info(reference: str, steps: list[dict], entries: list[dict]) -> dict:
    """posts.ts billInfo(), ported: identity + the full merged path."""
    tip = steps[0]
    return {
        "reference": reference,
        "title": tip.get("title") or "",
        "meta": tip.get("meta"),
        "polity": tip["polity"],
        "summary": next((p["summary"] for p in steps if p.get("summary")), None),
        "tip": tip,
        "steps": steps,
        "record": merge_record(reference, steps, entries),
    }


# Filename-safety gate for the /p/ id. Was `(us|eu)` — widened to any short
# lowercase bot prefix so a NEW legislature's posts get pages too (auto-adoption,
# SEO plan §2a); the shape still bans slashes/dots/traversal, and the bot value
# is the bots' own, not user input. The workflow's p/ stray-file guard and the
# check's id regex use the same widened shape.
_ID_SHAPE = re.compile(r"^[a-z]{2,12}-[0-9]{8}-[0-9a-f]{8}$")

SITEMAP = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n')


BILL_CSS = """
    .bill-wrap { max-width: 46rem; margin: 0 auto; padding: 1.5rem 1.25rem 4rem; }
    .crumbs { font-family: var(--sans); font-size: .82rem; color: var(--ink-faint);
      margin-bottom: 1.4rem; }
    .crumbs a { color: var(--ink-soft); }
    .bill-kicker { font-family: var(--sans); font-weight: 700; font-size: .72rem;
      letter-spacing: .14em; text-transform: uppercase; color: var(--accent); }
    .bill-ref { font-family: var(--serif); font-size: 2.1rem; line-height: 1.15;
      color: var(--navy-ink); margin: .35rem 0 .2rem; }
    .bill-title { font-family: var(--serif); font-size: 1.25rem; color: var(--ink);
      line-height: 1.4; margin: 0 0 .5rem; }
    .bill-meta { font-family: var(--sans); color: var(--ink-faint); font-size: .9rem; margin: 0 0 1rem; }
    .bill-summary { background: var(--wash); border: 1px solid var(--line);
      border-radius: var(--radius); padding: .9rem 1.1rem; font-size: 1rem; line-height: 1.65;
      color: var(--ink); margin: 0 0 1.2rem; }
    .ai-tag { font-family: var(--sans); font-size: .72rem; font-weight: 700; letter-spacing: .04em;
      color: var(--ink-faint); text-transform: uppercase; margin-left: .4rem; }
    .bill-status { display: flex; align-items: baseline; gap: .6rem; flex-wrap: wrap;
      border-left: 3px solid var(--accent); padding: .3rem 0 .3rem .9rem; margin: 0 0 .4rem; }
    .bill-status .st-label { font-size: 1.1rem; font-weight: 650; color: var(--navy-ink); }
    .bill-status .st-date { font-family: var(--sans); font-size: .88rem; color: var(--ink-faint); }
    .bill-asof { font-family: var(--sans); font-size: .82rem; color: var(--ink-faint); margin: 0 0 1.6rem; }
    .path { list-style: none; padding: 0; margin: 0 0 1.6rem; border-top: 1px solid var(--line-soft); }
    .path li { padding: .75rem 0 .75rem 1.1rem; border-bottom: 1px solid var(--line-soft);
      border-left: 2px solid transparent; }
    .path li.spine { border-left-color: var(--line); }
    .path li.detail { padding-left: 2rem; background: #FCFDFF; }
    .row-date { font-family: var(--sans); font-size: .78rem; color: var(--ink-faint); }
    .row-label { font-size: 1rem; color: var(--ink); line-height: 1.5; }
    .row-label a { color: var(--navy); }
    .row-tally { font-variant-numeric: tabular-nums; color: var(--ink-soft); }
    .row-note { color: var(--ink-soft); font-style: italic; }
    .row-text { font-size: .96rem; color: var(--ink-soft); line-height: 1.55; }
    .row-corrected { display: block; font-family: var(--sans); font-size: .82rem;
      color: var(--gold-text); margin-top: .25rem; }
    .glyph-wrap { position: relative; display: inline-block; vertical-align: -.18em; margin-right: .35rem; }
    .glyph { width: 1.15em; height: 1.15em; color: var(--accent); }
    .glyph-green { color: #1A7F37; }
    .glyph-badge { position: absolute; right: -.25em; bottom: -.2em; width: .7em; height: .7em; color: #1A7F37; }
    .glyph-badge svg { width: 100%; height: 100%; fill: none; stroke: currentColor; stroke-width: 2.4;
      stroke-linecap: round; stroke-linejoin: round; }
    .honesty { background: var(--wash); border: 1px solid var(--line); border-radius: var(--radius);
      padding: 1rem 1.2rem; font-size: .92rem; line-height: 1.6; color: var(--ink-soft); margin: 0 0 1.4rem; }
    .honesty strong { color: var(--ink); }
    .bill-links { display: flex; flex-wrap: wrap; gap: 1.2rem; margin-top: 1.4rem;
      font-family: var(--sans); font-size: .9rem; }
    .bill-links a { color: var(--ink-soft); }
"""

BILL_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} | BillTracking</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canonical}">
{robots}<meta property="og:type" content="article">
<meta property="og:url" content="{canonical}">
<meta property="og:title" content="{ogtitle}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="{SITE_URL}/assets/{polity}-banner.webp">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" type="image/png" sizes="32x32" href="/assets/favicon-32.png">
<link rel="stylesheet" href="/style.css">
<style>:root {{ --accent: {accent}; }}{BILL_CSS}</style>
{jsonld}
</head>
<body>
<header class="site-header">
  <div class="wrap">
{NAV}
  </div>
</header>

<main class="bill-wrap">
  <p class="crumbs"><a href="/index.html">Home</a> › <a href="/b/{polity}/">{bills_label}</a> › {ref}</p>
  <p class="bill-kicker">{leg_name}</p>
  <h1 class="bill-ref">{ref}</h1>
{title_block}{meta_block}{summary_block}  <div class="bill-status"><span class="st-label">{status_label}</span> <span class="st-date">{status_date}</span></div>
  <p class="bill-asof">Record as of {asof} — the most recent action in the official record. Status can lag; each step below carries its own date.</p>
{sprite}  <ol class="path">
{rows}  </ol>

  <div class="honesty">{honesty}</div>

{funnel}
  <p class="bill-links">
    <a href="{source_url}">Look up {ref} on {source_name}</a>
    <a href="/b/{polity}/">All {bills_label}</a>
  </p>
</main>

{FOOTER}
</body>
</html>
"""


def _correction_marker(rec: dict) -> str:
    """Compact per-row 'Corrected' note on the bill page — a corrected post must
    show it is corrected however old it is (accuracy law / HOW). Reuses the same
    computed fields render() uses; the /p/ page carries the full banner."""
    c = rec.get("_correction")
    if c:
        date = esc(human_date(c.get("date", "")))
        patch = c.get("patch") or {}
        now = esc(" ".join(str(patch.get(k, "")) for k in ("label", "tally") if patch.get(k)).strip())
        cp = rec.get("_correction_page")
        link = f' <a href="/p/{esc(cp)}">Read the correction</a>.' if cp else ""
        now_txt = f" Now reads: {now}." if now else ""
        return f'<span class="row-corrected">Corrected {date}.{now_txt}{link}</span>'
    rv = rec.get("_revision")
    if rv:
        d = esc(human_date(rv.get("date", "")))
        fig = esc(rv.get("figure", ""))
        now_txt = f" Now reads: {fig}." if fig else ""
        return (f'<span class="row-corrected">Corrected {d}. The official record was later '
                f'amended.{now_txt} <a href="/p/{esc(rv["page"])}">Read the correction</a>.</span>')
    return ""


def _row_html(row: dict, glyphs_mode: str) -> str:
    kind = "post" if row.get("post") else "record"
    cls = "spine" if row["spine"] else "detail"
    date = esc(row.get("eventDate") or "")
    # tally / method-note / review-note are mutually exclusive on a node.
    extra = ""
    if row.get("tally"):
        extra = f' <span class="row-tally">{esc(row["tally"])}</span>'
    elif row.get("methodNote"):
        extra = f' <span class="row-note">{esc(row["methodNote"])}</span>'
    elif row.get("reviewNote"):
        extra = f' <span class="row-note">{esc(row["reviewNote"])}</span>'

    if row.get("post"):
        p = row["post"]
        label_html = glyph_label_html(row.get("label") or "", glyphs_mode)
        body = (f'<a href="/p/{esc(p["permalink_id"])}">{label_html}</a>{extra}'
                f'{_correction_marker(p["_rec"])}')
    elif row.get("label"):
        # a classified record row we never posted — its bare official label.
        body = f'{glyph_label_html(row["label"], glyphs_mode)}{extra}'
    else:
        # a row the classifier can't place: show the official record's exact
        # words, never a label we made up (HOW: "…rather than a label we made up").
        body = f'<span class="row-text">{esc(row.get("text") or "")}</span>'

    return (f'  <li class="{cls}" data-key="{esc(row["key"])}" data-kind="{kind}">'
            f'<span class="row-date">{date}</span> '
            f'<span class="row-label">{body}</span></li>\n')


def _honesty_html(leg: dict, path_status: str, holds_full: bool | None) -> str:
    noun, src = leg["noun"], esc(leg["source_name"])
    begins = (f'Where the record reaches the beginning, the path starts where the {noun} '
              f'does in the official record; where that can\'t be shown, it says instead '
              f'where the shown record begins.')
    if path_status == "ok" and holds_full is True:
        return (f'<strong>The full recorded path.</strong> Every step {src} lists for this '
                f'{noun} is shown. {begins}')
    if path_status == "ok" and holds_full is False:
        return (f'<strong>Part of the record isn\'t shown.</strong> The steps here are copied '
                f'from {src} verbatim, but the official record is longer than what could be '
                f'shown — this is not the complete path. {begins}')
    if path_status in ("error", "schema"):
        return (f'<strong>Posted milestones only.</strong> The full recorded path from {src} '
                f'couldn\'t be loaded for this render — you\'re seeing the steps we\'ve posted, '
                f'not the whole record. It is not that this is all there is.')
    # 'none' / 'ok' with unproven completeness (null): posts + whatever path exists.
    if path_status == "none":
        tail = (' A path with no OEIL page yet is normal, not broken — OEIL sometimes opens a '
                'procedure page days after the proposal appears.' if leg["noun"] == "file"
                else ' An older bill appears here the next time it moves.')
        return (f'<strong>The steps we\'ve posted.</strong> A full procedural path for this '
                f'{noun} isn\'t published yet, so this shows the milestones we\'ve posted from '
                f'{src}.{tail}')
    return (f'<strong>The recorded path.</strong> The steps here are drawn from {src}; vote '
            f'tallies, dates and reference numbers are copied verbatim, and where the record '
            f'lacks a value the line is omitted, not estimated. {begins}')


def render_bill(bill: dict, glyphs_mode: str) -> str:
    L, ident, info = bill["leg"], bill["ident"], bill["info"]
    ref = bill["reference"]
    record = info["record"]
    # Two dated facts, kept distinct (final addendum §2 — status must never read
    # as a timeless claim): the LATEST STATUS headline is the newest MILESTONE
    # (spine) — the most significant recent step; "Record as of" is the newest
    # recorded action of ANY kind — the record's freshness. A stale Google cache
    # then shows a dated milestone + a dated freshness line, never a bare claim.
    newest = record[0]
    latest = next((r for r in record if r["spine"]), newest)
    # <title>: "<ref> — <short title>", ref never truncated (SEO plan §3).
    title_txt = info.get("title") or ""
    head_title = ref
    if title_txt:
        prefix = f"{ref} — "
        avail = 60 - len(prefix)
        t = title_txt if len(title_txt) <= avail else title_txt[:max(1, avail - 1)].rstrip() + "…"
        head_title = prefix + t
    # Description: the latest status + its date + one factual sentence. NOT the AI
    # summary (that would need an [AI-Generated] marker in the snippet) — this is
    # the dated status, which is human-classified from the record.
    latest_label_plain = re.sub(r"^[^A-Za-z0-9]+", "", latest.get("label") or "").strip() or "In progress"
    latest_date = latest.get("eventDate") or ""
    # NOT "the FULL recorded path" — completeness is a tri-state the on-page honesty
    # box gates on holds_full_record; asserting "full" in the share card/snippet
    # overclaimed on a proven-truncated bill (guard finding, 2026-08-17). "The
    # recorded path" is true regardless of completeness.
    desc = (f"{latest_label_plain} — {latest_date}. The recorded path of {ref} "
            f"on BillTracking, from {L['source_name']}.")[:180]

    title_block = f'  <h2 class="bill-title">{esc(title_txt)}</h2>\n' if title_txt else ""
    meta_block = f'  <p class="bill-meta">{esc(info["meta"])}</p>\n' if info.get("meta") else ""
    summary_block = ""
    if info.get("summary"):
        # The ONLY AI-written text on the page → the [AI-Generated] label is
        # mandatory (HOW / EU AI Act Art. 50(4)).
        summary_block = (f'  <p class="bill-summary">{esc(info["summary"])}'
                         f'<span class="ai-tag">[AI-Generated]</span></p>\n')

    rows = "".join(_row_html(r, glyphs_mode) for r in record)
    sprite = f"  {_glyph_sprite()}\n" if glyphs_mode == "svg" else ""
    robots = "" if INDEX_BILL_PAGES else '<meta name="robots" content="noindex">\n'
    honesty = _honesty_html(L, bill["path_status"], bill["holds_full"])

    return BILL_PAGE.format(
        title=esc(head_title), ogtitle=esc(f"{ref} — {title_txt}" if title_txt else ref),
        desc=esc(desc), canonical=bill["canonical"], robots=robots,
        SITE_URL=SITE_URL, polity=ident["polity"], accent=L["accent"], BILL_CSS=BILL_CSS,
        jsonld=_jsonld(bill), NAV=NAV, FOOTER=FOOTER,
        bills_label=esc(L["bills_label"]), leg_name=esc(L["name"]), ref=esc(ref),
        title_block=title_block, meta_block=meta_block, summary_block=summary_block,
        status_label=glyph_label_html(latest.get("label") or "In progress", glyphs_mode),
        status_date=esc(latest_date),
        asof=esc(newest.get("eventDate") or ""), sprite=sprite, rows=rows, honesty=honesty,
        funnel=funnel_html(ident["polity"]),
        source_url=esc(L["source_url"]) or "/", source_name=esc(L["source_name"]),
    )


BILL_INDEX = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{bills_label} | BillTracking</title>
<meta name="description" content="Every {noun} BillTracking has a recorded path for in the {leg_name}, most recently active first.">
<link rel="canonical" href="{SITE_URL}/b/{polity}/">
{robots}<link rel="icon" type="image/png" sizes="32x32" href="/assets/favicon-32.png">
<link rel="stylesheet" href="/style.css">
<style>:root {{ --accent: {accent}; }}
  .bi-wrap {{ max-width: 46rem; margin: 0 auto; padding: 2rem 1.25rem 4rem; }}
  .bi-wrap h1 {{ font-family: var(--serif); color: var(--navy-ink); }}
  .bi-wrap ul {{ list-style: none; padding: 0; }}
  .bi-wrap li {{ padding: .8rem 0; border-bottom: 1px solid var(--line-soft); }}
  .bi-ref {{ font-weight: 650; color: var(--navy); }}
  .bi-title {{ color: var(--ink-soft); }}
  .bi-date {{ display: block; color: var(--ink-faint); font-size: .82rem; margin-top: .1rem; }}
</style>
</head>
<body>
<header class="site-header"><div class="wrap">
{NAV}
</div></header>
<main class="bi-wrap">
  <h1>{bills_label}</h1>
  <p>Every {noun} the {leg_name} tracker has a recorded path for — most recently active first. {n} listed.</p>
  <ul>
{rows}  </ul>
</main>
{FOOTER}
</body>
</html>
"""


def build(feed_paths, overrides_paths, out_root, paths_dir=None, glyphs_mode="emoji"):
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

    # ── OVERRIDES pre-pass. Attach the sheet's effects to each record BEFORE
    # both renderers read it AND before the D19 join runs, so the /p/ page and the
    # bill-page row show the same correction and a hidden record joins nothing.
    for r in recs:
        ov = overrides.get(r["_iid"])
        if not ov:
            continue
        kind = ov.get("kind")
        if kind == "remove-duplicate":
            r["_hidden"] = True                 # technical dup — no page anywhere
        elif kind == "correction":
            r["_correction"] = ov
            cp = ov.get("correctionPostId")
            if cp:
                r["_correction_page"] = iid_to_id.get(cp)
        elif kind == "revision-link":
            r["_superseded"] = iid_to_id.get(ov.get("supersededBy"))

    # ── ADAPT + THE KEPT SET. Adapt every non-hidden record exactly as the app
    # does (drop-aware); `kept_iids` is the app's minted set, and EVERYTHING
    # downstream — the D19 join, the /p/ gate, the bill grouping — runs over it,
    # never over raw `recs`. `adapted` is newest-first (byNewest), so each bill's
    # post list is newest-first too.
    adapted = [p for p in (adapt_post(r) for r in recs if not r.get("_hidden")) if p]
    adapted.sort(key=lambda p: p["sortKey"], reverse=True)   # posts.ts adaptFeed byNewest
    kept_iids = {p["id"] for p in adapted}

    # D19 RECORD REVISIONS — posts.ts linkRecordRevisions, which runs over the
    # ADAPTED posts (the kept set), NOT the raw feed. A superseding record the
    # adapter DROPS (schema bump, unmapped family, empty text) must never become a
    # stamp: it has no /p/ page, so stamping its target would fabricate a
    # "Corrected" banner linking to a 404 on an otherwise-clean bill (guard
    # finding, 2026-08-17). So the join set is the kept records only. Target by
    # tweet_id FIRST, then the natural-key hash (the fallback for an X success
    # whose shape hid the tweet id); a revision never crosses polities; the LATEST
    # revision of a target wins; and the stamp follows the chain to its HEAD
    # (A←B←C stamps A with C's figure — the middle figure would assert a stale
    # number as current truth).
    kept_recs = [r for r in recs if r["_iid"] in kept_iids]
    by_tid = {str(r["tweet_id"]): r for r in kept_recs if r.get("tweet_id")}
    by_key = {hash8(f'{r.get("bot", "")}|{r.get("posted_at", "")}|{r.get("text", "")}'): r for r in kept_recs}
    stamp_for: dict[str, dict] = {}   # target internal id → revision record
    for r in kept_recs:
        tid, key = r.get("supersedes_tweet_id"), r.get("supersedes_post_key")
        target = (by_tid.get(str(tid)) if tid else None) or (by_key.get(hash8(key)) if key else None)
        if not target or target is r or target.get("bot") != r.get("bot"):
            continue
        prev = stamp_for.get(target["_iid"])
        if not prev or prev.get("posted_at", "") < r.get("posted_at", ""):
            stamp_for[target["_iid"]] = r
    for r in kept_recs:
        stamp = stamp_for.get(r["_iid"])
        if not stamp:
            continue
        head, seen = stamp, {r["_iid"], stamp["_iid"]}
        nxt = stamp_for.get(head["_iid"])
        while nxt and nxt["_iid"] not in seen:
            head = nxt; seen.add(head["_iid"]); nxt = stamp_for.get(head["_iid"])
        # Figure = the ADAPTED head post's label+tally — posts.ts correctedTo.
        # The app order is linkRecordRevisions(applyOverrides(...)), so if the HEAD
        # is ALSO a manual-correction target its label/tally were PATCHED before the
        # figure is read; reading the raw/adapted-only head quoted the pre-correction
        # number on the superseded post while the head's own page showed the
        # corrected one (guard finding, 2026-08-17). Mirror applyOverrides: a patch
        # value (if present) REPLACES the field wholesale (PATCHABLE label/tally).
        hp = adapt_post(head) or {}
        patch = (head.get("_correction") or {}).get("patch") or {}
        h_label = patch["label"] if patch.get("label") is not None else (hp.get("label") or "")
        h_tally = patch["tally"] if patch.get("tally") is not None else hp.get("tally")
        figure = (h_label + (f" {h_tally}" if h_tally else "")).strip()
        r["_revision"] = {"date": head.get("posted_at", "")[:10], "figure": figure, "page": head["_id"]}

    # ── BILL GROUPING (from the kept `adapted`). A US bill is keyed by (polity,
    # congress-type-number) so the Jan-2027 rollover never merges the 119th and
    # 120th "H.R. 3497" into one page; EU is self-identifying by year.
    bills: dict = {}
    for p in adapted:
        # A whitespace-only reference is not a real bill and must not mint an
        # indexable /b/ URL (it grouped before — the guard only rejected FALSY
        # refs, and " " is truthy). Guard finding, 2026-08-17.
        if p["postType"] != "status" or not (p.get("reference") or "").strip():
            continue
        ident0 = bill_identity(p["polity"], p["reference"], p.get("congress"))
        if not ident0:
            continue
        key = (p["polity"], ident0["slug"])
        bills.setdefault(key, {"reference": p["reference"], "polity": p["polity"], "posts": []})
        bills[key]["posts"].append(p)

    # internal id → the one canonical bill URL (SEO plan §1c: exactly one URL per
    # bill; the /p/ post pages point their canonical here). Built before the /p/
    # loop so every post knows its bill.
    iid_to_bill: dict = {}
    bill_records = []   # (polity, ref, slug, canonical, title, latest_iso, bill_obj)
    for (polity, slug), b in bills.items():
        steps = b["posts"]
        reference = b["reference"]
        congress = derive_congress(steps)
        ident = bill_identity(polity, reference, congress)
        art = load_path_artifact(paths_dir, polity, reference, congress)
        info = bill_info(reference, steps, art["entries"])
        canonical = f"{SITE_URL}/b/{polity}/{ident['slug']}"
        bill = {
            "reference": reference, "ident": ident, "info": info,
            "leg": legislature(polity), "canonical": canonical,
            "path_status": art["status"], "holds_full": art["holds_full_record"],
        }
        latest_iso = info["record"][0]["dayKey"] if info["record"] else steps[0]["sortKey"][:10]
        bill_records.append((polity, reference, ident["slug"], canonical,
                             info.get("title") or "", latest_iso, bill))
        for p in steps:
            iid_to_bill[p["id"]] = canonical

    # ── /p/ POST PAGES: exactly the records the APP keeps (adapter-gated), so the
    # /p/ set equals the app's minted "Copy link" set — never a superset. A record
    # the app fail-closes on (unsupported schema v, unmapped family, unknown type,
    # empty text, unparseable/empty date) is DROPPED here too and logged, or the
    # generator would publish + sitemap-list a page the app refuses to mint (guard
    # finding, 2026-08-17). Canonical repoints to the bill page for a post that
    # belongs to one; a franchise / non-bill post stays self-canonical.
    out_p = out_root / "p"
    out_p.mkdir(parents=True, exist_ok=True)
    pages, written, dropped = [], 0, 0
    for r in recs:
        if r.get("_hidden"):
            continue
        if r["_iid"] not in kept_iids:
            dropped += 1
            log.warning("skipping record the app drops (bot=%r type=%r family=%r) — "
                        "no /p/ page, matching the app's minted set",
                        r.get("bot"), r.get("type"), r.get("family"))
            continue
        id_ = r["_id"]
        bill_url = iid_to_bill.get(r["_iid"])
        (out_p / f"{id_}.html").write_text(
            render(r, id_, r.get("_superseded"), bill_url=bill_url), encoding="utf-8")
        title, _ = describe(r)
        pages.append((id_, title, r.get("posted_at", "")[:10], r.get("bot", "us")))
        written += 1
    if dropped:
        log.info("dropped %d record(s) the app also drops (no /p/ page)", dropped)

    urls = "".join(
        f"  <url><loc>{SITE_URL}/p/{id_}</loc><lastmod>{lastmod}</lastmod></url>\n"
        for id_, _t, lastmod, _b in pages)
    (out_p / "sitemap.xml").write_text(SITEMAP.format(urls=urls), encoding="utf-8")
    rows = "".join(
        f'<li><a href="/p/{id_}">{esc(t)}</a> '
        f'<span class="pi-date">{esc(human_date(d))} · {esc(TRACKER.get(b, ""))}</span></li>\n'
        for id_, t, d, b in sorted(pages, key=lambda x: x[2], reverse=True))
    (out_p / "index.html").write_text(
        INDEX.format(rows=rows, n=written, SITE_URL=SITE_URL, NAV=NAV), encoding="utf-8")
    log.info("wrote %d post pages + sitemap + index to %s", written, out_p)

    # ── /b/ BILL PAGES + per-polity index + the bill sitemap. This is the
    # INDEXABLE unit (bounded by bills that move, not by time). Written under a
    # SEPARATE tree (/b/) from the app's own web export (bill/[ref].html) so the
    # two never collide (SEO plan Gate 1: /b/, decided).
    out_b = out_root / "b"
    for polity, _ref, slug, _canon, _title, _iso, bill in bill_records:
        d = out_b / polity
        d.mkdir(parents=True, exist_ok=True)
        (d / f"{slug}.html").write_text(render_bill(bill, glyphs_mode), encoding="utf-8")
    by_polity: dict = {}
    for rec_ in bill_records:
        by_polity.setdefault(rec_[0], []).append(rec_)
    for polity, items in by_polity.items():
        items.sort(key=lambda x: x[5], reverse=True)   # most recently active first
        L = legislature(polity)
        li = "".join(
            f'<li><a href="/b/{polity}/{slug}"><span class="bi-ref">{esc(ref)}</span>'
            + (f' <span class="bi-title">{esc(title)}</span>' if title else "")
            + f'</a><span class="bi-date">Latest action {esc(human_date(latest_iso))}</span></li>\n'
            for polity, ref, slug, _c, title, latest_iso, _b in items)
        robots = "" if INDEX_BILL_PAGES else '<meta name="robots" content="noindex">\n'
        (out_b / polity / "index.html").write_text(BILL_INDEX.format(
            bills_label=esc(L["bills_label"]), noun=esc(L["noun"]), leg_name=esc(L["name"]),
            n=len(items), rows=li, robots=robots, accent=L["accent"],
            polity=polity, SITE_URL=SITE_URL, NAV=NAV, FOOTER=FOOTER), encoding="utf-8")

    bill_urls = "".join(
        f"  <url><loc>{canon}</loc><lastmod>{iso}</lastmod></url>\n"
        for _p, _r, _s, canon, _t, iso, _b in sorted(bill_records, key=lambda x: x[5], reverse=True))
    (out_root / "bill-sitemap.xml").write_text(SITEMAP.format(urls=bill_urls), encoding="utf-8")
    log.info("wrote %d bill pages + %d index(es) + bill-sitemap (indexable=%s)",
             len(bill_records), len(by_polity), INDEX_BILL_PAGES)

    # ── SUPPRESSION MANIFESTS for the workflow's PRECISE shrink guards. A page or
    # bill in the committed tree but absent from this render is EITHER a sanctioned
    # remove-duplicate OR an upstream gap; the workflow tells them apart by a
    # SET-DIFF against these exact lists — no fuzzy count that could over-count a
    # free-text "remove-duplicate" or mask a real shrink (guard finding, 2026-08-17).
    # Written to <out> root, never published (the workflow copies only p/, b/,
    # bill-sitemap.xml). Dotfiles so a stray-file guard would ignore them anyway.
    suppressed_pages = sorted(r["_id"] for r in recs if r.get("_hidden"))
    # A bill slug is suppressed iff it would exist from ALL adaptable posts but not
    # from the kept grouping — i.e. every one of its posts was hidden.
    would_be: set = set()
    for r in recs:
        p = adapt_post(r)
        if not p or p["postType"] != "status" or not (p.get("reference") or "").strip():
            continue
        ident0 = bill_identity(p["polity"], p["reference"], p.get("congress"))
        if ident0:
            would_be.add((p["polity"], ident0["slug"]))
    suppressed_bills = sorted(f"{pol}/{slug}" for pol, slug in would_be - set(bills.keys()))
    (out_root / ".suppressed-pages").write_text(
        "".join(f"{x}\n" for x in suppressed_pages), encoding="utf-8")
    (out_root / ".suppressed-bills").write_text(
        "".join(f"{x}\n" for x in suppressed_bills), encoding="utf-8")


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
                    help="output root (pages go to <out>/p/ and <out>/b/). REQUIRED — a "
                         "bare run used to default to the sibling PUBLIC site repo and "
                         "rendered the SAMPLE fixtures into the deploy tree (adversarial "
                         "review 2026-08-16); the sample-fed local preview must be pointed "
                         "at a throwaway dir.")
    ap.add_argument("--paths", type=Path, default=None,
                    help="directory of bill-path artifacts (paths/*.json, the same files "
                         "the app's path-client reads). Optional: a bill with no artifact "
                         "renders from its posted milestones alone (the app does the same).")
    ap.add_argument("--glyphs", choices=("emoji", "svg"), default="emoji",
                    help="status-label rendering on BILL pages: 'emoji' (default, matches "
                         "the archived /p/ post text) or 'svg' (the app's icon language). "
                         "A Gate-2 option — the owner picks; /p/ pages always keep emoji.")
    ap.add_argument("--list-paths", action="store_true",
                    help="print (one per line) the bill-path artifact filenames the feed "
                         "needs, then exit WITHOUT rendering. The workflow uses this to fetch "
                         "exactly those from the feed host before the render pass.")
    a = ap.parse_args()

    feed = a.feed or [here / "sample-feed.jsonl"]
    if a.list_paths:
        for name in needed_path_files(feed):
            print(name)
        return
    overrides = list(a.overrides or [])
    if not a.overrides:
        # feed dirs: pick up the per-bot sheets the bots publish; the sample
        # run: its own fixture.
        for p in feed:
            if p.is_dir():
                overrides += sorted(p.glob("*-overrides.jsonl"))
        if not a.feed:
            overrides = [here / "sample-overrides.jsonl"]
    build(feed, [o for o in overrides if o.is_file()], a.out,
          paths_dir=a.paths, glyphs_mode=a.glyphs)


if __name__ == "__main__":
    main()
