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

    def __init__(self, state_machine: StateMachine, parent=None):
        super().__init__(parent)
        self.state_machine = state_machine
        self.pomodoro_timer = QTimer(self)
        self.pomodoro_timer.timeout.connect(self._on_pomodoro_tick)
        self.pomodoro_seconds_left = 0
        self.pomodoro_total_seconds = 25 * 60
        self.pomodoro_active = False

        self._state_buttons = {}
        self._char_buttons = {}

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
        self.setFixedSize(400, 600)

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Container Card with Frosted Dark Glassmorphism
        card = QFrame(self)
        card.setObjectName("mainCard")
        card.setStyleSheet("""
            QFrame#mainCard {
                background-color: rgba(15, 23, 42, 0.97);
                border: 1.5px solid rgba(0, 240, 255, 0.5);
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
                padding: 6px 12px;
                font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
                font-size: 12px;
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
                padding: 8px 12px;
                font-size: 13px;
                font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
            }
            QLineEdit:focus {
                border: 1.5px solid #00F0FF;
            }
        """)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(18, 16, 18, 16)
        card_layout.setSpacing(12)

        # 1. Header: Title + Close Button
        header = QHBoxLayout()
        title = QLabel("✨ Codex Pet 控制台")
        title.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        title.setStyleSheet("color: #00F0FF; font-weight: bold;")

        close_btn = QPushButton("✕")
        close_btn.setFixedSize(28, 28)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                font-size: 15px;
                color: #94A3B8;
            }
            QPushButton:hover {
                background-color: #EF4444;
                color: white;
                border-radius: 14px;
            }
        """)
        close_btn.clicked.connect(self.hide)

        header.addWidget(title)
        header.addStretch()
        header.addWidget(close_btn)
        card_layout.addLayout(header)

        # 2. Live Status Badge Card
        status_box = QFrame()
        status_box.setStyleSheet("""
            QFrame {
                background-color: #1E293B;
                border: 1px solid #334155;
                border-radius: 8px;
                padding: 4px;
            }
        """)
        status_box_layout = QHBoxLayout(status_box)
        status_box_layout.setContentsMargins(10, 6, 10, 6)

        self.char_tag = QLabel(f"🐾 当前: {cfg.get('character', 'dewey').capitalize()}")
        self.char_tag.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.char_tag.setStyleSheet("color: #38BDF8;")

        self.status_chip = QLabel("● 待机中")
        self.status_chip.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.status_chip.setStyleSheet("color: #2ECC71; font-weight: bold;")

        status_box_layout.addWidget(self.char_tag)
        status_box_layout.addStretch()
        status_box_layout.addWidget(self.status_chip)
        card_layout.addWidget(status_box)

        # 3. State Triggers Grid (Large, crisp, high contrast)
        state_label = QLabel("⚡ 状态切换 (AI 状态实时测试)")
        state_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
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
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: #1E293B;
                    color: #F8FAFC;
                    font-size: 11px;
                    font-weight: 600;
                    padding: 8px 6px;
                    border: 1px solid #334155;
                }}
                QPushButton:hover {{
                    border-color: {col};
                    color: {col};
                }}
            """)
            btn.clicked.connect(lambda checked, s=st, t=timeout: self._trigger_state(s, t))
            self._state_buttons[st] = btn
            r = idx // 2
            c = idx % 2
            state_grid.addWidget(btn, r, c)

        card_layout.addLayout(state_grid)

        # 4. Character Switcher
        char_label = QLabel("🐾 切换桌宠形象")
        char_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        char_label.setStyleSheet("color: #E2E8F0;")
        card_layout.addWidget(char_label)

        char_row = QHBoxLayout()
        char_row.setSpacing(6)
        char_emojis = {
            "dewey": "🦆 整理鸭",
            "fireball": "🔥 火焰",
            "codebot": "🤖 机人",
            "neko": "🐱 猫猫",
            "slime": "🍮 史莱姆"
        }
        for char_info in list_characters():
            cid = char_info["id"]
            name = char_emojis.get(cid, cid)
            btn = QPushButton(name)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    font-size: 11px;
                    font-weight: bold;
                    padding: 6px 4px;
                }
            """)
            btn.clicked.connect(lambda checked, name=cid: self._switch_character(name))
            self._char_buttons[cid] = btn
            char_row.addWidget(btn)
        card_layout.addLayout(char_row)

        # 5. Speech Bubble & Quick Broadcast Input
        say_label = QLabel("💬 对话气泡广播")
        say_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        say_label.setStyleSheet("color: #E2E8F0;")
        card_layout.addWidget(say_label)

        say_layout = QHBoxLayout()
        self.say_input = QLineEdit()
        self.say_input.setPlaceholderText("输入让桌宠说的话，按回车发送...")
        self.say_input.returnPressed.connect(self._send_say)

        say_btn = QPushButton("发送")
        say_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        say_btn.setFixedWidth(60)
        say_btn.setStyleSheet("""
            QPushButton {
                background-color: #0284C7;
                border-color: #38BDF8;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0369A1;
            }
        """)
        say_btn.clicked.connect(self._send_say)

        say_layout.addWidget(self.say_input)
        say_layout.addWidget(say_btn)
        card_layout.addLayout(say_layout)

        # Presets row
        preset_row = QHBoxLayout()
        preset_row.setSpacing(6)
        presets = [
            ("🚀 开始构建", "正在编译核心模块中..."),
            ("✅ 测试全过", "所有 42 项单元测试通过！🎉"),
            ("🍵 喝水休息", "写代码辛苦啦，起来活动活动吧~"),
            ("🐛 发现Bug", "发现 1 处空指针异常，正在排查！")
        ]
        for tag, text in presets:
            btn = QPushButton(tag)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("font-size: 10px; padding: 4px 6px; color: #94A3B8;")
            btn.clicked.connect(lambda checked, t=text: self.say_requested.emit(t, "info"))
            preset_row.addWidget(btn)
        card_layout.addLayout(preset_row)

        # 6. Pomodoro Focus Clock
        pomo_layout = QHBoxLayout()
        self.pomo_btn = QPushButton("🍅 开启 25 分钟专注工作")
        self.pomo_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.pomo_btn.setStyleSheet("""
            QPushButton {
                background-color: #D97706;
                border-color: #F59E0B;
                color: #FFFFFF;
                font-weight: bold;
                padding: 8px 12px;
            }
            QPushButton:hover {
                background-color: #B45309;
            }
        """)
        self.pomo_btn.clicked.connect(self._toggle_pomodoro)
        pomo_layout.addWidget(self.pomo_btn)
        card_layout.addLayout(pomo_layout)

        # 7. Preferences: Scale, Sound, Top, Pill Toggle
        pref_row = QHBoxLayout()
        pref_row.setSpacing(6)

        sound_val = cfg.get("sound_enabled", True)
        sound_btn = QPushButton("🔊 音效: 开" if sound_val else "🔇 音效: 关")
        sound_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        sound_btn.clicked.connect(lambda: self._toggle_sound(sound_btn))

        top_val = cfg.get("always_on_top", True)
        top_btn = QPushButton("📌 置顶: 开" if top_val else "置顶: 关")
        top_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        top_btn.clicked.connect(lambda: self._toggle_top(top_btn))

        pill_btn = QPushButton("🏷️ 状态胶囊")
        pill_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        pill_btn.clicked.connect(lambda: self.status_pill_toggled.emit(True))

        pref_row.addWidget(sound_btn)
        pref_row.addWidget(top_btn)
        pref_row.addWidget(pill_btn)
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
        sound_player.play("click")
        self.character_changed.emit(name)
        char = get_character(name)
        self.char_tag.setText(f"🐾 当前: {char.display_name}")
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
            self.pomo_btn.setText(f"🍅 专注中 (25:00) - 点击取消")
            self.state_machine.set_state(PetState.WORKING)
            self.say_requested.emit("开始 25 分钟专注！桌宠全力陪你写代码~", "working")
            sound_player.play("done")
        else:
            self.pomodoro_active = False
            self.pomodoro_timer.stop()
            self.pomo_btn.setText("🍅 开启 25 分钟专注工作")
            self.state_machine.set_state(PetState.IDLE)
            self.say_requested.emit("专注已暂停，随时准备继续！", "info")

    def _on_pomodoro_tick(self):
        if self.pomodoro_seconds_left > 0:
            self.pomodoro_seconds_left -= 1
            m = self.pomodoro_seconds_left // 60
            s = self.pomodoro_seconds_left % 60
            self.pomo_btn.setText(f"🍅 专注中 ({m:02d}:{s:02d}) - 点击取消")
        else:
            self.pomodoro_active = False
            self.pomodoro_timer.stop()
            self.pomo_btn.setText("🍅 开启 25 分钟专注工作")
            self.state_machine.set_state(PetState.DONE, timeout_sec=6.0)
            self.say_requested.emit("🎉 专注时间结束！太棒啦，起来喝杯水吧！", "success")
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
        btn.setText("📌 置顶: 开" if new_val else "置顶: 关")

    def _on_state_updated(self, old_state: PetState, new_state: PetState):
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
