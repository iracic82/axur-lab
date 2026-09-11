---
slug: debrief-lookalike
type: quiz
title: 'Debrief 1 of 4: the domain that is not there yet'
teaser: A lookalike domain, but nothing on it. What do you do?
answers:
- Discard it. An empty page is a false positive, and Quarantine only clutters the queue.
- Leave it in Quarantine. Axur re-checks quarantined tickets every morning and flags any content change, so the day it becomes a phishing page you will know.
- Request a takedown now. The registrar will remove a domain that imitates a brand even before it hosts content.
- Escalate it as an Incident so the SOC starts blocking it at the firewall.
solution:
- 1
difficulty: ''
timelimit: 0
---
Debrief 1 of 4
===

Certificate transparency just surfaced **netflix-account-verify.com**. Axur opened a ticket and put the domain in
**Quarantine** on its own. You open it: the domain resolves, but the page is empty. No login form, no logo, nothing
to take down yet.

What is the right move, and why?
