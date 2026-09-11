---
slug: debrief-lookalike
id: 0fws3ivdrnyw
type: quiz
title: 'Debrief 1 of 4: the domain that is not there yet'
teaser: A lookalike domain, but nothing on it. What do you do?
notes:
- type: text
  contents: |-
    # End of shift

    You tuned what Axur listens for, watched it rank the findings, followed a leaked password back to an infected
    laptop, listened to the underground, put a person under protection and checked on a supplier.

    Four short questions before you clock out. Each one is a situation you will meet again, and each has one
    answer an experienced analyst would give.
answers:
- Discard it. An empty page is a false positive, and Quarantine only clutters the queue.
- Leave it in Quarantine. Axur re-checks quarantined tickets every morning and flags any content change, so the day it becomes a phishing page you will know.
- Request a takedown now. The registrar will remove a domain that imitates a brand even before it hosts content.
- Escalate it as an Incident so the SOC starts blocking it at the firewall.
solution:
- 1
difficulty: ''
timelimit: 0
enhanced_loading: null
---
Debrief 1 of 4
===

Certificate transparency just surfaced **netflix-account-verify.com**. Axur opened a ticket and put the domain in
**Quarantine** on its own. You open it: the domain resolves, but the page is empty. No login form, no logo, nothing
to take down yet.

What is the right move, and why?
