## ⚠️ DRAFT — FOR COUNSEL REVIEW. NOT LEGAL ADVICE.

This document was drafted by an AI assistant working from an audit of the project's own
source code and from publicly available legal sources. It has **not** been reviewed by a
qualified lawyer in any jurisdiction. It is **not legal advice** and must not be published
in this state.

Open questions are marked **inline**, as blockquotes, immediately next to the claim they
qualify. There is deliberately **no separate caveat section**: an earlier draft put its
hedges in a section marked "not part of the published policy", which meant that deleting
that section to publish would have stripped every qualification while leaving every
confident claim standing. Each blockquote below must be resolved or removed *together with*
the text it sits beside.

Where a fact was not established, this draft says so rather than guessing. A confidently
wrong statement is worse than an admitted gap — and the audience for this document is law
professors, who will check. Statements that were previously asserted without evidence from
the source-code audit — a past false publication, a moderation capability the architecture
cannot deliver, a vendor that is not in the stack — have been removed rather than softened.

**Draft date:** 2026-07-19 · **Status:** unpublished draft · **Effective date:** [[PLACEHOLDER: effective date, once counsel signs off]] · **Version:** [[PLACEHOLDER: version number, e.g. 1.0]]

---

# Terms of Service — BillTracking

**Effective date:** [[PLACEHOLDER: effective date]] · **Version:** [[PLACEHOLDER: version]]

## 1. What these terms are, and who publishes the Service

These terms govern your use of the BillTracking mobile app, the BillTracking website at
billtracking.org, and the BillTracking accounts on X (together, "the Service"). By using the
Service you accept these terms. If you do not accept them, please do not use the Service.

The Service is operated by **Thomas Vanhoutte**, an individual resident in Poland. There is no
company behind it and none is planned.

The Service is free. There is no subscription, no purchase, no account, no login and no
advertising.

**Contact:** contact@billtracking.org
**Accuracy reports:** accuracy@billtracking.org

Both addresses are aliases on a single mailbox and receive mail. Correspondence in English is
preferred.

> **OPEN QUESTION — PUBLISHED IDENTITY AND ADDRESS.** Apple's App Review Guideline 1.2 and
> Google Play's developer requirements both require published contact information. The EU-law
> hook for publishing a name and geographic address is **Article 5 of the e-Commerce Directive
> 2000/31/EC** and its Polish implementation (ustawa o świadczeniu usług drogą elektroniczną),
> whose scope test is "information society service" — itself arguable for a service that earns
> nothing and is normally supplied for remuneration. An earlier draft cited the Consumer Rights
> Directive here; that is doubtful, because the CRD's Art 6 information duties attach to
> distance *contracts* for goods, services or digital content, including (since Directive
> 2019/2161) digital content supplied against personal data — and here nothing is supplied
> against payment and nothing is supplied against personal data, since the app transmits
> nothing. Publishing an individual's home address is a real personal-safety and privacy cost,
> and a service address should be considered. Both stores will separately require a verified
> address from an individual developer account. **The narrow question for counsel:** what
> identifying information must appear *in this document*, as opposed to only in the store
> listings?

> **OPEN QUESTION — HOW THESE TERMS ARE ACCEPTED.** "By using the Service you accept these
> terms" is browsewrap, the weakest form of online contracting in US courts and vulnerable
> under EU unfair-terms rules where a consumer had no real opportunity to read the terms
> before being bound. If the operator wants these terms to be enforceable rather than merely
> informative, counsel should specify an affirmative acceptance step (a first-run screen with
> a link and a tap) and it must be built before publication.

## 2. What the Service is

BillTracking follows the public legislative record of the **United States Congress** and of
the **European Union institutions**, and presents it in three places:

- **Two accounts on X**, which post updates as bills move through the legislative process.
  These are produced by automated scripts that read official data and publish posts.
- **A mobile app**, which shows legislative updates and each bill's recorded history, lets you
  follow bills and set filters, and stores those choices on your own device.
- **A website** at billtracking.org, which is a set of static pages.

Source material comes from official public sources: the Congress.gov API for the United
States, and the European Parliament's OEIL and Cellar services for the European Union.

**How the Service is funded, stated as fact rather than as a legal category.** The Service has
never earned any money. There are no advertisements, no sponsors, no paid placements, no
in-app purchases, no subscriptions, and nothing is sold. The X accounts are **not enrolled in
and not eligible for** X's creator monetization programme. No monetization of the app is
planned.

> **🔵 OPEN QUESTION #1 — TRADER / COMMERCIAL STATUS. ANSWER THIS FIRST.** This section
> deliberately does **not** assert that the Service is "non-commercial". That word does legal
> work in several places at once — CalOPPA's "commercial website or online service" trigger,
> the CCPA's "for-profit business" test, and trader/consumer status under EU consumer law,
> Rome I and Brussels I — and the conclusion may differ between them on the same facts.
> Counsel should classify the Service in each regime rather than have the document assert a
> self-serving label. **This is the first question because three other parts of the package
> depend on the answer:** §11.4 assumes users are consumers, which presupposes the operator is
> a trader (przedsiębiorca) — if he is not, the unfair-terms analysis in §11.4 is inapplicable
> and that section is compliance theatre; §12's Rome I / Brussels I consumer-contract analysis
> has the same dependency; and the CalOPPA/CCPA treatment in the Privacy Policy turns on it
> too.

