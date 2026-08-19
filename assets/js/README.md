# `bt-web.js` — the contract with the HTML

**Status:** the HTML, the CSS and the glyph sprite exist; `bt-web.js` and
`bt-core.js` do not yet. This file is what the pages promise, written by the
markup lane so the JS lane can build against it without reading four HTML files.

`bt-web.js` is a thin **view**. It owns no product rules. Everything that
decides *what a card says* — the adapter, dedupe, ids, corrections/revisions,
ordering, the one date formatter (D22), labels + the glyph table,
`composePostText`, the card content model, `billKey()` and the URL builders,
the feed client with `FeedHealth` and staleness, vote logic and the tally
read — comes from **`bt-core`**, compiled from the app's own TypeScript
(plan §3). If you find yourself re-implementing a rule here, it belongs in the
core. A rendered field that is not proven identical across builds is a build
failure (D27, proposed).

Files this lane produced:

| Path | What |
|---|---|
| `tools/templates/feed-page.html` | the one feed-page template |
| `tools/build_feed_pages.py` | renders `us.html` + `eu.html` from it (`--check` fails on stale) |
| `assets/css/feed.css` | the card + page CSS, loaded after `style.css` |
| `tools/glyphs.svg` | the glyph sprite, generated from the app's `icon.tsx`, inlined into card pages at build time — **build input, not a served asset** |
| `us.html`, `eu.html`, `account.html`, `auth/callback.html`, `404.html` | the shells |

---

## 1. Page shells and mount points

All four page types load `<script type="module" src="/assets/js/bt-web.js">` as
the last element in `<body>`. One module, four entry paths; branch on what is
in the DOM, not on `location`.

### 1.1 Feed page — `us.html`, `eu.html` (served as `/us`, `/eu`)

```html
<main class="feed-page" data-polity="us">
  <header class="feed-head"> … eyebrow, H1, intro, explainer link … </header>
  <p    id="bt-freshness" class="feed-fresh"></p>
  <section id="bt-feed" class="feed" tabindex="-1" aria-busy="true" aria-label="The US feed"></section>
  <p    id="bt-announce" class="sr-only" role="status"></p>
  <div  id="bt-status" class="feed-status" role="status"></div>
  <button id="bt-more" class="btn btn-more" hidden>Show more posts</button>
  <noscript> … honest fallback … </noscript>
  <p id="bt-build" class="feed-build"></p>
</main>
```

* `data-polity` on `<main>` is the **only** polity input. Read it; never infer
  from the URL.
* `#bt-feed` — append `<article class="card">` elements here (§2). Set
  `aria-busy="false"` when the first render lands. It is `tabindex="-1"` because
  the skip link targets it.
* **`#bt-feed` is NOT a live region — do not add `aria-live`.** A polite live
  region announces everything inserted into it, so 25 cards on load (and 25 more
  per page) would be read out in full, unstoppably. Announce the *fact* instead:
  put one short sentence in `#bt-announce` (`role="status"`, visually hidden) —
  `25 posts loaded`, `25 more posts loaded`. The cards are read by navigating,
  like any list. (The brief for this lane asked for `aria-live` on the container;
  this is a deliberate, flagged deviation — overrule it here if the owner wants
  the container back as a live region.)
* `#bt-status` — exactly one state at a time (§3), or empty. `:empty` collapses
  it, so clear it with `replaceChildren()`; do not leave `<div></div>` padding.
  **It ships with the loading state already in the HTML** — true at first paint,
  and better than a blank rectangle. Replace it as soon as you know better; empty
  it the moment cards render. It stays a live region: a state change here *is*
  the announcement.
* `#bt-more` — 25 cards, then reveal (`hidden = false`). Keep it a `<button>`,
  and keep the label **"Show more posts"**: every card's expander says "Show
  more" (app law), so an identically-named pagination control would put 26
  same-named controls with two different jobs on one page. Move focus to the
  first newly-appended card after a page loads.
