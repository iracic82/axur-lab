# UI validation checklist (human tester)

Everything below is what the API **cannot** confirm and therefore has not been verified yet: it needs a person
playing the lab through the invite as a participant. What the API does confirm on every run (tenant, login,
assets, seed, sample ticket, detections) is checked automatically by `validate_tenant.py` in the setup log.

Invite: https://play.instruqt.com/infoblox/invite/qmefrgcrtv8f  ·  Tick each line, note the deviation if any.

## Loading and challenge 1, Your First Shift
- [ ] The three loading notes show while the sandbox builds (about 3 minutes).
- [ ] Step 1 shows tenant name, username and password (not empty).
- [ ] The **Axur Portal** tab opens one.axur.com and the credentials log in **without** a 2FA prompt or a forced password change.
- [ ] After login the tenant shown is the participant's own (name = sandbox id), not IE2L.

## Challenge 2, Day One on the Desk (menu paths and screenshots)
- [ ] 08:00  Settings > Monitoring Settings > Asset Management lists Demo Netflix, Inc, example.com, Microsoft, Alex Rivera; the brand asset shows monitoring phishing, similar domains, fake social media profiles and fraudulent brand use. Screenshots 1 and 2 still match the current UI.
- [ ] 09:00  Brand Protection shows hundreds of tickets. Search ticket = `golden` finds the sample with reference facebook.com/netflix.golden.lab.sample (the **Netflix Golden** profile; the Fake social media profile filter alone lists 1,000+ real profiles); it has a snapshot and AI fields. Quarantine / Incident / Discard actions exist. Takedown is NOT offered on the sample.
- [ ] 09:00  After moving the sample ticket, the **Check** button passes within a few seconds. Before moving it, Check fails with the hint text.
- [ ] 09:00  Similar domain name tickets sit in Open (none auto-quarantined); Send to Quarantine works on one. Closed tickets appear after 15 to 20 minutes. Screenshots 7 to 13 match.
- [ ] 11:00  Data Leakage: Add filter > Leak format > Combolist returns thousands of example.com records; Stealer log returns none (expected, captioned as demo). Screenshots 14 to 17 match.
- [ ] 14:00  Supply Chain Intel shows Microsoft with the tabs Overview, Threat Landscape (Only critical toggle), Attack Surface, Employee/Customer Credentials, Dark Web.
- [ ] 17:00  The handover to the debrief reads well.

## Challenge 3, Overtime (optional)
- [ ] 18:00  Keyword libraries: an empty library for Demo Netflix, Inc already exists (per tester feedback 2026-09-13); editing it or adding one works. Screenshot 3 is captioned as the demo library.
- [ ] 18:30  Filtering rules: rules exist for every detection type except Deep & Dark Web; Add rule with Detection type, Brand, Source and Monitored query (the query in the text is accepted) saves. Screenshots 4 and 5 match.
- [ ] 19:00  Search bots > Add bot: the six steps in the text match the wizard (source, asset, what to search for, searches generated, title, Save bot). No monitoring warning on Demo Netflix, Inc.
- [ ] 19:30  Deep & Dark Web > Explore accepts `netflix AND (hack OR premium)` and returns results. Screenshot 18 matches.
- [ ] 20:00  Executives > Alex Rivera: "Alex James Rivera" is accepted, "Alex J. Rivera" refused, variations autosave; the similar-name option under fake social media profile exists (confirm its exact label). Screenshots 19 to 21 are labelled as demo-executive examples.
- [ ] 20:30  CTI workspace opens; monitoring rules page reachable. Screenshots 22 and 23 match.
- [ ] 21:00  EASM shows the example.com seed with 0 assets (discovery queued; measured: first cycle more than a day after seeding). Discover now shows the queued message. Screenshot 24 is captioned as the finished result.

## Debrief (challenges 4 to 7)
- [ ] Each quiz shows the question and four answers; the marked answer is accepted, others rejected.

## Clock out (challenge 8)
- [ ] The four explanations match the accepted quiz answers. "What to take home" reads well for a prospect.

## End
- [ ] Stopping the lab: within ~3 minutes the tenant shows as suspended in Tenants management (admin, after re-login).
