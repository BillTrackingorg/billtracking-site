#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Make the link-preview card every page of this website carries.

    python tools/make_og_card.py            # writes assets/og/billtracking-og-v1.png
    python tools/make_og_card.py --check    # exit 1 if the committed card differs

Needs Pillow and fontTools (both on the build machine; nothing here runs in a
workflow). The inputs live in the app repo, checked out beside this one
(Projects/BillTracking/{app,site}); pass --app to point elsewhere.

WHAT THE CARD IS (the owner's ruling, 2026-10-15; app OPEN-ITEMS OI-0315). One
card for every page, every legislature and every post: the white emblem and the
wordmark "BillTracking.org" on the product blue #05327D, the exact midpoint of
the US blue #0A3161 and the EU blue #003399 (app store-assets/README.md). Red is
the US and yellow is the EU, so neither appears here. No accent, no skyline and
no caption: a line baked into an image cannot be corrected once a platform has
cached the preview, and Apple's guidance for link previews (TN3156) says to
avoid text in preview images. The page's own title and description carry the
words. The page banners (us-banner.webp, eu-banner.webp) stay what they are,
page art; they are no page's preview any more.

THE GEOGRAPHY OF THE IMAGE. 1200x630 is the size the platforms document. X
shows a large card at 2:1, so it keeps the central 1200x600; an app that shows a
square thumbnail keeps the central 630x630. The lockup is placed so that both
keep all of it, and the script refuses to write a card where they would not:
the test is made on the ink actually drawn, not on the planned boxes.

THE WORDMARK is the site header's (style.css, `.wordmark`): Source Serif 4 at
700 in white, ".org" at 400 in #8FB4E3, letter-spacing 0.005em, kerned as a
browser kerns it (the font's own GPOS pair adjustments, read with fontTools,
because Pillow's basic layout does not apply them and this machine's Pillow has
no complex-layout engine). The kerning stops at the ".org" span, as it does in
a browser, because the two runs are two fonts.

THE NAME CARRIES A VERSION. A platform caches a preview by the image's URL, so a
changed card under the same name can keep showing the old one for weeks. When
the card changes, raise the number in OUT and in the app repo's
`src/data/share-card.ts` (every generated page's tags are built from that file,
and the app's check:sitenav holds this repo's pages and this file's OUT to it),
and keep the old file until no page points at it.

DETERMINISTIC. Same inputs, same Pillow, same bytes: nothing here reads the
clock or the environment, and the PNG carries no timestamp. --check proves it by
rendering in memory and comparing with the committed file.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import pathlib
import sys

from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "og" / "billtracking-og-v1.png"

W, H = 1200, 630
BLUE = "#05327D"        # the product blue (app store-assets/README.md)
WHITE = "#FFFFFF"
TLD = "#8FB4E3"         # style.css `.wordmark .tld`
LETTER_SPACING = 0.005  # style.css `.wordmark`, in em

# The lockup: the emblem above the wordmark, centred. The sizes are the design;
# the safe areas below are the rule they must obey.
EMBLEM_HEIGHT = 250
WORDMARK_SIZE = 70
GAP = 34                 # the emblem's ink to the wordmark's cap height
X_CROP = 600             # X's large card keeps the central 1200x600
SQUARE = (W - H) // 2    # the central 630x630 starts here
SAFE_MARGIN = 24         # breathing room inside the square crop
MAX_BYTES = 300 * 1024


def inputs(app: pathlib.Path) -> dict[str, pathlib.Path]:
    fonts = app / "node_modules" / "@expo-google-fonts" / "source-serif-4"
    return {
        "emblem": app / "store-assets" / "emblem-white.png",
        "bold": fonts / "700Bold" / "SourceSerif4_700Bold.ttf",
        "regular": fonts / "400Regular" / "SourceSerif4_400Regular.ttf",
    }


class Run:
    """One run of text in one font, laid out as a browser lays it out: the
    font's own advances, its GPOS pair kerning and the CSS letter-spacing
    (which a browser adds after every character, the last one included)."""

    def __init__(self, path: pathlib.Path, size: int, text: str, fill: str):
        self.text, self.fill, self.size = text, fill, size
        self.pil = ImageFont.truetype(str(path), size, layout_engine=ImageFont.Layout.BASIC)
        tt = TTFont(str(path))
        self.scale = size / tt["head"].unitsPerEm
        cmap = tt.getBestCmap()
        glyphs = [cmap[ord(c)] for c in text]
        hmtx = tt["hmtx"]
        kern = _kerning(tt)
        spacing = LETTER_SPACING * size
        self.xs: list[float] = []
        x = 0.0
        for i, g in enumerate(glyphs):
            self.xs.append(x)
            x += hmtx[g][0] * self.scale + spacing
            if i + 1 < len(glyphs):
                x += kern(g, glyphs[i + 1]) * self.scale
        self.width = x

    def ink(self, x0: float, baseline: float) -> tuple[float, float, float, float]:
        """The run's ink box when its first glyph starts at x0 on `baseline`."""
        boxes = [self.pil.getbbox(c, anchor="ls") for c in self.text]
        return (
            x0 + min(self.xs[i] + b[0] for i, b in enumerate(boxes)),
            baseline + min(b[1] for b in boxes),
            x0 + max(self.xs[i] + b[2] for i, b in enumerate(boxes)),
            baseline + max(b[3] for b in boxes),
        )

    def draw(self, d: ImageDraw.ImageDraw, x0: float, baseline: float) -> None:
        # One glyph at a time, each at its kerned (fractional) position; Pillow
        # keeps the fraction, so nothing is snapped to whole pixels.
        for c, x in zip(self.text, self.xs):
            d.text((x0 + x, baseline), c, font=self.pil, fill=self.fill, anchor="ls")


def _kerning(tt: TTFont):
    """GPOS pair adjustment (x advance, font units) from the `kern` feature's
    lookups. Each lookup contributes once, through the first of its subtables
    that applies to the pair: a format-1 subtable applies only when it holds a
    record for the pair, a format-2 subtable whenever it covers the first glyph
    — the rule a shaper applies."""
    if "GPOS" not in tt:
        return lambda a, b: 0
    gpos = tt["GPOS"].table
    indices = sorted({i for fr in gpos.FeatureList.FeatureRecord if fr.FeatureTag == "kern"
                      for i in fr.Feature.LookupListIndex})
    lookups = [gpos.LookupList.Lookup[i] for i in indices]

    def subtables(lookup):
        for st in lookup.SubTable:
            if lookup.LookupType == 9:          # an extension wrapper
                if st.ExtensionLookupType != 2:
                    continue
                st = st.ExtSubTable
            elif lookup.LookupType != 2:        # not pair adjustment
                continue
            yield st

    def value(st, a: str, b: str) -> int | None:
        if a not in st.Coverage.glyphs:
            return None
        if st.Format == 1:
            for rec in st.PairSet[st.Coverage.glyphs.index(a)].PairValueRecord:
                if rec.SecondGlyph == b:
                    return (getattr(rec.Value1, "XAdvance", 0) or 0) if rec.Value1 else 0
            return None  # no record for this pair: the next subtable may have one
        c1 = st.ClassDef1.classDefs.get(a, 0)
        c2 = st.ClassDef2.classDefs.get(b, 0)
        v = st.Class1Record[c1].Class2Record[c2].Value1
        return (getattr(v, "XAdvance", 0) or 0) if v else 0

    def kern(a: str, b: str) -> int:
        total = 0
        for lookup in lookups:
            for st in subtables(lookup):
                v = value(st, a, b)
                if v is not None:
                    total += v
                    break
        return total

    return kern


def render(app: pathlib.Path) -> tuple[bytes, dict[str, object]]:
    src = inputs(app)
    missing = [str(p) for p in src.values() if not p.exists()]
    if missing:
        raise SystemExit("missing input(s) - is the app repo checked out beside this one?\n  "
                         + "\n  ".join(missing))

    emblem = Image.open(src["emblem"])
    if emblem.mode != "RGBA":
        raise SystemExit("the emblem is %s, not RGBA - the card needs the transparent white mark" % emblem.mode)
    emblem = emblem.crop(emblem.getbbox())
    ew = round(emblem.width * EMBLEM_HEIGHT / emblem.height)
    emblem = emblem.resize((ew, EMBLEM_HEIGHT), Image.Resampling.LANCZOS)

    name = Run(src["bold"], WORDMARK_SIZE, "BillTracking", WHITE)
    tld = Run(src["regular"], WORDMARK_SIZE, ".org", TLD)
    word_w = name.width + tld.width

    # Vertical: centre the INK of the whole lockup — the emblem's top to the
    # wordmark's descender — on the card's middle line.
    cap_top = name.ink(0, 0)[1]            # negative: the cap height above the baseline
    descent = max(name.ink(0, 0)[3], tld.ink(0, 0)[3])
    block = EMBLEM_HEIGHT + GAP + (-cap_top) + descent
    top = round((H - block) / 2)
    baseline = top + EMBLEM_HEIGHT + GAP + (-cap_top)
    word_x = (W - word_w) / 2
    emblem_x = (W - ew) // 2

    im = Image.new("RGB", (W, H), BLUE)
    im.paste(emblem, (emblem_x, top), emblem)
    d = ImageDraw.Draw(im)
    name.draw(d, word_x, baseline)
    tld.draw(d, word_x + name.width, baseline)

    # THE SAFE AREAS, enforced on the ink actually drawn rather than on the plan.
    ink = _union(
        (emblem_x, top, emblem_x + ew, top + EMBLEM_HEIGHT),
        name.ink(word_x, baseline),
        tld.ink(word_x + name.width, baseline),
    )
    x_crop = (0, (H - X_CROP) / 2, W, (H + X_CROP) / 2)
    square = (SQUARE + SAFE_MARGIN, SAFE_MARGIN, SQUARE + H - SAFE_MARGIN, H - SAFE_MARGIN)
    for label, box in (("X's 2:1 crop (central 1200x600)", x_crop),
                       ("the square crop (central 630x630, less the margin)", square)):
        if not _inside(ink, box):
            raise SystemExit("the lockup %s leaves %s %s - refusing to write it" % (
                tuple(round(v, 1) for v in ink), label, box))

    buf = io.BytesIO()
    im.save(buf, format="PNG", optimize=True)
    data = buf.getvalue()
    if len(data) > MAX_BYTES:
        raise SystemExit("the card is %d bytes, over the %d budget" % (len(data), MAX_BYTES))
    return data, {"lockup_ink": tuple(round(v, 1) for v in ink), "wordmark_width": round(word_w, 1)}


def _union(*boxes):
    return (min(b[0] for b in boxes), min(b[1] for b in boxes),
            max(b[2] for b in boxes), max(b[3] for b in boxes))


def _inside(inner, outer) -> bool:
    return (inner[0] >= outer[0] and inner[1] >= outer[1]
            and inner[2] <= outer[2] and inner[3] <= outer[3])


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--app", type=pathlib.Path, default=ROOT.parent / "app",
                    help="the app repo (default: beside this one)")
    ap.add_argument("--check", action="store_true",
                    help="do not write; exit 1 if the committed card differs from a fresh render")
    args = ap.parse_args(argv)

    data, facts = render(args.app.resolve())
    digest = hashlib.sha256(data).hexdigest()[:16]
    rel = OUT.relative_to(ROOT).as_posix()
    if args.check:
        current = OUT.read_bytes() if OUT.exists() else b""
        if current != data:
            print("stale: %s does not match a fresh render (%d bytes, sha256 %s...) - re-run "
                  "tools/make_og_card.py" % (rel, len(data), digest))
            return 1
        print("card up to date: %s (%d bytes, sha256 %s...)" % (rel, len(data), digest))
        return 0
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_bytes(data)
    print("wrote %s (%d bytes, sha256 %s...; lockup ink %s, wordmark %spx wide)"
          % (rel, len(data), digest, facts["lockup_ink"], facts["wordmark_width"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
