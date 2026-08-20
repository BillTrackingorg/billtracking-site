# `bt-web.js` — the contract with the HTML

**Status (2026-08-19, integration pass): `bt-web.js` IS IN THIS REPO.** The
shells, the CSS and the sprite were here already; the reader half, the account
half and the two HTML renderers were built in the app repo; this pass compiled
them, copied the bundle in, rendered the whole live corpus through the
TypeScript renderer and drove every page in a browser. What is in the tree now:
`assets/js/bt-web.js` + its chunks (the compiled core) and `tools/bt-site.cjs`
(the same core, for the workflow). Nothing is committed or pushed — that is the
owner's gate. The vote RPC does not exist yet, so the breakdown panel honestly
reports that it could not load rather than reporting a result.

⚠️ **UX round, 2026-08-19/20 — THE SIGN-IN CONTROLS ARE NO LONGER DISABLED.**
Owner directive: *"We shouldn't be building as though things are coming soon, we
should be building to launch."* The compile-time `WEB_PROVIDERS` gate is deleted;
the provider buttons are live and ask the Supabase project itself whether a
provider exists (§1.2), the card caption reads `Sign in to vote` on the chips'
own row (§2 rule 13, §2b), every page's nav ends with a gold **Sign in** pill
(§1.2), and `/p/`, `/b/` and the resolver share one proper back control (§2c).
There is no "coming soon" anywhere on the website; the honesty moved to the point
of action rather than being deleted. See §8 for the exact build-and-copy commands and §9 for what is still
open. This file is what the pages promise, written by the markup lane so the JS
lane can build against it without reading four HTML files. The card DOM in §2 is
what `renderCard` emits.

⚠️ **THERE IS NO `bt-web.js` SHIM ANY MORE — the bundle itself carries that
name** (integration pass, deviation from the earlier plan, recorded here per §7).
`src/web/entry-web.ts` still exports `main()` without calling it, because the
checks import it in Node; the side effect lives in a three-line
`src/web/boot-web.ts`, which is what esbuild compiles, and the emitted entry is
named `bt-web.js`. So the file the five shells reference is the real bundle, not
a one-line module importing another file: one fewer published file, one fewer
round trip before first paint, and nothing hand-written in a public repo that no
check covers. The ENTRY name is stable (no hash) because the shells name it
literally; the chunks are hashed and nothing but the bundle names them.

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

Every page that has something to wire loads
`<script type="module" src="/assets/js/bt-web.js">` as the last element in
`<body>`. One module, four entry paths; branch on what is in the DOM, not on
`location`. Since 2026-08-19 that set includes `/b/` bill pages — for the back
control, which is the one thing on them a static file cannot do (§2c) — and
`main()` wires the site chrome (the nav pill and the back control) BEFORE it
branches, because those two belong to every page type rather than to any mount.

### 1.1 Feed page — `us.html`, `eu.html` (served as `/us`, `/eu`)

```html
<main class="feed-page" data-polity="us">
  <header class="feed-head"> … eyebrow, H1, intro, explainer link … </header>
  <!-- THE FEED BAR IS BUILT BY THE RUNTIME, not written here — see below. -->
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
  It may carry ONE extra paragraph under the state, `<p class="feed-status-notice">`,
  and only for the unsupported-legislature line (§3): that sentence is a fact
  about the BUILD rather than about this feed's emptiness, so it renders under
  whichever state is showing. `.feed-status p` already styles it; the class is a
  hook for the day it wants its own margin. (Added 2026-08-19 by the runtime
  lane — the app draws the same line, in the same place, for the same reason.)
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

**The feed bar (2026-08-20, SEARCH-JOB-SPEC §6–§8) is NOT in this shell, and
that is deliberate.** `src/web/feed-page.ts` builds it and inserts it after
`.feed-head`:

```html
<div class="bt-barwrap">                      <!-- sticky; the panel's containing block -->
  <nav class="bt-seg" aria-label="Legislature">…one <a> per registry entry…</nav>
  <div class="bt-bar">
    <search class="bt-search">…<input class="bt-q">…<button class="bt-clear"></button></search>
    <button class="bt-disp" aria-expanded="false">Display<span class="bt-dot"></span></button>
  </div>
  <div class="bt-filtered" hidden>…</div>     <!-- in flow: it must stay on screen -->
  <div class="bt-drop"  hidden>…</div>        <!-- absolute: the resting hint -->
  <div class="bt-panel" hidden>…</div>        <!-- absolute (fixed sheet on a phone) -->
