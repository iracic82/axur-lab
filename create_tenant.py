import os
import sys
import time
import random
from axur_api import AxurTenantAPI

# Configuration
BASE_URL = os.environ.get("AXUR_BASE_URL", "https://api.axur.com/gateway/1.0")
TOKEN = os.environ.get("AXUR_TOKEN")
# Tenant name = the Instruqt sandbox id (one tenant per sandbox). Fallbacks for local runs.
TEAM_ID = (
    os.environ.get("AXUR_TENANT_NAME")
    or os.environ.get("INSTRUQT_SANDBOX_ID")
    or os.environ.get("INSTRUQT_PARTICIPANT_ID")
    or "default-team"
)
TENANT_KEY_FILE = "tenant_key.txt"
TENANT_NAME_FILE = "tenant_name.txt"

if not TOKEN:
    print("❌ AXUR_TOKEN is not set (create an API key in Axur ONE → My Preferences → API KEY).", flush=True)
    sys.exit(1)

# Allowed values for customer.segment (Axur API spec v1.0.81)
SEGMENTS = [
    "FOOD_BEVERAGE", "EDUCATION", "POWER_CHEMISTRY", "FINANCIAL_INSURANCE", "LAW",
    "MANUFACTURE", "HEALTHCARE", "REAL_ESTATE_SERVICES", "PUBLIC_SECTOR_NGOS", "TECHNOLOGY",
    "TELECOMMUNICATIONS", "TRANSPORT_LOGISTICS", "TRAVEL_TOURISM", "RETAIL_ECOMMERCE",
]

# Tenant description (same fields the Axur ONE UI sends)
#   tenant name + brand name = Instruqt sandbox id, segment random, website infoblox.com, billing Spain
tenant_request_body = {
    "partnerKey": os.environ.get("AXUR_PARTNER_KEY", "IE2L"),
    "name": TEAM_ID,
    "segment": os.environ.get("AXUR_SEGMENT") or random.choice(SEGMENTS),
    "brandName": os.environ.get("AXUR_BRAND_NAME", TEAM_ID),
    "brandOfficialWebsite": os.environ.get("AXUR_BRAND_WEBSITE", "www.infoblox.com"),
    # ctiEnabled=true activates the CTI & EASM workspace and consumes credits
    "ctiEnabled": os.environ.get("AXUR_CTI_ENABLED", "true").lower() == "true",
    "billingCountry": os.environ.get("AXUR_BILLING_COUNTRY", "ES"),   # ISO 3166-1 alpha-2, ES = Spain
}
print(f"ℹ️ Tenant '{TEAM_ID}' segment={tenant_request_body['segment']} "
      f"website={tenant_request_body['brandOfficialWebsite']} country={tenant_request_body['billingCountry']}", flush=True)

# API client initialization
api = AxurTenantAPI(base_url=BASE_URL, token=TOKEN)

# Idempotent: if a tenant with this name already exists (setup re-run), reuse it instead of creating a duplicate
existing_key = api.get_tenant_key_by_name(TEAM_ID)
if existing_key:
    print(f"ℹ️ Tenant '{TEAM_ID}' already exists with key {existing_key}; reusing it.", flush=True)
    resumed = api.resume_tenant(existing_key)
    if resumed["status"] != "success":
        print(f"⚠️ Resume returned {resumed.get('error')} (tenant is probably already active).", flush=True)
    with open(TENANT_KEY_FILE, "w") as f:
        f.write(existing_key)
    with open(TENANT_NAME_FILE, "w") as f:
        f.write(TEAM_ID)
    print(f"✅ Tenant key saved to {TENANT_KEY_FILE}: {existing_key}", flush=True)
    sys.exit(0)

# Retry on transient errors (e.g. 502/503/504, timeouts); do not retry 4xx
max_retries = 5
for attempt in range(max_retries):
    create_response = api.create_tenant(tenant_request_body)
    if create_response.get("status") == "success":
        break
    print(
        f"⚠️ Attempt {attempt+1} failed: {create_response.get('error')}",
        flush=True,
    )
    if not create_response.get("retryable"):
        print("❌ Non-retryable error (check token, 'MSSP Partner Manager' permission, or payload).", flush=True)
        sys.exit(1)
    time.sleep((2**attempt) + random.random())
else:
    print("❌ Tenant creation failed after retries", flush=True)
    sys.exit(1)

print("✅ Tenant created successfully.", flush=True)
tenant_data = create_response["data"]


def extract_key(data):
    """Find the tenant key in whatever shape the gateway returns."""
    if not isinstance(data, dict):
        return None
    for k in ("customerKey", "key", "tenantKey", "id"):
        if data.get(k):
            return str(data[k])
    for nested in ("customer", "tenant", "result", "data"):
        found = extract_key(data.get(nested))
        if found:
            return found
    return None


# Extract tenant key from the response; fall back to a lookup by name
tenant_key = extract_key(tenant_data)
if not tenant_key:
    print("ℹ️ Tenant key not in response body, looking it up by name…", flush=True)
    tenant_key = api.get_tenant_key_by_name(TEAM_ID)

if tenant_key and "/" in tenant_key:
    tenant_key = tenant_key.split("/")[-1]

if not tenant_key:
    print("❌ Tenant key not found. Aborting.", flush=True)
    sys.exit(1)

with open(TENANT_KEY_FILE, "w") as f:
    f.write(tenant_key)
print(f"✅ Tenant key saved to {TENANT_KEY_FILE}: {tenant_key}", flush=True)

with open(TENANT_NAME_FILE, "w") as f:
    f.write(TEAM_ID)
print(f"✅ Tenant name saved to {TENANT_NAME_FILE}: {TEAM_ID}", flush=True)
