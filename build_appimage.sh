#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="${SCRIPT_DIR}"
DIST_DIR="${PROJECT_DIR}/dist"
APPDIR="${DIST_DIR}/WhosNext.AppDir"
APP_ID="whos-next"
APP_NAME="Who's Next?"
ICON_NAME="whos-next"
ICON_SOURCE="${PROJECT_DIR}/logo.png"
VERSION_FILE="${PROJECT_DIR}/VERSION"
VERSION="$(tr -d '[:space:]' < "${VERSION_FILE}")"
ARCH="${ARCH:-x86_64}"
OUTPUT="${DIST_DIR}/WhosNext-${VERSION}-${ARCH}.AppImage"
PAYLOAD_DIR="${APPDIR}/usr/lib/${APP_ID}"
BIN_DIR="${APPDIR}/usr/bin"
DESKTOP_DIR="${APPDIR}/usr/share/applications"
ICON_DIR="${APPDIR}/usr/share/icons/hicolor/512x512/apps"
PYTHON_DIR="${PAYLOAD_DIR}/python"
REQ_FILE="${PROJECT_DIR}/requirements.txt"
VENDOR_DIR="${PROJECT_DIR}/vendor"
APPIMAGETOOL="${APPIMAGETOOL:-${PROJECT_DIR}/tools/appimagetool-${ARCH}.AppImage}"
APPIMAGETOOL_URL="https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-${ARCH}.AppImage"

# Bundled relocatable CPython (python-build-standalone). A venv created here
# would only symlink to the build machine's /usr/bin/python3 and carry no
# stdlib, so the AppImage would silently require the host to have the exact
# same interpreter version. Bundling a standalone interpreter avoids that.
PYTHON_VERSION="${PYTHON_VERSION:-3.11.16}"
PYTHON_STANDALONE_RELEASE="${PYTHON_STANDALONE_RELEASE:-20260901}"
PYTHON_TARBALL_NAME="cpython-${PYTHON_VERSION}+${PYTHON_STANDALONE_RELEASE}-${ARCH}-unknown-linux-gnu-install_only.tar.gz"
PYTHON_URL="https://github.com/astral-sh/python-build-standalone/releases/download/${PYTHON_STANDALONE_RELEASE}/${PYTHON_TARBALL_NAME}"

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is required."
  exit 1
fi

if ! command -v rsync >/dev/null 2>&1; then
  echo "rsync is required."
  exit 1
fi

if ! command -v curl >/dev/null 2>&1; then
  echo "curl is required."
  exit 1
fi

if [[ ! -f "${ICON_SOURCE}" ]]; then
  echo "Missing icon: ${ICON_SOURCE}"
  exit 1
fi

mkdir -p "${DIST_DIR}" "${PROJECT_DIR}/tools"
rm -rf "${APPDIR}"
mkdir -p "${PAYLOAD_DIR}" "${BIN_DIR}" "${DESKTOP_DIR}" "${ICON_DIR}"

rsync -a \
  --delete \
  --exclude '.git' \
  --exclude '.venv' \
  --exclude '.vendor-venv' \
  --exclude '__pycache__' \
  --exclude '*.pyc' \
  --exclude '*.pyo' \
  --exclude '*.bak' \
  --exclude '.DS_Store' \
  --exclude 'dist' \
  --exclude 'tools' \
  "${PROJECT_DIR}/" "${PAYLOAD_DIR}/"

# Fetch and unpack the standalone interpreter into the payload.
PYTHON_TARBALL="${PROJECT_DIR}/tools/${PYTHON_TARBALL_NAME}"
if [[ ! -f "${PYTHON_TARBALL}" ]]; then
  echo "Fetching standalone CPython ${PYTHON_VERSION}..."
  curl -fL "${PYTHON_URL}" -o "${PYTHON_TARBALL}"
fi

rm -rf "${PYTHON_DIR}"
EXTRACT_DIR="$(mktemp -d)"
tar -xzf "${PYTHON_TARBALL}" -C "${EXTRACT_DIR}"
mv "${EXTRACT_DIR}/python" "${PYTHON_DIR}"
rm -rf "${EXTRACT_DIR}"

PYTHON_BIN="${PYTHON_DIR}/bin/python3"
if [[ ! -x "${PYTHON_BIN}" ]]; then
  echo "Bundled interpreter is missing: ${PYTHON_BIN}"
  exit 1
fi

"${PYTHON_BIN}" -m pip install --upgrade pip --quiet
if [[ -d "${VENDOR_DIR}" ]] && find "${VENDOR_DIR}" -maxdepth 1 -type f | grep -q .; then
  "${PYTHON_BIN}" -m pip install --no-index --find-links "${PAYLOAD_DIR}/vendor" -r "${REQ_FILE}"
else
  "${PYTHON_BIN}" -m pip install -r "${REQ_FILE}"
fi

cat > "${BIN_DIR}/${APP_ID}" <<EOF
#!/usr/bin/env bash
set -euo pipefail
HERE="\$(cd "\$(dirname "\${BASH_SOURCE[0]}")/../lib/${APP_ID}" && pwd)"
cd "\${HERE}"
exec "\${HERE}/python/bin/python3" "\${HERE}/app.py"
EOF
chmod 755 "${BIN_DIR}/${APP_ID}"

cat > "${APPDIR}/AppRun" <<EOF
#!/usr/bin/env bash
set -euo pipefail
HERE="\$(cd "\$(dirname "\${BASH_SOURCE[0]}")" && pwd)"
export PATH="\${HERE}/usr/bin:\${PATH}"
exec "\${HERE}/usr/bin/${APP_ID}" "\$@"
EOF
chmod 755 "${APPDIR}/AppRun"

cat > "${DESKTOP_DIR}/${APP_ID}.desktop" <<EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=${APP_NAME}
Comment=Slot machine student picker
Exec=${APP_ID}
Icon=${ICON_NAME}
Terminal=false
Categories=Education;
StartupNotify=true
EOF

cp "${DESKTOP_DIR}/${APP_ID}.desktop" "${APPDIR}/${APP_ID}.desktop"
cp "${ICON_SOURCE}" "${ICON_DIR}/${ICON_NAME}.png"
cp "${ICON_SOURCE}" "${APPDIR}/${ICON_NAME}.png"

if [[ ! -x "${APPIMAGETOOL}" ]]; then
  curl -fL "${APPIMAGETOOL_URL}" -o "${APPIMAGETOOL}"
  chmod +x "${APPIMAGETOOL}"
fi

rm -f "${OUTPUT}"
APPIMAGE_EXTRACT_AND_RUN=1 ARCH="${ARCH}" "${APPIMAGETOOL}" "${APPDIR}" "${OUTPUT}"

echo "AppImage created:"
echo "  ${OUTPUT}"
