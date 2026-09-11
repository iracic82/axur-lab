# Axur MSSP tenant scripts (Instruqt)

Same pattern as the Infoblox CSP `sandbox_api.py` / `create_sandbox.py` / `delete_sandbox.py` trio.

| File | Purpose |
|---|---|
| `axur_api.py` | `AxurTenantAPI` client: create, list, lookup-by-name, suspend, resume. Loads `.env` automatically. |
| `create_tenant.py` | Creates a tenant named after `INSTRUQT_SANDBOX_ID`, retries transient errors, writes `tenant_key.txt` |
| `delete_tenant.py` | Reads `tenant_key.txt` (or takes a key argument), **suspends** the tenant, removes the file |
| `resume_tenant.py` | `python3 resume_tenant.py <KEY>` re-activates a suspended tenant |
| `preload.d/` | Extra preload scripts (`.py`/`.sh`), run in name order by the challenge-1 setup after the YAML. See `preload.d/README.md`. |
| `preload_tenant.py` + `tenant_preload.yml` | Per-tenant preload/config driver run by the **challenge-1 setup script**. Declarative YAML: `credit_limit`, `assets`, `safelist`, and a raw `requests` escape hatch; idempotent; `--dry-run` and `--undo`. The YAML holds Axur's lab content (Netflix brand, example.com domain, Microsoft vendor). |
| `validate_tenant.py` | Pulls the tenant back from the API and checks it against `tenant_preload.yml`: tenant active, every asset ACTIVE with its monitoring, seeded tickets and EASM seeds present (CRITICAL, exit 1), plus INFO on the participant user, real detections, credential exposures, credits and monitoring modules. Runs last in the challenge-1 setup (`--wait 120` polls for the first real detections). |
| `user_provision.py` | Registers the participant user on the tenant via Axur's event endpoint `POST /api/identity/registration/users/{tenant}` (email `<participant>@USER_DOMAIN`, generated password, `groupKey` manager). Writes `user_email.txt`, `user_password.txt`, `user_id.txt`, `user_credentials.sh`; idempotent on re-run. `--delete` is a no-op until Axur provides a delete endpoint (`AXUR_USER_DELETE_PATH`). Falls back to *pending* mode (exit 0) if the endpoint disappears. |
| `list_tenants.py` | Read-only listing of key / name / active / suspended. Good first check of the API key. |

## No login / 2FA needed — use an API key

The scripts never log in. Instead:

1. Log in to Axur ONE once (username + password + 2FA) with a user that has the
   **MSSP Partner Manager** permission.
