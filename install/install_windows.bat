@echo off
rem CorridorKey 2.0 for Nuke - Windows installer.
rem Usage: install_windows.bat [--backend D:\CorridorKey2.0] [--nuke-dir %USERPROFILE%\.nuke]
setlocal
set "HERE=%~dp0"
for %%V in (3.12 3.13 3.11 3.10) do (
    py -%%V -c "import sys" >nul 2>&1 && ( py -%%V "%HERE%install_backend.py" %* & goto :end )
)
python -c "import sys" >nul 2>&1 && ( python "%HERE%install_backend.py" %* & goto :end )
echo Python 3.10 - 3.13 was not found. Install it from https://www.python.org and run this again.
:end
pause
