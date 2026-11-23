@echo off
title AI Job Search - Live Dashboard & Scraper Server
cd /d "%~dp0"
echo =======================================================
echo    AI Job Search: Multi-Portal Daily Vacancy Scanner   
echo =======================================================
echo.
echo Starting local background API server on port 5000...
echo Keep this window open or minimized while using the dashboard.
echo.
start "" "http://127.0.0.1:5000/reports/application-dashboard.html"
python -u tools\live_server.py
if errorlevel 1 (
    echo.
    echo Warning: Server exited. Check if port 5000 is already in use.
    pause
)