## 3. What the Service is **not**

Read this section carefully. It is the most important part of these terms.

**It is not legal advice.** Nothing on the Service is legal advice and nothing on it creates a
lawyer–client relationship. Bill descriptions, procedural histories and summaries are general
information. They are not advice about your situation, your rights, your obligations, or any
matter you are dealing with. If you need advice, consult a qualified lawyer in your
jurisdiction.

**It is not an official government source.** BillTracking is not affiliated with, endorsed by,
or operated by the United States Congress, the Library of Congress, the European Parliament,
the Council of the European Union, the European Commission, or any other public body. It is an
independent project that republishes and describes material those bodies publish. **Where the
Service and the official source disagree, the official source is correct and the Service is
wrong.** Verify against the official record before relying on anything for academic,
professional or legal purposes.

**It is not a complete record.** Coverage is limited to what the Service's automated processes
retrieve and publish. Bills, stages, votes and documents may be missing, delayed, or reported
out of order.

**It is not a poll, a petition or a form of civic participation.** See §7 on the vote feature.

## 4. Accuracy, errors and corrections

The Service is produced by automated processes operating on external data sources. **It will
contain errors.** Automated classification of legislative stages is genuinely difficult: the
same procedural event can be recorded differently in different official feeds, and deciding
which stage a bill has reached from those records is an inference that can go wrong.
Procedural statuses shown or posted by the Service may therefore be incorrect.

We aim for accuracy. We do **not** guarantee that the Service is accurate, current, complete
or free of error, and you should not treat it as authoritative. This is an honest statement of
what an automated service can achieve; it is not a disclaimer intended to excuse indifference.

Official sources can also lag or contain errors of their own, and the Service inherits them.
An update may appear here after it appears on Congress.gov or in the European Parliament's
services, or may reflect a source record that is itself provisional.

**Reporting an error.** You can write to **accuracy@billtracking.org**. That address exists and
receives mail. A mechanism exists in the Service's code for overriding and correcting
published items.

> **OPEN QUESTION — WHAT MAY HONESTLY BE PROMISED ABOUT CORRECTIONS.** This draft deliberately
> stops at "you can write to this address, and a correction mechanism exists in the code". It
> does **not** say that every report is read, that reports will be reviewed, that corrections
> are published, or that a public correction log exists — because none of that is established
> as a live, sustainable practice. An unmet responsiveness or accuracy commitment in
> public-facing terms is a deceptive-practices exposure under FTC Act § 5 and under the EU
> Unfair Commercial Practices Directive, regardless of the project's size or revenue. House
> precedent already runs this way: the claim "every report is read" was deliberately softened
> elsewhere in the product for exactly this reason. If and when a public correction log is
> live at a stable URL, add it here in the present tense with the URL, and keep the wording
> identical across the app, the site and this document.

> **NOTE — NO PAST-INCIDENT ADMISSION IS MADE HERE.** An earlier draft stated that the project
> had previously published a post wrongly saying a bill had passed a chamber. Nothing in the
> source-code audit establishes that, and an unverified self-incriminating admission is as bad
> as an unverified boast — worse, because it is quotable against the operator by exactly the
> audience this document is written for. If the operator wants to disclose a specific past
> error, the specific post must be identified and verified first; the general and provable
> statement above stands on its own in the meantime.

## 5. AI-generated summaries

Some content on the Service is written by an AI language model. Where a summary is
AI-generated, it carries the label **[AI-Generated]** in the app and in the X posts. In the app
the label is structurally attached to the summary, so a summary cannot be displayed without
it. You can turn AI summaries off entirely in the app's settings.

Two scope limits, stated plainly because the honest claim is narrower than the one this
section could be tempted to make:

1. **Not every post involves AI.** Several kinds of post are assembled purely from the official
   record with no model involvement at all. Those correctly carry no label. The accurate claim
   is *"AI-generated summaries are labelled"* — not *"every post is labelled"*.
2. **There is a known labelling gap in page metadata.** The website's permalink generator
   places the AI-generated summary, **without the label**, into the page's meta description and
   into its Open Graph and Twitter card tags. That means a search-engine result or a social
   media link preview can show AI-generated text with no marker on it. This is a known,
   currently unfixed defect. It is disclosed here rather than papered over.

> **OPEN QUESTION — FIX THE METADATA GAP BEFORE PUBLICATION IF POSSIBLE.** The cleanest outcome
> is to fix the permalink generator so the label travels with the text into meta and card tags,
> and then delete limb 2 above. Publishing a disclosed defect is better than publishing a false
> claim, but fixing it is better than either — and an unlabelled AI-generated snippet
> distributed into search results is precisely the surface AI Act Art 50(4) is aimed at.

