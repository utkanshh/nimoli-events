#!/bin/bash
set -euo pipefail

if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "Build this app on a Mac; PyInstaller does not cross-build macOS apps from Windows." >&2
  exit 1
fi

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

PYTHON="${PYTHON:-python3}"
if ! "$PYTHON" -c "import tkinter" >/dev/null 2>&1; then
  echo "Python Tk is required. Install Python with Tk support, for example from python.org." >&2
  exit 1
fi

VENV="$ROOT/.venv-macos"
if [[ ! -x "$VENV/bin/python" ]]; then
  "$PYTHON" -m venv "$VENV"
fi

"$VENV/bin/python" -m pip install --upgrade -r requirements-build.txt
"$VENV/bin/python" -m PyInstaller \
  --noconfirm \
  --clean \
  --windowed \
  --onedir \
  --name "Nimoli Bhandari Events" \
  --osx-bundle-identifier "com.nimoli.bhandari.events" \
  --add-data "$ROOT/gather_rsvp:gather_rsvp" \
  --add-data "$ROOT/guests:guests" \
  --hidden-import guests.admin \
  --hidden-import guests.management.commands.seed_demo \
  --hidden-import guests.management.commands.remove_demo \
  --hidden-import guests.management.commands.send_whatsapp_campaigns \
  --collect-all openpyxl \
  --collect-all phonenumbers \
  --collect-all pycountry \
  --collect-all PIL \
  desktop_launcher.py

cp "$ROOT/MACOS-APP.txt" "$ROOT/dist/README.txt"
PACKAGE_ROOT="$(mktemp -d)"
PACKAGE_DIR="$PACKAGE_ROOT/Nimoli Bhandari Events"
mkdir "$PACKAGE_DIR"
trap 'rm -rf "$PACKAGE_ROOT"' EXIT
cp -R "$ROOT/dist/Nimoli Bhandari Events.app" "$PACKAGE_DIR/"
cp "$ROOT/dist/README.txt" "$PACKAGE_DIR/"
ditto -c -k --sequesterRsrc --keepParent \
  "$PACKAGE_DIR" \
  "$ROOT/dist/Nimoli-Bhandari-Events-macOS.zip"

echo
echo "Built: $ROOT/dist/Nimoli Bhandari Events.app"
echo "Download package: $ROOT/dist/Nimoli-Bhandari-Events-macOS.zip"
echo "Read me: $ROOT/dist/README.txt"
echo "Data folder: ~/Library/Application Support/Gather RSVP"
echo "The app is unsigned. For distribution beyond your own Mac, sign and notarize it with an Apple Developer ID."
