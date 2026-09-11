import os
import sys
import time
from axur_api import AxurTenantAPI

# "Delete" for an Axur MSSP tenant = suspend. The public API has no DELETE; suspending disables all
# asset monitoring and user activity, so the tenant stops consuming credits. Use resume_tenant.py to undo.
BASE_URL = os.environ.get("AXUR_BASE_URL", "https://api.axur.com/gateway/1.0")
TOKEN = os.environ.get("AXUR_TOKEN")
TENANT_KEY_FILE = "tenant_key.txt"
TENANT_NAME_FILE = "tenant_name.txt"

if not TOKEN:
    print("❌ AXUR_TOKEN is not set (paste it into .env).", flush=True)
    sys.exit(1)

api = AxurTenantAPI(base_url=BASE_URL, token=TOKEN)

# Tenant key: CLI argument > tenant_key.txt (written by create_tenant.py) > lookup by tenant name
tenant_key = ""
if len(sys.argv) > 1:
    tenant_key = sys.argv[1].strip()
else:
    try:
        with open(TENANT_KEY_FILE, "r") as f:
            tenant_key = f.read().strip()
    except FileNotFoundError:
        pass
    if not tenant_key:
        name = (
            os.environ.get("AXUR_TENANT_NAME")
            or os.environ.get("INSTRUQT_SANDBOX_ID")
            or os.environ.get("INSTRUQT_PARTICIPANT_ID")
        )
        if name:
            print(f"ℹ️ {TENANT_KEY_FILE} not found; looking up tenant '{name}' by name…", flush=True)
            tenant_key = api.get_tenant_key_by_name(name) or ""

if not tenant_key:
    print(f"❌ No tenant key: pass it as an argument, run create_tenant.py first, or set INSTRUQT_SANDBOX_ID.", flush=True)
    sys.exit(1)

def tenant_state(key):
    """Current {active, suspended} of the tenant from the documented listing, or None if not visible."""
    for t in api.list_tenants():
        if t.get("key") == key:
            return t
    return None


# Suspend, then VERIFY from the listing and retry if needed. Observed 2026-09-11 from Instruqt sandboxes:
# the suspend call answered HTTP 400 "Tenant is already suspended" while the listing showed the tenant
# active, and it stayed active; the state resolved by itself within ~25 minutes. Instruqt allows a track
# cleanup script 55 minutes, so keep retrying for up to 30 minutes (30 x 60 s) by default.
ATTEMPTS = int(os.environ.get("AXUR_SUSPEND_RETRIES", "30"))
DELAY = int(os.environ.get("AXUR_SUSPEND_RETRY_DELAY", "60"))
suspended = False
for attempt in range(1, ATTEMPTS + 1):
    print(f"🔗 Suspending tenant {tenant_key} (attempt {attempt}/{ATTEMPTS})", flush=True)
    result = api.suspend_tenant(tenant_key)
    if result["status"] != "success":
        print(f"⚠️ Suspend call: {result.get('error')}", flush=True)
    state = tenant_state(tenant_key)
    if state is None:
        print("⚠️ Tenant not visible in the listing yet.", flush=True)
    elif state.get("suspended"):
        suspended = True
        break
    else:
        print(f"⏳ Listing still shows tenant {tenant_key} active; retrying in {DELAY}s…", flush=True)
    if attempt < ATTEMPTS:
        time.sleep(DELAY)

if suspended:
    print(f"⏸️ Tenant {tenant_key} suspended (monitoring and credit consumption stopped).", flush=True)
    for path in (TENANT_KEY_FILE, TENANT_NAME_FILE):
        try:
            os.remove(path)
            print(f"📁 Removed file: {path}", flush=True)
        except FileNotFoundError:
            pass
        except OSError as e:
            print(f"⚠️ Could not remove file {path}: {e}", flush=True)
else:
    print(f"❌ Failed to suspend tenant {tenant_key}: {result.get('error')}", flush=True)
    print("⚠️ Tenant may still be active. Please verify manually in Axur ONE.", flush=True)
    sys.exit(1)
