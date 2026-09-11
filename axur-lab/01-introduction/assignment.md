---
slug: introduction
id: o2fpouyb9kwu
type: challenge
title: Your First Shift
teaser: You are the new external threat analyst. A tenant, a login and four assets
  under watch are waiting for you.
notes:
- type: text
  contents: |-
    # Your first shift starts in a few minutes

    Somewhere on the internet, right now, someone is registering a domain that looks almost like the
    brand you are about to protect. Someone else is pasting a list of stolen passwords into a forum.
    A fake profile is choosing a logo.

    You are the new external threat analyst. Your job is to see all of that before it reaches a
    customer. Axur is the platform you will do it with.
- type: text
  contents: |-
    # What is happening while you wait

    Behind this screen, your workplace is being built:

    - A **private Axur tenant** is being created, named after this session. It is yours alone.
    - Your **analyst account** is being registered on it, with manager rights.
    - Four assets are being placed **under watch**: the brand, the corporate domain, a key vendor and an executive.
    - The setup then reads everything back from Axur and checks it before letting you in.

    It takes about three minutes. When the lab opens, your credentials will be on the first page and
    the Axur Portal will be one tab away.
- type: text
  contents: |-
    # The day ahead

    You will work one shift, hour by hour:

    - **Morning:** learn what you protect, teach Axur your language, cut the noise and put the bots to work.
    - **Midday:** the board lights up. Fake profiles, lookalike domains, the one call the lab checks, and a
      leaked password that leads back to an infected laptop.
    - **Afternoon:** the dark web, the person at the top, your attack surface, what the internet sees, and a
      supplier whose problems are about to become yours.
    - **End of shift:** four short debrief questions. Each one is a situation you will meet again.

    Nothing you do here affects anyone else, so be curious.
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
- Four assets were placed **under watch**, so Axur's engines were already working before you signed in.
- The setup read all of it back from Axur and checked it against what this lab expects. If you are reading
  this, the checks passed.

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

Your predecessor left four things under monitoring. You will meet them in **Day One on the Desk**, but here
is the briefing.

**The brand: Netflix.** For this exercise your company's brand is Netflix, registered in Axur as the asset
**Demo Netflix, Inc**, the same name Axur uses in its own demo tenant. It was chosen because it is one of the
most impersonated brands on the internet, so there is always something to find. Axur is watching it for
**phishing** pages that copy the login screen, **lookalike domains** that trade on the name, **fake social
media profiles** and **fraudulent brand use** in ads and pages. Within minutes of the asset going live, usually before you finish reading this page, its collectors surface several
hundred of them, most with a working login form. When one needs to go, the first notification can go out in under four minutes, and most takedowns run
without a human touching them.

**The domain: example.com.** This is the corporate domain. Axur is watching leak markets, paste sites and
info-stealer logs for **employee credentials** and **customer credentials** tied to it, and public code
repositories for **secrets** committed by mistake.

**The vendor: Microsoft.** Your company depends on it, so its problems become your problems. Axur's
**Supply Chain Intel** keeps a living report on the vendor: bulletins, breaches, leaked credentials and dark
web mentions, so you hear about them before the incident report does.

**The executive: Alex Rivera.** Not every target is a logo. Alex is registered in **Executives & VIPs** so you
can see how a person is protected: fake profiles, leaked personal data, exposed credentials and cards. For
an executive, findings begin once their name variations and a photo are on file, which is done in the portal.

One more thing on the desk: among the real findings in Brand Protection there is a single sample ticket,
placed there for one exercise. The guide points it out when you get there.

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

***

## Key takeaways
===

____

Three things worth remembering from this page, whether you run a security team or a managed service:

- **Onboarding is an API call.** Your tenant, your analyst account, four assets and their monitoring were
  created and verified by script in about three minutes. No tickets, no waiting for a console. For a service
  provider that means one customer, one tenant, one run.
- **The watch starts immediately.** Nothing was imported. From the moment the brand was registered, Axur's
  collectors started comparing the internet against it, and the first findings are usually waiting before
  your first login.
- **Four assets cover the whole outside.** A brand, a domain, a vendor and a person cover the threats that
  never touch your network: fraud against your customers, leaked passwords, supplier incidents and attacks on
  the people at the top.

When you are ready, clock in. The next challenge is **Day One on the Desk**.
