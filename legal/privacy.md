---
# Canonical source for the Privacy page. Edit here, then run
# `python ../app/site-build/generate_legal.py` (from the site repo) to regenerate BOTH privacy.html (this site)
# and the app's in-app Privacy screen. Grammar: legal/LEGAL-SPEC.md
slug: privacy
title: What we hold, and how to make us stop
eyebrow: Privacy
htmlTitle: Privacy
description: What BillTracking collects, why, and how to delete it. No analytics, no trackers and no visitor logs anywhere — whatever a page keeps stays on your device. An account makes a vote count once, and keeps your followed bills across your devices.
ogTitle: Privacy — BillTracking
ogDescription: What we collect, why, and how to delete it — in plain language.
updated: 5 September 2026
---

The short version: **this website carries no analytics and no trackers of any kind, and we receive no visitor logs.** Whatever a page keeps for you — your reading preferences, and a sign-in session if you choose to vote — stays in your browser, on your device. The app needs no account to read anything. An account does exactly two things — it makes a vote count once per person, and it keeps your followed bills the same on every device you sign in on — and it can be deleted in two taps, from inside the app or from your account page on this website.

>! **What exists today.** The two X feeds, this website and its feed pages ([/us](/us) and [/eu](/eu)) are live — and voting, with Google sign-in, is live on this website. The BillTracking app is in closed testing and not yet in the app stores. Apple sign-in works in the app on iPhone; on this website, the Apple button still tells you it isn't available yet — the website's Apple flow is a separate setup we haven't finished.

^This website
## billtracking.org collects nothing from you

There is no analytics anywhere on this site. No Google Analytics, no Cloudflare, no pixel, no tag manager, no advertising and no tracking SDKs — on any page, of any kind. We do not record what you read, what you search for or where you arrived from, we do not sell or share anything about you, and we build no profile of you.

Some pages do keep things for you, deliberately — the feed pages ([/us](/us) and [/eu](/eu)) most of all. Whatever a page keeps — the posts it has already shown you, so that it opens quickly the next time, your display preferences, your docket keywords, and your sign-in session if you choose to vote — stays **in your browser, on your device**, and none of it is transmitted to us. We are not told which pages you opened, what you read, or where you arrived from. From this website, the only things that ever leave your device are a vote you deliberately cast and — if you sign in — the bills you choose to follow, exactly as described below.

One honest caveat, because the alternative would be a false claim: the site is hosted on **GitHub Pages**, and any web host necessarily handles your IP address at the network layer in order to send you a page. GitHub does not surface those logs to us and we have never seen them — but we will not tell you no IP address is processed anywhere, because that would not be true.

^The app — reading
## Reading needs no account and sends us nothing

The feed and bill timelines all work without signing in. The app and this website both fetch the published record as static files from GitHub Pages, the same infrastructure this site is hosted on; neither of them reports back what you read or what you search for. Your keywords and your display settings are stored **on your device** and are not transmitted to us. Followed bills stay on your device too, unless you sign in — then your follow list is kept with your account, so the app and this website show you the same bills. It is a list of bills, nothing more, and deleting your account deletes it.

The app contains no advertising, no third-party analytics and no tracking SDKs.

The app also checks for updates when it starts. That request carries a random identifier for the installation and the app's version — sent to Expo, the service that delivers our updates. It identifies the installation, not you. If the app failed to start the last time it ran, the request also carries the text of that error — the app's own crash message, shortened — so that a broken release can be spotted.

^The app — accounts and votes
## An account exists so your vote counts once

You can mark a bill with a thumbs up or down. Because a reader's position on a bill is **a political opinion** — a specially protected category of personal data under EU law — we are deliberately narrow about this.

- **Voting requires signing in with Google or Apple; reading never does.** The account is what makes one vote per person per bill possible. Without it, the counts would be meaningless.
- **All we act on from the sign-in is an account identifier and an email address.** If you use Sign in with Apple and choose *Hide My Email*, we only ever see Apple's relay address.
- **A vote record is: which bill, thumbs up or down, when, and — only if you choose to set it — a country and, for the US, a state.** That location is optional, you choose it yourself, and nobody verifies it. Leaving it unset is a normal and fully-supported way to use the app.
- **Who voted which way is never published, shown to anyone, or attached to a profile.** There are no public profiles and no vote histories. What is published is counts: how many voted each way overall, and how many from each country or state.
- **You can change or withdraw your vote at any time**, and deleting your account deletes every vote with it.

### What we ask you to understand about published counts

Counts are exact — we never round, estimate or randomise them, because the whole point of this project is that its numbers can be checked. Every place we show also shows **how many people voted there**, so a small number is visibly small rather than dressed up as a percentage.

> We are not going to claim that nobody could ever guess how you voted. If a bill is very one-sided, or very few people from your country have voted on it, someone who already knows you voted could make a reasonable guess. **That is true of any published total anywhere** and no threshold removes it. What we can tell you is that we never publish, display or share which way any individual voted, that setting a location is optional, and that you can withdraw a vote or delete the account entirely.

### Where it is stored, and on what legal basis

