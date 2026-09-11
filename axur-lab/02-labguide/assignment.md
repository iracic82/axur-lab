---
slug: labguide
id: uxm0jprdba1f
type: challenge
title: Day One on the Desk
teaser: Work a full shift as the analyst. Tune the monitoring, triage what lights
  up, chase leaked passwords, listen in the dark, and protect the people at the top.
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

Your badge works, your tenant is live, and three assets have been under watch since before you logged in.
What follows is one shift, told hour by hour. Every chapter is a place in the Axur portal, a thing an analyst
does there, and a decision you get to make. Take your time, click around, and remember that nothing you do
here can affect anyone else.

***

## 08:00  Know what you protect
===

____

Every alert Axur will ever raise for you traces back to an **asset**: the brand, the domain, the vendor.
An asset that is well described, with its official website, its name variations, its languages and its
logos, gives the detection engines something precise to compare the internet against. A vague asset produces
noise. Start the day by reading the file on the brand you are responsible for.

**Steps**

1. Open the **Axur Portal** tab and sign in to Axur ONE
2. Navigate to Settings > Monitoring Settings
![Screenshot%202026-07-13%20at%202.25.19%E2%80%AFPM.png](../assets/Screenshot%202026-07-13%20at%202.25.19%E2%80%AFPM.png)
3. Select Asset Management
4. Open the **Netflix** brand asset (in the demo environment it is called Demo Netflix)
5. Review the visible metadata, the monitoring attached to it, and any linked coverage areas
![Jul-13-2026_at_14.27.38-image.png](../assets/Jul-13-2026_at_14.27.38-image.png)

**What to notice**

1. Which fields describe the asset (website, country, language, logos)
2. How a well defined asset improves detection and cuts false positives
3. Which threat types are enabled under Brand Protection. Yours starts with phishing and lookalike domains
4. Whether **Takedown Authorization** is configured. With it, the Takedown action becomes available on applicable tickets, and Axur can act on your behalf

***

## 08:30  Teach the system your language
===

____

Attackers rarely spell the brand the way marketing does. **Keyword libraries** hold the variations, typos and
slogans that the search bots look for, so the quality of this list decides what the bots bring back.

**Steps**

1. On the same page, open the **Keyword libraries** option
2. Review an existing brand-related library by clicking its Edit icon (for example "Brand abuse related to Netflix")
![Jul-13-2026_at_14.35.19-image.png](../assets/Jul-13-2026_at_14.35.19-image.png)

**What to notice**

1. How keywords and keyword lists drive search bot queries
2. Why keyword quality decides monitoring relevance and the false positive rate

***

## 09:00  Cut the noise
===

____

An analyst who reads everything reads nothing. **Filtering rules** narrow what reaches the queue by threat
type, source, asset or other attributes, so the first ticket you open is worth opening.

**Steps**

1. On the same page, open **Filtering rules**
2. Review the filters that already exist
3. From the drop-down select Detection type **Deep and Dark Web** and Asset name **Netflix**
![Jul-13-2026_at_14.42.36-image.png](../assets/Jul-13-2026_at_14.42.36-image.png)
4. Observe how a rule refines visible findings by threat type, source, asset, or other attributes
![Jul-13-2026_at_14.43.12-image.png](../assets/Jul-13-2026_at_14.43.12-image.png)

**Your call**

Which filters would help most for:

- fake social profiles
- fraudulent brand use

***

## 09:30  Put the bots to work
===

____

You cannot search the internet by hand. **Search bots** do it on a schedule, combining an asset, a keyword
library and a set of sources, and turn what they find into detections.

**Steps**

1. Navigate to **Search Bots** under Searches and open one of the available bots
2. For the Netflix case, open the bot configured for fake accounts on Facebook
3. Review the bot configuration and its outputs

The page defines:

- which asset it applies to
- which keyword library it uses
- what it searches for
![Jul-13-2026_at_14.40.31-image.png](../assets/Jul-13-2026_at_14.40.31-image.png)

***

## 10:00  The board lights up
===

____

