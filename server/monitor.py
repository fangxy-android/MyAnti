"""Background monitor for system load and auto-sleep."""
import time
from PySide6.QtCore import QObject, QTimer, Signal
from engine.pet_state import PetState, StateMachine
from config import cfg

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

class SystemMonitor(QObject):
    high_load_detected = Signal()
    load_cleared = Signal()

    def __init__(self, state_machine: StateMachine, parent=None):
        super().__init__(parent)
        self.state_machine = state_machine
        self._was_high_load = False
        self._check_timer = QTimer(self)
        self._check_timer.timeout.connect(self._check)
        self._check_timer.start(3000) # Check every 3 seconds

    def _check(self):
        # 1. Check auto sleep
        sleep_mins = cfg.get("auto_sleep_minutes", 5)
        if sleep_mins > 0:
            self.state_machine.check_idle_sleep(auto_sleep_seconds=sleep_mins * 60)

        # 2. Check system CPU load if enabled
        if cfg.get("monitor_system", True) and HAS_PSUTIL:
            try:
                cpu = psutil.cpu_percent(interval=None)
                if cpu > 75:
                    if not self._was_high_load and self.state_machine.current_state == PetState.IDLE:
                        self._was_high_load = True
                        self.state_machine.set_state(PetState.WORKING)
                elif self._was_high_load and cpu < 40:
                    self._was_high_load = False
                    if self.state_machine.current_state == PetState.WORKING:
                        self.state_machine.set_state(PetState.DONE, timeout_sec=4.0)
            except Exception:
                pass
