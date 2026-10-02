"""Comic-style floating speech bubble with arrow pointer and auto-dismiss."""
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QGraphicsDropShadowEffect
from PySide6.QtCore import Qt, QPoint, QTimer, QRectF
from PySide6.QtGui import QPainter, QColor, QPainterPath, QFont, QPen
from config import cfg

class SpeechBubble(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool |
            Qt.WindowType.SubWindow
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

        self.hide_timer = QTimer(self)
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self.hide)

        self.text = ""
        self.mood = "info" # info, success, error, warning

        self.setFixedWidth(240)
        self.setMinimumHeight(60)

    def show_message(self, text: str, mood: str = "info", duration_sec: float = None, target_pos: QPoint = None):
        self.text = text
        self.mood = mood
        if duration_sec is None:
            duration_sec = cfg.get("speech_bubble_duration", 4.5)

        # Dynamic size based on text length
        line_count = max(1, len(text) // 14 + 1)
        self.setFixedHeight(max(56, 36 + line_count * 20))

        if target_pos:
            # Place bubble above target_pos (top-center of pet)
            bx = target_pos.x() - self.width() // 2
            by = target_pos.y() - self.height() - 8
            self.move(bx, by)

        self.show()
        self.update()
        self.hide_timer.start(int(duration_sec * 1000))

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.hide_timer.stop()
            self.hide()

    def paintEvent(self, event):
        if not self.text:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height() - 12 # Leave bottom for pointer arrow

        # Color schemes based on mood
        bg_colors = {
            "info": QColor(30, 39, 46, 235),
            "success": QColor(22, 60, 42, 235),
            "error": QColor(64, 28, 28, 235),
            "warning": QColor(64, 48, 20, 235)
        }
        border_colors = {
            "info": QColor(0, 206, 201),
            "success": QColor(46, 204, 113),
            "error": QColor(231, 76, 60),
            "warning": QColor(243, 156, 18)
        }

        bg_color = bg_colors.get(self.mood, bg_colors["info"])
        border_color = border_colors.get(self.mood, border_colors["info"])

        # Create rounded bubble path with bottom arrow
        path = QPainterPath()
        radius = 12
        path.addRoundedRect(QRectF(2, 2, w - 4, h - 2), radius, radius)

        # Bottom pointer arrow pointing down towards pet
        arrow_x = w / 2
        path.moveTo(arrow_x - 8, h - 1)
        path.lineTo(arrow_x, h + 10)
        path.lineTo(arrow_x + 8, h - 1)
        path.closeSubpath()

        # Draw fill and border
        painter.setBrush(bg_color)
        painter.setPen(QPen(border_color, 1.5))
        painter.drawPath(path)

        # Draw text
        painter.setPen(QColor(240, 245, 250))
        font = QFont("Microsoft YaHei", 9, QFont.Weight.Medium)
        painter.setFont(font)

        text_rect = QRectF(12, 6, w - 24, h - 10)
        painter.drawText(
            text_rect,
            Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap,
            self.text
        )
        painter.end()
