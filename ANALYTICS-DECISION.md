# Analytics decision — billtracking.org

**Status:** decided, ready to implement before launch
**Date:** 2026-07-19
**Applies to:** the public site at billtracking.org (GitHub Pages). Not the mobile app.

---

## 1. The recommendation

**Use Cloudflare Web Analytics, installed with the manual one-line snippet.**

Free, no traffic limit, no cookies, no browser storage, no account fee, one line of HTML pasted into six files. Nothing else to run, nothing to maintain, nothing to renew.

That is the whole decision. You do not need to choose between options, run a trial, or compare dashboards. Paste the line, launch the site, look at the dashboard in October.

### Why this one and not the others

This reverses an earlier draft recommendation of GoatCounter. The reversal is deliberate and is the single most important thing in this document, so here is the reasoning in plain terms.

**GoatCounter — rejected.** Its privacy page says it stores nothing in the browser. Its actual shipped tracking script disagrees: it writes and reads a `skipgc` value in the browser's localStorage, and it reads your visitor's screen width and sends it back along with the full query string of the URL. Each of those three things is exactly the kind of device contact that European cookie law (ePrivacy Article 5(3), which in Poland is Article 399 PKE) is about — and that law applies to *any* information touched on the device, not just personal data or cookies. Writing to localStorage is storage; reading it back is access; reading screen width is reading a device characteristic. So the "no consent banner needed" claim that made GoatCounter attractive rests on a marketing sentence that the vendor's own code contradicts. On top of that: no data-processing agreement (GDPR Art 28 requires one), a single maintainer with no successor, and a free tier that is stated goodwill rather than contract. It is a nice project run by a good person. It is not the right dependency for a site whose entire pitch is accuracy.

**"No analytics at all" — rejected.** Genuinely tempting, and the cleanest possible privacy posture. But the whole point of the September outreach is to learn whether emailing law professors works. Sending 200 emails and having literally no idea whether anyone visited is not a privacy win, it is flying blind on the one decision this project needs data for. The measurement described below is aggregate, storage-free, and modest enough that "no analytics" buys you very little extra protection.

**Reading server logs — impossible.** GitHub Pages does not give site owners access logs. The "Traffic" tab in a GitHub repository counts views of the *repository*, not of the website. This is a common confusion and worth knowing so you do not go looking.

**Putting Cloudflare's proxy in front of the site (DNS change, zero JavaScript) — rejected, narrowly.** This was seriously considered because it would be the strongest possible legal position: nothing at all runs on the visitor's device. Two things killed it. First, on Cloudflare's free plan the proxy-level traffic view gives you requests, unique visitors and countries — but **not referrers or page paths**, and referrer is your critical signal. Second, moving your nameservers away from Namecheap also moves your email records, and a mistake there silently breaks `contact@` and `accuracy@`. That is a real risk for a one-person project with no test environment. Not worth it for a weaker dataset.

**Plausible, Fathom, Matomo, Tinylytics — rejected on price.** All are good; all cost real money (roughly €100–€350/year). Self-hosting any of them needs a server, a database, TLS certificates and ongoing patching. That is a second project, and a new thing that can be broken into.

**Simple Analytics, Umami — rejected as unverified.** Both advertise free tiers whose limits I could not confirm from the vendors' own pages (their pricing pages render in the browser, and the numbers circulating online come from AI-written review sites). Umami's cloud is partly US-hosted with no documented EU-only guarantee. Neither is worth the uncertainty when a better-documented free option exists.

### One correction to the record

An earlier draft rejected Cloudflare because it "samples at ~10%, so a real visit shows as ten visits or as zero." That was a misreading. Cloudflare's own FAQ says the opposite of what was concluded: *"Sites with very low traffic volumes are sampled to greater percentages to maintain high confidence in aggregate figures,"* and *"The data ingestion pipeline does not apply sampling — every received beacon will be recorded."* The ~10% figure is a long-term storage aggregation applied to high-volume data after seven days. A site getting dozens of visits a week is in the "effectively 100%" band. Sampling is not a problem for you. If this project ever gets big enough for sampling to bite, that is a good problem and a reason to revisit.

---

## 2. What you will actually be able to see

Everything in the left column is the thing you said you need.