Votes are held in a database in **Frankfurt, Germany**, chosen so that this data does not leave the EU. The legal basis is your **explicit consent** (GDPR Article 9(2)(a)), given by choosing to vote after being told what a vote records. Withdrawing that consent and deleting your account are the same action — there is no state in which you have withdrawn consent and we still hold your votes.

Our database provider is Supabase, acting as a processor on our instructions. If you sign in with Apple, we also store a token from Apple used for one purpose only: to properly disconnect BillTracking from your Apple ID when you delete your account, as Apple requires.

^Deleting
## Deleting your account

In the app: **You → Delete account**. On this website: your [account page](https://billtracking.org/account). It is immediate and permanent. Your account, every vote you cast and your follow list are erased; there is no recovery window. We keep no working copy. Backups exist so that a failure cannot destroy everyone's work — they hold the votes, the consent records and the follow lists, because our database provider's free tier keeps no backups of its own — and they are only ever read to recover from a failure. Deleting your account removes all of it from the live database at once. In the backups it is put beyond use on the rotation: we keep every snapshot from the last 90 days and never fewer than two, so a deleted vote is normally gone from the archive within 90 days, and a very quiet spell can hold the second-oldest snapshot a while longer.

If you can no longer sign in in either place, use the [account deletion page](delete-account.html).

One thing we will not pretend about: counts that were already published — in a post, or in a file someone downloaded — are not retrospectively rewritten. They were true when published and they contain nothing that points to you. Your vote is removed from our database and from every count produced afterwards.

^Email, and everything else
## The rest of it

- **Email.** [contact@billtracking.org](mailto:contact@billtracking.org) and [accuracy@billtracking.org](mailto:accuracy@billtracking.org) are aliases on a single mailbox and receive mail. If you write to us, we hold your message and your address for as long as needed to deal with it. Please don't send us anything sensitive — it's an ordinary mailbox.
- **Legislators.** The feeds republish the official legislative record, which names Members of Congress and MEPs and records how they voted and what they sponsored. That is public record information, republished on the basis of legitimate interest in making the legislative process followable.
- **We sell nothing and share nothing.** No advertisers, no sponsors, no data brokers, no "partners". There is no revenue.
- **Children.** The app is not directed at children and we do not knowingly collect anything from them.
- **AI.** Plain-English bill summaries are AI-written and carry an explicit **[AI-Generated]** label. Dates, vote tallies, bill numbers and procedural facts are copied from the official record and are never AI-written.

### Your rights

If you are in the EU or UK you have the right to access, correct, erase, restrict or object to our processing of your personal data, and to receive it in a portable form. **You also have the right to object to processing based on legitimate interests, at any time.** For votes, the fastest route to all of this is the app itself, which lets you see and withdraw your votes and delete your account outright.

Otherwise, write to [contact@billtracking.org](mailto:contact@billtracking.org). We will respond within one month. If we refuse a request we will tell you why, and you can complain to your national data protection authority or go to court.

### Who we are

BillTracking is an independent project run by one person, not a company. The data controller is Thomas Vanhoutte, who can be reached at [contact@billtracking.org](mailto:contact@billtracking.org); a postal address is available on request.

### Changes

If we change how any of this works we will update this page and change the date below. We will not quietly start collecting something this page says we do not collect.

**5 September 2026.** Sign in with Apple went live in the app on iPhone. Nothing new is collected by it beyond what this page already describes: an account identifier and an email address (Apple's relay address if you hide yours), and one token from Apple kept for a single purpose — to disconnect BillTracking from your Apple ID when you delete your account, as the deletion section says. The website's Apple button is unchanged: not available yet, and it says so when pressed.

**26 August 2026.** The bullet above about signing in used to open "We ask for no profile. No name, no photo". That was not accurate and it has been removed, along with the list of things it went on to say we do not ask for. Nothing about what the product does changed and nothing new is collected — what changed is that this page no longer says something untrue, and says less. Later the same day, three more descriptions were corrected to match the product exactly: the update check's request also carries the previous run's crash message when there was one — it always did, and the page now says so; the deletion section describes the backups as they are — they hold the votes, the consent records and the follow lists, on a 90-day rotation that never keeps fewer than two snapshots, and a word about encryption that the pipeline does not support is gone; and the list of what a feed page keeps on your device now includes your docket keywords. As before, nothing about what the product does changed — the page stopped saying three things inexactly.

**23 August 2026.** Voting, with Google sign-in, went live on this website, and the what-exists-today note now says so. The note's Apple sentence was also corrected: the button is live and answers when pressed, not "visibly switched off". The deletion section states the backup reality: we keep no working copy, and deleted data ages out of encrypted disaster-recovery backups within 90 days. The app's update check is also disclosed — it has worked this way since over-the-air updates were wired in; what changed is that we wrote it down. And we dropped a mention of notification settings, which the app does not ship yet.

**22 August 2026.** The "Who we are" section now names the data controller, Thomas Vanhoutte. Nothing about what is collected or how it is handled changed.

**20 August 2026.** If you sign in, the bills you follow are now kept with your account so they follow you across devices, and the website can show you new actions on them. Signed out, nothing changed: follows stay on your device and are not transmitted to us.

**19 August 2026.** Signing in, voting and deleting an account are built into this website as well as the app, and switch on when sign-in is enabled — this page now covers them. Nothing new is collected, and nothing that was kept on your device moved off it.
