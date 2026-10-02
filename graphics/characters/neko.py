"""Neko character - adorable hacker cat companion."""
from PySide6.QtGui import QPixmap
from engine.pet_state import PetState
from graphics.characters.base import CharacterBase
from graphics.pixel_canvas import PixelCanvas

from graphics.renderer import CrispRenderer

class NekoCharacter(CharacterBase):
    name = "neko"
    display_name = "赛博猫猫 Neko"
    description = "敲键盘超快的黑白猫咪，灵动的尾巴和尖尖的耳朵！"

    def render_frames(self, state: PetState, target_size: int = 128) -> list[QPixmap]:
        return [
            CrispRenderer.render_neko(state, i, target_size)
            for i in range(4)
        ]

    def _draw_cat(self, canvas: PixelCanvas, ox: int, oy: int, tail_frame: int = 0,
                  eye_mode: str = "normal", blink: bool = False):
        c_black = "#2C3E50"
        c_white = "#FFFFFF"
        c_pink = "#FF7675"

        # Pointy ears
        canvas.draw_pixels(c_black, [
            (ox + 8, oy + 5), (ox + 9, oy + 4), (ox + 10, oy + 3), (ox + 11, oy + 4), (ox + 11, oy + 5),
            (ox + 20, oy + 5), (ox + 21, oy + 4), (ox + 22, oy + 3), (ox + 23, oy + 4), (ox + 24, oy + 5)
        ])
        canvas.set_pixel(ox + 10, oy + 5, c_pink)
        canvas.set_pixel(ox + 22, oy + 5, c_pink)

        # Head
        canvas.fill_rect(ox + 9, oy + 6, 14, 10, c_black)
        # White face muzzle patch
        canvas.fill_rect(ox + 13, oy + 10, 6, 6, c_white)

        # Eyes
        if eye_mode == "happy":
            canvas.draw_pixels(c_white, [
                (ox + 11, oy + 9), (ox + 12, oy + 8), (ox + 13, oy + 9),
                (ox + 19, oy + 9), (ox + 20, oy + 8), (ox + 21, oy + 9)
            ])
        elif eye_mode == "spiral":
            canvas.draw_pixels(c_pink, [(ox + 11, oy + 9), (ox + 13, oy + 9), (ox + 19, oy + 9), (ox + 21, oy + 9)])
        elif eye_mode == "sleep" or blink:
            canvas.fill_rect(ox + 11, oy + 9, 3, 1, c_white)
            canvas.fill_rect(ox + 18, oy + 9, 3, 1, c_white)
        else:
            # Big green cat eyes
            canvas.fill_rect(ox + 11, oy + 8, 3, 3, "#2ECC71")
            canvas.fill_rect(ox + 18, oy + 8, 3, 3, "#2ECC71")
            canvas.set_pixel(ox + 12, oy + 8, c_black) # Slit pupil
            canvas.set_pixel(ox + 19, oy + 8, c_black)

        # Pink nose
        canvas.set_pixel(ox + 15, oy + 12, c_pink)
        canvas.set_pixel(ox + 16, oy + 12, c_pink)

        # Whiskers
        canvas.draw_pixels(c_white, [
            (ox + 6, oy + 11), (ox + 7, oy + 11), (ox + 6, oy + 13), (ox + 7, oy + 13),
            (ox + 24, oy + 11), (ox + 25, oy + 11), (ox + 24, oy + 13), (ox + 25, oy + 13)
        ])

        # Body
        canvas.fill_rect(ox + 10, oy + 16, 12, 9, c_black)
        # White chest
        canvas.fill_rect(ox + 13, oy + 16, 6, 7, c_white)

        # Paws
        canvas.fill_rect(ox + 11, oy + 25, 3, 2, c_white)
        canvas.fill_rect(ox + 18, oy + 25, 3, 2, c_white)

        # Animated Tail
        tail_offsets = [
            [(ox + 22, oy + 21), (ox + 24, oy + 19), (ox + 26, oy + 17)], # Curled right
            [(ox + 22, oy + 21), (ox + 25, oy + 20), (ox + 27, oy + 19)], # Mid
            [(ox + 22, oy + 21), (ox + 25, oy + 22), (ox + 28, oy + 23)], # Low
            [(ox + 22, oy + 21), (ox + 25, oy + 20), (ox + 27, oy + 19)]  # Mid
        ]
        for tx, ty in tail_offsets[tail_frame % 4]:
            canvas.fill_rect(tx, ty, 3, 3, c_black)

    def _render_idle(self) -> list[PixelCanvas]:
        frames = []
        for i in range(4):
            c = PixelCanvas(36, 36)
            blink = (i == 2)
            self._draw_cat(c, 2, 4, tail_frame=i, blink=blink)
            frames.append(c)
        return frames

    def _render_thinking(self) -> list[PixelCanvas]:
        frames = []
        for i in range(4):
            c = PixelCanvas(36, 36)
            self._draw_cat(c, 2, 4, tail_frame=i)
            # Question mark above head
            c.draw_pixels("#F1C40F", [(24, 2), (25, 1), (26, 2), (25, 3), (25, 4), (25, 6)])
            frames.append(c)
        return frames

    def _render_working(self) -> list[PixelCanvas]:
        frames = []
        for i in range(4):
            c = PixelCanvas(36, 36)
            self._draw_cat(c, 0, 4, tail_frame=i)
            # Laptop
            c.fill_rect(17, 16, 2, 8, "#34495E")
            c.fill_rect(19, 17, 1, 6, "#00CEC9")
            c.fill_rect(15, 24, 10, 2, "#95A5A6")
            # Alternating paws typing
            if i % 2 == 0:
                c.fill_rect(15, 20, 3, 3, "#FFFFFF")
            else:
                c.fill_rect(18, 20, 3, 3, "#FFFFFF")
            # Matrix code sparks
            c.fill_rect(24, 10, 2, 2, "#2ECC71")
            frames.append(c)
        return frames

    def _render_done(self) -> list[PixelCanvas]:
        frames = []
        for i in range(4):
            c = PixelCanvas(36, 36)
            jump = -3 if i in (1, 2) else 0
            self._draw_cat(c, 2, 4 + jump, tail_frame=i, eye_mode="happy")
            # Cute fish treat popping up
            c.fill_rect(25, 4, 5, 3, "#3498DB")
            c.draw_pixels("#3498DB", [(30, 3), (30, 6)])
            frames.append(c)
        return frames

    def _render_error(self) -> list[PixelCanvas]:
        frames = []
        for i in range(4):
            c = PixelCanvas(36, 36)
            sh = 1 if i % 2 == 0 else -1
            self._draw_cat(c, 2 + sh, 4, tail_frame=i, eye_mode="spiral")
            # Sweat drop
            c.fill_rect(24, 8 + i, 2, 3, "#3498DB")
            frames.append(c)
        return frames

    def _render_waiting(self) -> list[PixelCanvas]:
        frames = []
        for i in range(4):
            c = PixelCanvas(36, 36)
            self._draw_cat(c, 2, 4, tail_frame=i)
            # Raised waving paw
            paw_y = 12 if i % 2 == 0 else 14
            c.fill_rect(6, paw_y, 4, 3, "#FFFFFF")
            # Alert dot
            c.fill_rect(26, 4, 2, 5, "#E67E22")
            c.set_pixel(26, 11, "#E67E22")
            frames.append(c)
        return frames

    def _render_clicked(self) -> list[PixelCanvas]:
        frames = []
        for i in range(4):
            c = PixelCanvas(36, 36)
            b = -2 if i in (1, 2) else 0
            self._draw_cat(c, 2, 4 + b, tail_frame=i, eye_mode="happy")
            # Floating hearts
            c.fill_rect(24, 6 - i * 2, 4, 3, "#FD79A8")
            frames.append(c)
        return frames

    def _render_sleep(self) -> list[PixelCanvas]:
        frames = []
        for i in range(4):
            c = PixelCanvas(36, 36)
            # Sleeping cat loaf
            c.fill_rect(8, 16, 18, 10, "#2C3E50")
            c.fill_rect(10, 18, 6, 6, "#FFFFFF") # White chest
            # Sleeping eye
            c.fill_rect(12, 17, 3, 1, "#FFFFFF")
            # Tail wrapped around body
            c.fill_rect(22, 23, 6, 3, "#2C3E50")
            zx = 24 + i * 2
            zy = 10 - i * 2
            c.fill_rect(zx, zy, 4, 1, "#74B9FF")
            c.set_pixel(zx + 2, zy + 1, "#74B9FF")
            c.set_pixel(zx + 1, zy + 2, "#74B9FF")
            c.fill_rect(zx, zy + 3, 4, 1, "#74B9FF")
            frames.append(c)
        return frames