AI-generated summaries can be wrong, incomplete or misleading even when the underlying data is
correct. Treat them as a starting point, not as a substitute for reading the bill.

**Legal basis for the labelling.** Article 50(4) of Regulation (EU) 2024/1689 (the AI Act)
requires deployers of an AI system that generates or manipulates text **published with the
purpose of informing the public on matters of public interest** to disclose that the text has
been artificially generated. Summaries of pending legislation fall squarely within that. Those
obligations apply from **2 August 2026**. The [AI-Generated] label is intended to satisfy that
duty and is not merely a courtesy.

> **OPEN QUESTION — DO NOT OVER-COMPLY.** The separate machine-readable marking duty in Art
> 50(2) falls on the **provider** of the generative model, not on BillTracking as a deployer.
> This document should not promise machine-readable watermarking that the project neither
> controls nor implements. Counsel to confirm the deployer/provider split on these facts and to
> confirm that the visible label satisfies Art 50(4) in the form used. See also the note on the
> Art 50(4) second-subparagraph editorial-review exemption in the counsel worksheet — we do not
> rely on it. Source: <https://artificialintelligenceact.eu/article/50/>

## 6. Acceptable use

These rules apply to your use of the Service. They are ordinary contractual terms; they are
not, and do not purport to be, a content-moderation policy for material supplied by users,
because the Service hosts no material supplied by users (see §7 — nothing is transmitted
anywhere, because there is no server).

**You agree not to:**

- attempt to access, probe, interfere with or disrupt the Service, its infrastructure, or its
  data sources — including by making automated requests to Congress.gov or to European
  Parliament services at a rate that burdens them;
- copy or redistribute the Service's presentation, layout, wording or design in a way that
  presents it as an official government product or as your own work;
- present the Service, or content taken from it, as an official record, as endorsed by any
  institution, or as legal advice;
- use the Service in breach of any law that applies to you.

**What we can actually do about it.** This is a short list, because the Service's architecture
genuinely limits it:

- We can **remove, correct or withhold content we publish** — a post on X, a page on the
  website, a summary in a future release of the app.
- We can **decline to publish** an item, or discontinue a feature or a whole area of coverage.
- We can **stop responding** to correspondence that is abusive or vexatious.

**What we cannot do, and do not claim to be able to do.** There are no accounts and no user or
device identifiers anywhere in the Service. We therefore have **no ability to suspend, ban,
rate-limit or otherwise act against an individual user**. We do not claim otherwise, and you
should not read this section as implying a moderation capability that does not exist. Nor can
we change anything already shipped inside an installed copy of the app except by publishing an
update through the app stores.

**Complaints about a restriction.** If we remove or withhold something and you think we were
wrong, write to contact@billtracking.org and say what was removed and why you disagree.

> **NOTE — THE DSA FRAMING HAS BEEN REMOVED, DELIBERATELY.** An earlier draft presented this
> section as satisfying Article 14 of Regulation (EU) 2022/2065 and added dual Art 11/12 points
> of contact. That was an overbuild on a scope question that is answered one step earlier: the
> DSA applies to **intermediary services** — mere conduit, caching or hosting (Art 3(g)).
> BillTracking publishes exclusively its own content and, as built, stores nothing supplied by a
> recipient of the service. On those facts the Regulation's scope is not engaged at all, so
> Arts 11, 12 and 14 do not attach — not because the Art 19 micro-enterprise exemption applies
> (that exempts only the Section 3 online-platform duties). Counsel should confirm that scope
> conclusion rather than re-import the obligations. **If reader votes are ever submitted and
> stored, re-run DSA scope from the start:** stored reader-submitted votes may make this a
> hosting service, at which point Arts 14, 16, 17 and 20 need drafting and an Art 24(5)
> Transparency Database process is needed. Source:
> <https://eur-lex.europa.eu/eli/reg/2022/2065/oj>

> **NOTE — RULES ABOUT VOTING LIVE IN §7.1, NOT HERE.** An earlier draft prohibited distorting
> reader-sentiment figures and claimed a power to withhold or reset a bill's results. Both
> describe a system that does not exist: the figures are a fixed constant plus your own tap,
> nobody's interaction can affect anyone else's view, and there is nothing on a server to reset.
> Those provisions now sit in §7.1 in the conditional, and should be moved back into this
> section in the same commit that ships a real vote backend — not before.

## 7. Reader voting — **a planned feature, not a working one**

> **This section describes something that does not exist yet. Read it as a description of
> intent, not of behaviour.**

The app shows a vote control on bills and displays up/down figures and a geographic breakdown.
**None of it is connected to anything.**

As the Service is built today:

- Tapping a vote chip writes a value **only to your own device**, into the app's single local
  storage entry. **Nothing is transmitted anywhere.** The app makes no network requests at all.
