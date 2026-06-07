**Install**

Run the installer once as root:

```bash
cd /path/to/whos-next
sudo ./install.sh
```

This same command works from a flash drive copy of the folder too:

```bash
cd /media/.../whos-next
sudo ./install.sh
```

This does the following:

- Copies the app into `/opt/whos-next`
- Creates `/opt/whos-next/.venv`
- Installs `PyQt6` and `pypdf`
- If a bundled `vendor/` directory exists, installs dependencies fully offline from that directory
- Installs a launcher at `/opt/whos-next/run.sh`
- Installs a shared desktop entry at `/usr/local/share/applications/whos-next.desktop`
- Sets the shared directory group to `studentpicker`
- Gives group write access so the in-app auto-update can overwrite `/opt/whos-next/app.py` without sudo
- Adds all existing `/home` users to `studentpicker`
- Installs desktop shortcuts for all existing `/home` users
- Places desktop shortcuts into `/etc/skel` for future users

**How Launching Works**

The desktop file launches:

```bash
/opt/whos-next/run.sh
```

That script starts:

```bash
/opt/whos-next/.venv/bin/python /opt/whos-next/app.py
```

**Auto-Update Notes**

The current app auto-update logic downloads a full zip bundle and overlays the app directory.

That works with this installer because:

- `/opt/whos-next` is group writable
- users in `studentpicker` can write to the app directory
- no sudo is needed during normal app use

Expected release artifact:

- `whos-next.zip`

Recommended bundle contents:

- `app.py`
- `requirements.txt`
- audio files
- icon file
- installer files if you want them refreshed too
- optional `vendor/` wheel cache for offline installs and updates

**Build Release Bundle**

Create the update bundle with:

```bash
cd /path/to/whos-next
./build_release_bundle.sh
```

That creates:

```bash
dist/whos-next.zip
```

Upload that zip to the URL configured in `BUNDLE_URL`.

**Build AppImage**

To create a single-file Linux build for normal users:

```bash
cd /path/to/whos-next
./build_appimage.sh
```

That creates:

```bash
dist/WhosNext-<version>-x86_64.AppImage
```

The script downloads `appimagetool` automatically the first time if it is not already present in `tools/`.

AppImage notes:

- AppImages run without root installation
- the existing in-app zip updater is disabled inside AppImage builds
- publish the AppImage as an extra GitHub Release asset alongside `whos-next.zip`

**Prepare Offline Wheels**

If you want to deploy to many boards without repeated downloads:

```bash
cd /path/to/whos-next
./prepare_offline_vendor.sh
./build_release_bundle.sh
```

That creates a `vendor/` directory containing the required wheels and includes it in `dist/whos-next.zip`.

With `vendor/` present:

- `install.sh` installs dependencies offline
- in-app updates also install dependencies offline from the bundled wheels

**USB / Flash Drive Workflow**

For a board with no setup yet:

1. Prepare a clean USB-ready folder:

```bash
cd /path/to/whos-next
./prepare_usb_bundle.sh
```

2. Copy `dist/whos-next-usb` to the flash drive.
3. On the board, open a terminal in that folder and run:

```bash
cd /media/.../whos-next-usb
sudo ./install.sh
```

Manual alternative:

1. Copy the entire `whos-next` folder to the flash drive.
2. Make sure that folder includes:
   `app.py`, `requirements.txt`, `vendor/`, sounds, icon, installer scripts.
2. Plug the flash drive into the board.
3. Open a terminal on the board and run:

```bash
cd /media/.../whos-next
sudo ./install.sh
```

After it finishes:

- the app is installed to `/opt/whos-next`
- all existing `/home` users are enrolled automatically
- desktop launchers are created automatically
- dependencies install from the bundled wheels offline

If `requirements.txt` changes, the app will also run:

```bash
/opt/whos-next/.venv/bin/pip install -r /opt/whos-next/requirements.txt
```

after unpacking the update.

If `vendor/` exists and contains wheels, the update uses:

```bash
/opt/whos-next/.venv/bin/pip install --no-index --find-links /opt/whos-next/vendor -r /opt/whos-next/requirements.txt
```