</div>
<div class="bt-backdrop" hidden></div>
<p   class="bt-count" hidden></p>
```

* **The chips are the REGISTRY's, so the shell cannot hold them.** One `<a>` per
  `LEGISLATURES` entry, at its own `feedPath`; a template that wrote one chip per
  legislature would be the fifth per-legislature table this product spent a week
  deleting. Past four entries the same slot becomes a filterable menu.
* **They are plain links and they write NOTHING.** Switching legislature is
  navigation between two pages — it works without JavaScript, it is linkable, the
  back button is right, and a web selector that persisted a scope would silently
  change what the reader's phone shows (D25).
* **No `?q=` in the URL.** A query in the address bar puts what people search
  into history and into the `Referer` of the next click out to Congress.gov.
* `.bt-drop` and `.bt-panel` are absolutely positioned INSIDE `.bt-barwrap`
  because the bar is sticky: left in the page's flow they sit where the page was
  when they were drawn, and open the panel after scrolling and nothing appears.
* `.bt-filtered` is in flow inside the bar on purpose — a filtered feed that
  looks like the plain feed is a lie by omission, so it travels with the query.

### 1.2 Account — `account.html`

```html
<main class="account-page" id="bt-account">
  <section class="acct-region" id="bt-acct-loading"> … </section>
  <section class="acct-region" id="bt-acct-signed-out" hidden>
      <button id="bt-signin-google" class="btn-provider">Continue with Google</button>
      <button id="bt-signin-apple"  class="btn-provider">Continue with Apple</button>
      <p id="bt-provider-note" class="acct-note"></p>   <!-- EMPTY; only a failed sign-in fills it -->
  </section>
  <section class="acct-region" id="bt-acct-signed-in" hidden>
      <p id="bt-acct-email" class="acct-value"></p>
      <div id="bt-geo-picker"></div>     <!-- MOUNT: location picker -->
      <div id="bt-consent"></div>        <!-- MOUNT: consent status  -->
      <button id="bt-signout" class="btn-provider">Sign out on this device</button>
      <a href="/delete-account"> … </a>
  </section>
  <p id="bt-acct-status" class="acct-status" role="status"></p>
