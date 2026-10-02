"""System Tray Icon manager for Codex Desktop Pet."""
from PySide6.QtWidgets import QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QFont, QGuiApplication
from PySide6.QtCore import Qt

from engine.pet_state import PetState, StateMachine
from graphics.characters import list_characters, get_character
from config import cfg

class TrayIcon(QSystemTrayIcon):
    def __init__(self, pet_window, parent=None):
        super().__init__(parent)
        self.pet_window = pet_window
        self.state_machine = pet_window.state_machine

        self._update_icon()
        self._init_menu()

        self.activated.connect(self._on_tray_activated)
        self.state_machine.register_listener(self._on_state_changed)

    def _update_icon(self):
        # Generate clean tray icon with pet face
        pm = QPixmap(32, 32)
        pm.fill(Qt.GlobalColor.transparent)
        p = QPainter(pm)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Background circle
        p.setBrush(QColor(0, 206, 201))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(2, 2, 28, 28)

        # Pet symbol '🐾' or 'D'
        p.setPen(QColor(26, 32, 44))
        p.setFont(QFont("Segoe UI Emoji", 14, QFont.Weight.Bold))
        p.drawText(pm.rect(), Qt.AlignmentFlag.AlignCenter, "🐾")
        p.end()

        self.setIcon(QIcon(pm))
        self.setToolTip("Codex Desktop Pet - 您的代码陪伴助手")

    def _init_menu(self):
        menu = QMenu()
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
                padding: 6px 18px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #319795;
                color: #FFFFFF;
            }
        """)

        # Toggle Pet Window
        show_act = menu.addAction("👁️ 显示/隐藏桌宠")
        show_act.triggered.connect(self._toggle_pet_window)

        # Open Quick Bar
        quick_act = menu.addAction("✨ 打开控制台 (Quick Bar)")
        quick_act.triggered.connect(self.pet_window.toggle_quick_bar)

        menu.addSeparator()

        # Character sub-menu
        char_menu = menu.addMenu("🐾 切换形象")
        self._char_actions = {}
        for char_info in list_characters():
            act = char_menu.addAction(char_info["display_name"])
            act.setCheckable(True)
            act.triggered.connect(lambda checked, name=char_info["id"]: self.pet_window._on_character_changed(name, announce=True))
            self._char_actions[char_info["id"]] = act

        def _update_char_checks():
            current_id = self.pet_window.anim_engine.current_character.name
            for cid, act in self._char_actions.items():
                act.setChecked(cid == current_id)

        char_menu.aboutToShow.connect(_update_char_checks)

        menu.addSeparator()

        # Exit
        exit_act = menu.addAction("✕ 退出桌宠")
        exit_act.triggered.connect(QGuiApplication.instance().quit)

        self.setContextMenu(menu)

    def _on_tray_activated(self, reason):
        if reason in (QSystemTrayIcon.ActivationReason.Trigger, QSystemTrayIcon.ActivationReason.DoubleClick):
            self._toggle_pet_window()

    def _toggle_pet_window(self):
        if self.pet_window.isVisible():
            self.pet_window.hide()
            if self.pet_window.bubble.isVisible():
                self.pet_window.bubble.hide()
            if self.pet_window.quick_bar.isVisible():
                self.pet_window.quick_bar.hide()
        else:
            self.pet_window.show()

    def _on_state_changed(self, old_state: PetState, new_state: PetState):
        self.setToolTip(f"Codex Desktop Pet - {self.state_machine.state_description}")