- The vote counts you see are **a fixed sample constant** built into the app, plus your own tap.
  They are not counts of anything.
- The geographic breakdown you see is **generated by a pseudo-random number generator**. It is
  synthetic. It does not describe any real readers, including you.
- There is **no server** anywhere in this project, so there is nothing collecting, aggregating,
  storing or publishing votes.

**Do not cite any figure shown by this feature.** It is placeholder display data, not a
measurement, and it is not a survey, a poll, or evidence of reader opinion.

> **OPEN QUESTION — SHOULD THE FEATURE SHIP AT ALL IN THIS STATE?** Displaying synthetic numbers
> that a reader could mistake for real reader sentiment is a misleading-presentation risk in its
> own right — under FTC Act § 5, under the Unfair Commercial Practices Directive, and under
> Apple Guideline 2.3 (accurate metadata / no misleading functionality). A disclosure buried in
> the terms is a weak fix. Strongly consider either labelling the figures as sample data **in
> the interface itself**, or not shipping the feature until it is real. Counsel and the operator
> to decide; this document should be updated to match whatever ships.

### 7.1 If and when voting is built

The intended design, **not yet implemented**, is that a vote would be submitted **anonymously**:
with no account, no user identifier and no device identifier attached, together with a coarse
self-reported location (country, and US state for US readers) so results can be shown by place.

If that design is built as intended, these consequences would follow, and readers should
understand them before the feature goes live:

- **A vote could not be changed or withdrawn after submission**, because nothing would link it
  to you. That is a deliberate privacy choice, not an unfixed limitation.
- **Repeat voting could not be prevented**, for the same reason. Results would be an indication
  of sentiment among people using the app — not a survey, not a poll, and not a statistically
  valid measurement of opinion.
- **These rules would apply, and do not apply today:** you would agree not to distort, inflate
  or manipulate the figures, including by automated or bulk interaction, and not to attempt to
  identify, single out or re-identify any individual reader from any aggregate figure, or to
  combine displayed figures with other data for that purpose.
- **The only available remedy against distortion would be blunt.** We would be able to withhold
  or reset the published results for a bill whose totals we believed had been distorted. We
  would **not** be able to identify, remove or act against particular votes or particular
  people, and we do not claim we would.

> **OPEN QUESTION — ANY ANTI-ABUSE MECHANISM DESTROYS THE ANONYMITY POSITION.** Attaching a
> per-device token, salted hash, rate-limit key or abuse fingerprint to a vote submission would
> make votes **pseudonymous rather than anonymous**, which pulls the whole dataset inside the
> GDPR and, because a vote on legislation is a political opinion, inside Art 9. Nothing of the
> kind may be added without redoing the data-protection analysis first. Also note the precise
> point, which is narrower than "no Art 9(2) condition exists": explicit consent under Art
> 9(2)(a) is available in the abstract, but it is not compatible with an anonymous submission
> design, because demonstrable consent under Art 7(1) requires an identifier — the very thing
> the design removes. The feature would need redesign, not a rewritten justification. Counsel
> should also decide, before anything is built, whether the design is meant to survive as
> anonymous data outside the GDPR (Recital 26) or as personal data not requiring identification
> (Art 11, which relieves Arts 15–20 but imposes Art 11(2) duties). The Privacy Policy carries
> the full analysis.

### 7.2 Small-cell suppression — a planned disclosure control

The app contains logic that withholds the up/down split for a geographic cell with fewer than
ten recorded votes, while still showing that cell's total.

Stated accurately: **this is display logic operating on sample data. It is not a working privacy
safeguard and must not be relied on as one.** It protects nothing today, because every figure it
operates on is invented, and the logic as written would not reliably protect real readers if it
were wired to a real backend unchanged.

> **OPEN QUESTION — FIX BEFORE ANY REAL DATA IS EVER WIRED IN.** The specific defects in the
> current implementation, and the fix, are recorded in the internal review notes and in the
> component's code comment rather than here: a public terms document is not the right place for
> a working description of how to defeat a disclosure control, and that paragraph must not
> survive into the version published on the day a real backend ships. Until the fix is made, do
> not restate this mechanism as a protection anywhere in the app, the site or this document.
> Note also that k-anonymity thresholds are not a guarantee against inference attacks even when
> implemented correctly.

## 8. Privacy

How the Service handles personal data is described in the **Privacy Policy** at
[[PLACEHOLDER: published privacy policy URL — this is a build task, not a drafting task: the
site must be deployed, the policy published at a stable path, and a Privacy Policy link added
to the app's settings screen, before this placeholder can be filled. Both stores require both
the public URL and the in-app link. Confirm the App Store Connect support URL at the same
time.]]

In short, and accurately as built:

- **The app makes no network requests at all.** It contains no analytics, crash-reporting,
  telemetry, advertising or attribution software, and it generates and transmits no device
  identifier, install identifier or push token.
