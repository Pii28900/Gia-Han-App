@echo off
cd /d "%~dp0"
where pyw >nul 2>nul
if not errorlevel 1 (
 start "" pyw -3 desktop.py
 exit /b
)
where pythonw >nul 2>nul
if not errorlevel 1 (
 start "" pythonw desktop.py
 exit /b
)
echo Can cai Python 3.12+ tu python.org va chon Add Python to PATH.
echo Sau do bam lai Start-Windows.bat.
pause
