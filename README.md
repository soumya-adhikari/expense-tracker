# Expense Tracker (Offline Desktop)

Simple offline expense tracker desktop application built with Python and Tkinter, using SQLite for local storage.

Features (MVP):
- Add / list / delete expenses
- Categories, notes, payment method
- CSV export

Requirements:
- Python 3.10+ (a virtualenv is recommended)
- Tkinter (bundled with standard Python on Windows)

Quick start:
1. Create and activate a virtual environment (recommended).
2. Install any dependencies (none required for Tkinter/SQLite).
3. Run the app:

```powershell
"c:/Users/Soumya/OneDrive - Soumyadip Sardar/Documents/vs code/.venv/Scripts/python.exe" main.py
```

Project files:
- `main.py` - Tkinter GUI application for desktop
- `db.py` - SQLite helper functions (shared)
- `android_app.py` - Kivy-based Android-compatible UI (needs packaging)
- `expenses.db` - created automatically after first run

Android build notes (Kivy + Buildozer)
-------------------------------------
If you'd like a native Android APK, the easiest path is to port/run the included `android_app.py` using Kivy and build an APK with Buildozer on Linux. On Windows you can use WSL (Ubuntu) or a remote Linux builder. The app already uses the same `db.py` (SQLite) so data model logic is shared.

High-level steps to build an APK (recommended: WSL on Windows):
1. Install WSL2 + Ubuntu and open a shell.
2. Install system deps (example):
	sudo apt update && sudo apt install -y python3-pip python3-venv git zip unzip openjdk-17-jdk
3. Install Buildozer and Android SDK/NDK dependencies (official Buildozer docs have full list).
4. In the project folder inside WSL, create/use a Python venv, install buildozer and kivy:
	python3 -m venv .venv
	source .venv/bin/activate
	pip install --upgrade pip
	pip install buildozer kivy
5. Initialize buildozer in the project (this creates `buildozer.spec`):
	buildozer init
6. Edit `buildozer.spec` to include `requirements = python3,kivy` and ensure `source.include_exts = py,kv,db` or include `db.py`.
7. Build the APK (this downloads Android SDK/NDK and may take a while):
	buildozer -v android debug

When build finishes you'll find an APK under `bin/` which you can install on your Android device.

If you prefer not to set up a local build environment I can:
- Add a GitHub Actions workflow to build the APK in CI and upload artifacts.
- Help you set up WSL + Buildozer with a step-by-step script.

Notes and limitations
- Packaging an APK requires a Linux environment for Buildozer; Windows native Buildozer support is limited.
- The Kivy app stores the SQLite DB in the app working directory on the device; syncing across devices requires explicit sync (cloud or web server).
- The included `android_app.py` is intentionally minimal; we can improve UI/UX, add exports/imports, and polish before packaging.

How to build & distribute via GitHub Releases (automatic)
-------------------------------------------------------
This project includes a GitHub Actions workflow that builds an APK using Buildozer and attaches it to a GitHub Release for each run. To use it:

1. Commit and push this repository to GitHub (create a repository and push your local branch to `main`).

	Example (PowerShell):
```powershell
git init
git add .
git commit -m "Initial expense tracker with CI build"
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repo>.git
git push -u origin main
```

2. Open the repository on GitHub, go to the Actions tab → "Build Android APK" workflow. You can trigger it by pushing to `main` or using "Run workflow".

3. Wait for the workflow to complete (first run may take a long time because it downloads Android SDK/NDK). When it finishes:
	- Open the workflow run and download the APK from the Artifacts section, or
	- Open the repository's Releases page — a Release named like `expense-tracker-apk-<run_number>` will be created with the APK attached.

4. Share the Release URL with your friends; they can download the APK and install it on their Android devices.

Install notes for Android users
-----------------------------
- For Android 8+ you must allow the installer app to install unknown apps (Settings → Apps → select your browser/file manager → Allow install unknown apps).
- For older Android versions, enable "Unknown sources" under Security.
- Sideload the APK (transfer via USB, cloud link, or direct download) and open it to install.

Signing (optional, recommended for stable installs)
-------------------------------------------------
The workflow currently builds a debug APK. If you want a signed release APK that installs without debug warnings and can be published, we can add keystore signing to the workflow.

To sign in CI you'll need to:
- Create a Java keystore (locally) and add it to your repository as an encrypted secret, or store it in a secure location and add the signing commands to the workflow.
- Provide the keystore password and alias as GitHub Secrets and update `buildozer.spec` with signing configuration.

Helper scripts
----------------
I added helper scripts to the `scripts/` folder to create a Java keystore and export it as base64 for use in GitHub Secrets.

- Windows PowerShell: `scripts/generate_keystore_ps.ps1`
	- Run in PowerShell where the JDK is installed. It will create `release.keystore` and `keystore.base64`.

- WSL / Linux: `scripts/generate_keystore_wsl.sh`
	- Run in WSL or Linux with `keytool` available. It will create the same outputs.

After creating `keystore.base64`, copy its contents into the `KEYSTORE_BASE64` secret and add the passwords and alias to the other secrets mentioned earlier.

If you want, I can add signing steps and a secure workflow that uses GitHub Secrets to sign the APK automatically.

License: MIT
