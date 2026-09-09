import os
import sys
from axur_api import AxurTenantAPI

# Re-activates a suspended tenant:  python3 resume_tenant.py <KEY>
BASE_URL = os.environ.get("AXUR_BASE_URL", "https://api.axur.com/gateway/1.0")
TOKEN = os.environ.get("AXUR_TOKEN")

if not TOKEN:
    print("❌ AXUR_TOKEN is not set (paste it into .env).", flush=True)
    sys.exit(1)
if len(sys.argv) < 2 or not sys.argv[1].strip():
    print("Usage: python3 resume_tenant.py <TENANT_KEY>   (keys: python3 list_tenants.py)", flush=True)
    sys.exit(1)

tenant_key = sys.argv[1].strip()
api = AxurTenantAPI(base_url=BASE_URL, token=TOKEN)
result = api.resume_tenant(tenant_key)
if result["status"] == "success":
    print(f"▶️ Tenant {tenant_key} resumed.", flush=True)
else:
    print(f"❌ Failed to resume tenant {tenant_key}: {result.get('error')}", flush=True)
    sys.exit(1)