* `#bt-freshness` — §4. `:empty` collapses it; leave it empty until you know.
* `#bt-build` — optional one-line build stamp (core sha / built-at). `:empty`
  collapses it.

### 1.2 Account — `account.html`

```html
<main class="account-page" id="bt-account">
  <section class="acct-region" id="bt-acct-loading"> … </section>
  <section class="acct-region" id="bt-acct-signed-out" hidden>
      <button id="bt-signin-google" class="btn-provider" disabled>Continue with Google</button>
      <button id="bt-signin-apple"  class="btn-provider" disabled>Continue with Apple</button>
      <p id="bt-provider-note" class="acct-note">Sign-in coming soon.</p>
  </section>
  <section class="acct-region" id="bt-acct-signed-in" hidden>
      <p id="bt-acct-email" class="acct-value"></p>
      <div id="bt-geo-picker"></div>     <!-- MOUNT: location picker -->
      <div id="bt-consent"></div>        <!-- MOUNT: consent status  -->
      <button id="bt-signout" class="btn-provider">Sign out on this device</button>
      <a href="/delete-account.html"> … </a>
  </section>
  <p id="bt-acct-status" class="acct-status" role="status"></p>
</main>
```

* Exactly one region visible: toggle the `hidden` attribute; `.acct-region[hidden]`
  is `display:none` in CSS, so nothing flashes.
* **The provider buttons ship `disabled` and the note reads "Sign-in coming
  soon."** That is the honest default: enable them and swap the note *only*
  when the provider is actually configured. Inviting a sign-in that cannot
  happen is the dishonest affordance this product exists to avoid — the app
  makes the same call in `vote-chips.tsx` (interim wording, 2026-08-14).
* Sign-out is `{ scope: 'local' }` — a browser sign-out must never kill the
  phone's session (`auth.ts:157` defaults to global; that is a known bug).
* `#bt-geo-picker` and `#bt-consent` are **mounts, not copy**. Location is
  account-level (set once, same on every surface); the consent sentence comes
  from `lib/voter.ts` `consentSentence()`, which lifts it VERBATIM from the
  published privacy policy through the D23 pipeline. Do not write a second
  wording here — the one the reader agreed to has to be the one we published.
  `CONSENT_VERSION` is what makes it answerable later.
* Delete account keeps its own page (`/delete-account.html`); do not build a
  second deletion flow here.
* `#bt-acct-loading` carries a static second line saying what it means if the
  region never changes (the module failed to load — `<noscript>` does not fire
  for that). Replacing the region, which is what you do anyway, removes it.
* **NOTHING LINKS TO `/account` YET.** The site's nav is one shared block across
  every page and is not this lane's to fork, so the feed→account edge is the
  card's: on a card whose chips are actionable but whose reader is signed out,
  the caption under the chips is a **link to `/account`** — the web equivalent
  of the app's caption opening the You tab (`vote-chips.tsx`, "a caption that
  names an action IS the action"). Until sign-in exists the caption keeps the
  app's interim wording, `Voting — coming soon`, and still links there. A nav
  entry is an owner call, not a JS one.

### 1.3 OAuth return — `auth/callback.html` (served as `/auth/callback`)

```html
<main id="bt-callback">
  <h1 id="bt-callback-title">Signing you in…</h1>
  <p  id="bt-callback-status" class="auth-status" role="status"> … </p>
  <div id="bt-callback-error" class="acct-card" hidden>
      <p id="bt-callback-error-detail"></p>
  </div>
</main>
```

* **The one page with `detectSessionInUrl: true`.** Everywhere else it is
  `false`. `flowType: 'pkce'` everywhere, always — with the supabase-js default
  (`implicit`) this page would put a refresh token in the URL fragment and in
  browser history.
* Validate the return path against a **same-origin allowlist** before
  redirecting. An open redirect here hands somebody else the account.
* On failure: fill `#bt-callback-error-detail` with the reason you were given,
  unhide `#bt-callback-error`, and change `#bt-callback-title` — do not leave
  "Signing you in…" on screen while showing an error.
