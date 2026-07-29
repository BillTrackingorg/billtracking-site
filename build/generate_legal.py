#!/usr/bin/env python3
"""
generate_legal.py — one source, two renderers for the legal pages.

The problem this solves (owner directive 2026-07-30): the privacy and terms
text used to live in two hand-maintained copies — long-form drafts in the app
repo and shorter hand-written HTML here — with nothing keeping them in sync.
Edit one, the other silently goes stale. This generator makes the Markdown in
`legal/*.md` the SINGLE SOURCE OF TRUTH and renders it into both places:

  legal/privacy.md ──> privacy.html            (this site, full chrome)
                  └──> ../app/src/data/legal/privacy.generated.ts
                                                (the app's in-app screen)

So updating a policy is: edit the .md, run this script, commit both repos.
One parser here means the two renderings can never drift.

Grammar (kept deliberately tiny, stdlib-only — matching generate.py's zero-dep
style; the full spec with examples is legal/LEGAL-SPEC.md):

  --- front-matter ---     slug / title / eyebrow / htmlTitle / description /
                           ogTitle / ogDescription / updated  (# = comment)
  first paragraph          the hero lede
  ^Kicker                  optional eyebrow label for the NEXT section
  ## Heading               starts a section (site <h2>)
  ### Subheading           an <h3> inside the current section
  - item                   a bullet in a "principles" list
  > text                   a callout box  (>! = the gold "important" variant)
  plain text               a paragraph
  inline: **bold**  *italic*  [text](href)   ([**bold link**](href) also works)

  Blocks BEFORE the first `##` form a heading-less lead section (the "What
  exists today" notice on the privacy page).

Presentation is each renderer's job (mirrors the app's D16): the alternating
section tint on the site is applied HERE from section order, and is NOT encoded
in the source; the app ignores it and the per-section eyebrow entirely.

Usage:
    python generate_legal.py                 # site + app (auto-detects siblings)
    python generate_legal.py --site-out DIR --app-out DIR
    python generate_legal.py --no-app        # site only
"""
from __future__ import annotations

import argparse
import html
import json
import logging
import re
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger("generate_legal")

SITE_URL = "https://billtracking.org"
OG_IMAGE = f"{SITE_URL}/assets/us-banner.webp"

# In-app links: cross-links to our own privacy/terms open the native screens;
# every other relative page opens its published web version; schemes pass through.
APP_ROUTE = {"privacy.html": "/privacy", "terms.html": "/terms"}


# --------------------------------------------------------------------------- #
#  Parsing  (Markdown source -> structured document)
# --------------------------------------------------------------------------- #
# The href group allows ONE level of nested parentheses so URLs like EUR-Lex
# `.../833(1)/oj` survive — a plain `[^)]+` would truncate the href at the first
# inner `)` and dump the tail as literal text (silent dead link).
_INLINE = re.compile(
    r"\*\*(.+?)\*\*|\*(.+?)\*|\[([^\]]+)\]\(((?:[^()]|\([^()]*\))+)\)")
_BOLD_LABEL = re.compile(r"^\*\*(.+)\*\*$")


def parse_inline(text: str) -> list[dict]:
    """A line of prose -> a list of runs: {text, bold?, em?, href?}."""
    runs: list[dict] = []
    pos = 0
    for m in _INLINE.finditer(text):
        if m.start() > pos:
            runs.append({"text": text[pos:m.start()]})
        bold, em, link_text, href = m.groups()
        if bold is not None:
            runs.append({"text": bold, "bold": True})
        elif em is not None:
            runs.append({"text": em, "em": True})
        else:  # link — a wholly-bold label ([**x**](url)) keeps its bold
            bm = _BOLD_LABEL.match(link_text)
            run = {"text": bm.group(1) if bm else link_text, "href": href}
            if bm:
                run["bold"] = True
            runs.append(run)
        pos = m.end()
    if pos < len(text):
        runs.append({"text": text[pos:]})
    return runs


def _special(line: str) -> bool:
    s = line.strip()
    return (s.startswith("^") or s.startswith("## ") or s.startswith("### ")
            or s.startswith("- ") or s.startswith(">"))


def parse_front_matter(text: str) -> tuple[dict, str]:
    """Returns (meta, body). Front-matter is the block between the first two
    `---` fences; `#` lines inside it are comments."""
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.DOTALL)
    if not m:
        raise ValueError("missing --- front-matter block")
    meta: dict = {}
    for line in m.group(1).splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        key, _, val = line.partition(":")
        meta[key.strip()] = val.strip()
    return meta, m.group(2)


