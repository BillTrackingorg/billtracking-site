---
# Canonical source for the Privacy page. Edit here, then run
# `python ../app/site-build/generate_legal.py` (from the site repo) to regenerate BOTH privacy.html (this site)
# and the app's in-app Privacy screen. Grammar: legal/LEGAL-SPEC.md
slug: privacy
title: Data collection and retention
eyebrow: Privacy
htmlTitle: Privacy
description: What BillTracking collects, why, and how to delete it. No analytics, trackers or visitor logs anywhere, and anything a page keeps stays on your device. An account allows one vote per person on each bill and keeps your followed bills and settings the same across your devices.
ogTitle: Privacy
ogDescription: A live, source-linked record of lawmaking
updated: 31 October 2026
---

In short: **this website has no analytics or trackers of any kind, and we receive no visitor logs.** Anything a page keeps for you, such as the filter you set on a feed page or your sign-in session, stays in your browser on your device. You don't need an account to read anything in the app. An account does three things. It allows one vote per person on each bill. It keeps your followed bills and docket keywords the same on every device you sign in on. And it keeps your settings the same on every device. You can delete it in two taps, in the app or on your account page on this website.

>! **What exists today.** The two X feeds, this website and its feed pages ([/us](/us) and [/eu](/eu)) are live, and you can vote on this website with Google sign-in. The BillTracking app is not in the app stores yet. Apple sign-in works in the app on iPhone and on this website.

^billtracking.org
## The website

This site has no analytics on any page. There is no Google Analytics, no Cloudflare, no pixel, no tag manager, no advertising and no tracking SDK of any kind. We don't record what you read in the feed or on bill pages, what you search for, or where you came from. We don't sell or share anything about you, and we don't build a profile of you.

Some pages keep things for you on purpose, mostly the feed pages ([/us](/us) and [/eu](/eu)). A page may keep the posts it has already shown you (so it opens quickly next time), the filter you set on a feed page, and your sign-in session if you sign in. Anything a page keeps stays **in your browser on your device**, and none of it is sent to us. The one exception is a location you set before your first vote: it waits in your browser until you vote, and is then saved to your account. We are not told which pages you opened, what you read, or where you came from. The only things this website ever sends from your device are a vote you choose to cast and, if you sign in, the bills you follow, your docket keywords, your settings and what you do in your notifications list. These are described below.

One caveat: the site is hosted on **GitHub Pages**, and every web host has to handle your IP address at the network level to send you a page. GitHub does not show us those logs and we have never seen them. But we can't say that no IP address is processed anywhere, because that would not be true.

^No account needed
## Reading in the app

The feed and bill timelines work without signing in. The app and this website both load the published record as static files from GitHub Pages, which also hosts this site. Reading the feed and bill pages, and searching, sends nothing back to us. When you are signed in, your saved filters, display settings and docket keywords are kept with your account, so the app and this website show you the same set-up. When you are signed out, nothing is kept about you. You need an account to follow a bill. Your follow list is kept with your account, so the app and this website show you the same bills. It is only a list of bills, and deleting your account deletes it.

**Notifications.** If you have an account, we keep your notifications for 30 days so you can see them wherever you sign in. We also store which ones you have read, when you last opened the list, and when you last turned on a notification setting or a legislature. A notification you delete is gone for good. Your notifications are not backed up, and they are deleted with your account.

**Push notifications.** If you allow push notifications, we keep your phone's push address with your account, along with the type of phone, its time zone and when it was added. Pushes go through Expo and Apple or Google to reach your phone. We keep a delivery receipt for up to two days. Turning push off, signing out on that phone or deleting your account removes the address. On Android, Google's push service registers the app when it first opens, even if you never allow push.

The app contains no advertising, no third-party analytics and no tracking SDKs.

The app also checks for updates when it starts. The request goes to Expo, the service that delivers our updates, and carries a random identifier for the installation and the app's version. It identifies the installation, not you. If the app failed to start the last time it ran, the request also carries a shortened copy of the app's own crash message, so we can spot a broken release.

^If you sign in
## Accounts and votes

You can vote for or against a bill. A reader's position on a bill is **a political opinion**, which EU law treats as a specially protected category of personal data, so we keep this deliberately narrow.

- **You need to sign in with Google or Apple to vote. You never need to sign in to read.** The account is what allows one vote per person on each bill. Without it, the counts would mean nothing.
- **From the sign-in, the only things we act on are an account identifier and an email address.** If you use Sign in with Apple and choose *Hide My Email*, we only see Apple's relay address.
- **A vote record is made up of the bill, whether you voted for or against, when you voted, and a country (and for the US, a state) only if you choose to set one.** The location is optional, you choose it yourself, and nobody checks it. Leaving it unset is a normal way to use the app, and everything still works.
- **We never publish who voted which way, show it to anyone, or attach it to a profile.** There are no public profiles and no public vote histories. Your own votes are shown only to you, on the Your votes page in the app and on this website, where you can change or withdraw any of them. What we publish is counts: how many voted each way overall, and how many from each country or state.
- **You can change or withdraw a vote at any time, or withdraw all your votes at once.** Deleting your account deletes every vote with it.