* Remove `#bt-callback-boot-note` as soon as the module runs. It is the static
  answer to "this page's script never loaded", and it must not sit under a
  status line that *is* being updated.

### 1.4 Resolver — `404.html`

```html
<main id="bt-resolver" data-path="">
  <p id="bt-resolver-status" class="resolver-status"> … plain 404 copy … </p>
  <div id="bt-resolver-mount"></div>
  <ul class="page-links"> … /us /eu / /p/ /b/ … </ul>
</main>
```

* `data-path` is **empty in the file** — a static host cannot fill it. Set it
  from `location.pathname` on entry so the state is inspectable, then resolve.
* The static copy is already a correct 404. Only replace it when you have
  actually resolved something; if the resolver finds nothing, leave the page
  alone. Never render "loading" over a page that is already true.
* `/p/<id>` or `/b/<polity>/<slug>` published but not yet rendered (the cron
  runs every 15 min) ⇒ draw it client-side into `#bt-resolver-mount`, so a link
  works the instant it exists. Legacy `/bill/<ref>` ⇒ resolve to the key and
  redirect **only when unambiguous**; otherwise say so and offer the choices.

---

## 2. The card DOM

`feed.css` styles exactly this tree. Order matters — the collapse rule (D6)
depends on it.

```html
<article class="card" data-polity="us"
         data-post-id="<postPermalinkId>"
         aria-labelledby="t-<postPermalinkId>"
         data-billkey="us/119-sres-815">     <!-- OMIT the attribute when there is no key -->

  <!-- 1. HEAD — never clipped. Status cards lead with the reference; -->
  <!--    franchise/batch cards lead with the date.                    -->
  <div class="card-head">
    <div class="card-ref-row">
      <a class="card-ref" href="/b/us/119-sres-815">S.Res. 815</a>
      <!-- ONE pill max: a correction flag wins the slot over "Older action". -->
      <a class="pill-correction" data-kind="inaccurate" href="/p/…">Inaccurate</a>
      <!-- or --> <a class="pill-correction" data-kind="correction" href="/p/…">Correction</a>
      <!-- or --> <span class="flag-older">Older action</span>
    </div>
    <!-- The head-right slot OPENS THE POST; it is not the app's ⋯ menu. -->
    <a class="card-open" href="/p/<id>" aria-label="Open this post">
      <svg class="glyph" aria-hidden="true"><use href="#chevron-right"/></svg>
    </a>
  </div>

  <!-- franchise variant of the head's left side -->
  <p class="card-date-lead">
    <svg class="glyph" aria-hidden="true"><use href="#calendar-event-band"/></svg>
    8 August 2026 at 09:30 AM
  </p>

  <!-- 2. BODY — the ONLY collapsing region. data-clipped="1" when it overflows. -->
  <div class="card-body" data-clipped="1">
    <!-- status. HEADING LEVEL 2 (the page's h1 is the feed's title) and it
         carries the id the <article> is labelled by. -->
    <h2 class="card-title" id="t-<postPermalinkId>">A resolution commending …</h2>
    <p class="card-meta">Sen. Richard Durbin (D-IL) | Commerce, Science, and Transportation Committee</p>
    <p class="card-action">
      <svg class="glyph glyph-cal" aria-hidden="true"><use href="#calendar-event-band"/></svg>
      <span class="card-action-date"> 7 August 2026&nbsp; |&nbsp; </span>
      <span class="glyph-wrap has-badge">
        <svg class="glyph glyph-label" aria-hidden="true"><use href="#capitol"/></svg>
        <span class="glyph-badge"><svg class="glyph" aria-hidden="true"><use href="#check"/></svg></span>
      </span>
      <span class="card-action-label">Agreed to</span>
      <span class="card-action-tally"> (unanimous consent)</span>
    </p>
    <p class="card-source">Source: OEIL procedure file 2023/0447(COD)</p>   <!-- EU only -->

    <!-- franchise — the headline IS the card's heading, same level and same
         labelling job as a status card's title. It was a <p>, which left a
         third of the feed with no heading and no accessible name at all. -->
    <h2 class="card-headline" id="t-<postPermalinkId>">
      <span class="glyph-wrap"><svg class="glyph glyph-label" aria-hidden="true"><use href="#capitol"/></svg></span>
      Today on the Hill
    </h2>
    <div class="card-body-lines"><p>…</p><p>…</p></div>
  </div>

  <!-- 3. ANCHORED — always visible, never inside the clip. -->
  <div class="card-anchored">
    <p class="card-next"><span class="lead">What's next: </span>Policy adoption …</p>
    <p class="card-budget"><span class="lead">Budget impact: </span>…</p>
  </div>

  <!-- 4. DEFERRED — always behind the expander, never clipped. -->
  <div class="card-deferred">
    <div class="card-summary">
      <p><span class="lead">Summary: </span>The resolution would …</p>
      <span class="ai-tag">[AI-Generated]</span>
    </div>
    <p class="card-older-note">⏱ About older actions: …</p>
    <a class="card-quote" href="/p/<targetId>">
      <p class="card-quote-tag">Correcting this post</p>
      <div class="card-quote-head">
        <span class="card-quote-ref">S. 5271</span>
        <span class="card-quote-date">8 August 2026</span>
      </div>
      <p class="card-quote-label">Cloture not invoked<span class="card-quote-tally"> (52-46)</span></p>
    </a>
  </div>

  <!-- 5. EXPANDER -->
  <button class="card-expander" aria-expanded="false" aria-controls="…-body">
    <span class="card-expander-label">Show more</span>
    <svg class="glyph" aria-hidden="true"><use href="#chevron-down"/></svg>
  </button>

  <!-- 6. STRIP — never clipped. Status posts with a reference.
       THE STRIP GATES ON THE REFERENCE, THE BREAKDOWN GLYPH ON THE IDENTITY. -->
  <div class="card-strip">
    <!-- ONLY when the card has a data-billkey. -->
    <button class="card-strip-glyph" aria-label="Vote breakdown">
      <svg class="glyph" aria-hidden="true"><use href="#chart-bar"/></svg>
    </button>
    <div class="vote-chips">
      <button class="vote-chip" data-dir="up"   aria-pressed="false">▲ Yea</button>
      <button class="vote-chip" data-dir="down" aria-pressed="false">▼ Nay</button>
      <p class="vote-reason"></p>
    </div>
  </div>
</article>
```

