#!/usr/bin/env bash
set -euo pipefail

APP_NAME="whos-next"
APP_GROUP="${APP_GROUP:-whosnext}"
INSTALL_DIR="${INSTALL_DIR:-/opt/whos-next}"
APP_USER_DESKTOP_NAME="Whos Next.desktop"
ICON_NAME="logo.png"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_DIR="${SCRIPT_DIR}"
REQ_FILE="${SRC_DIR}/requirements.txt"
LAUNCHER_PATH="${INSTALL_DIR}/run.sh"
DESKTOP_TEMPLATE="${INSTALL_DIR}/WhosNext.desktop"
VENDOR_DIR="${INSTALL_DIR}/vendor"

if [[ "${EUID}" -ne 0 ]]; then
  echo "Run this installer with sudo or as root."
  echo "Example:"
  echo "  sudo ./install.sh"
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is required."
  exit 1
fi

if ! command -v getent >/dev/null 2>&1; then
  echo "getent is required."
  exit 1
fi

echo "Installing ${APP_NAME} from:"
echo "  ${SRC_DIR}"
echo "Into:"
echo "  ${INSTALL_DIR}"

if ! getent group "${APP_GROUP}" >/dev/null 2>&1; then
  groupadd --system "${APP_GROUP}"
fi

mkdir -p "${INSTALL_DIR}"
rsync -a --delete \
  --exclude '.venv' \
  --exclude '__pycache__' \
  --exclude '*.pyc' \
  "${SRC_DIR}/" "${INSTALL_DIR}/"

python3 -m venv "${INSTALL_DIR}/.venv"
"${INSTALL_DIR}/.venv/bin/pip" install --upgrade pip
if [[ -d "${VENDOR_DIR}" ]] && find "${VENDOR_DIR}" -maxdepth 1 -type f | grep -q .; then
  "${INSTALL_DIR}/.venv/bin/pip" install --no-index --find-links "${VENDOR_DIR}" -r "${REQ_FILE}"
else
  "${INSTALL_DIR}/.venv/bin/pip" install -r "${REQ_FILE}"
fi

cat > "${LAUNCHER_PATH}" <<EOF
#!/usr/bin/env bash
set -euo pipefail
cd "${INSTALL_DIR}"
exec "${INSTALL_DIR}/.venv/bin/python" "${INSTALL_DIR}/app.py"
EOF
chmod 755 "${LAUNCHER_PATH}"

cat > "${DESKTOP_TEMPLATE}" <<EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Who's Next?
Comment=Slot machine student picker
Exec=${LAUNCHER_PATH}
Path=${INSTALL_DIR}
Icon=${INSTALL_DIR}/${ICON_NAME}
Terminal=false
Categories=Education;
StartupNotify=true
EOF
chmod 644 "${DESKTOP_TEMPLATE}"

install -Dm644 "${DESKTOP_TEMPLATE}" /usr/local/share/applications/whos-next.desktop

chown -R root:"${APP_GROUP}" "${INSTALL_DIR}"
find "${INSTALL_DIR}" -type d -exec chmod 2775 {} +
find "${INSTALL_DIR}" -type f -exec chmod 664 {} +
chmod 755 "${LAUNCHER_PATH}"
chmod 644 /usr/local/share/applications/whos-next.desktop

echo
echo "Adding existing /home users to ${APP_GROUP} and installing desktop shortcuts..."

for home_dir in /home/*; do
  [[ -d "${home_dir}" ]] || continue
  username="$(basename "${home_dir}")"
  desktop_dir="${home_dir}/Desktop"
  local_apps_dir="${home_dir}/.local/share/applications"

  id "${username}" >/dev/null 2>&1 || continue
  usermod -aG "${APP_GROUP}" "${username}"
  mkdir -p "${desktop_dir}" "${local_apps_dir}"
  install -m 755 "${DESKTOP_TEMPLATE}" "${desktop_dir}/${APP_USER_DESKTOP_NAME}"
  install -m 644 "${DESKTOP_TEMPLATE}" "${local_apps_dir}/whos-next.desktop"
  chown "${username}:${username}" "${desktop_dir}/${APP_USER_DESKTOP_NAME}" "${local_apps_dir}/whos-next.desktop"
done

mkdir -p /etc/skel/Desktop /etc/skel/.local/share/applications
install -m 755 "${DESKTOP_TEMPLATE}" "/etc/skel/Desktop/${APP_USER_DESKTOP_NAME}"
install -m 644 "${DESKTOP_TEMPLATE}" /etc/skel/.local/share/applications/whos-next.desktop

echo
echo "Installation complete."
echo "Shared app dir: ${INSTALL_DIR}"
echo "Launcher: ${LAUNCHER_PATH}"
echo "Desktop entry: /usr/local/share/applications/whos-next.desktop"
echo
echo "All existing /home users were added to ${APP_GROUP}."
echo "Users may need to log out and back in after installation."
