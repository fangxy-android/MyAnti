"""Codex Quick Chat & Command Palette - Sleek floating control drawer."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit,
    QComboBox, QSlider, QFrame, QScrollArea, QTabWidget, QGridLayout
)
from PySide6.QtCore import Qt, Signal, QTimer, QPoint
from PySide6.QtGui import QColor, QFont, QIcon, QPainter, QBrush, QPen

from engine.pet_state import PetState, StateMachine
from graphics.characters import list_characters, get_character
from engine.sound import sound_player
from config import cfg

class QuickBar(QWidget):
    character_changed = Signal(str)
    scale_changed = Signal(float)
    say_requested = Signal(str, str)

    def __init__(self, state_machine: StateMachine, parent=None):
        super().__init__(parent)
        self.state_machine = state_machine
        self.pomodoro_timer = QTimer(self)
        self.pomodoro_timer.timeout.connect(self._on_pomodoro_tick)
        self.pomodoro_seconds_left = 0
        self.pomodoro_total_seconds = 25 * 60
        self.pomodoro_active = False

        self._init_window()
        self._init_ui()
        self.state_machine.register_listener(self._on_state_updated)

    def _init_window(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(380, 520)

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Container card with dark glassmorphism
        card = QFrame(self)
        card.setObjectName("card")
        card.setStyleSheet("""
            QFrame#card {
                background-color: rgba(26, 32, 44, 0.95);
                border: 1.5px solid rgba(0, 206, 201, 0.4);
                border-radius: 16px;
            }
            QLabel {
                color: #ECEFF1;
                font-family: 'Segoe UI', 'Microsoft YaHei';
            }
            QPushButton {
                background-color: #2D3748;
                color: #EDF2F7;
                border: 1px solid #4A5568;
                border-radius: 8px;
                padding: 6px 12px;
                font-family: 'Segoe UI', 'Microsoft YaHei';
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #319795;
                border-color: #4FD1C5;
                color: #FFFFFF;
            }
            QPushButton:pressed {
                background-color: #285E61;
            }
            QLineEdit {
                background-color: #1A202C;
                border: 1px solid #4A5568;
                border-radius: 8px;
                color: #FFFFFF;
                padding: 6px 10px;
                font-family: 'Segoe UI', 'Microsoft YaHei';
            }
            QLineEdit:focus {
                border: 1px solid #4FD1C5;
            }
        """)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 16, 16, 16)
        card_layout.setSpacing(12)

        # Header: Title + Close Button
        header_layout = QHBoxLayout()
        title_label = QLabel("✨ Codex Pet 控制台")
        title_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #4FD1C5;")

        close_btn = QPushButton("✕")
        close_btn.setFixedSize(28, 28)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                font-size: 14px;
                color: #A0AEC0;
            }
            QPushButton:hover {
                background-color: #E53E3E;
                color: white;
                border-radius: 14px;
            }
        """)
        close_btn.clicked.connect(self.hide)

        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(close_btn)
        card_layout.addLayout(header_layout)

        # Current State Badge
        self.status_badge = QLabel("状态: 待机中")
        self.status_badge.setStyleSheet("""
            background-color: #2D3748;
            border-left: 3px solid #4FD1C5;
            padding: 6px 10px;
            border-radius: 4px;
            color: #E2E8F0;
            font-size: 11px;
        """)
        card_layout.addWidget(self.status_badge)

        # Quick State Trigger Buttons Grid
        state_group_label = QLabel("⚡ 快速状态切换 (AI 状态测试)")
        state_group_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        state_group_label.setStyleSheet("color: #CBD5E0;")
        card_layout.addWidget(state_group_label)

        state_grid = QGridLayout()
        state_grid.setSpacing(6)

        states = [
            ("😴 待机", PetState.IDLE, None),
            ("💭 思考", PetState.THINKING, 4.0),
            ("⚡ 编码", PetState.WORKING, 5.0),
            ("🎉 完成", PetState.DONE, 4.0),
            ("⚠️ 报错", PetState.ERROR, 4.0),
            ("🔔 提醒", PetState.WAITING, 4.0),
            ("💖 互动", PetState.CLICKED, 2.5),
            ("💤 休眠", PetState.SLEEP, None)
        ]

        for idx, (label, st, timeout) in enumerate(states):
            btn = QPushButton(label)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #2D3748;
                    font-size: 11px;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #38B2AC;
                    color: white;
                }
            """)
            btn.clicked.connect(lambda checked, s=st, t=timeout: self._trigger_state(s, t))
            r = idx // 4
            c = idx % 4
            state_grid.addWidget(btn, r, c)

        card_layout.addLayout(state_grid)

        # Character Switcher
        char_label = QLabel("🐾 选择桌宠形象")
        char_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        char_label.setStyleSheet("color: #CBD5E0;")
        card_layout.addWidget(char_label)

        char_layout = QHBoxLayout()
        char_layout.setSpacing(6)
        for char_info in list_characters():
            btn = QPushButton(char_info["display_name"].split()[0])
            btn.setToolTip(f"{char_info['display_name']}\n{char_info['description']}")
            btn.setStyleSheet("""
                QPushButton {
                    font-size: 10px;
                    padding: 4px 6px;
                }
            """)
            btn.clicked.connect(lambda checked, name=char_info["id"]: self._switch_character(name))
            char_layout.addWidget(btn)
        card_layout.addLayout(char_layout)

        # Quick Say / Toast Input
        say_label = QLabel("💬 桌宠对话 / 气泡测试")
        say_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        say_label.setStyleSheet("color: #CBD5E0;")
        card_layout.addWidget(say_label)

        say_layout = QHBoxLayout()
        self.say_input = QLineEdit()
        self.say_input.setPlaceholderText("输入想让桌宠说的话...")
        self.say_input.returnPressed.connect(self._send_say)

        say_btn = QPushButton("发送")
        say_btn.setFixedWidth(50)
        say_btn.clicked.connect(self._send_say)

        say_layout.addWidget(self.say_input)
        say_layout.addWidget(say_btn)
        card_layout.addLayout(say_layout)

        # Productivity Tools: Pomodoro Timer
        pomo_layout = QHBoxLayout()
        self.pomo_btn = QPushButton("🍅 开启25分钟专注")
        self.pomo_btn.setStyleSheet("""
            QPushButton {
                background-color: #DD6B20;
                border-color: #ED8936;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #C05621;
            }
        """)
        self.pomo_btn.clicked.connect(self._toggle_pomodoro)
        pomo_layout.addWidget(self.pomo_btn)
        card_layout.addLayout(pomo_layout)

        # Footer settings: Size scale & API info
        footer_layout = QHBoxLayout()
        sound_btn = QPushButton("🔊 音效: 开" if cfg.get("sound_enabled") else "🔇 音效: 关")
        sound_btn.clicked.connect(lambda: self._toggle_sound(sound_btn))

        top_btn = QPushButton("📌 置顶" if cfg.get("always_on_top") else "置顶: 关")
        top_btn.clicked.connect(lambda: self._toggle_top(top_btn))

        footer_layout.addWidget(sound_btn)
        footer_layout.addWidget(top_btn)
        card_layout.addLayout(footer_layout)

        # API info notice
        api_notice = QLabel(f"🌐 外部集成 API: http://127.0.0.1:{cfg.get('server_port', 8765)}")
        api_notice.setStyleSheet("font-size: 10px; color: #718096;")
        card_layout.addWidget(api_notice)

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
        sound_player.play("click")
        self.character_changed.emit(name)
        char = get_character(name)
        self.say_requested.emit(f"已切换为 {char.display_name}！", "info")

    def _send_say(self):
        text = self.say_input.text().strip()
        if text:
            sound_player.play("notify")
            self.say_requested.emit(text, "info")
            self.say_input.clear()

    def _toggle_pomodoro(self):
        if not self.pomodoro_active:
            self.pomodoro_active = True
            self.pomodoro_seconds_left = self.pomodoro_total_seconds
            self.pomodoro_timer.start(1000)
            self.pomo_btn.setText(f"🍅 专注中 (25:00)")
            self.state_machine.set_state(PetState.WORKING)
            self.say_requested.emit("开始25分钟专注工作！我会陪着你写代码~", "info")
            sound_player.play("done")
        else:
            self.pomodoro_active = False
            self.pomodoro_timer.stop()
            self.pomo_btn.setText("🍅 开启25分钟专注")
            self.state_machine.set_state(PetState.IDLE)
            self.say_requested.emit("专注已暂停。", "info")

    def _on_pomodoro_tick(self):
        if self.pomodoro_seconds_left > 0:
            self.pomodoro_seconds_left -= 1
            m = self.pomodoro_seconds_left // 60
            s = self.pomodoro_seconds_left % 60
            self.pomo_btn.setText(f"🍅 专注中 ({m:02d}:{s:02d})")
        else:
            self.pomodoro_active = False
            self.pomodoro_timer.stop()
            self.pomo_btn.setText("🍅 开启25分钟专注")
            self.state_machine.set_state(PetState.DONE, timeout_sec=6.0)
            self.say_requested.emit("🎉 专注时间结束！太棒啦，起来活动一下、喝杯水吧！", "success")
            sound_player.play("done")

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
        btn.setText("📌 置顶" if new_val else "置顶: 关")

    def _on_state_updated(self, old_state: PetState, new_state: PetState):
        self.status_badge.setText(f"状态: {self.state_machine.state_description}")
