import os
import random
import sys
from pathlib import Path

LOCAL_SITE_PACKAGES = (
    Path(__file__).resolve().parent
    / ".venv"
    / "lib"
    / f"python{sys.version_info.major}.{sys.version_info.minor}"
    / "site-packages"
)
if LOCAL_SITE_PACKAGES.exists():
    sys.path.insert(0, str(LOCAL_SITE_PACKAGES))

from PyQt6.QtCore import (
    QEasingCurve,
    QPropertyAnimation,
    QSettings,
    QThread,
    QTimer,
    Qt,
    QUrl,
)
from PyQt6.QtGui import QFont
from PyQt6.QtMultimedia import QAudioOutput, QMediaPlayer
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from pdf_parser import parse_pdf_rosters
from updater import UpdateResult, UpdateWorker
from widgets import LeverWidget, ReelWidget, Toast

LEVER_SOUND_PATH = os.path.join(os.path.dirname(__file__), "lever_pull.m4a")
SPIN_SOUND_PATH = os.path.join(os.path.dirname(__file__), "spin_loop.m4a")
SPIN_SOUND_ONE_TIME_PATH = os.path.join(os.path.dirname(__file__), "spin_loop_one_time.m4a")
CLICK_SOUND_PATH = os.path.join(os.path.dirname(__file__), "click.mp3")
SUCCESS_SOUND_PATH = os.path.join(os.path.dirname(__file__), "success.mp3")
SELECTED_SOUND_PATH = os.path.join(os.path.dirname(__file__), "selected.mp3")
ERROR_SOUND_PATH = os.path.join(os.path.dirname(__file__), "error.mp3")
DEFAULT_PDF_PATH = ""
ORGANIZATION_NAME = "WhosNext"
APPLICATION_NAME = "WhosNextApp"

TRANSLATIONS = {
    "en": {
        "title": "Who’s Next?",
        "subtitle": "Pull the lever to choose a student",
        "load_title": "Load Student PDF",
        "load_subtitle": "Select a class list PDF",
        "pdf_file": "PDF File",
        "select_pdf": "Select PDF",
        "load_pdf": "Load PDF",
        "change_pdf": "Change PDF",
        "reset_list": "Reset List",
        "loading_pdf": "Loading PDF...",
        "load_ready": "Choose a PDF to begin.",
        "load_success": "PDF loaded successfully.",
        "load_error": "PDF load failed.",
        "pdf_missing": "Select a PDF file first.",
        "pdf_selected": "Selected PDF",
        "language": "Language",
        "class": "Class",
        "continue": "Continue",
        "done": "Done",
        "remove_student": "Remove Student From List",
        "success_title": "Success",
        "error_title": "Error",
        "winner_title": "Student Selected",
        "pdf_success_message": "The PDF was imported successfully and classes are ready.",
        "winner_popup_message": "Selected student: {name}",
        "empty_class_message": "There are no students left in this class.",
        "spin_ready": "Ready",
        "spinning": "Spinning...",
        "winner": "Selected Student",
        "check_update": "Check Update",
        "update_started": "Update started. Downloading the latest app...",
        "update_done": "Update complete. Restart the app to use the new version.",
        "update_none": "You already have the latest version.",
        "update_error": "Update check failed.",
        "update_appimage": "AppImage builds cannot update themselves. Download the latest AppImage from Releases.",
        "version": "Version",
    },
    "tr": {
        "title": "Sıradaki Kim?",
        "subtitle": "Bir öğrenci seçmek için şalteri çekin",
        "load_title": "PDF Yükle",
        "load_subtitle": "Bir sınıf listesi PDF dosyası seçin",
        "pdf_file": "PDF Dosyası",
        "select_pdf": "PDF Seç",
        "load_pdf": "PDF Yükle",
        "change_pdf": "PDF Değiştir",
        "reset_list": "Listeyi Sıfırla",
        "loading_pdf": "PDF yükleniyor...",
        "load_ready": "Başlamak için bir PDF seçin.",
        "load_success": "PDF başarıyla yüklendi.",
        "load_error": "PDF yükleme başarısız oldu.",
        "pdf_missing": "Önce bir PDF dosyası seçin.",
        "pdf_selected": "Seçilen PDF",
        "language": "Dil",
        "class": "Sınıf",
        "continue": "Devam",
        "done": "Tamam",
        "remove_student": "Öğrenciyi Listeden Çıkar",
        "success_title": "Başarılı",
        "error_title": "Hata",
        "winner_title": "Öğrenci Seçildi",
        "pdf_success_message": "PDF başarıyla içe aktarıldı ve sınıflar hazır.",
        "winner_popup_message": "Seçilen öğrenci: {name}",
        "empty_class_message": "Bu sınıfta hiç öğrenci kalmadı.",
        "spin_ready": "Hazır",
        "spinning": "Dönüyor...",
        "winner": "Seçilen Öğrenci",
        "check_update": "Güncellemeyi Kontrol Et",
        "update_started": "Güncelleme başladı. En son sürüm indiriliyor...",
        "update_done": "Güncelleme tamamlandı. Yeni sürüm için uygulamayı yeniden başlatın.",
        "update_none": "Zaten en güncel sürümü kullanıyorsunuz.",
        "update_error": "Güncelleme denetimi başarısız oldu.",
        "update_appimage": "AppImage sürümü kendini güncelleyemez. En son AppImage dosyasını Releases bölümünden indirin.",
        "version": "Sürüm",
    },
}