</main>
```

* Exactly one region visible: toggle the `hidden` attribute; `.acct-region[hidden]`
  is `display:none` in CSS, so nothing flashes.
* **The provider buttons ship LIVE, and `#bt-provider-note` ships EMPTY.**
  ⚠️ **CHANGED 2026-08-19** (owner directive: *"We shouldn't be building as
  though things are coming soon, we should be building to launch … honest, not a
  disabled button"*). They used to ship `disabled` under "Sign-in coming soon",
  gated by a compile-time `WEB_PROVIDERS` table in `src/web/auth.ts`. **That
  table is deleted.** Pressing a button now asks the Supabase project itself —
  GoTrue's public `/auth/v1/settings` (`external.google`, `external.apple`), one
  small `fetch`, no auth library — and:
  * provider ON → `signInWithOAuth`, and the browser leaves for the provider;
  * provider OFF → the button re-enables and `#bt-provider-note` says
    *"Google sign-in isn't available yet — we're still setting it up."*
    (`PROVIDER_UNAVAILABLE`, per provider);
  * could not ask → proceed anyway. "We could not check" is not "it is off",
    and a flaky connection must not be reported as a missing feature.

  Two things this buys beyond the copy. The answer is **the project's, not a
  constant's**, so the day the owner switches a provider on in the dashboard the
  website is correct with no code change, no build and no deploy — the failure
  mode `GOOGLE_OAUTH.configured` warns about ("a hand-set boolean is how a build
  claims to be configured when it is not") is gone. And the refusal happens **on
  our page, in our words**: `signInWithOAuth` cannot report it (it assigns
  `location` and returns `{error:null}` whatever the settings say — supabase-js
  2.110.7 `_handleProviderSignIn`), so without the probe a reader would land on
  GoTrue's own 400 page. The signed-out region ships `hidden`, so a reader with
  no JavaScript never sees a live-looking button a missing script has made inert.
  `check:webauth` fails if a compile-time provider table comes back, if the probe
  is removed, or if a refusal message reverts to "coming soon".
* Sign-out is `{ scope: 'local' }` — a browser sign-out must never kill the
  phone's session. **Settled, and not this file's to get right any more:** the
  bug was fixed in the app repo and the scoped call now lives in
  `src/lib/auth-core.ts`, platform-free, which the web imports rather than
  re-typing (`src/web/auth.ts` `signOutLocal`). `check:votes` pins the scope of
  both it and `deleteAccount`; `check:webauth` fails the build if any web module
  calls `auth.signOut(` for itself.
* `#bt-geo-picker` and `#bt-consent` are **mounts, not copy**. Location is
  account-level (set once, same on every surface); the consent sentence comes
  from `lib/voter.ts` `consentSentence()`, which lifts it VERBATIM from the
  published privacy policy through the D23 pipeline. Do not write a second
  wording here — the one the reader agreed to has to be the one we published.
  `CONSENT_VERSION` is what makes it answerable later.

  What lands in them (`src/web/geo-picker.ts`, `src/web/consent.ts`) — the CSS
  lane owns every class below, and none of them is styled yet:

  ```html
  <div class="geo-picker">
    <label class="geo-field"><span class="geo-label">Country</span>
      <select class="geo-select" name="country"> … "Not set" first … </select></label>
    <label class="geo-field" hidden><span class="geo-label">State</span>
      <select class="geo-select" name="us_state"> … </select></label>
    <p class="acct-note geo-status" role="status"></p>
  </div>
  ```

  Native `<select>`s on purpose: keyboard- and screen-reader-correct everywhere
  for free, and a phone renders them as the same native picker the app's sheet
  is. The state field is `hidden` unless the country is `US`.

  ⚠️ **The picker is DISABLED until the account has a `voters` row**, and says
  so. That row is the consent record and `setVoterLocation` UPDATES only —
  creating one here would record a consent nobody gave — so a write before the
  first vote would match zero rows, return no error, and look exactly like a
  successful save. **This is a real product gap, not a JS limitation**: the phone
  keeps a location locally and hands it up at the consent step, and the web has
  no such fallback by design (D27/§12(3): location is the account's). A reader
  who wants their first vote counted in their own state cannot currently set it
  first. Owner call — the fix is a product decision, not a patch.

  The consent mount renders **status only** — `Recorded` / `Not recorded yet`,
  the policy's own sentence, and the stored version string verbatim (never
  parsed back into a date). What consent *means*, how it is withdrawn and what
  re-consent looks like after a policy change stay in the published policy and
  remain an owner item (identity packet §8(3)).
* ~~Delete account keeps its own page (`/delete-account.html`); do not build a
  second deletion flow here.~~ **DEVIATION, recorded 2026-08-19 by the auth
  lane.** The plan is explicit that `/account` carries deletion ("delete account
  (existing Edge Function, CORS already allows the site) … required once accounts
  can be created on the web (Apple 5.1.1(v), D13)", §2), and once an account can
  be MADE here, the email route is a several-day wait for something the phone
  does in two taps. So the signed-in region grows an `.acct-delete` card, mounted
  by the JS above the existing link.

  What the rule was protecting is intact: there is no second *flow*. The card
  calls the same `deleteAccount()` in `lib/auth-core.ts` that the phone's sheet
  calls, renders the same `DELETE_ACCOUNT_COPY` from that module, arms in the
  same two steps, and shows the same Apple "one more step" notice from the same
  `appleFallbackNotice()` — which is also why it does **not** redirect away the
  moment the server answers: that notice is the only place a reader is ever told
  they still have a dead entry in their Apple ID settings. They leave by pressing
  **Done**. `/delete-account.html` stays exactly as it is; it is the route for
  somebody who no longer has any way to sign in, and it should gain a line about
  this one (owner/copy call, not a JS one).
* `#bt-acct-loading` carries a static second line saying what it means if the
  region never changes (the module failed to load — `<noscript>` does not fire
  for that). Replacing the region, which is what you do anyway, removes it.
* ~~**NOTHING LINKS TO `/account` YET.**~~ ⚠️ **SUPERSEDED 2026-08-19** — the
  owner made that call: *"How come there's no standard sign-in tab or page on the
  website? A yellow button seems like it could make sense."* **Every served page's
  nav now ends with a gold pill linking to `/account`**, and it is one block
  everywhere — the hand-authored pages, `tools/templates/feed-page.html`,
  `src/site/chrome.ts` (the generated `/p/` and `/b/` pages) and
  `site-build/generate_legal.py` (privacy + terms):

  ```html
  <a class="nav-signin" id="bt-nav-account" href="/account">Sign in</a>
  ```

  * **`style.css` styles it, never `feed.css`.** Every page loads the first;
    only card-drawing pages load the second, and a nav control missing on
    `/about` is not a nav control. Same rule sends `.back-link` there (§2c).
  * **The runtime relabels it, and only it.** With `bt-web.js` on the page,
    `src/web/site-chrome.ts` sets the word to `Account` when this browser holds a
    session — read from the **cheap storage probe**, never `getSessionState()`:
    labelling a nav item must not fetch 200 KB of auth library, least of all on a
    `/b/` page. Same href either way; `/account` is the page that answers both
    questions and says which one it is answering.
  * The card caption stays exactly what it was — the feed→account edge on a card,
    now reading `Sign in to vote` (§2b) — and carries `?next=` where the pill does
    not: the pill is on every page including ones `safeNext` would refuse.

  `check:sitenav` (app repo, in `npm run check`) fails the build if any served
  page carries zero or two account pills, or if any page's nav link set or ORDER
  differs from the one `src/site/chrome.ts` emits. Destinations are compared
  resolved, so this site's three spellings (`index.html`, `/index.html`, `/us`)
  compare as the pages they are.

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
  **One flagged deviation (runtime lane, 2026-08-19):** the moment the address
  PARSES as a `/p/`, `/b/` or `/bill/` target, `#bt-resolver-status` is replaced
  with "Looking for this in the published record…". From that moment the static
  "there is nothing at that address" may be false, and leaving a claim standing
  while actively disproving it is the one thing this page must not do. Everything
  else — the heading, the links, the note — is untouched until something is
  found. An address that does not parse still gets the page exactly as shipped.
* **On a hit, the eyebrow and the `<h1>` are hidden** (`hidden`, so the UA rule
  applies). "404 / Page not found" over a post that was just found is a page
  arguing with itself, and a bill render brings its own kicker and `<h1>`.
* **A client-rendered `/b/` page has no bill-page CSS here, and that is a known
  gap for the generator lane.** The `/b/` markup is `renderBillPath`'s — the
  same rows the generated page uses — but those pages carry their own inline
  `BILL_CSS` from `generate.py`, which `404.html` does not load, so the path
  renders as a plain, readable `<ol>`. Two ways out when the generator swaps to
  the shared renderer: move `BILL_CSS` into a stylesheet both pages link, or lift
  the row rules into `feed.css`. Until then this is degraded, not wrong.
* **`#ic-` glyph ids are bridged at runtime.** `renderBillPath` references the
  generated page's prefixed symbols (`#ic-capitol`); this page's inlined sprite
  uses bare ids. `dom.ts` `bridgeGlyphIds()` clones each missing `#ic-x` from
  `#x` before painting — because a `<use>` at a missing id paints nothing and
  reports nothing, which is the exact failure class §5 exists to prevent. It
  disappears the day the two stylesheets merge.
* `/p/<id>` or `/b/<polity>/<slug>` published but not yet rendered (the cron
  runs every 15 min) ⇒ draw it client-side into `#bt-resolver-mount`, so a link
  works the instant it exists. Legacy `/bill/<ref>` ⇒ resolve to the key and
  redirect **only when unambiguous**; otherwise say so and offer the choices.
  "Unambiguous" is only known once the WHOLE archive has loaded (the app's
  `/bill/[ref]` shim waits for the same reason — after a rollover the hot window
  shows the newer bill first), so the redirect waits for it; the pick rows name
  each bill's Congress (`congressOrdinal`, from the identity's own field) and
  title, because a rollover pair prints the same reference (verifier,
  2026-08-19; `.resolver-pick-title` in `feed.css` §5).

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

  <!-- Franchise variant of the head's left side. It rides INSIDE the same
       `.card-ref-row`, because a franchise post can carry a correction pill too
       (the app draws one in exactly that place) and the pill needs a flex row
       to sit in. Status cards put `.card-ref` in that row; franchise cards put
       this. (Recorded 2026-08-19 by the renderer lane — the original sketch
       showed this as a sibling of `.card-ref-row`, which left a corrected
       franchise card with nowhere to hang its pill.) -->
  <div class="card-ref-row">
    <p class="card-date-lead">
      <svg class="glyph" aria-hidden="true"><use href="#calendar-event-band"/></svg>
      8 August 2026 at 09:30 AM
    </p>
    <!-- pill, when the post carries one -->
  </div>

  <!-- 2. BODY — the ONLY collapsing region. data-clipped="1" when it overflows. -->
  <div class="card-body" data-clipped="1">
    <!-- status. HEADING LEVEL 2 (the page's h1 is the feed's title) and it
         carries the id the <article> is labelled by. -->
    <h2 class="card-title" id="t-<postPermalinkId>">A resolution commending …</h2>
    <p class="card-meta">Sen. Richard Durbin (D-IL) | Commerce, Science, and Transportation Committee</p>
    <p class="card-action">
      <svg class="glyph glyph-cal" aria-hidden="true"><use href="#calendar-event-band"/></svg>
      <!-- The separator's two-space padding is drawn with a literal U+00A0 in
           each pair rather than the `&nbsp;` entity — identical to a browser,
           and it keeps the renderer's escaping unconditional (nothing is
           spliced in raw). -->
      <span class="card-action-date"> 7 August 2026  |  </span>
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

  <!-- 2b. THE MATCH DISCLOSURE ROW — present ONLY on a search result whose
       match is not otherwise on the card (a summary is behind the expander by
       structure; a bodyLines hit can be past the clip). It is the IMMEDIATE
       next sibling of `.card-body`, which is load-bearing: feed.css collapses
       it with `.card-body:not([data-clipped="1"]) + .card-hit[data-field=…]`
       and with `.card.is-open .card-hit`, so no script has to decide what the
       reader can see. -->
  <p class="card-hit" data-field="bodyLines"><span class="lead">Match: </span>…a study of <mark class="bt-hit">AI</mark>-enabled toys…</p>

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
       THE STRIP GATES ON THE REFERENCE, THE BREAKDOWN GLYPH ON THE IDENTITY.
       ONE ROW: [glyph] [caption] … [chips]. ⚠️ `.vote-reason` IS A CHILD OF
       `.card-strip`, NOT OF `.vote-chips` — changed 2026-08-19, see rule 13. -->
  <div class="card-strip">
    <!-- ONLY when the card has a data-billkey. -->
    <button class="card-strip-glyph" aria-label="Vote breakdown">
      <svg class="glyph" aria-hidden="true"><use href="#chart-bar"/></svg>
    </button>
    <p class="vote-reason"></p>
    <div class="vote-chips">
      <button class="vote-chip" data-dir="up"   aria-pressed="false">▲ Yea</button>
      <button class="vote-chip" data-dir="down" aria-pressed="false">▼ Nay</button>
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
13. **The caption slot sits ON the chips' row, left of them.** `.vote-reason` is
   a direct child of `.card-strip` (`flex: 1 1 auto; min-width: 0`), between the
   breakdown glyph and `.vote-chips`. ⚠️ **MOVED 2026-08-19** — owner directive:
   *"it should be 'Sign in to vote' and it should be on the same row as the
   buttons and only appear when a user is not signed in."* It used to live INSIDE
   `.vote-chips` with `flex-basis: 100%`, taking a line of its own under them, on
   the argument that `NO_IDENTITY_REASON` is a full sentence and reads like an
   error toast when squeezed beside two pills. True of that sentence — and the
   caption a reader actually meets is four words, and it is the strip's primary
   invitation. It is also where the APP has always put it (`vote-chips.tsx`
   renders the caption as the third child of the chip ROW, `flexShrink: 1`), so
   the web was the outlier. `min-width: 0` is what lets the long refusal wrap
   inside the row rather than push the chips off the card; below 24rem the strip
   wraps and the caption takes the first line. An EMPTY slot collapses
   (`.vote-reason:empty`), so a signed-in reader's strip carries no hole.

---

## 2b. What the vote island adds to a card (`src/web/votes.ts`, `breakdown.ts`)

The island **wires the strip §2 already drew** — it never draws a second one.
Chips, their vocabulary, the disabled state and `NO_IDENTITY_REASON` all come
from `renderCard` (and, on `/p/` and `/b/`, from the generator emitting the same
DOM). What it adds is behaviour, plus the four small structures below. They were
written before the styling so the markup could be reviewed against a contract
rather than against a screenshot; **the styling landed on 2026-08-19**
(`feed.css` section 6), built against this spec and against the DOM the modules
actually emit. Everything below still describes the contract — change the class,
change this.

**1. The caption lives in the slot that is already there.** `.vote-reason` is one
slot with a fixed precedence, exactly as the app's is:

| state | what is in `.vote-reason` |
|---|---|
| no `data-billkey` | `NO_IDENTITY_REASON`, as rendered. The island does not touch it — there is nothing to sign in *for* on that post. |
| keyed, signed out | `<a class="vote-caption" href="/account?next=…">Sign in to vote</a>` — **always, on the web** (`VOTE_COPY.signIn`, imported). ⚠️ **CHANGED 2026-08-19**: it used to fall back to the app's interim wording while `WEB_PROVIDERS` said no provider was configured. That table is deleted (§1.2) — the honest answer is now given at the point of action, on `/account`, by the project itself. The PHONE still uses the interim wording; its gate is `GOOGLE_OAUTH.configured` and it is a separate owner call (`data/vote-copy.ts`). |
| keyed, signed in | empty. |
| after a failed write | the one-line note, then back to the row above. |

The caption is **persistent, not tap-triggered** (the app renders it the same
way). A chip tap by a signed-out reader adds `.is-pulse` to it for 800 ms and
does nothing else: the caption's words never change mid-tap (owner call
2026-07-23 — swapping instructions reads as scolding), and a chip tap must not
navigate, because the caption is the thing that navigates. **`.vote-caption` and
`.vote-caption.is-pulse` need a rule** — the app's is a dark letter-wave; a
single emphasis sweep is enough here. With no CSS the tap is silent, which is the
one thing this state must not be.