def parse_body(body: str) -> tuple[list[dict], list[dict]]:
    """Returns (lede_runs, sections). A section is
    {eyebrow, heading, blocks[]}; heading is None for the lead notice."""
    lines = body.split("\n")
    n = len(lines)
    i = 0
    while i < n and not lines[i].strip():
        i += 1
    lede_lines = []
    while i < n and lines[i].strip() and not _special(lines[i]):
        lede_lines.append(lines[i].strip())
        i += 1
    lede = parse_inline(" ".join(lede_lines))

    sections: list[dict] = []
    current = {"eyebrow": None, "heading": None, "blocks": []}
    pending_eyebrow = None

    def flush():
        if current["heading"] is not None or current["blocks"]:
            sections.append(current)

    while i < n:
        s = lines[i].strip()
        if not s:
            i += 1
            continue
        # Fail loud on markers that look like a typo rather than silently
        # emitting them as body text (a mistyped heading would also drop a
        # section and flip every later section's tint).
        if s.startswith("#") and not (s.startswith("## ") or s.startswith("### ")):
            raise ValueError(f"heading must be '## ' or '### ' (with a space): {s!r}")
        if re.match(r"^-\S", s):
            raise ValueError(f"list item must start with '- ' (with a space): {s!r}")
        if s.startswith("^"):
            # an eyebrow kicker only makes sense directly above its heading;
            # otherwise it would leak onto a later section or vanish silently
            j = i + 1
            while j < n and not lines[j].strip():
                j += 1
            if j >= n or not lines[j].strip().startswith("## "):
                raise ValueError(
                    f"'^{s[1:].strip()}' must be immediately followed by a '## ' heading")
            pending_eyebrow = s[1:].strip()
            i += 1
        elif s.startswith("## "):
            flush()
            current = {"eyebrow": pending_eyebrow, "heading": s[3:].strip(),
                       "blocks": []}
            pending_eyebrow = None
            i += 1
        elif s.startswith("### "):
            current["blocks"].append(
                {"kind": "subheading", "runs": parse_inline(s[4:].strip())})
            i += 1
        elif s.startswith("- "):
            items = []
            while i < n and lines[i].strip().startswith("- "):
                items.append(parse_inline(lines[i].strip()[2:].strip()))
                i += 1
            current["blocks"].append({"kind": "list", "items": items})
        elif s.startswith(">"):
            # consecutive `>` lines fold into ONE callout paragraph (so a
            # hard-wrapped quote is not split into stray <p>s — matches how
            # plain paragraphs fold)
            variant = "gold" if s.startswith(">!") else "default"
            texts = []
            while i < n and lines[i].strip().startswith(">"):
                t = lines[i].strip()
                t = t[2:] if t.startswith(">!") else t[1:]
                texts.append(t.strip())
                i += 1
            current["blocks"].append(
                {"kind": "callout", "variant": variant,
                 "paras": [parse_inline(" ".join(texts))]})
        else:
            para_lines = []
            while i < n and lines[i].strip() and not _special(lines[i]):
                para_lines.append(lines[i].strip())
                i += 1
            current["blocks"].append(
                {"kind": "para", "runs": parse_inline(" ".join(para_lines))})
    flush()
    return lede, sections


REQUIRED_KEYS = ("slug", "title", "eyebrow", "htmlTitle", "description",
                 "ogTitle", "ogDescription", "updated")


def load_doc(md_path: Path) -> dict:
    meta, body = parse_front_matter(md_path.read_text(encoding="utf-8"))
    missing = [k for k in REQUIRED_KEYS if k not in meta]
    if missing:
        raise ValueError(f"{md_path.name}: missing front-matter key(s): {missing}")
    lede, sections = parse_body(body)
    if not lede:
        raise ValueError(f"{md_path.name}: the first body paragraph (hero lede) is empty")
    doc = dict(meta)
    doc["lede"] = lede
    doc["sections"] = sections
    return doc


# --------------------------------------------------------------------------- #
#  Site renderer  (structured document -> full HTML page)
# --------------------------------------------------------------------------- #
def esc(s: str) -> str:
    """For attribute values (href, meta content) — quotes escaped."""
    return html.escape(str(s), quote=True)


