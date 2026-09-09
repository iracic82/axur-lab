# Axur MSSP tenant scripts (Instruqt)

Same pattern as the Infoblox CSP `sandbox_api.py` / `create_sandbox.py` / `delete_sandbox.py` trio.

| File | Purpose |
|---|---|
| `axur_api.py` | `AxurTenantAPI` client: create, list, lookup-by-name, suspend, resume. Loads `.env` automatically. |
| `create_tenant.py` | Creates a tenant named after `INSTRUQT_SANDBOX_ID`, retries transient errors, writes `tenant_key.txt` |
| `delete_tenant.py` | Reads `tenant_key.txt` (or takes a key argument), **suspends** the tenant, removes the file |
| `resume_tenant.py` | `python3 resume_tenant.py <KEY>` re-activates a suspended tenant |
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
  `INSTRUQT_SANDBOX_ID` (falls back to `INSTRUQT_PARTICIPANT_ID`) as tenant + brand name. The key and name
  are exported as agent variables `AXUR_TENANT_KEY` / `AXUR_TENANT_NAME`.
- `track_scripts/cleanup-shell` sources `axur.env` and runs `delete_tenant.py` (= suspend), using
  `tenant_key.txt` from setup or a lookup by name if that file is gone.

Workflow:

```bash
git push                                   # scripts are cloned from GitHub at sandbox start
cd axur-lab && instruqt track validate && instruqt track push
```

One-time in Instruqt: create the team secret **AXUR_TOKEN** (your Axur API key) — the track only declares it.
Setup is idempotent: if a tenant with the sandbox's name already exists it is resumed and reused.

## Endpoints used (all documented, all under `https://api.axur.com/gateway/1.0/api`)

| Call | Path | Notes |
|---|---|---|
| Create | `POST /customers-api/customer` | body `{"customer": {partnerKey, name, segment, ctiEnabled, billingCountry}, "asset": {name, website}}` → 201 with `customerKey` |
| List | `GET /customers-api/customers` | `[{name, key, active, suspended, category, parentCustomerKey, childTenantCount}]` |
| Suspend | `POST /customers-api/tenant/{key}/suspend` | 200/204 |
| Resume | `POST /customers-api/tenant/{key}/resume` | 200/204 |

Spec: https://docs.axur.com/en/axur/api/ (`openapi-axur.yaml`, v1.0.81).
