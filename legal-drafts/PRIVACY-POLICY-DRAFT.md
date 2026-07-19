# ⚠️ DRAFT FOR COUNSEL REVIEW — NOT LEGAL ADVICE

This document is a working draft prepared for a qualified lawyer to review, correct and
approve before publication. It is not legal advice and must not be published as-is.

Every factual statement below has been checked against an audit of the app, site and bot
source code carried out on 2026-07-19. Where a fact is genuinely unknown, it appears as a
`[[PLACEHOLDER: …]]`. Where a claim is qualified, the qualification sits **inline, in a
blockquote, next to the claim it qualifies** — there is deliberately no separate "open
questions" section, because deleting such a section before publication would strip every
hedge while leaving every confident assertion standing.

Two rules were applied throughout this revision and should be applied to any future edit:

1. **Nothing is asserted that the code audit does not establish.** Several sentences in the
   previous revision described behaviour that was inferred rather than verified — a store
   backing AsyncStorage, secret-handling in the bots, disk encryption, an absence of
   clipboard reads, a history of law-enforcement requests. Each has been cut or reduced to a
   placeholder. A plausible premise asserted as ground truth is the failure mode this
   project has already been burned by once.
2. **Obligations are not volunteered before scope is tested.** Material on the Digital
   Services Act, on Texas and Washington state law, on a UK representative and on a
   warrant canary has been removed, because the threshold question in each case is answered
   one step earlier than the previous draft asked it.

Draft date: 2026-07-19. Revision 2.

---

# BillTracking Privacy Policy

**Effective date:** [[PLACEHOLDER: date of first publication]]
**Last updated:** [[PLACEHOLDER: same as effective date for v1.0]]
**Version:** 1.0
**Applies to:** the BillTracking mobile app (iOS and Android), the website at
billtracking.org, and the BillTracking accounts on X.

---

## 1. Plain-English summary

This summary is written to promise only what the software actually does today. Nothing in it
is aspirational.

- **There are no accounts.** You never register, never log in, and never give us a name, an
  email address, a phone number or a password.
- **The app does not connect to us at all.** It makes no network requests of any kind. There
  is no BillTracking server, no API and no endpoint — not for content, not for settings, not
  for anything. Because the app makes no requests, anything it shows you is already inside
  the app package on your phone.
- **The app contains no analytics, crash-reporting, advertising or attribution software.**
  None. This was verified against the actually-installed dependency tree, not just the
  manifest.
- **The app does not create any identifier for you.** No device ID, no install ID, no random
  UUID, no advertising ID, no push token. The push-notification library is not installed, so
  no push token can exist.
- **The app stores one thing on your phone, and it stays there.** A single settings record,
  described in full in section 4. It is never transmitted, backed up or synchronised by us,
  because the app has no way to transmit anything. Deleting the app or clearing its data
  removes it from the device. Depending on your phone's own backup settings a copy may exist
  in your device backup — that backup is yours, not ours, and we cannot reach it.
- **The website, when it launches, will run no JavaScript and load nothing from any other
  company.** It is built that way today and is not yet deployed. No analytics, no trackers,
  no third-party fonts, no embedded content, and no cookie banner because there is nothing
  that would need consent.
- **We do not have servers.** But the website will be hosted by GitHub, and any host
  necessarily handles visitors' IP addresses in order to deliver a page. That is described in
  section 5 — we are not going to claim that no IP address is ever processed anywhere.
- **Reader voting is not built yet.** The vote buttons you may see in the app write only to
  your own phone. The counts shown next to them are sample figures, and the geographic
  breakdown is randomly generated placeholder content. Nothing is sent anywhere, because
  there is nowhere to send it. Section 8 explains what is planned and what that will mean.
- **Some summaries are written by AI** and carry an `[AI-Generated]` label. Section 18
  explains exactly where that label appears and one place where it currently does not.

---

## 2. Who we are, and how to contact us

BillTracking is operated by **Thomas Vanhoutte**, an individual resident in Poland.

- **All privacy matters, and general contact:** contact@billtracking.org
- **Accuracy and corrections:** accuracy@billtracking.org
- **Working language:** English, for all correspondence.
- **Postal address:** [[PLACEHOLDER: address to be supplied — Article 13(1)(a) GDPR requires
  the controller's identity and contact details, and counsel should advise on whether a
  postal address is required here and on the privacy implications of publishing a home
  address. A service address or PO box may be preferable.]]

There is no company and no other legal entity behind the project. The operator is a natural
person acting as the data controller for the limited processing described in this policy.

**Data Protection Officer.** None appointed. Article 37(1) GDPR requires one only for public
authorities, for controllers whose core activities require large-scale regular and systematic
monitoring, or for large-scale processing of special-category data. None applies.

> **Counsel note.** This conclusion should be re-checked if reader voting is ever built and
> deployed, since aggregated political opinions are special-category data and the "large
> scale" assessment would then need to be made on real figures rather than on a feature that
> does not exist.

**EU representative (Article 27 GDPR).** Not required. Article 27 applies to controllers *not
established in the Union*. The operator is established in Poland, so the GDPR applies
directly under Article 3(1) and no representative is needed.

