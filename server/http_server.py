"""Lightweight local HTTP REST API Server for IDE & external agent integration."""
import json
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from PySide6.QtCore import QObject, Signal, Qt

from engine.pet_state import PetState
from config import cfg

class PetApiBridge(QObject):
    state_requested = Signal(str, str, float, str)  # state, text, timeout, mood
    say_requested = Signal(str, str, float)         # message, mood, duration
    character_requested = Signal(str)              # character_name
    action_requested = Signal(str)                 # action name

class PetRequestHandler(BaseHTTPRequestHandler):
    bridge: PetApiBridge = None
    state_machine = None

    pet_window = None

    def _send_json_response(self, status_code: int, data: dict):
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        if self.path == "/api/status" or self.path == "/":
            curr_state = self.state_machine.current_state.value if self.state_machine else "idle"
            desc = self.state_machine.state_description if self.state_machine else ""
            char = self.pet_window.anim_engine.current_character.name if (self.pet_window and hasattr(self.pet_window, "anim_engine")) else cfg.get("character", "codebot")
            self._send_json_response(200, {
                "status": "ok",
                "pet": "Codex Desktop Pet",
                "character": char,
                "state": curr_state,
                "description": desc
            })
        else:
            self._send_json_response(404, {"error": "Not found"})

    def do_POST(self):
        content_len = int(self.headers.get("Content-Length", 0))
        post_body = self.rfile.read(content_len) if content_len > 0 else b"{}"

        try:
            payload = json.loads(post_body.decode("utf-8"))
        except Exception:
            payload = {}

        if self.path == "/api/state":
            state = payload.get("state", "idle")
            text = payload.get("text", "")
            timeout = payload.get("timeout", None)
            mood = payload.get("mood", "info")
            if self.bridge:
                self.bridge.state_requested.emit(state, text, float(timeout) if timeout else 0.0, mood)
            self._send_json_response(200, {"success": True, "state": state})

        elif self.path == "/api/say":
            message = payload.get("message", payload.get("text", ""))
            mood = payload.get("mood", "info")
            duration = payload.get("duration", 4.0)
            if self.bridge and message:
                self.bridge.say_requested.emit(message, mood, float(duration))
            self._send_json_response(200, {"success": True, "message": message})

        elif self.path == "/api/character":
            char_name = payload.get("character", payload.get("name", "codebot"))
            from graphics.characters import get_character
            resolved_char = get_character(char_name)
            if self.bridge:
                self.bridge.character_requested.emit(resolved_char.name)
            self._send_json_response(200, {
                "success": True,
                "character": resolved_char.name,
                "display_name": resolved_char.display_name
            })

        elif self.path == "/api/action":
            action = payload.get("action", "click")
            if self.bridge:
                self.bridge.action_requested.emit(action)
            self._send_json_response(200, {"success": True, "action": action})

        else:
            self._send_json_response(404, {"error": "Endpoint not found"})

    def log_message(self, format, *args):
        # Suppress noisy default http logging
        pass

class PetHttpServer(QObject):
    def __init__(self, state_machine, pet_window, port: int = None, parent=None):
        super().__init__(parent)
        self.state_machine = state_machine
        self.pet_window = pet_window
        self.port = port or int(cfg.get("server_port", 8765))
        self.bridge = PetApiBridge()

        # Connect bridge signals to GUI thread actions safely via QueuedConnection
        self.bridge.state_requested.connect(self._on_state_requested, Qt.ConnectionType.QueuedConnection)
        self.bridge.say_requested.connect(self._on_say_requested, Qt.ConnectionType.QueuedConnection)
        self.bridge.character_requested.connect(self._on_character_requested, Qt.ConnectionType.QueuedConnection)
        self.bridge.action_requested.connect(self._on_action_requested, Qt.ConnectionType.QueuedConnection)

        self._server = None
        self._thread = None

    def start(self):
        class BoundHandler(PetRequestHandler):
            pass

        BoundHandler.bridge = self.bridge
        BoundHandler.state_machine = self.state_machine
        BoundHandler.pet_window = self.pet_window

        try:
            HTTPServer.allow_reuse_address = False
            self._server = HTTPServer(("127.0.0.1", self.port), BoundHandler)
            self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
            self._thread.start()
            print(f"[PetHttpServer] Running at http://127.0.0.1:{self.port}")
        except Exception as e:
            print(f"[PetHttpServer] Failed to bind port {self.port}: {e}")

    def stop(self):
        if self._server:
            self._server.shutdown()
            self._server.server_close()

    def _on_state_requested(self, state: str, text: str, timeout: float, mood: str):
        timeout_val = timeout if timeout > 0 else None
        self.state_machine.set_state(state, timeout_sec=timeout_val)
        if text:
            self.pet_window.say(text, mood=mood, duration_sec=timeout_val)

    def _on_say_requested(self, message: str, mood: str, duration: float):
        self.pet_window.say(message, mood=mood, duration_sec=duration)

    def _on_character_requested(self, char_name: str):
        self.pet_window._on_character_changed(char_name, announce=True)

    def _on_action_requested(self, action: str):
        act = str(action).lower().strip()
        if act in ("click", "poke"):
            self.pet_window._handle_pet_click()
        elif act == "wake":
            self.pet_window._wake_pet()
        elif act == "sleep":
            self.pet_window._sleep_pet()
        elif act in ("reset", "reset_pos"):
            self.pet_window._reset_position()
        elif act in ("quick_bar", "console", "bar"):
            self.pet_window.toggle_quick_bar()