| You need | Do you get it? | Where |
|---|---|---|
| How many people visited | **Yes** — page views and visits, by day | Dashboard, main chart |
| Which pages they looked at | **Yes** — a ranked list of paths (`/educators.html`, `/accuracy.html`, …) | "Top pages" |
| **Where they came from (referrer)** | **Yes** — ranked list of referring sites; direct/none shown as its own bucket | "Referrers" |
| Roughly what country | **Yes** — country level | "Countries" |
| Clicks through to the app stores | **Not directly** — Cloudflare has no click-event feature. Solved with redirect pages, see step 5 below | "Top pages" |
| Trends over time | **Yes** — date range selector, day by day | Dashboard |
| Browser / operating system / desktop-vs-mobile | Yes, as a by-product | Dashboard |

What you will **not** get, by design and permanently:

- No individual visitors. There is no "user" in this system, no visitor ID, nothing to click into.
- No journeys or paths through the site. You will know 40 people saw `/educators.html` and 12 saw `/accuracy.html`. You will never know whether they were the same 12.
- No returning-visitor identification. Someone who visits three times over three weeks is three visits, not one person visiting thrice.
- No demographics, interests, age, gender, or any inferred audience characteristic.
- No session recording, heatmaps, or scroll tracking.
- No cross-site tracking. Cloudflare Web Analytics does not follow anyone anywhere else.
- No query strings. Cloudflare deliberately does not log anything after a `?` in the URL. This is a feature — see the note on campaign links in step 5.

**Bottom of the funnel:** once the app is published, App Store Connect and Google Play Console both give you free, first-party install numbers and acquisition-source data — including which websites referred people to your store listing. That is the one measurement no website analytics can ever see, and you already have it, at no cost and with no extra tooling.

---

## 3. Do you need a cookie banner?

**No. Confidence: high, but this is a legal position, not a certainty. No court in the EU has ruled on it.**

Here is the honest breakdown, separated into what is settled and what is not, so you can hand this to a lawyer without it looking like marketing.

### Settled — not seriously disputed by anyone

- The cookie rule (ePrivacy Art 5(3); in Poland, Art 399 PKE, in force since 10 November 2024) applies to **storing information on, or reading information from, a visitor's device** — regardless of whether the information is personal data. "We're anonymous, so no banner" is a non-argument. This is why so many "GDPR-compliant, no consent needed" vendor claims are wrong.
- "Cookieless" has **no legal meaning**. localStorage, sessionStorage, IndexedDB and browser fingerprinting are all covered. Reading without writing counts too.
- Anonymising data *after* you have touched the device does not fix having touched the device.
- Genuinely anonymous aggregate statistics fall outside GDPR entirely (Recital 26).
- Your GDPR supervisory authority is **UODO** in Poland, because you are established there.

### Why Cloudflare Web Analytics clears that bar

The beacon script:

- sets **no cookie**;
- writes **nothing** to localStorage, sessionStorage, IndexedDB or any other browser storage (I checked the shipped script directly — no reference to any of them);
- generates **no visitor identifier**, on the device or anywhere else;
- does **no fingerprinting** — no canvas, no font enumeration, no screen or hardware reads;
- does **not** send the query string, so campaign identifiers and UTM tags are never collected even if someone else appends them;
- determines a "visit" server-side by comparing the referrer's host to your host, which needs no state on the device at all.

Because nothing is stored on and nothing is read from the device, the Article 5(3) rule is not engaged. When the rule is not engaged, you do not need consent and you do not even need to argue about exemptions.

The remaining data — the visitor's IP address, which Cloudflare uses to derive a country and does not store — is processing under GDPR, covered comfortably by legitimate interest (Art 6(1)(f)): minimal, not stored, no impact on anyone, entirely expected. Two recent rulings help here: the CJEU in *EDPS v SRB* (C-413/23 P, 4 September 2025) confirmed that whether data is "personal" depends on whether *you specifically* can realistically re-identify someone; and Poland's Supreme Administrative Court (III OSK 2595/22, 16 October 2025) held that IP addresses are not automatically personal data and that the burden of proving identifiability sits with the regulator.

⚠️ **Verify that Polish judgment with a lawyer before quoting it.** I have it from research that did not link a primary source, and Polish administrative judgments are hard to check in English. The conclusion does not depend on it — it is supporting weight, not load-bearing.

