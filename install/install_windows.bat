@echo off
rem CorridorKey 2.0 for Nuke - Windows installer.
rem Usage: install_windows.bat [--backend D:\CorridorKey2.0] [--nuke-dir %USERPROFILE%\.nuke]
rem Needs only an NVIDIA GPU driver and internet: Python, conda and ffmpeg are installed privately.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install_windows.ps1" %*
echo.
pause
