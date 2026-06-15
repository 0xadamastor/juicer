@echo off
setlocal EnableDelayedExpansion
title Juice Shop - Start

echo.
echo  =====================================================
echo   OWASP Juice Shop - Start
echo  =====================================================
echo.

echo  Checking Docker daemon...
docker info >nul 2>&1
if %ERRORLEVEL% EQU 0 goto DOCKER_OK

echo  [WARN] Docker daemon not running. Attempting to start...
if exist "C:\Program Files\Docker\Docker\Docker Desktop.exe" (
    start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    goto DAEMON_WAIT
)
if exist "C:\Program Files (x86)\Docker\Docker\Docker Desktop.exe" (
    start "" "C:\Program Files (x86)\Docker\Docker\Docker Desktop.exe"
    goto DAEMON_WAIT
)
net start com.docker.service >nul 2>&1

:DAEMON_WAIT
echo  Waiting for Docker to be ready...
set /a WAIT=0
:DAEMON_LOOP
timeout /t 3 /nobreak >nul
docker info >nul 2>&1
if %ERRORLEVEL% EQU 0 goto DOCKER_OK
set /a WAIT+=1
if !WAIT! GEQ 10 (
    echo  [ERROR] Docker did not respond. Open Docker Desktop manually and retry.
    exit /b 1
)
goto DAEMON_LOOP

:DOCKER_OK
docker ps --filter "name=juiceshop" --format "{{.Names}}" 2>nul | findstr /i "juiceshop" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo  [OK] Juice Shop already running at http://localhost:3000
    timeout /t 2 /nobreak >nul
    start http://localhost:3000
    exit /b 0
)

docker ps -a --filter "name=juiceshop" --format "{{.Names}}" 2>nul | findstr /i "juiceshop" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo  Found existing stopped container, starting it...
    docker start juiceshop >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        echo  [ERROR] Could not start existing container.
        exit /b 1
    )
) else (
    echo  Creating and starting container...
    docker run -d -p 3000:3000 --name juiceshop -v juiceshop-data:/juice-shop/data bkimminich/juice-shop >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        echo  [ERROR] Could not start container.
        echo  Check if port 3000 is in use: netstat -ano ^| findstr :3000
        exit /b 1
    )
)

echo  Waiting for server to be ready...
set /a RETRIES=0
:WAIT_SERVER
timeout /t 2 /nobreak >nul
curl -s -o nul -w "%%{http_code}" http://localhost:3000 2>nul | findstr "200 302" >nul 2>&1
if %ERRORLEVEL% EQU 0 goto READY
set /a RETRIES+=1
if !RETRIES! GEQ 20 (
    echo  [WARN] Server is taking longer than expected, opening browser anyway...
    goto READY
)
<nul set /p "=."
goto WAIT_SERVER

:READY
echo.
echo.
echo  =====================================================
echo   [OK] Juice Shop is ready at http://localhost:3000
echo  =====================================================
echo.
timeout /t 1 /nobreak >nul
start http://localhost:3000
