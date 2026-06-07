#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="${SCRIPT_DIR}"
VENDOR_DIR="${PROJECT_DIR}/vendor"
REQ_FILE="${PROJECT_DIR}/requirements.txt"
BUILD_VENV="${PROJECT_DIR}/.vendor-venv"

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is required."
  exit 1
fi

rm -rf "${BUILD_VENV}"
python3 -m venv "${BUILD_VENV}"
"${BUILD_VENV}/bin/pip" install --upgrade pip

mkdir -p "${VENDOR_DIR}"
find "${VENDOR_DIR}" -mindepth 1 -maxdepth 1 -type f -delete

"${BUILD_VENV}/bin/pip" download \
  --dest "${VENDOR_DIR}" \
  -r "${REQ_FILE}"

rm -rf "${BUILD_VENV}"

echo "Offline wheels downloaded to:"
echo "  ${VENDOR_DIR}"
