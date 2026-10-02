"""Pet state definitions and state machine."""
from enum import Enum
import time

class PetState(str, Enum):
    IDLE = "idle"
    THINKING = "thinking"
    WORKING = "working"
    DONE = "done"
    ERROR = "error"
    WAITING = "waiting"
    CLICKED = "clicked"
    SLEEP = "sleep"

STATE_DESCRIPTIONS = {
    PetState.IDLE: "待机中 (Idle & Relaxing)",
    PetState.THINKING: "思考中 (AI Processing / Analyzing)",
    PetState.WORKING: "编写代码中 (Coding / Executing)",
    PetState.DONE: "任务完成 (Success / Done!)",
    PetState.ERROR: "遇到错误 (Error / Alert)",
    PetState.WAITING: "等待确认 (Waiting for Confirmation / Input)",
    PetState.CLICKED: "互动中 (Petted / Happy)",
    PetState.SLEEP: "休眠中 (Resting / Zzz)"
}

class StateMachine:
    def __init__(self, initial_state: PetState = PetState.IDLE):
        self._current_state = initial_state
        self._previous_state = initial_state
        self._state_start_time = time.time()
        self._state_timeout = None
        self._timeout_revert_state = PetState.IDLE
        self._listeners = []
        self._last_interaction_time = time.time()

    @property
    def current_state(self) -> PetState:
        return self._current_state

    @property
    def state_description(self) -> str:
        return STATE_DESCRIPTIONS.get(self._current_state, "未知状态")

    def register_listener(self, callback):
        if callback not in self._listeners:
            self._listeners.append(callback)

    def unregister_listener(self, callback):
        if callback in self._listeners:
            self._listeners.remove(callback)

    def set_state(self, new_state: PetState, timeout_sec: float = None, revert_to: PetState = PetState.IDLE):
        if isinstance(new_state, str):
            try:
                new_state = PetState(new_state.lower())
            except ValueError:
                new_state = PetState.IDLE

        self._last_interaction_time = time.time()
        old_state = self._current_state
        self._previous_state = old_state
        self._current_state = new_state
        self._state_start_time = time.time()
        self._state_timeout = timeout_sec
        self._timeout_revert_state = revert_to

        for listener in self._listeners:
            try:
                listener(old_state, new_state)
            except Exception as e:
                print(f"[StateMachine] Error in state listener: {e}")

    def update(self):
        """Called periodically (e.g. per frame or timer tick) to check timeout transitions."""
        now = time.time()
        if self._state_timeout and (now - self._state_start_time) >= self._state_timeout:
            revert = self._timeout_revert_state
            self._state_timeout = None
            self.set_state(revert)

    def touch(self):
        """Signal user interaction to reset idle/sleep timer."""
        self._last_interaction_time = time.time()
        if self._current_state == PetState.SLEEP:
            self.set_state(PetState.IDLE)

    def check_idle_sleep(self, auto_sleep_seconds: float = 300):
        if self._current_state == PetState.IDLE:
            if time.time() - self._last_interaction_time > auto_sleep_seconds:
                self.set_state(PetState.SLEEP)
