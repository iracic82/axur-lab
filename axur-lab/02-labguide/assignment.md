---
slug: labguide
id: uxm0jprdba1f
type: challenge
title: Day One on the Desk
teaser: Work a full shift as the analyst. Tune the monitoring, triage what lights
  up, chase leaked passwords, listen in the dark, and protect the people at the top.
notes:
- type: text
  contents: |-
    # Clocking in

    It is 08:00. Your badge worked, your tenant is live, and while you were reading the briefing Axur's collectors
    were already busy: by now there are usually a few hundred findings waiting for the Netflix brand alone.

    This challenge is one full shift, told hour by hour. Every chapter is a place in the portal, what an analyst
    does there, and a decision that is yours.
- type: text
  contents: |-
    # One decision is checked

    At 10:00 you will meet a fake profile called **Netflix Golden**. It was placed in your tenant for this
    exercise. Quarantine it, escalate it or discard it, then press **Check**: the lab reads your tenant back from
    the Axur API and confirms the ticket has left Potential threats.

    Everything else is yours to explore. Nothing you do can affect anyone else.
tabs:
- id: 8xk2pbuykb1r
  title: Axur Portal
  type: browser
  hostname: axur
difficulty: ""
timelimit: 0
enhanced_loading: null
---
Day One on the Desk
===

Your badge works, your tenant is live, and four assets have been under watch since before you logged in:
the **Netflix** brand, the **example.com** domain, the **Microsoft** vendor and the executive **Alex Rivera**.
What follows is one shift, told hour by hour. Each chapter is a situation an analyst meets, what Axur does
about it, the clicks to see it, and a decision that is yours to make. Nothing you do here can affect anyone
else.

**About the screens in this guide.** They were taken in Axur's demo tenant, **Infoblox Sales**, where the
brand is registered as **Demo Netflix, Inc**. Your tenant uses the same asset name and the same screens. Only
the tenant name in the top bar, the ticket counts and the dates differ. Where a screen shows something that
takes time to appear in a fresh tenant, the text says so.

***

## Your badge

If the **Axur Portal** tab asks you to sign in again, or you skipped ahead, these are your credentials.
They are the same ones you picked up on the first page.

**Your Tenant Name:**
```
[[ Instruqt-Var key="AXUR_TENANT_NAME" hostname="shell" ]]
```

**Your Login Username:**
```
[[ Instruqt-Var key="AXUR_USER_EMAIL" hostname="shell" ]]
```

**Your Login Password:**
```
[[ Instruqt-Var key="AXUR_USER_PASSWORD" hostname="shell" ]]
```

***

## 08:00  Know what you protect
===

____

**The situation.** A takedown request, a phishing alert, a lookalike domain: all of it traces back to how well
the brand is described. Axur compares the internet against the asset file, so a precise file means precise
detections and a vague one means noise.

**Axur's edge.** During registration the platform assigns the brand an automatic **exposure level** from its
web traffic, which sets the right coverage. Add the official website, name variations, locales and logos and
the engines have something exact to match. Enable **Takedown Authorization** and the platform can act on your
behalf when it finds abuse.

**Steps**

1. Open the **Axur Portal** tab and sign in to Axur ONE
2. Navigate to Settings > Monitoring Settings
![Screenshot%202026-07-13%20at%202.25.19%E2%80%AFPM.png](../assets/Screenshot%202026-07-13%20at%202.25.19%E2%80%AFPM.png)
3. Select Asset Management
4. Open the **Demo Netflix, Inc** brand asset. Its brand name and variation is **Netflix**, which is what the collectors match
5. Review the visible metadata, the monitoring attached to it, and any linked coverage areas
![Jul-13-2026_at_14.27.38-image.png](../assets/Jul-13-2026_at_14.27.38-image.png)

**What to notice**

1. Which fields describe the asset (website, country, language, logos)
2. Which threat types are enabled under Brand Protection. Yours starts with phishing, lookalike domains, fake social media profiles and fraudulent brand use
3. Whether Takedown Authorization is configured. Some platforms only act on a signed authorization that carries the brand logo

***

## 08:30  Teach the system your language
===

____

