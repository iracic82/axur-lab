#!/usr/bin/env python3
"""
Instruqt User Provisioning for an Axur MSSP sub-tenant

Uses the endpoint Axur engineering added for the Infoblox Exchange event:
  POST /api/identity/registration/users/{customer}
  body: {"email", "password", "firstName", "lastName", "groupKey": "manager" | "viewer"}
  200 created · 400 invalid input · 403 token not allowed for that customer
Notes from Axur: temporary, non-public, limited to sub-tenants of root tenant IE2L; the token must belong
to a manager of IE2L (the lab API key does). There is NO delete endpoint yet.

Reads the tenant created by create_tenant.py (tenant_key.txt / tenant_name.txt), builds the participant's
login email, generates a strong password, registers the user on the tenant and saves the credentials for
the Instruqt setup script to expose.

Usage in Instruqt (setup script, AFTER create_tenant.py):
  python3 user_provision.py

  # Cleanup script (no-op until Axur provides a delete endpoint; set AXUR_USER_DELETE_PATH then):
  python3 user_provision.py --delete

Environment Variables:
  AXUR_TOKEN               - Required. API key of an IE2L manager (MSSP Partner Manager).
  INSTRUQT_PARTICIPANT_ID  - Required. Unique per student; becomes the email local part / last name.
  USER_DOMAIN              - Domain for the login email (default: infoblox.lab)
  AXUR_USER_GROUP          - groupKey: manager (default) | viewer
  AXUR_USER_FIRSTNAME      - firstName (default: Lab)
  AXUR_USER_LASTNAME       - lastName  (default: the participant id)
  AXUR_BASE_URL            - Gateway base (default: https://api.axur.com/gateway/1.0)
  AXUR_USER_CREATE_PATH    - override (default: /api/identity/registration/users/{key})
  AXUR_USER_DELETE_PATH    - none by default; "{key}" and "{user_id}" placeholders when Axur adds one

Input Files (from create_tenant.py):   tenant_key.txt, tenant_name.txt
Output Files:  user_email.txt, user_password.txt, user_id.txt, user_credentials.sh

Idempotent: if user_id.txt already holds a created user, the existing credentials are kept and nothing is
sent (challenge restarts). If the endpoint answers 404/405 the script falls back to "PENDING" mode
(files written, no user) and exits 0, so the lab setup never breaks on a withdrawn endpoint.
"""

import os
import sys
import time
import random
import string
import requests

from axur_api import AxurTenantAPI  # noqa: F401  (import for the .env side effect)

PENDING = "PENDING"


def generate_password(length=16):
    """Strong password: uppercase, lowercase, digits and several special characters."""
    upper = random.choices(string.ascii_uppercase, k=3)
    lower = random.choices(string.ascii_lowercase, k=5)
    digits = random.choices(string.digits, k=4)
    specials = random.choices("!@#$%&", k=4)
    password = upper + lower + digits + specials
    random.shuffle(password)
    return "".join(password)