### The one honest wrinkle — flag this to a lawyer if you ever get one

Cloudflare's beacon reads page-load timing values from the browser's Performance API and sends them back. Those values are produced on the device. A maximally strict regulator could argue that reading them is "gaining access to information in terminal equipment." I think that argument is weak — performance timings are not an identifier, cannot single anyone out, and no regulator has ever enforced on that basis — but it is not zero, and I would rather you knew about it than discovered it later. It is the only residual point.

### Also contested (context, not a problem for you)

- The EDPB has suggested (Guidelines 2/2023, para 50) that merely *caching* a delivered resource counts as "storage." Read literally that would make every image on every website a consent event, which cannot be right. It is heavily criticised and untested in court.
- Whether hashed or rotating-IP identifiers count as anonymous is unsettled. **Not your problem** — the recommended setup creates no identifier of any kind.

### In flight

The EU's **Digital Omnibus** proposal (November 2025) would move the cookie rule into GDPR with an explicit exemption for aggregate audience measurement — i.e. it would put exactly your use case on a clear statutory footing. It is a proposal, years away. Do not build around it; just know it is trending your way.

### Practical conclusion

Ship without a banner. Publish the transparency note in section 7 instead. For an audience of law professors, a short honest "here is what we count and what we deliberately refuse to count" page is worth far more than a consent pop-up, and a consent pop-up on a trust-positioned site actually reads as *worse*.

---

## 4. Google Analytics: what is actually on the site

**There is no Google Analytics on billtracking.org. There never was. There is no JavaScript on the site at all.**

I checked all 13 HTML files. There is not a single `<script>` tag anywhere, and no `.js` file exists in the repository. Every `<head>` loads exactly three things, all local: a favicon, an apple-touch-icon, and `style.css`.

**So there is nothing to remove.** What needs fixing is three documents that describe a GA4 install that does not exist. Left uncorrected, these would make your published privacy policy factually false on its first day — the worst possible failure mode for this project.

### Verify it yourself in 30 seconds

Do this rather than taking my word for it. It is the check that would have caught the GoatCounter problem.

1. Open the site (or a local copy) in Chrome or Edge.
2. Press `F12` to open developer tools.
3. Click the **Application** tab → in the left sidebar, **Storage**.
4. Look at **Cookies**, **Local storage**, and **Session storage**. All three should be empty.
5. Click the **Network** tab, tick **Disable cache**, reload the page. Every row should be a `billtracking.org` address (or your local file). Nothing from Google, Cloudflare, or anywhere else.

**Run this same check again after you paste the analytics snippet.** The only change you should see is one request to `static.cloudflareinsights.com` and one to `cloudflareinsights.com/cdn-cgi/rum`. Storage must still be empty on all three. If it is not, stop and re-read this document.

### The three documents to correct

| File | Line | What it wrongly says | Fix |
|---|---|---|---|
| `site/README.md` | 47–49 | "confirm the GA4 tag is still on every page" in the site-change checklist | Replace with: confirm the Cloudflare Web Analytics snippet is still on every page, and re-submit the sitemap |
| `site/legal-drafts/PRIVACY-POLICY-DRAFT.md` | 231–232 | "uses Google Analytics 4, with a notice and an opt-out available on the site" | Replace with the drafted text in section 7 |
| `site/legal-drafts/PRIVACY-POLICY-DRAFT.md` | 216 | table row: `Website analytics (GA4) | Consent, via the notice and opt-out on the site` | Replace with: `Website analytics | Legitimate interest (Art 6(1)(f)) — aggregate counts only, no device storage` |
| `site/legal-drafts/REVIEW-NOTES.md` | 59–61 | "GA4 is the only confirmed personal-data flow in the entire project" | Mark resolved: premise was factually wrong, no GA4 exists; the reviewer's legal reasoning was sound but applied to a flow that never existed |
| `site/legal-drafts/PRIVACY-POLICY-DRAFT.md` | 234, 434 (open question 16.5) | "whether the mobile app contains analytics is not confirmed" | Answer it: the app's `package.json` contains no analytics, telemetry, crash-reporting or attribution SDK of any kind. No Firebase, Sentry, Amplitude, AppsFlyer, Adjust, PostHog or equivalent |