**The situation.** Attackers never spell the brand the way marketing does. "Netflx", "netflix-billing",
"NetflixPremium": the variations are where the fraud lives.

**Axur's edge.** **Keyword libraries** hold those variations and feed the search bots, so tuning this list is
the cheapest way to raise detection and cut false positives at the same time.

**Steps**

1. On the same page, open **Keyword libraries**. Axur already created an empty library for **Demo Netflix, Inc**
2. Open it with the Edit icon, or click **Add Library** and call your own **Netflix variations**. Give it the terms an impersonator would use: netflix, netflx, net-flix, netflix-premium, netflix billing
3. Save. Every term becomes a search the bots will run, so more terms mean more collections and tickets, and fewer terms mean fewer
![Jul-13-2026_at_14.35.19-image.png](../assets/Jul-13-2026_at_14.35.19-image.png)

The screen shows the edit form on a demo library called **Keywords for Youtube**. Yours works the same way.

**What to notice**

1. How keywords and keyword lists drive search bot queries
2. Why keyword quality decides monitoring relevance and the false positive rate

***

## 09:00  Cut the noise
===

____

**The situation.** An analyst who reads everything reads nothing. Somewhere in the stream is the one finding
that matters today.

**Axur's edge.** **Filtering rules** narrow what reaches the queue by threat type, source, asset or other
attributes, and the platform's AI already ranks tickets by severity, marking the urgent ones with flame icons,
so what you open first is worth opening.

**Steps**

1. On the same page, open **Filtering rules**. Axur pre-built a rule for each detection type of Demo Netflix, Inc, except one: there is no rule yet for Deep and Dark Web. That one is yours to write
![Jul-13-2026_at_14.42.36-image.png](../assets/Jul-13-2026_at_14.42.36-image.png)
2. Click **Add rule**. Detection type **Deep & Dark Web**, Brand **Netflix**, Source **Forums & Markets**
3. In **Monitored query**, paste the query below. It matches the brand and its spellings in the content, the description or the address of a post
4. Read the line under the query: the average results per day this rule would have produced over the last 15 days. **Simulate in Threat Hunting** shows them before you commit. Then **Save**

```
(content=(Netflix OR "Net-flix" OR "Net_flix" OR "Net.Flix") OR description=(Netflix OR "Net-flix" OR "Net_flix" OR "Net.Flix") OR uri=(Netflix OR "Net-flix" OR "Net_flix" OR "Net.Flix"))
```

![Jul-13-2026_at_14.43.12-image.png](../assets/Jul-13-2026_at_14.43.12-image.png)

The screen shows the finished rule in the demo tenant. Yours looks the same once saved.

**Your call**

Which filters would help most for:

- fake social profiles
- fraudulent brand use

***

## 09:30  Put the bots to work
===

____

**The situation.** You cannot search the internet by hand, and the fraud does not keep office hours.

**Axur's edge.** **Search bots** run on a schedule, combining an asset, a keyword library and a set of sources,
and turn what they find into detections. On the brand's own website, a discreet **OnePixel** script goes
further and flags pages that copy the official layout the moment they load.

**Steps**

1. Under Searches, open **Search bots** and click **Add bot**
2. **Which source will this bot scan?** Choose **Facebook**. Some sources offer templates. Create this one from scratch to see every step
3. **For which asset will this bot work?** Demo Netflix, Inc
4. **What to search for?** Add the asset library **Brand name and variations** and the keyword library you just built
5. Read **Searches generated**: one search per term and target, and how often they run. Facebook bots run once a day at a random time
6. Give it a title such as **Netflix fake accounts on Facebook** and click **Save bot**. On the list, its toggle shows green

**What to notice**

- A bot is three choices: a source, an asset for the tickets, and what to search for
- This bot's first harvest lands after your shift, since Facebook bots run once a day. The fake profile tickets already in Brand Protection show what that harvest looks like
![Jul-13-2026_at_14.40.31-image.png](../assets/Jul-13-2026_at_14.40.31-image.png)

In the demo screen the asset's monitoring was switched off, hence the yellow warning. In your tenant fake social media profile monitoring is active on **Demo Netflix, Inc**, so your bot runs at its next daily slot.