**United Kingdom.** The Service is not directed to the United Kingdom — there is no UK
legislative coverage, no UK-specific content, marketing or pricing — and it monitors nobody's
behaviour anywhere. No UK representative is appointed under UK GDPR Article 27. We would
revisit this if UK legislative coverage were ever added. UK readers can still complain to the
ICO; see section 14.

> **Counsel note.** Availability in English worldwide is not, by itself, "offering services
> to" data subjects in a country. We have stated a conclusion here rather than paying for
> advice on a question the architecture answers: there is no processing of any UK visitor's
> data to represent.

---

## 3. The app makes no network requests

This is the central fact about BillTracking, so we state it precisely.

The app's source contains **no `fetch`, no `XMLHttpRequest`, no `axios` call and no
WebSocket**. There is no API base URL and no endpoint constant anywhere in it. Every image is
a local file bundled into the application package.

The following are **not present** in the app. This was checked against the installed
dependency tree and the lockfile, not merely the list of declared dependencies:

Sentry · Firebase · Amplitude · Segment · Google Analytics · the Facebook SDK ·
`expo-insights` · `expo-updates` · `expo-notifications`

Because `expo-notifications` is absent, the app cannot obtain or hold a push token.

> `expo-device` and `expo-constants` are present in the dependency tree as transitive
> dependencies of other packages. Neither is imported anywhere in the app's own source, so
> neither is used to read or report anything about your device. We mention this because a
> reader inspecting the lockfile would see them and we would rather explain them than be
> asked.

The practical consequence: **we receive nothing from the app.** Not a request, not a
heartbeat, not an error report, not a crash log. If that ever changes, this policy will say
so *before* it changes — see section 19.

---

## 4. What the app stores on your device

The app writes exactly one record to your device's local application storage, under the key
`billtracking.state.v1`. There is one place in the code that writes it. It contains:

| What | Detail |
|---|---|
| Home tab | which tab the app opens on |
| Feed filters | the filters you have applied |
| Followed bills | the bill references you chose to follow |
| Search keywords | search terms **you typed**, saved so you do not retype them |
| Docket-only flags | display flags you set |
| Hide toggles | three display toggles |
| Notification category settings | which categories you have switched on |
| Your votes | a map of bill reference to `up` or `down`, recorded when you tap a vote chip |
| Country and US state | optional, only if you choose to enter them |

Two of these deserve to be called out even though they never leave your phone:

- **Your votes are political opinions.** Under Article 9 GDPR political opinions are a
  special category of personal data. See section 9.
- **Search keywords are free text**, so they can reveal anything you happen to type.

**This record is never transmitted.** Not by us and not by the app, which as explained in
section 3 has no networking code at all. We do not receive it, cannot request it, and hold no
copy of it. Deleting the app or clearing its data removes it from the device; a copy may
persist in your own device backup if you use one, which is under your control and not ours.
There is nothing for us to delete on your behalf because we never had it.

**Why we store it at all.** Solely to remember the settings you yourself chose, so that the
app behaves the way you left it. Under Article 5(3) of the ePrivacy Directive, storing
information on your device requires your consent unless it is strictly necessary to provide
the service you explicitly requested. Our position is that remembering the preferences you
deliberately set is strictly necessary in that sense, and that no consent banner is
therefore required.

> **Counsel note.** The vote map is the item most likely to be argued the other way, since
> recording a political opinion goes somewhat beyond a display preference — even though it is
> written only in response to a deliberate tap by the user and never leaves the device. If
> counsel disagrees with the assessment above, the cure is a **consent step before the first
> vote is written to storage** — Article 5(3) is a consent rule, not a transparency rule, so
> a one-time disclosure notice would not fix it — or removing the vote map from the persisted
> record and holding it in memory only.

**In app-store terms**, this is *not* "collection". Both Google Play's Data safety
declaration and Apple's App Privacy disclosures define collection as data being transmitted
off the device. Nothing here is. We describe it anyway, because you are entitled to know what
the app puts on your phone.

### 4.1 Links out of the app, and the clipboard

**Links.** The app can hand a link to your operating system's browser or mail client when you
tap it. When that happens, *your browser* makes the request — the app does not. The
destinations are: billtracking.org, x.com (our feeds), congress.gov,
oeil.europarl.europa.eu, and `mailto:` addresses. Every web link is HTTPS; there is no
plain `http://` link anywhere in the app.

Once you are on someone else's site, their privacy policy governs, not ours. We have no
visibility into what happens there.

**Clipboard.** When you ask the app to copy something — a post URL, a bill reference, an
email address — it writes that text to your system clipboard.

> [[PLACEHOLDER: the audit verified the clipboard *write* sites only. Before publication,
> verify that there are no clipboard **read** call sites (`getStringAsync` / `getString`) in
> `src/`. If verified, add: "It never reads the clipboard." Do not add that sentence
> otherwise — iOS shows the user a system toast when an app reads the clipboard, so a false
> negative here would be visibly wrong to the reader.]]

---

## 5. The website, and the fact that a host sees IP addresses

**What the site does not do.** billtracking.org contains **no JavaScript at all** — zero
`<script>` tags. No `<iframe>`, no `<form>`. No Google Analytics, no Plausible, no Matomo, no
analytics of any kind. No advertising or tracking pixels. There is no cookie banner because
the site sets no cookies and stores nothing on your device.

