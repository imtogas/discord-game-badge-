@echo off
cd /d "%~dp0"
py -m pip install pyinstaller
if errorlevel 1 goto fail
py -m PyInstaller --noconfirm --clean --onefile --windowed --name SteamDiscordLauncher app.py
if errorlevel 1 goto fail
echo Built dist\SteamDiscordLauncher.exe
pause
exit /b 0
:fail
echo Build failed. Install Python and the py launcher.
pause
exit /b 1