### Rules the CSS assumes

1. **`data-polity` on the article** drives every accent: the ref link, the
   label glyph, the summary rule, the selected chip, and `--glyph-band` (the
   calendar's header band — US red, EU gold). A post keeps its **own** polity
   colours on every page; the page never re-themes a card.
2. **`data-billkey` is transcribed, never derived.** The key is
   `<polity>/<slug>` (`us/119-hr-3497`, `eu/2023-0447-cod`), minted only by
   `billKey()` in the app's `data/bill-identity.ts`. No key ⇒
   * omit the attribute entirely;
   * render both chips `disabled`;
   * put `NO_IDENTITY_REASON` — the exported constant from that same module,
     imported through the core, **never re-typed** (straight apostrophes and
     all: re-typing it is how it drifts) — into `.vote-reason`;
   * **and render NO `.card-strip-glyph`.** The strip gates on the reference,
     the breakdown gates on the identity (`post-card.tsx:691`, identity packet
     §3 row 8): with no key there is no tally to fetch, so the glyph would be a
     door onto a room that can only ever be empty. Disabled chips are the
     honest shape of "we don't know"; a working-looking door is not.

   Deriving a key on the client is how a vote lands on the wrong Congress's bill.
3. **The collapse (D6).** Only `.card-body` collapses; head, anchored, deferred
   and strip never do. After inserting a card:
   * `hasDeferred` = the card has any deferred content;
   * `clipped` = `body.scrollHeight > 168 + 24` (`CARD_BODY_MAX` = 168, and the
     +24 is the app's "a control that hides eight points reads as broken");
   * set `data-clipped="1"` on `.card-body` when `clipped`;
   * show the expander when `hasDeferred || clipped`, else leave it `hidden`;
   * opening = add `.is-open` to the `<article>` (CSS drops the cap, drops the
     fade, un-clamps the title, reveals `.card-deferred`), flip `aria-expanded`,
     swap the label to "Show less" and the `<use>` to `#chevron-up`.
   * Re-measure on resize (debounced) — a narrower column clips more.
4. **The title clamps while the card is CLOSED, and the full title shows on
   open.** Both halves are the app's (`numberOfLines={expanded ? undefined : 3}`,
   `post-card.tsx:593`), and the CSS does all of it: `.card:not(.is-open)
   .card-title` clamps to 3 lines. Do not clamp in JS, and do not key the clamp
   to `data-clipped` — a clamped title is not the same thing as a clipped body.
   **Known parity item, not a web bug:** a card whose title alone runs past three
   lines but whose body neither overflows nor carries deferred content shows no
   expander, so the rest of the title cannot be reached — on the web *and* in the
   app, for the same reason. Recorded rather than fixed on one surface only.
5. **The action-line separator is conditional.** No label ⇒ no `|`. The app
   shipped a dangling pipe on every EU card once; don't repeat it.
6. **`[AI-Generated]` renders with every summary, unconditionally.**
7. **One pill.** Correction flags win the header slot over "Older action" — but
   the older-action **footer note still renders** in `.card-deferred` whether or
   not its pill won.
8. **Chips carry no counts, on any surface.** `▲ Yea / ▼ Nay` (US),
   `▲ For / ▼ Against` (EU). Never hearts, thumbs, or a net score. Selected is
   `aria-pressed="true"` — the CSS reads the ARIA state, so the two cannot drift.
9. **Colour only for good news.** `.glyph-label.is-green` (the ✅ family) and the
   green corner badge are the only coloured glyphs. A rejection, veto,
   withdrawal or send-back stays neutral ink — never red.
10. **Every card has a heading and a name.** The status card's `.card-title` and
   the franchise card's `.card-headline` are both `<h2>` (the page's `<h1>` is
   the feed's own title) carrying `id="t-<postId>"`, and the `<article>` carries
   `aria-labelledby` pointing at it. Cards are how this page is navigated; an
   unnamed `<article>` is announced as "article" and nothing more.
11. **Per-glyph stroke weight travels in `--glyph-stroke`, not `stroke-width`.**
   `feed.css` sets weight through `var(--glyph-stroke, …)`, because a CSS rule
   beats an SVG presentation attribute and `svg.setAttribute('stroke-width', …)`
   would be silently ignored. For a label glyph whose table row carries a
   `stroke`: `svg.style.setProperty('--glyph-stroke', String(lp.stroke))` — on
   the `<svg>` itself, never a wrapper (it inherits, and the green badge is in a
   sibling span). Rows without a `stroke` need nothing; the default is already
   `1.7`. This is the one place `el.style` beats a class: the table can invent a
   weight tomorrow, and a fixed set of utility classes could not carry it.
12. **The head-right control opens the post; it is not the ⋯ menu.**
   `.card-open` is an `<a href="/p/<id>">` drawing `#chevron-right`, with
   `aria-label="Open this post"`. The app's ⋯ opens a sheet (share, report,
   source) that the web does not have; drawing a menu glyph for a control that
   navigates would promise a menu that is not there, and it was also the *only*
   feed→post edge on the page. If the web ever grows that sheet, ⋯ returns to
   this slot and the open affordance moves elsewhere — say so here when it does.

