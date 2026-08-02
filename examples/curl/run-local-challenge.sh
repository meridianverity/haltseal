#!/usr/bin/env bash
set -euo pipefail
BASE="${HALTSEAL_BASE_URL:-http://127.0.0.1:8787/haltseal/evaluation/v1}"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
curl -fsS -H 'Content-Type: application/json' -d '{"profile":"payment.one-time-purchase.v1"}' "$BASE/challenges" > "$TMP/challenge.json"
TOKEN="$(python -c 'import json,sys; print(json.load(open(sys.argv[1]))["challenge_token"])' "$TMP/challenge.json")"
python - "$TOKEN" > "$TMP/resolve.json" <<'PY'
import json,sys
print(json.dumps({"challenge_token":sys.argv[1],"action":{"amount_minor":25000,"currency":"USD","merchant_id":"merchant_synthetic_alpha","terms":"ONE_TIME","destination_id":"account_synthetic_a"}}))
PY
curl -fsS -D "$TMP/headers.txt" -H 'Content-Type: application/json' -H 'Idempotency-Key: curl-local-challenge-0001' --data-binary @"$TMP/resolve.json" "$BASE/resolve" > "$TMP/response.json"
cat "$TMP/response.json" | python -m json.tool
RECEIPT="$(python -c 'import json,sys; print(json.load(open(sys.argv[1]))["receipt"]["jws"])' "$TMP/response.json")"
printf '%s\n' "$RECEIPT" > "$TMP/receipt.jws"
curl -fsS "$BASE/jwks.json" > "$TMP/jwks.json"
PYTHONPATH="$(cd "$(dirname "$0")/../.." && pwd)" python -m haltseal_resolve.cli verify "$TMP/receipt.jws" --jwks "$TMP/jwks.json"
echo "Idempotent retry header:"
curl -fsS -D - -o /dev/null -H 'Content-Type: application/json' -H 'Idempotency-Key: curl-local-challenge-0001' --data-binary @"$TMP/resolve.json" "$BASE/resolve" | grep -i 'X-HALTSEAL-Idempotent-Replayed'