**No third-party resources.** Fonts are self-hosted `woff2` files. The stylesheet, icons and
images are all served from the same origin. The only cross-origin references on the site are
ordinary `<a href>` links, which send nothing anywhere unless you click them.

> The site is not yet deployed. The domain is registered but currently serves nothing. This
> policy describes the site as built and as it will be published; every statement in this
> section is written in the present tense about the built artefact, not about a live service.

**Hosting, and IP addresses.** The site will be hosted on **GitHub Pages** (GitHub, Inc., a
Microsoft company). GitHub does not provide visitor access logs to repository owners, so we
will not see or hold visitor IP addresses. But delivering a web page over the internet
inherently requires the host to process the visitor's IP address at the network layer, and
GitHub does so as our hosting provider. We are not going to claim otherwise. An IP address
can be personal data in the hands of a service operator.

- **Role:** GitHub acts as our processor for hosting.
- **Purpose:** delivering the pages you request, and network security.
- **Legal basis:** our legitimate interest in making the site available and keeping it
  secure (Article 6(1)(f) GDPR).
- **Retention and transfers:** governed by GitHub's own terms and privacy statement, not by
  us. GitHub is US-based; transfers rely on GitHub's own transfer mechanism.

> [[PLACEHOLDER: counsel to confirm whether a GitHub Pages arrangement on a free account is
> covered by a data processing agreement satisfying Article 28(3) GDPR, and to identify the
> transfer mechanism GitHub relies on. If no Article 28 terms are available, that is a gap to
> record and accept or to solve by changing host.]]

> [[PLACEHOLDER: the proposition that a dynamic IP address can be personal data in the hands
> of a website operator is normally sourced to *Breyer* (CJEU, C-582/14). Counsel to confirm
> the citation and its current standing before the case name is added to published text. This
> draft states the proposition without the citation deliberately — see the note at section 9
> on unverified authorities.]]

**If we ever add website analytics.** We currently have none. A written decision document in
the project considers possibly adding a cookieless, storage-free, identifier-free analytics
product in future. It is **not installed**, and no such provider is part of our stack today.
If it is ever added, this policy will be updated before it goes live and will name the
provider, and section 11 will gain a row.

---

## 6. Email

contact@billtracking.org and accuracy@billtracking.org are aliases on a single mailbox hosted
on **Microsoft Exchange Online**. If you email us, Microsoft processes that message as our
processor, and we read it.

- **What we get:** whatever you put in your message — your email address, your name if you
  sign it, and the content.
- **Purpose:** answering you, and handling accuracy reports.
- **Legal basis:** our legitimate interest in responding to correspondence (Article 6(1)(f)).
- **Retention:** [[PLACEHOLDER: retention period for correspondence to be decided and stated
  — e.g. "deleted 24 months after the exchange concludes". It should be a period we actually
  apply, not one we aspire to.]]

**There is no contact form anywhere.** Not on the site, not in the app. All contact is by
`mailto:` link, which opens your own mail client and submits to no endpoint of ours.

> **Internal action, not for publication.** Article 30(5) GDPR exempts controllers with fewer
> than 250 employees from keeping a record of processing activities only where the processing
> is occasional, poses no risk to rights and freedoms, and involves no special-category data.
> Inbound correspondence to two published addresses is **not occasional**, so on the
> regulator's reading of Article 30(5) a record is required for at least the email processing
> and the hosting-layer IP processing. Prepare a one-page internal Article 30(1) record
> covering purposes, categories of data subject and data, recipients (Microsoft, GitHub),
> transfers, retention and security measures. Keep it available on request. Nothing about it
> belongs in the published policy.

---

## 7. The X feeds, and data about legislators

Two Python scripts post legislative updates to X. They are command-line programs run on a
schedule by GitHub Actions. They are **outbound HTTP clients only** — they fetch from
official sources and post to X. Nothing connects *to* them; they do not listen on a network
port and no web framework is installed in either project. A reader's IP address is therefore
never presented to them.

If you read or interact with our posts on X, **X is the controller for that**, under X's own
privacy policy. We see only what any account holder sees.

**Sources of the legislative data:** the US Congress API (api.congress.gov) and the European
Parliament's open data (OEIL and Cellar).

**Personal data about legislators (Article 14 GDPR).** The official record we republish names
Members of Congress and Members of the European Parliament, and records how they voted and
what they sponsored in their official capacity. That is personal data about them, obtained
not from them but from the official public sources listed above. We process it to report on
legislative activity, on the basis of our legitimate interests under Article 6(1)(f) — the
interest pursued being public access to the legislative record. Politicians' public official
acts sit at the centre of legitimate public-interest reporting. Roll-call votes cast in
office are official acts, not the private political opinions of a data subject in the
Article 9 sense.

> **Counsel note — priority question.** Poland implemented Article 85 GDPR (processing for
> journalistic, academic, artistic or literary expression) in the Act of 10 May 2018 on the
> Protection of Personal Data, which disapplies substantial parts of the Regulation —
> including Articles 13–16 and 21 — for processing carried out for those purposes. The
> operator is established in Poland, and republishing and describing the legislative record
> about named legislators is close to the paradigm case. If the derogation applies, the
> Article 14 notification problem for legislator data disappears entirely and there is no
> need to reach for the disproportionate-effort exemption in Article 14(5)(b). This is
> cheaper to answer than most of the placeholders in this draft and should be answered first.

