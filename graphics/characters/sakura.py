"""Sakura Character - Japanese Anime Chibi Girl Developer Companion."""
from PySide6.QtGui import QPixmap
from engine.pet_state import PetState
from graphics.characters.base import CharacterBase
from graphics.renderer import CrispRenderer

class SakuraCharacter(CharacterBase):
    name = "sakura"
    display_name = "二次元萌妹 · 樱子"
    description = "粉色双马尾二次元动漫少女，水汪汪的大眼睛，敲代码时樱花与代码齐飞！"

    def render_frames(self, state: PetState, target_size: int = 128) -> list[QPixmap]:
        return [
            CrispRenderer.render_sakura(state, i, target_size)
            for i in range(4)
        ]
