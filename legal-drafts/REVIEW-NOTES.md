# REVIEW NOTES — adversarial read of the two legal drafts

**Reviewed:** `PRIVACY-POLICY-DRAFT.md` and `TERMS-OF-SERVICE-DRAFT.md`, both dated 2026-07-19.
**Reviewer brief:** find claims the project cannot back. Not a general edit pass.
**Status:** these notes are not legal advice either. They are a defect list for the owner and
for counsel.

**Overall:** the drafts are unusually honest for this genre. They flag their own gaps rather
than papering over them, they refuse to pick a governing law, and they explicitly decline to
use consent as a fallback for votes. The defects below are real, but they are defects in a
sound document, not a rewrite.

**Verdict: NEEDS WORK.** Nothing here is fraudulent. But there are four things that would be
false on the day of publication, and one of them (item 1) is a structural trap in how the
privacy policy is assembled.

---

## BLOCKING — would be untrue or unsupportable if published today

### 1. The privacy policy's caveats all live in a section that is not published

`PRIVACY-POLICY-DRAFT.md` §16 opens with: *"This section is not part of the published
policy."* Meanwhile §8 says the anonymity claim is unverified, and §16.3 says that if IP
addresses are logged at any layer, *"the anonymity claim in this draft is wrong."*

But §1 (the plain-English summary — the part almost everyone actually reads) states without
qualification:

- "the vote is sent to us anonymously. It carries no user identifier and no device identifier"
- "**Uninstalling the app deletes everything we hold about you locally**, because everything
  we hold about you is local"

The second one is a claim that the project holds *nothing* server-side about a reader. That
is not established. §8 says server logging is unknown. §16.7 says a contact form may exist.
So the summary asserts as settled precisely what the rest of the document says is unresolved.

Delete §16 to publish — which is what §16 tells you to do — and every hedge disappears while
every confident claim survives. That is the worst possible failure mode, and it happens by
following the draft's own instructions.

**Fix:** adopt the Terms draft's pattern instead. The ToS keeps its open questions **inline
as blockquotes** next to the text they qualify, so a caveat cannot be separated from its
claim. Move each §16 item next to the section it governs. Additionally, rewrite §1 so it
promises only what §8 has confirmed — or hold §1 back until §16.3 is answered.

### 2. GA4 lawful basis is stated as "consent" but the described mechanism is opt-out

§6 lists the lawful basis for website analytics as **"Consent, via the notice and opt-out on
the site."** §7 repeats: GA4 runs "with a notice and an opt-out."

An opt-out is not consent. Article 5(3) of the ePrivacy Directive requires **prior** consent
for storing or reading information on a user's device, and analytics cookies are not covered
by the strictly-necessary exemption in most Member States. The EDPB's Guidelines 2/2023 on
the technical scope of Art 5(3) widened this further, to pixels, URL tracking and
fingerprinting. Consent under GDPR Art 4(11) must be a freely given, specific, informed,
unambiguous **affirmative action** — a pre-set banner the user can later switch off is not
that.

This matters more than the vote analysis does, because **GA4 is the only confirmed
personal-data flow in the entire project.** Everything else is either device-only or
asserted-anonymous. The one processing that is definitely happening, definitely involves
personal data (client ID, IP), and definitely involves a third-party US recipient gets three
sentences and a wrong lawful basis.

**Fix:** either (a) change the site to a genuine prior-consent banner and keep "consent" as
the basis, or (b) describe the mechanism accurately and let counsel deal with the exposure.
Do not describe an opt-out as consent. §7 also needs the Art 13 detail it currently lacks:
what GA4 collects, Google's role, the transfer mechanism to the US, and the retention
setting (§11 still says `[TO COMFIRM]` — note also the typo).

