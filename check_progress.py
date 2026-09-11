#!/usr/bin/env python3
"""
Check what the participant DID in their tenant, by reading it back from the Axur API.
Used by the Instruqt challenge check script (exit 0 = pass, exit 1 = fail with a message).

Checks:
  --sample-decision   The seeded "Netflix Golden" fake-profile ticket has left the Potential threats tab
                      (participant sent it to Quarantine, escalated it as an Incident, or discarded it).
                      Verified via GET /tickets-api/tickets?...&current.status=<tab> and the ticket history.

Usage:  python3 check_progress.py --sample-decision        (tenant from tenant_key.txt)
        python3 check_progress.py --key OSMR --sample-decision

Verifiable through the API (for future checks): ticket tab changes (open/quarantine/incident/treatment/closed),
ticket history actions, takedown requests, safelist items, EASM seeds, manually created tickets.
NOT verifiable (UI only): keyword libraries, filtering rules, search bots, CTI monitoring rules, executive details.
"""

import os
import sys
import argparse
import requests

from axur_api import AxurTenantAPI  # noqa: F401  (.env side effect)

BASE_URL = os.environ.get("AXUR_BASE_URL", "https://api.axur.com/gateway/1.0").rstrip("/")
TOKEN = os.environ.get("AXUR_TOKEN")
SAMPLE_REF = os.environ.get("AXUR_SAMPLE_TICKET_REF", "https://www.facebook.com/netflix.golden.lab.sample")
TABS = ("open", "quarantine", "incident", "treatment", "closed")   # current.status values (open = Potential threats)


def get(path, **params):
    r = requests.get(f"{BASE_URL}{path}", headers={"Authorization": f"Bearer {TOKEN}", "Accept": "application/json"},
                     params=params, timeout=60)
    try:
        return r.status_code, r.json()
    except ValueError:
        return r.status_code, {}


def configured_brand_name():
    """Name of the first BRAND asset in tenant_preload.yml (next to this script), or None."""
    try:
        import yaml
        cfg = yaml.safe_load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "tenant_preload.yml"))) or {}
        return next((a.get("name") for a in cfg.get("assets", []) or [] if a.get("type") == "BRAND"), None)
    except Exception:
        return None


def find_sample(key):
    """Return (ticketKey, tab) for the seeded sample ticket, searching every tab of the brand asset."""
    code, body = get("/api/assets-api/assets", customerKey=key, perPage=100)
    brands = [a for a in body.get("assets", []) if a.get("type") == "BRAND"] if code == 200 else []
    # The brand the sample ticket hangs on: the one configured in tenant_preload.yml if present, else the only brand.
    wanted = configured_brand_name()
    brand = next((a["assetKey"] for a in brands if a.get("name") == wanted), None) or (brands[0]["assetKey"] if brands else None)
    if not brand:
        return None, None
    for tab in TABS:
        page = 1
        while page <= 5:
            code, body = get("/api/tickets-api/tickets", assets=brand, pageSize=200, page=page, include="fields", **{"current.status": tab})
            items = body.get("tickets", []) if code == 200 else []
            for t in items:
                if (t.get("ticket") or {}).get("reference") == SAMPLE_REF:
                    return (t.get("ticket") or {}).get("ticketKey"), tab
            if len(items) < 200:
                break
            page += 1
    return None, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--key")
    ap.add_argument("--sample-decision", action="store_true")
    args = ap.parse_args()
    if not TOKEN:
        print("AXUR_TOKEN is not set", flush=True); sys.exit(2)
    key = args.key or (open("tenant_key.txt").read().strip() if os.path.exists("tenant_key.txt") else None)
    if not key:
        print("no tenant key", flush=True); sys.exit(2)

    if args.sample_decision:
        tk, tab = find_sample(key)
        if not tk:
            print("FAIL: the Netflix Golden sample ticket (reference facebook.com/netflix.golden.lab.sample) was not found on this tenant.", flush=True); sys.exit(1)
        code, hist = get(f"/api/tickets-api/ticket-history/{tk}")
        actions = [a.get("type") for a in (hist.get("actions", []) if code == 200 else [])]
        if tab == "open":
            print(f"FAIL: sample ticket {tk} is still in Potential threats (history: {actions}).", flush=True)
            sys.exit(1)
        print(f"PASS: sample ticket {tk} is now in '{tab}' (history: {actions}).", flush=True)
        sys.exit(0)

    print("nothing to check (pass a check flag)", flush=True)
    sys.exit(0)


if __name__ == "__main__":
    main()