Note the current draft promises "an opt-out available on the site." **Do not promise an opt-out you cannot technically deliver.** See section 7 for wording that is both honest and stronger.

---

## 5. Implementation — step by step

Total time: about 20 minutes. Do it before you point the domain at GitHub Pages, so there is never a window where visitors are counted without the notice being live.

### Step 1 — Create the Cloudflare account

1. Go to `https://dash.cloudflare.com/sign-up`.
2. Sign up with your `contact@billtracking.org` address (not a personal address — this belongs to the project).
3. Confirm the verification email. **Do not** add your domain, do not change nameservers, do not buy anything. Web Analytics does not need any of that.

### Step 2 — Add the site in Web Analytics

1. In the left sidebar choose **Analytics & Logs → Web Analytics**.
2. Click **Add a site**.
3. Enter the hostname: `billtracking.org`.
4. Choose the **manual / JS snippet** option (not automatic — automatic requires proxying your DNS through Cloudflare, which we decided against).
5. Cloudflare shows you a snippet containing a long token. Copy it.
6. Leave "Exclude EU visitor data" **off**. Your audience is largely EU; switching it on would blind you to most of your traffic, and you do not need it — the setup is lawful as it stands.

### Step 3 — Paste the snippet into every page

The snippet looks like this. **Use the one Cloudflare gives you** — the token below is a placeholder and will not work:

```html
<script defer src="https://static.cloudflareinsights.com/beacon.min.js" data-cf-beacon='{"token": "PASTE_YOUR_TOKEN_HERE"}'></script>
```

Paste it **immediately before the closing `</body>` tag** in each of these six files:

- `index.html`
- `about.html`
- `accuracy.html`
- `educators.html`
- `eu-process.html`
- `us-process.html`

So the bottom of each file goes from:

```html
  </footer>
</body>
</html>
```

to:

```html
  </footer>
  <script defer src="https://static.cloudflareinsights.com/beacon.min.js" data-cf-beacon='{"token": "PASTE_YOUR_TOKEN_HERE"}'></script>
</body>
</html>
```

**Also add it to the generated permalink pages.** Those are built by `build/generate.py`, so add the same line to the page template inside that script rather than editing the generated files by hand — otherwise it will vanish the next time you rebuild.

Take care with the quotes: the outer quotes on `data-cf-beacon` are **single** quotes and the inner ones are **double**. Copying from Cloudflare directly avoids the problem.

### Step 4 — Verify

Run the 30-second DevTools check from section 4. Then wait a few minutes, visit a couple of pages yourself, and confirm they appear in the Cloudflare dashboard. Data appears within minutes, not days.

### Step 5 — Measure the clicks that matter, without any tracking

Cloudflare Web Analytics cannot record clicks on outbound links. There is a simple, storage-free way around it that works on plain GitHub Pages: send outbound clicks through a page on your own site first.

Create small pages:

- `go/ios/index.html`
- `go/android/index.html`
- `go/x-us/index.html`
- `go/x-eu/index.html`

Each one contains a meta refresh and a visible fallback link:

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Opening the App Store — BillTracking</title>
  <meta name="robots" content="noindex">
  <meta http-equiv="refresh" content="2; url=https://apps.apple.com/app/idYOURAPPID">
  <link rel="stylesheet" href="/style.css?v=2">
</head>
<body>
  <main style="padding:4rem 1.5rem;text-align:center">
    <p>Opening the App Store&hellip;</p>
    <p><a href="https://apps.apple.com/app/idYOURAPPID">Continue to the App Store</a></p>
  </main>
  <script defer src="https://static.cloudflareinsights.com/beacon.min.js" data-cf-beacon='{"token": "PASTE_YOUR_TOKEN_HERE"}'></script>