### What vote counts show

Counts are exact. We never round, estimate or randomise them, because the point of this project is that its numbers can be checked. Every place we show also shows **how many people voted there**, so a small number looks small instead of being dressed up as a percentage.

> We can't promise that nobody could ever guess how you voted. If a bill is very one-sided, or very few people from your country have voted on it, someone who already knows you voted could make a reasonable guess. **That is true of any published total**, and no threshold removes it. What we can say is this: we never publish, show or share which way any person voted, setting a location is optional, and you can withdraw a vote or delete your account entirely.

### Where it's stored and why

Votes are held in a database in **Frankfurt, Germany**, which we chose so that this data does not leave the EU. The legal basis is your **explicit consent** (GDPR Article 9(2)(a)), which you give by choosing to vote after being told what a vote records. Withdrawing that consent and deleting your account are the same action, so there is never a time when you have withdrawn consent and we still hold your votes.

Our database provider is Supabase, which acts as a processor on our instructions. If you sign in with Apple, we also store a token from Apple. We use it for one purpose only: to disconnect BillTracking from your Apple ID when you delete your account, as Apple requires.

^Your data
## Deleting your account

In the app, go to **You → Delete account**. On this website, use your [account page](https://billtracking.org/account). Deletion is immediate and permanent. Your account, every vote you cast and your follow list are erased; there is no recovery window. Your docket keywords, saved settings and notifications are deleted too. We keep no working copy.

Our encrypted backups hold votes, consent records, follow lists, when you last opened your notifications, docket keywords and saved settings. We only read them to recover from a failure. Deleting your account removes all of it from the live database at once. In the backups, it is put beyond use, and it disappears as old copies are replaced. We keep every snapshot from the last 90 days and never fewer than two, so deleted data is normally gone from the backups within 90 days. During a very quiet spell, the second-oldest snapshot can be kept a while longer.

When votes leave with a deleted account, we record how many left each bill, from which place, and how many were for and against. This count contains nothing that identifies a person. It lets a bill's history show that votes left, rather than suggesting that people changed their minds.

If you can no longer sign in to the app or this website, use the [account deletion page](delete-account.html).

Counts that were already published, in a post or in a file someone downloaded, are not rewritten afterwards. They were true when published and contain nothing that points to you. Your vote is removed from our database and from every count made after that.

^Other details
## Everything else

- **Email.** [contact@billtracking.org](mailto:contact@billtracking.org) and [accuracy@billtracking.org](mailto:accuracy@billtracking.org) both go to one ordinary mailbox. If you write to us, we keep your message and your address for as long as we need to deal with it. Please don't send anything sensitive.
- **Legislators.** The feeds republish the official legislative record, which names Members of Congress and MEPs and records how they voted and what they sponsored. This is public record, and we republish it on the basis of a legitimate interest in making the legislative process something people can follow.
- **We sell nothing and share nothing.** We have no advertisers, sponsors, data brokers or "partners", and no revenue.
- **Children.** The app is not directed at children and we do not knowingly collect anything from them.
- **AI.** Nothing in a post is written by AI. The dates, vote tallies, bill numbers and procedural facts in a post's own lines are copied from the official record. When a post has a summary, it is the legislature's own official summary, quoted word for word.

### Your rights

If you are in the EU or UK, you have the right to access, correct, erase, restrict or object to our processing of your personal data, and to receive it in a portable form. **You also have the right to object at any time to processing based on legitimate interests.** For votes, the quickest way to do all of this is the app or your account page on this website. Both let you see and withdraw your votes (all at once if you want) and delete your account.

Otherwise, write to [contact@billtracking.org](mailto:contact@billtracking.org). We will respond within one month. If we refuse a request, we will tell you why, and you can complain to your national data protection authority or go to court.

### Who we are

BillTracking is an independent project run by one person, not a company. The data controller is Thomas Vanhoutte, who can be reached at [contact@billtracking.org](mailto:contact@billtracking.org). A postal address is available on request.

### Changes

If we change how any of this works, we will update this page and change the date below. We will not quietly start collecting something this page says we do not collect.

**31 October 2026.** This page is reworded in plainer language, with new headings. Nothing about what is collected or how it is handled changed. Three descriptions were corrected. The what-exists-today note no longer says the app is in closed testing, which ended in September. Votes are described as for or against instead of thumbs up or down, which the app does not use. And the page now says that a location you set on this website before your first vote waits in your browser until you vote, and is then saved to your account.

**23 October 2026.** The AI line now says that nothing in a post is written by AI: summaries are the legislatures' own, quoted word for word. Nothing about what is collected or how it is handled changed.

**22 October 2026.** The AI line now says what is true of summaries: they may repeat figures and dates from their source. Nothing about what is collected or how it is handled changed.

**15 October 2026.** Our backups are encrypted now. The weekly copy is locked before it is stored, with a key that only we hold and that is kept outside the service storing the copy. The deletion sentence in the app and on this website says "encrypted backups" again, as it did before 29 September, because it is true now.

**8 October 2026.** Your votes have a page of their own now, in the app and on this website, listing every vote you have cast with the same controls to change or withdraw any of them, and a button that withdraws all of them at once, there and on the [delete some of your data](delete-data.html) page. The sentence above that said there are no vote histories now says there are no public ones. Nothing new is collected.

**8 October 2026.** Added that on Android, Google's push service registers the app when it first opens.

**7 October 2026.** We now keep your notifications with your account for 30 days. We have kept when you last opened your notifications since August, and this page now says so. This page now also says what we keep if you allow push notifications.

**29 September 2026.** Our backups now also hold docket keywords and saved settings, on the same 90-day rotation as the rest. The account deletion screens in the app and on this website still called the backups encrypted, which our backup process does not do. That word is gone there too.

**20 September 2026.** Your saved feed filters, display choices and docket keywords are now kept with your account when you are signed in, alongside your notification settings and legislatures, and are deleted with it. Following a bill now needs an account in the app, as it always did on this website. Signed out, none of it reaches us.

**9 September 2026.** Your notification settings and your choice of legislatures became part of your account rather than of one device, so that setting them in the app sets them on this website too, and the other way round. Two sentences here had to change with that: an account was described as doing “exactly two things”, and this website was described as sending nothing but a vote and the bills you follow. Both were meant as complete lists and both had stopped being complete. (The 23 August entry below records this page dropping a mention of notification settings because the app did not ship them yet; this is the same page following the product the other way.) Nothing new is collected about you — settings that already existed on your device are now kept with your account instead, and they are deleted with it. Signed out, none of it leaves your device at all.

**7 September 2026.** The deletion section now says what we keep when votes leave with a deleted account: a count of how many left each bill, from which place, and how many were for and against. It is a count and nothing else — no account, no name, no time finer than the day — and it is there so that a bill's published history can show that votes left, instead of leaving a fall to be read as people changing their minds. Nothing about the erasure itself changed: your account and every vote you cast still go immediately and completely.

**5 September 2026.** Sign in with Apple went live in the app on iPhone. Nothing new is collected by it beyond what this page already describes: an account identifier and an email address (Apple's relay address if you hide yours), and one token from Apple kept for a single purpose — to disconnect BillTracking from your Apple ID when you delete your account, as the deletion section says. Later the same day, Sign in with Apple went live on this website too — the same account, the same token, the same disconnect at deletion.

**26 August 2026.** The bullet above about signing in used to open "We ask for no profile. No name, no photo". That was not accurate and it has been removed, along with the list of things it went on to say we do not ask for. Nothing about what the product does changed and nothing new is collected — what changed is that this page no longer says something untrue, and says less. Later the same day, three more descriptions were corrected to match the product exactly: the update check's request also carries the previous run's crash message when there was one — it always did, and the page now says so; the deletion section describes the backups as they are — they hold the votes, the consent records and the follow lists, on a 90-day rotation that never keeps fewer than two snapshots, and a word about encryption that the pipeline does not support is gone; and the list of what a feed page keeps on your device now includes your docket keywords. As before, nothing about what the product does changed — the page stopped saying three things inexactly.

**23 August 2026.** Voting, with Google sign-in, went live on this website, and the what-exists-today note now says so. The note's Apple sentence was also corrected: the button is live and answers when pressed, not "visibly switched off". The deletion section states the backup reality: we keep no working copy, and deleted data ages out of encrypted disaster-recovery backups within 90 days. The app's update check is also disclosed — it has worked this way since over-the-air updates were wired in; what changed is that we wrote it down. And we dropped a mention of notification settings, which the app does not ship yet.

**22 August 2026.** The "Who we are" section now names the data controller, Thomas Vanhoutte. Nothing about what is collected or how it is handled changed.

**20 August 2026.** If you sign in, the bills you follow are now kept with your account so they follow you across devices, and the website can show you new actions on them. Signed out, nothing changed: follows stay on your device and are not transmitted to us.

**19 August 2026.** Signing in, voting and deleting an account are built into this website as well as the app, and switch on when sign-in is enabled — this page now covers them. Nothing new is collected, and nothing that was kept on your device moved off it.