ACCENT_PURPLE = "#C06BEF"
ACCENT_PURPLE_SOFT = "#D694F7"


class WhosNextWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = QSettings(ORGANIZATION_NAME, APPLICATION_NAME)
        self.language = self.settings.value("language", "en", str)
        if self.language not in TRANSLATIONS:
            self.language = "en"
        self.current_pdf_path = self.settings.value("pdf_path", DEFAULT_PDF_PATH, str)
        self.class_rosters: dict[str, list[str]] = {}
        self.original_class_rosters: dict[str, list[str]] = {}
        self.selected_class = self.settings.value("class_name", "", str)
        self.current_names = ["No Students"]
        self.current_index = 0
        self.winner_index = 0
        self.spin_elapsed = 0
        self.spin_duration_ms = 3000
        self.is_spinning = False
        self.spin_start_position = 0.0
        self.spin_target_position = 0.0
        self.update_worker = None
        self.update_thread = None
        self.winner_animation = None
        self.lever_player = None
        self.lever_audio = None
        self.spin_player = None
        self.spin_audio = None
        self.click_player = None
        self.click_audio = None
        self.success_player = None
        self.success_audio = None
        self.selected_player = None
        self.selected_audio = None
        self.error_player = None
        self.error_audio = None
        self.last_spin_sound_ms = -10_000

        self.setWindowTitle(self.tr_text("title"))
        self.setMinimumSize(1180, 700)
        self.resize(1400, 820)

        self.spin_timer = QTimer(self)
        self.spin_timer.timeout.connect(self.advance_spin)
        self.spin_timer.setInterval(16)
        self.toast = Toast(self)
        self.setup_audio()

        self.build_ui()
        self.apply_window_style()
        self.apply_language()
        self.refresh_pdf_path_label()
        if self.current_pdf_path and os.path.exists(self.current_pdf_path):
            self.load_status_label.setText(self.tr_text("load_ready"))
        QTimer.singleShot(900, self.check_for_updates_silently)

    def tr_text(self, key: str) -> str:
        return TRANSLATIONS[self.language][key]

    def setup_audio(self) -> None:
        if os.path.exists(LEVER_SOUND_PATH):
            self.lever_audio = QAudioOutput(self)
            self.lever_audio.setVolume(0.72)
            self.lever_player = QMediaPlayer(self)
            self.lever_player.setAudioOutput(self.lever_audio)
            self.lever_player.setSource(QUrl.fromLocalFile(LEVER_SOUND_PATH))

        if os.path.exists(CLICK_SOUND_PATH):
            self.click_audio = QAudioOutput(self)
            self.click_audio.setVolume(0.72)
            self.click_player = QMediaPlayer(self)
            self.click_player.setAudioOutput(self.click_audio)
            self.click_player.setSource(QUrl.fromLocalFile(CLICK_SOUND_PATH))

        if os.path.exists(SUCCESS_SOUND_PATH):
            self.success_audio = QAudioOutput(self)
            self.success_audio.setVolume(0.72)
            self.success_player = QMediaPlayer(self)
            self.success_player.setAudioOutput(self.success_audio)
            self.success_player.setSource(QUrl.fromLocalFile(SUCCESS_SOUND_PATH))

        if os.path.exists(SELECTED_SOUND_PATH):
            self.selected_audio = QAudioOutput(self)
            self.selected_audio.setVolume(0.72)
            self.selected_player = QMediaPlayer(self)
            self.selected_player.setAudioOutput(self.selected_audio)
            self.selected_player.setSource(QUrl.fromLocalFile(SELECTED_SOUND_PATH))

        if os.path.exists(ERROR_SOUND_PATH):
            self.error_audio = QAudioOutput(self)
            self.error_audio.setVolume(0.72)
            self.error_player = QMediaPlayer(self)
            self.error_player.setAudioOutput(self.error_audio)
            self.error_player.setSource(QUrl.fromLocalFile(ERROR_SOUND_PATH))

        spin_source = None
        if os.path.exists(SPIN_SOUND_ONE_TIME_PATH):
            spin_source = SPIN_SOUND_ONE_TIME_PATH
        elif os.path.exists(SPIN_SOUND_PATH):
            spin_source = SPIN_SOUND_PATH

        if spin_source is not None:
            self.spin_audio = QAudioOutput(self)
            self.spin_audio.setVolume(0.72)
            self.spin_player = QMediaPlayer(self)
            self.spin_player.setAudioOutput(self.spin_audio)
            self.spin_player.setSource(QUrl.fromLocalFile(spin_source))

    def play_lever_sound(self) -> None:
        self.play_sound(self.lever_player)

    def start_spin_sound(self) -> None:
        if self.spin_player is None:
            return
        self.last_spin_sound_ms = -10_000
        self.spin_player.stop()
        self.spin_player.play()
        self.last_spin_sound_ms = self.spin_elapsed

    def stop_spin_sound(self) -> None:
        if self.spin_player is None:
            return
        self.spin_player.stop()

    def play_sound(self, player: QMediaPlayer | None) -> None:
        if player is None:
            return
        player.stop()
        player.play()

    def play_click_sound(self) -> None:
        self.play_sound(self.click_player)

    def play_success_sound(self) -> None:
        self.play_sound(self.success_player)

    def play_selected_sound(self) -> None:
        self.play_sound(self.selected_player)

    def play_error_sound(self) -> None:
        self.play_sound(self.error_player)

    def update_spin_sound(self, progress: float) -> None:
        if self.spin_player is None:
            return
        cadence_ms = int(85 + (progress * 210))
        if (self.spin_elapsed - self.last_spin_sound_ms) < cadence_ms:
            return
        self.spin_player.stop()
        self.spin_player.play()
        self.last_spin_sound_ms = self.spin_elapsed

    def build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)

        root = QVBoxLayout(central)
        root.setContentsMargins(28, 28, 28, 28)
        root.setSpacing(0)

        self.stack = QStackedWidget()
        root.addWidget(self.stack)

        self.load_page = QWidget()
        load_layout = QVBoxLayout(self.load_page)
        load_layout.setContentsMargins(0, 0, 0, 0)
        load_layout.addStretch(1)

        load_card = QFrame()
        load_card.setObjectName("loadCard")
        load_card_layout = QVBoxLayout(load_card)
        load_card_layout.setContentsMargins(34, 34, 34, 34)
        load_card_layout.setSpacing(18)

        self.load_title_label = QLabel()
        self.load_title_label.setStyleSheet("color: #F4F0E8; font-size: 34px; font-weight: 800;")
        self.load_subtitle_label = QLabel()
        self.load_subtitle_label.setWordWrap(True)
        self.load_subtitle_label.setStyleSheet("color: #B2B8C1; font-size: 18px; font-weight: 500;")

        self.pdf_path_title_label = QLabel()
        self.pdf_path_title_label.setStyleSheet("color: #B2B8C1; font-size: 16px; font-weight: 700;")
        self.pdf_path_value_label = QLabel()
        self.pdf_path_value_label.setWordWrap(True)
        self.pdf_path_value_label.setStyleSheet("color: #F4F0E8; font-size: 18px; font-weight: 600;")

        load_button_row = QHBoxLayout()
        load_button_row.setSpacing(14)
        self.select_pdf_button = QPushButton()
        self.select_pdf_button.clicked.connect(self.play_click_sound)
        self.select_pdf_button.clicked.connect(self.select_pdf)
        self.load_pdf_button = QPushButton()
        self.load_pdf_button.clicked.connect(self.play_click_sound)
        self.load_pdf_button.clicked.connect(self.load_selected_pdf)
        load_button_row.addWidget(self.select_pdf_button)
        load_button_row.addWidget(self.load_pdf_button)

        self.load_status_label = QLabel()
        self.load_status_label.setWordWrap(True)
        self.load_status_label.setStyleSheet("color: #B2B8C1; font-size: 16px; font-weight: 600;")

        load_card_layout.addWidget(self.load_title_label)
        load_card_layout.addWidget(self.load_subtitle_label)
        load_card_layout.addSpacing(6)
        load_card_layout.addWidget(self.pdf_path_title_label)
        load_card_layout.addWidget(self.pdf_path_value_label)
        load_card_layout.addLayout(load_button_row)
        load_card_layout.addWidget(self.load_status_label)

        load_layout.addWidget(load_card, 0, Qt.AlignmentFlag.AlignCenter)
        load_layout.addStretch(1)

        self.picker_page = QWidget()
        picker_root = QHBoxLayout(self.picker_page)
        picker_root.setContentsMargins(0, 0, 0, 0)
        picker_root.setSpacing(24)

        left_panel = QFrame()
        left_panel.setObjectName("leftPanel")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(28, 24, 28, 28)
        left_layout.setSpacing(18)

        top_bar = QHBoxLayout()
        top_bar.setSpacing(16)

        title_wrap = QVBoxLayout()
        title_wrap.setSpacing(4)
        self.title_label = QLabel()
        self.title_label.setStyleSheet("color: #F4F0E8; font-size: 32px; font-weight: 800;")
        self.subtitle_label = QLabel()
        self.subtitle_label.setStyleSheet("color: #B2B8C1; font-size: 18px; font-weight: 500;")
        title_wrap.addWidget(self.title_label)
        title_wrap.addWidget(self.subtitle_label)

        self.status_chip = QLabel()
        self.status_chip.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_chip.setMinimumWidth(170)
        self.status_chip.setStyleSheet(
            """
            QLabel {
                color: #F4F0E8;
                background: rgba(255, 255, 255, 0.04);
                border: 1px solid rgba(214, 148, 247, 0.35);
                border-radius: 18px;
                padding: 10px 16px;
                font-size: 18px;
                font-weight: 700;
            }
            """
        )

        self.language_combo = QComboBox()
        self.language_combo.addItem("English", "en")
        self.language_combo.addItem("Türkçe", "tr")
        self.language_combo.activated.connect(lambda _=0: self.play_click_sound())
        self.language_combo.currentIndexChanged.connect(self.on_language_changed)
        self.language_combo.setMinimumWidth(150)
        self.language_label = QLabel()
        self.language_label.setStyleSheet("color: #B2B8C1; font-size: 17px; font-weight: 700;")

        self.class_combo = QComboBox()
        self.class_combo.activated.connect(lambda _=0: self.play_click_sound())
        self.class_combo.currentIndexChanged.connect(self.on_class_changed)
        self.class_combo.setMinimumWidth(260)
        self.class_label = QLabel()
        self.class_label.setStyleSheet("color: #B2B8C1; font-size: 17px; font-weight: 700;")

        self.change_pdf_button = QPushButton()
        self.change_pdf_button.clicked.connect(self.play_click_sound)
        self.change_pdf_button.clicked.connect(self.show_load_page)
        self.change_pdf_button.setMinimumSize(190, 56)
        self.reset_list_button = QPushButton()
        self.reset_list_button.clicked.connect(self.play_click_sound)
        self.reset_list_button.clicked.connect(self.reset_current_lists)
        self.reset_list_button.setMinimumSize(190, 56)
        self.update_button = QPushButton()
        self.update_button.clicked.connect(self.play_click_sound)
        self.update_button.clicked.connect(self.check_for_updates_verbose)
        self.update_button.setMinimumSize(190, 56)

        top_bar.addLayout(title_wrap, 1)
        top_bar.addWidget(self.status_chip)
        top_bar.addWidget(self.class_label)
        top_bar.addWidget(self.class_combo)
        top_bar.addWidget(self.language_label)
        top_bar.addWidget(self.language_combo)

        self.reel_widget = ReelWidget(self.current_names)
        self.winner_label = QLabel()
        self.winner_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.winner_label.setStyleSheet("color: #B2B8C1; font-size: 20px; font-weight: 600;")

        bottom_bar = QHBoxLayout()
        bottom_bar.setSpacing(18)

        bottom_left = QHBoxLayout()
        bottom_left.addWidget(self.change_pdf_button, 0, Qt.AlignmentFlag.AlignLeft)

        bottom_center = QHBoxLayout()
        bottom_center.addWidget(self.reset_list_button, 0, Qt.AlignmentFlag.AlignCenter)

        bottom_right = QHBoxLayout()
        bottom_right.addWidget(self.update_button, 0, Qt.AlignmentFlag.AlignRight)

        bottom_bar.addLayout(bottom_left, 1)
        bottom_bar.addLayout(bottom_center, 1)
        bottom_bar.addLayout(bottom_right, 1)

        left_layout.addLayout(top_bar)
        left_layout.addStretch(1)
        left_layout.addWidget(self.reel_widget, 8)
        left_layout.addWidget(self.winner_label)
        left_layout.addSpacing(16)
        left_layout.addLayout(bottom_bar)
        left_layout.addStretch(1)

        right_panel = QFrame()
        right_panel.setObjectName("rightPanel")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(16, 20, 16, 20)
        right_layout.setSpacing(10)

        self.lever = LeverWidget()
        self.lever.pulled.connect(self.start_spin)
        right_layout.addStretch(1)
        right_layout.addWidget(self.lever, 0, Qt.AlignmentFlag.AlignCenter)
        right_layout.addStretch(1)

        picker_root.addWidget(left_panel, 7)
        picker_root.addWidget(right_panel, 2)

        self.stack.addWidget(self.load_page)
        self.stack.addWidget(self.picker_page)
        self.stack.setCurrentWidget(self.load_page)

    def refresh_pdf_path_label(self) -> None:
        if self.current_pdf_path:
            self.pdf_path_value_label.setText(self.current_pdf_path)
        else:
            self.pdf_path_value_label.setText("-")

    def show_error_dialog(self, message: str) -> None:
        self.play_error_sound()
        dialog = QMessageBox(self)
        dialog.setIcon(QMessageBox.Icon.Critical)
        dialog.setWindowTitle(self.tr_text("error_title"))
        dialog.setText(message)
        dialog.setStandardButtons(QMessageBox.StandardButton.Ok)
        dialog.exec()

    def show_success_dialog(self, message: str) -> None:
        self.play_success_sound()
        dialog = QMessageBox(self)
        dialog.setIcon(QMessageBox.Icon.Information)
        dialog.setWindowTitle(self.tr_text("success_title"))
        dialog.setText(message)
        continue_button = dialog.addButton(self.tr_text("continue"), QMessageBox.ButtonRole.AcceptRole)
        dialog.setDefaultButton(continue_button)
        dialog.exec()

    def show_winner_dialog(self, winner: str) -> None:
        self.play_selected_sound()
        dialog = QMessageBox(self)
        dialog.setIcon(QMessageBox.Icon.Information)
        dialog.setWindowTitle(self.tr_text("winner_title"))
        dialog.setText(self.tr_text("winner_popup_message").format(name=winner))
        done_button = dialog.addButton(self.tr_text("done"), QMessageBox.ButtonRole.AcceptRole)
        remove_button = dialog.addButton(self.tr_text("remove_student"), QMessageBox.ButtonRole.DestructiveRole)
        dialog.setDefaultButton(done_button)
        dialog.exec()

        if dialog.clickedButton() is remove_button:
            self.remove_current_winner()

    def select_pdf(self) -> None:
        selected_path, _ = QFileDialog.getOpenFileName(
            self,
            self.tr_text("select_pdf"),
            self.current_pdf_path or os.path.dirname(__file__),
            "PDF Files (*.pdf *.PDF)",
        )
        if not selected_path:
            return
        self.current_pdf_path = selected_path
        self.settings.setValue("pdf_path", self.current_pdf_path)
        self.refresh_pdf_path_label()
        self.load_status_label.setText(self.tr_text("load_ready"))

    def populate_class_combo(self) -> None:
        self.class_combo.blockSignals(True)
        self.class_combo.clear()
        for class_name in self.class_rosters:
            self.class_combo.addItem(class_name, class_name)
        self.class_combo.blockSignals(False)

    def activate_rosters(self, rosters: dict[str, list[str]]) -> None:
        self.original_class_rosters = {key: value[:] for key, value in rosters.items()}
        self.class_rosters = {key: value[:] for key, value in rosters.items()}
        remembered_class = self.settings.value("class_name", "", str)
        if remembered_class in self.class_rosters:
            self.selected_class = remembered_class
        else:
            self.selected_class = next(iter(self.class_rosters))
        self.current_names = self.class_rosters[self.selected_class]
        self.current_index = 0
        self.populate_class_combo()
        self.reel_widget.set_names(self.current_names)
        self.apply_language()
        self.stack.setCurrentWidget(self.picker_page)
        self.load_status_label.setText(self.tr_text("load_success"))
        self.show_success_dialog(self.tr_text("pdf_success_message"))

    def load_selected_pdf(self) -> None:
        if not self.current_pdf_path:
            self.load_status_label.setText(self.tr_text("pdf_missing"))
            self.show_error_dialog(self.tr_text("pdf_missing"))
            return
        self.load_status_label.setText(self.tr_text("loading_pdf"))
        QApplication.processEvents()
        try:
            rosters = parse_pdf_rosters(self.current_pdf_path)
        except (OSError, ValueError) as exc:
            error_message = f"{self.tr_text('load_error')} {exc}"
            self.load_status_label.setText(error_message)
            self.show_error_dialog(error_message)
            return

        self.settings.setValue("pdf_path", self.current_pdf_path)
        self.activate_rosters(rosters)

    def show_load_page(self) -> None:
        if self.is_spinning:
            return
        self.stack.setCurrentWidget(self.load_page)

    def reset_current_lists(self) -> None:
        if self.is_spinning or not self.original_class_rosters:
            return
        self.class_rosters = {key: value[:] for key, value in self.original_class_rosters.items()}
        if self.selected_class not in self.class_rosters:
            self.selected_class = next(iter(self.class_rosters))
        self.current_names = self.class_rosters[self.selected_class]
        self.current_index = 0
        self.populate_class_combo()
        self.reel_widget.set_names(self.current_names)
        self.apply_language()

    def remove_current_winner(self) -> None:
        if not self.selected_class or self.selected_class not in self.class_rosters:
            return
        if self.current_index >= len(self.current_names):
            return
        del self.current_names[self.current_index]
        self.class_rosters[self.selected_class] = self.current_names
        self.current_index = 0
        self.reel_widget.set_names(self.current_names)
        if self.current_names:
            self.winner_label.setText(f"{self.tr_text('winner')}: {self.reel_widget.current_name()}")
        else:
            self.winner_label.setText(f"{self.tr_text('winner')}: {self.tr_text('empty_class_message')}")

    def apply_window_style(self) -> None:
        self.setStyleSheet(
            f"""
            QMainWindow {{
                background: #16191F;
            }}
            QFrame#leftPanel, QFrame#rightPanel, QFrame#loadCard {{
                background: #22262D;
                border: 1px solid #4E4561;
                border-radius: 28px;
            }}
            QComboBox, QPushButton {{
                color: #F4F0E8;
                background: #2B3038;
                border: 1px solid #6E6286;
                border-radius: 14px;
                padding: 10px 14px;
                font-size: 17px;
                font-weight: 700;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 24px;
            }}
            QComboBox QAbstractItemView {{
                background: #2B3038;
                color: #F4F0E8;
                selection-background-color: {ACCENT_PURPLE};
            }}
            QPushButton:hover, QComboBox:hover {{
                border-color: {ACCENT_PURPLE_SOFT};
            }}
            """
        )

    def apply_language(self) -> None:
        self.setWindowTitle(self.tr_text("title"))
        self.title_label.setText(self.tr_text("title"))
        self.subtitle_label.setText(self.tr_text("subtitle"))
        self.load_title_label.setText(self.tr_text("load_title"))
        self.load_subtitle_label.setText(self.tr_text("load_subtitle"))
        self.pdf_path_title_label.setText(self.tr_text("pdf_file"))
        self.select_pdf_button.setText(self.tr_text("select_pdf"))
        self.load_pdf_button.setText(self.tr_text("load_pdf"))
        self.status_chip.setText(self.tr_text("spin_ready") if not self.is_spinning else self.tr_text("spinning"))
        self.class_label.setText(self.tr_text("class"))
        self.language_label.setText(self.tr_text("language"))
        self.change_pdf_button.setText(self.tr_text("change_pdf"))
        self.reset_list_button.setText(self.tr_text("reset_list"))
        self.update_button.setText(self.tr_text("check_update"))
        self.winner_label.setText(f"{self.tr_text('winner')}: {self.reel_widget.current_name()}")
        self.class_combo.blockSignals(True)
        class_index = self.class_combo.findData(self.selected_class)
        if self.class_combo.count() > 0:
            self.class_combo.setCurrentIndex(max(class_index, 0))
        self.class_combo.blockSignals(False)
        self.language_combo.blockSignals(True)
        index = self.language_combo.findData(self.language)
        self.language_combo.setCurrentIndex(max(index, 0))
        self.language_combo.blockSignals(False)
        if self.stack.currentWidget() is self.load_page and not self.class_rosters:
            self.load_status_label.setText(self.tr_text("load_ready"))

    def on_language_changed(self) -> None:
        self.language = self.language_combo.currentData()
        self.settings.setValue("language", self.language)
        self.apply_language()

    def on_class_changed(self) -> None:
        if self.is_spinning:
            return
        self.selected_class = self.class_combo.currentData()
        if not self.selected_class:
            return
        self.settings.setValue("class_name", self.selected_class)
        self.current_names = self.class_rosters[self.selected_class]
        self.current_index = 0
        self.reel_widget.set_names(self.current_names)
        self.winner_label.setText(f"{self.tr_text('winner')}: {self.reel_widget.current_name()}")

    def start_spin(self) -> None:
        if self.is_spinning:
            return
        if not self.current_names:
            self.show_error_dialog(self.tr_text("empty_class_message"))
            return
        self.is_spinning = True
        self.play_lever_sound()
        self.lever.set_enabled_state(False)
        self.class_combo.setEnabled(False)
        self.status_chip.setText(self.tr_text("spinning"))
        self.reel_widget.set_highlight_strength(0.0)
        self.spin_elapsed = 0
        self.winner_index = random.randrange(len(self.current_names))
        self.spin_start_position = self.reel_widget.get_position()
        current_slot = int(round(self.spin_start_position)) % len(self.current_names)
        delta = (self.winner_index - current_slot) % len(self.current_names)
        self.spin_target_position = self.spin_start_position + (len(self.current_names) * 5) + delta
        self.start_spin_sound()
        self.spin_timer.start()

    def advance_spin(self) -> None:
        self.spin_elapsed += self.spin_timer.interval()
        progress = min(1.0, self.spin_elapsed / self.spin_duration_ms)
        eased = QEasingCurve(QEasingCurve.Type.OutQuart).valueForProgress(progress)
        new_position = self.spin_start_position + ((self.spin_target_position - self.spin_start_position) * eased)
        self.reel_widget.set_position(new_position)
        self.update_spin_sound(progress)

        if progress >= 1.0:
            self.spin_timer.stop()
            self.finish_spin()
            return

    def finish_spin(self) -> None:
        self.current_index = self.winner_index
        self.reel_widget.set_position(float(self.spin_target_position))
        winner = self.current_names[self.current_index]
        self.stop_spin_sound()
        self.status_chip.setText(self.tr_text("spin_ready"))
        self.lever.set_enabled_state(True)
        self.class_combo.setEnabled(True)
        self.is_spinning = False
        self.winner_label.setText(f"{self.tr_text('winner')}: {winner}")
        self.play_winner_animation()
        self.show_winner_dialog(winner)

    def play_winner_animation(self) -> None:
        glow_anim = QPropertyAnimation(self.reel_widget, b"highlight_strength", self)
        glow_anim.setDuration(1000)
        glow_anim.setStartValue(0.0)
        glow_anim.setKeyValueAt(0.35, 1.0)
        glow_anim.setKeyValueAt(0.7, 0.2)
        glow_anim.setEndValue(0.65)
        glow_anim.setEasingCurve(QEasingCurve.Type.InOutSine)
        self.winner_animation = glow_anim
        glow_anim.finished.connect(self.clear_winner_animation, Qt.ConnectionType.SingleShotConnection)
        glow_anim.start()

    def check_for_updates_silently(self) -> None:
        self.run_update_check(show_no_update=False)

    def check_for_updates_verbose(self) -> None:
        self.run_update_check(show_no_update=True)

    def run_update_check(self, show_no_update: bool) -> None:
        if self.update_thread is not None:
            return
        if os.getenv("APPIMAGE"):
            self.toast.show_message(self.tr_text("update_appimage"), 3200)
            return
        script_path = os.path.abspath(__file__)

        self.update_thread = QThread(self)
        self.update_worker = UpdateWorker(script_path)
        self.update_worker.moveToThread(self.update_thread)
        self.update_thread.started.connect(self.update_worker.run)
        self.update_worker.started.connect(
            lambda: self.toast.show_message(self.tr_text("update_started"), 2000)
        )
        self.update_worker.finished.connect(
            lambda result: self.on_update_finished(result, show_no_update)
        )
        self.update_worker.finished.connect(self.update_thread.quit)
        self.update_worker.finished.connect(self.update_worker.deleteLater)
        self.update_thread.finished.connect(self.update_thread.deleteLater)
        self.update_thread.finished.connect(self.clear_update_refs)
        self.update_thread.start()

    def on_update_finished(self, result: UpdateResult, show_no_update: bool) -> None:
        if result.updated or show_no_update or result.message_key == "update_error":
            self.toast.show_message(self.tr_text(result.message_key))

    def clear_update_refs(self) -> None:
        self.update_thread = None
        self.update_worker = None

    def clear_winner_animation(self) -> None:
        self.winner_animation = None

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        if self.toast.isVisible():
            x = (self.width() - self.toast.width()) // 2
            self.toast.move(x, self.toast.y())


def configure_font(app: QApplication) -> None:
    font = QFont()
    font.setFamilies(["DejaVu Sans", "Noto Sans", "Ubuntu", "Cantarell", "Sans Serif"])
    font.setPointSize(11)
    app.setFont(font)


def main() -> int:
    app = QApplication(sys.argv)
    app.setOrganizationName(ORGANIZATION_NAME)
    app.setApplicationName(APPLICATION_NAME)
    app.setStyle("Fusion")
    configure_font(app)
    window = WhosNextWindow()
    window.showMaximized()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
