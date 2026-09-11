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
- [ ] 08:00  Settings > Monitoring Settings > Asset Management lists Netflix, example.com, Microsoft, Alex Rivera; the Netflix asset shows monitoring phishing + similar domains. Screenshots 1 and 2 still match the current UI.
- [ ] 08:30  Keyword libraries page exists at that path; creating a library works as described. Screenshot 3 matches.
- [ ] 09:00  Filtering rules page: creating the Deep & Dark Web / Netflix rule works. Screenshots 4 and 5 match.
- [ ] 09:30  Search Bots under Searches: creating a bot with the library and Facebook works. Screenshot 6 matches.
- [ ] 10:00  Brand Protection shows hundreds of tickets. Filter Ticket Type = Fake social media profile shows the **Netflix Golden** sample; it has a snapshot and AI fields. Quarantine / Incident / Discard actions exist. Takedown is NOT offered on the sample.
- [ ] 10:00  After moving the sample ticket, the **Check** button passes within a few seconds. Before moving it, Check fails with the hint text.
- [ ] 10:00  Incidents, Quarantine and Closed tabs exist; Closed shows a resolution column (Discarded/Resolved/...). Screenshots 7 to 13 match.
- [ ] 11:30  Data Leakage shows credentials for example.com; Employee/Customer switch and Leak Format (Table, Stealer Log) exist. Screenshots 14 to 17 match.
- [ ] 13:00  Deep & Dark Web > Explore accepts `netflix AND (hack OR premium)` and returns results. Screenshot 18 matches.
- [ ] 14:00  Settings > Monitoring Settings > Assets > Executives shows Alex Rivera; name variations and name similarity inspection can be saved. Screenshots 19 to 21 are labelled as demo-executive examples.
- [ ] 15:00  CTI workspace opens; monitoring rules page reachable. Screenshots 22 and 23 match.
- [ ] 15:30  EASM shows the example.com seed and, after discovery ran, hosts/IPs. Note how long discovery took. Screenshot 24 matches.
- [ ] 16:00  Supply Chain Intel shows Microsoft with the tabs Overview, Threat Landscape (Only critical toggle), Attack Surface, Employee/Customer Credentials, Dark Web.
- [ ] 17:00  The handover to the debrief reads well.

## Debrief (challenges 3 to 6)
- [ ] Each quiz shows the question and four answers; the marked answer is accepted, others rejected.

## End
- [ ] Stopping the lab: within ~3 minutes the tenant shows as suspended in Tenants management (admin, after re-login).