---

## 3. `#bt-status` — the six honest states

Render **one**, in the app's order (`app/src/app/(tabs)/index.tsx` `FeedEmpty`),
in the app's words. Shape:

```html
<h2>Can't reach the feed</h2>
<p>We can't load posts right now, and we'd rather show you nothing than something out of date. This is a problem our end, not yours — check back shortly.</p>
```

| order | when | title | body |
|---|---|---|---|
| 1 | feed not loaded yet | `Loading…` | `Fetching the latest from the official record.` |
| 2 | `feedHealth.state === 'unavailable'` | `Can't reach the feed` | as above — an outage outranks everything below |
| 3 | a search query with no hits | `No matches` | `No posts on this feed match that search. The record is searched — labels, titles and summaries; predictions are not.` |
| 4 | zero posts at all | `No posts yet` | `Nothing has been published to this feed yet. When Congress moves on a bill, it will appear here.` (EU: `the European Parliament`) |
| 5 | docket filter on, nothing matches | `Nothing on your docket` | `There are recent posts, but none are for bills you follow or keywords you've saved. Turn off the docket filter to see everything.` |
| 6 | display filters hide everything | `Nothing to show` | `Your display filters hide every recent post on this feed. Tap the filter icon above to adjust them.` |
| 7 | otherwise | `Nothing recent` | `There are no recent posts for Congress on this feed.` |

