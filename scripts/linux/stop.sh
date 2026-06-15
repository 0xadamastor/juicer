#!/usr/bin/env bash
set -euo pipefail

echo
echo " ====================================================="
echo "  OWASP Juice Shop - Stop"
echo " ====================================================="
echo

if ! docker ps -a --filter "name=juiceshop" --format "{{.Names}}" 2>/dev/null | grep -qi "juiceshop"; then
    echo " [INFO] No Juice Shop container found. Nothing to stop."
    echo
    exit 0
fi

echo " Stopping container..."
docker stop juiceshop >/dev/null 2>&1 || true

echo
echo " ====================================================="
echo "  [OK] Juice Shop stopped."
echo "  Progress is saved in Docker volume juiceshop-data."
echo "  Container kept (use reset.sh to remove it entirely)."
echo " ====================================================="
echo
