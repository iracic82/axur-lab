#!/usr/bin/env python3
"""
Per-tenant preload / configuration driver for the Axur Instruqt lab.

Runs the steps declared in tenant_preload.yml against ONE tenant, idempotently, so it can be
re-run safely (challenge restarts, retries). Meant for the challenge-1 setup script; when Axur
tells us what each lab tenant must contain, we edit the YAML — not this script.

Usage:
  python3 preload_tenant.py                       # tenant from tenant_key.txt, config tenant_preload.yml
  python3 preload_tenant.py --key OSMR            # explicit tenant
  python3 preload_tenant.py --config other.yml
  python3 preload_tenant.py --dry-run             # show the calls, send nothing
  python3 preload_tenant.py --undo                # deactivate assets created by a previous run, reset credit limit

Config sections (all optional; see tenant_preload.yml for commented examples):
  credit_limit:  unlimited | <number> | {BRAND_PROTECTION: 100, TAKEDOWN: 10, ...}   (by-product)
  assets:        list of asset payloads for POST /assets-api/customers/{key}/asset
  easm_seeds:    list of domains / IPs / CIDRs for POST /easm/seeds (skipped when already registered with a policy)
  easm_policy:   EASM monitoring policy sent with the seed (default: everything on except port scanning)
  safelist:      list of {group, items[]} for POST /touchpoints/items
  requests:      raw escape hatch: list of {method, path, json?, params?, ok?[]} — "{key}"/"{name}"/"{asset:<asset name>}"
                 placeholders are substituted anywhere in path / json / params.

Environment:
  AXUR_TOKEN (required), AXUR_BASE_URL (default https://api.axur.com/gateway/1.0)

State: preload_state.json records the asset keys this script created (used by --undo).
"""

import os
import sys
import json
import argparse
import requests

from axur_api import AxurTenantAPI  # noqa: F401  (imported for the .env side effect + logger)

BASE_URL = os.environ.get("AXUR_BASE_URL", "https://api.axur.com/gateway/1.0").rstrip("/")
TOKEN = os.environ.get("AXUR_TOKEN")
STATE_FILE = "preload_state.json"


# ------------------------------------------------------------------ helpers
def log(msg):
    print(msg, flush=True)


