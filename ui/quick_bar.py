"""Codex Quick Bar & Command Console - Studio Grade Floating Control Drawer."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QFrame, QGridLayout, QProgressBar
)
from PySide6.QtCore import Qt, Signal, QTimer, QPoint
from PySide6.QtGui import QColor, QFont, QCursor

from engine.pet_state import PetState, StateMachine
from graphics.characters import list_characters, get_character
from engine.sound import sound_player
from config import cfg

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

class QuickBar(QWidget):
    character_changed = Signal(str)
    scale_changed = Signal(float)
    say_requested = Signal(str, str)
    status_pill_toggled = Signal(bool)
    top_toggled = Signal(bool)
    sound_toggled = Signal(bool)
    reset_position_requested = Signal()
    wake_requested = Signal()
    sleep_requested = Signal()
    interaction_requested = Signal()

    def __init__(self, state_machine: StateMachine, parent=None):
        super().__init__(parent)
        self.state_machine = state_machine
        self._state_buttons = {}
        self._char_buttons = {}

        self._init_window()
        self._init_ui()
        self.state_machine.register_listener(self._on_state_updated)
        self.refresh_all_ui()

    def _init_window(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(430, 520)

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)

        # Container Card with Frosted Dark Glassmorphism
        card = QFrame(self)
        card.setObjectName("mainCard")
        card.setStyleSheet("""
            QFrame#mainCard {
                background-color: rgba(15, 23, 42, 0.98);
                border: 1.5px solid rgba(0, 240, 255, 0.55);
                border-radius: 16px;
            }
            QLabel {
                color: #F1F5F9;
                font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
            }
            QPushButton {
                background-color: #1E293B;
                color: #E2E8F0;
                border: 1px solid #334155;
                border-radius: 8px;
                padding: 6px 10px;
                font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
                font-size: 11px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #0F766E;
                border-color: #00F0FF;
                color: #FFFFFF;
            }
            QPushButton:pressed {
                background-color: #115E59;
            }
            QLineEdit {
                background-color: #0F172A;
                border: 1px solid #334155;
                border-radius: 8px;
                color: #FFFFFF;
                padding: 7px 10px;
                font-size: 12px;
                font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
            }
            QLineEdit:focus {
                border: 1.5px solid #00F0FF;
            }
        """)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 14, 16, 14)
        card_layout.setSpacing(10)

        # 1. Header: Title + Close Button
        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        title = QLabel("🤖 CodeBot 开发者控制台")
        title.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        title.setStyleSheet("color: #00F0FF; font-weight: bold;")

        close_btn = QPushButton("✕")
        close_btn.setFixedSize(26, 26)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                font-size: 14px;
                color: #94A3B8;
                padding: 0;
            }
            QPushButton:hover {
                background-color: #EF4444;
                color: white;
                border-radius: 13px;
            }
        """)
        close_btn.clicked.connect(self.hide)

        header.addWidget(title)
        header.addStretch()
        header.addWidget(close_btn)
        card_layout.addLayout(header)

        # 2. Live Status & Diagnostics Badge
        status_box = QFrame()
        status_box.setStyleSheet("""
            QFrame {
                background-color: #1E293B;
                border: 1px solid #334155;
                border-radius: 8px;
                padding: 2px;
            }
        """)
        status_box_layout = QVBoxLayout(status_box)
        status_box_layout.setContentsMargins(10, 6, 10, 6)
        status_box_layout.setSpacing(4)

        row1 = QHBoxLayout()
        self.char_tag = QLabel("🤖 形象: 赛博机人 CodeBot")
        self.char_tag.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.char_tag.setStyleSheet("color: #38BDF8;")

        self.status_chip = QLabel("● 待机中")
        self.status_chip.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.status_chip.setStyleSheet("color: #2ECC71; font-weight: bold;")

        row1.addWidget(self.char_tag)
        row1.addStretch()
        row1.addWidget(self.status_chip)
        status_box_layout.addLayout(row1)

        row2 = QHBoxLayout()
        port = cfg.get("server_port", 8765)
        api_tag = QLabel(f"🌐 API: 127.0.0.1:{port} [就绪]")
        api_tag.setFont(QFont("Segoe UI", 9))
        api_tag.setStyleSheet("color: #94A3B8;")

        sync_tag = QLabel("⚡ IDE 实时联动")
        sync_tag.setFont(QFont("Segoe UI", 9))
        sync_tag.setStyleSheet("color: #A78BFA;")

        row2.addWidget(api_tag)
        row2.addStretch()
        row2.addWidget(sync_tag)
        status_box_layout.addLayout(row2)

        card_layout.addWidget(status_box)

        # 3. State Triggers Grid (AI 状态实时切换)
        state_label = QLabel("⚡ 状态切换 (实时反馈)")
        state_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        state_label.setStyleSheet("color: #E2E8F0;")
        card_layout.addWidget(state_label)

        state_grid = QGridLayout()
        state_grid.setSpacing(6)

        states = [
            ("😴 待机 (Idle)", PetState.IDLE, None, "#94A3B8"),
            ("💭 思考 (Thinking)", PetState.THINKING, 4.0, "#F1C40F"),
            ("⚡ 编码 (Working)", PetState.WORKING, 5.0, "#00F0FF"),
            ("🎉 完成 (Done)", PetState.DONE, 4.0, "#2ECC71"),
            ("⚠️ 报错 (Error)", PetState.ERROR, 4.0, "#FF7675"),
            ("🔔 确认 (Waiting)", PetState.WAITING, 4.0, "#F39C12"),
            ("💖 互动 (Clicked)", PetState.CLICKED, 2.5, "#E84393"),
            ("💤 休眠 (Sleep)", PetState.SLEEP, None, "#64748B")
        ]

        for idx, (label, st, timeout, col) in enumerate(states):
            btn = QPushButton(label)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFixedHeight(32)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: #1E293B;
                    color: #F8FAFC;
                    font-size: 11px;
                    font-weight: 600;
                    padding: 3px 6px;
                    border: 1px solid #334155;
                    border-radius: 6px;
                }}
                QPushButton:hover {{
                    border-color: {col};
                    color: {col};
                    background-color: #273549;
                }}
            """)
            btn.clicked.connect(lambda checked, s=st, t=timeout: self._trigger_state(s, t))
            self._state_buttons[st] = (btn, col)
            r = idx // 2
            c = idx % 2
            state_grid.addWidget(btn, r, c)

        card_layout.addLayout(state_grid)

        # 4. Quick Real Actions (Real interactions instead of fake presets)
        action_label = QLabel("🎮 快捷控制")
        action_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        action_label.setStyleSheet("color: #E2E8F0;")
        card_layout.addWidget(action_label)

        act_layout = QHBoxLayout()
        act_layout.setSpacing(6)

        wake_btn = QPushButton("☀️ 唤醒")
        wake_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        wake_btn.setFixedHeight(28)
        wake_btn.setToolTip("唤醒桌宠并切换至待机状态")
        wake_btn.clicked.connect(self._on_wake_clicked)

        sleep_btn = QPushButton("💤 休眠")
        sleep_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        sleep_btn.setFixedHeight(28)
        sleep_btn.setToolTip("让桌宠立即进入休眠省电状态")
        sleep_btn.clicked.connect(self._on_sleep_clicked)

        poke_btn = QPushButton("💖 戳戳")
        poke_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        poke_btn.setFixedHeight(28)
        poke_btn.setToolTip("与桌宠互动戳一戳")
        poke_btn.clicked.connect(self._on_poke_clicked)

        reset_btn = QPushButton("🔄 归位")
        reset_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        reset_btn.setFixedHeight(28)
        reset_btn.setToolTip("重置桌宠到屏幕右下角默认位置")
        reset_btn.clicked.connect(self._on_reset_clicked)

        act_layout.addWidget(wake_btn)
        act_layout.addWidget(sleep_btn)
        act_layout.addWidget(poke_btn)
        act_layout.addWidget(reset_btn)
        card_layout.addLayout(act_layout)

        # 6. Speech Bubble Broadcast Input
        say_label = QLabel("💬 对话气泡广播")
        say_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        say_label.setStyleSheet("color: #E2E8F0;")
        card_layout.addWidget(say_label)

        say_layout = QHBoxLayout()
        say_layout.setSpacing(6)
        self.say_input = QLineEdit()
        self.say_input.setPlaceholderText("输入台词广播给桌宠，按回车发送...")
        self.say_input.returnPressed.connect(self._send_say)

        say_btn = QPushButton("发送")
        say_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        say_btn.setFixedWidth(56)
        say_btn.setFixedHeight(30)
        say_btn.setStyleSheet("""
            QPushButton {
                background-color: #0284C7;
                border-color: #38BDF8;
                font-weight: bold;
                color: #FFFFFF;
            }
            QPushButton:hover {
                background-color: #0369A1;
            }
        """)
        say_btn.clicked.connect(self._send_say)

        say_layout.addWidget(self.say_input)
        say_layout.addWidget(say_btn)
        card_layout.addLayout(say_layout)

        # 7. Preferences: Sound, Top, Pill, Scale
        pref_row = QHBoxLayout()
        pref_row.setSpacing(6)

        sound_val = cfg.get("sound_enabled", True)
        self.sound_btn = QPushButton("🔊 音效: 开" if sound_val else "🔇 音效: 关")
        self.sound_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.sound_btn.setFixedHeight(28)
        self.sound_btn.clicked.connect(lambda: self._toggle_sound(self.sound_btn))

        top_val = cfg.get("always_on_top", True)
        self.top_btn = QPushButton("📌 置顶: 开" if top_val else "置顶: 关")
        self.top_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.top_btn.setFixedHeight(28)
        self.top_btn.clicked.connect(lambda: self._toggle_top(self.top_btn))

        self.pill_btn = QPushButton("🏷️ 胶囊")
        self.pill_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.pill_btn.setFixedHeight(28)
        self.pill_btn.clicked.connect(lambda: self.status_pill_toggled.emit(True))

        curr_scale = float(cfg.get("scale", 2.0))
        self.scale_btn = QPushButton(f"📏 {curr_scale:.1f}x")
        self.scale_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.scale_btn.setFixedHeight(28)
        self.scale_btn.setFixedWidth(64)
        self.scale_btn.setToolTip("点击循环切换尺寸: 1.5x -> 2.0x -> 2.5x -> 3.0x")
        self.scale_btn.clicked.connect(self._cycle_scale)

        pref_row.addWidget(self.sound_btn)
        pref_row.addWidget(self.top_btn)
        pref_row.addWidget(self.pill_btn)
        pref_row.addWidget(self.scale_btn)
        card_layout.addLayout(pref_row)

        main_layout.addWidget(card)

    def _trigger_state(self, state: PetState, timeout: float = None):
        sound_name = "click"
        if state == PetState.DONE:
            sound_name = "done"
        elif state == PetState.ERROR:
            sound_name = "error"
        elif state == PetState.THINKING:
            sound_name = "bubble"
        elif state == PetState.WORKING:
            sound_name = "tick"

        sound_player.play(sound_name)
        self.state_machine.set_state(state, timeout_sec=timeout)

    def _switch_character(self, name: str):
        pass

    def refresh_all_ui(self):
        self.update_state_ui(self.state_machine.current_state)
        self.update_character_ui(cfg.get("character", "codebot"))

    def update_character_ui(self, name: str = "codebot"):
        char = get_character(name)
        self.char_tag.setText(f"🤖 形象: {char.display_name}")


    def update_state_ui(self, new_state: PetState):
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
        col, text = info.get(new_state, ("#00F0FF", "● 正常"))
        self.status_chip.setText(text)
        self.status_chip.setStyleSheet(f"color: {col}; font-weight: bold;")

        for st, (btn, c) in self._state_buttons.items():
            if st == new_state:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: #1E3A5F;
                        border: 1.5px solid {c};
                        color: {c};
                        font-size: 11px;
                        font-weight: bold;
                        border-radius: 6px;
                        padding: 4px 6px;
                    }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: #1E293B;
                        border: 1px solid #334155;
                        color: #E2E8F0;
                        font-size: 11px;
                        font-weight: 600;
                        border-radius: 6px;
                        padding: 4px 6px;
                    }}
                    QPushButton:hover {{
                        border-color: {c};
                        color: {c};
                        background-color: #273549;
                    }}
                """)

    def _send_say(self):
        text = self.say_input.text().strip()
        if text:
            sound_player.play("notify")
            self.say_requested.emit(text, "info")
            self.say_input.clear()

    def _on_wake_clicked(self):
        sound_player.play("click")
        self.wake_requested.emit()

    def _on_sleep_clicked(self):
        sound_player.play("click")
        self.sleep_requested.emit()

    def _on_poke_clicked(self):
        sound_player.play("click")
        self.interaction_requested.emit()

    def _on_reset_clicked(self):
        sound_player.play("click")
        self.reset_position_requested.emit()

    def _cycle_scale(self):
        curr = float(cfg.get("scale", 2.0))
        scale_steps = [1.5, 2.0, 2.5, 3.0]
        try:
            # find closest
            idx = min(range(len(scale_steps)), key=lambda i: abs(scale_steps[i] - curr))
            new_scale = scale_steps[(idx + 1) % len(scale_steps)]
        except Exception:
            new_scale = 2.0
        cfg.set("scale", new_scale)
        self.scale_btn.setText(f"📏 {new_scale:.1f}x")
        self.scale_changed.emit(new_scale)
        sound_player.play("click")

    def _toggle_sound(self, btn: QPushButton):
        curr = cfg.get("sound_enabled", True)
        new_val = not curr
        cfg.set("sound_enabled", new_val)
        btn.setText("🔊 音效: 开" if new_val else "🔇 音效: 关")
        if new_val:
            sound_player.play("click")

    def _toggle_top(self, btn: QPushButton):
        curr = cfg.get("always_on_top", True)
        new_val = not curr
        cfg.set("always_on_top", new_val)
        btn.setText("📌 置顶: 开" if new_val else "置顶: 关")
        self.top_toggled.emit(new_val)

    def _on_state_updated(self, old_state: PetState, new_state: PetState):
        self.update_state_ui(new_state)