**2. The consent step, inside the strip that raised it** (`.vote-consent`,
`.vote-consent-text`, `.vote-consent-actions`, `.vote-consent-btn.is-agree`).
Shown once per account, before the first cast ever reaches the database, with
the policy's own sentence and two buttons from `lib/voter.ts` — never words
written for the button.

**3. The breakdown panel** opens in place, after `.card-strip`, when the
`.card-strip-glyph` is pressed (the island sets `aria-expanded` on it and toggles
on a second press; Escape closes and returns focus). It is a panel and not a
dialog on purpose: a page has room, and a focus trap is a heavier promise than
"show me the numbers". Classes: `.vote-breakdown[data-polity]` › `.vb-eyebrow`,
`.vb-title`, `.vb-message`(`-title`/`-body`) + `.vb-retry`, `.vb-stats` ›
`.vb-stat.is-inpolity` › `.vb-stat-label`/`-count`/`-split`, `.vb-coverage`,
`.vb-rows` › `.vb-row[data-group-start]` › `.vb-row-head` ›
`.vb-flag`/`.vb-badge.is-residual`/`.vb-label`/`.vb-you`/`.vb-split` ›
`.vb-split-down`/`.vb-total`, then `.vb-track` › `.vb-fill`, `.vb-more` ›
`.vb-more-btn`, `.vb-legend` › `.vb-dot.is-up`/`.is-down`, `.vb-foot`.

