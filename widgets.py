from PyQt6.QtCore import QEasingCurve, QPoint, QPropertyAnimation, QRectF, QTimer, Qt, pyqtProperty, pyqtSignal
from PyQt6.QtGui import QColor, QFont, QLinearGradient, QPainter, QPainterPath, QPen
from PyQt6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QLabel,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


TEXT_PRIMARY = "#EAF7FF"
FRAME_DARK = "#20242B"
PAPER = "#F2EEE6"
ACCENT_PURPLE = "#C06BEF"


class Toast(QFrame):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setWindowFlags(Qt.WindowType.SubWindow | Qt.WindowType.FramelessWindowHint)
        self.setObjectName("toast")
        self.label = QLabel(self)
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet(f"color: {TEXT_PRIMARY}; font-size: 18px; font-weight: 600;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 16, 22, 16)
        layout.addWidget(self.label)
        self.setStyleSheet(
            """
            QFrame#toast {
                background-color: rgba(11, 16, 32, 235);
                border: 1px solid #6A727E;
                border-radius: 18px;
            }
            """
        )
        self.hide_timer = QTimer(self)
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self.fade_out)
        self.opacity_anim = QPropertyAnimation(self, b"windowOpacity", self)
        self.opacity_anim.setDuration(250)

    def show_message(self, message: str, duration_ms: int = 2400) -> None:
        self.label.setText(message)
        self.adjustSize()
        width = min(max(self.parent().width() // 2, 320), 720)
        self.resize(width, self.sizeHint().height())
        x = (self.parent().width() - self.width()) // 2
        y = 26
        self.move(x, y)
        self.setWindowOpacity(0.0)
        self.show()
        self.raise_()
        self.opacity_anim.stop()
        self.opacity_anim.setStartValue(0.0)
        self.opacity_anim.setEndValue(1.0)
        self.opacity_anim.start()
        self.hide_timer.start(duration_ms)

    def fade_out(self) -> None:
        self.opacity_anim.stop()
        self.opacity_anim.setStartValue(self.windowOpacity())
        self.opacity_anim.setEndValue(0.0)
        self.opacity_anim.finished.connect(self.hide, Qt.ConnectionType.SingleShotConnection)
        self.opacity_anim.start()


class ReelWidget(QWidget):
    def __init__(self, names: list[str]):
        super().__init__()
        self.names = names or ["No Students"]
        self._position = 0.0
        self._highlight_strength = 0.0
        self.setMinimumHeight(360)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(28)
        self.shadow.setColor(QColor(0, 0, 0, 140))
        self.shadow.setOffset(0, 10)
        self.setGraphicsEffect(self.shadow)

    def get_position(self) -> float:
        return self._position

    def set_position(self, value: float) -> None:
        self._position = value
        self.update()

    position = pyqtProperty(float, get_position, set_position)

    def get_highlight_strength(self) -> float:
        return self._highlight_strength

    def set_highlight_strength(self, value: float) -> None:
        self._highlight_strength = value
        self.update()

    highlight_strength = pyqtProperty(float, get_highlight_strength, set_highlight_strength)

    def set_names(self, names: list[str]) -> None:
        self.names = names or ["No Students"]
        self._position = 0.0
        self._highlight_strength = 0.0
        self.update()

    def current_name(self) -> str:
        return self.names[int(round(self._position)) % len(self.names)]

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), Qt.GlobalColor.transparent)

        outer = QRectF(6, 6, self.width() - 12, self.height() - 12)
        painter.setPen(QPen(QColor("#566170"), 2))
        painter.setBrush(QColor(FRAME_DARK))
        painter.drawRoundedRect(outer, 28, 28)

        bezel = outer.adjusted(16, 16, -16, -16)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#4A525E"))
        painter.drawRoundedRect(bezel, 24, 24)

        window_rect = bezel.adjusted(28, 24, -28, -24)
        painter.setBrush(QColor("#0F1217"))
        painter.drawRoundedRect(window_rect, 22, 22)

        clip_path = QPainterPath()
        clip_path.addRoundedRect(window_rect, 22, 22)
        painter.save()
        painter.setClipPath(clip_path)

        row_height = window_rect.height() / 4.1
        center_y = window_rect.center().y()
        visible_slots = 6
        base_index = int(self._position)
        fractional = self._position - base_index

        for offset in range(-visible_slots, visible_slots + 1):
            slot_position = offset - fractional
            y = center_y + (slot_position * row_height)
            if y < window_rect.top() - row_height or y > window_rect.bottom() + row_height:
                continue

            distance = min(abs(slot_position), 3.2)
            depth = max(0.0, 1.0 - (distance / 3.2))
            scale = 0.72 + (depth * 0.34)
            alpha = 0.18 + (depth * 0.82)
            inset = 30 + ((1.0 - depth) * 72)
            item_rect = QRectF(
                window_rect.left() + inset,
                y - ((row_height * scale) / 2),
                window_rect.width() - (inset * 2),
                row_height * scale,
            )
            index = (base_index + offset) % len(self.names)

            if distance < 0.55:
                highlight = QColor(255, 255, 255, int(36 + self._highlight_strength * 46))
                painter.setBrush(highlight)
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawRoundedRect(item_rect.adjusted(-8, 0, 8, 0), 20, 20)

            text_color = QColor(PAPER)
            text_color.setAlphaF(alpha)
            font = QFont("DejaVu Sans")
            font.setBold(True)
            font.setPointSizeF(18 + (depth * 15))
            painter.setFont(font)
            painter.setPen(text_color)
            painter.drawText(item_rect, int(Qt.AlignmentFlag.AlignCenter), self.names[index])

        fade_height = int(window_rect.height() * 0.20)
        top_fade = QRectF(window_rect.left(), window_rect.top(), window_rect.width(), fade_height)
        bottom_fade = QRectF(
            window_rect.left(),
            window_rect.bottom() - fade_height,
            window_rect.width(),
            fade_height,
        )
        top_gradient = QLinearGradient(top_fade.topLeft(), top_fade.bottomLeft())
        top_gradient.setColorAt(0.0, QColor(15, 18, 23, 235))
        top_gradient.setColorAt(1.0, QColor(15, 18, 23, 0))
        bottom_gradient = QLinearGradient(bottom_fade.topLeft(), bottom_fade.bottomLeft())
        bottom_gradient.setColorAt(0.0, QColor(15, 18, 23, 0))
        bottom_gradient.setColorAt(1.0, QColor(15, 18, 23, 235))
        painter.setBrush(top_gradient)
        painter.drawRect(top_fade)
        painter.setBrush(bottom_gradient)
        painter.drawRect(bottom_fade)
        painter.restore()

        center_band = QRectF(
            window_rect.left() + 18,
            center_y - (row_height * 0.52),
            window_rect.width() - 36,
            row_height * 1.04,
        )
        band_fill = QColor("#A98B58")
        band_fill.setAlphaF(0.08 + self._highlight_strength * 0.10)
        painter.setBrush(band_fill)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(center_band, 18, 18)