Mid-morning, and **Brand Protection** has findings. This is the workspace where impersonation, phishing,
fraudulent websites and fake profiles land as **tickets**. Every ticket moves through a lifecycle. It starts as
new, can be parked in **quarantine** while you investigate, escalated as an **incident**, **discarded** as a
false positive, or sent for **takedown** when authorization allows. Your job this hour is to make those calls.

#### A fake profile wearing your logo

**Steps**

1. Navigate to Workspaces > Brand Protection
![Jul-13-2026_at_14.46.30-image.png](../assets/Jul-13-2026_at_14.46.30-image.png)
2. Filter by Ticket Type and select **Fake social media profile**
3. Open a sample ticket, such as the "Netflix Golden" example
4. Review the profile details, the logo similarity, the risk level assigned by Axur AI and the attributes on the ticket
![Jul-13-2026_at_14.46.56-image.png](../assets/Jul-13-2026_at_14.46.56-image.png)

**Your call**

- Quarantine it, escalate it as an incident, discard it as a false positive, or send it for takedown once authorization is confirmed

#### An incident of fraudulent brand use

**Steps**

1. Navigate to the **Incidents** tab
2. Open a ticket of type Fraudulent brand use
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

1. Navigate to the **Quarantine** tab
2. Open the similar domain findings
3. Review how domain lookalikes are presented
![Jul-13-2026_at_14.53.07-image.png](../assets/Jul-13-2026_at_14.53.07-image.png)
4. Look for signals such as branding overlap, impersonation patterns, hosting behavior, or campaign context

#### The ones that are already closed

**Steps**

1. Navigate to the **Closed** tickets tab
2. Filter the ticket type to Phishing
3. Open a phishing example tied to the Netflix asset
4. Review the timeline, the evidence, the disposition and the final resolution
![Screenshot%202026-08-13%20at%2010.58.33%E2%80%AFPM.png](../assets/Screenshot%202026-08-13%20at%2010.58.33%E2%80%AFPM.png)

**What to notice**

- How the original detection was investigated and validated
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
2. Select the phishing ticket for the Netflix asset
3. Observe how completed takedowns are documented
![Jul-13-2026_at_15.10.22-image.png](../assets/Jul-13-2026_at_15.10.22-image.png)
4. Note what "solved" means operationally
![Jul-13-2026_at_15.10.42-image.png](../assets/Jul-13-2026_at_15.10.42-image.png)

**Your call**

- Which evidence or actions led to closure

***

## 11:30  Someone is selling your passwords
===

____

Your second asset is the corporate domain, example.com, and the **Data Leakage** workspace is where its
troubles surface: credentials in combolists, records scraped from breached sites, and passwords stolen straight
from infected laptops by info-stealer malware. Employee leaks and customer leaks are different problems, so
Axur keeps them apart.

**Steps**

1. Navigate to Workspaces > Data Leakage
![Jul-13-2026_at_15.12.59-image.png](../assets/Jul-13-2026_at_15.12.59-image.png)
2. Open the credentials tab (if not already open)
3. Notice that the filter is set to status New or In treatment
4. Click Leak Format and select **Table Format** (structured credential records with fields such as username or email, password, and URL)
5. Select the **Employee** radio button to see leaked employee credentials
6. Select the **Customer** radio button to see customer credentials captured on sites related to the asset
![Jul-13-2026_at_15.13.56-image.png](../assets/Jul-13-2026_at_15.13.56-image.png)
7. Open a record to see the details of the leak
8. Walk through what is available:

- the source of the exposure
- the group or community where it was found
- the file name
- the username, URL and other metadata
![Jul-13-2026_at_15.14.22-image.png](../assets/Jul-13-2026_at_15.14.22-image.png)
9. Set the leak format to **Stealer Log** and open one of the users in the list
10. Review the infected machine context, the original file or package, the malware details and the related evidence
![Screenshot%202026-08-14%20at%2011.42.45%E2%80%AFAM.png](../assets/Screenshot%202026-08-14%20at%2011.42.45%E2%80%AFAM.png)

**Your call**

- Which of these leaks would you escalate first, and who in the company needs to know today

***

## 13:00  Listening in the dark
===

____

