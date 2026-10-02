"""Antigravity IDE Real-time Transcript Monitor.
Automatically monitors Antigravity session transcript logs and syncs desktop pet state.
Zero IDE plugin dependency, 100% reliable real-time linkage.
"""
import os
import glob
import json
import re
from typing import Optional
from PySide6.QtCore import QObject, QTimer, Signal
from engine.pet_state import StateMachine, PetState

class AntigravityMonitor(QObject):
    """Monitors ~/.gemini/antigravity/brain/*/transcript.jsonl in real time."""
    state_change_detected = Signal(str, str, float, str)  # state, text, timeout, mood

    def __init__(self, state_machine: StateMachine, pet_window=None, parent=None):
        super().__init__(parent)
        self.state_machine = state_machine
        self.pet_window = pet_window

        self._brain_dir = os.path.expanduser(r"~/.gemini/antigravity/brain")
        self._tracked_file: Optional[str] = None
        self._last_pos: int = 0
        self._last_event_signature: Optional[str] = None

        # Timer to poll active transcript file (300ms)
        self._poll_timer = QTimer(self)
        self._poll_timer.timeout.connect(self._poll_transcript)
        self._poll_timer.start(300)

        # Timer to scan for new/switched conversations (3000ms)
        self._scan_timer = QTimer(self)
        self._scan_timer.timeout.connect(self._scan_active_conversation)
        self._scan_timer.start(3000)

        # Initial conversation discovery
        self._scan_active_conversation(initial=True)

    def _find_latest_transcript(self) -> Optional[str]:
        if not os.path.exists(self._brain_dir):
            return None
        pattern = os.path.join(self._brain_dir, "*", ".system_generated", "logs", "transcript.jsonl")
        files = glob.glob(pattern)
        if not files:
            return None
        try:
            return max(files, key=os.path.getmtime)
        except Exception:
            return None

    def _scan_active_conversation(self, initial: bool = False):
        latest = self._find_latest_transcript()
        if not latest:
            return

        if latest != self._tracked_file:
            self._tracked_file = latest
            try:
                size = os.path.getsize(latest)
                if initial:
                    # On startup, start near the end of file (last 8KB) to inspect current status
                    self._last_pos = max(0, size - 8192)
                else:
                    # When switching conversation, start at current end
                    self._last_pos = size
            except Exception:
                self._last_pos = 0

    def _poll_transcript(self):
        if not self._tracked_file or not os.path.exists(self._tracked_file):
            return

        try:
            current_size = os.path.getsize(self._tracked_file)
        except OSError:
            return

        if current_size < self._last_pos:
            # File was truncated or restarted
            self._last_pos = 0

        if current_size == self._last_pos:
            return

        try:
            with open(self._tracked_file, "r", encoding="utf-8", errors="replace") as f:
                f.seek(self._last_pos)
                chunk = f.read()
                self._last_pos = f.tell()

            lines = chunk.strip().split("\n")
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    self._handle_entry(entry)
                except Exception:
                    continue
        except Exception:
            pass

    def _handle_entry(self, entry: dict):
        typ = entry.get("type", "")
        source = entry.get("source", "")
        status = entry.get("status", "")
        tool_calls = entry.get("tool_calls", [])
        content = entry.get("content", "")

        # 1. User submitted a prompt
        if typ == "USER_INPUT":
            req_match = re.search(r"<USER_REQUEST>(.*?)</USER_REQUEST>", content, re.DOTALL)
            user_text = req_match.group(1).strip() if req_match else content.strip()
            # Clean lines
            user_text = " ".join(user_text.split())
            if len(user_text) > 22:
                say_text = f"收到指令: {user_text[:20]}... 🤖"
            elif user_text:
                say_text = f"收到指令: {user_text} 🤖"
            else:
                say_text = "收到指令！指令分析处理中... 🤖"

            self._apply_state(PetState.WORKING, say_text, timeout=300.0, mood="working")
            return

        # 2. Agent calling tools
        if tool_calls:
            first_tool = tool_calls[0]
            tname = first_tool.get("name", "tool")
            args = first_tool.get("args", {})

            if tname == "ask_question":
                self._apply_state(
                    PetState.WAITING,
                    "等待确认: 有需要您选择的项目 ❓",
                    timeout=300.0,
                    mood="info"
                )
            else:
                action_desc = (
                    args.get("toolAction")
                    or args.get("toolSummary")
                    or f"正在执行 {tname}"
                )
                action_clean = str(action_desc).strip('"\'')
                self._apply_state(
                    PetState.WORKING,
                    f"{action_clean} ⚡",
                    timeout=180.0,
                    mood="working"
                )
            return

        # 3. Tool execution error
        if status == "ERROR":
            self._apply_state(
                PetState.ERROR,
                "执行遇到一点异常... ⚠️",
                timeout=8.0,
                mood="error"
            )
            return

        # 4. Turn finished (MODEL PLANNER_RESPONSE with content and no pending tool calls)
        if source == "MODEL" and typ == "PLANNER_RESPONSE" and not tool_calls and content:
            self._apply_state(
                PetState.DONE,
                "任务完成！请查看结果 (✓) 🤖",
                timeout=12.0,
                mood="success"
            )
            return

    def _apply_state(self, state: PetState, text: str, timeout: float, mood: str):
        sig = f"{state.value}:{text}"
        if sig == self._last_event_signature:
            return
        self._last_event_signature = sig

        self.state_machine.set_state(state, timeout_sec=timeout)
        if self.pet_window and text:
            self.pet_window.say(text, mood=mood, duration_sec=timeout)