def read_file(filename, required=True):
    try:
        with open(filename, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        if required:
            print(f"❌ {filename} not found. Run create_tenant.py first.", flush=True)
            sys.exit(1)
        return None


def headers(token):
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json", "Accept": "application/json"}


def extract_id(obj):
    """Axur returns ids as {"value": 30968}; accept that, a plain scalar, or nested user/id shapes."""
    if not isinstance(obj, dict):
        return str(obj) if obj not in (None, "") else None
    for k in ("id", "userId", "user_id"):
        if k in obj:
            v = obj[k]
            if isinstance(v, dict):
                v = v.get("value") or v.get("id")
            return str(v) if v not in (None, "") else None
    if isinstance(obj.get("user"), dict):
        return extract_id(obj["user"])
    if "value" in obj:
        return str(obj["value"])
    return None


def get_user_by_email(base_url, hdrs, tenant_key, email):
    """Documented GET /identity/users filtered by customer; returns the user dict or None."""
    try:
        resp = requests.get(
            f"{base_url}/api/identity/users",
            headers=hdrs,
            params={"customers": tenant_key, "freeText": email, "pageSize": 50},
            timeout=60,
        )
        if resp.status_code != 200:
            return None
        body = resp.json()
        users = body if isinstance(body, list) else body.get("users") or body.get("results") or []
        for u in users:
            if not isinstance(u, dict):
                continue
            mail = u.get("email") or (u.get("credentials") or {}).get("email") or ""
            if str(mail).lower() == email.lower():
                return u
    except (requests.RequestException, ValueError):
        pass
    return None


def register_user(base_url, hdrs, path, tenant_key, email, password, first, last, group):
    """
    POST /api/identity/registration/users/{customer}
    Returns (user_id_or_None, status) with status in: created | exists | pending | error
    """
    endpoint = f"{base_url}{path.format(key=tenant_key)}"
    payload = {"email": email, "password": password, "firstName": first, "lastName": last, "groupKey": group}

    for attempt in range(5):
        try:
            resp = requests.post(endpoint, headers=hdrs, json=payload, timeout=60)
            text = resp.text[:300]
            if resp.status_code in (404, 405):
                print(f"  ⚠️ {resp.status_code} from {endpoint} — registration endpoint not available (placeholder mode)", flush=True)
                return None, "pending"
            if resp.status_code == 409 or (resp.status_code == 400 and ("exist" in text.lower() or "already" in text.lower())):
                print(f"  ⚠️ User already registered ({resp.status_code}): {text}", flush=True)
                return None, "exists"
            if resp.status_code == 403:
                print(f"  ❌ 403: token is not allowed to register users for tenant {tenant_key} "
                      f"(needs an IE2L manager token; tenant must be a sub-tenant of IE2L)", flush=True)
                return None, "error"
            if resp.status_code == 400:
                print(f"  ❌ 400 invalid input: {text}", flush=True)
                return None, "error"
            if resp.status_code >= 500 or resp.status_code in (408, 429):
                raise requests.RequestException(f"HTTP {resp.status_code}: {text}")
            if resp.status_code not in (200, 201, 202):
                print(f"  ❌ HTTP {resp.status_code}: {text}", flush=True)
                return None, "error"
            body = {}
            if resp.content:
                try:
                    body = resp.json()
                except ValueError:
                    body = {}
            return extract_id(body), "created"
        except (requests.RequestException, ValueError) as e:
            print(f"  ⚠️ Attempt {attempt + 1} failed: {e}", flush=True)
            time.sleep((2 ** attempt) + random.random())
    return None, "error"


def delete_user(base_url, hdrs, path, tenant_key, user_id):
    """Only if Axur provides an endpoint (AXUR_USER_DELETE_PATH). Returns True on success or if absent."""
    endpoint = f"{base_url}{path.format(key=tenant_key, user_id=user_id)}"
    try:
        resp = requests.delete(endpoint, headers=hdrs, timeout=60)
    except requests.RequestException as e:
        print(f"  ❌ {e}", flush=True)
        return False
    if resp.status_code in (200, 202, 204):
        return True
    if resp.status_code in (404, 405):
        print(f"  ⚠️ {resp.status_code} from {endpoint} — nothing to delete", flush=True)
        return True
    print(f"  ❌ HTTP {resp.status_code}: {resp.text[:300]}", flush=True)
    return False


def save_credentials(user_email, user_password, user_id, tenant_key, tenant_name):
    for filename, value in {"user_email.txt": user_email, "user_password.txt": user_password, "user_id.txt": user_id}.items():
        with open(filename, "w") as f:
            f.write(value)
    os.chmod("user_password.txt", 0o600)
    with open("user_credentials.sh", "w") as f:
        f.write("#!/bin/bash\n# Auto-generated by user_provision.py\n")
        f.write(f"export AXUR_USER_EMAIL='{user_email}'\n")
        f.write(f"export AXUR_USER_PASSWORD='{user_password}'\n")
        f.write(f"export AXUR_USER_ID='{user_id}'\n")
        f.write(f"export AXUR_TENANT_KEY='{tenant_key}'\n")
        f.write(f"export AXUR_TENANT_NAME='{tenant_name}'\n")
    os.chmod("user_credentials.sh", 0o600)


def summary(title, tenant_name, tenant_key, user_email, user_password, user_id):
    print(f"\n{'='*60}", flush=True)
    print(title, flush=True)
    print(f"   Tenant:   {tenant_name} ({tenant_key})", flush=True)
    print(f"   Email:    {user_email}", flush=True)
    print(f"   Password: {user_password}", flush=True)
    print(f"   User ID:  {user_id}", flush=True)
    print(f"\n   Login at: https://one.axur.com", flush=True)
    print(f"{'='*60}", flush=True)


# ==============================================================
# Main
# ==============================================================
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Register (or delete) the participant user on the sandbox's Axur tenant")
    parser.add_argument("--delete", action="store_true", help="Delete the user instead of creating (needs AXUR_USER_DELETE_PATH)")
    args = parser.parse_args()

    BASE_URL = os.environ.get("AXUR_BASE_URL", "https://api.axur.com/gateway/1.0").rstrip("/")
    TOKEN = os.environ.get("AXUR_TOKEN")
    USER_DOMAIN = os.environ.get("USER_DOMAIN", "infoblox.lab")
    GROUP = os.environ.get("AXUR_USER_GROUP", "manager")
    CREATE_PATH = os.environ.get("AXUR_USER_CREATE_PATH", "/api/identity/registration/users/{key}")
    DELETE_PATH = os.environ.get("AXUR_USER_DELETE_PATH", "")

    if not TOKEN:
        print("❌ AXUR_TOKEN is not set", flush=True)
        sys.exit(1)
    PARTICIPANT_ID = os.environ.get("INSTRUQT_PARTICIPANT_ID")
    if not PARTICIPANT_ID:
        print("❌ INSTRUQT_PARTICIPANT_ID not set", flush=True)
        sys.exit(1)

    tenant_key = read_file("tenant_key.txt")
    tenant_name = read_file("tenant_name.txt", required=False) or tenant_key
    hdrs = headers(TOKEN)

    user_email = f"{PARTICIPANT_ID}@{USER_DOMAIN}"
    first = os.environ.get("AXUR_USER_FIRSTNAME", "Lab")
    last = os.environ.get("AXUR_USER_LASTNAME", PARTICIPANT_ID)

    print(f"📋 Tenant:   {tenant_name} ({tenant_key})", flush=True)
    print(f"📋 User:     {user_email}  ({first} {last}, groupKey={GROUP})", flush=True)
    print()

    # --- DELETE mode ---
    if args.delete:
        user_id = read_file("user_id.txt", required=False)
        if not user_id or user_id == PENDING:
            print("⚠️ No registered user recorded — nothing to delete", flush=True)
            sys.exit(0)
        if not DELETE_PATH:
            print(f"ℹ️ Axur has no user-delete endpoint yet; user {user_email} stays on tenant {tenant_key} (tenant gets suspended).", flush=True)
            sys.exit(0)
        print(f"🗑️ Deleting user {user_email} (ID: {user_id})...", flush=True)
        sys.exit(0 if delete_user(BASE_URL, hdrs, DELETE_PATH, tenant_key, user_id) else 1)

    # --- CREATE mode: idempotent on re-run ---
    existing_id = read_file("user_id.txt", required=False)
    if existing_id and existing_id != PENDING and os.path.exists("user_password.txt"):
        print(f"ℹ️ User already provisioned in this sandbox (ID {existing_id}); keeping existing credentials.", flush=True)
        summary("🎉 User Provisioning (already done)", tenant_name, tenant_key,
                read_file("user_email.txt"), read_file("user_password.txt"), existing_id)
        sys.exit(0)

    user_password = generate_password()
    print(f"👤 Registering user {user_email} on tenant {tenant_key}...", flush=True)
    user_id, status = register_user(BASE_URL, hdrs, CREATE_PATH, tenant_key, user_email, user_password, first, last, GROUP)

    if status == "error":
        print("❌ User registration failed", flush=True)
        sys.exit(1)
    if status == "exists":
        print("❌ User exists on Axur but this sandbox has no saved password for it — cannot continue.", flush=True)
        print("   (A previous sandbox with the same participant id? Use a fresh participant / USER_DOMAIN.)", flush=True)
        sys.exit(1)
    if status == "pending":
        user_id = PENDING
        print("⚠️ PLACEHOLDER: registration endpoint not available — credentials generated but no user exists.", flush=True)
    else:
        if not user_id:  # 200 without an id in the body -> look it up, else fall back to the email as identifier
            found = get_user_by_email(BASE_URL, hdrs, tenant_key, user_email)
            user_id = (extract_id(found) if found else None) or user_email
        print(f"✅ User created (ID: {user_id})", flush=True)

    save_credentials(user_email, user_password, user_id, tenant_key, tenant_name)
    summary("🎉 User Provisioning Complete!" if user_id != PENDING else "🕓 User Provisioning PENDING (placeholder)",
            tenant_name, tenant_key, user_email, user_password, user_id)