Sources: [EDPB Guidelines 2/2023 on Art 5(3) ePrivacy](https://www.edpb.europa.eu/system/files/2024-10/edpb_guidelines_202302_technical_scope_art_53_eprivacydirective_v2_en_0.pdf) ·
[Art 5(3) ePrivacy Directive](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=celex%3A32002L0058)

### 3. "We do not share personal data" is contradicted inside its own section

§9 opens: *"We do not sell personal data. We do not share personal data."* Four lines later
the same section lists recipients: infrastructure providers, and Google for GA4.

GA4 transmits IP address and client identifier to Google. That is a disclosure of personal
data to a third party, whatever its legal characterisation. The flat opener is not true as
written. Note also that "share" has a specific defined meaning under the CCPA
(cross-context behavioural advertising) which is *narrower* than the ordinary reading — so
the sentence is simultaneously too broad in plain English and doing unintended work in
Californian.

**Fix:** "We do not sell personal data and we do not use it for advertising. We do disclose
data to the providers listed below, who process it on our behalf." Then list them.

### 4. Both documents promise operational things that may not exist

Two specific promises, each stated as fact in one document and flagged as unverified in the
other:

- `PRIVACY-POLICY-DRAFT.md` §15: *"where we get something wrong we correct it and log the
  correction."* Asserted as an existing practice. `TERMS-OF-SERVICE-DRAFT.md` §4's open
  question asks whether the public correction log is even live and at what URL.
- `TERMS-OF-SERVICE-DRAFT.md` §5: *"you can report it and we will review it."* The open
  question in the same section says the in-app reporting affordance is an unmade build
  decision, and does not know who triages.

The ToS §4 open question specifically warns against publishing responsiveness promises the
project cannot keep, citing FTC Act §5. Then §5 makes one, twelve lines later.

There is also a house precedent here: the app and site already softened *"every report is
read"* for exactly this reason while keeping the public-log commitment. These two sentences
walk it back.

**Fix:** neither sentence ships until the log URL and the reporting channel exist. Describe
the mechanism that is actually built, in the present tense, or say nothing.

---

## IMPORTANT — capability, scope and mandatory-content gaps

### 5. The Terms claim an anti-manipulation power the architecture removes

ToS §6: *"We may withhold, correct or remove vote results that we reasonably believe have
been manipulated."*

With no identifier of any kind on a vote, the project cannot detect manipulation, cannot
attribute it, and cannot excise the affected votes. The only real remedies are blunt: pull a
whole bill's results, or reset a whole dataset. The sentence as written implies targeted
removal, which is exactly the capability §6 spends the preceding paragraphs explaining does
not exist.

Note the trap: building the detection capability that would make this sentence true is the
very thing the §6 open question warns destroys the anonymity claim.

**Fix:** state the actual remedy — "we may withhold or reset the published results for a
bill where we believe the totals have been distorted" — and drop the implication of
per-vote action.

### 6. Asserting ownership of the AI-generated summaries

ToS §8 lists "the AI-generated summaries as published by us" among the material the project
claims as its own and forbids copying.

Purely AI-generated text without meaningful human authorship is generally not copyrightable
in the US, and the position elsewhere is unsettled at best. Claiming exclusive rights over
material that is probably in the public domain is a claim the project cannot back — and it
is a slightly awkward one for a project whose §8 opens by explaining that government works
are not copyrightable and that it asserts no rights over them.

**Fix:** keep the selection-and-arrangement claim, which is defensible. Drop or heavily
qualify the claim over the AI summaries themselves. Counsel to advise on whether human
editing of summaries changes this.

### 7. The EU AI Act is not mentioned in either document — and it bites in two weeks

Article 50(4) of the AI Act requires deployers who use AI to generate or manipulate text
**published with the purpose of informing the public on matters of public interest** to
disclose that the text is artificially generated. That is a near-verbatim description of
[AI-Generated] summaries of pending legislation.

Article 50 obligations apply from **2 August 2026** — roughly two weeks after this draft
date. Neither document names the AI Act.

The good news: the existing [AI-Generated] label very likely satisfies the deployer
disclosure obligation already. This is a documentation gap more than a compliance one. But
counsel should confirm, and the drafts should cite the obligation rather than leave the
labelling looking like a purely voluntary courtesy. Note separately that the Art 50(2)
machine-readable marking duty falls on the *provider* of the model, not on BillTracking as
deployer — do not over-comply into a claim you cannot keep.

Sources: [Art 50 AI Act](https://artificialintelligenceact.eu/article/50/) ·
[Commission guidance on marking AI-generated content](https://digital-strategy.ec.europa.eu/en/policies/code-practice-ai-generated-content)

### 8. The Digital Services Act is not mentioned either

An EU-facing service that publishes content and displays reader-submitted aggregates has DSA
exposure. Articles 11 and 12 require a single point of contact for authorities and for
users. Article 14 requires terms and conditions to set out content-moderation and
restriction policies in clear language. Small and micro enterprises are exempt from the
heavier Section 3 obligations, but not from these.

The ToS acceptable-use list in §6 is most of an Art 14 policy already. It needs a stated
process and a contact point to become one.

**Fix:** counsel to determine whether the Service is a hosting service or an online platform
under the DSA, and add the contact points. This interacts with §16 (Contact) of the ToS,
which is currently empty.

### 9. There is no security section anywhere, and no encryption-in-transit statement

Neither document addresses GDPR Art 32 (security of processing). The privacy policy has no
security section at all.

This is also a store-form gap: Google Play's Data safety form asks directly whether data is
encrypted in transit. §16.15 correctly flags that TLS must be verified in code rather than
assumed — but there is nowhere in the policy for the answer to go once it is verified.

### 10. Google Play's data-deletion questions must be answered even with no accounts

§16.11 covers the Apple App Privacy answers, the privacy manifest and the Play Data safety
form. It does not cover Play's **Data deletion** questions, which are a separate mandatory
part of the Data safety form and have been fully enforced since April 2024.

An app with no account creation is outside the *account*-deletion requirement — but the form
still has to be completed, and the honest answer here is unusual: personal data is
device-only, and votes cannot be deleted because they cannot be identified. That answer is
defensible but it needs drafting before a reviewer sees it cold.

Source: [Play account deletion requirements](https://support.google.com/googleplay/android-developer/answer/13327111?hl=en)

### 11. The Article 11 argument undercuts the anonymity argument

The policy runs two incompatible positions at once. §5 and §6 say the primary position is
that vote data **is not personal data at all** (Recital 26 anonymity). Then §4.3 and §12
invoke **Article 11 GDPR** — a provision that only makes sense *if the data is personal data*
and the controller merely cannot identify the subject.

Pleading Art 11 is an implicit concession that Recital 26 anonymity does not hold. A
regulator will read it that way. The draft does flag "[Counsel to confirm the Article 11
framing]", so this is not an unflagged error — but the flag understates it. This is not a
wording question; it is a choice between two mutually exclusive legal theories.

**Fix:** pick the primary position, state it, and put the other in the alternative
explicitly ("and in any event, if contrary to our position…"), which is how a lawyer would
plead it.

### 12. The small-cell protection is promised in the published text and doubted in the unpublished text

§4.4 tells readers suppression exists "to prevent a published tally exposing the opinions of
a handful of identifiable people." §16.9 says the mechanism probably has a differencing
hole — a split hidden at 9 voters and shown at 10 reveals the tenth person by subtraction,
and national totals minus shown state rows leak the same way.

§4.4 already carries a genuinely good caveat about k-anonymity not being a guarantee, with a
real citation. But that caveat is about inference attacks in general. It does not tell the
reader that the specific mechanism may not be implemented soundly.

§16.9 is correct that this is an implementation bug, not a drafting point. **It should be
fixed in code before either document is published**, because the fix is cheap (evaluate
suppression once, stickily, across every derived view) and the alternative is publishing a
protective claim about a mechanism you suspect is leaky. Apple's guideline 5.1.2(iii) is the
sharp end of that.

### 13. A draft EDPB guideline is described as "the applicable framework"

§5 says: *"The applicable framework is the EDPB's draft Guidelines 02/2026 on
Anonymisation."* The same bullet then correctly notes they are in draft and open for
consultation until 30 October 2026.

Draft guidelines are not the applicable framework. They are not law even when final —
guidelines are interpretive. The applicable framework is Art 4(1), Recital 26 and the case
law; the guidelines inform how a regulator will read them.

**Fix:** "the EDPB's draft Guidelines 02/2026 indicate how regulators are likely to
approach this." Note also that this citation and the 2026 guidelines generally are the one
part of the draft I could not independently verify — counsel should check the document
exists in the form cited and re-check the final text before launch.

### 14. "Non-commercial" is used as a legal self-classification

Both documents describe the Service as "non-commercial" while also stating that it earns
revenue from X creator monetization. Those are in tension, and the word is doing legal work
in at least four places:

- CalOPPA applies to operators of **commercial** websites and online services. PP §13 asserts
  CalOPPA applies "with no size threshold" without addressing whether the Service is
  commercial — arguing both sides in one section.
- CCPA's "for-profit business" analysis (§13).
- Trader/consumer status under Rome I and Brussels I — ToS §14 correctly treats users as
  consumers, which implies the operator is a trader, which sits badly with "non-commercial".
- EU institutional reuse terms and Congress.gov guidance, which sometimes distinguish
  commercial reuse (ToS §8 open question).

**Fix:** stop asserting the conclusion and state the facts: no ads, no sponsors, no paid
placements, no subscriptions, nothing sold; revenue is X creator monetization on public
posts. Let counsel classify.

### 15. Rights listed in §12 that do not attach to anything

§12 recites access, rectification, erasure, restriction, **objection** and **portability**.
Portability (Art 20) only applies to processing based on consent or contract and carried out
by automated means. Objection (Art 21) applies to processing based on Art 6(1)(e) or (f).
On the draft's own account, no processing rests on any of those bases.

Reciting the full statutory list and then explaining that none of it applies is standard
practice and not wrong. But it sits oddly in a document whose stated ethic is not implying
controls it cannot deliver.

---

## MINOR

16. **§11 typo:** `[TO COMFIRM]` → `[TO CONFIRM]`.
17. **§12 citation:** "Articles 12–22 GDPR" links to `art-13-gdpr`. Link the range or cite
    the specific articles.
18. **§4.1 presents a closed list.** It enumerates three things the app sends, then §4.2
    reinforces the closure with "what is *not* sent". §16.3(b) admits a timestamp is probably
    persisted. A timestamp is a transmitted field — list it, with granularity marked open,
    rather than leaving it implied by an open question about granularity.
19. **ToS §7 + §15 incorporate the privacy policy into the contract** ("forms part of these
    terms", plus the whole-agreement clause). Generally better to keep a GDPR transparency
    notice *outside* the contract — it muddies the Art 6(1)(b) analysis and turns a notice
    you must be able to update unilaterally into a term you may not be able to.
20. **No UK representative counterpart.** §12 promises UK rights and names the ICO. §2 deals
    with the EU Art 27 representative but there is no equivalent treatment of the UK GDPR
    Art 27 duty. Same analysis, second jurisdiction.
21. **Children: COPPA only.** §14 handles COPPA. Nothing addresses GDPR Art 8 (which sets the
    digital-consent age between 13 and 16 depending on Member State), the UK Age Appropriate
    Design Code (which applies to services *likely to be accessed by* children, a lower bar
    than "directed to"), or the child-safety declarations both stores now require. Risk is
    genuinely low for a legislative-procedure app aimed at law students — but the store forms
    demand answers regardless.
22. **EDPS v SRB is cited only on the limb that hurts.** §5 cites C-413/23 P for the
    proposition that identifiability is assessed at collection and from the controller's
    perspective. That is accurate — it is the transparency-obligation limb of the judgment.
    But the case's headline holding is contextual and cuts the *other* way: the Court held
    that sufficiently pseudonymised data may be personal to the sender and not personal to a
    recipient who cannot re-identify. Citing only the unhelpful limb is admirably honest, and
    I would not change it — but counsel should know the case also contains the better
    argument.
    [C-413/23 P](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=celex:62023CJ0413)
23. **ToS §1 is browsewrap.** "By using the Service you accept these terms" with no
    affirmative acceptance step is the weakest form of online contracting in US courts. The
    §14 open question notes that enforceability depends on presentation; that observation
    belongs against §1 too.

---

## What the drafts get right, and should not be "improved" away

Worth saying explicitly, because a later editing pass may be tempted to smooth these out:

- **Refusing consent as a fallback for votes** (§6) is the correct call and the reasoning is
  right: demonstrable consent under Art 7(1) requires an identifier, which destroys the
  anonymity the design depends on.
- **§4.3, "what we cannot do and why"** is the best writing in either document. It states
  four capability losses plainly instead of hiding them. Keep it.
- **The k-anonymity caveat in §4.4**, with a real citation, refusing to present suppression
  as a guarantee.
- **§14 of the ToS refusing to pick a governing law**, and explaining exactly why the choice
  is contested, rather than reflexively naming a jurisdiction that would not survive Rome I
  against EU consumers.
- **The US-law note in §5** — declining to claim that US law treats a vote as sensitive when
  it does not.

---

## Suggested order of work

1. **Answer §16.3** (IP logging at every layer, timestamp granularity, any token on a vote).
   Nothing else can be finalised first — items 1, 3 and 11 all resolve differently depending
   on the answer.
2. **Answer §16.5** (any SDK in the app). Second-largest branch point.
3. **Fix the suppression implementation** (item 12) before publishing a claim about it.
4. **Restructure the privacy policy** so caveats sit inline, ToS-style (item 1).
5. **Fix the GA4 consent mechanism or the GA4 description** (item 2).
6. Strip the two unbackable operational promises (item 4).
7. Then hand to counsel with the remaining open questions attached.

---

*Prepared 2026-07-19 as an adversarial review of the two drafts. Not legal advice. The legal
sources cited above were checked against current published material where the date allowed;
the 2026 EDPB anonymisation guidelines cited in the privacy policy could not be
independently verified in this review and should be checked by counsel.*