def load_config(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    try:
        import yaml  # optional dependency; JSON is also valid YAML
        return yaml.safe_load(text) or {}
    except ImportError:
        return json.loads(text) if text.strip() else {}


def substitute(obj, mapping):
    """Replace {key}/{name} placeholders in every string of a nested structure."""
    if isinstance(obj, str):
        for k, v in mapping.items():
            obj = obj.replace("{" + k + "}", str(v))
        return obj
    if isinstance(obj, list):
        return [substitute(x, mapping) for x in obj]
    if isinstance(obj, dict):
        return {k: substitute(v, mapping) for k, v in obj.items()}
    return obj


class Api:
    def __init__(self, base_url, token, dry_run=False):
        self.base_url = base_url
        self.h = {"Authorization": f"Bearer {token}", "Content-Type": "application/json", "Accept": "application/json"}
        self.dry_run = dry_run

    def call(self, method, path, json_body=None, params=None, ok=(200, 201, 202, 204)):
        url = self.base_url + path
        if self.dry_run:
            log(f"   [dry-run] {method} {path} params={params or {}} json={json.dumps(json_body) if json_body else '-'}")
            return 0, {}
        r = requests.request(method, url, headers=self.h, json=json_body, params=params, timeout=60)
        body = {}
        if r.content:
            try:
                body = r.json()
            except ValueError:
                body = {"text": r.text[:300]}
        if r.status_code not in ok:
            log(f"   ❌ {method} {path} -> HTTP {r.status_code}: {json.dumps(body)[:300]}")
        return r.status_code, body


def load_state():
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except (FileNotFoundError, ValueError):
        return {}


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


# ------------------------------------------------------------------ steps
def step_credit_limit(api, key, limit):
    """PATCH /credit-management-api/customers/{key}/limit/{monthlyLimit}; skip if already set."""
    code, cur = api.call("GET", f"/api/credit-management-api/customers/{key}/settings", ok=(200, 0))
    if isinstance(limit, dict):                       # by-product limits
        log(f"💳 credit limit by product: {limit}")
        api.call("PATCH", f"/api/credit-management-api/customers/{key}/limit/by-product", json_body={"limits": limit})
        return
    limit = str(limit)
    if code == 200 and limit == "unlimited" and cur.get("unlimited") is True:
        log("💳 credit limit already unlimited — skip")
        return
    if code == 200 and limit.isdigit() and cur.get("unlimited") is False and str(cur.get("maximumLimit")) == limit:
        log(f"💳 credit limit already {limit} — skip")
        return
    log(f"💳 credit limit -> {limit}")
    api.call("PATCH", f"/api/credit-management-api/customers/{key}/limit/{limit}")


def existing_assets(api, key):
    """All assets of the tenant (API caps perPage at 100, so paginate)."""
    out, page = [], 1
    while True:
        code, body = api.call("GET", "/api/assets-api/assets", params={"customerKey": key, "perPage": 100, "page": page}, ok=(200, 0))
        if code != 200:
            break
        chunk = body.get("assets", [])
        out.extend(chunk)
        if len(chunk) < 100:
            break
        page += 1
    return out


def reactivate(api, existing, asset, created):
    """A deactivated asset cannot be re-created (409); adding monitoring reactivates it (per the spec)."""
    monitoring = asset.get("monitoring") or []
    if not monitoring:
        log(f"   ⚠️ {existing['assetKey']} is INACTIVE and the config has no monitoring to add — left inactive")
        return
    code, body = api.call("PATCH", f"/api/assets-api/assets/{existing['assetKey']}/monitoring/add",
                          json_body={"monitoring": monitoring}, ok=(200, 0))
    if code == 200:
        created.append({"assetKey": existing["assetKey"], "type": existing.get("type"), "name": existing.get("name")})
        log(f"   ♻️  reactivated {existing['assetKey']} (status {body.get('status')}) by adding monitoring {monitoring}")


def step_assets(api, key, assets, state):
    """
    POST /assets-api/customers/{key}/asset for each asset not already present (matched on type+name).
    ACTIVE match -> skip. INACTIVE match (e.g. after --undo) -> reactivate by adding the monitoring.
    """
    have = {}
    for a in existing_assets(api, key):
        have[(a.get("type"), a.get("name"))] = a
    created = state.setdefault("assets", [])
    for asset in assets:
        # TRACKING_TOKEN has no name (backend generates it); identify it by its tokenName property
        ident = (asset.get("type"), asset.get("name") or (asset.get("properties") or {}).get("tokenName"))
        existing = have.get(ident)
        if existing and existing.get("status") != "INACTIVE":
            log(f"🏷️  asset {ident[0]} '{ident[1]}' already exists ({existing.get('status')}) — skip")
            continue
        if existing:
            log(f"🏷️  asset {ident[0]} '{ident[1]}' exists but is INACTIVE — reactivating")
            reactivate(api, existing, asset, created)
            continue
        log(f"🏷️  creating asset {ident[0]} '{ident[1]}' monitoring={asset.get('monitoring', [])}")
        code, body = api.call("POST", f"/api/assets-api/customers/{key}/asset", json_body=asset, ok=(200, 201, 409, 0))
        if code == 409:
            # not in the listing we fetched (or a naming difference): look again and reactivate if it is inactive
            again = {(a.get("type"), a.get("name")): a for a in existing_assets(api, key)}.get(ident)
            if again and again.get("status") == "INACTIVE":
                reactivate(api, again, asset, created)
            else:
                log("   ⚠️ 409 conflict — treated as already existing")
        elif code in (200, 201) and body.get("assetKey"):
            created.append({"assetKey": body["assetKey"], "type": body.get("type"), "name": body.get("name")})
            log(f"   ✅ assetKey {body['assetKey']}")


# EASM monitoring policy applied when a seed is created. Verified 2026-09-14: a seed registered without a policy has no
# monitoring at all (GET /easm/seeds/{id}/policy -> "record not found"), the account policy does not exist until a seed is
# created with one, and a policy cannot be attached to an existing seed afterwards. Mirrors the portal's Monitoring
# setup: everything on except port scanning, which generates traffic against the target and is not needed in a lab.
DEFAULT_EASM_POLICY = {
    "vulnerabilities": {"enabled": True, "cvss_min_threshold": 0, "epss_min_threshold": 0.0, "include_unscored": True, "cisa_kev": False},
    "open_ports": {"enabled": False, "scan_type": "standard", "scanning_ip_mode": "DYNAMIC_IPS", "custom_port_ranges": [], "exclude_ports": []},
    "dns_hygiene": {
        "dangling_cnames": {"enabled": True, "alert_on_non_existent": True, "alert_on_orphaned": True},
        "dmarc_records": {"enabled": True, "alert_on_missing": True, "alert_on_weak": True},
        "spf_records": {"enabled": True, "alert_on_missing": True, "alert_on_weak": True},
        "lame_delegation": {"enabled": True},
        "zone_transfers": {"enabled": True},
        "expiring_domains": {"enabled": True, "alert_on_expired": True, "alert_on_expiring_soon": True, "days_until_expiration": 30},
    },
    "certificates": {"expiring": {"enabled": True, "days_until_expiration": 30}, "self_signed": {"enabled": True},
                     "weak_encryption": {"enabled": True}, "wildcard": {"enabled": True}},
}


def seed_has_policy(api, key, seed_id):
    code, _ = api.call("GET", f"/api/easm/seeds/{seed_id}/policy", params={"axur_tenant_key": key}, ok=(200, 404, 500, 0))
    return code == 200


def step_easm_seeds(api, key, seeds, policy=None):
    """Register EASM seeds together with their monitoring policy, re-creating any seed that has none, then queue discovery."""
    policy = policy or DEFAULT_EASM_POLICY
    code, body = api.call("POST", "/api/easm/seeds/list", json_body={}, params={"axur_tenant_key": key}, ok=(200, 0))
    have = {s.get("seed_name"): s for s in (body.get("results", []) if code == 200 else [])}
    to_create = [s for s in seeds if s not in have]
    for s in seeds:
        if s not in have:
            continue
        sid = have[s].get("id")
        if api.dry_run or seed_has_policy(api, key, sid):
            log(f"🌱 EASM seed '{s}' already registered with a monitoring policy — skip")
        else:
            log(f"🌱 EASM seed '{s}' has no monitoring policy (never scanned) — re-creating it with one")
            api.call("POST", "/api/easm/seeds/remove", json_body={"ids": [sid]}, params={"axur_tenant_key": key}, ok=(200, 204, 0))
            to_create.append(s)
    if to_create:
        log(f"🌱 registering EASM seed(s) {to_create} with monitoring policy")
        api.call("POST", "/api/easm/seeds", json_body={"seed_names": to_create, "description": "Infoblox Exchange lab", "policy": policy},
                 params={"axur_tenant_key": key}, ok=(200, 201, 0))
    # Queue discovery right away. Axur processes it "in the next scheduled cycle" (observed: a day or more), so this
    # only moves the tenant up the queue; 409 means a run is already queued.
    code, body = api.call("POST", "/api/easm/seeds/list", json_body={}, params={"axur_tenant_key": key}, ok=(200, 0))
    ids = [r.get("id") for r in (body.get("results", []) if code == 200 else []) if r.get("seed_name") in seeds and r.get("id")]
    if ids:
        log(f"🌱 queueing EASM discovery for {len(ids)} seed(s)")
        api.call("POST", "/api/easm/seeds/scan", json_body={"ids": ids}, params={"axur_tenant_key": key}, ok=(200, 202, 409, 0))


def step_safelist(api, key, entries):
    """POST /touchpoints/items with customerKey."""
    for e in entries:
        items = [{"content": c} for c in e.get("items", [])]
        log(f"🛡️  safelist group={e.get('group', 'self')} items={len(items)}")
        api.call("POST", "/api/touchpoints/items", json_body={"customerKey": key, "group": e.get("group", "self"), "items": items},
                 ok=(200, 201, 204, 409, 0))


def asset_placeholders(api, key):
    """{asset:<name>} -> asset key, read back from the tenant so nobody has to guess how Axur derives keys."""
    return {f"asset:{a.get('name')}": a.get("assetKey") for a in existing_assets(api, key) if a.get("assetKey")}


def step_requests(api, key, name, reqs):
    """Raw escape hatch: whatever Axur asks us to preload that has no dedicated step yet."""
    mapping = {"key": key, "name": name}
    if any("{asset:" in json.dumps(r) for r in reqs):
        mapping.update(asset_placeholders(api, key))
    for r in reqs:
        r = substitute(r, mapping)
        if "{asset:" in json.dumps(r):
            log(f"⚠️ unresolved asset placeholder in request {r['path']} (asset not found in tenant) — skipping"); continue
        ok = tuple(r.get("ok", [200, 201, 202, 204]))
        log(f"🔧 {r['method'].upper()} {r['path']}")
        api.call(r["method"].upper(), r["path"], json_body=r.get("json"), params=r.get("params"), ok=ok + (0,))


def undo(api, key, state):
    for a in state.get("assets", []):
        log(f"↩️  deactivating asset {a.get('assetKey')} ({a.get('type')} '{a.get('name')}')")
        api.call("PUT", f"/api/assets-api/assets/{a['assetKey']}/deactivate", ok=(200, 204, 404, 0))
    log("↩️  credit limit -> unlimited")
    api.call("PATCH", f"/api/credit-management-api/customers/{key}/limit/unlimited", ok=(200, 204, 0))
    if not api.dry_run:
        save_state({})


# ------------------------------------------------------------------ main
if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Preload / configure one Axur tenant from tenant_preload.yml")
    p.add_argument("--key", help="tenant key (default: tenant_key.txt)")
    p.add_argument("--config", default="tenant_preload.yml")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--undo", action="store_true", help="deactivate assets created earlier and reset the credit limit")
    args = p.parse_args()

    if not TOKEN:
        log("❌ AXUR_TOKEN is not set"); sys.exit(1)

    key = args.key
    if not key:
        try:
            key = open("tenant_key.txt").read().strip()
        except FileNotFoundError:
            log("❌ tenant_key.txt not found — run create_tenant.py first or pass --key"); sys.exit(1)
    try:
        name = open("tenant_name.txt").read().strip()
    except FileNotFoundError:
        name = key

    api = Api(BASE_URL, TOKEN, dry_run=args.dry_run)
    state = load_state()

    if args.undo:
        log(f"↩️  Undo preload on tenant {key}")
        undo(api, key, state)
        log("✅ undo complete"); sys.exit(0)

    try:
        cfg = load_config(args.config)
    except FileNotFoundError:
        log(f"⚠️ {args.config} not found — nothing to preload"); sys.exit(0)
    cfg = substitute(cfg, {"key": key, "name": name})

    log(f"🚀 Preload tenant {key} ({name}) from {args.config}{' [dry-run]' if args.dry_run else ''}")
    planned = [s for s in ("credit_limit", "assets", "easm_seeds", "safelist", "requests") if cfg.get(s)]
    if not planned:
        log("ℹ️ nothing to preload (all sections empty) — placeholder in place, edit tenant_preload.yml when specs arrive")
        sys.exit(0)

    if cfg.get("credit_limit") is not None:
        step_credit_limit(api, key, cfg["credit_limit"])
    if cfg.get("assets"):
        step_assets(api, key, cfg["assets"], state)
    if cfg.get("easm_seeds"):
        step_easm_seeds(api, key, cfg["easm_seeds"], cfg.get("easm_policy"))
    if cfg.get("safelist"):
        step_safelist(api, key, cfg["safelist"])
    if cfg.get("requests"):
        step_requests(api, key, name, cfg["requests"])

    if not args.dry_run:
        save_state(state)
    log("✅ preload complete")