class LeverWidget(QWidget):
    pulled = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setMinimumSize(300, 640)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        self._handle_offset = 0.0
        self.drag_active = False
        self.disabled = False
        self.animation_in_progress = False
        self.drag_start_pos = QPoint()
        self.pull_threshold = 0.72
        self.pull_animation = None
        self.spring_animation = None

    def get_handle_offset(self) -> float:
        return self._handle_offset

    def set_handle_offset(self, value: float) -> None:
        self._handle_offset = max(0.0, min(1.0, value))
        self.update()

    handle_offset = pyqtProperty(float, get_handle_offset, set_handle_offset)

    def set_enabled_state(self, enabled: bool) -> None:
        self.disabled = not enabled
        self.update()

    def pivot_center(self) -> QPoint:
        housing_rect = QRectF((self.width() - 176) / 2, (self.height() * 0.50) - 82, 176, 164)
        return QPoint(int(housing_rect.center().x()), int(housing_rect.center().y()))

    def travel_bounds(self) -> tuple[float, float]:
        return 54.0, float(self.height() - 48)

    def shaft_rect(self) -> QRectF:
        top, bottom = self.travel_bounds()
        pivot = self.pivot_center()
        return QRectF(pivot.x() - 42, top, 84, max(40.0, bottom - top))

    def handle_center(self) -> QPoint:
        pivot = self.pivot_center()
        top, bottom = self.travel_bounds()
        y = top + (self._handle_offset * (bottom - top))
        return QPoint(int(pivot.x()), int(y))

    def handle_radius(self) -> int:
        return max(34, min(self.width(), self.height()) // 7)

    def handle_hit(self, pos: QPoint) -> bool:
        center = self.handle_center()
        radius = self.handle_radius() + 18
        expanded = QRectF(center.x() - radius, center.y() - radius, radius * 2, radius * 2)
        return expanded.contains(float(pos.x()), float(pos.y()))

    def mousePressEvent(self, event) -> None:
        if self.disabled or self.animation_in_progress:
            return
        if event.button() == Qt.MouseButton.LeftButton:
            if self.handle_hit(event.position().toPoint()):
                self.drag_active = True
                self.drag_start_pos = event.position().toPoint()
                event.accept()
                return
            self.animate_full_pull()
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:
        if not self.drag_active or self.disabled or self.animation_in_progress:
            return
        top, bottom = self.travel_bounds()
        local_y = max(top, min(event.position().y(), bottom))
        self.set_handle_offset((local_y - top) / (bottom - top))
        if self._handle_offset >= 0.98:
            self.trigger_pull()

    def mouseReleaseEvent(self, event) -> None:
        if not self.drag_active:
            super().mouseReleaseEvent(event)
            return
        moved_distance = (event.position().toPoint() - self.drag_start_pos).manhattanLength()
        self.drag_active = False
        if self._handle_offset >= self.pull_threshold:
            self.trigger_pull()
        elif moved_distance < 10:
            self.animate_full_pull()
        else:
            self.spring_back()
        event.accept()

    def mouseDoubleClickEvent(self, event) -> None:
        if self.disabled or self.animation_in_progress:
            return
        if event.button() == Qt.MouseButton.LeftButton:
            self.animate_full_pull()
            event.accept()

    def trigger_pull(self) -> None:
        if self.animation_in_progress or self.disabled:
            return
        self.drag_active = False
        self.animation_in_progress = True
        self.disabled = True
        self.pull_animation = QPropertyAnimation(self, b"handle_offset", self)
        self.pull_animation.setDuration(120)
        self.pull_animation.setStartValue(self._handle_offset)
        self.pull_animation.setEndValue(1.0)
        self.pull_animation.setEasingCurve(QEasingCurve.Type.InQuad)
        self.pull_animation.finished.connect(self.on_pull_complete, Qt.ConnectionType.SingleShotConnection)
        self.pull_animation.start()

    def animate_full_pull(self) -> None:
        if self.disabled or self.animation_in_progress:
            return
        self.animation_in_progress = True
        self.disabled = True
        self.pull_animation = QPropertyAnimation(self, b"handle_offset", self)
        self.pull_animation.setDuration(260)
        self.pull_animation.setStartValue(0.0)
        self.pull_animation.setEndValue(1.0)
        self.pull_animation.setEasingCurve(QEasingCurve.Type.InOutBack)
        self.pull_animation.finished.connect(self.on_pull_complete, Qt.ConnectionType.SingleShotConnection)
        self.pull_animation.start()

    def on_pull_complete(self) -> None:
        self.pulled.emit()
        self.spring_back()

    def spring_back(self) -> None:
        self.spring_animation = QPropertyAnimation(self, b"handle_offset", self)
        self.spring_animation.setDuration(500)
        self.spring_animation.setStartValue(self._handle_offset)
        self.spring_animation.setEndValue(0.0)
        self.spring_animation.setEasingCurve(QEasingCurve.Type.OutElastic)
        self.spring_animation.finished.connect(self.on_spring_complete, Qt.ConnectionType.SingleShotConnection)
        self.spring_animation.start()

    def on_spring_complete(self) -> None:
        self.animation_in_progress = False
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), Qt.GlobalColor.transparent)

        accent = QColor("#9F78B8" if self.disabled else ACCENT_PURPLE)
        base_color = QColor("#434A54")
        rail_color = QColor("#BFC5CC")
        shadow_color = QColor(0, 0, 0, 65)
        width = self.width()
        height = self.height()

        housing_rect = QRectF((width - 176) / 2, (height * 0.50) - 82, 176, 164)
        pivot_center = QPoint(int(housing_rect.center().x()), int(housing_rect.center().y()))
        handle_center = self.handle_center()
        handle_radius = self.handle_radius()
        shaft_x = pivot_center.x()
        upper_shaft_bottom = handle_center.y() - handle_radius + 14
        housing_inner = housing_rect.adjusted(16, 16, -16, -16)
        guide_rect = QRectF(shaft_x - 42, housing_rect.top() - 10, 84, housing_rect.height() + 20)
        pivot_ring = QRectF(pivot_center.x() - 46, pivot_center.y() - 46, 92, 92)
        pivot_core = QRectF(pivot_center.x() - 28, pivot_center.y() - 28, 56, 56)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(shadow_color)
        painter.drawRoundedRect(housing_rect.adjusted(10, 12, 12, 14), 32, 32)
        painter.setBrush(QColor("#2A2F36"))
        painter.drawRoundedRect(housing_rect.adjusted(-8, -8, 8, 8), 32, 32)
        painter.setBrush(base_color)
        painter.drawRoundedRect(housing_rect, 28, 28)
        painter.setBrush(QColor("#59616D"))
        painter.drawRoundedRect(housing_inner, 22, 22)
        painter.setBrush(QColor(255, 255, 255, 16))
        painter.drawRoundedRect(housing_inner.adjusted(10, 10, -10, -58), 14, 14)
        painter.setBrush(QColor("#2B3038"))
        painter.drawRoundedRect(guide_rect, 28, 28)

        shaft_pen = QPen(rail_color, 22)
        shaft_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(shaft_pen)
        painter.drawLine(shaft_x, pivot_center.y(), shaft_x, upper_shaft_bottom)

        painter.setPen(QPen(QColor(255, 255, 255, 55), 5))
        painter.drawLine(
            shaft_x - 5,
            pivot_center.y() + 12,
            shaft_x - 5,
            max(pivot_center.y() + 20, upper_shaft_bottom - 8),
        )

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#9098A4"))
        painter.drawEllipse(pivot_ring)
        painter.setBrush(QColor("#313740"))
        painter.drawEllipse(pivot_ring.adjusted(6, 6, -6, -6))
        painter.setBrush(QColor("#DEE3E8"))
        painter.drawEllipse(pivot_core)
        painter.setBrush(QColor("#8A919B"))
        painter.drawEllipse(pivot_core.adjusted(12, 12, -12, -12))

        painter.setBrush(QColor(0, 0, 0, 70))
        painter.drawEllipse(QPoint(handle_center.x() + 4, handle_center.y() + 6), handle_radius, handle_radius)
        painter.setBrush(accent)
        painter.drawEllipse(QPoint(handle_center.x(), handle_center.y()), handle_radius, handle_radius)
        painter.setBrush(QColor("#8E69A6" if self.disabled else "#D694F7"))
        painter.drawEllipse(
            QPoint(handle_center.x(), handle_center.y()),
            max(12, handle_radius - 7),
            max(12, handle_radius - 7),
        )
        painter.setBrush(QColor(255, 255, 255, 36))
        painter.drawEllipse(
            QPoint(handle_center.x(), handle_center.y()),
            max(8, handle_radius - 15),
            max(8, handle_radius - 15),
        )
        painter.setBrush(QColor(255, 255, 255, 120))
        painter.drawEllipse(
            QPoint(handle_center.x() - (handle_radius // 3), handle_center.y() - (handle_radius // 3)),
            max(6, handle_radius // 3),
            max(6, handle_radius // 3),
        )
