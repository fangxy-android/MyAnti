"""Fireball character - dynamic energetic flame companion."""
from PySide6.QtGui import QPixmap
from engine.pet_state import PetState
from graphics.characters.base import CharacterBase
from graphics.pixel_canvas import PixelCanvas

class FireballCharacter(CharacterBase):
    name = "fireball"
    display_name = "火焰精灵 Fireball"
    description = "Codex经典桌宠！燃烧着代码热情的火焰精灵"

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

    def _draw_flame(self, canvas: PixelCanvas, ox: int, oy: int, tip_shift: int = 0,
                    palette: tuple = ("#D63031", "#E17055", "#F39C12", "#FFEAA7"),
                    eye_mode: str = "normal"):
        c_outer, c_mid, c_inner, c_core = palette

        # Outer flame contour
        canvas.fill_rect(ox + 8, oy + 12, 16, 14, c_outer)
        canvas.fill_rect(ox + 6, oy + 15, 20, 9, c_outer)
        # Flame tip (animated)
        canvas.fill_rect(ox + 12 + tip_shift, oy + 4, 6, 8, c_outer)
        canvas.fill_rect(ox + 14 + tip_shift * 2, oy + 1, 3, 4, c_outer)

        # Mid flame
        canvas.fill_rect(ox + 9, oy + 14, 14, 11, c_mid)
        canvas.fill_rect(ox + 13 + tip_shift, oy + 7, 4, 7, c_mid)

        # Inner flame / core
        canvas.fill_rect(ox + 11, oy + 16, 10, 8, c_inner)
        canvas.fill_rect(ox + 13, oy + 18, 6, 5, c_core)

        # Eyes
        if eye_mode == "happy":
            canvas.draw_pixels("#2D3436", [
                (ox + 11, oy + 18), (ox + 12, oy + 17), (ox + 13, oy + 18),
                (ox + 17, oy + 18), (ox + 18, oy + 17), (ox + 19, oy + 18)
            ])
        elif eye_mode == "spiral":
            canvas.draw_pixels("#2D3436", [
                (ox + 11, oy + 17), (ox + 12, oy + 17), (ox + 12, oy + 19), (ox + 11, oy + 19),
                (ox + 17, oy + 17), (ox + 18, oy + 17), (ox + 18, oy + 19), (ox + 17, oy + 19)
            ])
        elif eye_mode == "sleep":
            canvas.fill_rect(ox + 11, oy + 18, 3, 1, "#2D3436")
            canvas.fill_rect(ox + 17, oy + 18, 3, 1, "#2D3436")
        else:
            # Cute round eyes
            canvas.fill_rect(ox + 11, oy + 17, 3, 3, "#2D3436")
            canvas.set_pixel(ox + 12, oy + 17, "#FFFFFF")
            canvas.fill_rect(ox + 17, oy + 17, 3, 3, "#2D3436")
            canvas.set_pixel(ox + 18, oy + 17, "#FFFFFF")

    def _render_idle(self) -> list[PixelCanvas]:
        frames = []
        shifts = [0, 1, 0, -1]
        for s in shifts:
            c = PixelCanvas(36, 36)
            self._draw_flame(c, 2, 4, tip_shift=s)
            # Floating ember
            c.fill_rect(10 + s, 2, 2, 2, "#F39C12")
            frames.append(c)
        return frames

    def _render_thinking(self) -> list[PixelCanvas]:
        # Blue flame for deep thinking
        blue_palette = ("#0984E3", "#00CEC9", "#74B9FF", "#DFE6E9")
        frames = []
        shifts = [-1, 0, 1, 0]
        for i, s in enumerate(shifts):
            c = PixelCanvas(36, 36)
            self._draw_flame(c, 2, 4, tip_shift=s, palette=blue_palette)
            # Orbiting sparkles
            orb_pos = [(6, 8), (28, 8), (26, 26), (8, 26)]
            ox, oy = orb_pos[i]
            c.fill_rect(ox, oy, 3, 3, "#00CEC9")
            c.set_pixel(ox + 1, oy + 1, "#FFFFFF")
            frames.append(c)
        return frames

    def _render_working(self) -> list[PixelCanvas]:
        frames = []
        for i in range(4):
            c = PixelCanvas(36, 36)
            s = (i % 2) * 2 - 1
            self._draw_flame(c, 0, 4, tip_shift=s)
            # Fiery laptop / keyboard
            c.fill_rect(18, 16, 2, 8, "#2D3436")
            c.fill_rect(20, 17, 1, 6, "#FF7675")
            c.fill_rect(16, 24, 10, 2, "#636E72")
            # Rapid sparks
            sparks = [[(26, 12), (28, 6)], [(24, 10), (30, 8)], [(25, 8), (27, 4)], [(28, 11), (25, 5)]]
            for sx, sy in sparks[i]:
                c.fill_rect(sx, sy, 2, 2, "#F1C40F")
            frames.append(c)
        return frames

    def _render_done(self) -> list[PixelCanvas]:
        frames = []
        for i in range(4):
            c = PixelCanvas(36, 36)
            jump = -3 if i in (1, 2) else 0
            self._draw_flame(c, 2, 4 + jump, eye_mode="happy")
            # Celebration fireworks
            c.fill_rect(4, 4, 3, 3, "#F1C40F")
            c.fill_rect(28, 5, 3, 3, "#E84393")
            c.fill_rect(16, 1, 3, 3, "#00CEC9")
            frames.append(c)
        return frames

    def _render_error(self) -> list[PixelCanvas]:
        gray_palette = ("#636E72", "#B2BEC3", "#DFE6E9", "#F5F6FA")
        frames = []
        for i in range(4):
            c = PixelCanvas(36, 36)
            sh = 1 if i % 2 == 0 else -1
            self._draw_flame(c, 2 + sh, 6, palette=gray_palette, eye_mode="spiral")
            # Smoke puff
            c.fill_rect(16 + i * 2, 2, 4, 3, "#B2BEC3")
            frames.append(c)
        return frames

    def _render_waiting(self) -> list[PixelCanvas]:
        frames = []
        for i in range(4):
            c = PixelCanvas(36, 36)
            pulse = i % 2
            self._draw_flame(c, 2, 4 + pulse)
            c.fill_rect(26, 4, 2, 5, "#F39C12")
            c.set_pixel(26, 11, "#F39C12")
            frames.append(c)
        return frames

    def _render_clicked(self) -> list[PixelCanvas]:
        pink_palette = ("#E84393", "#FD79A8", "#FF7675", "#FFEAA7")
        frames = []
        for i in range(4):
            c = PixelCanvas(36, 36)
            b = -2 if i in (1, 2) else 0
            self._draw_flame(c, 2, 4 + b, palette=pink_palette, eye_mode="happy")
            # Floating hearts
            c.fill_rect(24, 6 - i * 2, 4, 3, "#E84393")
            frames.append(c)
        return frames

    def _render_sleep(self) -> list[PixelCanvas]:
        blue_palette = ("#2980B9", "#3498DB", "#74B9FF", "#DFE6E9")
        frames = []
        for i in range(4):
            c = PixelCanvas(36, 36)
            # Tiny candle flame
            self._draw_flame(c, 2, 8, palette=blue_palette, eye_mode="sleep")
            zx = 24 + i * 2
            zy = 12 - i * 2
            c.fill_rect(zx, zy, 4, 1, "#74B9FF")
            c.set_pixel(zx + 2, zy + 1, "#74B9FF")
            c.set_pixel(zx + 1, zy + 2, "#74B9FF")
            c.fill_rect(zx, zy + 3, 4, 1, "#74B9FF")
            frames.append(c)
        return frames
