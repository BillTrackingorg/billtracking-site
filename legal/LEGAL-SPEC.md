# Legal pages — one source, two renderers

`privacy.md` and `terms.md` in this folder are the **single source of truth**
for the Privacy and Terms pages. One generator turns each into both outputs:

```
legal/privacy.md ──> ../privacy.html                          (this website)
                └──> ../../app/src/data/legal/privacy.generated.ts   (the app)
legal/terms.md   ──> ../terms.html   +   terms.generated.ts
```

The app renders those `.generated.ts` modules natively (see the app repo:
`src/components/legal-doc-view.tsx`, `src/app/privacy.tsx` / `terms.tsx`, and
`DECISIONS.md` D23). One parser here means the website and the app can never
show different words.

## Updating a policy

1. Edit `legal/privacy.md` or `legal/terms.md`.
2. Regenerate:

```bash
python build/generate_legal.py
```

3. Commit the changed files in **both** repos (the site `.html` here, and the
   `.generated.ts` in the app repo — they are written as siblings on disk).

`python build/generate_legal.py --no-app` writes only the site page, for when
the app repo isn't checked out beside the site.

Do **not** hand-edit `*.html` or `*.generated.ts` — they are build output and
the next regenerate overwrites them.

## Grammar

Deliberately tiny and stdlib-only (no Markdown dependency), matching the
zero-dependency style of `build/generate.py`.

### Front-matter

Between the first two `---` fences. `#` lines are comments.

| key             | used for                                             |
|-----------------|------------------------------------------------------|
| `slug`          | output filenames + canonical/og URL (`privacy`/`terms`) |
| `title`         | hero `<h1>` on the site; screen title in the app     |
| `eyebrow`       | the small kicker above the hero title (site only)    |
| `htmlTitle`     | `<title>` — e.g. `Privacy`                           |
| `description`   | `<meta name="description">`                          |
| `ogTitle`       | `og:title`                                           |
| `ogDescription` | `og:description`                                     |
| `updated`       | the "Last updated …" line                            |

### Body

| you write          | you get                                                        |
|--------------------|----------------------------------------------------------------|
| first paragraph    | the hero **lede**                                              |
| `^Kicker`          | eyebrow label for the section that follows (site only)         |
| `## Heading`       | a new section (`<h2>` on site; section heading in app)         |
| `### Subheading`   | an `<h3>` inside the current section                           |
| `- item`           | a bullet in a "principles" list                                |
| `> text`           | a callout box                                                  |
| `>! text`          | the gold "important" callout variant                           |
| plain line(s)      | a paragraph                                                    |

Blocks **before** the first `##` form a heading-less lead section — that is the
"What exists today" notice at the top of the privacy page.

### Inline

`**bold**` · `*italic*` · `[text](href)` · `[**bold link**](href)`

Link `href` handling in the **app** (the site keeps them as written):
`privacy.html` and `terms.html` become the in-app routes `/privacy` and
`/terms`; any other relative `*.html` is absolutised to `https://billtracking.org/…`;
`mailto:` and `http(s):` links pass through unchanged.

### What the source does NOT control

Presentation each renderer owns (mirrors the app's D16): the alternating
section tint on the site is applied from section order in the generator, and
the app ignores both the tint and the per-section eyebrow. Change the look in
`style.css` (site) or `legal-doc-view.tsx` (app), never here.
