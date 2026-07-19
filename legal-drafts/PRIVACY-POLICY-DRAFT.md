> # ⚠️ DRAFT FOR COUNSEL REVIEW — NOT LEGAL ADVICE
>
> This document was prepared as a working draft for a qualified lawyer to review, correct
> and approve before publication. It is not legal advice and must not be published as-is.
> Several statements in it depend on facts about the app's implementation that have **not
> yet been verified** — those are collected in [Section 16, Open Questions for the
> Owner](#16-open-questions-for-the-owner). Any claim that turns out to be wrong must be
> removed rather than softened: a wrong privacy claim is worse than an admitted gap.
>
> Draft date: 2026-07-19. Effective date: **[TO BE SET ON PUBLICATION]**.

---

# BillTracking Privacy Policy

**Effective date:** [TO BE SET]
**Last updated:** [TO BE SET]
**Applies to:** the BillTracking mobile app (iOS and Android) and the website at billtracking.org

---

## 1. Plain-English summary

BillTracking publishes the official legislative record of the US Congress and the EU
institutions. It is free, independent and non-commercial. There are no ads, no sponsors, no
subscriptions and nothing is sold.

In short:

- **There are no accounts.** You never create one, never log in, and never give us a name,
  an email address or a password.
- **Your personal settings never leave your phone.** The bills you follow, your notification
  settings, your display preferences and what you have already read are stored in the app's
  own storage on your device. We do not receive them and cannot see them.
- **If you vote on a bill, the vote is sent to us anonymously.** It carries no user
  identifier and no device identifier. It is not connected to you, to your other votes, or
  to anything else you do in the app.
- **The deliberate consequence:** because a vote is not tied to you, we cannot find it
  again. That means we cannot show you your votes, change them, or delete them at your
  request. We accepted losing those features in exchange for not holding a record of your
  political opinions. There is also, for the same reason, no way for us to prevent someone
  voting twice.
- **We hide small results.** If fewer than 10 people have voted in a given place, we do not
  show how that group voted — only that votes exist. This is to stop a handful of people's
  opinions being exposed by a public tally.
- **A vote is a political opinion**, which European law treats as one of the most sensitive
  kinds of information there is. The whole design above exists because of that.
- **Uninstalling the app deletes everything we hold about you locally**, because everything
  we hold about you is local.

The rest of this document is the detailed version, written to meet the legal requirements
that apply to us.

---

## 2. Who we are (controller identity)

**[OPEN — see Section 16.1.]** The publisher of BillTracking is
**[LEGAL ENTITY NAME]**, established at **[ADDRESS, COUNTRY]**.

Contact for any privacy question: **[CONTACT EMAIL]**.

We have not appointed a Data Protection Officer, and we do not believe we are required to
under Article 37 GDPR. **[Counsel to confirm.]**

**EU representative (Article 27 GDPR):** **[OPEN — see Section 16.2.]** Article 27 requires
a controller outside the EU that falls within Article 3(2) to appoint a written
representative in the Union, unless the narrow exemption in Article 27(2)(a) applies
([Art 27 GDPR](https://gdpr-info.eu/art-27-gdpr/)). Whether that exemption is available to us
depends on facts not yet settled (see Section 16). This section must be completed before
publication.

We do not claim that being free or non-commercial puts us outside the GDPR. Article 3(2)(a)
applies to controllers outside the EU offering services to people in the Union
"irrespective of whether a payment of the data subject is required", and BillTracking is
deliberately aimed at readers in the EU ([EDPB Guidelines 3/2018 on territorial
scope](https://www.edpb.europa.eu/sites/default/files/files/file1/edpb_guidelines_3_2018_territorial_scope_after_public_consultation_en_1.pdf)).
This document is written as a GDPR notice.

---

## 3. What stays on your device and never reaches us

The following are stored by the app in local storage on your own device:

| What | Examples |
|---|---|
| Followed bills | the bills you have chosen to track |
| Notification preferences | which alerts you want, if any |
| Display preferences | appearance and layout settings |
| Reading state | which posts or updates you have already seen |

We do not transmit, receive, back up or synchronise any of this. There is no cloud account
to sync it to. If you uninstall the app, or clear its data, it is gone — and we have no copy
to restore or to delete on request.

Because this information never leaves your device, it is not "collected" for the purposes of
the Google Play Data safety declaration or Apple's App Privacy disclosures, both of which
define collection as data being transmitted off the device
([Google Play Data safety](https://support.google.com/googleplay/android-developer/answer/10787469?hl=en);
[Apple App Privacy details](https://developer.apple.com/app-store/app-privacy-details/)).
We describe it here anyway, because you should know what the app stores and because it
explains why there is nothing for us to delete.

---

## 4. Reader votes on bills

### 4.1 What is sent

When you tap to record a view on a bill, the app sends:

- the bill the vote relates to;
- the position you chose (from a fixed set of options — there is no free text);
- a coarse geographic value: your country, and for the United States your state, used only
  to display aggregate breakdowns.

**[OPEN — see Section 16.4:** how the country/state value is determined, and what timestamp
granularity is stored, are not yet confirmed and this section cannot be finalised until they
are.**]**

### 4.2 What is *not* sent

No account identifier (there are no accounts). No device identifier. No advertising
identifier. No session token. No name, email address or phone number. No login of any kind.

There is deliberately no anti-abuse token, rate-limiting key or device fingerprint attached
to a vote. Any such value would make the vote *pseudonymous* rather than anonymous, and
pseudonymised data remains fully personal data under the GDPR
([Recital 26](https://gdpr-info.eu/recitals/no-26/);
[EDPB Guidelines 01/2025 on pseudonymisation](https://www.edpb.europa.eu/system/files/2025-01/edpb_guidelines_202501_pseudonymisation_en.pdf)).
**[OPEN — must be verified in code before publication; see Section 16.3.]**

### 4.3 What we cannot do, and why

Because a vote carries nothing that points back to you:

- **We cannot show you your own votes.**
- **We cannot let you change or withdraw a vote after it is cast.**
- **We cannot delete a vote on request**, because we cannot identify which vote is yours.
- **We cannot prevent double voting**, and we do not claim the totals are protected against
  it.

These are not refusals to help. They are the direct, intended cost of not holding a linkable
record of your political opinions. Under Article 11 GDPR, a controller that cannot identify
a data subject is not required to acquire additional information solely in order to comply
with the GDPR — and we will not do so. **[Counsel to confirm the Article 11 framing.]**

Your control over future votes is simple and complete: **do not vote.** Reading the app does
not require it, and voting is entirely optional.

### 4.4 Small-cell suppression

Where fewer than **10** votes exist for a given cut of the data, we withhold the breakdown
and show only that votes exist. This applies to per-place rows and to headline figures.

The purpose is to prevent a published tally exposing the opinions of a handful of
identifiable people. Suppression thresholds of this kind (k-anonymity) are a mainstream
disclosure control, but they are **not** a guarantee of anonymity and we do not present them
as one: the technique does not defeat inference attacks, and the academic literature is
explicit that it does not reliably prevent singling out
([Cohen & Nissim, PNAS 2020](https://www.pnas.org/doi/10.1073/pnas.1914598117)).

We treat the threshold of 10 as a public commitment. We will not lower it without updating
this policy and our app-store disclosures.

---

## 5. Why a vote is treated as highly sensitive

A view on a piece of legislation is a **political opinion**. Under
[Article 9 GDPR](https://gdpr-info.eu/art-9-gdpr/) political opinions are a *special
category* of personal data, subject to a much higher bar than ordinary personal data —
processing is prohibited unless a specific Article 9(2) condition applies, in addition to a
lawful basis under Article 6.

Our position, stated plainly: **we designed the vote feature so that the data we receive is
not personal data at all.** Where information is genuinely anonymous — that is, where the
person is not, and can no longer be, identified by any means reasonably likely to be used —
the GDPR does not apply to it ([Recital 26](https://gdpr-info.eu/recitals/no-26/)). Anonymity
is the foundation of this design, not consent.

We are careful about the limits of that claim:

- Anonymity must hold **at the moment of collection and from our own perspective**, not
  merely from the perspective of a reader looking at the published tallies. The Court of
  Justice confirmed this framing in *EDPS v SRB*
  ([C-413/23 P, 4 September 2025](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=celex:62023CJ0413)),
  which also confirmed that opinions can be personal data.
- The applicable framework is the EDPB's
  [draft Guidelines 02/2026 on Anonymisation (adopted 7 July 2026)](https://www.edpb.europa.eu/system/files/2026-07/edpb_guidelines_202602_anonymisation_v1_en_0.pdf),
  which require that data resist **singling out**, **linkability** and **inference**. Those
  guidelines are in **draft** and open for consultation until 30 October 2026; the final
  text may change the analysis, and this policy will be revisited when it is adopted.
- Anonymity under that framework is context-relative and must be **reviewed periodically**,
  not decided once. Re-identification risk grows as an app grows.

**We are treating votes as if they were special-category data regardless.** That is why they
carry no identifier, why small results are suppressed, and why we accept the loss of vote
editing and double-vote prevention.

**Note for readers outside the EU:** neither the CCPA/CPRA nor any enacted US state
comprehensive privacy law lists political opinions as "sensitive personal information"
(see [Cal. Civ. Code § 1798.140](https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=1798.140.&lawCode=CIV)).
We are not claiming US law classifies your vote as sensitive. We apply the stricter European
standard everywhere as a matter of design choice.

---

## 6. Lawful basis

| Processing | Position |
|---|---|
| Personal settings on your device | Not processed by us at all; never transmitted. |
| Reader votes | Our position is that what we receive is anonymous information outside the scope of the GDPR (Recital 26). **If, contrary to that position, any element is personal data, we do not have a fallback lawful basis identified and the feature would need redesign** — see Section 16.3. |
| Website analytics (GA4) | Consent, via the notice and opt-out on the site. |
| Serving app content | Delivering the content you requested. |

We deliberately do **not** claim consent as a safety net for votes. Article 7(1) requires a
controller to be able to *demonstrate* consent, which would mean recording an identifier
against each vote — destroying the anonymity the design depends on. Consent and anonymity
pull in opposite directions here, and we chose anonymity.

We do not rely on legitimate interests for anything relating to votes; Article 9 offers no
legitimate-interests route in any event.

---

## 7. Website analytics

The website billtracking.org uses Google Analytics 4, with a notice and an opt-out available
on the site. This is separate from the app.

**Whether the mobile app contains any analytics, crash-reporting or attribution SDK is not
confirmed in this draft and must not be guessed at — see [Section 16.5](#16-open-questions-for-the-owner).
This section cannot be finalised until it is answered.**

---

## 8. Server logs and technical data

**[OPEN — see Section 16.3. This is the single most important unresolved section of this
draft and it must be completed with verified facts.]**

Any request over the internet carries an IP address. Under
[*Breyer*, C-582/14](https://gdprhub.eu/index.php?title=CJEU_-_C-582/14_-_Breyer) an IP
address can be personal data in the hands of a service operator. "No user ID and no device
ID" therefore does not, by itself, make a submission anonymous — the anonymity has to be
engineered at the receiving end.

Before publication we must state truthfully, for the vote endpoint and every layer in front
of it (hosting provider, CDN, reverse proxy, serverless platform):

- whether IP addresses are logged;
- if so, for how long they are retained;
- whether any log line could be joined to a stored vote by timestamp.

If IP addresses are logged alongside vote timing, **the anonymity claim in Sections 1, 4
and 5 is not currently true and must be removed or rewritten.**

---

## 9. Who we share data with

We do not sell personal data. We do not share personal data. We do not use personal data for
targeted advertising, and we run no advertising of any kind.

Our only revenue is X (Twitter) creator monetization arising from public posts. No personal
data is exchanged with X as part of that. **[Counsel/owner to confirm — Section 16.6.]**

Recipients of data, other than the infrastructure providers that host the service, are:
**[TO COMPLETE — hosting provider, CDN, and, for the website only, Google (GA4)]**.

---

## 10. International transfers

**[OPEN — to complete once hosting arrangements are confirmed.]** State where the servers
receiving votes are located, and for any transfer of personal data out of the EEA, the
Article 46 safeguard relied on or the adequacy decision that applies. If the votes are
anonymous information, no transfer of personal data occurs by that route — but website
analytics and any app SDK must be addressed separately.

---

## 11. Retention

| Data | Retention |
|---|---|
| Device-only settings | Held on your device for as long as you keep the app; deleted when you uninstall or clear app data. We hold no copy. |
| Vote records | **[TO COMPLETE]** — retained indefinitely as anonymous aggregate input, or for a stated period. Owner decision required. |
| Server logs | **[TO COMPLETE — see Section 8.]** |
| Website analytics | Per the GA4 retention setting configured on the property: **[TO COMFIRM]**. |

---

## 12. Your rights

If you are in the EU/EEA or the UK, you have the rights of access, rectification, erasure,
restriction of processing, objection, and data portability, and the right to withdraw
consent where processing is based on consent, as set out in
[Articles 12–22 GDPR](https://gdpr-info.eu/art-13-gdpr/).

How they apply here:

- **For your device-only settings:** there is nothing for us to act on. You already have
  complete access, correction and deletion — through the app's own settings and by
  uninstalling.
- **For your votes:** we cannot act on these requests, because we cannot identify which
  votes are yours. This is Article 11 GDPR territory: where the controller can no longer
  identify the data subject, the rights of access, rectification, erasure, restriction and
  portability do not apply unless you provide additional information enabling identification
  — and in this case no such information exists, because none was ever created. We would
  rather tell you this plainly than imply a control we cannot deliver.
- **For website analytics:** use the opt-out on the site.

You have the right to lodge a complaint with a supervisory authority. In the EU, that is the
data protection authority of your country of residence, work or the alleged infringement
([list of authorities](https://www.edpb.europa.eu/about-edpb/about-edpb/members_en)). In the
UK, the Information Commissioner's Office (ico.org.uk).

**Providing any data is entirely optional.** There is no statutory or contractual
requirement to give us anything. You can read every bill, every update and every history in
the app without voting and without providing anything at all.

**There is no automated decision-making or profiling** within the meaning of Article 22. We
do not build profiles of readers.

---

## 13. California and other US state disclosures

**We do not meet the thresholds that make the CCPA/CPRA apply.** The CCPA applies to
for-profit businesses that also exceed one of three thresholds — gross annual revenue above
$26,625,000, buying/selling/sharing the personal information of 100,000+ California
consumers or households annually, or deriving 50%+ of revenue from selling or sharing
personal information
([CPPA threshold adjustment](https://cppa.ca.gov/regulations/cpi_adjustment.html)). We meet
none of them. We still tell you, voluntarily, that we do not sell or share personal
information and do not use it for targeted advertising.

**CalOPPA disclosures** ([Cal. Bus. & Prof. Code § 22575 et seq.](https://leginfo.legislature.ca.gov/faces/codes_displayText.xhtml?division=8.&chapter=22.&lawCode=BPC)),
which applies with no size threshold:

- *Categories of personally identifiable information collected:* **[TO COMPLETE pending
  Sections 8 and 16.5.]** On our current understanding: none through the app.
- *Categories of third parties with whom it is shared:* none, other than infrastructure
  providers acting on our behalf.
- *Process for reviewing and requesting changes:* device-only settings are entirely under
  your control in the app. There is **no** review-or-change process for votes, because
  nothing links a vote to the person who cast it.
- *How we notify you of material changes:* see Section 15.
- *Do Not Track:* **[TO COMPLETE — state whether the site and app respond to DNT signals.]**
- *Effective date:* stated at the top of this policy.

**Texas:** the TDPSA has no revenue or volume threshold. Its small-business exemption
nonetheless preserves one duty — no sale of sensitive personal data without prior consent
([§ 541.107](https://tdpsa.org/section-541-107-requirements-for-small-businesses/)). We sell
nothing, so this is satisfied. **[Counsel to confirm SBA small-business classification.]**

**Washington My Health My Data Act:** votes are political opinions, not consumer health
data, and carry no identifier linking them to a consumer. We do not believe the Act applies.
**[Counsel to confirm — the private right of action makes this asymmetric.]**

---

## 14. Children

BillTracking is a general-audience service about legislative procedure, aimed at law
professors, their students and interested readers. It is **not directed to children under
13**, we do not market it to them, and we do not knowingly collect personal information from
them. With no accounts and no age collection, we hold no age data and have no realistic
means of acquiring actual knowledge of a child user
([COPPA Rule, 16 C.F.R. Part 312](https://www.federalregister.gov/documents/2025/04/22/2025-05904/childrens-online-privacy-protection-rule)).

---

## 15. Content, accuracy and changes to this policy

**Content sources.** Bill text, status and vote records come from official sources —
Congress.gov and the EU institutions' open data (OEIL, Cellar, European Parliament). US
Government works are not subject to copyright ([17 U.S.C. § 105](https://www.law.cornell.edu/uscode/text/17/105)).

**AI-generated summaries.** Some narrative summaries are generated by AI and are always
labelled **[AI-Generated]**. Numbers and vote tallies are never AI-written. We take care with
accuracy but do not guarantee it; where we get something wrong we correct it and log the
correction. **[Cross-check the exact wording against accuracy.html and the app's accuracy
screen — these must match.]**

**Changes to this policy.** We will post the updated policy at this URL with a new effective
date. Because there are no accounts and no mailing list, we have no way to email you.
Material changes will additionally be signalled in the app. **[OWNER DECISION — see Section
16.8.]**

---

## 16. OPEN QUESTIONS FOR THE OWNER

*This section is not part of the published policy. It lists every point where the draft
above depends on a fact that the project's documented architecture does not establish. Each
must be answered — not assumed — before publication.*

**16.1 — Which legal entity is the controller, and where is it established?**
Required by Article 13(1)(a). Also determines nonprofit exemptions, the Texas SBA analysis,
and who is actually liable. YAP APP LTD or an individual? For-profit or not?

**16.2 — Is an Article 27 EU representative required?**
Falls out of 16.3 and 16.5. If nothing personal is received, arguably not. If server logs or
app analytics receive personal data, the "occasional processing" limb of the Art 27(2)(a)
exemption almost certainly fails for a continuously-running app. This is a recurring paid
engagement, so it is a cost decision as well as a legal one.

**16.3 — 🔵 THE CRITICAL ONE. What does the vote endpoint actually receive and log?**
Three sub-questions, all of which must be answered from code and provider configuration, not
from intent:
  a. Are IP addresses logged at *any* layer — application, hosting provider, CDN, reverse
     proxy, WAF, serverless platform? Many log by default with no developer action. For how
     long? Could a log line be joined to a stored vote by timestamp?
  b. What timestamp granularity is persisted with a vote — second, minute, hour, day? A
     second-precision timestamp plus a US state on a small-audience app is a far stronger
     quasi-identifier than the vote itself.
  c. Is *any* token, salted hash, session key, rate-limit key or anti-abuse fingerprint
     attached to a vote? Any of these makes the data pseudonymous and pulls the entire
     dataset back inside Article 9.
If (a) or (c) is yes, the anonymity claim in this draft is **wrong** and Sections 1, 4, 5, 6
and 12 must be rewritten before anything is published.

**16.4 — How is the country / US state derived?**
User-selected from a list, device locale, or server-side IP geolocation? If IP-derived, the
geography field sits downstream of an identifier, the anonymity analysis changes, and
Coarse/Approximate Location must be declared on both app-store forms. Several US state laws
also treat precise geolocation as sensitive.

**16.5 — Does the mobile app carry any analytics, crash-reporting or attribution SDK?**
The website's GA4 is documented; the app's position is not. This single answer determines
whether the "device-only" framing holds, whether an Article 27 representative is needed,
whether a DPIA is mandatory, what goes in the Apple App Privacy answers and the Play Data
safety form, and whether an App Tracking Transparency prompt is required. **Do not assume
either way.**

**16.6 — Does the X creator-monetization relationship involve any data flow?**
Confirm nothing beyond ordinary public posting, and that no analytics or advertising
identifiers are exchanged. The "we do not sell or share" statement in Section 9 depends on
it.

**16.7 — Is there any other off-device channel?** Contact form, feedback submission, crash
report, in-app link-out or embed. Any of these is an exception to "device-only" and must be
disclosed. The project's email setup suggests a contact form exists somewhere.

**16.8 — How will material changes be notified?** CalOPPA requires the policy to describe
the process. With no accounts and no mailing list, the mechanism is likely in-app notice plus
a revision date — but it has to be decided and built before it can be promised.

**16.9 — Is MIN_CELL=10 suppression *sticky over time* and consistent across every derived
view?**
Not a drafting point — a probable implementation bug. If suppression is evaluated
independently per query, a **differencing attack** recovers individual votes: a split hidden
at 9 voters and shown at 10 reveals the 10th person's position by subtraction, and the same
leak occurs between a national total and the sum of shown state rows. The marginal voter's
political opinion is exactly the special-category data the design exists to protect. Also
confirm whether suppression is display-only or applies to what is stored — Apple guideline
5.1.2(iii) forbids facilitating re-identification of data you have described as anonymised
or aggregated.

**16.10 — DPIA or documented negative screening?**
Article 35(3)(b) makes a DPIA mandatory for large-scale processing of special-category data.
If the anonymity claim holds, it is not triggered. Since the anonymity claim is precisely
what is uncertain, writing the assessment is the cheapest way to resolve it — and it would
surface 16.3 and 16.9 as a by-product. The EDPB's 2026 draft guidelines separately require
written, retained documentation of the anonymisation process *including testing*, which the
project does not currently have. One document can satisfy both needs.

**16.11 — App-store consistency.** The published policy, the Apple App Privacy answers, the
`PrivacyInfo.xcprivacy` privacy manifest, and the Google Play Data safety form must all be
drafted from the same source of truth. Inconsistency between them is a common rejection
cause. Note that AsyncStorage is backed by NSUserDefaults, a required-reason API, so a
privacy manifest is required even for this deliberately minimal app.

**16.12 — Apple 5.1.1(ii) consent at vote time.** Apple requires consent for collection of
usage data "even if such data is considered to be anonymous", so the anonymous design does
not remove the obligation. Recommend an explicit pre-vote disclosure at the moment of
tapping: what is sent, that it cannot be withdrawn or edited, that it is not tied to you.
One well-drafted disclosure covers this and the GDPR position at once.

**16.13 — Google's AI-content policy.** Apps that generate content using AI are required to
provide in-app reporting/flagging (policy set in force since 15 April 2026). The
[AI-Generated] summaries likely trigger this. Needs a build decision and a triage process —
it dovetails with the existing public-correction-log commitment.

**16.14 — Are votes ever exported or shared in bulk with researchers?**
The audience is law professors, so this is plausible. It would change the "shared" answers on
the Play form and needs its own treatment in Section 9.

**16.15 — Is TLS confirmed for every vote submission and content fetch, with no plaintext
fallback?** Google's Data safety form asks directly. Verify in code, do not assume.

**16.16 — Retention periods** for votes, server logs and GA4 (Section 11) are unset.

**16.17 — Should the project respond to the EDPB consultation** on draft Guidelines 02/2026,
open until 30 October 2026? Not required. But the guidelines govern the project's central
legal claim and are still in draft — counsel should re-check the final text before launch
regardless.

---

*Ends. Draft prepared 2026-07-19 for counsel review. Not legal advice.*
