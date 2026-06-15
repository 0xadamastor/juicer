@echo off
setlocal EnableDelayedExpansion
title Juice Shop - Stop

echo.
echo  =====================================================
echo   OWASP Juice Shop - Stop
echo  =====================================================
echo.

docker ps -a --filter "name=juiceshop" --format "{{.Names}}" 2>nul | findstr /i "juiceshop" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo  [INFO] No Juice Shop container found. Nothing to stop.
    echo.
    exit /b 0
)

echo  Stopping container...
docker stop juiceshop >nul 2>&1

echo.
echo  =====================================================
echo   [OK] Juice Shop stopped.
echo   Progress is saved in Docker volume juiceshop-data.
echo   Container kept (use reset.bat to remove it entirely).
echo  =====================================================
echo.
