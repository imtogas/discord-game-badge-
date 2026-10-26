# Steam Discord Launcher (experimental)

A Windows desktop prototype that searches the public Steam Store, saves favorites, and launches/stops a tiny mock process with a user-supplied executable filename.

**Important:** This does not run a real game. Discord may not recognize the mock process, and Game Variety badge progress is **not guaranteed**. Activity spoofing may conflict with platform rules.

## Download Windows build

Open **Actions** → **Build Windows EXE** → select a successful run → download the **SteamDiscordLauncher-Windows** artifact. Extract it and run the executable.

## Run from source

Install Python 3.10+ on Windows and run `python app.py`. Tkinter is part of standard Python installations.

## Local build

Double-click `build_windows.bat` with Python installed. Output: `dist/SteamDiscordLauncher.exe`.

## How to use

1. Search for a Steam game and select it.
2. Enter the game's **actual** executable filename (for example, `ExampleGame.exe`); Steam Store search does not provide this.
3. Click **Start mock process**, inspect Discord manually, then **Stop**.
4. Save games to Favorites for reuse.

No Steam/Discord login or token is required. Favorites are stored in `%LOCALAPPDATA%\SteamDiscordLauncher\favorites.json`.

First launch for each executable name compiles a small .NET executable using Windows PowerShell's `Add-Type`; this may fail on some systems. No game data is downloaded.

This prototype has not been tested on Windows in the development environment.
