@echo off
cd /d "%~dp0"
echo Starting Relief-Relay warehouse. Keep this window open.
py server.py
if errorlevel 1 python server.py
pause
