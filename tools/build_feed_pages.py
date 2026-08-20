#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Render the feed pages (/us, /eu) from ONE template.

    python tools/build_feed_pages.py            # writes us.html, eu.html
    python tools/build_feed_pages.py --check    # exit 1 if either is stale

Standard library only, like tools/generate.py.

WHY A GENERATOR FOR TWO PAGES. Because there will not be two. The web-overhaul
plan's amendment 2 says a legislature is a REGISTRY ROW — id, names, vote
vocabulary, reference grammar, accent, explainer link, feed location — consumed
by the app, the web and the generator, so that adding a legislature is data
rather than a fifth copy of the same table. This script is the web end of that:
one template per registry entry, and the registry below is a placeholder that
moves into `bt-core` when the core lands (see assets/js/README.md).

WHAT THE COPY IS ALLOWED TO SAY. Every claim here is checked against the
published site pages:

  * "checked every hour" is a US-only claim (index.html:80). The EU line uses
    the site's own EU wording (index.html:111) and makes no cadence claim.
  * no "complete history" — the archive starts 2026-07.
  * no "complete path", no notification promises.
  * titles, descriptions and OG carry no "live"/"real time" superlative;
    "as it moves" is the house phrase.
  * THE WINDOW CLAIMS (D30, owner 2026-08-20). The intro names the session
    window the feed covers, and the tracking-start date scopes what is IN it —
    the two sentences travel together, because we joined mid-session and
    "covers the 119th" alone would read as completeness back to January 2025.
    The dates are the published record's own first posts (us-2026-07.jsonl:
    2026-07-16; eu-2026-07.jsonl: 2026-07-17 — verified 2026-08-20), not the
    bots' X launch. Only the US line may promise a reset: US bills die with
    their Congress, while EU files are often RESUMED across terms under their
    original codes, so the EU window keys on last activity and a "resets in
    2029" would be false (AGENTS.md, EU WINDOW NUANCE). ⏰ At the 120th's
    convening (2027-01-03) the US row's window sentence must be re-dated —
    filed with the rollover cluster in the app repo's OPEN-ITEMS.

