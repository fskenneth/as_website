"""
as_webapp — Astra Staging internal operations server.

Serves:
- Portal HTML frontend (to be migrated from main.py in Phase 2)
- /api/v1/* Bearer-token API for iOS + Android (Phase 1 — done)
- Background Zoho sync tasks (to be migrated in Phase 3)

Run from the repo root (as_website/) so shared imports (tools/, page/)
resolve correctly:

    cd /path/to/as_website
    python3 -m as_webapp.main          # runs on port 5002
    ./as_webapp/run.sh                 # same thing

Why this lives separately from main.py: the public marketing site (main.py
on :5001) must keep serving astrastaging.com even if this ops server is
down for updates.
"""
from fasthtml.common import fast_app
from starlette.responses import JSONResponse

from as_webapp.as_portal_api import routes as portal_api


app, rt = fast_app(live=False)


@rt("/")
def root():
    """Temporary landing — portal web UI arrives in Phase 2."""
    return JSONResponse({
        "service": "as_webapp",
        "status": "ok",
        "phase": 1,
        "notes": "Portal HTML UI not yet migrated. API at /api/v1/*.",
    })


# Register /api/v1/* routes (iOS + Android clients)
portal_api.register(rt)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("as_webapp.main:app", host="0.0.0.0", port=5002, reload=True)