***

## 10:00  The board lights up
===

____

**The situation.** Mid-morning, and **Brand Protection** has findings for Netflix. Not one or two: within
minutes of the asset going live, Axur's collectors typically surface several hundred, from cloned login pages
on free hosting to casino sites trading on the name and domains one letter away from the real one. Most of the
pages carry a working login form, and a good share ask for payment.

**Axur's edge.** Every finding is a **ticket** with a lifecycle you control. A new ticket can be parked in
**Quarantine**, where Axur re-checks it every morning and flags any change, escalated as an **Incident**,
**Discarded** as a false positive, or sent for **Takedown**. Takedowns are what Axur is known for: the first
phishing notification goes out in under four minutes, 86% of requests run fully automated from detection to
decision to notification, and the success rate is around 98%, with a stay-down guarantee. Lookalike domains
need no setup at all: smart monitoring compares new registrations and certificates against the brand and opens a
ticket for each one. Parking the empty ones in Quarantine is your move, and Axur re-checks them every morning.

![The life of a ticket in Brand Protection](../assets/diag-ticket-lifecycle.png)

#### A fake profile wearing your logo

**Steps**

1. Navigate to Workspaces > Brand Protection
![Jul-13-2026_at_14.46.30-image.png](../assets/Jul-13-2026_at_14.46.30-image.png)
2. In **Search ticket**, type **golden**. That is the fastest way to it: the Fake social media profile filter alone returns well over a thousand real profiles by now
3. Open the sample ticket whose reference is **facebook.com/netflix.golden.lab.sample**. It stands for the Netflix Golden profile in the screen below and was placed in your tenant for this exercise, so please do not request a takedown on it
4. Review the profile details, the logo similarity, the risk level assigned by Axur AI and the attributes on the ticket
![Jul-13-2026_at_14.46.56-image.png](../assets/Jul-13-2026_at_14.46.56-image.png)

**Your call**

- Quarantine it, escalate it as an incident, or discard it as a false positive. This is the one decision the
  lab checks: when you press **Check**, the lab reads your tenant back from the Axur API and confirms the
  sample ticket has left Potential threats. Takedown is not offered on this sample, and please leave it that way

#### An incident of fraudulent brand use

**Steps**

1. Filter by Ticket Type and select **Fraudulent brand use**. In your tenant these sit in the **Open** tab until you escalate one. The demo screen shows the **Incidents** tab after that
2. Open one ticket. If the filter comes back empty, the collectors have not reached that source yet, so take a phishing ticket instead
![Jul-13-2026_at_14.50.44-image.png](../assets/Jul-13-2026_at_14.50.44-image.png)
3. Review the evidence and the current status
4. Walk through the possible actions:

- request a takedown
- move it to quarantine
- if it looks like a false positive, discard it

**Your call**

- Investigate one ticket and decide its next action

#### Lookalike domains in quarantine

**Steps**

1. In the **Open** tab, filter Ticket Type = **Similar domain name**
2. Open a few. Most resolve to an empty page or a parked domain, which is what a phishing page looks like the week before it goes live
3. Review how domain lookalikes are presented
![Jul-13-2026_at_14.53.07-image.png](../assets/Jul-13-2026_at_14.53.07-image.png)
4. Look for signals such as branding overlap, impersonation patterns, hosting behavior, or campaign context

**What to notice**

- These were found without anyone's help. Send an empty one to **Quarantine**: Axur re-checks quarantined tickets every morning at 06:00 and flags the ticket the day content appears. The demo screen shows one already parked there

#### The ones that are already closed

**Steps**

1. Navigate to the **Closed** tickets tab
2. Filter the ticket type to Phishing
3. Open a ticket tied to the Demo Netflix, Inc asset. The first closed tickets appear 15 to 20 minutes into your shift, once the AI has revisited today's findings. If the tab is still empty, carry on and come back
4. Review the timeline, the evidence, the disposition and the final resolution
![Screenshot%202026-08-13%20at%2010.58.33%E2%80%AFPM.png](../assets/Screenshot%202026-08-13%20at%2010.58.33%E2%80%AFPM.png)

**What to notice**

