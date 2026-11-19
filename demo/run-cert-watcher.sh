#!/usr/bin/env bash
# Starts cert-watcher with demo certificates whose expiry matches evals/golden.yaml:
#   payments-gateway  5 days   -> CRITICAL
#   customer-portal   20 days  -> WARNING
#   internal-wiki     200 days -> OK
#   expired.badssl.com         -> EXPIRED (public test endpoint)
# Re-run it before an evaluation so the day counts stay in range.
set -euo pipefail

image="${CERT_WATCHER_IMAGE:-ghcr.io/hussain-dhoraji/cert-watcher:latest}"
dir="$(cd "$(dirname "$0")" && pwd)/certs"
mkdir -p "$dir"

make_cert() {
  local name="$1" days="$2"
  openssl req -x509 -newkey ec -pkeyopt ec_paramgen_curve:P-256 -nodes -days "$days" \
    -subj "/CN=${name}.contoso.example" -keyout /dev/null -out "$dir/${name}.crt" 2>/dev/null
}

make_cert payments-gateway 5
make_cert customer-portal 20
make_cert internal-wiki 200

docker rm -f cert-watcher-demo >/dev/null 2>&1 || true
docker run -d --name cert-watcher-demo -p 8080:8080 \
  -v "$dir:/certs:ro" \
  -e CERT_WATCHER_CERTIFICATE_FILES=/certs/payments-gateway.crt,/certs/customer-portal.crt,/certs/internal-wiki.crt \
  -e CERT_WATCHER_ENDPOINTS=expired.badssl.com \
  "$image"

echo "cert-watcher is starting on http://localhost:8080/api/v1/certificates"