(States 5 and 6 have no web control yet — keep the branches, they cost nothing
and the alternative is blaming the wrong thing when they arrive.)

**Clear `#bt-status` the moment cards render.** The bug this replaced was
telling readers to go fix filters that were not the problem.

---

## 4. `#bt-freshness`

Two facts, both true, no adjectives:

```
Newest post: 18 August 2026 · checked 2:32 PM
```

* the date through the core's **one** formatter (`formatDisplayDate`, D22) —
  never a second date format anywhere, ever; `eventDate` is a join key;
* "checked" = when *this browser* last fetched, local time. Not a build time:
  the page fetches live, which is the whole point. **Twelve-hour clock with
  `AM`/`PM`** — the cards say "5 August 2026 at 10:00 AM" because that is what
  the bots write, and our own clock two lines above them saying `14:32` is one
  page speaking two conventions. `hour: 'numeric', minute: '2-digit',
  hour12: true`, then upper-case the meridiem.
* Past 36 h without a new post, append the core's `stalenessNotice(...)` in a
  `<span class="fresh-warn">`: `No new posts in N days. That may be a quiet
  period — or a problem our end.` Health states come from the same function
  (`Can't reach the feed…`, `Showing saved posts — no connection.`).
* Empty until you know. `.feed-fresh:empty` collapses, so an unknown state
  costs no layout and tells no story.

---

## 5. Glyphs

`tools/glyphs.svg` is a sprite of `<symbol>`s **generated from the app's
`src/components/icon.tsx` PATHS table** (Tabler, MIT; `ballot` is Lucide `vote`,
ISC; `capitol` is custom). It lives in `tools/` because it is **build input**:
it was at `assets/glyphs.svg`, which published a URL for a file that provably
does not work when linked (below), and a public URL is an invitation to link it.
Symbol ids are the glyph names. Reference them with a
**bare fragment** — the sprite is already in the document:

```html
<svg class="glyph" aria-hidden="true"><use href="#circle-check"/></svg>
```

**The sprite is INLINED at build time, never linked.** `build_feed_pages.py`
pastes it between the `BT-SPRITE:START` / `BT-SPRITE:END` markers of every page
that draws cards (`us.html`, `eu.html`, `404.html`); the JS never fetches it and
must never emit `href="/assets/glyphs.svg#id"`.

Why, so nobody "fixes" it back: the external form was built first and measured
on 2026-08-19. The file returned **200** and the symbol still did not
instantiate — `getBBox()` 0×0, nothing painted, no console error — same-origin,
with and without the CSP, from static markup and from injected markup. A glyph
that can vanish with no error is the failure class this product does not ship;
inlining costs ~9 KB (~3 KB gzipped) and one fewer request. If a page ever needs
glyphs and is not in `SPRITE_PAGES`, add it there — do not link the file.

