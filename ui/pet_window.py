"""Main transparent floating Pet Window with drag, interactions, and menus."""
from PySide6.QtWidgets import QWidget, QMenu
from PySide6.QtCore import Qt, QPoint, QRect, Signal
from PySide6.QtGui import QPainter, QPixmap, QCursor, QAction, QGuiApplication

from engine.pet_state import PetState, StateMachine
from engine.animation import AnimationEngine
from engine.sound import sound_player
from ui.speech_bubble import SpeechBubble
from ui.quick_bar import QuickBar
from ui.status_pill import StatusPill
from graphics.characters import list_characters, get_character
from config import cfg

class PetWindow(QWidget):
    def __init__(self, state_machine: StateMachine, animation_engine: AnimationEngine):
        super().__init__()
        self.state_machine = state_machine
        self.anim_engine = animation_engine
        self.current_pixmap: QPixmap = None

        self._dragging = False
        self._drag_start_pos = QPoint()
        self._press_global_pos = QPoint()

        self._init_window()
        self._init_helpers()
        self._restore_position()

        # Connect animation updates
        self.anim_engine.frame_changed.connect(self._on_frame_changed)
        self.state_machine.register_listener(self._on_state_changed)
        if hasattr(self.anim_engine, "current_frames") and self.anim_engine.current_frames:
            self.current_pixmap = self.anim_engine.current_frames[self.anim_engine.frame_index]

    def _init_window(self):
        flags = Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool
        if cfg.get("always_on_top", True):
            flags |= Qt.WindowType.WindowStaysOnTopHint

        self.setWindowFlags(flags)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        size = self.anim_engine.pet_size
        self.setFixedSize(size, size)

    def _init_helpers(self):
        # Speech bubble
        self.bubble = SpeechBubble()

        # Status Pill (Clear high-definition status chip under the pet)
        self.pill = StatusPill(self.state_machine)
        if cfg.get("show_status_pill", True):
            self.pill.show()

        # Quick control drawer
        self.quick_bar = QuickBar(self.state_machine)
        self.quick_bar.character_changed.connect(lambda name: self._on_character_changed(name, announce=False))
        self.quick_bar.say_requested.connect(self.say)
        self.quick_bar.status_pill_toggled.connect(self._toggle_pill)
        self.quick_bar.scale_changed.connect(self.set_scale)
        self.quick_bar.reset_position_requested.connect(self._reset_position)
        self.quick_bar.wake_requested.connect(self._wake_pet)
        self.quick_bar.sleep_requested.connect(self._sleep_pet)
        self.quick_bar.interaction_requested.connect(self._handle_pet_click)
        self.quick_bar.top_toggled.connect(self._set_top)

    def _restore_position(self):
        screen = QGuiApplication.primaryScreen().availableGeometry()
        saved_x = cfg.get("window_x", -1)
        saved_y = cfg.get("window_y", -1)

        if saved_x >= 0 and saved_y >= 0 and saved_x < screen.right() - 20 and saved_y < screen.bottom() - 20:
            self.move(saved_x, saved_y)
        else:
            self._reset_position(announce=False)

        self.pill.follow_pet(self.pos(), self.width(), self.height())

    def _reset_position(self, announce: bool = True):
        screen = QGuiApplication.primaryScreen().availableGeometry()
        default_x = screen.right() - self.width() - 80
        default_y = screen.bottom() - self.height() - 70
        self.move(default_x, default_y)
        cfg.set("window_x", default_x)
        cfg.set("window_y", default_y)
        self.pill.follow_pet(self.pos(), self.width(), self.height())
        if announce:
            self.say("已重置到屏幕右下角~ 🤖", "info", 2.5)

    def _wake_pet(self):
        self.state_machine.set_state(PetState.IDLE)
        sound_player.play("notify")
        self.say("呼...醒来啦！今天要做什么？✨", "info", 3.0)

    def _sleep_pet(self):
        self.state_machine.set_state(PetState.SLEEP)
        sound_player.play("click")
        self.say("Zzz... 桌宠进入休眠省电中~ 💤", "info", 3.0)

    def say(self, message: str, mood: str = "info", duration_sec: float = None):
        pet_top_center = QPoint(self.x() + self.width() // 2, self.y())
        self.bubble.show_message(message, mood=mood, duration_sec=duration_sec, target_pos=pet_top_center)

    def _toggle_pill(self, *args):
        curr = self.pill.isVisible()
        new_val = not curr
        cfg.set("show_status_pill", new_val)
        if new_val:
            self.pill.follow_pet(self.pos(), self.width(), self.height())
            self.pill.show()
        else:
            self.pill.hide()

    def _on_frame_changed(self, pixmap: QPixmap):
        self.current_pixmap = pixmap
        size = self.anim_engine.pet_size
        if self.width() != size or self.height() != size:
            self.setFixedSize(size, size)
            self.pill.follow_pet(self.pos(), self.width(), self.height())
        self.update()

    def _on_state_changed(self, old_state: PetState, new_state: PetState):
        if new_state == PetState.CLICKED:
            sound_player.play("click")
        elif new_state == PetState.DONE:
            sound_player.play("done")
        elif new_state == PetState.ERROR:
            sound_player.play("error")
        elif new_state == PetState.THINKING:
            sound_player.play("bubble")
        elif new_state == PetState.WORKING:
            sound_player.play("tick")
        elif new_state == PetState.WAITING:
            sound_player.play("notify")

    def _on_character_changed(self, character_name: str, announce: bool = True):
        self.anim_engine.set_character(character_name)
        size = self.anim_engine.pet_size
        self.setFixedSize(size, size)
        self.pill.follow_pet(self.pos(), self.width(), self.height())
        self.quick_bar.update_character_ui(character_name)
        char = self.anim_engine.current_character
        if announce:
            self.say(f"已切换为 {char.display_name}！✨", "info", 3.0)
        sound_player.play("click")
        self.update()

    def set_scale(self, scale: float):
        self.anim_engine.set_scale(scale)
        size = self.anim_engine.pet_size
        self.setFixedSize(size, size)
        self.pill.follow_pet(self.pos(), self.width(), self.height())
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = True
            self._drag_start_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self._press_global_pos = event.globalPosition().toPoint()
            self.state_machine.touch()

    def mouseMoveEvent(self, event):
        if self._dragging:
            screen = QGuiApplication.primaryScreen().availableGeometry()
            new_pos = event.globalPosition().toPoint() - self._drag_start_pos
            # Clamp position within screen bounds with slight margin
            nx = max(screen.left() - self.width() // 2, min(new_pos.x(), screen.right() - self.width() // 2))
            ny = max(screen.top(), min(new_pos.y(), screen.bottom() - self.height() // 2))
            self.move(nx, ny)
            self.pill.follow_pet(self.pos(), self.width(), self.height())
            # Sync speech bubble if visible
            if self.bubble.isVisible():
                pet_top_center = QPoint(self.x() + self.width() // 2, self.y())
                self.bubble.move(pet_top_center.x() - self.bubble.width() // 2, pet_top_center.y() - self.bubble.height() - 8)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = False
            # Check if this was a click (not a drag)
            release_pos = event.globalPosition().toPoint()
            distance = (release_pos - self._press_global_pos).manhattanLength()
            if distance < 6:
                self._handle_pet_click()

            # Save window position
            cfg.set("window_x", self.x())
            cfg.set("window_y", self.y())

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.toggle_quick_bar()

    def _handle_pet_click(self):
        curr = self.state_machine.current_state
        if curr == PetState.SLEEP:
            self.state_machine.set_state(PetState.IDLE)
            self.say("呼...醒来啦！今天要做什么？✨", "info", 3.0)
        elif curr == PetState.IDLE:
            self.state_machine.set_state(PetState.CLICKED, timeout_sec=2.0)
            self.say("✨ (咕噜噜~ 正在为你加油！)", "info", 2.5)

    def toggle_quick_bar(self):
        if self.quick_bar.isVisible():
            self.quick_bar.hide()
        else:
            # Position quick bar beside the pet
            screen = QGuiApplication.primaryScreen().availableGeometry()
            bx = self.x() + self.width() + 12
            if bx + self.quick_bar.width() > screen.right():
                bx = self.x() - self.quick_bar.width() - 12
            bx = max(screen.left() + 10, bx)
            by = min(self.y(), screen.bottom() - self.quick_bar.height() - 10)
            by = max(screen.top() + 10, by)
            self.quick_bar.move(bx, by)
            self.quick_bar.update_character_ui(self.anim_engine.current_character.name)
            self.quick_bar.update_state_ui(self.state_machine.current_state)
            self.quick_bar.show()
            self.quick_bar.raise_()
            self.quick_bar.activateWindow()

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #1A202C;
                color: #EDF2F7;
                border: 1px solid #4A5568;
                border-radius: 8px;
                padding: 6px;
                font-family: 'Segoe UI', 'Microsoft YaHei';
            }
            QMenu::item {
                padding: 6px 20px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #319795;
                color: #FFFFFF;
            }
            QMenu::separator {
                height: 1px;
                background-color: #2D3748;
                margin: 4px 8px;
            }
        """)

        # Quick Control Panel
        open_quick = menu.addAction("✨ 打开控制台 (Quick Bar)")
        open_quick.triggered.connect(self.toggle_quick_bar)

        menu.addSeparator()

        # State test sub-menu
        state_menu = menu.addMenu("⚡ 状态测试")
        states = [
            ("待机 (Idle)", PetState.IDLE, None),
            ("思考 (Thinking)", PetState.THINKING, 4.0),
            ("编码中 (Working)", PetState.WORKING, 5.0),
            ("完成 (Done)", PetState.DONE, 4.0),
            ("报错 (Error)", PetState.ERROR, 4.0),
            ("等待确认 (Waiting)", PetState.WAITING, 4.0),
            ("休眠 (Sleep)", PetState.SLEEP, None)
        ]
        for label, st, tout in states:
            act = state_menu.addAction(label)
            act.triggered.connect(lambda checked, s=st, t=tout: self.state_machine.set_state(s, timeout_sec=t))

        # Scale sub-menu
        scale_menu = menu.addMenu("📏 尺寸缩放")
        scales = [("小 (1.5x)", 1.5), ("标准 (2.0x)", 2.0), ("大 (2.5x)", 2.5), ("特大 (3.0x)", 3.0)]
        curr_scale = float(cfg.get("scale", 2.0))
        for label, sc in scales:
            act = scale_menu.addAction(label)
            act.setCheckable(True)
            act.setChecked(abs(curr_scale - sc) < 0.1)
            act.triggered.connect(lambda checked, s=sc: self.set_scale(s))

        menu.addSeparator()

        # Sound toggle
        sound_act = menu.addAction("🔊 播放音效")
        sound_act.setCheckable(True)
        sound_act.setChecked(cfg.get("sound_enabled", True))
        sound_act.triggered.connect(self._toggle_sound)

        # Always on top toggle
        top_act = menu.addAction("📌 窗口总在最前")
        top_act.setCheckable(True)
        top_act.setChecked(cfg.get("always_on_top", True))
        top_act.triggered.connect(self._toggle_top)

        # Status Pill toggle
        pill_act = menu.addAction("🏷️ 显示状态胶囊标签")
        pill_act.setCheckable(True)
        pill_act.setChecked(self.pill.isVisible())
        pill_act.triggered.connect(self._toggle_pill)

        menu.addSeparator()

        # Exit action
        exit_act = menu.addAction("✕ 退出桌宠")
        exit_act.triggered.connect(QGuiApplication.instance().quit)

        menu.exec(event.globalPos())

    def _toggle_sound(self):
        curr = cfg.get("sound_enabled", True)
        cfg.set("sound_enabled", not curr)

    def _toggle_top(self):
        curr = cfg.get("always_on_top", True)
        self._set_top(not curr)

    def _set_top(self, new_val: bool):
        cfg.set("always_on_top", new_val)
        flags = self.windowFlags()
        if new_val:
            flags |= Qt.WindowType.WindowStaysOnTopHint
        else:
            flags &= ~Qt.WindowType.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        self.show()

    def paintEvent(self, event):
        if self.current_pixmap and not self.current_pixmap.isNull():
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
            painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
            # Center pixmap
            px = (self.width() - self.current_pixmap.width()) // 2
            py = (self.height() - self.current_pixmap.height()) // 2
            painter.drawPixmap(px, py, self.current_pixmap)
            painter.end()