> **Counsel note.** If the Article 85 derogation does *not* apply, two points then matter:
> (i) whether any republished material about named legislators engages Article 9 (e.g.
> reporting party affiliation), and (ii) whether Article 14(5)(b) is needed to explain why we
> do not notify each legislator individually. Our view is that it plainly is, but it should
> be recorded.

---

## 8. Reader voting — **planned, not built**

**As of the effective date of this policy, there is no vote submission of any kind.**

What actually happens today when you tap a vote chip in the app:

1. The choice is held in memory and written to the local settings record described in
   section 4.
2. The count displayed next to it is a **hardcoded sample number** plus your own tap.
3. The geographic breakdown shown is **generated by a seeded random-number generator**. It is
   placeholder content. It represents no real people.

Nothing is transmitted, received, aggregated or stored anywhere off your device, because
there is no server to receive it.

> We are stating this bluntly rather than describing the feature as though it worked, because
> the difference matters: a reader who believes their vote is being counted is being
> misinformed, and a reader who believes their political opinion has been transmitted to us
> is being alarmed for no reason.

### 8.1 What is planned, and what it will mean

If reader voting is built, the design intention — decided and recorded, but not implemented —
is that a vote will be submitted **anonymously**: with no account identifier (there are no
accounts), no device identifier, no advertising identifier, no session token and no
anti-abuse fingerprint. A vote would carry the bill reference, the position chosen from a
fixed set of options, and optionally a coarse geography that you self-report.

That design would have real, permanent consequences, which we would rather state now than at
launch:

- **We would not be able to show you your own votes.**
- **We would not be able to change or withdraw a vote after it is cast**, at your request or
  at all.
- **We would not be able to delete a specific vote on request**, because nothing would
  identify which one is yours.
- **We would not be able to prevent double voting**, and we would not claim the totals were
  protected against it.

These are the accepted price of not holding a linkable record of anyone's political opinions.
Your control would be complete but blunt: **do not vote.** Reading BillTracking never
requires it.

> Anything in this subsection describing what a vote "would" do is a statement of design
> intention about software that does not exist. If and when voting is built, this policy will
> be rewritten in the present tense **before** the feature ships, and this section will need
> to state: whether any IP address is logged at any layer in front of the receiving endpoint
> and for how long; what timestamp granularity is stored with a vote; whether any token or
> rate-limit key is attached; where the receiving infrastructure is located; and the retention
> period for vote records. None of those questions can be answered today, because there is
> nothing to answer them about.

> **Counsel note — which legal framing is the design built to survive?** Section 9 sets out
> an anonymity position resting on Recital 26. There is a second, competing framing that a
> regulator may reach for first: **Article 11** GDPR, which governs processing that does not
> require identification. Article 11 presupposes that the data *is* personal data, relieves
> the controller of Articles 15–20 in the ordinary case, but imposes Article 11(2) duties —
> informing the data subject that we cannot identify them, and allowing them to supply
> additional identifying information. The planned payload (bill reference, position,
> self-reported country and US state, plus whatever timestamp) is closer to the classic
> Article 11 case than to the classic Recital 26 case, particularly in small geographic cells.
> Counsel should decide which framing the design is built to survive **before** anything is
> built, because the answer changes the design, not just the policy text.

### 8.2 Small-cell suppression — a planned disclosure control

The app's interface contains a threshold rule (`MIN_CELL = 10`) in one component: where a
category has fewer than ten votes, it withholds the up/down split and shows only the row
total.

**It operates entirely on the sample data described above, and it is not a working privacy
safeguard. Please do not rely on it.** We will not present it as protecting readers unless
and until it protects real data and has been corrected.

> **Counsel and engineering note.** The rule as implemented has a known differencing weakness
> and is recomputed independently on every render rather than applied once and held. The
> mechanics are written up in the internal review notes and in the code comment, and are
> deliberately **not** reproduced here: a published privacy policy is the wrong place for a
> working description of how to defeat a disclosure control, and the paragraph would
> otherwise survive into the version published on the day a real backend ships. The defect
> must be fixed before the control is connected to anything real.

> **Counsel note.** Threshold suppression of this kind (k-anonymity) is a mainstream
> disclosure control but is not a guarantee of anonymity even when correctly implemented; it
> does not reliably prevent singling out or defeat inference attacks. The academic source the
> previous draft cited for this has been removed pending verification — see the note at
> section 9. We would not present a corrected version of the control as a guarantee either.

---

## 9. Political opinions as special-category data

A view on a piece of legislation is a **political opinion**. Under Article 9 GDPR, political
opinions are a *special category* of personal data: processing is prohibited unless a
specific Article 9(2) condition applies, on top of an Article 6 lawful basis.

**Our position is that we do not process anyone's political opinions.** The vote map exists
only in storage on your own device, which we cannot read and never receive. There is no
transmission and no server-side record.

> **Counsel note.** We state this as our reasoned position rather than as a settled
> conclusion. "Storage" is expressly processing under Article 4(2), and controllership does
> not require access to the data — the operator did write the code that determines that a
> political opinion be written to the device. The favourable answer (no access, no personal
> data in his hands) is good but contested, and it is the same tension recorded in the
> counsel note at section 4. Both notes should be resolved together.