- Closed tickets carry one of four outcomes: Discarded, Resolved, Unresolved or Interrupted
- Which evidence and workflow actions led to the resolution
- How a closed ticket tells a customer the story of visibility, analyst judgement and measurable remediation

#### Discarded tickets

**Steps**

1. From the Resolution drop-down select **Discarded**
2. Typical reasons for a discard:

- the ad is no longer available
- the content is no longer visible to users
- the AI revisited the content, found it inactive, and discarded it automatically

#### Takedown as the resolution

**Steps**

1. From the Treatment drop-down select **Takedown**
2. Select a phishing ticket for the Demo Netflix, Inc asset. Nothing in your tenant has been sent for takedown yet, so this view fills only after you request one. The screens below show a finished takedown from the demo tenant, and the events history that got it there
3. Observe how completed takedowns are documented
![Jul-13-2026_at_15.10.22-image.png](../assets/Jul-13-2026_at_15.10.22-image.png)
4. Note what "solved" means operationally
![Jul-13-2026_at_15.10.42-image.png](../assets/Jul-13-2026_at_15.10.42-image.png)

**Your call**

- Which evidence or actions led to closure. The more evidence on a ticket, from screenshots to HTML, the higher the odds of removal

***

## 11:30  Someone is selling your passwords
===

____

**The situation.** Your second asset is the corporate domain, example.com. Somewhere a combolist carries an
employee's password, and somewhere a laptop infected with an info-stealer has been quietly uploading every
saved login, including the one to your VPN.

**Axur's edge.** **Data Leakage** separates what a business must treat differently: **employee credentials**,
which are a route into your systems, and **customer credentials**, which are account takeover waiting to
happen. Stealer logs come with the infected machine's context, so you can tell an old breach from active
malware. Secrets committed to public code are caught as well.

**Steps**

1. Navigate to Workspaces > Data Leakage and open the **Credentials** tab
![Jul-13-2026_at_15.12.59-image.png](../assets/Jul-13-2026_at_15.12.59-image.png)
2. The filter already applied is Status **New** or **In treatment**. Click **Add filter**, choose **Leak format** and select **Combolist**: the bulk of what leaks about example.com, thousands of records within minutes of the asset going live
3. Select the **Employees** radio button for leaked employee credentials, then **Customers** for customer credentials captured on sites related to the domain
![Jul-13-2026_at_15.13.56-image.png](../assets/Jul-13-2026_at_15.13.56-image.png)
4. Open a record and walk through what is there: the source and the forum or community where it was found, the leak's name and description, the file it came from, the username, the password type and the URL it grants access to
![Jul-13-2026_at_15.14.22-image.png](../assets/Jul-13-2026_at_15.14.22-image.png)
5. The other leak format is **Stealer log**. example.com is a documentation domain, no real laptop is logged into it, so a fresh tenant has no stealer logs for it. The record below comes from the demo tenant: the infected machine's file path, the browser profile and the source package, which is what turns a leaked password into an infected computer you can find
![Screenshot%202026-08-14%20at%2011.42.45%E2%80%AFAM.png](../assets/Screenshot%202026-08-14%20at%2011.42.45%E2%80%AFAM.png)

**Your call**

- Which of these leaks would you escalate first, and who in the company needs to know today

***

## 13:00  Listening in the dark
===

____

**The situation.** After lunch you go where the conversations happen: forums, marketplaces and closed chat
groups where Netflix accounts are traded and "premium" hacks are advertised.

**Axur's edge.** The **Deep and Dark Web** workspace monitors more than three thousand channels, from restricted
forums and onion sites to WhatsApp, Telegram and Discord groups. **Explore** lets you search all of it with
exact phrases and operators, and a relevant result becomes a ticket with one click.

**Steps**

1. Navigate to Workspace > Deep and Dark Web
2. Open the **Explore** page
3. Add the search filter `netflix AND (hack OR premium)`
![Jul-13-2026_at_15.16.53-image.png](../assets/Jul-13-2026_at_15.16.53-image.png)
4. Select one of the filtered messages
5. Review the finding and decide what makes a result relevant or irrelevant
6. Decide whether it deserves to become a ticket

***

## 14:00  The name on the door
===

