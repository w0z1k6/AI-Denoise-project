@echo off
setlocal
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0start-webapp.ps1" %*
if errorlevel 1 (
  echo.
  echo Startup failed. See messages above.
  pause
)