**If voting is built**, the design intention (section 8.1) is that what we would receive
would be anonymous information falling outside the GDPR, on the Recital 26 basis that the
person is not and can no longer be identified by any means reasonably likely to be used.
Anonymity — not consent — would be the foundation of that design, because consent under
Article 7(1) must be *demonstrable*, which would require attaching an identifier to each
vote and would destroy the anonymity it was meant to secure.

We would be careful about the limits of that position:

- Anonymity would have to hold **at the moment of collection and from our own perspective**,
  not merely from the perspective of a reader looking at a published tally.
- Anonymity is context-relative and would have to be reviewed periodically, not decided once.
  Re-identification risk grows as an audience grows.
- The competing Article 11 framing set out in the counsel note at section 8.1 may be the one
  a regulator applies.
- **And in any event, if contrary to that position** any element of a submitted vote were
  held to be personal data, we would have **no Article 9(2) condition compatible with an
  anonymous submission design**: explicit consent under Article 9(2)(a) must be demonstrable
  under Article 7(1), and demonstrability requires an identifier that the design deliberately
  removes. The feature would then require redesign, not a rewritten justification. We say so
  now so that nobody — including us — treats the anonymity position as a formality.

> **Counsel note — authorities.** The previous draft cited a 2025 Court of Justice judgment
> (*EDPS v SRB*) for the proposition that anonymity is assessed from the collector's own
> perspective, a draft EDPB guideline on anonymisation by number, and an academic paper on
> k-anonymity. **All three have been removed from the published text and none should be
> reinstated on the drafter's characterisation.** The SRB line of litigation is best known
> for a *recipient*-relative holding at first instance, which is close to the opposite of the
> proposition it was cited for, and the appeal postdates the drafter's reliable knowledge.
> Counsel should read the actual judgment, confirm the guideline exists and is correctly
> numbered, and either supply the correct authority or leave the propositions stated without
> citation. The audience for this document is law professors; a wrong case number in a
> document arguing for factual rigour is disproportionately damaging. The same instruction
> applies to every case citation, article number and date anywhere in this draft.

**Readers outside the EU:** we apply the stricter European standard everywhere as a design
choice.

> [[PLACEHOLDER: counsel to confirm whether any enacted US state privacy law treats a
> legislative opinion as "sensitive personal information". The previous draft asserted, in
> the operator's own voice, that none of roughly twenty enacted statutes does. That is a
> sweeping negative statement of law that nobody verified, in the one document whose purpose
> is not to contain one.]]

---

## 10. Lawful bases, summarised

| Processing | Lawful basis |
|---|---|
| Settings stored on your device (section 4) | Not processed by us. We have no access and receive no copy. Storage on your device is strictly necessary for the functionality you requested (ePrivacy Art 5(3)). |
| Delivering website pages; visitor IPs handled by GitHub as host (section 5) | Legitimate interests (Art 6(1)(f)) — making the site available and secure. |
| Email you send us (section 6) | Legitimate interests (Art 6(1)(f)) — responding to correspondence. |
| Republishing the official legislative record, including data about legislators (section 7) | Legitimate interests (Art 6(1)(f)) — our interest, and readers' interest, in making the public legislative record accessible. |
| Reader votes | **Not applicable — the feature does not exist.** See section 8. |

> **Counsel note.** The previous draft blended "legitimate interests **and** the public
> interest" in the legislator row. Public interest as a separate basis is Article 6(1)(e),
> which we do not rely on and which would require a basis in Union or Member State law. The
> row now states Article 6(1)(f) alone, with the public interest characterised as the
> *interest pursued* inside the balancing test. See also the Article 85 question at
> section 7, which may displace this analysis for that row entirely.

We rely on **no consent-based processing** at present, and there is accordingly no consent
for you to withdraw. We run no advertising and no profiling of any kind.

---

## 11. Who receives data, and where they are

**We do not sell personal data. We do not share it for advertising, and we run no advertising
of any kind. We do not disclose personal data to anyone for their own purposes.**

We do use service providers, who process data on our behalf:

| Provider | What they process | Role | Location |
|---|---|---|---|
| GitHub, Inc. | Visitor IP addresses at the network layer, as host of billtracking.org (section 5) | Hosting processor | US |
| Microsoft (Exchange Online) | Email you send to our published addresses (section 6) | Email processor | US-headquartered |

Those are the only providers that process personal data on our behalf. There is no analytics
provider, no advertising network, no CDN of our own, no crash-reporting service, no
error-tracking service and no database provider, because there is no server-side application
to need one.

> [[PLACEHOLDER: operator to confirm the position of the domain registrar and the DNS
> provider, and whether either processes any personal data of readers, before this table is
> described as exhaustive of the whole infrastructure rather than of reader-data processors.
> X is a separate case: it is the controller for what happens on its own platform, not our
> processor.]]

**International transfers.** We do not operate servers and do not ourselves transfer personal
data outside the EEA. Both providers above are US-based; any transfer of personal data to
them occurs under their own transfer mechanisms.

> [[PLACEHOLDER: counsel to identify and state the specific transfer mechanism each provider
> relies on — EU-US Data Privacy Framework certification, standard contractual clauses, or
> both — and to confirm they are current as at the effective date.]]

