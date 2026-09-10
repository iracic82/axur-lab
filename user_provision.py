#!/usr/bin/env python3
"""
Instruqt User Provisioning for an Axur MSSP tenant  — PLACEHOLDER until Axur ships the user API

Reads the tenant created by create_tenant.py (tenant_key.txt / tenant_name.txt), constructs the
participant's login email, generates a strong password, creates the user on the tenant, and saves
the credentials for the Instruqt setup script to expose.

Usage in Instruqt (setup script, AFTER create_tenant.py):
  python3 user_provision.py

  # Delete user (cleanup script, BEFORE delete_tenant.py):
  python3 user_provision.py --delete

Environment Variables:
  AXUR_TOKEN               - Required. API key with MSSP Partner Manager permission.
  INSTRUQT_PARTICIPANT_ID  - Required. Unique per student; becomes the user name / email local part.
  USER_DOMAIN              - Domain for the user email (default: infoblox.lab)
  AXUR_BASE_URL            - Gateway base (default: https://api.axur.com/gateway/1.0)
  AXUR_USER_PERMISSION     - Permission level to request (default: MANAGER)
  AXUR_USER_CREATE_PATH    - Create endpoint, "{key}" = tenant key
                             (default: /api/customers-api/customer/{key}/user)   <-- TO BE CONFIRMED BY AXUR
  AXUR_USER_DELETE_PATH    - Delete endpoint, "{key}" and "{user_id}" placeholders
                             (default: /api/customers-api/customer/{key}/user/{user_id})  <-- TO BE CONFIRMED BY AXUR

Input Files (from create_tenant.py):
  tenant_key.txt        - Axur customer key (e.g. OSMR)
  tenant_name.txt       - Tenant name (= Instruqt sandbox id)

Output Files:
  user_email.txt        - Generated login email
  user_password.txt     - Generated password
  user_id.txt           - Axur user ID for cleanup, or "PENDING" while the API does not exist yet
  user_credentials.sh   - Source-able credentials for bash

Placeholder behaviour: if the create endpoint answers 404/405 (not built yet), the script prints a clear
warning, still writes the files (user_id = PENDING) and exits 0 so the lab setup keeps working.
Cleanup skips deletion for PENDING users.
"""

import os
import sys
import time
import random
import string
import requests

# Loads .env (AXUR_TOKEN) the same way the other scripts do
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


