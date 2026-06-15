#!/usr/bin/env bash
set -euo pipefail

echo
echo " ====================================================="
echo "  OWASP Juice Shop - Start"
echo " ====================================================="
echo

echo " Checking Docker daemon..."
if ! docker info &>/dev/null; then
    echo " [ERROR] Docker daemon is not running."
    echo " Start it with:  sudo systemctl start docker"
    exit 1
fi

if docker ps --filter "name=juiceshop" --format "{{.Names}}" 2>/dev/null | grep -qi "juiceshop"; then
    echo " [OK] Juice Shop is already running at http://localhost:3000"
    sleep 1
    xdg-open http://localhost:3000 &>/dev/null || true
    exit 0
fi

if docker ps -a --filter "name=juiceshop" --format "{{.Names}}" 2>/dev/null | grep -qi "juiceshop"; then
    echo " Found existing stopped container, starting it..."
    docker start juiceshop >/dev/null
else
    echo " Creating and starting container..."
    docker run -d -p 3000:3000 --name juiceshop -v juiceshop-data:/juice-shop/data bkimminich/juice-shop
fi

echo " Waiting for server to be ready..."
RETRIES=0
while true; do
    sleep 2
    CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 2>/dev/null || true)
    if [[ "$CODE" == "200" || "$CODE" == "302" ]]; then
        break
    fi
    RETRIES=$((RETRIES + 1))
    if [[ $RETRIES -ge 20 ]]; then
        echo " [WARN] Server is taking longer than expected but may still be starting..."
        break
    fi
    printf "."
done

echo
echo
echo " ====================================================="
echo "  [OK] Juice Shop is ready at http://localhost:3000"
echo " ====================================================="
echo
sleep 1
xdg-open http://localhost:3000 &>/dev/null || \
    python3 -m webbrowser http://localhost:3000 &>/dev/null || \
    echo " Open http://localhost:3000 in your browser."