2. Go to **My Preferences → API KEY** (https://one.axur.com/preferences?tab=api-keys) and create a key.
3. Paste it into `.env` as `AXUR_TOKEN=...` (file is gitignored) or export it in the environment.

Every request then carries `Authorization: Bearer <key>`. The key is tied to your user: if the user is
deactivated the key is revoked, and it can be revoked from the same tab at any time.

## Why "delete" is a suspend (confirmed by Axur support, 2026-09-09)

- API keys work **only on routes whose path includes `/api`**. The routes the web portal calls
  (`/gateway/1.0/customers/mssp-tenants/...`) are portal-only and answer 403 to API keys.
- The tenant lifecycle offered by the API is create + **suspend** + **resume**; there is no DELETE.
  Suspending disables all asset monitoring and user activity, so the tenant stops consuming credits.
  Suspended tenants stay in the list; `resume_tenant.py` brings one back.
- **Portal visibility lag:** a tenant created through the API does not appear in *Tenants management*
  until the partner admin's session token refreshes (~30 minutes). Then log out and back in. This only
  affects the root (partner) tenant's existing sessions; the tenant itself is live immediately.
  Reason (Axur): permissions live inside stateless JWTs. Creating a tenant forces a refresh of the
  *creating* credential only — the browser session when created in the UI, the API key when created via
  the API. Any other already-issued token (e.g. your open portal session) keeps its old permission list
  until it refreshes or you log in again.

## Environment

| Variable | Default | Notes |
|---|---|---|
| `AXUR_TOKEN` | required | API key, see above |
| `INSTRUQT_SANDBOX_ID` | — | **Tenant name** (one tenant per Instruqt sandbox). Axur derives a 5-letter key from it (e.g. `igor-script-test` → `IGRSC`). Fallbacks, in order: `AXUR_TENANT_NAME` (highest), `INSTRUQT_PARTICIPANT_ID`, `default-team`. |
| `AXUR_PARTNER_KEY` | `IE2L` | Your MSSP partner key |
| `AXUR_SEGMENT` | random per run | Set to pin one of: FOOD_BEVERAGE, EDUCATION, POWER_CHEMISTRY, FINANCIAL_INSURANCE, LAW, MANUFACTURE, HEALTHCARE, REAL_ESTATE_SERVICES, PUBLIC_SECTOR_NGOS, TECHNOLOGY, TELECOMMUNICATIONS, TRANSPORT_LOGISTICS, TRAVEL_TOURISM, RETAIL_ECOMMERCE |
| `AXUR_BRAND_NAME` | tenant name (sandbox id) | Brand asset name |
| `AXUR_BRAND_WEBSITE` | `www.infoblox.com` | Brand asset website |
| `AXUR_CTI_ENABLED` | `true` | `true` activates the CTI & EASM workspace and **consumes credits** |
| `AXUR_BILLING_COUNTRY` | `ES` (Spain) | ISO 3166-1 alpha-2 |
| `AXUR_BASE_URL` | `https://api.axur.com/gateway/1.0` | Override for testing |
| `USER_DOMAIN` | `infoblox.lab` | `user_provision.py`: login email = `<participant id>@<USER_DOMAIN>` |
| `AXUR_USER_GROUP` | `manager` | `user_provision.py`: `groupKey` for the participant (`manager` or `viewer`) |
| `AXUR_USER_FIRSTNAME` / `AXUR_USER_LASTNAME` | `Lab` / participant id | `user_provision.py`: display name |
| `AXUR_USER_CREATE_PATH` | `/api/identity/registration/users/{key}` | `user_provision.py`: Axur's event registration endpoint (IE2L sub-tenants only) |
| `AXUR_USER_DELETE_PATH` | none | `user_provision.py`: set when Axur provides a delete endpoint (`{key}`, `{user_id}`) |

## Run

```bash
pip install -r requirements.txt
python3 list_tenants.py                       # sanity-check the key
export INSTRUQT_SANDBOX_ID=team-42      # Instruqt sets this for you
python3 create_tenant.py                      # -> tenant_key.txt, tenant_name.txt
python3 delete_tenant.py                      # suspends the key in tenant_key.txt, removes the files
python3 delete_tenant.py ZOOM                 # or suspend an explicit key
python3 resume_tenant.py ZOOM
```

Every request is logged to `AxurTenant.log` (rotating, 5 MB × 3).

## Instruqt track integration (`axur-lab/`)

The track is pulled into `axur-lab/` (`instruqt track pull axur-lab`). What was added:

- `config.yml`: a `shell` container (`gcr.io/instruqt/cloud-client`) to run lifecycle scripts, one virtual
  browser `axur` → https://one.axur.com/ (the Infoblox Portal browser was removed), and the secret `AXUR_TOKEN`.
- Both challenges have a single **Axur Portal** tab (`type: browser`, `hostname: axur`).
- `track_scripts/setup-shell` (same pattern as the other labs): installs deps, `git clone`s this repo
  (https://github.com/iracic82/axur-lab, public so the sandbox can clone anonymously) to `/root/lab/axur-lab`, writes `/root/lab/axur.env` with the
  token and sandbox id (xtrace off so the secret never hits the logs), and runs `create_tenant.py` with
  `INSTRUQT_SANDBOX_ID` (falls back to `INSTRUQT_PARTICIPANT_ID`) as tenant + brand name, then
  `user_provision.py` to register the participant's login on that tenant. Agent variables exported:
  `AXUR_TENANT_KEY`, `AXUR_TENANT_NAME`, `AXUR_USER_EMAIL`, `AXUR_USER_PASSWORD` (shown in challenge 1).
- `track_scripts/cleanup-shell` sources `axur.env`, runs `user_provision.py --delete` (no-op until Axur adds a
  delete endpoint), waits 120 s, then runs `delete_tenant.py` (= suspend), using `tenant_key.txt` from setup or
  a lookup by name if that file is gone. `delete_tenant.py` **verifies** the suspension from the tenant listing
  and retries every 60 s for up to 30 min (`AXUR_SUSPEND_RETRIES` / `AXUR_SUSPEND_RETRY_DELAY`): from sandboxes
  the suspend call has answered `400 Tenant is already suspended` while the tenant stayed active, and the state
  only became consistent minutes later. Instruqt gives cleanup scripts 55 min, so this fits.

- `01-introduction/setup-shell` (challenge-1 setup) does `git pull` in `/root/lab/axur-lab` and runs
  `preload_tenant.py`, which applies `tenant_preload.yml` to the sandbox's tenant. The same partner API key
  is used for every tenant (per-tenant endpoints take the `customerKey`); no per-tenant keys exist.
  Because of the `git pull`, changing what is preloaded is a commit + push of the YAML — no track push.

Workflow:

```bash
git push                                   # scripts are cloned from GitHub at sandbox start
cd axur-lab && instruqt track validate && instruqt track push
```

One-time in Instruqt: create the team secret **AXUR_TOKEN** (your Axur API key) — the track only declares it.
Setup is idempotent: if a tenant with the sandbox's name already exists it is resumed and reused.

## How to preload configuration into each lab tenant

Every sandbox gets its own empty Axur tenant. Whatever each tenant must contain for the lab is applied by
the **challenge-1 setup script**, which pulls this repo and runs two things in order:

1. `tenant_preload.yml` via `preload_tenant.py` — declarative, for plain API calls.
2. `preload.d/*` — scripts, for anything that needs logic.

Both target the sandbox's tenant automatically (`tenant_key.txt`, written at track setup) with the partner
API key. Deploying a change is `git commit && git push`; the next sandbox picks it up. No track push.

### 1. Declarative: edit `tenant_preload.yml`

| Section | What it does | Endpoint |
|---|---|---|
| `credit_limit` | `unlimited`, a number, or a per-product map | `PATCH /credit-management-api/customers/{key}/limit/...` |
| `assets` | list of asset payloads; skipped if an asset with the same type+name exists | `POST /assets-api/customers/{key}/asset` |
| `safelist` | `{group, items[]}` entries | `POST /touchpoints/items` |
| `requests` | raw `{method, path, json, params, ok}` for anything else (automations, tickets, ...) | any |

`{key}` and `{name}` inside any string become the tenant key and the tenant name (= sandbox id).
The file ships with commented examples for each section; uncomment and adapt.

Example — one brand asset and a credit cap per tenant:

```yaml
credit_limit: 500
assets:
  - type: BRAND
    name: "{name}"
    monitoring: [phishing, malware, fake-social-media-profile, similar-domain-name]
    properties:
      officialWebsite: https://www.infoblox.com
      nameVariations: ["infoblox"]
      primaryLocale: ["US:en"]
```

Asset types and required properties are in the Axur spec (`openapi-axur.yaml`, `POST /assets-api/customers/{customerKey}/asset`):
BRAND needs `nameVariations`, `primaryLocale` and `officialWebsite` (or logos); DOMAIN needs only `name`.

**Catalogue:** `examples/tenant_preload.example.yml` is a complete, dry-runnable file with one entry per asset
type (BRAND incl. takedown capability, DOMAIN, VIP, APP, THIRD_PARTY_PAGE, IP, BIN, TRACKING_TOKEN), per-product
credit limits, safelist groups, an automation, a manual ticket and an EASM discovery seed. Copy from it.
What was live-verified on tenant PRLD (2026-09-10): BRAND, DOMAIN, VIP, APP, BIN assets and the safelist call.
Two API rules learned there: a THIRD_PARTY_PAGE name must be a bare domain (paths are rejected), and
`cti:infrastructure` monitoring (IP / DOMAIN) is only accepted on tenants created with `ctiEnabled: true`.

**Vendor assets** (`CUSTOMER_VENDOR`, Supply Chain Intel) need `properties.vendorId`, a number from Axur's
vendor catalogue, and the asset `name` must match that vendor's catalogue name. The public API has no vendor
lookup, but a create request with a wrong name returns `asset.customerVendor.name` with the vendor's real name,
so ids can be discovered by probing (no side effects). The first 50 are in `examples/axur_vendor_ids.json`
(Microsoft = 30, Infoblox = 23, Cisco = 8, Google = 20, Amazon Web Services = 3, ...).

**Current lab content** (Axur's recommendation, 2026-09-11, in `tenant_preload.yml`): brand *Netflix*
(phishing, similar-domain-name), domain *example.com* (user/employee credentials, code-secret-leak) and vendor
*Microsoft* (supply-chain-intel). All three verified live: created ACTIVE, skipped on re-run, removed by `--undo`.

### 2. Scripts: add a file to `preload.d/`

For steps that need conditions, lookups or several calls, add `NN-name.py` or `NN-name.sh` (run in name
order after the YAML). Start from `preload.d/00-report.py`. Rules in `preload.d/README.md`: read the tenant
from `tenant_key.txt`, be idempotent (treat 409 as "already there"), exit 0 unless the lab cannot continue.

### 3. Test before you push

```bash
# what would be sent, no calls made
python3 preload_tenant.py --key PRLD --dry-run

# apply for real to a throwaway tenant, run twice (second run must skip everything), then undo
python3 preload_tenant.py --key PRLD
python3 preload_tenant.py --key PRLD
python3 preload_tenant.py --key PRLD --undo          # deactivates created assets, limit -> unlimited

# a preload.d script on its own (repo root, tenant files present)
echo PRLD > tenant_key.txt && python3 preload.d/00-report.py
```

`PRLD` (`preload-test`) is a suspended throwaway tenant kept for this; `python3 resume_tenant.py PRLD` if a
test needs it active. To rehearse the whole challenge-1 script, `instruqt track test axur-lab` runs a real
sandbox (creates and then suspends a tenant named after the test participant id).

### 4. Deploy and verify

```bash
git add tenant_preload.yml preload.d && git commit -m "preload: ..." && git push
```

Start a sandbox and open the challenge-1 setup log in Instruqt: `preload_tenant.py` prints every step it
applied or skipped, and `00-report.py` prints the tenant's credit limit, assets and enabled monitoring at
the end. `instruqt track logs axur-lab --since 15m` shows the same from the CLI (it tails; Ctrl-C to stop).

## Synthetic data: what is possible and what makes sense (explored 2026-09-11)

**Most of the lab is fed by real data within minutes, so little needs seeding.** Measured on fresh lab tenants:

| Workspace | What a new tenant contains | Source of the data |
|---|---|---|
| Brand Protection | **500 to 700 real tickets within ~10 min** of the Netflix asset going live: phishing pages (urlscan, html-links), lookalike domains (certificate-transparency `ctlog`), threat-hunting hits, passive DNS, Facebook ads. Each carries Axur's AI predictions (login form present, payment requested, language, colours) | Axur collectors, automatic |
| Data Leakage | **9,745 credential exposures** on example.com the moment the domain asset exists (historical breaches, employee/customer split, stealer logs) | Axur leak index, automatic |
| Deep & Dark Web, CTI, Supply Chain Intel | Explore searches, bulletins and the Microsoft vendor report are global datasets | Axur, automatic |
| EASM | Empty until a **seed** is added; one API call starts discovery of example.com | needs preload (tested) |
| Executives & VIPs | Empty. A VIP asset can be created (monitoring id `executives`), but name variations and the face photo are UI-only, and a fictional executive yields no detections | needs a decision |

**Enabled in `tenant_preload.yml`** (decision 2026-09-11): the EASM seed for example.com, one curated
`fake-social-media-profile` ticket ("Netflix Golden") because real detections are only phishing and lookalike
domains, and the fictional executive **Alex Rivera** as a VIP asset so the Executives workspace is configured.
A curated phishing ticket is kept commented out; the collectors deliver hundreds on their own.

What the API can seed, all tested live:

- `POST /api/easm/seeds?axur_tenant_key={key}` with `{"seed_names": ["example.com"]}` starts EASM discovery.
- `POST /api/tickets-api/tickets` creates curated tickets (`phishing`, `fake-social-media-profile`, ...). `assets`
  must be an **array of string asset keys** (objects give a 500). A repeated reference answers 409, so re-runs are
  safe. Useful to guarantee a predictable example (e.g. the "Netflix Golden" profile the guide mentions) beside the
  hundreds of real ones. Participants should not request takedowns on seeded tickets.
- `POST /api/assets-api/customers/{key}/asset` with `type: VIP, monitoring: [executives]` adds an executive.
- `POST /api/touchpoints/items` adds safelist entries (works). Automations need a `status` precondition for
  `CREDENTIAL` match types (not enabled).

Not seedable through the API: credential leaks, dark web content, executive detections, CTI bulletins. Those come
from Axur's own collection, which is the point of the demo.

Reading the data back: `GET /api/tickets-api/tickets?assets=<assetKey>&pageSize=200&include=fields` (the `customer`
filter is rejected; types and AI predictions are under `detection.*`), `GET /api/exposure-api/credentials?customer=<key>`
and `/credentials/total`.

## Open items with Axur

1. **User-delete endpoint.** Cleanup leaves each participant's user attached to its suspended tenant. The
   script already has the slot: set `AXUR_USER_DELETE_PATH` (placeholders `{key}`, `{user_id}`) when they
   provide the path; `cleanup-shell` already calls `user_provision.py --delete`.
2. **Vendor ids for any other vendors** they want in the lab (see below). Microsoft is covered.
3. **Feedback for them:** the `CUSTOMER_VENDOR` example they sent was incomplete (no `vendorId`), and there is
   no documented way to look vendor ids up. A small catalogue endpoint or a list in the docs would help.

### The vendor asset, explained

Axur's payload for the Microsoft asset was

```json
{"type": "CUSTOMER_VENDOR", "name": "Microsoft", "monitoring": ["supply-chain-intel"]}
```

Sent as-is the API answers `400 asset.missingRequiredProperty` for `VENDOR_ID`. A vendor asset is not free
text like a brand or a domain: it links to an entry in Axur's own vendor catalogue, so the entry's numeric id
must be passed as `properties.vendorId`, and the `name` must equal the catalogue name for that id
(`400 asset.customerVendor.name` otherwise).

The public API has no catalogue search, but that second error is informative: a request with an id and a wrong
name returns the vendor's real name. Ids 1, 2, 3, ... were probed that way with a dummy name (nothing gets
created by a rejected request); Microsoft is **30**. The working payload, now in `tenant_preload.yml`:

```json
{"type": "CUSTOMER_VENDOR", "name": "Microsoft", "monitoring": ["supply-chain-intel"], "properties": {"vendorId": 30}}
```

The first 50 ids collected during the scan are in `examples/axur_vendor_ids.json` (Infoblox 23, Cisco 8,
Google 20, Amazon Web Services 3, ...). To find another vendor, probe further ids the same way or ask Axur.

## Lab story: sources for the product claims

The challenge texts (`axur-lab/01-introduction`, `axur-lab/02-labguide`) describe what Axur does in Axur's own
terms. Every claim traces to one of these, checked 2026-09-11:

| Claim in the story | Source |
|---|---|
| Ticket lifecycle: Quarantine (re-checked daily 06:00, auto-discard after 6 months), Incident, Discard, Takedown; evidence raises removal odds | [Actions within a ticket](https://help.axur.com/en/articles/9005224-actions-within-a-ticket) |
| Closed tickets end as Discarded, Resolved, Unresolved or Interrupted | [Work lists and Export](https://help.axur.com/en/articles/7967405-work-lists-and-export) |
| AI severity classification with flame icons; OnePixel real-time clone detection | [Phishing](https://help.axur.com/en/articles/7988780-phishing), [Sorting and prioritization](https://help.axur.com/en/articles/7967591-sorting-and-prioritization-of-tickets) |
| Lookalike domains: ticket opened and quarantined automatically | [Smart Monitoring of Similar Domains](https://help.axur.com/en/articles/11566976-smart-monitoring-of-similar-domains) |
| Takedown: ~98% success, first phishing notification < 4 min, 86% fully automated, stay-down guarantee, authorization document with brand logo | [How Takedown works](https://help.axur.com/en/articles/9345675-how-takedown-works-the-role-of-entities-and-the-time-it-takes-to-resolve-an-incident), [Takedown authorization](https://help.axur.com/en/articles/8058239-takedown-authorization-document-and-other-documents-required-for-takedown), [axur.com/takedown](https://www.axur.com/en-us/takedown/), [axur.com/brand-protection](https://www.axur.com/en-us/brand-protection/) |
| Brand exposure level assigned at registration | [Understand what brand exposure level means](https://help.axur.com/en/articles/10962984-understand-what-brand-exposure-level-means) |
| Employee vs customer credentials, stealer logs with machine context, code secrets, breach mentions | [Mentions in data breach](https://help.axur.com/en/articles/12996239-mentions-in-data-breach), [Code secret exposure](https://help.axur.com/en/articles/8992985-code-secret-exposure), [Infiltrated accounts](https://help.axur.com/en/articles/8043746-infiltrated-accounts) |
| Deep & Dark Web: 3,000+ channels incl. WhatsApp/Telegram/Discord; Explore with quotes/operators; ticket from a result | [axur.com/technical-information](https://www.axur.com/en-us/technical-information/), [Explore](https://help.axur.com/en/articles/8043835-explore-open-searches-in-deep-dark-web) |
| Executives & VIPs: personal info, credentials, cards, fake profiles via facial recognition (7-day Face Match), encrypted storage | [Monitoring for Executives and VIPs](https://help.axur.com/en/articles/10495379-monitoring-for-executives-and-vips-personalized-security) |
| CTI monitoring rules (technologies, industry, geography, actors, risk level), default rules, follow to get alerts; risk score triage | [Cyber Threat Intel](https://help.axur.com/en/articles/8950599-cyber-threat-intel-cti), [Risk Score](https://help.axur.com/en/articles/16165330-risk-score-understanding-and-using-threat-prioritization) |
| EASM: seeds → hosts, subdomains, IPs, ports, certificates; risk score from CVSS + EPSS + context | [EASM](https://help.axur.com/en/articles/16162907-external-attack-surface-management-easm) |
| Supply Chain Intel vendor report tabs, AI summary, critical bulletins, trend indicators, PDF export | [Supply Chain Intel](https://help.axur.com/en/articles/16007279-supply-chain-intel) |
| Workspace names and taglines | Axur ONE workspace menu (screenshot, 2026-09-11) |

## Endpoints used (all documented, all under `https://api.axur.com/gateway/1.0/api`)

| Call | Path | Notes |
|---|---|---|
| Create | `POST /customers-api/customer` | body `{"customer": {partnerKey, name, segment, ctiEnabled, billingCountry}, "asset": {name, website}}` → 201 with `customerKey` |
| List | `GET /customers-api/customers` | `[{name, key, active, suspended, category, parentCustomerKey, childTenantCount}]` |
| Suspend | `POST /customers-api/tenant/{key}/suspend` | 200/204 |
| Resume | `POST /customers-api/tenant/{key}/resume` | 200/204 |

Spec: https://docs.axur.com/en/axur/api/ (`openapi-axur.yaml`, v1.0.81).