____

**The situation.** Not every target is a brand. One compromised executive is worth more to an attacker than a
thousand users: a fake profile in their name, a leaked document number, a password reused from a breach. Your
company has just asked you to put its new CEO, **Alex Rivera**, under protection.

**Axur's edge.** **Executives & VIPs** watches for personal information leaks, credential and card exposure and
fake profiles, using facial recognition to spot image abuse across the major social platforms. Executive data
is stored encrypted, and each detection comes with recommended next steps. Protection is only as good as the
profile you give it, and that profile is your job in this chapter.

**Steps**

1. Navigate to Settings > Monitoring Settings > Assets > **Executives** and open **Alex Rivera**
2. Under **Full name and variations**, add the spellings an impersonator might use, for example **Alex James Rivera** and **Alexandra Rivera**. The form only accepts names of two or more words and refuses initials with a dot, so "Alex J. Rivera" is rejected. Each variation saves as you add it
3. Under the fake social media profile detection, switch on the option that catches profiles with a **similar name**. Axur calls it name similarity inspection: profiles whose name is 80% or more similar to a registered name are caught even without a photo
4. Note the remaining fields: a **face photo** for facial recognition, and the emails, phone numbers, documents and cards whose leaks should raise a ticket. A real onboarding fills these in, or sends the executive a **SafeShare** form to fill in themselves
5. There is no Save button, the profile saves as you go. Open Workspace > Executives & VIPs: this is where Alex's findings will land once the profile is complete and the collectors have run

**What findings look like.** The screens below come from Axur's demo executive, Patrick Mahomes, a public figure
with a complete profile. This is what lands in the workspace once collection runs: the executive filter, a
personal-information-leak ticket, and the recommended actions on it.
![Screenshot%202026-08-14%20at%2012.36.06%E2%80%AFPM.png](../assets/Screenshot%202026-08-14%20at%2012.36.06%E2%80%AFPM.png)
![Screenshot%202026-08-14%20at%2012.39.01%E2%80%AFPM.png](../assets/Screenshot%202026-08-14%20at%2012.39.01%E2%80%AFPM.png)
![Screenshot%202026-08-14%20at%2012.40.59%E2%80%AFPM.png](../assets/Screenshot%202026-08-14%20at%2012.40.59%E2%80%AFPM.png)

**Your call**

- Which three fields on Alex's profile would you insist the real CEO fills in first, and why

***

## 15:00  Beyond your perimeter
===

____

**The situation.** A new campaign is exploiting a product you run. You would like to know before it is news.

**Axur's edge.** **Cyber Threat Intel** aggregates intelligence sources into bulletins on vulnerabilities,
threat actors, campaigns and indicators, with a risk score that lets you triage from the top. **Monitoring
rules** turn that into alerts that apply to you: combine your technologies, industry, geography, threat actors
and risk level, then follow the rule to start receiving them.
![Screenshot%202026-08-17%20at%201.54.14%E2%80%AFPM.png](../assets/Screenshot%202026-08-17%20at%201.54.14%E2%80%AFPM.png)

**Monitoring rules**

The platform ships with default rules to copy from: threats to my technologies, threats aimed at specific
industries and locations, and specific threat actor activity. For example, threats aimed at a location in an
industry:
![Screenshot%202026-08-17%20at%201.58.45%E2%80%AFPM.png](../assets/Screenshot%202026-08-17%20at%201.58.45%E2%80%AFPM.png)

***

## 15:30  What the internet sees
===

____

**The situation.** Every attacker starts with reconnaissance. Do it first.

**Axur's edge.** **External Attack Surface Management** starts from a seed such as example.com and expands
outward through related domains, hosts, IPs, services, open ports and certificates. Each asset gets a risk
score that blends CVSS, exploitability and context such as production relevance and brand similarity, so the
list sorts itself by what to fix first.

**Steps**