Do not add a claim to this file without the same check.
"""

from __future__ import annotations

import argparse
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "tools" / "templates" / "feed-page.html"
# BUILD INPUT, NOT AN ASSET. It lived at assets/glyphs.svg first, which put a
# public URL on a file that provably does not work when it is linked (see the
# note below) — an invitation to a silent failure. Nothing fetches it; this
# script pastes it.
SPRITE = ROOT / "tools" / "glyphs.svg"

# Pages that draw cards need the glyph sprite in the document. It is INLINED,
# not linked: an external <use href="/assets/glyphs.svg#id"> fetches 200 and
# still fails to instantiate the symbol (measured 2026-08-19, same-origin, with
# and without a CSP, from static markup — bbox 0×0, no console error). A glyph
# that can silently disappear is not something this product ships, so the sprite
# is pasted between these markers and every reference is a bare `#id`.
SPRITE_START = "<!-- BT-SPRITE:START"
SPRITE_END = "<!-- BT-SPRITE:END -->"

# Hand-authored pages that also draw cards and therefore carry the same block.
SPRITE_PAGES = ["404.html"]

# --------------------------------------------------------------------------
# The registry. Interim home: this table moves into bt-core (the one
# legislature registry the app, the web and the generator all read) and this
# script will import it from the built view instead of declaring it.
#
# ⚠️ IT IS A SECOND REGISTRY UNTIL THEN, AND A CHECK HOLDS IT EQUAL. The app's
# `scripts/check-site-nav.js` parses this table and compares it, row by row,
# against `src/data/legislatures.ts` — the id set and its ORDER (a legislature in
# the registry with no feed page is a page this script owes), the names, the
# accent hex and the explainer path. Adding a legislature there and forgetting it
# here now fails `npm run check` instead of quietly shipping one feed page for a
# two-legislature build (estate review, 2026-08-20).
#
# What the check deliberately does NOT compare is the PROSE — intro, title,
# og_title, description, explainer_label. Those are this page's own copy, the
# registry has no field for them, and inventing one so a check could compare it
# would put marketing sentences in the app's data layer. They are governed by the
# copy law in this file's docstring instead.
#
# The mapping, so the two tables can be read side by side:
#     polity_name  = names.formal      eyebrow      = f"{names.short} tracker"
#     h1           = f"The {names.short} feed"      accent  = theme C[accent.blue]
#     explainer_url = explainerPath                 og_image = SITE/assets/<id>-banner.webp
# --------------------------------------------------------------------------

LEGISLATURES: dict[str, dict[str, str]] = {
    "us": {
        "polity_name": "US Congress",
        "eyebrow": "US tracker",
        "h1": "The US feed",
        # FEED, NOT DATABASE (owner law 2026-08-20): the intro says what this IS —
        # a live feed with a stated start date — never an archive's promise. The
        # old line ("Every recorded step…") read as a completeness claim over all
        # of history; a reader hunting an old bill would blame our record, not
        # our scope. Bill pages ARE complete per bill, and the intro says so.
        # The window sentence is D30's (see the docstring's WINDOW CLAIMS law).
        "intro": (
            "A live feed of the US Congress — bills as they move, from the "
            "official record at Congress.gov. The feed covers the 119th "
            "Congress (January 2025 – January 2027) and resets with the "
            "120th; tracking since 16 July 2026. Each bill's page carries "
            "its complete official path."
        ),
        "explainer_url": "/us-process",
        "explainer_label": "How a bill becomes law",
        "accent": "#0A3161",
        "title": "The US feed — Congress as it moves | BillTracking",
        "og_title": "The US feed — Congress as it moves",
        "description": (
            "A live feed of the US Congress — bills as they move, from the "
            "official record at Congress.gov. Covering the 119th Congress; "
            "tracking since 16 July 2026."
        ),
        "og_image": "https://billtracking.org/assets/us-banner.webp",
    },
    "eu": {
        # The registry's `names.formal` — the institution, formally, which is the
        # register the sentence this fills needs ("… in the <name> bill index",
        # beside "US Congress" on the other page). It read "EU" until 2026-08-20,
        # which was `names.short` doing a formal name's job: the two rows
        # answered one question in two different registers, and neither the app
        # nor a check could tell which was intended.
        "polity_name": "European Union",
        "eyebrow": "EU tracker",
        "h1": "The EU feed",
        # No reset promise here, deliberately — EU files are often resumed
        # across terms under their original codes (the docstring's WINDOW
        # CLAIMS law), so this row names the term and stops.
        "intro": (
            "A live feed of EU lawmaking — procedures as they move through the "
            "European Parliament and the Council, from the EU's official "
            "registers, in plain English. The feed covers the 10th "
            "parliamentary term (2024–2029); tracking since 17 July 2026. "
            "Each file's page carries its complete path."
        ),
        "explainer_url": "/eu-process",
        "explainer_label": "How an EU law is made",
        "accent": "#003399",
        "title": "The EU feed — EU lawmaking as it moves | BillTracking",
        "og_title": "The EU feed — EU lawmaking as it moves",
        "description": (
            "A live feed of EU lawmaking as it moves through the "
            "European Parliament and the Council — from the EU's official "
            "registers. Covering the 10th parliamentary term; tracking "
            "since 17 July 2026."
        ),
        "og_image": "https://billtracking.org/assets/eu-banner.webp",
    },
}

CURRENT = ' aria-current="page"'


def esc(value: str) -> str:
    """HTML-escape a registry value.

    The whole point of this file is that a legislature is a REGISTRY ROW. A row
    is written by a person, and the first row containing an ampersand ("Justice
    & Home Affairs"), a quote or an angle bracket would otherwise walk straight
    into an attribute and break the page silently. Every attribute here is
    double-quoted, so `&<>"` is the complete set; the apostrophe is left alone
    to keep the rendered HTML readable.
    """
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def paste_sprite(html: str, sprite: str, where: str) -> str:
    """Replace whatever sits between the BT-SPRITE markers with the sprite."""
    i = html.find(SPRITE_START)
    j = html.find(SPRITE_END)
    if i < 0 or j < 0 or j < i:
        raise SystemExit("%s: BT-SPRITE markers missing or out of order" % where)
    head_end = html.index("-->", i) + len("-->")
    return html[:head_end] + "\n" + sprite.rstrip("\n") + "\n" + html[j:]


def render(polity: str, entry: dict[str, str], template: str) -> str:
    # Registry text is escaped; the two computed values are MARKUP this script
    # writes itself and are the only things allowed through raw.
    fields = {
        "POLITY": esc(polity),
        "POLITY_NAME": esc(entry["polity_name"]),
        "EYEBROW": esc(entry["eyebrow"]),
        "H1": esc(entry["h1"]),
        "INTRO": esc(entry["intro"]),
        "EXPLAINER_URL": esc(entry["explainer_url"]),
        "EXPLAINER_LABEL": esc(entry["explainer_label"]),
        "ACCENT": esc(entry["accent"]),
        "TITLE": esc(entry["title"]),
        "OG_TITLE": esc(entry["og_title"]),
        "DESCRIPTION": esc(entry["description"]),
        "OG_IMAGE": esc(entry["og_image"]),
        # ONE "Feed" nav entry, and EVERY page this script renders is a feed
        # page, so it always carries aria-current (SEARCH-JOB-SPEC section 7).
        # The link's href is the FIRST registry entry's feed for every one of
        # them - which is why the current page is marked by the attribute
        # rather than by the address: on /eu the reader IS on the feed, and a
        # nav that said otherwise would be lying about where they are.
        "NAV_CURRENT_FEED": CURRENT,
    }
    out = template
    for key, value in fields.items():
        out = out.replace("{{%s}}" % key, value)
    left = [tok for tok in out.split("{{")[1:]]
    if left:
        raise SystemExit(
            "unfilled placeholder(s) in %s.html: %s"
            % (polity, ", ".join(sorted({t.split("}}")[0] for t in left})))
        )
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--check",
        action="store_true",
        help="do not write; exit 1 if any page differs from what the template renders",
    )
    args = ap.parse_args(argv)

    template = TEMPLATE.read_text(encoding="utf-8")
    sprite = SPRITE.read_text(encoding="utf-8")
    stale: list[str] = []

    for polity, entry in LEGISLATURES.items():
        target = ROOT / ("%s.html" % polity)
        html = paste_sprite(render(polity, entry, template), sprite, target.name)
        if args.check:
            current = target.read_text(encoding="utf-8") if target.exists() else ""
            if current != html:
                stale.append(target.name)
            continue
        target.write_text(html, encoding="utf-8", newline="\n")
        print("wrote %s (%d bytes)" % (target.name, len(html.encode("utf-8"))))

    # The hand-authored card-drawing pages keep the same sprite block, refreshed
    # in place — everything outside the markers is theirs and is left alone.
    for name in SPRITE_PAGES:
        target = ROOT / name
        current = target.read_text(encoding="utf-8")
        html = paste_sprite(current, sprite, name)
        if args.check:
            if current != html:
                stale.append(name)
            continue
        if html != current:
            target.write_text(html, encoding="utf-8", newline="\n")
            print("refreshed the sprite in %s" % name)

    if args.check:
        if stale:
            print("stale (re-run tools/build_feed_pages.py): %s" % ", ".join(stale))
            return 1
        print("feed pages up to date: %s (+ %s)"
              % (", ".join(sorted(LEGISLATURES)), ", ".join(SPRITE_PAGES)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
