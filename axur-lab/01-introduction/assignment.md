---
slug: introduction
id: o2fpouyb9kwu
type: challenge
title: Your First Shift
teaser: You are the new external threat analyst. A tenant, a login and three assets under
  watch are waiting for you.
notes:
- type: text
  contents: |-
    # **Infoblox Axur Introductory lab**

    Your environment is being provisioned: a private Axur tenant is being created for you, your analyst
    account is being registered, and the first assets are being placed under watch. You will access it
    through the **Axur Portal** tab.

    **In this lab you will…**
    - Step into the role of an external threat analyst with a live tenant of your own.
    - See what Axur already knows about the brand, domain and vendor you are responsible for.
    - Learn how findings become tickets, and tickets become takedowns.
tabs:
- id: tg0fzhghiigb
  title: Axur Portal
  type: browser
  hostname: axur
difficulty: ""
timelimit: 0
enhanced_loading: null
---
## Your first shift
===

Welcome aboard. You have just joined the security team as its **external threat analyst**: the person who
watches what happens *outside* the firewall, where attackers register lookalike domains, clone login pages,
trade leaked passwords, and impersonate the brand on social media.

While this page was loading, a few things happened on your behalf:

- A **private Axur tenant** was created for you. It carries your session's name, nobody else can see it,
  and it is suspended automatically when the lab ends.
- An **analyst account** with manager rights was registered on that tenant. Its credentials are below.
- Three assets were placed **under watch**, so Axur's engines were already working before you signed in.

***

## Step 1: Pick up your badge
===

____

Switch to the **Axur Portal** tab and log in using the credentials below. This is your tenant and your
login. Whatever you do here stays in your sandbox.

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

## Step 2: What is already on your desk
===

____

Your predecessor left three things under monitoring. You will meet them in the Lab Guide, but here is the
briefing.

**The brand: Netflix.** For this exercise your company's brand is Netflix, chosen because it is one of the
most impersonated brands on the internet, so there is always something to find. Axur is watching it for
**phishing** pages that copy the login screen and for **lookalike domains** that trade on the name.

**The domain: example.com.** This is the corporate domain. Axur is watching the leak markets and paste sites
for **employee credentials** and **customer credentials** tied to it, and public code repositories for
**secrets** committed by mistake.

**The vendor: Microsoft.** Your company depends on it, so its problems become your problems. Axur's
**Supply Chain Intel** tracks the vendor's exposure, breaches and critical bulletins so you hear about
them before the incident report does.

Everything else in the portal, from workspaces to keyword libraries to bots, is there for you to explore.
Nothing in this tenant affects any other participant.

***

## Step 3: Your mission
===

____

By the end of the lab you should be able to:

- Navigate the Axur interface confidently across assets, monitoring brand protection, data leakage, executive protection, deep and dark web, threat hunting and CTI workflows
- Explain how Axur helps surface external threats such as brand abuse, impersonation, fraudulent domains, leaked credentials and deep/dark web exposure
- Use keyword libraries, bots, and filters to surface relevant insights
- Review ticket states and analyze possible response actions such as safelisting, escalation, quarantine, and closure
- Demonstrate how Axur supports external threat disruption and monitoring through automation and takedown-oriented workflows

***

## Step 4: Who this lab is for
===

____

- Sales engineers
- Security specialists
- Partners
- Customers in guided workshop settings

***

## Step 5: Before you start
===

____

- A browser, and the Axur Portal tab on this page
- The credentials from Step 1
- Curiosity: the tenant is yours, so click around

When you are ready, clock in. The next challenge is **Day One on the Desk**.
