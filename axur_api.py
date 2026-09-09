import json
import logging
from logging.handlers import RotatingFileHandler

import os
import requests


def _load_dotenv(path: str | None = None) -> None:
    """Load KEY=VALUE lines from a .env next to this file into os.environ (existing vars win)."""
    path = path or os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if not os.path.isfile(path):
        return
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key, value = key.strip(), value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value


_load_dotenv()

# Setup logging
logger = logging.getLogger("AxurTenantLogger")
logger.setLevel(logging.DEBUG)
handler = RotatingFileHandler("AxurTenant.log", maxBytes=5_000_000, backupCount=2)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

# HTTP status codes worth retrying (transient gateway / server problems)
RETRYABLE_STATUS = {408, 425, 429, 500, 502, 503, 504}


class AxurTenantAPI:
    """
    Manages Axur MSSP customer tenants through the documented public API
    (https://docs.axur.com/en/axur/api/, paths under /gateway/1.0/api/customers-api/).

    Auth: `Authorization: Bearer <API key>`; the key is created in Axur ONE under
    My Preferences -> API KEY and needs the "MSSP Partner Manager" permission.

    Per Axur support (2026-09-09): API keys work only on routes whose path includes the /api prefix;
    the routes the web portal calls (/gateway/1.0/customers/mssp-tenants/...) are portal-only. The
    tenant lifecycle is create + suspend + resume; there is no DELETE. A tenant created through the
    API shows up in the portal only after the admin's session token refreshes (~30 min, then log out
    and back in).
    """

    def __init__(self, base_url: str, token: str, timeout: int = 60):
        self.base_url = base_url.rstrip("/")          # e.g. https://api.axur.com/gateway/1.0
        self.token = token                            # API key; valid only on /api/... routes
        self.timeout = timeout

    # ------------------------------------------------------------------ helpers
    def _headers(self):
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    @staticmethod
    def _body(response):
        """Parse a JSON body if there is one; otherwise return the raw text (may be empty)."""
        if not response.content:
            return {}
        try:
            return response.json()
        except ValueError:
            return response.text

    # ------------------------------------------------------------------ create
    def create_tenant(self, tenant: dict) -> dict:
        """
        POST /api/customers-api/customer  (documented)

        Takes the same flat fields the Axur ONE UI sends and maps them onto the API schema:
          {"partnerKey": "IE2L", "name": "Zoom", "segment": "FINANCIAL_INSURANCE",
           "brandName": "Zoom", "brandOfficialWebsite": "www.zoom.com",
           "ctiEnabled": true, "billingCountry": "AS"}
        ->
          {"customer": {partnerKey, name, segment, ctiEnabled, billingCountry},
           "asset":    {"name": brandName, "website": brandOfficialWebsite}}

        Returns {"status": "success", "data": <json>, "status_code": int} or
                {"status": "failure", "error": str, "retryable": bool, "status_code": int|None}
        The 201 body contains the generated "customerKey" (e.g. "IGRSC").
        """
        endpoint = f"{self.base_url}/api/customers-api/customer"
        customer = {k: tenant[k] for k in ("partnerKey", "name", "segment", "ctiEnabled", "billingCountry")
                    if k in tenant and tenant[k] is not None}
        payload = {"customer": customer}
        asset = {}
        if tenant.get("brandName"):
            asset["name"] = tenant["brandName"]
        if tenant.get("brandOfficialWebsite"):
            asset["website"] = tenant["brandOfficialWebsite"]
        if asset:
            payload["asset"] = asset          # omitted -> API auto-creates a BRAND asset from the name
        if tenant.get("user"):
            payload["user"] = tenant["user"]  # optional {"name", "email"}
        try:
            logger.debug(f"Creating tenant at {endpoint} with payload: {payload}")
            response = requests.post(
                url=endpoint,
                headers=self._headers(),
                data=json.dumps(payload),
                timeout=self.timeout,
            )
            body = self._body(response)
            if response.status_code in (200, 201, 202):
                logger.info(f"Tenant created ({response.status_code}): {json.dumps(body, indent=2)}")
                return {"status": "success", "data": body, "status_code": response.status_code}
            msg = f"HTTP {response.status_code}: {body}"
            logger.error(f"Failed to create tenant: {msg}")
            return {
                "status": "failure",
                "error": msg,
                "retryable": response.status_code in RETRYABLE_STATUS,
                "status_code": response.status_code,
            }
        except requests.RequestException as e:          # timeouts, DNS, connection resets
            logger.error(f"Failed to create tenant: {e}")
            return {"status": "failure", "error": str(e), "retryable": True, "status_code": None}

    # ------------------------------------------------------------------ lookup
    def list_tenants(self) -> list:
        """GET /api/customers-api/customers  (documented) -> list of {name, key, active, suspended, ...}"""
        endpoint = f"{self.base_url}/api/customers-api/customers"
        try:
            logger.debug(f"Listing tenants at {endpoint}")
            response = requests.get(endpoint, headers=self._headers(), timeout=self.timeout)
            response.raise_for_status()
            result = response.json()
            # documented shape is a bare array; tolerate a wrapped one too
            if isinstance(result, dict):
                result = result.get("customers") or result.get("results") or result.get("data") or []
            return result if isinstance(result, list) else []
        except Exception as e:
            logger.error(f"Error listing tenants: {e}")
            return []

    def get_tenant_key_by_name(self, name: str):
        """Return the tenant `key` (customerKey) whose name matches, else None."""
        for tenant in self.list_tenants():
            if isinstance(tenant, dict) and tenant.get("name") == name:
                key = tenant.get("key") or tenant.get("customerKey")
                logger.info(f"Found tenant key: {key} for name: {name}")
                return key
        logger.warning(f"No tenant found with name: {name}")
        return None

    # ------------------------------------------------------------------ suspend / resume (documented)
    def suspend_tenant(self, tenant_key: str) -> dict:
        """POST /api/customers-api/tenant/{key}/suspend  (documented) -> 204 on success"""
        return self._tenant_action(tenant_key, "suspend")

    def resume_tenant(self, tenant_key: str) -> dict:
        """POST /api/customers-api/tenant/{key}/resume  (documented) -> 204 on success"""
        return self._tenant_action(tenant_key, "resume")

    def _tenant_action(self, tenant_key: str, action: str) -> dict:
        endpoint = f"{self.base_url}/api/customers-api/tenant/{tenant_key}/{action}"
        try:
            logger.debug(f"{action} tenant {tenant_key} at {endpoint}")
            response = requests.post(endpoint, headers=self._headers(), timeout=self.timeout)
            if response.status_code in (200, 202, 204):
                logger.info(f"Tenant {tenant_key} {action}d successfully.")
                return {"status": "success", "status_code": response.status_code}
            msg = f"HTTP {response.status_code}: {self._body(response)}"
            logger.error(f"Failed to {action} tenant {tenant_key}: {msg}")
            return {"status": "failure", "error": msg, "status_code": response.status_code}
        except requests.RequestException as e:
            logger.error(f"Error on {action} for tenant {tenant_key}: {e}")
            return {"status": "failure", "error": str(e), "status_code": None}