def esc_text(s: str) -> str:
    """For element text — only &, <, > need escaping; apostrophes and quotes
    stay literal, so the rendered source reads like the hand-written original."""
    return html.escape(str(s), quote=False)


def inline_html(runs: list[dict]) -> str:
    out = []
    for r in runs:
        t = esc_text(r["text"])
        if r.get("href"):
            inner = f"<strong>{t}</strong>" if r.get("bold") else t
            out.append(f'<a href="{esc(r["href"])}">{inner}</a>')
        elif r.get("bold"):
            out.append(f"<strong>{t}</strong>")
        elif r.get("em"):
            out.append(f"<em>{t}</em>")
        else:
            out.append(t)
    return "".join(out)


def block_html(b: dict) -> str:
    k = b["kind"]
    if k == "para":
        return f'    <p class="measure-wide muted">{inline_html(b["runs"])}</p>'
    if k == "subheading":
        return f"    <h3>{inline_html(b['runs'])}</h3>"
    if k == "list":
        lis = "\n".join(f"      <li>{inline_html(it)}</li>" for it in b["items"])
        return f'    <ul class="principles">\n{lis}\n    </ul>'
    if k == "callout":
        cls = "callout gold" if b["variant"] == "gold" else "callout"
        ps = "\n".join(f"      <p>{inline_html(p)}</p>" for p in b["paras"])
        return f'    <div class="{cls}">\n{ps}\n    </div>'
    return ""


HEADER = """<header class="site-header">
  <div class="wrap">
    <a class="wordmark" href="index.html">BillTracking<span class="tld">.org</span></a>
    <nav class="site-nav" aria-label="Main">
      <a href="index.html">Home</a>
      <a href="us-process.html">US Process</a>
      <a href="eu-process.html">EU Process</a>
      <a href="educators.html">Educators</a>
      <a href="accuracy.html">Accuracy</a>
      <a href="about.html">About</a>
    </nav>
  </div>
</header>"""

FOOTER = """<footer class="site-footer">
  <div class="wrap">
    <div class="footer-grid">
      <div>
        <a class="wordmark" href="index.html">BillTracking<span class="tld">.org</span></a>
        <p>An independent project publishing a live, source-linked record of US and EU
        lawmaking. No sponsors, no advertisers, no
        paid placements. Not affiliated with, or endorsed by, the United States
        Congress, the European Union, or any government body.</p>
      </div>
      <div>
        <h5>Pages</h5>
        <ul>
          <li><a href="us-process.html">The US process</a></li>
          <li><a href="eu-process.html">The EU process</a></li>
          <li><a href="educators.html">Educators</a></li>
          <li><a href="accuracy.html">Accuracy &amp; corrections</a></li>
          <li><a href="about.html">About</a></li>
        </ul>
      </div>
      <div>
        <h5>Legal</h5>
        <ul>
          <li><a href="privacy.html">Privacy</a></li>
          <li><a href="terms.html">Terms of use</a></li>
          <li><a href="delete-account.html">Delete your account</a></li>
        </ul>
      </div>
      <div>
        <h5>Contact</h5>
        <ul>
          <li><a href="mailto:contact@billtracking.org">contact@billtracking.org</a></li>
          <li><a href="mailto:accuracy@billtracking.org">accuracy@billtracking.org</a></li>
          <li><a href="https://x.com/USBillTracker">@USBillTracker</a></li>
          <li><a href="https://x.com/EUBillTracker">@EUBillTracker</a></li>
        </ul>
      </div>
    </div>
    <div class="footer-legal">
      <p>BillTracking is an independent project · © 2026 billtracking.org</p>
    </div>
  </div>
</footer>"""

HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{htmlTitle} | BillTracking</title>
<meta name="description" content="{description}">
<link rel="canonical" href="{site}/{slug}.html">
<meta property="og:type" content="website">
<meta property="og:url" content="{site}/{slug}.html">
<meta property="og:title" content="{ogTitle}">
<meta property="og:description" content="{ogDescription}">
<meta property="og:image" content="{og_image}">
<link rel="icon" type="image/png" sizes="32x32" href="assets/favicon-32.png">
<link rel="icon" type="image/png" sizes="16x16" href="assets/favicon-16.png">
<link rel="apple-touch-icon" sizes="180x180" href="assets/favicon-180.png">
<link rel="stylesheet" href="style.css?v=2">
</head>
<body>
"""


def render_site(doc: dict) -> str:
    parts = [HEAD.format(
        htmlTitle=esc(doc["htmlTitle"]), description=esc(doc["description"]),
        site=SITE_URL, slug=esc(doc["slug"]), ogTitle=esc(doc["ogTitle"]),
        ogDescription=esc(doc["ogDescription"]), og_image=OG_IMAGE)]
    parts.append("\n" + HEADER + "\n\n<main>\n\n")
    parts.append('<div class="hero">\n  <div class="hero-inner">\n'
                 f'    <p class="eyebrow">{esc_text(doc["eyebrow"])}</p>\n'
                 f'    <h1>{esc_text(doc["title"])}</h1>\n'
                 f'    <p class="lede">{inline_html(doc["lede"])}</p>\n'
                 "  </div>\n</div>\n")

    content_i = 0
    last = len(doc["sections"]) - 1
    for idx, sec in enumerate(doc["sections"]):
        alt = ""
        if sec["heading"] is not None:
            alt = ' class="alt"' if content_i % 2 == 1 else ""
            content_i += 1
        parts.append(f"\n<section{alt}>\n  <div class=\"wrap\">\n")
        if sec["eyebrow"]:
            parts.append(f'    <p class="eyebrow on-light">{esc_text(sec["eyebrow"])}</p>\n')
        if sec["heading"] is not None:
            parts.append(f'    <h2>{esc_text(sec["heading"])}</h2>\n')
        parts.append("\n".join(block_html(b) for b in sec["blocks"]) + "\n")
        if idx == last:  # the "Last updated" line closes the final section
            parts.append(f'    <p class="muted"><em>Last updated {esc_text(doc["updated"])}.</em></p>\n')
        parts.append("  </div>\n</section>\n")

    parts.append("\n</main>\n\n" + FOOTER + "\n\n</body>\n</html>\n")
    return "".join(parts)


# --------------------------------------------------------------------------- #
#  App renderer  (structured document -> typed TS data module)
# --------------------------------------------------------------------------- #
def js(s: str) -> str:
    return json.dumps(s, ensure_ascii=False)


def to_const(slug: str) -> str:
    """slug -> the exported TS identifier, camelCased so a kebab slug like
    `cookie-policy` yields a valid `cookiePolicyDoc` (not `cookie-policyDoc`,
    which is a TS syntax error). `privacy` -> `privacyDoc`, unchanged."""
    parts = [p for p in re.split(r"[^a-zA-Z0-9]+", slug) if p]
    head = parts[0].lower()
    tail = "".join(p[:1].upper() + p[1:] for p in parts[1:])
    return f"{head}{tail}Doc"


def app_href(raw: str) -> str:
    if raw in APP_ROUTE:
        return APP_ROUTE[raw]
    if "://" in raw or raw.startswith("mailto:"):
        return raw
    if raw.endswith(".html"):
        return f"{SITE_URL}/{raw}"
    return raw


def ts_run(r: dict) -> str:
    parts = [f"text: {js(r['text'])}"]
    if r.get("bold"):
        parts.append("bold: true")
    if r.get("em"):
        parts.append("em: true")
    if r.get("href"):
        parts.append(f"href: {js(app_href(r['href']))}")
    return "{ " + ", ".join(parts) + " }"


def ts_runs(runs: list[dict]) -> str:
    return "[" + ", ".join(ts_run(r) for r in runs) + "]"


def ts_block(b: dict) -> str:
    k = b["kind"]
    if k in ("para", "subheading"):
        return f'{{ kind: "{k}", runs: {ts_runs(b["runs"])} }}'
    if k == "list":
        items = ", ".join(ts_runs(it) for it in b["items"])
        return f'{{ kind: "list", items: [{items}] }}'
    if k == "callout":
        paras = ", ".join(ts_runs(p) for p in b["paras"])
        return f'{{ kind: "callout", variant: "{b["variant"]}", paras: [{paras}] }}'
    return "null"


def ts_section(sec: dict) -> str:
    heading = js(sec["heading"]) if sec["heading"] is not None else "null"
    blocks = ",\n      ".join(ts_block(b) for b in sec["blocks"])
    return ("  {\n"
            f"    heading: {heading},\n"
            "    blocks: [\n"
            f"      {blocks},\n"
            "    ],\n"
            "  }")


def render_app(doc: dict) -> str:
    const = to_const(doc["slug"])
    sections = ",\n".join(ts_section(s) for s in doc["sections"])
    return (
        "// GENERATED — do not edit by hand.\n"
        f"// Source of truth: site/legal/{doc['slug']}.md\n"
        "// Regenerate:      python site/build/generate_legal.py\n"
        "// Rendered by:     src/components/legal-doc-view.tsx (see DECISIONS.md D23)\n"
        "import type { LegalDoc } from './types';\n\n"
        f"export const {const}: LegalDoc = {{\n"
        f'  slug: "{doc["slug"]}",\n'
        f"  title: {js(doc['title'])},\n"
        f"  updated: {js(doc['updated'])},\n"
        f"  lede: {ts_runs(doc['lede'])},\n"
        "  sections: [\n"
        f"{sections},\n"
        "  ],\n"
        "};\n"
    )


# --------------------------------------------------------------------------- #
#  Self-test — the grammar's edge behaviour, so it can't silently regress
# --------------------------------------------------------------------------- #
def _selftest() -> None:
    # a ) inside a URL survives (EUR-Lex-style link)
    assert parse_inline("[x](https://e.eu/833(1)/oj)") == [
        {"text": "x", "href": "https://e.eu/833(1)/oj"}]
    # consecutive `>` lines fold into ONE callout paragraph
    _, secs = parse_body("Lede.\n\n> one\n> two")
    callout = secs[0]["blocks"][0]
    assert callout["kind"] == "callout" and len(callout["paras"]) == 1, callout
    # kebab slug -> valid camelCase identifier; single word unchanged
    assert to_const("cookie-policy") == "cookiePolicyDoc"
    assert to_const("privacy") == "privacyDoc"
    # out-of-grammar input FAILS LOUD instead of mis-rendering
    for bad in ("Lede.\n\n^Kicker\nnot a heading",   # orphaned eyebrow
                "Lede.\n\n^Kicker",                   # eyebrow at EOF
                "Lede.\n\n##Heading",                 # missing space
                "Lede.\n\n#### H4",                   # unsupported level
                "Lede.\n\n-item"):                    # list missing space
        try:
            parse_body(bad)
        except ValueError:
            continue
        raise AssertionError(f"expected ValueError for: {bad!r}")
    print("selftest OK")


# --------------------------------------------------------------------------- #
#  Build
# --------------------------------------------------------------------------- #
def main():
    here = Path(__file__).resolve().parent          # site/build
    site_root = here.parent                         # site
    legal_src = site_root / "legal"

    ap = argparse.ArgumentParser(description="Generate BillTracking legal pages.")
    ap.add_argument("--site-out", type=Path, default=site_root,
                    help="site root that receives <slug>.html")
    ap.add_argument("--app-out", type=Path, default=None,
                    help="app dir that receives <slug>.generated.ts "
                         "(default: ../app/src/data/legal)")
    ap.add_argument("--no-app", action="store_true", help="skip the app module")
    ap.add_argument("--selftest", action="store_true",
                    help="run the grammar self-test and exit")
    a = ap.parse_args()

    if a.selftest:
        _selftest()
        return

    app_out = a.app_out
    if app_out is None and not a.no_app:
        guess = site_root.parent / "app" / "src" / "data" / "legal"
        app_out = guess if guess.parent.parent.exists() else None
        if app_out is None:
            log.warning("app repo not found beside the site — writing site only")

    for md in sorted(legal_src.glob("*.md")):
        # a policy source starts with `---` front-matter; other .md files here
        # (LEGAL-SPEC.md, README.md) are documentation — skip, don't parse them
        if not md.read_text(encoding="utf-8").lstrip().startswith("---"):
            log.info("skip  %s (no front-matter - documentation, not a source)", md.name)
            continue
        doc = load_doc(md)
        (a.site_out / f"{doc['slug']}.html").write_text(
            render_site(doc), encoding="utf-8")
        log.info("site  <- %s -> %s.html", md.name, doc["slug"])
        if app_out and not a.no_app:
            app_out.mkdir(parents=True, exist_ok=True)
            (app_out / f"{doc['slug']}.generated.ts").write_text(
                render_app(doc), encoding="utf-8")
            log.info("app   <- %s -> %s.generated.ts", md.name, doc["slug"])


if __name__ == "__main__":
    main()
