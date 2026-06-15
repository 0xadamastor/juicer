#!/usr/bin/env bash
set -euo pipefail

echo
echo " ====================================================="
echo "  OWASP Juice Shop - Full Reset"
echo "  WARNING: This will wipe all challenge progress!"
echo " ====================================================="
echo

if docker ps -a --filter "name=juiceshop" --format "{{.Names}}" 2>/dev/null | grep -qi "juiceshop"; then
    echo " Stopping container..."
    docker stop juiceshop >/dev/null 2>&1 || true
    echo " Removing container..."
    docker rm juiceshop >/dev/null 2>&1 || true
else
    echo " [INFO] No container found."
fi

echo " Removing data volume..."
if docker volume rm juiceshop-data >/dev/null 2>&1; then
    echo " [OK] Volume removed."
else
    echo " [INFO] No volume found or already removed."
fi

echo
echo " ====================================================="
echo "  [OK] Reset complete. All progress has been wiped."
echo "  Run setup.sh then start.sh to begin fresh."
echo " ====================================================="
echo
