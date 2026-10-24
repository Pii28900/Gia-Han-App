@echo off
cd /d "%~dp0"
where pyw >nul 2>nul
if not errorlevel 1 (
 start "" pyw -3 browser_app.py
 exit /b
)
where pythonw >nul 2>nul
if not errorlevel 1 (
 start "" pythonw browser_app.py
 exit /b
)
echo Can cai Python 3.12+ tu python.org va chon Add Python to PATH.
echo Ban EXE tren GitHub Actions khong can cai Python.
pause
