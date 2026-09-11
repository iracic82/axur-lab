#!/usr/bin/env python3
"""
Validate a lab tenant against what the lab promises, by pulling its state back from the Axur API.

Runs at the end of the challenge-1 setup (after preload) and can be run by hand:
  python3 validate_tenant.py                 # tenant from tenant_key.txt, expectations from tenant_preload.yml
  python3 validate_tenant.py --key OSMR
  python3 validate_tenant.py --key OSMR --wait 300   # keep polling up to 300 s for real detections to arrive

Checks (CRITICAL ones fail the run with exit 1; INFO ones only report):
  CRITICAL  tenant exists, is active and not suspended
  CRITICAL  every asset in tenant_preload.yml exists and is ACTIVE, with the configured monitoring attached
  CRITICAL  every seeded ticket in tenant_preload.yml (requests to /tickets-api/tickets) exists on its asset
  CRITICAL  every EASM seed in tenant_preload.yml (requests to /easm/seeds) is registered
  INFO      participant user registered on the tenant (user_email.txt, if present)
  INFO      real Brand Protection tickets already collected on the brand asset (count, by type)
  INFO      credential exposures on the domain asset (total)
  INFO      tenant credit settings (limit) and monitoring modules enabled
"""

import os
import sys
import json
import time
import argparse
import requests

from axur_api import AxurTenantAPI  # noqa: F401  (.env side effect)

BASE_URL = os.environ.get("AXUR_BASE_URL", "https://api.axur.com/gateway/1.0").rstrip("/")
TOKEN = os.environ.get("AXUR_TOKEN")


def hdrs():
    return {"Authorization": f"Bearer {TOKEN}", "Accept": "application/json", "Content-Type": "application/json"}


def get(path, **params):
    r = requests.get(f"{BASE_URL}{path}", headers=hdrs(), params=params, timeout=60)
    try:
        return r.status_code, r.json()
    except ValueError:
        return r.status_code, {}


def post(path, body=None, params=None):
    r = requests.post(f"{BASE_URL}{path}", headers=hdrs(), json=body or {}, params=params, timeout=60)
    try:
        return r.status_code, r.json()
    except ValueError:
        return r.status_code, {}


def load_config(path):
    try:
        import yaml
        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        return {}


def substitute(obj, mapping):
    if isinstance(obj, str):
        for k, v in mapping.items():
            obj = obj.replace("{" + k + "}", str(v))
        return obj
    if isinstance(obj, list):
        return [substitute(x, mapping) for x in obj]
    if isinstance(obj, dict):
        return {k: substitute(v, mapping) for k, v in obj.items()}
    return obj


def all_tickets(asset_key, max_pages=5):
    out, page = [], 1
    while page <= max_pages:
        code, body = get("/api/tickets-api/tickets", assets=asset_key, pageSize=200, page=page, include="fields")
        if code != 200:
            break
        chunk = body.get("tickets", [])
        out.extend(chunk)
        if len(chunk) < 200:
            break
        page += 1
    return out


