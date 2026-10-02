"""Main entry point for Codex Desktop Pet."""
import sys
import os
from pathlib import Path

import traceback

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)
    sys.stderr.reconfigure(encoding="utf-8", line_buffering=True)

def exception_hook(exctype, value, tb):
    print("UNCAUGHT EXCEPTION:", exctype, value, file=sys.stderr)
    traceback.print_exception(exctype, value, tb)
    try:
        crash_file = Path(__file__).resolve().parent / "crash.log"
        with open(crash_file, "a", encoding="utf-8") as f:
            traceback.print_exception(exctype, value, tb, file=f)
    except Exception:
        pass
    sys.__excepthook__(exctype, value, tb)

sys.excepthook = exception_hook

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
from server.antigravity_monitor import AntigravityMonitor
import urllib.request
import urllib.error


def check_existing_instance(port: int = 8765) -> bool:
    try:
        req = urllib.request.Request(f"http://127.0.0.1:{port}/api/status", headers={"User-Agent": "codex-pet-checker"})
        with urllib.request.urlopen(req, timeout=0.8) as resp:
            if resp.status == 200:
                wake_req = urllib.request.Request(
                    f"http://127.0.0.1:{port}/api/action",
                    data=b'{"action":"quick_bar"}',
                    headers={"Content-Type": "application/json"}
                )
                urllib.request.urlopen(wake_req, timeout=1.0)
                return True
    except Exception:
        pass
    return False


def main():
    port = int(cfg.get("server_port", 8765))
    if cfg.get("server_enabled", True) and check_existing_instance(port):
        print(f"🐾 Codex Desktop Pet 已在运行中 (端口 {port})，已唤醒已有桌宠控制台。")
        sys.exit(0)

    # Attach to interactive desktop on Windows
    if sys.platform == "win32":
        try:
            import ctypes
            user32 = ctypes.windll.user32
            hDesk = user32.OpenDesktopW("Default", 0, False, 0x01FF)
            if hDesk:
                user32.SetThreadDesktop(hDesk)
        except Exception:
            pass

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

    # Initialize Antigravity IDE Real-time Conversation Auto-Sync
    agy_monitor = AntigravityMonitor(state_machine, pet_window=pet_window)

    # Welcome greeting after UI renders
    def on_ready():
        char_name = cfg.get("character", "sakura")
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
