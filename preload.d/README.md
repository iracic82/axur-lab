# preload.d — extra per-tenant preload scripts

Anything that does not fit the declarative `tenant_preload.yml` goes here as a script. The challenge-2
setup script runs every file in this folder **in name order** after `preload_tenant.py`, so prefix
names with a number: `10-keyword-library.py`, `20-seed-tickets.sh`, ...

Rules:

- `.py` files run with `python3`, `.sh` files with `bash`, anything else must be executable.
- Working directory is `/root/lab/axur-lab`: read the tenant from `tenant_key.txt` / `tenant_name.txt`.
- `AXUR_TOKEN`, `AXUR_BASE_URL` (optional) and the `INSTRUQT_*` variables are in the environment;
  `from axur_api import AxurTenantAPI` gives you the client and `.env` loading for local runs.
- Be idempotent: challenges can be restarted. Check before creating; treat 409 as "already there".
- Exit non-zero only if the lab cannot continue; otherwise log a warning and exit 0.

Delivery: commit + push to this repo. The sandbox does `git pull` at challenge start — no track push needed.

Minimal template:

```python
#!/usr/bin/env python3
import os, requests
from axur_api import AxurTenantAPI          # loads .env for local runs

key = open("tenant_key.txt").read().strip()
api = AxurTenantAPI(os.environ.get("AXUR_BASE_URL", "https://api.axur.com/gateway/1.0"), os.environ["AXUR_TOKEN"])
r = requests.get(f"{api.base_url}/api/assets-api/assets", headers=api._headers(), params={"customerKey": key, "perPage": 100}, timeout=60)
print(f"tenant {key}: {len(r.json().get('assets', []))} asset(s)")
```