**The project earns no revenue.** There are no ads, no sponsors, no in-app purchases, no
subscriptions, no paid placements, and nothing is sold. The X accounts are not enrolled in
and are not eligible for creator monetization. No data is exchanged with X beyond ordinary
public posting.

> We state these facts rather than the conclusion "non-commercial", because that term does
> specific legal work under CalOPPA, the CCPA and EU trader/consumer rules, and its
> application is for counsel to determine rather than for us to assert. Trader status is the
> single question on which the most other answers depend — see section 16.

---

## 12. Retention

| Data | Retention |
|---|---|
| Settings on your device (section 4) | Kept on your device for as long as you keep the app. Removed from the device when you uninstall it or clear its data. We hold no copy and cannot retain what we never receive. |
| Website visitor IPs at the hosting layer (section 5) | Determined by GitHub, not by us. We hold no access logs. |
| Email correspondence (section 6) | [[PLACEHOLDER: period to be set — see section 6.]] |
| Vote records | Not applicable. No vote record exists anywhere off your device. |

---

## 13. Security of processing (Article 32 GDPR)

The strongest security measure in this project is **data minimisation by architecture**: an
app that makes no network requests, ships no third-party SDKs, generates no identifier and
stores a single local record cannot leak what it never holds or transmits. That is a design
decision, not an accident, and it is the measure we rely on most.

Beyond that:

- **Encryption in transit.** Every network address in the app is HTTPS; there is no `http://`
  URL anywhere in its source. The website will be served over HTTPS by GitHub Pages. Both
  bots contact official sources and X over HTTPS.
- **Storage on your device.** The settings record is written through the platform's standard
  application storage. **We add no encryption of our own and do not claim any.** Whatever
  protection applies to it is the operating system's, not ours, and it varies by platform,
  OS version and device settings.
- **No credentials to steal.** There are no user accounts, no passwords, no session tokens
  and no password database, because there is no authentication anywhere in the product.
- **Bot operations.** The bots run in GitHub Actions as outbound clients and expose no
  inbound network surface.

> [[PLACEHOLDER: two security claims were cut from this section because the code audit did
> not cover them. Reinstate only after a verified check. (1) Bot secret handling — "API keys
> are held as encrypted repository secrets and are never committed to source" is an absolute
> claim about the whole history of two repositories that nobody has examined; check both
> histories before publishing it. (2) Access control — "the operator is the only person with
> access to the mailbox and the repositories" requires checking the GitHub collaborator lists
> and Exchange mailbox delegation, which takes about two minutes and has not been done.]]

We do not claim the software is free of defects. Section 8.2 records one we know about.

---

## 14. Your rights

If you are in the EU or EEA you have, under Articles 15–22 GDPR, the rights of **access**,
**rectification**, **erasure**, **restriction of processing**, **objection**, and **data
portability**, in the circumstances each Article specifies. Readers in the UK have equivalent
rights under the UK GDPR.

### Your right to object

**You have the right to object at any time to our processing based on legitimate interests —
that is, the processing described in sections 5, 6 and 7.** Email contact@billtracking.org
and say so. We will consider the objection on its merits and tell you the outcome.

> Stated separately and up front because Article 21(4) requires the right to object to be
> brought to your attention explicitly and separately from other information, not buried in a
> list.

### How the other rights work here, honestly

- **Your app settings, followed bills, search terms and votes:** we hold none of this, so
  there is no request for us to answer. On your own device you can change every setting in
  the app, and you can delete the whole record by clearing the app's data or uninstalling the
  app. **The app does not currently provide a way to view or export the stored record as a
  file.** We say that rather than describing your control as complete.
- **Email you have sent us:** we hold it, and we will act on access, rectification and
  erasure requests. Write to contact@billtracking.org.
- **Website visits:** we hold no access logs and cannot identify you from a visit, so there
  is nothing for us to retrieve.
- **Portability (Art 20)** applies to processing based on consent or contract carried out by
  automated means. We rely on neither, so in practice it does not arise; we list it because
  the law requires you be told it exists.

**No automated decision-making or profiling.** There is none within the meaning of Article
22, and we build no profiles of readers.

**Providing data is entirely optional.** There is no statutory or contractual requirement to
give us anything, and no consequence of not doing so. You can read every bill, every update
and every history without providing anything at all.

**Making a request.** Email contact@billtracking.org. We will respond within one month, and
will tell you within that month if we need the extension that Article 12(3) permits. For
anything the app holds, the answer is always the same: it is on your device and we have no
copy. Verification of your identity only arises for email correspondence.

> **Note to the operator, not to counsel.** Three sentences in this section are commitments
> you are *undertaking*, not descriptions of the status quo: that email requests will be
> acted on, that objections will be considered and answered, and the response timescale.
> There is currently no triage process behind the mailbox. The Article 12(3) timescale is the
> law and is not optional; the other two are choices, and they are enforceable against you
> once published. This is the same class of claim the project has already had to soften once
> elsewhere ("every report is read").

### Your right to complain

You can lodge a complaint with a data protection supervisory authority. Because the operator
is established in Poland, our lead supervisory authority is:

**Prezes Urzędu Ochrony Danych Osobowych (President of the Personal Data Protection Office,
"UODO")**
ul. Stawki 2, 00-193 Warsaw, Poland — uodo.gov.pl