- **The app stores exactly one entry on your device**, holding your tab, filters, followed
  bills, search keywords, display toggles, notification preferences, any votes you have tapped,
  and any country or state you have entered. Deleting the app removes it from the device.
- **The website loads no scripts and no third-party resources**, and sets nothing on your
  device. It has no analytics. It is built that way today and is not yet deployed.
- **The website will be hosted on GitHub Pages.** GitHub, as host, necessarily processes
  visitors' IP addresses at the network layer in order to serve pages. GitHub does not make
  visitor access logs available to us, and we do not receive them — but we do not claim that no
  IP processing occurs.
- **Email you send us is processed by Microsoft**, which provides the mailbox.

> **NOTE — KEEP THIS SECTION OUTSIDE THE CONTRACT.** This draft deliberately does *not* say the
> Privacy Policy "forms part of these terms". A GDPR transparency notice is better kept outside
> the contract: incorporating it muddies any Art 6(1)(b) analysis and converts a notice that
> must be updatable unilaterally into a contractual term that may not be. Counsel to confirm.

> **OPEN QUESTION — IF ANALYTICS IS EVER ADDED.** A decision document in the site repository
> contemplates possibly adding Cloudflare Web Analytics later (cookieless, no device storage,
> no identifier). It is **not installed**. If it is ever adopted, this section and the Privacy
> Policy each need one added paragraph, the provider must be added to §9's third-party names
> list and to the Privacy Policy's processor table, and the app-store data declarations must be
> revisited.

## 9. Intellectual property

**The official material is not ours.** The legislative record itself — bill texts, votes,
procedural histories and official documents of the US Congress and of the EU institutions — is
not owned by BillTracking. Works of the United States Government are not subject to copyright
under 17 U.S.C. § 105, and legislative enactments are treated as uncopyrightable edicts of
government. EU institutional material is published under those institutions' own reuse terms.
Nothing in these terms asserts any right over that underlying material, and nothing here
restricts your use of it at its source.

> **OPEN QUESTION — SOURCE ATTRIBUTION WORDING.** The EU institutions' reuse conditions (e.g.
> Commission Decision 2011/833/EU and the European Parliament's own reuse notice) generally
> permit reuse subject to attribution and non-distortion conditions, and the Congress.gov API
> has its own attribution and rate-limit guidance. Counsel should confirm the exact wording each
> source requires; it should then be stated verbatim here and in the app rather than
> paraphrased.

**What we do claim.** We claim rights in the **selection, arrangement and structuring** of the
material we publish, in our categorisation of legislative stages, in the app and website design
and layout, and in the wording of our own explanatory text and the BillTracking name. You may
not copy or redistribute that material except as permitted below or by law.

**What we expressly do not claim.** We do **not** assert copyright in the AI-generated summaries
themselves. Text produced by a generative model without meaningful human authorship is generally
not copyrightable in the United States, and the position elsewhere is unsettled. It would be
inconsistent for a project that opens this section by explaining that government works are
uncopyrightable to then claim exclusive rights in material that is probably in the public domain
too.

> **OPEN QUESTION — HUMAN EDITING.** If a summary is meaningfully edited by a human before
> publication, the edited version may attract protection in the edits. Counsel to advise whether
> to say anything about that here, or to leave the disclaimer unqualified — which is simpler and
> safer.

**What you may do without asking.** Quote reasonable extracts, link to the Service, share
individual posts, take screenshots, and use it for teaching, study, research, journalism and
commentary — with attribution to BillTracking, and provided you do not present the material as
official or as your own.

> **OPEN QUESTION — BULK OR DATASET ACCESS.** The core audience is law professors, so requests
> for bulk access are plausible. Decide deliberately rather than leaving it ambiguous. Note that
> any dataset containing reader votes would be a dataset of political opinions and would need
> its own analysis before being offered to anyone.

**Third-party names.** Names and marks of the US Congress, the EU institutions, X, Apple,
Google, Microsoft and GitHub belong to their owners and are used descriptively only.

> **NOTE — CLOUDFLARE WAS REMOVED FROM THE LIST ABOVE.** It is not part of the stack. It appears
> only in an internal decision document as a possible future addition, and naming it here would
> imply a vendor relationship that does not exist. Add it only in the same change that actually
> adopts it (see §8).

## 10. Links to other sites, and the X accounts

