---
slug: overtime
id: it5hl75fkmab
type: challenge
title: Overtime (Optional)
teaser: Optional. Tune libraries, rules and bots, listen in the dark web, protect
  an executive, read the threat landscape and queue your attack surface.
notes:
- type: text
  contents: |-
    # Overtime is optional

    The shift is over and the one decision the lab checks is behind you. What follows is the rest of the desk:
    the tuning tools, the deep and dark web, the executive, threat intelligence and your attack surface.

    Short on time? Press **Next** when the page opens and go straight to the debrief.
tabs:
- id: aq3facmfkawm
  title: Axur Portal
  type: browser
  hostname: axur
difficulty: ""
timelimit: 0
enhanced_loading: null
---
Overtime
===

The queue is handled and the shift is over. Overtime is optional, and everything in it is real in your tenant.
It holds the tools that make tomorrow's shift easier, and the parts of the desk you did not reach today.

**Short on time?** Press **Next** now and go straight to the debrief. Your tenant stays exactly as you left it.

The screens in this chapter come from Axur's demo tenant, **Infoblox Sales**, like the ones on the desk. Where
a screen shows something a fresh tenant does not have yet, the text says so.

***

## 18:00  Teach the system your language
===

____

**The situation.** Attackers never spell the brand the way marketing does. "Netflx", "netflix-billing",
"NetflixPremium": the variations are where the fraud lives.

**Axur's edge.** **Keyword libraries** hold those variations and feed the search bots, so tuning this list is
the cheapest way to raise detection and cut false positives at the same time.

**Steps**

1. Navigate to Settings > Monitoring Settings and, under Searches, open **Keyword libraries**. Axur already created an empty library for **Demo Netflix, Inc**
2. Open it with the Edit icon, or click **Add Library** and call your own **Netflix variations**. Give it the terms an impersonator would use: netflix, netflx, net-flix, netflix-premium, netflix billing
3. Save. Every term becomes a search the bots will run, so more terms mean more collections and tickets, and fewer terms mean fewer
![Jul-13-2026_at_14.35.19-image.png](../assets/Jul-13-2026_at_14.35.19-image.png)

The screen shows the edit form on a demo library called **Keywords for Youtube**. Yours works the same way.

**What to notice**

1. How keywords and keyword lists drive search bot queries
2. Why keyword quality decides monitoring relevance and the false positive rate

***

## 18:30  Cut the noise
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

## 19:00  Put the bots to work
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

## 19:30  Listening in the dark
===

____

**The situation.** With the queue handled, you go where the conversations happen: forums, marketplaces and closed chat
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

## 20:00  The name on the door
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

## 20:30  Beyond your perimeter
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

## 21:00  What the internet sees
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

## 21:30  Lights out
===

____

You tuned what Axur listens for, put the bots to work, listened to the underground, put a person under
protection, read the threat landscape and queued your attack surface. Tomorrow's shift starts with less noise
and more coverage.

***

## Key takeaways
===

____

Five more things to carry back:

- **Signal over noise.** Libraries, rules and automations mean you decide the policy once and the platform
  applies it to every new finding. Analysts read what matters.
- **Deep and Dark Web.** Forums, marketplaces and closed chat groups searched for you. You read the
  conversation without going in.
- **Executive protection.** Attackers target people, not logos. One VIP asset covers fake profiles, exposed
  documents and reused passwords for the names that matter.
- **Threat Intelligence.** Campaigns, actors and exploited products in context, so a vulnerability in
  something you run is known to you before it is news.
- **Attack surface.** From one seed, Axur maps what you expose to the internet the way an attacker doing
  reconnaissance would see it.

Next comes the debrief: four short questions about the calls you made on the desk, with the answers and the
reasoning behind them after the last one.

Your tenant is suspended automatically when this lab ends.
