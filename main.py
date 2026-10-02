"""Main entry point for Codex Desktop Pet."""
import sys
import os
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon, QFont

from config import cfg
from engine.pet_state import StateMachine, PetState
from engine.animation import AnimationEngine
from engine.sound import sound_player
from ui.pet_window import PetWindow
from ui.tray_icon import TrayIcon
from server.http_server import PetHttpServer
from server.monitor import SystemMonitor

def main():
    # Enable High DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("Codex Desktop Pet")
    app.setQuitOnLastWindowClosed(False)

    # Global font styling
    font = QFont("Segoe UI", 9)
    app.setFont(font)

    # Initialize State Machine & Animation Engine
    state_machine = StateMachine(PetState.IDLE)
    animation_engine = AnimationEngine(state_machine)

    # Initialize Main Floating Pet Window
    pet_window = PetWindow(state_machine, animation_engine)
    pet_window.show()

    # Initialize System Tray
    tray = TrayIcon(pet_window)
    tray.show()

    # Initialize Background HTTP API Server (default port 8765)
    if cfg.get("server_enabled", True):
        server = PetHttpServer(state_machine, pet_window)
        server.start()

    # Initialize System Load & Auto-sleep Monitor
    monitor = SystemMonitor(state_machine)

    # Welcome greeting after UI renders
    def on_ready():
        char_name = cfg.get("character", "dewey")
        sound_player.play("notify")
        pet_window.say("✨ Codex 桌宠就绪！点击互动，双击打开控制台~", "info", 4.5)

    QTimer.singleShot(600, on_ready)

    print("=" * 60)
    print("🐾 Codex Desktop Pet 已启动！")
    print(f"📌 当前形象: {cfg.get('character', 'dewey')}")
    print(f"🌐 外部控制 API: http://127.0.0.1:{cfg.get('server_port', 8765)}")
    print(f"💡 命令行测试: python pet-cli.py working \"正在编译...\"")
    print("=" * 60)

    exit_code = app.exec()

    # Clean shutdown
    if cfg.get("server_enabled", True):
        server.stop()

    sys.exit(exit_code)

if __name__ == "__main__":
    main()
