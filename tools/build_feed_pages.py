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
moves into `bt-core` when the core lands (see the app repo's docs/WEB-CONTRACT.md).

WHAT THE COPY IS ALLOWED TO SAY. Every claim here is checked against the
published site pages:

  * "checked every hour" is a US-only claim (index.html:80). The EU line uses
    the site's own EU wording (index.html:111) and makes no cadence claim.
  * no "complete history" — the archive starts 2026-07.
  * no "complete path", no notification promises.
  * titles, descriptions and OG carry no "live"/"real time" superlative;
    "as it moves" is the house phrase.
    [2026-10-15, app OPEN-ITEMS OI-0315 — the owner's site line "A live, source-linked
    record of lawmaking" is the OG description of every feed page (the template), by his
    ruling that night ("keep the word live"); this file's own titles said "A live feed"
    before that. The rule holds otherwise.]
  * THE SESSION CLAIMS (D30). The intro names the session the feed is in
    now, and the tracking-start date scopes what is in it: the two travel
    together, because we joined mid-session and the session's name alone
    would read as completeness back to its start. The dates are the
    published record's own first posts (us-2026-07.jsonl: 2026-07-16;
    eu-2026-07.jsonl: 2026-07-17), not the bots' X launch. "Now in", never
    "covers", and no reset: where a session changes the feed shows a
    heading. The page fills the session line from the registry
    (#bt-window); the words here are its fallback without JavaScript and
    name no session ("Now in the current Congress"), so they never go
    stale. The meta description takes the same neutral words.

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
# What the check deliberately does NOT compare is the PROSE — intro, window,
# title, og_title, description, explainer_label. Those are this page's own
# copy, the registry has no field for them, and inventing one so a check could
# compare it would put marketing sentences in the app's data layer. They are
# governed by the copy law in this file's docstring instead.
#
# The mapping, so the two tables can be read side by side:
#     polity_name  = names.formal      eyebrow      = f"{names.short} tracker"
#     h1           = f"The {names.short} feed"      accent  = theme C[accent.blue]
#     explainer_url = explainerPath
#
# THE LINK PREVIEW IS NOT A ROW FIELD (the owner's ruling, 2026-10-15; app
# OPEN-ITEMS OI-0315: one card for every page, every legislature). Each row
# carried `og_image` (SITE/assets/<id>-banner.webp, the legislature's banner)
# until then; the card, its size and alt text, `og:site_name` and the site line
# (`og:description`) are written in the template, the same on every feed page,
# and the app's check:sitenav holds them to the app's `src/data/share-card.ts`.
# The row's `description` stays the page's meta description, the search snippet.
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
        # The session line is D30's (see the docstring's SESSION CLAIMS law):
        # {window} is where it stands, in the span the page fills (intro_html).
        "intro": (
            "A live feed of the US Congress — bills as they move, from the "
            "official record at Congress.gov. {window}; tracking since 16 "
            "July 2026. Each bill's page carries its complete official path."
        ),
        # OI-0211: provisional wording, the owner's copy pass
        "window": "Now in the current Congress",
        "explainer_url": "/us-process",
        "explainer_label": "How a bill becomes law",
        "accent": "#0A3161",
        "title": "The US feed — Congress as it moves | BillTracking",
        "og_title": "The US feed — Congress as it moves",
        # OI-0211: provisional wording, the owner's copy pass
        "description": (
            "A live feed of the US Congress — bills as they move, from the "
            "official record at Congress.gov. Now in the current Congress; "
            "tracking since 16 July 2026."
        ),
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
        # No reset promise (the docstring's SESSION CLAIMS law). This row never
        # made one: EU files are often resumed across terms under their
        # original codes.
        "intro": (
            "A live feed of EU lawmaking — procedures as they move through the "
            "European Parliament and the Council, from the EU's official "
            "registers, in plain English. {window}; tracking since 17 July "
            "2026. Each file's page carries its complete path."
        ),
        # OI-0211: provisional wording, the owner's copy pass
        "window": "Now in the current parliamentary term",
        "explainer_url": "/eu-process",
        "explainer_label": "How an EU law is made",
        "accent": "#003399",
        "title": "The EU feed — EU lawmaking as it moves | BillTracking",
        "og_title": "The EU feed — EU lawmaking as it moves",
        # OI-0211: provisional wording, the owner's copy pass
        "description": (
            "A live feed of EU lawmaking as it moves through the "
            "European Parliament and the Council — from the EU's official "
            "registers. Now in the current parliamentary term; tracking "
            "since 17 July 2026."
        ),
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


WINDOW_MARK = "{window}"


def intro_html(polity: str, entry: dict[str, str]) -> str:
    """The intro, escaped, with its session line in the span the page fills.

    The feed page writes the session in force into `#bt-window` from the
    registry (the app's `sessionWindowNow`, src/data/sessions.ts), so it
    re-dates itself. The row's `window` is what the span holds until then,
    and for a reader without JavaScript. The row's intro marks where it
    stands with {window}, exactly once.
    """
    before, mark, after = entry["intro"].partition(WINDOW_MARK)
    if not mark or WINDOW_MARK in after:
        raise SystemExit("%s: the intro must carry %s exactly once"
                         % (polity, WINDOW_MARK))
    return '%s<span id="bt-window">%s</span>%s' % (
        esc(before), esc(entry["window"]), esc(after))


def paste_sprite(html: str, sprite: str, where: str) -> str:
    """Replace whatever sits between the BT-SPRITE markers with the sprite."""
    i = html.find(SPRITE_START)
    j = html.find(SPRITE_END)
    if i < 0 or j < 0 or j < i:
        raise SystemExit("%s: BT-SPRITE markers missing or out of order" % where)
    head_end = html.index("-->", i) + len("-->")
    return html[:head_end] + "\n" + sprite.rstrip("\n") + "\n" + html[j:]


def render(polity: str, entry: dict[str, str], template: str) -> str:
    # Registry text is escaped; the markup this script writes itself (the
    # intro's #bt-window span and the nav's aria-current) is the only thing
    # allowed through raw.
    fields = {
        "POLITY": esc(polity),
        "POLITY_NAME": esc(entry["polity_name"]),
        "EYEBROW": esc(entry["eyebrow"]),
        "H1": esc(entry["h1"]),
        "INTRO": intro_html(polity, entry),
        "EXPLAINER_URL": esc(entry["explainer_url"]),
        "EXPLAINER_LABEL": esc(entry["explainer_label"]),
        "ACCENT": esc(entry["accent"]),
        "TITLE": esc(entry["title"]),
        "OG_TITLE": esc(entry["og_title"]),
        "DESCRIPTION": esc(entry["description"]),
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