Two rules the CSS must not undo: **`n` is rendered beside every split and is not
decoration** (D14 — it is what keeps a one-person row honest, and hiding it to
tidy the row turns an honest row into a misleading one), and **there is never a
net score** — both sides, always, in the legislature's own words.

`.vb-fill` carries its width as a custom property, `style="--vb-fill:34%"`. Same
sanctioned exception as `--glyph-stroke` (rule 11): a per-row percentage cannot
be a class, and a custom property is data rather than a style rule.

**4. `.acct-delete`** and `.btn-provider.is-danger` on the account page (§1.2).

---

## 2c. The back control — `/p/`, `/b/`, and the resolver

Added 2026-08-19. Owner directive: *"When a bill path is accessed through a
post's bill ref link, the bill path should have a back button that goes back to
the feed … let's just use a large back arrow … Where is the standard arrow that
most modern sites, including X, use?"*

```html
<a class="back-link" href="/us" data-bt-back>
  <svg class="back-arrow" viewBox="0 0 24 24" width="22" height="22" fill="none"
       stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
       aria-hidden="true" focusable="false"><path d="M5 12l14 0M5 12l6 6M5 12l6 -6"/></svg>
  <span class="back-label">Back to the feed</span>
</a>
```

* **One definition** — `backControl(feedPath)` in the app's `src/site/chrome.ts`
  — used by the `/p/` template, the `/b/` template and the 404 resolver (which
  drew its own `Back to the <short> feed` line before). It replaced `&larr;`, a
  text glyph at body weight, which is exactly why it read as skinny.
