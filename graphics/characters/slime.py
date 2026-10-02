"""Slime character - bouncy cute jelly companion."""
from PySide6.QtGui import QPixmap
from engine.pet_state import PetState
from graphics.characters.base import CharacterBase
from graphics.pixel_canvas import PixelCanvas

class SlimeCharacter(CharacterBase):
    name = "slime"
    display_name = "果冻史莱姆 Slime"
    description = "Q弹可爱的青柠果冻史莱姆，伴随每一次操作软萌晃动！"

    def render_frames(self, state: PetState, target_size: int = 128) -> list[QPixmap]:
        frames = []
        if state == PetState.WORKING:
            frames = self._render_working()
        elif state == PetState.THINKING:
            frames = self._render_thinking()
        elif state == PetState.DONE:
            frames = self._render_done()
        elif state == PetState.ERROR:
            frames = self._render_error()
        elif state == PetState.WAITING:
            frames = self._render_waiting()
        elif state == PetState.CLICKED:
            frames = self._render_clicked()
        elif state == PetState.SLEEP:
            frames = self._render_sleep()
        else: # IDLE
            frames = self._render_idle()

        return [canvas.to_pixmap(target_size) for canvas in frames]

    def _draw_slime(self, canvas: PixelCanvas, ox: int, oy: int, squash_w: int = 0, squash_h: int = 0,
                    eye_mode: str = "normal"):
        c_body = "#00CEC9"
        c_body_dark = "#0984E3"
        c_highlight = "#81ECEC"

        w = 18 + squash_w
        h = 14 + squash_h
        x = ox + (18 - w) // 2
        y = oy + (14 - h)

        # Main round body
        canvas.fill_rect(x + 2, y + 2, w - 4, h - 2, c_body)
        canvas.fill_rect(x + 4, y, w - 8, h, c_body)
        canvas.fill_rect(x + 1, y + 4, w - 2, h - 5, c_body)

        # Darker base shadow
        canvas.fill_rect(x + 3, y + h - 2, w - 6, 2, c_body_dark)

        # Highlight reflection
        canvas.fill_rect(x + 4, y + 2, 4, 3, c_highlight)
        canvas.set_pixel(x + 5, y + 1, "#FFFFFF")

        # Eyes
        if eye_mode == "happy":
            canvas.draw_pixels("#2D3436", [
                (x + 5, y + 6), (x + 6, y + 5), (x + 7, y + 6),
                (x + w - 8, y + 6), (x + w - 7, y + 5), (x + w - 6, y + 6)
            ])
        elif eye_mode == "dizzy":
            canvas.draw_pixels("#2D3436", [
                (x + 5, y + 5), (x + 7, y + 7), (x + 7, y + 5), (x + 5, y + 7),
                (x + w - 8, y + 5), (x + w - 6, y + 7), (x + w - 6, y + 5), (x + w - 8, y + 7)
            ])
        elif eye_mode == "sleep":
            canvas.fill_rect(x + 5, y + 6, 3, 1, "#2D3436")
            canvas.fill_rect(x + w - 8, y + 6, 3, 1, "#2D3436")
        else:
            canvas.fill_rect(x + 5, y + 5, 3, 3, "#2D3436")
            canvas.set_pixel(x + 6, y + 5, "#FFFFFF")
            canvas.fill_rect(x + w - 8, y + 5, 3, 3, "#2D3436")
            canvas.set_pixel(x + w - 7, y + 5, "#FFFFFF")

    def _render_idle(self) -> list[PixelCanvas]:
        frames = []
        squashes = [(0, 0), (2, -2), (0, 0), (-2, 2)]
        for sw, sh in squashes:
            c = PixelCanvas(36, 36)
            self._draw_slime(c, 9, 12, squash_w=sw, squash_h=sh)
            frames.append(c)
        return frames

    def _render_thinking(self) -> list[PixelCanvas]:
        frames = []
        for i in range(4):
            c = PixelCanvas(36, 36)
            self._draw_slime(c, 9, 12)
            # Internal ascending bubbles
            c.fill_rect(13, 20 - i * 2, 2, 2, "#81ECEC")
            c.fill_rect(21, 22 - ((i + 2) % 4) * 2, 2, 2, "#81ECEC")
            frames.append(c)
        return frames

    def _render_working(self) -> list[PixelCanvas]:
        frames = []
        for i in range(4):
            c = PixelCanvas(36, 36)
            self._draw_slime(c, 7, 12)
            # Tiny laptop
            c.fill_rect(22, 17, 2, 7, "#34495E")
            c.fill_rect(24, 18, 1, 5, "#FFEAA7")
            c.fill_rect(20, 24, 9, 2, "#7F8C8D")
            # Morphing jelly arm typing
            if i % 2 == 0:
                c.fill_rect(19, 21, 4, 3, "#00CEC9")
            else:
                c.fill_rect(18, 19, 4, 3, "#00CEC9")
            # Matrix code bits
            c.fill_rect(27, 10, 2, 2, "#00FFCC")
            frames.append(c)
        return frames

    def _render_done(self) -> list[PixelCanvas]:
        frames = []
        for i in range(4):
            c = PixelCanvas(36, 36)
            jump = -5 if i in (1, 2) else 0
            self._draw_slime(c, 9, 12 + jump, eye_mode="happy")
            # Crown on top
            c.fill_rect(16, 8 + jump, 5, 2, "#F1C40F")
            c.draw_pixels("#F1C40F", [(15, 6 + jump), (18, 5 + jump), (21, 6 + jump)])
            c.set_pixel(18, 7 + jump, "#E74C3C") # Crown ruby
            frames.append(c)
        return frames

    def _render_error(self) -> list[PixelCanvas]:
        frames = []
        for i in range(4):
            c = PixelCanvas(36, 36)
            # Melted flat
            self._draw_slime(c, 9, 15, squash_w=6, squash_h=-5, eye_mode="dizzy")
            frames.append(c)
        return frames

    def _render_waiting(self) -> list[PixelCanvas]:
        frames = []
        for i in range(4):
            c = PixelCanvas(36, 36)
            self._draw_slime(c, 9, 12)
            # Waving jelly arm
            ay = 16 if i % 2 == 0 else 18
            c.fill_rect(6, ay, 4, 3, "#00CEC9")
            c.fill_rect(26, 4, 2, 5, "#F39C12")
            c.set_pixel(26, 11, "#F39C12")
            frames.append(c)
        return frames

    def _render_clicked(self) -> list[PixelCanvas]:
        frames = []
        for i in range(4):
            c = PixelCanvas(36, 36)
            b = -2 if i in (1, 2) else 0
            self._draw_slime(c, 9, 12 + b, squash_w=-2, squash_h=2, eye_mode="happy")
            # Floating heart
            c.fill_rect(24, 6 - i * 2, 4, 3, "#FD79A8")
            frames.append(c)
        return frames

    def _render_sleep(self) -> list[PixelCanvas]:
        frames = []
        for i in range(4):
            c = PixelCanvas(36, 36)
            self._draw_slime(c, 9, 14, squash_w=4, squash_h=-3, eye_mode="sleep")
            zx = 24 + i * 2
            zy = 10 - i * 2
            c.fill_rect(zx, zy, 4, 1, "#74B9FF")
            c.set_pixel(zx + 2, zy + 1, "#74B9FF")
            c.set_pixel(zx + 1, zy + 2, "#74B9FF")
            c.fill_rect(zx, zy + 3, 4, 1, "#74B9FF")
            frames.append(c)
        return frames
