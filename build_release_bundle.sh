#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="${SCRIPT_DIR}"
DIST_DIR="${PROJECT_DIR}/dist"
BUNDLE_ROOT="${DIST_DIR}/whos-next"
BUNDLE_NAME="${BUNDLE_NAME:-whos-next.zip}"
BUNDLE_PATH="${DIST_DIR}/${BUNDLE_NAME}"

mkdir -p "${DIST_DIR}"
rm -rf "${BUNDLE_ROOT}"
mkdir -p "${BUNDLE_ROOT}"

rsync -a \
  --delete \
  --exclude '.git' \
  --exclude '.venv' \
  --exclude 'dist' \
  --exclude '__pycache__' \
  --exclude '*.pyc' \
  --exclude '*.pyo' \
  --exclude '*.bak' \
  --exclude '.DS_Store' \
  --exclude '.vendor-venv' \
  "${PROJECT_DIR}/" "${BUNDLE_ROOT}/"

rm -f "${BUNDLE_ROOT}/build_release_bundle.sh"

cd "${DIST_DIR}"
rm -f "${BUNDLE_PATH}"
zip -r "${BUNDLE_PATH}" "whos-next" >/dev/null

echo "Bundle created:"
echo "  ${BUNDLE_PATH}"
