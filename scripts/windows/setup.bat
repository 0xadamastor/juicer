@echo off
setlocal EnableDelayedExpansion
title Juice Shop - Setup

echo.
echo  =====================================================
echo   OWASP Juice Shop - Initial Setup
echo  =====================================================
echo.

echo [1/3] Checking Docker...
docker --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo  [ERROR] Docker not found.
    echo  Install Docker Desktop: https://www.docker.com/products/docker-desktop/
    echo  Or Docker Engine CLI:   https://docs.docker.com/engine/install/
    echo.
    exit /b 1
)
echo  [OK] Docker found.

echo [2/3] Checking Docker daemon...
docker info >nul 2>&1
if %ERRORLEVEL% EQU 0 goto DAEMON_READY

echo  [WARN] Docker daemon not running. Attempting to start...
if exist "C:\Program Files\Docker\Docker\Docker Desktop.exe" (
    start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    goto DAEMON_WAIT
)
if exist "C:\Program Files (x86)\Docker\Docker\Docker Desktop.exe" (
    start "" "C:\Program Files (x86)\Docker\Docker\Docker Desktop.exe"
    goto DAEMON_WAIT
)
echo  [WARN] Docker Desktop not found. Trying Windows service...
net start com.docker.service >nul 2>&1

:DAEMON_WAIT
echo  Waiting for Docker to be ready...
set /a WAIT=0
:DAEMON_LOOP
timeout /t 3 /nobreak >nul
docker info >nul 2>&1
if %ERRORLEVEL% EQU 0 goto DAEMON_READY
set /a WAIT+=1
if !WAIT! GEQ 10 (
    echo  [ERROR] Docker did not start in time. Open Docker Desktop manually and retry.
    exit /b 1
)
goto DAEMON_LOOP

:DAEMON_READY
echo  [OK] Docker daemon is running.

echo [3/3] Pulling Juice Shop image...
echo  (First run is ~300MB, may take a few minutes)
echo.
docker pull bkimminich/juice-shop
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo  [ERROR] Image pull failed. Check your internet connection.
    exit /b 1
)

echo.
echo  =====================================================
echo   [OK] Setup complete.
echo   Run start.bat or use the GUI to launch Juice Shop.
echo  =====================================================
echo.
