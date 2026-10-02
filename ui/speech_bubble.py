"""High-definition floating comic Speech Bubble with crisp typography and status tags."""
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFrame, QGraphicsDropShadowEffect
from PySide6.QtCore import Qt, QPoint, QTimer, QRectF
from PySide6.QtGui import QPainter, QColor, QPainterPath, QFont, QPen, QGuiApplication
from config import cfg

class SpeechBubble(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

        self.hide_timer = QTimer(self)
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self.hide)

        self.mood = "info"
        self._init_ui()

    def _init_ui(self):
        self.setFixedWidth(280)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(6, 6, 6, 14) # Bottom margin for pointer arrow
        main_layout.setSpacing(0)

        # Bubble Card Frame
        self.card = QFrame(self)
        self.card.setObjectName("bubbleCard")

        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(12, 10, 12, 10)
        card_layout.setSpacing(4)

        # Tag Header Row: e.g. [● 任务完成]
        self.tag_label = QLabel("● 提示")
        self.tag_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.tag_label.setStyleSheet("color: #00F0FF; font-weight: bold;")
        card_layout.addWidget(self.tag_label)

        # Message Text Body: Crisp, high-contrast, perfectly readable
        self.text_label = QLabel("")
        self.text_label.setWordWrap(True)
        self.text_label.setFont(QFont("Microsoft YaHei", 10, QFont.Weight.Medium))
        self.text_label.setStyleSheet("""
            color: #FFFFFF;
            line-height: 1.4;
            font-size: 13px;
        """)
        card_layout.addWidget(self.text_label)

        main_layout.addWidget(self.card)

        # Apply default style
        self._apply_style("info")

    def _apply_style(self, mood: str):
        self.mood = mood
        palettes = {
            "info": {
                "border": "rgba(0, 240, 255, 0.6)",
                "tag_color": "#00F0FF",
                "tag_text": "● 提示 (Info)"
            },
            "success": {
                "border": "rgba(46, 204, 113, 0.7)",
                "tag_color": "#2ECC71",
                "tag_text": "● 完成 (Done 🎉)"
            },
            "error": {
                "border": "rgba(231, 76, 60, 0.7)",
                "tag_color": "#FF7675",
                "tag_text": "● 报错 (Error ⚠️)"
            },
            "warning": {
                "border": "rgba(243, 156, 18, 0.7)",
                "tag_color": "#F39C12",
                "tag_text": "● 提醒 (Attention)"
            },
            "working": {
                "border": "rgba(52, 152, 219, 0.7)",
                "tag_color": "#54A0FF",
                "tag_text": "● 编写中 (Working ⚡)"
            }
        }
        pal = palettes.get(mood, palettes["info"])
        self.tag_label.setText(pal["tag_text"])
        self.tag_label.setStyleSheet(f"color: {pal['tag_color']}; font-weight: bold; font-size: 11px;")

        self.card.setStyleSheet(f"""
            QFrame#bubbleCard {{
                background-color: rgba(15, 23, 42, 0.96);
                border: 1.5px solid {pal['border']};
                border-radius: 12px;
            }}
        """)

    def show_message(self, text: str, mood: str = "info", duration_sec: float = None, target_pos: QPoint = None):
        self._apply_style(mood)
        self.text_label.setText(text)

        if duration_sec is None:
            duration_sec = cfg.get("speech_bubble_duration", 4.5)

        # Adjust width and height to fit text nicely
        self.card.adjustSize()
        self.adjustSize()

        if target_pos:
            screen = QGuiApplication.primaryScreen().availableGeometry()
            bx = target_pos.x() - self.width() // 2
            by = target_pos.y() - self.height() - 6
            if by < screen.top() + 10:
                by = target_pos.y() + 140
            bx = max(screen.left() + 10, min(bx, screen.right() - self.width() - 10))
            self.move(bx, by)

        self.show()
        self.raise_()
        self.hide_timer.start(int(duration_sec * 1000))

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.hide_timer.stop()
            self.hide()

    def paintEvent(self, event):
        # Draw comic pointer triangle at the bottom center
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        arrow_w = 14
        arrow_h = 10
        cx = self.width() / 2
        cy = self.height() - 14

        border_colors = {
            "info": QColor("#00F0FF"),
            "success": QColor("#2ECC71"),
            "error": QColor("#FF7675"),
            "warning": QColor("#F39C12"),
            "working": QColor("#54A0FF")
        }
        b_col = border_colors.get(self.mood, border_colors["info"])

        path = QPainterPath()
        path.moveTo(cx - arrow_w / 2, cy)
        path.lineTo(cx, cy + arrow_h)
        path.lineTo(cx + arrow_w / 2, cy)
        path.closeSubpath()

        painter.setBrush(QColor(15, 23, 42, 245))
        painter.setPen(QPen(b_col, 1.5))
        painter.drawPath(path)
        painter.end()
