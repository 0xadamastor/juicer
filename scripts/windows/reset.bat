@echo off
setlocal EnableDelayedExpansion
title Juice Shop - Reset

echo.
echo  =====================================================
echo   OWASP Juice Shop - Full Reset
echo   WARNING: This will wipe all challenge progress!
echo  =====================================================
echo.

docker ps -a --filter "name=juiceshop" --format "{{.Names}}" 2>nul | findstr /i "juiceshop" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo  Stopping container...
    docker stop juiceshop >nul 2>&1
    echo  Removing container...
    docker rm juiceshop >nul 2>&1
) else (
    echo  [INFO] No container found.
)

echo  Removing data volume...
docker volume rm juiceshop-data >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo  [OK] Volume removed.
) else (
    echo  [INFO] No volume found or already removed.
)

echo.
echo  =====================================================
echo   [OK] Reset complete. All progress has been wiped.
echo   Run setup.bat then start.bat to begin fresh.
echo  =====================================================
echo.
