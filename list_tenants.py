import os
import sys
from axur_api import AxurTenantAPI

# Read-only: lists the MSSP tenants your API key can see. Good for checking the key + permission.
BASE_URL = os.environ.get("AXUR_BASE_URL", "https://api.axur.com/gateway/1.0")
TOKEN = os.environ.get("AXUR_TOKEN")

if not TOKEN:
    print("❌ AXUR_TOKEN is not set (paste it into .env).", flush=True)
    sys.exit(1)

api = AxurTenantAPI(base_url=BASE_URL, token=TOKEN)
tenants = api.list_tenants()

if not tenants:
    print("⚠️ No tenants returned (empty list, bad token, or missing 'MSSP Partner Manager' permission — see AxurTenant.log).", flush=True)
    sys.exit(1)

print(f"✅ {len(tenants)} tenant(s):", flush=True)
print(f"{'KEY':<12} {'NAME':<40} {'ACTIVE':<7} {'SUSPENDED':<10} {'CATEGORY':<14} PARENT", flush=True)
for t in tenants:
    print(
        f"{str(t.get('key','')):<12} {str(t.get('name',''))[:40]:<40} "
        f"{str(t.get('active','')):<7} {str(t.get('suspended','')):<10} "
        f"{str(t.get('category','')):<14} {t.get('parentCustomerKey') or ''}",
        flush=True,
    )
