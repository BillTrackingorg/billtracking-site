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
# --------------------------------------------------------------------------

LEGISLATURES: dict[str, dict[str, str]] = {
    "us": {
        "polity_name": "US Congress",
        "eyebrow": "US tracker",
        "h1": "The US feed",
        "intro": (
            "Every recorded step a bill takes in the US Congress — from the "
            "official record at Congress.gov, checked every hour."
        ),
        "explainer_url": "/us-process.html",
        "explainer_label": "How a bill becomes law",
        "accent": "#0A3161",
        "title": "The US feed — Congress as it moves | BillTracking",
        "og_title": "The US feed — Congress as it moves",
        "description": (
            "Every recorded step a bill takes in the US Congress, posted as it "
            "moves — from the official record at Congress.gov."
        ),
        "og_image": "https://billtracking.org/assets/us-banner.webp",
    },
    "eu": {
        "polity_name": "EU",
        "eyebrow": "EU tracker",
        "h1": "The EU feed",
        "intro": (
            "Every recorded step a legislative procedure takes through the "
            "European Parliament and the Council — from the EU's official "
            "registers, in plain English."
        ),
        "explainer_url": "/eu-process.html",
        "explainer_label": "How an EU law is made",
        "accent": "#003399",
        "title": "The EU feed — EU lawmaking as it moves | BillTracking",
        "og_title": "The EU feed — EU lawmaking as it moves",
        "description": (
            "Every recorded step an EU legislative procedure takes through the "
            "European Parliament and the Council, posted as it moves — from "
            "the EU's official registers."
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
        "NAV_CURRENT_US": CURRENT if polity == "us" else "",
        "NAV_CURRENT_EU": CURRENT if polity == "eu" else "",
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
