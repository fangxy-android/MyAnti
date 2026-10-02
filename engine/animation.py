"""Animation engine for rendering pet frames and handling transitions."""
from PySide6.QtCore import QObject, Signal, QTimer
from PySide6.QtGui import QPixmap
from engine.pet_state import PetState, StateMachine
from graphics.characters.base import CharacterBase
from graphics.characters import get_character
from config import cfg

class AnimationEngine(QObject):
    frame_changed = Signal(QPixmap)
    character_changed = Signal(str)

    def __init__(self, state_machine: StateMachine):
        super().__init__()
        self.state_machine = state_machine
        self.current_character: CharacterBase = get_character(cfg.get("character", "sakura"))
        self.scale = float(cfg.get("scale", 2.0))

        self.current_frames: list[QPixmap] = []
        self.frame_index = 0

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._on_timer_tick)

        self.state_machine.register_listener(self._on_state_changed)
        self._refresh_frames()
        self._start_timer()

    @property
    def pet_size(self) -> int:
        # Base sprite canvas is 36x36 or 32x32, base scaled display is 64 * scale
        return int(64 * self.scale)

    def set_character(self, character_name: str):
        char = get_character(character_name)
        if char:
            self.current_character = char
            cfg.set("character", char.name)
            self.frame_index = 0
            duration = self.current_character.get_frame_duration(self.state_machine.current_state)
            self.timer.setInterval(duration)
            self._refresh_frames()
            self.character_changed.emit(char.name)

    def set_scale(self, scale: float):
        self.scale = max(1.0, min(4.0, scale))
        cfg.set("scale", self.scale)
        self._refresh_frames()

    def _refresh_frames(self):
        state = self.state_machine.current_state
        self.current_frames = self.current_character.get_frames(state, self.pet_size)
        if not self.current_frames:
            return
        self.frame_index = self.frame_index % len(self.current_frames)
        self.frame_changed.emit(self.current_frames[self.frame_index])

    def _start_timer(self):
        duration = self.current_character.get_frame_duration(self.state_machine.current_state)
        self.timer.start(duration)

    def _on_state_changed(self, old_state: PetState, new_state: PetState):
        self.frame_index = 0
        self._refresh_frames()
        duration = self.current_character.get_frame_duration(new_state)
        self.timer.setInterval(duration)

    def _on_timer_tick(self):
        # Update state machine timeout expiration
        self.state_machine.update()

        # Advance frame
        if self.current_frames:
            self.frame_index = (self.frame_index + 1) % len(self.current_frames)
            self.frame_changed.emit(self.current_frames[self.frame_index])