You may also complain to the authority in your own EU country of residence or workplace, or
where you believe an infringement occurred. In the UK, the Information Commissioner's Office
(ico.org.uk). You do not have to contact us first, though we would like the chance to fix
things.

---

## 15. Children

BillTracking is a general-audience service about legislative procedure, written for law
professors, their students and interested readers. It is **not directed to children**, we do
not market it to them, and we do not knowingly collect personal information from anyone of
any age — because, as set out above, the app collects nothing from anyone.

- **COPPA (US):** the app is not directed to children under 13 and transmits no personal
  information off the device, so there is nothing to collect from a child user. With no
  accounts and no age collection, we hold no age data and have no realistic route to actual
  knowledge of a child user.
- **GDPR Article 8:** the information-society-service consent rules for children aged between
  13 and 16 (depending on Member State) are not engaged, because we rely on no consent-based
  processing.
- **UK Age Appropriate Design Code:** applies to services *likely to be accessed by* children,
  a lower threshold than "directed to". A legislative-procedure app is unlikely to meet it,
  but the code's data-minimisation and no-profiling standards are met by the architecture
  regardless: no profiling, no nudges toward giving up data, and no data collection at all.

> [[PLACEHOLDER: counsel to confirm the app's age rating on both stores is set consistently
> with this section, and to review the child-safety declarations both stores now require.]]

---

## 16. US state law disclosures

**CCPA / CPRA (California).** We do not believe the CCPA applies to us: it applies to
for-profit businesses meeting one of three thresholds (revenue, volume of consumers' personal
information bought/sold/shared, or share of revenue from selling or sharing personal
information). We meet none of them — the project earns no revenue at all. We tell you
voluntarily and unconditionally that **we do not sell or share personal information and do
not use it for targeted advertising.** We have no "sensitive personal information" to
disclose because we receive none.

**CalOPPA.** CalOPPA attaches to a commercial site or online service that *collects
personally identifiable information about individual California consumers who use or visit
it*. **No such information is collected**: the app transmits nothing, the site runs no
scripts, sets no cookies, has no forms and produces no logs reachable by us, and email is
initiated by you. The collection limb is therefore not satisfied, and the question of whether
the Service is "commercial" does not need to be reached. We make the disclosures below
anyway, because they are cheap and consistent with how we would rather write:

- *Categories of personally identifiable information collected:* **none through the app**;
  none through the website beyond IP addresses processed by our host (section 5); the contents
  of any email you choose to send us (section 6).
- *Categories of third parties it is shared with:* none, other than the two processors listed
  in section 11 acting on our behalf.
- *Process for reviewing and requesting changes:* your device-held settings are entirely under
  your own control in the app. For email, write to contact@billtracking.org.
- *How we notify you of material changes:* see section 19.
- *Do Not Track:* the app makes no network requests and so cannot send or receive a DNT
  signal. The website runs no JavaScript, sets no cookies and performs no tracking of any
  kind, so there is no tracking for a DNT signal to disable. We therefore do not respond to
  DNT signals, and there is nothing they would change.

**Other US states.** We process no personal data of residents of any US state through the app
or the site: the app transmits nothing, the site produces no logs available to us, and the
only inbound channel is email you chose to send. On that footing the Texas Data Privacy and
Security Act does not apply, and the Washington My Health My Data Act does not apply — we
process no consumer health data of any kind, and political opinions are not health data.

> The previous draft argued the Texas position through the small-business exemption and asked
> counsel to confirm an SBA classification point. That question never arises: the threshold
> is answered one step earlier, at whether any Texan's personal data is processed at all.
> The same applies to Washington. Both placeholders have been deleted rather than sent to
> counsel.

---

## 17. App-store disclosures and data deletion

The answers we give on Apple's App Privacy questionnaire, in the iOS privacy manifest
(`PrivacyInfo.xcprivacy`), and on Google Play's Data safety form are drawn from this document
and must not diverge from it.

- **Data collected:** none. The app transmits nothing.
- **Data shared:** none.
- **Tracking:** none. No advertising identifier is accessed, so no App Tracking Transparency
  prompt is required.
- **Encrypted in transit:** yes for the outbound links the app hands to your browser (all
  HTTPS); the question is otherwise moot, since the app makes no requests of its own.
- **Data deletion (Google Play).** Play requires this to be answered even where an app has no
  accounts. Our answer: **there is no account to delete, and no server-side data to delete.**
  All data the app holds about you is on your own device, and you delete it yourself by
  clearing the app's data or uninstalling the app. There is no deletion request to make of
  us, and no request URL, because there is nothing on our side to erase.

> [[PLACEHOLDER: required-reason APIs. The previous draft asserted that the app's local
> storage is backed by `NSUserDefaults` on iOS and therefore reaches a required-reason API.
> The audit establishes only that the app uses AsyncStorage; which native store backs it was
> never checked, and the assertion is likely wrong, since React Native / Expo AsyncStorage on
> iOS is generally a file-based store. Confirm from the installed async-storage
> implementation in `node_modules` which, if any, required-reason APIs are reached, and
> declare accordingly. This drives an actual Apple filing, so a guess here propagates into a
> store submission.]]