* **The icon is INLINE, not a sprite symbol.** `tools/glyphs.svg` carries LABEL
  glyphs, is inlined per page under two id vocabularies (§5), and is a build
  input generated in the app repo. A chrome control does not earn all of that.
* **CSS in `style.css`, not `feed.css`** — `/b/` pages draw no cards and never
  load `feed.css`. 44px hit area, 22px arrow, navy, and the hover underline is on
  the LABEL only (a rule under the arrow makes it read as part of a word).
* **`data-bt-back` is the behaviour hook.** `src/web/site-chrome.ts` installs ONE
  delegated document listener (so a resolver-rendered control is covered without
  being wired) and calls `history.back()` **only** when `document.referrer` is
  same-origin AND its path is `/us` or `/eu` (`.html` stripped — Pages serves
  both spellings), on a plain left click. That is the only case where "back" is
  the feed, and it is what puts the reader back at their scroll position.
  Anything else — a cold link, a search result, a shared URL, no JavaScript,
  ctrl/⌘/shift/middle click — is the plain `<a href>` to the polity's feed.
* **`/b/` pages now load `bt-web.js`** for this (`island: true` in the bill page's
  `documentHtml`). It is the one thing on that page a static file cannot do, and
  it is the same cached bundle every other page already asks for.

### One departure from the packet's client spec, with its evidence

The vote/auth packet asked for `lock: navigatorLock` on the web client. **It is
not passed**, verified against the pinned `@supabase/supabase-js` 2.110.7 on
2026-08-19: `GoTrueClient` now calls the option a *"legacy opt-in path preserved
for backwards compatibility"* marked for removal in v3 and uses its own lockless
cross-tab coordination when none is given — and `navigatorLock` is not exported
by `@supabase/supabase-js` at all, only by the transitive `@supabase/auth-js`.
Reaching into a transitive package to satisfy a recommendation the library has
withdrawn is how a build breaks on a patch release. Everything else in that spec
is set, and set ONCE, in the app's `lib/supabase-core.ts`: PKCE, the explicit
storage key, `persistSession`, `autoRefreshToken`, `storage` left to the library
(browser `localStorage`). `check:webauth` fails if any web module sets `flowType`
or builds a client of its own.

---

## 3. `#bt-status` — the six honest states

Render **one**, in the app's order and in the app's words. ⚠️ **Since
2026-08-19 those words are not copied — they are IMPORTED.** The ladder moved out
of the screen into `app/src/data/feed-copy.ts`, which both surfaces consume
(D27), and `npm run check:web` executes it branch by branch; `web/status.ts`
renders the result. Do not re-type the table below into any page. Shape:

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
| 5 | docket filter on, nothing matches | `Nothing on your docket` | `There are recent posts, but none are for bills you follow or keywords you've saved. Turn off "My docket only" in the Display controls to see everything.` |
| 6 | display filters hide everything | `Nothing to show` | `Your display filters hide every recent post on this feed. Adjust the Display controls above.` |
| 7 | otherwise | `Nothing recent` | `There are no recent posts for Congress on this feed.` |

⚠️ **The remedies in 5 and 6 are the WEB's.** The app says "Turn off the docket
filter" and "Tap the filter icon above", because those are true on a phone; a
browser has a panel called Display and a switch called "My docket only", and a
sentence pointing at an affordance the reader cannot see reads as a broken page
rather than as a fact about the feed. One verdict, two ways out — `feedEmptyCopy`
takes the surface (2026-08-20). State 3's body also gained a second sentence
saying that words are matched whole, which is what makes `ai` returning two posts
explicable after the matcher change.