`stroke` and `stroke-width` are inherited properties, so the sprite carries
geometry only and the referencing element decides weight and colour.
`.glyph` sets `fill:none; stroke:currentColor; stroke-width:var(--glyph-stroke,2)`;
the size and per-context defaults (`.glyph-cal` 18.5/1.7, `.glyph-label` 20/1.7,
`.card-headline .glyph-label` 24/1.7) are in `feed.css`, and a table row's own
weight rides in `--glyph-stroke` (rule 11 above). Glyphs whose weight is fixed by
their context rather than the table — the expander chevron 2.2, the breakdown
glyph 1.7, the badge tick 3.8 — keep a literal `stroke-width` and are not
overridable.

Two special symbols:

* **`calendar-event-band`** — the app's `CalendarIcon`: the calendar paths plus
  the accent header band, painted `var(--glyph-band)` (custom properties inherit
  through the `<use>` shadow tree, so `data-polity` on the card colours it). Use
  this one on cards; plain `calendar-event` is the unbanded Tabler glyph.
* **`bell-filled`** — filled path data, so it paints rather than strokes; the
  symbol sets `fill="currentColor" stroke="none"` itself.

Regenerate the sprite whenever `icon.tsx` changes. It is generated output — do
not hand-edit it.

### The label → glyph map (reference only)

**Do not hand-port this.** It is `app/src/lib/label-icon.tsx`'s `GLYPHS` table
and it belongs in `bt-core`; the JS imports `splitLabel()` from there. It is
reproduced here so the JS lane can see the shape it will get — and because the
**belt matters**: a prefix this table does not know renders as **the raw emoji
it always was**. The bots have more families than any table, and a new family
must never break a card.

Order matters — longest prefix first (`✅🏛️` before `✅`).

```json
[
  { "prefix": "✅🏛️", "icon": "capitol",        "badge": true },
  { "prefix": "✅",   "icon": "circle-check",  "green": true, "stroke": 2 },
  { "prefix": "🗳️", "icon": "ballot",         "stroke": 1.95 },
  { "prefix": "🗳",  "icon": "ballot",         "stroke": 1.95 },
  { "prefix": "📋",  "icon": "clipboard-text" },
  { "prefix": "⏱️", "icon": "clock" },
  { "prefix": "⏱",  "icon": "clock" },
  { "prefix": "📅",  "icon": "calendar-event" },
  { "prefix": "🗓️", "icon": "calendar-event" },
  { "prefix": "🗓",  "icon": "calendar-event" },
  { "prefix": "📌",  "icon": "send" },
  { "prefix": "🧭",  "icon": "compass" },
  { "prefix": "🤝",  "icon": "handshake",      "stroke": 1.55 },
  { "prefix": "🖋️", "icon": "signature" },
  { "prefix": "🖋",  "icon": "signature" },
  { "prefix": "📜✍️", "icon": "scroll",         "badge": true },
  { "prefix": "📜",  "icon": "scroll",         "badge": true },
  { "prefix": "✍️", "icon": "signature" },
  { "prefix": "✍",  "icon": "signature" },
  { "prefix": "🏛️", "icon": "capitol" },
  { "prefix": "🏛",  "icon": "capitol" },
  { "prefix": "❌",  "icon": "x",              "stroke": 2.15 },
  { "prefix": "↩️", "icon": "arrow-back-up" },
  { "prefix": "↩",  "icon": "arrow-back-up" },
  { "prefix": "⚖️", "icon": "scale" },
  { "prefix": "⚖",  "icon": "scale" },
  { "prefix": "🗑️", "icon": "file-off" },
  { "prefix": "🗑",  "icon": "file-off" },
  { "prefix": "📝",  "icon": "edit" }
]
```

Rendering flags: `green` ⇒ add `is-green` to the glyph's class (the ✅ family
only — colour only for good news). `badge` ⇒ wrap in
`<span class="glyph-wrap has-badge">` with the `.glyph-badge` check. `stroke`
⇒ `svg.style.setProperty('--glyph-stroke', String(row.stroke))` on that one
`<svg>` — **not** a `stroke-width` attribute, which the class rule beats
silently (rule 11). The default for label glyphs is `1.7`
(`LABEL_ICON_STROKE`), which `feed.css` already applies.