class Report:
    def __init__(self):
        self.rows, self.critical_failures = [], 0

    def add(self, level, ok, name, detail=""):
        self.rows.append((level, ok, name, detail))
        if level == "CRITICAL" and not ok:
            self.critical_failures += 1
        mark = "✅" if ok else ("❌" if level == "CRITICAL" else "⚠️")
        print(f"{mark} [{level}] {name}{(': ' + detail) if detail else ''}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--key")
    ap.add_argument("--config", default="tenant_preload.yml")
    ap.add_argument("--wait", type=int, default=0, help="seconds to keep polling for real detections (INFO check)")
    args = ap.parse_args()
    if not TOKEN:
        print("❌ AXUR_TOKEN is not set", flush=True); sys.exit(1)

    key = args.key or (open("tenant_key.txt").read().strip() if os.path.exists("tenant_key.txt") else None)
    if not key:
        print("❌ no tenant key (pass --key or run create_tenant.py first)", flush=True); sys.exit(1)
    name = open("tenant_name.txt").read().strip() if os.path.exists("tenant_name.txt") else key
    cfg = substitute(load_config(args.config), {"key": key, "name": name})
    rep = Report()
    print(f"🔎 Validating tenant {key} ({name}) against {args.config}", flush=True)

    # --- tenant ---
    code, tenants = get("/api/customers-api/customers")
    t = next((x for x in (tenants if isinstance(tenants, list) else []) if x.get("key") == key), None)
    rep.add("CRITICAL", bool(t), "tenant exists", f"HTTP {code}" if not t else f"active={t.get('active')} suspended={t.get('suspended')}")
    if t:
        rep.add("CRITICAL", bool(t.get("active")) and not t.get("suspended"), "tenant is active and not suspended")

    # --- assets ---
    code, body = get("/api/assets-api/assets", customerKey=key, perPage=100)
    assets = body.get("assets", []) if code == 200 else []
    by_ident = {(a.get("type"), a.get("name")): a for a in assets}
    brand_key = domain_key = None
    for want in cfg.get("assets", []) or []:
        ident = (want.get("type"), want.get("name") or (want.get("properties") or {}).get("tokenName"))
        have = by_ident.get(ident)
        if not have:
            rep.add("CRITICAL", False, f"asset {ident[0]} '{ident[1]}' exists", "not found"); continue
        active = have.get("status") == "ACTIVE"
        missing = [m for m in (want.get("monitoring") or []) if m not in (have.get("monitoring") or [])]
        rep.add("CRITICAL", active and not missing, f"asset {ident[0]} '{ident[1]}' is ACTIVE with configured monitoring",
                f"{have.get('assetKey')} status={have.get('status')}" + (f" missing monitoring {missing}" if missing else ""))
        if ident[0] == "BRAND" and not brand_key: brand_key = have.get("assetKey")
        if ident[0] == "DOMAIN" and not domain_key: domain_key = have.get("assetKey")

    # --- seeded requests: tickets and EASM seeds ---
    want_tickets = [r for r in cfg.get("requests", []) or [] if r.get("path", "").endswith("/tickets-api/tickets")]
    want_seeds = [r for r in cfg.get("requests", []) or [] if r.get("path", "").endswith("/easm/seeds")]
    if cfg.get("easm_seeds"):
        want_seeds.append({"json": {"seed_names": list(cfg["easm_seeds"])}})
    if want_tickets:
        cache = {}
        for r in want_tickets:
            ref = (r.get("json") or {}).get("reference"); aks = (r.get("json") or {}).get("assets") or []
            found = False
            for ak in aks:
                cache.setdefault(ak, all_tickets(ak))
                if any((x.get("ticket") or {}).get("reference") == ref for x in cache[ak]):
                    found = True; break
            rep.add("CRITICAL", found, f"seeded ticket exists: {ref}")
    if want_seeds:
        code, body = post("/api/easm/seeds/list", {}, params={"axur_tenant_key": key})
        have_seeds = {s.get("seed_name") for s in (body.get("results", []) if code == 200 else [])}
        for r in want_seeds:
            for sn in (r.get("json") or {}).get("seed_names") or []:
                rep.add("CRITICAL", sn in have_seeds, f"EASM seed registered: {sn}", f"HTTP {code}" if code != 200 else "")

    # --- INFO: participant user ---
    if os.path.exists("user_email.txt"):
        email = open("user_email.txt").read().strip()
        code, users = get("/api/identity/users", customers=key, pageSize=50)
        ok = code == 200 and any(str((u.get("credentials") or {}).get("email", "")).lower() == email.lower() for u in (users if isinstance(users, list) else []))
        rep.add("INFO", ok, f"participant user registered: {email}", f"HTTP {code}" if code != 200 else "")

    # --- INFO: real detections (poll if asked); seeded references do not count ---
    if brand_key:
        seeded_refs = {(r.get("json") or {}).get("reference") for r in want_tickets}
        deadline = time.time() + args.wait
        while True:
            items = [x for x in all_tickets(brand_key) if (x.get("ticket") or {}).get("reference") not in seeded_refs]
            if items or time.time() >= deadline:
                break
            print(f"   ⏳ no real detections yet on {brand_key}; polling…", flush=True); time.sleep(30)
        types = {}
        for x in items:
            ty = (x.get("detection") or {}).get("type") or "unknown"; types[ty] = types.get(ty, 0) + 1
        rep.add("INFO", bool(items), f"real detections on brand asset {brand_key}", f"{len(items)} tickets {json.dumps(types)}")
    if domain_key:
        code, tot = get("/api/exposure-api/credentials/total", customer=key)
        rep.add("INFO", code == 200 and (tot.get("total") or 0) > 0, "credential exposures on the domain", f"total={tot.get('total')}" if code == 200 else f"HTTP {code}")

    # --- INFO: settings & monitoring ---
    code, s = get(f"/api/credit-management-api/customers/{key}/settings")
    if code == 200:
        rep.add("INFO", True, "credit settings", f"limit={'unlimited' if s.get('unlimited') else s.get('maximumLimit')} billing={s.get('billingCountry')}")
    code, m = get(f"/api/assets-api/customers/{key}/monitoring")
    if code == 200:
        mods = m.get("monitoring", []); on = sum(1 for x in mods if x.get("limit", {}).get("isMonitoringEnabled"))
        rep.add("INFO", on == len(mods), "monitoring modules enabled", f"{on}/{len(mods)}")

    print(f"\n{'✅ VALIDATION PASSED' if rep.critical_failures == 0 else '❌ VALIDATION FAILED'}: "
          f"{rep.critical_failures} critical failure(s), {len(rep.rows)} checks", flush=True)
    sys.exit(0 if rep.critical_failures == 0 else 1)


if __name__ == "__main__":
    main()
