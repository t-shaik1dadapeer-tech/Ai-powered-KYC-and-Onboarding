#!/usr/bin/env bash
# Export OpenAPI schema from FastAPI app
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="$ROOT/docs/api/openapi.json"
API_DIR="$ROOT/services/onboarding-api"

mkdir -p "$(dirname "$OUT")"

cd "$API_DIR"
"$API_DIR/.venv/bin/python" - <<'PY'
import json
from app.main import app

schema = app.openapi()
print(json.dumps(schema, indent=2))
PY
> "$OUT"

echo "OpenAPI exported to $OUT"
python3 -c "import json; s=json.load(open('$OUT')); print(f\"paths: {len(s.get('paths',{}))}, title: {s['info']['title']}\")"