> [[PLACEHOLDER: build task, not a drafting task. Both stores require the privacy policy to
> be reachable at a public URL **and** from within the app. The site is not deployed, so the
> URL does not exist, and no in-app Privacy Policy link screen has been built. Sequence:
> deploy the site → publish this policy at a stable path → add a Privacy Policy link in the
> app's settings screen → fill the URL in here and in App Store Connect and Play Console.
> Also confirm the App Store Connect support URL, which no draft has mentioned.]]

---

## 18. AI-generated summaries, accuracy and corrections

Some narrative bill summaries in the app and in our X posts are generated by an AI model.

**They carry a literal `[AI-Generated]` label.** In the app the label is structurally coupled
to the summary — a summary cannot be rendered without it. Both bots' post composers append
it. You can also **switch summaries off entirely** in the app's settings.

Two scope limits, stated because overstating this would be exactly the kind of claim this
policy exists to avoid:

1. **Not every post is AI-generated, and posts that are not are not labelled.** Several post
   types are assembled purely from the official record with no model involvement, and
   correctly carry no label. The accurate claim is that *AI-generated summaries are
   labelled*, not that every post carries a label.
2. **Known gap.** The website's permalink generator currently places the AI summary,
   **unlabelled**, into the page's meta description and its Open Graph / Twitter card tags.
   That means a search-engine result or a social-media link preview can show AI-generated
   text with no marker on it. This is unfixed as at the effective date of this policy. We are
   documenting it rather than writing "AI text always carries the label", which would be
   false.

> [[PLACEHOLDER: when the meta-tag gap is fixed, update or remove item 2 — and do not remove
> it before the fix ships.]]

**EU AI Act.** Article 50(4) of Regulation (EU) 2024/1689 requires deployers who use AI to
generate or manipulate text published to inform the public on matters of public interest to
disclose that the text is artificially generated. Those obligations apply from **2 August
2026**. Our `[AI-Generated]` label is intended to meet that duty, and the gap at item 2 above
is the part that would need to be closed for it to be met everywhere the text appears.

> We do **not** claim to satisfy Article 50(2), which requires machine-readable marking of
> synthetic content. That obligation falls on the *provider* of the AI model, not on us as a
> deployer.

> **Counsel note.** The second subparagraph of Article 50(4) disapplies the disclosure duty
> where the AI-generated content has undergone human review or editorial control and a
> natural or legal person holds editorial responsibility for publication. **We do not rely on
> it**: the bots publish on a schedule with no human in the loop. That is precisely why the
> meta-tag gap at item 2 matters rather than being a technicality. Revisit if a human review
> step is ever introduced.

### Accuracy and the source record

Procedural status and official roll-call figures are taken from the official record —
Congress.gov (US) and the European Parliament's open data, OEIL and Cellar (EU) — and are not
written by a model. (Reader-vote figures are neither official nor AI-written; see section 8.)
US Government works are not subject to copyright (17 U.S.C. § 105).

Automated classification of legislative stages is genuinely difficult, and the Service will
contain errors. We take care with accuracy but do not guarantee it. The project contains a
mechanism for recording overrides and corrections to published items.

> We are not, at this version, promising a public correction log at a specific URL, and we
> are not promising that every report will be reviewed. Both would be reasonable commitments
> to make, and neither is made here, because the log is not confirmed live and there is no
> established triage process behind the mailbox. We would rather under-promise on this page
> than repeat a claim we have already had to soften once elsewhere.

If you believe something is wrong, email **accuracy@billtracking.org**.

> [[PLACEHOLDER: once a public correction log exists at a stable URL, and a triage commitment
> can honestly be made, replace this subsection with the actual mechanism, in the present
> tense, and mirror the change across the app's accuracy screen and the site's accuracy page
> — these three must always say the same thing.]]

---

## 19. Changes to this policy

If we change this policy we will publish the updated version at this URL with a new effective
date and a new version number.

> [[PLACEHOLDER: the previous draft also promised to "keep the previous version accessible
> for comparison". No versioned archive exists, the site is not deployed, and no versioning
> scheme has been established. Build the archive mechanism first, then promise it. The
> mechanism must exist before it is described — the same rule the Terms apply to change
> notification.]]

We cannot email you about changes: there are no accounts, no mailing list and no way for us
to reach you. Please check this page if it matters to you.

**We will update this policy *before*, not after**, any of the following: the app making its
first network request; any analytics being added to the site; reader voting being deployed;
or any new processor being engaged.

> **Counsel note — scope questions deliberately not answered here.** The previous draft built
> a section around "Articles 11 and 12 of the Digital Services Act" and asked counsel to
> classify the Service within the DSA. That framing has been removed. The DSA applies to
> *intermediary services* — mere conduit, caching or hosting (Article 3(g)). BillTracking
> publishes exclusively its own content and, as built, stores nothing supplied by a recipient
> of the service, so the Regulation's scope is not engaged at all — not because a
> micro-enterprise exemption applies (Article 19 exempts only Section 3 platform duties), but
> because there is no intermediary service. One contact address (section 2) is retained
> because it is useful, not because a DSA article requires it. **Re-run the DSA scope
> analysis if reader votes are ever submitted and stored**: stored reader-submitted content
> may make this a hosting service, at which point Articles 14, 16, 17 and 20 need drafting.

---

*Version 1.0 — draft prepared 2026-07-19, revised same day for counsel review. Not legal
advice.*