def read_file(filename):
    """Read a single-line txt file, exit if missing."""
    try:
        with open(filename, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        print(f"❌ {filename} not found. Run create_tenant.py first.", flush=True)
        sys.exit(1)


def headers(token):
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json", "Accept": "application/json"}


def get_user_id_by_email(base_url, hdrs, tenant_key, email):
    """Look up an existing user on the tenant via the documented GET /identity/users. Returns id or None."""
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
            if isinstance(u, dict) and str(u.get("email", "")).lower() == email.lower():
                return str(u.get("id") or u.get("userId") or u.get("user_id") or "")
    except (requests.RequestException, ValueError):
        pass
    return None


def create_user(base_url, hdrs, path, tenant_key, name, email, password, permission):
    """
    PLACEHOLDER — Axur is building this endpoint. Payload shape assumed from the createCustomer
    `user` object ({name, email}) plus password and permission level; adjust when Axur confirms.
    Returns (user_id, status): status is "created", "exists" or "pending".
    """
    endpoint = f"{base_url}{path.format(key=tenant_key)}"
    payload = {"name": name, "email": email, "password": password, "permissionLevel": permission}

    for attempt in range(5):
        try:
            resp = requests.post(endpoint, headers=hdrs, json=payload, timeout=60)
            if resp.status_code in (404, 405):
                print(f"  ⚠️ {resp.status_code} from {endpoint} — user API not available yet (placeholder mode)", flush=True)
                return None, "pending"
            if resp.status_code == 409:
                print("  ⚠️ User already exists, looking up ID...", flush=True)
                return get_user_id_by_email(base_url, hdrs, tenant_key, email), "exists"
            if resp.status_code >= 500 or resp.status_code in (408, 429):
                raise requests.RequestException(f"HTTP {resp.status_code}: {resp.text[:200]}")
            if resp.status_code not in (200, 201, 202):
                print(f"  ❌ HTTP {resp.status_code}: {resp.text[:300]}", flush=True)
                return None, "error"
            body = resp.json() if resp.content else {}
            uid = body.get("id") or body.get("userId") or body.get("user_id") or (body.get("user") or {}).get("id") or ""
            uid = str(uid).split("/")[-1] if uid else get_user_id_by_email(base_url, hdrs, tenant_key, email)
            return uid, "created"
        except (requests.RequestException, ValueError) as e:
            print(f"  ⚠️ Attempt {attempt + 1} failed: {e}", flush=True)
            time.sleep((2 ** attempt) + random.random())
    return None, "error"


def delete_user(base_url, hdrs, path, tenant_key, user_id):
    """PLACEHOLDER — delete endpoint to be confirmed by Axur. Returns True on success or if the API is absent."""
    endpoint = f"{base_url}{path.format(key=tenant_key, user_id=user_id)}"
    try:
        resp = requests.delete(endpoint, headers=hdrs, timeout=60)
    except requests.RequestException as e:
        print(f"  ❌ {e}", flush=True)
        return False
    if resp.status_code in (200, 202, 204):
        return True
    if resp.status_code in (404, 405):
        print(f"  ⚠️ {resp.status_code} from {endpoint} — user API not available yet, nothing to delete", flush=True)
        return True
    print(f"  ❌ HTTP {resp.status_code}: {resp.text[:300]}", flush=True)
    return False


# ==============================================================
# Main
# ==============================================================
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Provision or delete the participant user on the sandbox's Axur tenant")
    parser.add_argument("--delete", action="store_true", help="Delete the user instead of creating")
    args = parser.parse_args()

    # --- Config ---
    BASE_URL = os.environ.get("AXUR_BASE_URL", "https://api.axur.com/gateway/1.0").rstrip("/")
    TOKEN = os.environ.get("AXUR_TOKEN")
    USER_DOMAIN = os.environ.get("USER_DOMAIN", "infoblox.lab")
    PERMISSION = os.environ.get("AXUR_USER_PERMISSION", "MANAGER")
    CREATE_PATH = os.environ.get("AXUR_USER_CREATE_PATH", "/api/customers-api/customer/{key}/user")
    DELETE_PATH = os.environ.get("AXUR_USER_DELETE_PATH", "/api/customers-api/customer/{key}/user/{user_id}")

    if not TOKEN:
        print("❌ AXUR_TOKEN is not set", flush=True)
        sys.exit(1)

    PARTICIPANT_ID = os.environ.get("INSTRUQT_PARTICIPANT_ID")
    if not PARTICIPANT_ID:
        print("❌ INSTRUQT_PARTICIPANT_ID not set", flush=True)
        sys.exit(1)

    # --- Read tenant files ---
    tenant_key = read_file("tenant_key.txt")
    tenant_name = read_file("tenant_name.txt")
    hdrs = headers(TOKEN)

    # --- Construct user credentials (participant_id is unique per student) ---
    user_email = f"{PARTICIPANT_ID}@{USER_DOMAIN}"
    user_password = generate_password()

    print(f"📋 Tenant:   {tenant_name} ({tenant_key})", flush=True)
    print(f"📋 User:     {user_email}", flush=True)
    print()

    # --- DELETE mode ---
    if args.delete:
        try:
            user_id = read_file("user_id.txt")
        except SystemExit:
            print("⚠️ user_id.txt missing — nothing to delete", flush=True)
            sys.exit(0)
        if user_id == PENDING:
            print("⚠️ User was never created (placeholder mode) — nothing to delete", flush=True)
            sys.exit(0)
        print(f"🗑️ Deleting user {user_email} (ID: {user_id})...", flush=True)
        if delete_user(BASE_URL, hdrs, DELETE_PATH, tenant_key, user_id):
            print("✅ User deleted", flush=True)
            sys.exit(0)
        print("❌ Delete failed", flush=True)
        sys.exit(1)

    # --- CREATE mode ---
    print(f"👤 Creating user {user_email} on tenant {tenant_key}...", flush=True)
    user_id, status = create_user(BASE_URL, hdrs, CREATE_PATH, tenant_key, PARTICIPANT_ID, user_email, user_password, PERMISSION)

    if status == "error":
        print("❌ User creation failed", flush=True)
        sys.exit(1)
    if status == "pending":
        user_id = PENDING
        print("⚠️ PLACEHOLDER: Axur user API not available yet — credentials generated but no user exists on the tenant.", flush=True)
        print("   Set AXUR_USER_CREATE_PATH / AXUR_USER_DELETE_PATH once Axur publishes the endpoint.", flush=True)
    else:
        user_id = user_id or PENDING
        print(f"✅ User {status} (ID: {user_id})", flush=True)

    # --- Save credentials ---
    files = {
        "user_email.txt": user_email,
        "user_password.txt": user_password,
        "user_id.txt": user_id,
    }
    for filename, value in files.items():
        with open(filename, "w") as f:
            f.write(value)
    os.chmod("user_password.txt", 0o600)

    with open("user_credentials.sh", "w") as f:
        f.write("#!/bin/bash\n")
        f.write("# Auto-generated by user_provision.py\n")
        f.write(f"export AXUR_USER_EMAIL='{user_email}'\n")
        f.write(f"export AXUR_USER_PASSWORD='{user_password}'\n")
        f.write(f"export AXUR_USER_ID='{user_id}'\n")
        f.write(f"export AXUR_TENANT_KEY='{tenant_key}'\n")
        f.write(f"export AXUR_TENANT_NAME='{tenant_name}'\n")
    os.chmod("user_credentials.sh", 0o600)

    # --- Summary ---
    print(f"\n{'='*60}", flush=True)
    print("🎉 User Provisioning Complete!" if user_id != PENDING else "🕓 User Provisioning PENDING (placeholder)", flush=True)
    print(f"   Tenant:   {tenant_name} ({tenant_key})", flush=True)
    print(f"   Email:    {user_email}", flush=True)
    print(f"   Password: {user_password}", flush=True)
    print(f"   User ID:  {user_id}", flush=True)
    print(f"\n   Login at: https://one.axur.com", flush=True)
    print(f"\n   Instruqt:", flush=True)
    print(f"     set-var AXUR_USER_EMAIL '{user_email}'", flush=True)
    print(f"     set-var AXUR_USER_PASSWORD '{user_password}'", flush=True)
    print(f"{'='*60}", flush=True)