After lunch you go where the conversations happen. The **Deep and Dark Web** workspace collects brand
mentions, leaked data, illicit discussions and other intelligence from forums, markets and messaging channels.
The skill here is separating a real threat from chatter.

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

Not every target is a brand. Executives and public figures are impersonated, doxxed and phished because one
compromised leader is worth more to an attacker than a thousand users. The **Executives & VIPs** workspace
watches for fake profiles, targeted threats and exposed personal information.

**Steps**

1. Navigate to Workspace > Executives & VIPs
2. Set the Asset filter to Patrick Mahomes and the Ticket Type filter to Personal Information leak
![Screenshot%202026-08-14%20at%2012.36.06%E2%80%AFPM.png](../assets/Screenshot%202026-08-14%20at%2012.36.06%E2%80%AFPM.png)
3. Open and review one of the open tickets tied to the executive
![Screenshot%202026-08-14%20at%2012.39.01%E2%80%AFPM.png](../assets/Screenshot%202026-08-14%20at%2012.39.01%E2%80%AFPM.png)
4. Review the recommended actions to understand the next steps that mitigate the threat
![Screenshot%202026-08-14%20at%2012.40.59%E2%80%AFPM.png](../assets/Screenshot%202026-08-14%20at%2012.40.59%E2%80%AFPM.png)

***

## 15:00  Beyond your perimeter
===

____

**Cyber Threat Intel** aggregates and analyzes intelligence sources and turns them into contextual insights
and bulletins: vulnerabilities, threat actors, campaigns and indicators of compromise. It serves the analyst
in an investigation and the executive who needs a one-page picture of the threat landscape.
![Screenshot%202026-08-17%20at%201.54.14%E2%80%AFPM.png](../assets/Screenshot%202026-08-17%20at%201.54.14%E2%80%AFPM.png)

**Monitoring rules**

You can create monitoring rules based on technologies, malware, threat actors, geography, industry and risk
level, so the intelligence that reaches you is the intelligence that applies to you. For example, threats
aimed at a specific location in a specific industry:
![Screenshot%202026-08-17%20at%201.58.45%E2%80%AFPM.png](../assets/Screenshot%202026-08-17%20at%201.58.45%E2%80%AFPM.png)

***

## 15:30  What the internet sees
===

____

**External Attack Surface Management** maps your company the way an attacker would: hosts, IPs, technology
stack, open ports, certificates, and the exposures that come with them.

**Steps**

1. Navigate to Workspace > External attack surface management (EASM)
2. The home page summarizes the assets being monitored and the ones affected
3. Select a monitored asset to review its hosts, IPs, technology stack and open port entries
4. The same section lists the exposures associated with the selected asset for further investigation
![Screenshot%202026-08-17%20at%202.07.09%E2%80%AFPM.png](../assets/Screenshot%202026-08-17%20at%202.07.09%E2%80%AFPM.png)

***

## 16:00  Your vendor's problem is your problem
===

____

Your third asset is not yours at all. Microsoft is a vendor, and **Supply Chain Intel** exists because a
breach, a leaked corporate credential or a critical bulletin at a supplier becomes your incident the moment
you depend on them. Axur keeps a vendor profile with its exposure, its threat landscape and its history, so
you hear about it before the incident report does.

**Steps**

1. Navigate to the Supply Chain Intel area and open the **Microsoft** vendor
2. Read the overview: the vendor's main domain, corporate name and last update
3. Browse the sections Axur maintains for a vendor: dark web mentions, corporate credentials, external attack surface, threat landscape and indicators
4. Open the history and look for critical bulletins

**Your call**

- Which of these would you raise with the team that owns the Microsoft relationship, and how urgently

***

## 17:00  End of shift
===

____

In one day you tuned what Axur listens for, triaged what it found, followed a leaked password back to an
infected laptop, listened to the underground, protected a person rather than a logo, mapped your own attack
surface and checked on a supplier. That is the external half of the picture.

Axur helps Infoblox move earlier in the attack lifecycle by identifying and disrupting external threats before
they reach users. Combined with Infoblox protection at the DNS layer, it gives organizations a stronger and
more preemptive way to reduce digital risk.

Your tenant is suspended automatically when this lab ends. Nothing else is required of you.
