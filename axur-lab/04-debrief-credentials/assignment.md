---
slug: debrief-credentials
id: qv6etzkyo7nh
type: quiz
title: 'Debrief 2 of 4: two leaks, one afternoon'
teaser: Which leak do you escalate first?
notes:
- type: text
  contents: |-
    # Debrief, question 2

    Two leaks landed on your desk this afternoon. Only one of them is about to become an incident.
answers:
- Record A. Employee credentials are always more dangerous than customer credentials.
- Record B. A stealer log from yesterday means active malware on a real machine and a fresh credential for your own login page, while Record A is an old, already-known leak.
- Neither. Credentials found on the dark web cannot be acted on until the user reports a problem.
- Both equally. Every credential exposure must be treated as an incident within the hour.
solution:
- 1
difficulty: ''
timelimit: 0
enhanced_loading: null
---
Debrief 2 of 4
===

Data Leakage shows two new records for example.com this afternoon:

- **Record A**: an employee's email and password in a combolist, source dated 2017, the same password appears in three older breaches.
- **Record B**: a customer's email and password in a **stealer log** collected yesterday, with the infected machine's hostname, browser and the URL of your login page.

Both are real. Which one do you escalate first?
