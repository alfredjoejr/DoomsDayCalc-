<#
.SYNOPSIS
    One-click launcher for DoomsDayCalc (FastAPI + Matplotlib backend and Vite + React frontend).
.PARAMETER NoBrowser
    Skip opening http://localhost:5173 in the default browser after startup.
#>
param(
    [switch]$NoBrowser
)

$ErrorActionPreference = 'Stop'

$RootDir = $PSScriptRoot
$BackendDir = Join-Path $RootDir 'backend'
$FrontendDir = Join-Path $RootDir 'frontend'
$VenvDir = Join-Path $BackendDir '.venv'
$VenvPython = Join-Path $VenvDir 'Scripts\python.exe'
$UvicornExe = Join-Path $VenvDir 'Scripts\uvicorn.exe'
$RequirementsFile = Join-Path $BackendDir 'requirements.txt'
$NodeModulesDir = Join-Path $FrontendDir 'node_modules'

Write-Host '=== DoomsDayCalc Enterprise Launcher ===' -ForegroundColor Cyan

# 1. Bootstrap Python backend virtual environment if missing
if (-not (Test-Path $UvicornExe)) {
    Write-Host '[Backend] Creating virtual environment and installing dependencies...' -ForegroundColor Yellow
    if (-not (Test-Path $VenvPython)) {
        & python -m venv $VenvDir
        if ($LASTEXITCODE -ne 0) {
            throw 'Failed to create backend Python virtual environment.'
        }
    }
    & $VenvPython -m pip install -r $RequirementsFile
    if ($LASTEXITCODE -ne 0) {
        throw 'Failed to install backend Python requirements.'
    }
}

# 2. Bootstrap Frontend node_modules if missing
if (-not (Test-Path $NodeModulesDir)) {
    Write-Host '[Frontend] Installing npm packages...' -ForegroundColor Yellow
    Push-Location $FrontendDir
    try {
        & npm install
        if ($LASTEXITCODE -ne 0) {
            throw 'Failed to install frontend npm dependencies.'
        }
    }
    finally {
        Pop-Location
    }
}

# 3. Launch FastAPI + Matplotlib Backend in its own PowerShell window
$BackendCommand = "`$Host.UI.RawUI.WindowTitle = 'DoomsDayCalc - FastAPI Backend :8000'; Set-Location '$BackendDir'; & '$UvicornExe' app.main:app --reload --host 127.0.0.1 --port 8000"
Write-Host '[Backend] Starting FastAPI + Matplotlib on http://127.0.0.1:8000 ...' -ForegroundColor Green
Start-Process powershell.exe -ArgumentList '-NoExit', '-ExecutionPolicy', 'Bypass', '-Command', $BackendCommand

# 4. Launch Vite + React Frontend in its own PowerShell window
$FrontendCommand = "`$Host.UI.RawUI.WindowTitle = 'DoomsDayCalc - Vite Frontend :5173'; Set-Location '$FrontendDir'; npm run dev"
Write-Host '[Frontend] Starting Vite Dev Server on http://localhost:5173 ...' -ForegroundColor Green
Start-Process powershell.exe -ArgumentList '-NoExit', '-ExecutionPolicy', 'Bypass', '-Command', $FrontendCommand

# 5. Wait briefly for backend health check
$BackendReady = $false
for ($i = 0; $i -lt 20; $i++) {
    try {
        $resp = Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/v1/health' -TimeoutSec 1 -ErrorAction Stop
        if ($resp.status -eq 'ok') {
            $BackendReady = $true
            break
        }
    }
    catch {
        Start-Sleep -Milliseconds 500
    }
}

if ($BackendReady) {
    Write-Host '[Health] FastAPI + Matplotlib engine is LIVE.' -ForegroundColor Green
}
else {
    Write-Host '[Health] Backend is still warming up in its window.' -ForegroundColor Yellow
}

Write-Host ''
Write-Host '  Frontend UI:  http://localhost:5173' -ForegroundColor White
Write-Host '  FastAPI Docs: http://127.0.0.1:8000/docs' -ForegroundColor White
Write-Host ''

if (-not $NoBrowser) {
    Start-Process 'http://localhost:5173'
}