1. Navigate to Workspace > External attack surface management (EASM)
2. Open **Asset management**. The seed **example.com** was registered when your tenant was built, and discovery was queued at the same time. Axur runs discovery in scheduled cycles, and in the lab tenants the first cycle took more than a day, so during this shift the home page most likely still shows 0 assets. That is the queue, not a fault
3. Click **Discover now** to see the confirmation that a run is queued. Nothing else is needed from you
4. The screen below is what discovery produces for example.com once it has run: the host, its IP, tags such as dmarc and spf, open ports, certificates, the tech stack, and the exposures found on it, each with severity, ease of exploitation and an owner
![Screenshot%202026-08-17%20at%202.07.09%E2%80%AFPM.png](../assets/Screenshot%202026-08-17%20at%202.07.09%E2%80%AFPM.png)

**What to notice**

- The two exposures in the screen are real for example.com: a DMARC misconfiguration and an expired domain, each scored on severity and effort
- If your session runs long enough for discovery to complete, the same view appears in your tenant with no further setup

***

## 16:00  Your vendor's problem is your problem
===

____

**The situation.** Your third asset is not yours at all. Microsoft is a vendor, and a ransomware announcement
or a leaked corporate credential at a supplier becomes your incident the moment you depend on them.

**Axur's edge.** **Supply Chain Intel** keeps a living report per vendor: an AI summary of its posture,
security bulletins with the categories you care about flagged as critical, its attack surface, leaked employee
and customer credentials, and dark web mentions, each with week-over-week or month-over-month trend
indicators. A ransomware group naming a supplier often shows up here before mainstream news, and the whole
report exports to PDF for the people who need it.

**Steps**

1. Open the **Supply Chain Intel** workspace and select the **Microsoft** vendor
2. Read the **Overview**: main domain, corporate name and last update
3. Open **Threat Landscape** and read the AI summary, then filter the bulletins with **Only critical**
4. Browse **Attack Surface**, **Employee Credentials**, **Customer Credentials** and **Dark Web**, and note the trend indicators

**Your call**

- Which of these would you raise with the team that owns the Microsoft relationship, and how urgently

***

## 17:00  End of shift
===

____

In one day you tuned what Axur listens for, watched it rank the findings, sent a takedown, followed a leaked
password back to an infected laptop, listened to the underground, protected a person rather than a logo,
mapped your own attack surface and checked on a supplier. That is the external half of the picture.

Axur helps Infoblox move earlier in the attack lifecycle by identifying and disrupting external threats before
they reach users. Combined with Infoblox protection at the DNS layer, it gives organizations a stronger and
more preemptive way to reduce digital risk.

***

## Key takeaways
===

____

One shift, ten use cases. This is what to carry back to your own organisation:

- **Brand Protection.** A brand registered at 08:00 had several hundred findings by 10:00: cloned login
  pages, lookalike domains and sites trading on the name. Axur finds the fraud before your customers report it.
- **Signal over noise.** Libraries, rules and automations mean you decide the policy once and the platform
  applies it to every new finding. Analysts read what matters.
- **Takedown.** One click starts it, and Axur runs the notification chain with hosting providers, registrars
  and platforms until the content is gone. Pages that die on their own are closed by the AI, so nobody
  chases ghosts.
- **Credential exposure.** Leaked passwords arrive with their source. A 2017 combolist and yesterday's stealer
  log are different emergencies, and the stealer log tells you which machine is infected.
- **Deep and Dark Web.** Forums, marketplaces and closed chat groups searched for you. You read the
  conversation without going in.
- **Executive protection.** Attackers target people, not logos. One VIP asset covers fake profiles, exposed
  documents and reused passwords for the names that matter.
- **Threat Intelligence.** Campaigns, actors and exploited products in context, so a vulnerability in
  something you run is known to you before it is news.
- **Attack surface.** From one seed, Axur maps what you expose to the internet the way an attacker doing
  reconnaissance would see it.
- **Supply Chain Intel.** Your vendor's ransomware announcement or leaked credential is your incident. Axur
  tells you before the mainstream news does.
- **API first.** Everything this lab did to your tenant, from creation to the Check button, went through the
  public API. Provisioning, configuration and validation are scripts, which is what a managed service or a
  large security team needs.

Before you clock out, four short questions about the calls you made today. They are the debrief, and each
one is a situation you will meet again. The answers, and the reasoning behind them, wait for you after the
last question.

Your tenant is suspended automatically when this lab ends.