The **app** contains links that open in your own browser or mail app — billtracking.org, x.com,
congress.gov, oeil.europarl.europa.eu — and email links. The **website** likewise contains plain
links to other sites [[PLACEHOLDER: enumerate the site's outbound link destinations once the
site's link inventory has been checked; the app's list above is audited, the site's is not]].
Opening a link hands it to your own browser or mail app, which then makes the request. We have
no control over those sites, do not endorse them, and are not responsible for their content,
availability or privacy practices. Their own terms and privacy policies apply once you arrive.

The X accounts are hosted on a platform we do not control. X's own terms govern your use of that
platform, and X may change, restrict or remove the accounts or their content independently of
us.

## 11. Availability, disclaimers and liability

### 11.1 Availability

The Service is provided as-is and may be unavailable, interrupted, delayed, changed or
discontinued at any time, with or without notice. Features may be added or removed. We do not
commit to any level of availability, to continued coverage of any bill or jurisdiction, or to
maintaining the Service at all.

### 11.2 Disclaimers

To the fullest extent permitted by the law that applies to you, the Service and all content on
it are provided **"as is" and "as available", without warranties of any kind**, express, implied
or statutory. We specifically disclaim implied warranties of merchantability, fitness for a
particular purpose, accuracy, completeness, timeliness, non-infringement and uninterrupted
availability.

We make no warranty that the Service is accurate, that legislative stages are correctly
classified, that coverage is complete, that AI-generated summaries fairly represent the bills
they describe, that any displayed figure means anything (see §7), or that the Service is free of
defects.

### 11.3 Limitation of liability

To the fullest extent permitted by applicable law, we are not liable for loss or damage arising
from your use of, or reliance on, the Service. That includes loss arising from inaccurate,
incomplete, delayed or misclassified legislative information; from AI-generated summaries; from
reliance on any displayed figure; from unavailability; and from any academic, professional,
commercial or legal decision taken in reliance on anything published here.

We do not exclude or limit liability for **damage caused intentionally**, which cannot be
excluded in advance under Article 473 § 2 of the Polish Civil Code; for death or personal injury
caused by negligence; for fraud or fraudulent misrepresentation; or for anything else that
cannot lawfully be excluded or limited.

> **OPEN QUESTION — CONFIRM THE POLISH CARVE-OUT LIST, DO NOT IMPORT THE ENGLISH ONE.** The
> death/personal-injury and fraud limbs come from the English-law template. The rule that
> actually binds this operator is Polish: art. 473 § 2 k.c. makes void in advance any stipulation
> excluding liability for damage caused intentionally (*szkoda wyrządzona umyślnie*). The
> operator is a natural person resident in Poland with personal, uncapped exposure, and Polish
> courts are the realistic forum. Counsel should confirm the full Polish mandatory list and prune
> or keep the imported English limbs accordingly.

### 11.4 If you are a consumer in the EU or the UK

**Your statutory rights are not affected by anything in this section.** Sections 11.2 and 11.3
apply only to the extent the law permits, and against consumers in the EU and UK that extent is
limited.

> **INLINE FLAG — THESE CLAUSES ARE PARTLY UNENFORCEABLE AGAINST EU CONSUMERS, AND THAT IS A
> PROBLEM IN ITSELF.** Directive 93/13/EEC on unfair terms in consumer contracts renders
> non-negotiated terms unfair — and therefore not binding — where they cause a significant
> imbalance to the consumer's detriment; blanket exclusions of liability sit on the Annex's
> indicative list. Polish law (Civil Code art. 385¹ et seq.) applies the same analysis and is the
> operator's home forum; note that abusive clauses have been dealt with by **UOKiK administrative
> decision since the April 2016 reform**, and the old register of prohibited clauses is legacy —
> do not cite the register as the live mechanism. Two practical consequences counsel should
> weigh: (a) a broad US-style exclusion may simply fail against EU consumers however it is
> drafted; and (b) *including* a clause known to be unfair can itself be a compliance problem
> under the UCPD and can attract consumer-authority attention, so the maximalist draft is not
> costless. A narrower, honestly-scoped clause may be worth more than a broad unenforceable one.
> **This whole subsection is conditional on the trader-status answer in §2:** Directive 93/13 and
> art. 385¹ apply only between a trader and a consumer. If the operator is not a trader, this
> subsection is inapplicable and should be cut rather than kept as reassurance.

> **OPEN QUESTION — LIABILITY CAP.** A conventional cap ("the greater of amounts paid or $100")
> is meaningless here: users pay nothing and the Service earns nothing. Counsel to decide
> between a nominal cap, exclusions only, or no cap. Note that the relevant real-world exposure
> is an individual's personal assets, not a company's — which argues for taking this section
> seriously rather than treating it as boilerplate.

## 12. Governing law and disputes

> ## 🔵 OPEN QUESTION — GOVERNING LAW AND JURISDICTION. **NOT DECIDED. DO NOT PUBLISH THIS SECTION UNTIL COUNSEL HAS CHOSEN.**
>
> [[PLACEHOLDER: governing law]] · [[PLACEHOLDER: forum / dispute resolution]]
>
> This draft deliberately **does not pick**, because picking badly is worse than leaving it to
> advice.
>
> The facts counsel needs:
>
> - The operator is **an individual resident in Poland**. There is **no company** and none is
>   planned, so there is no entity-of-incorporation to point at.
> - Users are **in the United States and the European Union**, and are targeted there
>   deliberately: US and EU law-school audiences, a dedicated EU section, EU institutional data
>   sources.
> - The Service is **free**, earns nothing, and its users are overwhelmingly **consumers** — but
>   whether the operator is a **trader** is itself undecided (§2), and the consumer-contract
>   rules below only engage if he is.
>
> The tensions:
>
> 1. **A choice-of-law clause will not fully work against EU consumers.** Under Rome I (Reg.
>    593/2008) Art 6, a choice of law in a consumer contract cannot deprive the consumer of the
>    mandatory protections of their country of habitual residence where the trader directs
>    activities there. This Service plainly directs activities at Member States.
>    <https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=celex%3A32008R0593>
> 2. **A forum clause has the same problem.** Under Brussels I Recast (Reg. 1215/2012) Arts
>    17–19, a consumer domiciled in a Member State may generally sue, and can generally only be
>    sued, in their own Member State.
>    <https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=celex%3A32012R1215>
> 3. **The operator's own residence points at Poland**, which is where any judgment would
>    realistically reach him — an argument for not fighting a battle the clause cannot win.
> 4. **US users are a separate analysis.** US courts more readily enforce choice-of-law and
>    forum clauses online, but enforceability turns on presentation and acceptance (see the
>    browsewrap flag in §1), and some state consumer statutes resist waiver.
>
> A plausible shape, for counsel to accept or reject and **not a recommendation from this
> draft**: name Polish law and the Polish courts as the general rule; add an express carve-out
> preserving for EU-resident consumers the mandatory protections and the courts of their own
> country of residence; and say nothing purporting to strip a US user of a non-waivable
> state-law right.
>
> Whatever is chosen, the **GDPR applies regardless** by virtue of Art 3, and cannot be
> contracted out of. <https://gdpr-info.eu/art-3-gdpr/>

> **OPEN QUESTION — EU ONLINE DISPUTE RESOLUTION / ADR.** If the operator is a trader for
> consumer-law purposes (§2), information duties about out-of-court dispute resolution may
> attach. Note that the EU ODR platform ceased operating in 2025; counsel should state the
> current position rather than copy the obsolete standard clause.

## 13. Children

The Service is not directed to children. It is a legislative-information service intended for an
adult and university-student audience. The app collects nothing from anyone. The website sets
nothing on your device and we receive no visitor logs (see §8). No personal information is
therefore knowingly collected from children or from anybody else.

> **OPEN QUESTION — MINIMUM AGE AND STORE RATINGS.** The operator must set an intended minimum
> age. It drives Apple's age-rating questionnaire and Google Play's IARC rating, and both store
> forms demand answers regardless of how low the real risk is. Legislative subject matter means
> bill summaries will touch violence, drugs and sexual-offence topics, which interacts with the
> newer questionnaire items. Answers must be honest — Apple Guideline 2.3.6 warns that
> mis-rating can trigger regulatory inquiry. Counsel should also address GDPR Art 8 (digital
> consent age, 13–16 by Member State) and the UK Age Appropriate Design Code, which applies to
> services *likely to be accessed by* children — a lower bar than "directed to".

## 14. Changes to these terms

We may update these terms. The version in force is the one published at the terms URL, with its
version number and effective date shown at the top.

There are no accounts and no mailing list, so there is no channel through which we can notify
you directly. [[PLACEHOLDER: describe the notification mechanism that actually exists — e.g. an
in-app notice on first launch after a change, a dated changelog on the site, a post on X.]]

> **OPEN QUESTION — THE MECHANISM MUST EXIST BEFORE IT IS DESCRIBED.** California's CalOPPA
> requires an online service's policy to describe its process for notifying users of material
> changes, and it has no revenue or user-volume threshold (subject to the "commercial" question
> flagged in §2). Whatever is written into the placeholder above must be a mechanism that is
> built and running, not an intention. The same rule applies to any promise to keep superseded
> versions accessible for comparison: do not promise a versioned archive until one exists.

## 15. General

If any provision of these terms is found unenforceable, the rest remains in effect and the
unenforceable provision applies to the maximum extent permitted. Our failure to enforce a
provision is not a waiver of it. You may not transfer your rights under these terms.

---

## Counsel worksheet — delete this whole worksheet only after every inline blockquote above has been resolved and removed

**This worksheet is an index of the inline notes, not a substitute for them.** It exists so
counsel can see the whole question set at once. Deleting it does not resolve anything: each item
below corresponds to a blockquote sitting next to the text it qualifies, and resolving a question
means editing that text and then deleting that blockquote. If this worksheet is deleted while the
inline blockquotes remain, nothing is lost; if the inline blockquotes are deleted and this
worksheet is kept, every hedge in the document has been stripped while every confident claim
stands. Consider moving this worksheet into a separate review-notes file so it cannot survive
publication.

### Questions with an inline counterpart

1. **🔵 Trader / commercial status — answer first.** §11.4, §12 and the Privacy Policy's
   CalOPPA/CCPA treatment all depend on it. (§2)
2. **🔵 Governing law and jurisdiction — undecided, counsel must choose.** (§12)
3. Published identity and address: e-Commerce Directive Art 5 and its Polish implementation, not
   the CRD; how much must appear here versus in the store listings. (§1)
4. Whether an affirmative acceptance step is built, or the terms remain browsewrap. (§1)
5. What may honestly be said about corrections; whether a public log exists and at what URL. (§4)
6. Whether to disclose any specific past error, and only after the specific post is verified. (§4)
7. Fix the site-metadata AI-labelling gap, or publish the disclosure in §5 as written. (§5)
8. Confirm the AI Act deployer/provider split and that the visible label satisfies Art 50(4). (§5)
9. Confirm the DSA scope conclusion — that the Service is not an intermediary service at all —
   and re-run scope from scratch if reader votes are ever submitted and stored. (§6)
10. Whether the vote UI should ship at all while its figures are synthetic. (§7)
11. Confirm that no token, hash or fingerprint will be attached to any future vote submission,
    and decide the Recital 26 / Art 11 framing before anything is built. (§7.1)
12. Fix the small-cell suppression logic before any real data is wired in. (§7.2)
13. Privacy policy URL — a build task: deploy site, publish policy, add in-app settings link,
    confirm the App Store Connect support URL. (§8)
14. Whether analytics is ever added (one added paragraph, plus §9 and processor table). (§8)
15. Exact attribution wording required by Congress.gov and the EU institutions. (§9)
16. Whether bulk or dataset access will ever be offered. (§9)
17. The website's outbound link inventory, which is unaudited. (§10)
18. Confirm the Polish mandatory carve-out list under art. 473 § 2 k.c.; prune the imported
    English limbs if appropriate. (§11.3)
19. Liability cap: nominal, exclusions only, or none — under EU consumer-law constraints, and
    conditional on the trader answer. (§11.4)
20. Consumer ADR/ODR information duties, if any. (§12)
21. Intended minimum age; Apple and IARC answers; GDPR Art 8 and UK AADC. (§13)
22. The actual change-notification mechanism, and no versioned-archive promise until one is
    built. (§14)
23. Effective date and version number, once counsel signs off. (header)

### Additional review notes with no inline counterpart

These are deliberately kept out of the published text.

- **AI Act Art 50(4), second subparagraph** exempts content that has undergone human review or
  editorial control where a natural or legal person holds editorial responsibility for its
  publication. The bots publish unreviewed on a cron schedule, so **we do not rely on it** — which
  is precisely why the meta-tag labelling gap in §5 matters rather than being a technicality. If a
  human review step is ever introduced, revisit. The 2 August 2026 application date and the Art
  50(2) provider/deployer split are stated correctly in §5.
- **Small-cell suppression, the specific defects** (kept out of §7.2 because a public document
  should not carry a working description of how to defeat a disclosure control): MIN_CELL = 10
  exists in one UI component; it withholds the up/down split below ten while always showing the
  row total; visible row up-counts sum exactly to the published overall total, so a hidden split
  can be recovered by subtracting the visible ones; and it is recomputed on every render rather
  than fixed once, so a cell hidden at nine becomes visible at ten and the transition itself can
  be informative. The fix — evaluate suppression once and stickily across every derived view, and
  suppress the total as well as the split where differencing is possible — is cheap and must
  precede any backend. Mirror this note as a code comment in the component.
- **GDPR Art 30 record of processing.** The Art 30(5) derogation for organisations under 250
  people applies only where processing is occasional, presents no risk to rights and freedoms, and
  involves no special-category data. Inbound correspondence to two published addresses is not
  occasional, so on the regulator reading a record is required for at least the email processing.
  Create a one-page internal Art 30(1) record covering email correspondence and site
  hosting/IP at the GitHub layer: purposes, categories of data subject and data, recipients
  (Microsoft, GitHub), transfers, retention, security measures. **Internal only — do not publish
  it and add nothing to the policy.**
- **Polish Art 85 GDPR derogation.** Poland implemented Art 85 (journalistic, academic, artistic
  or literary expression) in the Act of 10 May 2018, disapplying substantial parts of the
  Regulation — including Arts 13–16 and 21 — for such processing. Republishing and describing the
  legislative record about named legislators is the paradigm case, and the operator is established
  in Poland. This is a priority counsel question for the Privacy Policy: it is cheaper to answer
  than most of the placeholders in the package and may remove the Art 14 notification problem for
  legislator data entirely.
- **Verify every citation before publication.** The audience is law professors, who will check
  citations before they check anything else. Counsel to verify each case name, case number,
  article number and date independently — particularly any 2025 or 2026 authority, where details
  may have moved, and where the drafter's *characterisation* of a holding must not be accepted at
  face value.

*Draft prepared 2026-07-19 from an audit of the project's source code. Not legal advice. Do not
publish without review by a qualified lawyer familiar with EU consumer and data protection law
and with US online-terms enforceability.*
