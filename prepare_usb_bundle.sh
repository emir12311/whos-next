#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="${SCRIPT_DIR}"
DIST_DIR="${PROJECT_DIR}/dist"
USB_DIR="${DIST_DIR}/whos-next-usb"

mkdir -p "${DIST_DIR}"
rm -rf "${USB_DIR}"
mkdir -p "${USB_DIR}"

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
  "${PROJECT_DIR}/" "${USB_DIR}/"

echo "USB bundle prepared at:"
echo "  ${USB_DIR}"
echo
echo "Copy the entire 'whos-next-usb' folder to your flash drive."