---

## 6. CSP, and one thing it cannot do

Every new page carries the same meta CSP:

```
default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline';
img-src 'self' data:; font-src 'self';
connect-src 'self' https://billtrackingorg.github.io https://skqngxvuncdavlshkepb.supabase.co;
object-src 'none'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'
```

Consequences for the JS:

* `script-src 'self'` — no `eval`, no `new Function`, no inline `<script>`, no
  CDN. Ship modules from `/assets/js/`.
* `connect-src` lists exactly two remotes: the published feed on
  `billtrackingorg.github.io` (CORS `*`, verified live) and Supabase. Anything
  else fails, loudly, in the console. The OAuth hop to the provider is a
  **navigation**, not a fetch, so it is unaffected.
* `style-src 'unsafe-inline'` is there because `style.css` is joined by inline
  attribute styles elsewhere on the site. Prefer classes over `el.style` anyway —
  `--glyph-stroke` (rule 11) is the one sanctioned exception, and it is a custom
  property, not a style rule.
* `object-src 'none'` carries over from the Expo page's policy: `default-src`
  would cover it, but plugin content is worth denying by name.
* **`frame-ancestors` is inert in a `<meta>` CSP** — it only works as an HTTP
  header, and GitHub Pages does not let us set headers. It is included so the
  policy is complete the day this moves behind anything that can send headers.
  Clickjacking protection today is *not* in place; that is a known, stated gap,
  not something the meta tag quietly fixes.

---

## 7. House rules that outrank convenience

* **`noindex` stays** on `/us`, `/eu`, `/account`, `/auth/callback` and `/404`
  until the owner's SEO gate (plan §9, Gate D). Do not remove it as a
  side-effect of anything.
* **Never write to the bots' repos or their feed key.** The website is a third
  *reader* of files the bots already publish. Zero bot lines.
* **No second date formatter.** `eventDate` is a join key for tally claiming.
* **Drop-never-guess.** If the core's adapter drops a record, the web drops it
  too, and says nothing it cannot prove.
* **Corrections cannot be filtered away**, at any age (D18).
* Copy law for these pages: no "complete history" (the archive starts 2026-07),
  no "every hour" for the EU (US-only claim), no notification promises, no
  "complete path", and no "live"/"real time" superlative in a title,
  description or OG tag — **"as it moves"** is the house phrase.

## 8. Rebuilding the shells

```sh
python tools/build_feed_pages.py           # us.html + eu.html from the template,
                                           # and refreshes the sprite block in 404.html
python tools/build_feed_pages.py --check   # exit 1 if any of them is stale
```

`account.html`, `auth/callback.html` and `404.html` are hand-authored — they are
one of a kind, and a template for one page is a template that rots. The only
part of them the generator owns is the `BT-SPRITE` block, so a regenerated
sprite reaches every page that draws cards; everything outside those markers is
the page's own and is left untouched.

The sprite itself is regenerated from the app's `icon.tsx` whenever that file's
PATHS table changes. That step lives in the app repo (it reads app source), and
its output is committed here.

---

## 9. Two things to carry into the cut-over (not fixed here, deliberately)

* **Push ordering is load-bearing.** `/us` paints head → "Loading…" → footer and
  stops until `bt-web.js` exists. Pages caches HTML for ten minutes, so an HTML
  push that lands without the bundle gives every visitor a `role="status"` that
  says "Loading…" and never changes — the page telling a lie about itself, for
  ten minutes minimum. Ship the bundle in the same push as the HTML, or before.
* **`/auth/callback` resolving from `auth/callback.html` is asserted, not
  proven.** Pages' extensionless resolution is the same rule the site already
  relies on, but it has not been probed for a file one directory down. The OAuth
  redirect URI is registered exactly once and a 404 there breaks sign-in
  completely: probe the live URL at Gate B, before the provider config is
  written.
