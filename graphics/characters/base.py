"""Base class for animated pet characters."""
from PySide6.QtGui import QPixmap
from engine.pet_state import PetState

class CharacterBase:
    name: str = "base"
    display_name: str = "Base Pet"
    description: str = "Base Character"

    def __init__(self):
        self._frame_cache = {}

    def get_frames(self, state: PetState, target_size: int = 128) -> list[QPixmap]:
        cache_key = (state, target_size)
        if cache_key in self._frame_cache:
            return self._frame_cache[cache_key]

        frames = self.render_frames(state, target_size)
        self._frame_cache[cache_key] = frames
        return frames

    def render_frames(self, state: PetState, target_size: int = 128) -> list[QPixmap]:
        """Subclasses override this to generate frames."""
        raise NotImplementedError

    def get_frame_duration(self, state: PetState) -> int:
        """Frame duration in milliseconds."""
        if state == PetState.WORKING:
            return 90
        elif state == PetState.THINKING:
            return 140
        elif state == PetState.DONE:
            return 110
        elif state == PetState.ERROR:
            return 120
        elif state == PetState.CLICKED:
            return 100
        elif state == PetState.WAITING:
            return 150
        elif state == PetState.SLEEP:
            return 280
        else:
            return 160
