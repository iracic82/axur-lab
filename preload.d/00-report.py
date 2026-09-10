#!/usr/bin/env python3
"""
00-report.py — read-only sanity check that runs first in preload.d/.
Prints the tenant's state (settings + assets + enabled monitoring) into the Instruqt log so a failed
preload is easy to diagnose. Also the template for further preload.d scripts.
"""
import os
import sys
import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # repo root -> axur_api importable
from axur_api import AxurTenantAPI  # noqa: E402  (loads .env for local runs)

key = open("tenant_key.txt").read().strip()
name = open("tenant_name.txt").read().strip() if os.path.exists("tenant_name.txt") else key
api = AxurTenantAPI(os.environ.get("AXUR_BASE_URL", "https://api.axur.com/gateway/1.0"), os.environ.get("AXUR_TOKEN", ""))
h = api._headers()

try:
    settings = requests.get(f"{api.base_url}/api/credit-management-api/customers/{key}/settings", headers=h, timeout=60).json()
    assets = requests.get(f"{api.base_url}/api/assets-api/assets", headers=h, params={"customerKey": key, "perPage": 100}, timeout=60).json().get("assets", [])
    mon = requests.get(f"{api.base_url}/api/assets-api/customers/{key}/monitoring", headers=h, timeout=60).json().get("monitoring", [])
except (requests.RequestException, ValueError) as e:
    print(f"⚠️ report failed: {e}", flush=True)
    sys.exit(0)  # diagnostic only — never block the lab

limit = "unlimited" if settings.get("unlimited") else settings.get("maximumLimit")
enabled = [m["id"] for m in mon if m.get("limit", {}).get("isMonitoringEnabled")]
print(f"📋 tenant {key} ({name}): credit limit={limit}, billing={settings.get('billingCountry')}, "
      f"assets={len(assets)}, monitoring enabled={len(enabled)}/{len(mon)}", flush=True)
for a in assets:
    print(f"   - {a.get('assetKey'):<10} {a.get('type'):<8} {a.get('name')}  [{a.get('status')}]", flush=True)