</body>
</html>
```

Then change the buttons on your pages from `href="https://apps.apple.com/..."` to `href="/go/ios/"`.

Now `/go/ios/` shows up in your "Top pages" list, and its count *is* your click-through count. No event tracking, no identifiers, no JavaScript click handlers, nothing stored. Add `Disallow: /go/` to `robots.txt` so search engines do not inflate the number.

Two seconds of delay is a small tax; the alternative is no conversion data at all. If you would rather not add the friction, skip this and rely on App Store Connect / Play Console referrer data instead — but then you cannot measure clicks to X, which is your only conversion point until the app ships.

**Today's reality check:** there are no app-store links on the site yet. Your only conversion points right now are the X profile links (17 to `x.com/USBillTracker`, 15 to `x.com/EUBillTracker`) and the educator kit download. Set up `/go/x-us/` and `/go/x-eu/` now; add the store ones when the app is live.

### Step 6 — Campaign tracking without campaign parameters

Most email clients strip the referrer, so outreach traffic will otherwise arrive as "direct" and be indistinguishable from someone typing your URL. Do **not** solve this with `?utm_source=` tags — Cloudflare does not log query strings, so they would not work anyway, and they are precisely the identifier-in-URL pattern that the cookie rules are most hostile to.

Solve it with **a distinct page path per outreach wave**. For example, link September's emails to `/educators.html` and a later wave to `/teaching/` (a real page with real content, its own entry in the sitemap). The path then tells you which wave someone came from, and it tells you nothing whatsoever about *who* they are. It also degrades gracefully: if someone forwards the link, you learn the campaign spread, not that a person did the forwarding.

This is my analysis, not a published regulator position — a URL path is content the visitor requested, not an identifier attached to their device — but it is structurally much safer than UTM parameters and worth a lawyer's eye if you ever get one.

### Step 7 — Publish the transparency note

Add `privacy.html` using the text in section 7, and link it from the footer on every page. **Do this in the same commit as the snippet**, so the notice is live from the first visitor.

---

## 6. Third-party resources on the site

**Good news, and it is genuinely unusual: the site currently loads zero third-party resources.** Every byte a visitor fetches comes from `billtracking.org`. No visitor IP is disclosed to anybody by loading a page. You already avoided the hard problem — a Google Fonts link or an embedded tweet leaks visitor IP addresses to a third party on every single page load, no matter what analytics you choose, and fixing that afterwards is painful. You do not have to.

| Resource | Status | Action |
|---|---|---|
| Fonts (Public Sans, Source Serif 4) | **Self-hosted** as local `.woff2` in `assets/fonts/`, declared inline in `style.css`. No `fonts.googleapis.com`, no `fonts.gstatic.com` | **None.** Correct as-is. Do not ever swap these for a Google Fonts `<link>` |
| CSS imports | None. `style.css` has no `@import`; its only `url()` references are the three local fonts | None |
| Scripts / CDNs / tag managers / pixels | None exist | None — until you add the one line above |
| Iframes, embeds, video | None | None |
| X / Twitter content | **Hand-built static HTML mockups** with local avatar images. No `platform.twitter.com/widgets.js`, no `blockquote class="twitter-tweet"` | **None — and keep it this way.** The official X embed loads third-party JavaScript and sets cookies on your visitors. It would single-handedly do more privacy damage than every analytics option in this document combined |
| Images, banners, QR codes | All local (`assets/*.webp`, `assets/kit/qr-*.png`) | None |
| Outbound links (`x.com`, `congress.gov`, `oeil.europarl.europa.eu`, `mailto:`) | Links only — nothing loads until clicked | None |
| `assets/fonts/fonts-local.css` | Dead file. Duplicates the `@font-face` rules already inline in `style.css`; linked by nothing | Delete it, or add a comment saying it is unused. Harmless either way |

**The one thing that changes.** Adding the Cloudflare snippet means the site loads its first third-party resource, and visitor IPs reach Cloudflare, a US company. Be clear-eyed about this rather than pretending otherwise:

- GitHub Pages already hosts the site, so **Microsoft/GitHub — also a US company — already receives every visitor's IP address on every request**. You cannot use GitHub Pages and have zero US processors. Cloudflare does not change the category; it adds one more.
- Cloudflare provides a real, public data-processing agreement under GDPR Art 28, Standard Contractual Clauses, and Data Privacy Framework certification. GoatCounter provides none of these, which is one more reason for the reversal.
- The DPF's validity is on appeal to the CJEU (*Latombe*, C-703/25 P) after the General Court upheld it on 3 September 2025. Worth knowing; not a reason to wait.

**Two unrelated launch blockers, since they touch the same files:** `.well-known/apple-app-site-association` and `.well-known/assetlinks.json` still contain `REPLACE_` placeholders, and the pages under `p/` are built from synthetic sample data. Publishing fabricated bill pages on an accuracy-positioned site would be far more damaging than any analytics decision. Neither is an analytics matter, but neither should go live.

---

## 7. What to write in the privacy policy

### For the site — `privacy.html`, linked from the footer of every page

> ## What this site measures
>
> BillTracking measures how many people visit this site, which pages they read, roughly which country they are in, and which websites link to us. We use this for one purpose: to find out whether telling people about this project actually reaches anyone.
>
> We use Cloudflare Web Analytics. It works differently from most analytics:
>
> - **It stores nothing on your device.** No cookies. No local storage. Nothing is written to your computer or phone and nothing is read from it.
> - **It does not identify you.** There is no visitor ID, no fingerprint, no account, no profile. We cannot tell whether two page views came from the same person, and we have no way to find out.
> - **We never see your IP address.** Cloudflare uses it to work out which country a visit came from and then discards it. It is not stored and it never reaches us.
> - **We do not see anything you typed.** Anything after a `?` in a web address is discarded before it is recorded.
> - **We cannot follow you.** This measurement stops at the edge of this website. There is no tracking of you across other sites, no advertising network, and nothing is shared with one.
> - **There is no recording.** No session replay, no heatmaps, no scroll or mouse tracking.
>
> What we hold is a set of daily counts: 40 people read the accuracy page on Tuesday; 12 arrived from a university website. Nothing in it points to a person.
>
> **We are not required to show you a cookie banner, because we do not use cookies or store anything on your device.** That is why you have not seen one. We would rather explain what we do than ask you to dismiss a pop-up.
>
> **If you would rather not be counted at all,** any content blocker or privacy-focused browser will stop it — the script is loaded from `static.cloudflareinsights.com`. Blocking it changes nothing about how this site works for you.
>
> **The mobile app contains no analytics at all** — no telemetry, no crash reporting, no attribution or advertising SDK of any kind.
>
> Questions: contact@billtracking.org

*(That "if you would rather not be counted" line is deliberately worded as something you can actually deliver and a visitor can actually verify. Do not replace it with a promise of an opt-out toggle unless you build one.)*

### For `PRIVACY-POLICY-DRAFT.md` — replacing the GA4 passages

> **Website analytics.** The website billtracking.org uses Cloudflare Web Analytics. It sets no cookies and stores no information on the visitor's device. It generates no visitor identifier and performs no fingerprinting. Cloudflare Inc. acts as processor and derives an approximate country from the visitor's IP address without storing it; no IP address is retained by, or made available to, the operator. Query strings are not collected. The data retained is aggregate: page views, visits, referring sites, countries, and browser and device categories, by day. No individual visitor can be identified or singled out from it.
>
> **Legal basis.** Legitimate interest (Art 6(1)(f) GDPR) in understanding whether the site reaches its intended audience. The processing involves no storage on or access to terminal equipment, and so does not engage Art 5(3) of Directive 2002/58/EC as transposed in Art 399 of the Polish Prawo komunikacji elektronicznej. No consent is required and none is sought.
>
> **Mobile application.** The BillTracking mobile application contains no analytics, telemetry, crash-reporting, attribution or advertising software of any kind.

And in the table at line 216:

> `| Website analytics | Legitimate interest (Art 6(1)(f)) — aggregate counts only, no device storage, no identifier |`

### One inconsistency to resolve first

Your brief says revenue is zero. The site footer (`index.html:216-218`, `about.html:142-146`) says *"Its only revenue is X's creator monetization."* Those cannot both be true in a published privacy policy. Decide which is accurate and make the policy, the about page and the footer say the same thing. This matters beyond tidiness: "non-commercial" is a condition on some free tiers, and a law professor checking your funding disclosure against your privacy policy is exactly the reader you are optimising for. (It is not a condition on Cloudflare's free plan — another reason this choice is safer than the alternatives.)

---

## 8. What this costs you compared to Google Analytics

This trade-off is real. Do not let anyone tell you privacy-preserving analytics is free of cost — it is not, it is just that the cost is worth paying here.

**What you genuinely give up:**

1. **Returning visitors.** GA4 would tell you "60 users, 140 sessions." You will see 140 visits and have no idea whether that is 60 people or 140. For an outreach campaign this actually matters: you cannot tell the difference between one enthusiastic professor and ten curious ones.
2. **Funnel and path analysis.** GA4 would show you that 30 people landed on `/educators.html`, 12 continued to `/accuracy.html`, and 4 clicked through. You get three separate numbers and will have to reason about them yourself. With traffic this small, that reasoning is often guesswork.
3. **Conversion attribution.** GA4 could tie a store click back to the referrer that brought that visitor in. You will see "12 referrals from a .edu domain" and "5 clicks on /go/ios/" and never know if they are the same people.
4. **Audience insight.** No demographics, no interests, no "your readers also read X." Some of that is junk anyway, but it is genuinely gone.
5. **Query-string data.** No UTM campaign reporting. Distinct landing paths are a workable substitute, but a coarser one — one path per wave, not one tag per email variant.
6. **The ecosystem.** No Google Ads linkage, no Search Console traffic integration inside the analytics view, no Looker Studio dashboards, no large body of tutorials and consultants.

**What you get in exchange:**

- A privacy position you can state plainly to law professors and have it survive their scrutiny — which is the entire commercial logic of this project.
- No consent banner, and no risk of one being wrong.
- No transfer-impact assessment, no supplementary-measures analysis, no Google-shaped compliance surface.
- A privacy policy that is short, true, and verifiable by anyone with developer tools.
- Roughly ten minutes of setup and zero ongoing maintenance.

**My honest assessment:** for measuring whether emailing 200 professors produced any visits, from where, to which pages, and how many clicked through, the recommended setup gives you every number you will actually act on. Points 1 and 3 above are the ones you will occasionally wish you had. You will not miss the rest.

---

## 9. Revisit this decision if any of these happen

| Trigger | What to do |
|---|---|
| **The project starts earning real money** (beyond X creator payouts) or a company is formed | Revisit the whole legal framing, not just the tool. A commercial controller with revenue attracts a different level of expectation, and a paid EU option (Plausible at ~€108/yr, hosted entirely in the EU) becomes cheap insurance and a better story. Also revisit whether the operator is still an individual for GDPR purposes |
| **Traffic grows past roughly 100,000 page views a month** | Sampling and dashboard granularity start to matter. Reassess whether Cloudflare's aggregation still gives you the precision you need |
| **You want to know whether people come back** | This is the real limit of the current setup. It cannot be solved without device storage and therefore without a consent banner. Decide deliberately: the answer is probably still "no, not worth it" |
| **The app launches and you add store links** | Implement the `/go/` redirect pages at the same time, and start reading App Store Connect and Play Console acquisition data. Update `.well-known/` placeholders in the same pass |
| **Cloudflare changes its free tier, or is acquired** | Export or screenshot your dashboard monthly regardless, as a matter of routine. It takes a minute and means a service disappearing costs you nothing but a migration |
| **The Digital Omnibus is adopted** | If the aggregate-audience-measurement exemption survives into law, update the privacy note to cite it — it would turn a well-reasoned position into an explicit statutory one |
| **The CJEU rules in *Latombe* (C-703/25 P)** | If the Data Privacy Framework falls, re-examine every US processor, including GitHub Pages itself. This would be a bigger problem than analytics |
| **You ever consider adding an X embed, YouTube video, Google Font, or CDN script** | Don't. Re-read section 6 first. Any one of these leaks more visitor data than all the analytics in this document put together |

---

## 10. One-page summary

- **Decision:** Cloudflare Web Analytics, manual snippet. Free. One line in six files plus the page template.
- **You will see:** visits, page views, top pages, referrers, countries, trends by day, and outbound clicks via `/go/` redirect pages.
- **You will not see:** individuals, returning visitors, journeys, demographics, or recordings — ever, by design.
- **Cookie banner:** not required. High confidence, well-supported, not judicially settled. Publish the transparency note instead.
- **Google Analytics:** not on the site and never was. Nothing to remove; three documents to correct.
- **Third-party resources:** currently zero, fonts already self-hosted, no X embeds. The analytics snippet is the first one, deliberately.
- **Reversed:** the earlier GoatCounter recommendation. Its script writes to browser localStorage, reads screen width, and sends the full query string, and it offers no data-processing agreement.
- **Do it before launch**, so no visitor is ever counted without the notice being live.
