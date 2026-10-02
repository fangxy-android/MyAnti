"""Floating Status Pill / Capsule attached below the pet."""
from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QFrame
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QFont, QColor, QGuiApplication
from engine.pet_state import PetState, StateMachine

class StatusPill(QWidget):
    def __init__(self, state_machine: StateMachine, parent=None):
        super().__init__(parent)
        self.state_machine = state_machine
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool |
            Qt.WindowType.SubWindow
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

        self._init_ui()
        self.state_machine.register_listener(self._on_state_changed)
        self.update_state(self.state_machine.current_state)

    def _init_ui(self):
        self.setFixedSize(130, 28)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.card = QFrame(self)
        self.card.setObjectName("pillCard")
        card_layout = QHBoxLayout(self.card)
        card_layout.setContentsMargins(8, 2, 8, 2)
        card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.label = QLabel("● 待机中")
        self.label.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        card_layout.addWidget(self.label)

        layout.addWidget(self.card)

    def update_state(self, state: PetState):
        info = {
            PetState.IDLE: ("#2ECC71", "● 待机中"),
            PetState.THINKING: ("#F1C40F", "● 思考中"),
            PetState.WORKING: ("#00F0FF", "● 编码中"),
            PetState.DONE: ("#2ECC71", "● 任务完成"),
            PetState.ERROR: ("#FF7675", "● 遇到错误"),
            PetState.WAITING: ("#E67E22", "● 等待确认"),
            PetState.CLICKED: ("#E84393", "● 互动中"),
            PetState.SLEEP: ("#7F8C8D", "● 休眠中")
        }
        color, text = info.get(state, ("#00F0FF", "● 状态正常"))
        self.label.setText(text)
        self.label.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 11px;")
        self.card.setStyleSheet(f"""
            QFrame#pillCard {{
                background-color: rgba(15, 23, 42, 0.92);
                border: 1px solid {color};
                border-radius: 12px;
            }}
        """)

    def _on_state_changed(self, old_state: PetState, new_state: PetState):
        self.update_state(new_state)

    def follow_pet(self, pet_pos: QPoint, pet_width: int, pet_height: int):
        screen = QGuiApplication.primaryScreen().availableGeometry()
        x = pet_pos.x() + (pet_width - self.width()) // 2
        y = pet_pos.y() + pet_height + 2
        if y + self.height() > screen.bottom():
            y = pet_pos.y() - self.height() - 2
        x = max(screen.left() + 4, min(x, screen.right() - self.width() - 4))
        self.move(x, y)
