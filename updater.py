import os
import shutil
import subprocess
import tempfile
import urllib.error
import urllib.request
from dataclasses import dataclass

from pathlib import Path

from PyQt6.QtCore import QObject, pyqtSignal


BASE_DIR = Path(__file__).resolve().parent
CURRENT_VERSION = (BASE_DIR / "VERSION").read_text(encoding="utf-8").strip()
VERSION_URL = "https://raw.githubusercontent.com/emir12311/whos-next/main/VERSION"
BUNDLE_URL = "https://github.com/emir12311/whos-next/releases/latest/download/whos-next.zip"
VENDOR_DIR_NAME = "vendor"


def version_tuple(version: str) -> tuple[int, ...]:
    return tuple(int(part) for part in version.strip().split(".") if part.isdigit())


@dataclass
class UpdateResult:
    updated: bool
    message_key: str


class UpdateWorker(QObject):
    started = pyqtSignal()
    finished = pyqtSignal(object)

    def __init__(self, script_path: str):
        super().__init__()
        self.script_path = script_path

    def apply_bundle_update(self, bundle_bytes: bytes) -> None:
        import zipfile

        target_dir = os.path.dirname(self.script_path)
        extract_dir = tempfile.mkdtemp(prefix="whos-next-update-", dir=target_dir)
        bundle_path = os.path.join(extract_dir, "bundle.zip")

        try:
            with open(bundle_path, "wb") as bundle_file:
                bundle_file.write(bundle_bytes)

            with zipfile.ZipFile(bundle_path, "r") as archive:
                archive.extractall(extract_dir)

            candidates = [
                entry
                for entry in os.listdir(extract_dir)
                if entry not in {"bundle.zip"} and not entry.startswith(".")
            ]

            root_path = os.path.join(extract_dir, candidates[0]) if len(candidates) == 1 else extract_dir

            for entry in os.listdir(root_path):
                if entry in {".venv", "__pycache__"}:
                    continue
                source_path = os.path.join(root_path, entry)
                destination_path = os.path.join(target_dir, entry)
                if os.path.isdir(source_path):
                    shutil.copytree(source_path, destination_path, dirs_exist_ok=True)
                else:
                    shutil.copy2(source_path, destination_path)

            pip_path = os.path.join(target_dir, ".venv", "bin", "pip")
            requirements_path = os.path.join(target_dir, "requirements.txt")
            vendor_dir = os.path.join(target_dir, VENDOR_DIR_NAME)
            if os.path.exists(pip_path) and os.path.exists(requirements_path):
                install_cmd = [pip_path, "install"]
                if os.path.isdir(vendor_dir) and os.listdir(vendor_dir):
                    install_cmd.extend(["--no-index", "--find-links", vendor_dir])
                install_cmd.extend(["-r", requirements_path])
                subprocess.run(
                    install_cmd,
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
        finally:
            shutil.rmtree(extract_dir, ignore_errors=True)

    def run(self) -> None:
        try:
            latest_version = (
                urllib.request.urlopen(VERSION_URL, timeout=5).read().decode("utf-8").strip()
            )
            if version_tuple(latest_version) <= version_tuple(CURRENT_VERSION):
                self.finished.emit(UpdateResult(False, "update_none"))
                return

            self.started.emit()
            bundle_data = urllib.request.urlopen(BUNDLE_URL, timeout=20).read()
            self.apply_bundle_update(bundle_data)

            self.finished.emit(UpdateResult(True, "update_done"))
        except (OSError, ValueError, urllib.error.URLError, subprocess.SubprocessError):
            self.finished.emit(UpdateResult(False, "update_error"))
