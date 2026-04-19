#!/usr/bin/env bash
# Run as_webapp on port 5002. Execute from the repo root.
set -euo pipefail
cd "$(dirname "$0")/.."
exec python3 -m as_webapp.main