(Until 2026-08-20 states 5 and 6 had no web control at all and the branches were
kept anyway, "because the alternative is blaming the wrong thing when they
arrive". They arrived — the Display panel drives both, and `web/status.ts` now
passes the reader's real preferences instead of a hardcoded `false`/`true`.)

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
object-src 'none'; base-uri 'none'; form-action 'none'
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
* **`frame-ancestors` is NOT in the policy, and its absence is the honest
  state** (removed 2026-08-20, estate review R6). The directive is defined for
  HTTP headers only; in a `<meta>` policy every browser ignores it *and logs an
  error saying so on every page load*. It used to be carried "so the policy is
  complete the day this moves behind anything that can send headers" — but a
  directive that does nothing except print an error is not completeness. It
  reads as protection while providing none, and it fills this site's console
  with a line that teaches everybody to ignore the console.

  **There is no framing protection on this site today.** GitHub Pages cannot
  send headers, so there is nothing to put the directive *in*; the gap is
  recorded in the app repo's `docs/WEB.md` traps, and the directive comes back
  in the same edit that puts a real header in front of the site. What bounds it
  in the meantime is what the site actually offers: the only controls anywhere
  on it are the two sign-in buttons, "Sign out on this device", and a vote chip.
  Account deletion is **not a button on the web at all** — `/delete-account`
  is a page of instructions with no form and no script — so there is no
  one-click destructive action for a frame to steal a click on.

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

## 7b. The generated `/p/` pages draw cards too — and they draw them OPEN

`tools/bt-site.cjs` renders the same `renderCard` output onto every `/p/` page,
beneath the site chrome and above the archived post text (`tools/README-bt-site.md`).
Two consequences for this lane, recorded here by the site-renderer lane on
2026-08-19 because they are exceptions to §2 rule 3:

* A generated page ships its card **open**: its own `<style>` block sets
  `.post-wrap .card-deferred { display: block }`, un-caps `.card-body`, and
  hides `.card-expander`. A static page has no script to operate the control,
  and a control that does nothing is a fabricated affordance — while a page
  whose whole job is ONE post has nothing to gain by hiding half of it.
  **When the vote island mounts on `/p/` (Phase 3), do not re-collapse it** and
  do not wire the expander there; `wireCards` should skip a card inside
  `.post-wrap`. ✅ **Done 2026-08-19:** `main()`'s fallthrough calls
  `mountStaticIslands(document)`, which mounts the vote strips and nothing else,
  so no measurement ever touches a card the page has deliberately opened.
* Those pages load `/style.css` **and** `/assets/css/feed.css`, so the card is
  styled by exactly this lane's stylesheet. A change to `.card*` therefore
  reaches `/p/` too — the point of the arrangement, and worth knowing before
  scoping a rule to `.feed-page`. (`.feed-page :focus-visible` is scoped that
  way today, so a `/p/` card falls back to `style.css`'s gold ring; harmless,
  but the first thing to widen if that ring is ever judged too weak on white.)

## 8. Rebuilding — the shells, and the bundle

### 8a. The shells

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

### 8b. The bundle — `assets/js/bt-web.js` and `tools/bt-site.cjs`

Both are COMPILED ARTEFACTS of the private app repo. They are never edited here
and never built here: the build refuses to emit unless the app's own
`npm run check` is green, which is the whole reason a compiled bundle is allowed
to sit in a public repo at all (D27; `site-build/core/build.mjs`).

The two repos are siblings (`…/BillTracking/app`, `…/BillTracking/site`), and
both steps are run from the APP repo:

```sh
cd ../app
npm run build:core     # runs `npm run check` first and stops on red
npm run copy:site      # copies into ../site, prunes, and proves the copy
```

`copy:site` is `site-build/core/copy-to-site.mjs` in the app repo. It copies
`out/web/*.js` into `assets/js/` and `out/site/bt-site.cjs` into `tools/`,
deletes the chunks nothing needs any more, writes `assets/js/.chunks-prev`, and
finishes by running `node tools/bt-site.cjs --selftest` from this repo's root —
exactly the way `permalinks.yml` will run it fifteen minutes later. It commits
nothing and pushes nothing: **push is deploy**, and that stays a person's
decision.

It refuses, rather than publishing something wrong, when `out/` is missing, when
the build's stamp names a different commit than the app tree is on, or when
anything under the app's `src/` was touched after the build ran. All three mean
the same thing — the bytes are not what this tree would build — and the site
prints that stamp on every page.

Four rules the copy obeys:

* **`*.js` ONLY — never a `*.map`.** esbuild's source maps embed
  `sourcesContent`, which for this bundle is the whole of the app's TypeScript
  *including its comments*: copying them here would publish the private repo's
  source. The build emits maps as `sourcemap: 'external'` so the published files
  carry no `//# sourceMappingURL` pointer either — no leak, and no 404 in
  anyone's devtools. The maps stay in the app repo, where `out/` is gitignored.
  `copy:site` copies `.js` only *and then checks* that no `.map` is sitting in
  `assets/js/` or `tools/`, refusing if one is.
* **The entry name is stable, the chunk names are not.** `bt-web.js` is
  referenced literally by `us.html`, `eu.html`, `account.html`,
  `auth/callback.html`, `404.html`, `tools/templates/feed-page.html` and every
  generated `/p/` page — and, since 2026-08-19, every generated `/b/` page too
  (§2c). The chunks are content-hashed, so something has to remove the dead ones
  or the directory grows for ever.
* **…and the PREVIOUS generation of chunks survives one deploy.** This is why
  the old recipe's `rm -f assets/js/bt-*.js` is gone: it deleted the chunks that
  readers were still using. A browser holding a cached `bt-web.js` — or a tab
  that has been open since before the deploy — imports chunks by the hashed
  names the *old* build gave them, and sweeping them all makes those URLs 404:
  sign-in breaks where the dynamic import fails, and the page never boots at all
  where a static one does. `copy:site` keeps the union of the new generation and
  the one it replaces, and deletes only `bt-*` chunks in neither.
  `assets/js/.chunks-prev` is how it remembers which those were — a small JSON
  manifest of the two most recent generations, committed with them. Deleting it
  costs one generation of grace and nothing else; it is served (this repo has a
  `.nojekyll`) and carries only filenames and the app's short commit sha, both
  of which the bundle's own build stamp already publishes.
* **Bundle and HTML ship together** (§9). Never the HTML first.

### 8c. Rendering the pages locally (what CI does)

```sh
mkdir -p /tmp/feed /tmp/paths
# month files since 2026-07 for us+eu + both -overrides.jsonl, from
#   https://billtrackingorg.github.io/billtracking-feed
node tools/bt-site.cjs --feed /tmp/feed --list-paths      # which artifacts to fetch
node tools/bt-site.cjs --feed /tmp/feed --paths /tmp/paths --out /tmp/out
```

`--out` is required and must NOT be this repo: `p/`, `b/` and `view/` are
workflow-owned trees. Serve `/tmp/out` over the working tree to look at it.

---

## 9. What to carry into the cut-over

* **Push ordering is load-bearing.** `/us` paints head → "Loading…" → footer and
  stops until `bt-web.js` exists. Pages caches HTML for ten minutes, so an HTML
  push that lands without the bundle gives every visitor a `role="status"` that
  says "Loading…" and never changes — the page telling a lie about itself, for
  ten minutes minimum. Ship the bundle in the same push as the HTML, or before.
  The same ordering binds `tools/bt-site.cjs`: `permalinks.yml` now runs it and
  fails loudly every 15 minutes if it is not there, so the bundle must land in
  or before the push that merges the workflow.
* **`/auth/callback` resolving from `auth/callback.html` is asserted, not
  proven.** Pages' extensionless resolution is the same rule the site already
  relies on, but it has not been probed for a file one directory down. The OAuth
  redirect URI is registered exactly once and a 404 there breaks sign-in
  completely: probe the live URL at Gate B, before the provider config is
  written.
* **The stylesheet is versioned by hand, and only on the shells.** The five
  hand-authored pages ask for `/assets/css/feed.css?v=7`; the generated `/p/`
  pages ask for `/assets/css/feed.css` with no query at all. Same file, two cache
  entries. It is harmless before the first publish (nothing holds either yet),
  but from the first publish on, ANY edit to `feed.css` needs the query bumped in
  the template + the four hand-authored shells, or returning visitors keep the
  old sheet. **`?v=1` → `?v=2` on 2026-08-20** with the `.card-open` hit-area fix
  (estate review R2) — pre-publish, so it defeated nothing, and done anyway
  because the habit is what has to hold after the cut-over, not the arithmetic.
  **`?v=2` → `?v=3` (with style.css `?v=3` → `?v=4`) later that day** with the
  `.feed-page` min-height and the cross-document view transitions; **`?v=3` →
  `?v=4` the same evening** with the refusal pulse going gold (`--gold-wash`);
  **`?v=4` → `?v=5` the same night** with the desktop scroll-lock revert (the
  cap is phone-only now — owner ruling); **`?v=5` → `?v=6` right after** — the desktop panel cap (and its internal scrollbar) removed with it; **`?v=6` → `?v=7` on 2026-08-21** with the scroll CLAMP (the owner's spec: page scrolls to the bar's park point then holds; panel cap + overflow restored as the tall-panel fallback).
  ⚠️ A section of this file was once lost to `git checkout -- assets/js` run to
  reset the BUNDLE — this README lives in assets/js but is hand-maintained, so
  reset the chunk files by name, never the directory.
  Worth collapsing to one form at the cut-over.
* **A client-rendered `/b/` path on `404.html` is unstyled.** `renderBillPath`'s
  markup is styled by `BILL_CSS`, which lives inside the generated bill page's
  own `<style>` block (app repo `src/site/chrome.ts`) and cannot reach the
  hand-authored 404 page. The resolver's bill render is therefore a plain,
  readable `<ol>` — degraded, never wrong, and it self-heals within one workflow
  run when the real page appears. The clean fix is the one `chrome.ts` already
  names: move the bill-path rules into `feed.css` (which `404.html` loads) and
  let the generated page load `feed.css` instead of inlining a second copy —
  which also collapses the `#ic-` sprite prefix and `dom.ts`'s `bridgeGlyphIds`.
  One job, not a drive-by.
* **`/b/` pages carry `data-billkey` and no vote strip.** Plan §2 promises the
  bill page a vote island; the bill-path content model has no strip today, and
  the app's own bill screen shows chips only on the post cards it embeds. The
  attribute is already on `<main class="bill-wrap">`, so the day a strip is drawn
  the island wires it with no new transcription. Deliberately not invented here.

---

## 10. What the integration pass changed in this contract (2026-08-19)

Recorded here because §7 says a deviation is written into this file in the same
edit that makes it.

1. **`bt-web.js` is the bundle, not a shim** — see the Status block at the top.
2. **Generated `/p/` pages load the runtime.** `documentHtml` grew an `island`
   flag (app repo `src/site/chrome.ts`) and post pages set it, so a `/p/` page
   ends with the same `<script type="module" src="/assets/js/bt-web.js">` the
   shells carry. Without it those pages drew two enabled vote chips that answered
   nothing — a fabricated affordance, and the very thing §7b's argument for
   un-collapsing the static card is about. Index pages and `/b/` pages set it
   `false`: neither has a control only a browser can work.
3. **§7b's request is honoured by a named entry point, not by a special case in
   the measurer.** `main()`'s fallthrough calls `mountStaticIslands(document)`
   (votes only) rather than `mountIslands` (votes + card wiring), so nothing
   re-measures a card whose own stylesheet has lifted the clip and hidden the
   expander.
4. **§2b's classes now exist in `feed.css`** (its new section 6). Two of them
   were reachable by any visitor with nothing to draw them: `.vote-caption.is-pulse`
   (a signed-out chip tap was completely silent) and `.vote-breakdown` (the door
   beside the chips opens for everyone, signed in or not, and drew unstyled text
   under the card). The consent, geo and delete rules are written from the same
   spec but cannot be exercised until a provider and the migration exist.
