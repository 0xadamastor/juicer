#!/usr/bin/env bash
set -euo pipefail

echo
echo " ====================================================="
echo "  OWASP Juice Shop - Initial Setup"
echo " ====================================================="
echo

echo "[1/3] Checking Docker..."
if ! command -v docker &>/dev/null; then
    echo
    echo " [ERROR] Docker not found."
    echo " Install Docker Engine: https://docs.docker.com/engine/install/"
    echo " Or Docker Desktop:     https://www.docker.com/products/docker-desktop/"
    echo
    exit 1
fi
echo " [OK] Docker found."

echo "[2/3] Checking Docker daemon..."
if ! docker info &>/dev/null; then
    echo " [WARN] Docker daemon not running. Attempting to start..."
    sudo systemctl start docker >/dev/null 2>&1 || true

    RETRIES=0
    while ! docker info &>/dev/null; do
        sleep 2
        RETRIES=$((RETRIES + 1))
        if [[ $RETRIES -ge 10 ]]; then
            echo " [ERROR] Docker daemon is not running."
            echo " Start it with:  sudo systemctl start docker"
            echo " Or add yourself to the docker group and re-login:"
            echo "   sudo usermod -aG docker \$USER"
            exit 1
        fi
        printf "."
    done
    echo
fi
echo " [OK] Docker daemon is running."

echo "[3/3] Pulling Juice Shop image..."
echo " (First run is ~300MB, may take a few minutes)"
echo
docker pull bkimminich/juice-shop

echo
echo " ====================================================="
echo "  [OK] Setup complete."
echo "  Run start.sh or use the GUI to launch Juice Shop."
echo " ====================================================="
echo
