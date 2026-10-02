"""Dewey the Duck - Codex's beloved coder duck companion."""
from PySide6.QtGui import QPixmap, QPainter, QColor, QFont
from PySide6.QtCore import Qt, QRect
from engine.pet_state import PetState
from graphics.characters.base import CharacterBase
from graphics.pixel_canvas import PixelCanvas

class DeweyCharacter(CharacterBase):
    name = "dewey"
    display_name = "整理鸭 Dewey"
    description = "Codex经典桌宠！戴着小绿帽、充满活力的编程鸭子"

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

    def _draw_base_duck(self, canvas: PixelCanvas, ox: int, oy: int, blink: bool = False, eye_type: str = "normal"):
        # Colors
        c_body = "#F9D342"
        c_body_dark = "#E1B12C"
        c_body_light = "#FFF3B0"
        c_beak = "#F39C12"
        c_beak_dark = "#D35400"
        c_cap = "#2ECC71"
        c_cap_dark = "#27AE60"
        c_feet = "#E67E22"

        # Cap
        canvas.fill_rect(ox + 8, oy + 4, 10, 3, c_cap)
        canvas.fill_rect(ox + 10, oy + 2, 6, 2, c_cap_dark)
        canvas.fill_rect(ox + 16, oy + 6, 5, 2, c_cap) # Visor

        # Head
        canvas.fill_rect(ox + 7, oy + 7, 12, 9, c_body)
        canvas.fill_rect(ox + 9, oy + 7, 8, 2, c_body_light) # Head highlight

        # Eye
        if eye_type == "happy":
            # ^ ^ eye
            canvas.draw_pixels("#2C3E50", [(ox + 14, oy + 9), (ox + 15, oy + 8), (ox + 16, oy + 9)])
        elif eye_type == "spiral" or eye_type == "dizzy":
            # @ eye
            canvas.draw_pixels("#C0392B", [
                (ox + 13, oy + 9), (ox + 14, oy + 8), (ox + 15, oy + 9), (ox + 14, oy + 10), (ox + 13, oy + 10)
            ])
        elif eye_type == "sleep":
            # - eye
            canvas.fill_rect(ox + 13, oy + 10, 4, 1, "#2C3E50")
        elif blink:
            # - eye
            canvas.fill_rect(ox + 13, oy + 10, 3, 1, "#2C3E50")
        else:
            # Big sparkly eye
            canvas.fill_rect(ox + 13, oy + 9, 3, 3, "#2C3E50")
            canvas.set_pixel(ox + 14, oy + 9, "#FFFFFF") # Shine

        # Beak
        canvas.fill_rect(ox + 17, oy + 11, 6, 3, c_beak)
        canvas.fill_rect(ox + 17, oy + 13, 5, 1, c_beak_dark)

        # Body
        canvas.fill_rect(ox + 5, oy + 15, 13, 10, c_body)
        canvas.fill_rect(ox + 4, oy + 17, 3, 6, c_body_dark) # Back/tail
        canvas.fill_rect(ox + 5, oy + 23, 12, 2, c_body_dark) # Belly shadow

        # Wing (relaxed)
        canvas.fill_rect(ox + 8, oy + 17, 6, 5, c_body_dark)

        # Feet
        canvas.fill_rect(ox + 7, oy + 25, 4, 2, c_feet)
        canvas.fill_rect(ox + 13, oy + 25, 4, 2, c_feet)

    def _render_idle(self) -> list[PixelCanvas]:
        frames = []
        for i in range(4):
            c = PixelCanvas(36, 36)
            bob = 1 if i in (1, 3) else 0
            blink = (i == 2)
            self._draw_base_duck(c, 7, 5 + bob, blink=blink)
            frames.append(c)
        return frames

    def _render_thinking(self) -> list[PixelCanvas]:
        frames = []
        for i in range(4):
            c = PixelCanvas(36, 36)
            self._draw_base_duck(c, 7, 6, eye_type="normal")
            # Thinking bubble above head
            bubble_colors = ["#3498DB", "#2980B9", "#00CEC9", "#74B9FF"]
            col = bubble_colors[i]
            # Gear or lightbulb dots
            if i % 2 == 0:
                c.fill_rect(24, 3, 4, 4, col)
                c.fill_rect(22, 5, 8, 2, col)
                c.set_pixel(21, 9, col)
            else:
                c.fill_rect(23, 2, 5, 5, col)
                c.fill_rect(25, 1, 2, 2, "#F1C40F") # Yellow bulb glow
                c.set_pixel(22, 8, col)
            frames.append(c)
        return frames

    def _render_working(self) -> list[PixelCanvas]:
        frames = []
        for i in range(4):
            c = PixelCanvas(36, 36)
            # Duck sitting forward
            self._draw_base_duck(c, 4, 6, eye_type="normal")

            # Laptop
            # Screen
            c.fill_rect(19, 13, 2, 10, "#34495E") # Screen lid
            c.fill_rect(21, 14, 1, 8, "#00F0FF")  # Screen glow
            # Base/keyboard
            c.fill_rect(17, 23, 11, 2, "#7F8C8D")

            # Typing wings (alternating up and down)
            if i % 2 == 0:
                c.fill_rect(13, 19, 4, 3, "#E1B12C") # Left wing on keys
                c.fill_rect(11, 17, 3, 3, "#F9D342") # Right wing raised
            else:
                c.fill_rect(11, 19, 3, 3, "#E1B12C") # Right wing down
                c.fill_rect(14, 16, 4, 3, "#F9D342") # Left wing raised

            # Flying code particles
            code_particles = [
                [(24, 9), (28, 6)],
                [(25, 7), (29, 4)],
                [(23, 6), (27, 8)],
                [(26, 8), (30, 5)],
            ]
            for px, py in code_particles[i]:
                c.fill_rect(px, py, 2, 2, "#00FFCC")

            frames.append(c)
        return frames

    def _render_done(self) -> list[PixelCanvas]:
        frames = []
        for i in range(4):
            c = PixelCanvas(36, 36)
            jump_y = -3 if i in (1, 2) else 0
            self._draw_base_duck(c, 7, 5 + jump_y, eye_type="happy")
            # Wings up in V-shape
            c.fill_rect(5, 14 + jump_y, 3, 5, "#E1B12C")
            c.fill_rect(19, 14 + jump_y, 3, 5, "#E1B12C")

            # Victory stars
            star_coords = [
                [(4, 4), (27, 6)],
                [(3, 6), (28, 4), (16, 1)],
                [(5, 5), (26, 7), (15, 2)],
                [(4, 3), (29, 5)]
            ]
            for sx, sy in star_coords[i]:
                c.fill_rect(sx, sy, 3, 3, "#F1C40F")
                c.set_pixel(sx + 1, sy - 1, "#F39C12")
                c.set_pixel(sx + 1, sy + 3, "#F39C12")
                c.set_pixel(sx - 1, sy + 1, "#F39C12")
                c.set_pixel(sx + 3, sy + 1, "#F39C12")

            frames.append(c)
        return frames

    def _render_error(self) -> list[PixelCanvas]:
        frames = []
        for i in range(4):
            c = PixelCanvas(36, 36)
            shake_x = 1 if i % 2 == 0 else -1
            self._draw_base_duck(c, 7 + shake_x, 6, eye_type="spiral")
            # Sweat drop
            c.fill_rect(24, 10 + (i * 2) % 6, 2, 3, "#3498DB")
            c.set_pixel(24, 9 + (i * 2) % 6, "#74B9FF")
            # Alert sign
            if i % 2 == 1:
                c.fill_rect(26, 2, 2, 4, "#E74C3C")
                c.set_pixel(26, 7, "#E74C3C")
            frames.append(c)
        return frames

    def _render_waiting(self) -> list[PixelCanvas]:
        frames = []
        for i in range(4):
            c = PixelCanvas(36, 36)
            self._draw_base_duck(c, 7, 6, eye_type="normal")
            # Waving wing
            if i % 2 == 0:
                c.fill_rect(19, 14, 4, 3, "#F9D342")
                c.fill_rect(22, 12, 3, 3, "#F9D342")
            else:
                c.fill_rect(19, 16, 4, 3, "#F9D342")
                c.fill_rect(22, 18, 3, 3, "#F9D342")

            # Exclamation bubble
            c.fill_rect(26, 4, 2, 5, "#F39C12")
            c.set_pixel(26, 11, "#F39C12")
            frames.append(c)
        return frames

    def _render_clicked(self) -> list[PixelCanvas]:
        frames = []
        for i in range(4):
            c = PixelCanvas(36, 36)
            bounce_y = -2 if i in (1, 2) else 0
            self._draw_base_duck(c, 7, 6 + bounce_y, eye_type="happy")
            # Pink blush cheeks
            c.fill_rect(12, 12 + bounce_y, 3, 2, "#FF7675")
            c.fill_rect(18, 12 + bounce_y, 3, 2, "#FF7675")

            # Heart floating up
            hx, hy = 23, 7 - i * 2
            c.fill_rect(hx, hy + 1, 2, 2, "#E84393")
            c.fill_rect(hx + 3, hy + 1, 2, 2, "#E84393")
            c.fill_rect(hx + 1, hy + 2, 4, 2, "#FD79A8")
            c.fill_rect(hx + 2, hy + 4, 2, 1, "#E84393")
            frames.append(c)
        return frames

    def _render_sleep(self) -> list[PixelCanvas]:
        frames = []
        for i in range(4):
            c = PixelCanvas(36, 36)
            # Curled up duck
            c_body = "#F9D342"
            c_beak = "#F39C12"
            breath = 1 if i in (1, 2) else 0

            # Round curled body
            c.fill_rect(7, 14 + breath, 18, 11 - breath, c_body)
            c.fill_rect(5, 16 + breath, 22, 8 - breath, c_body)
            # Sleeping eye
            c.fill_rect(16, 17 + breath, 4, 1, "#2C3E50")
            # Tucked beak
            c.fill_rect(20, 18 + breath, 5, 2, c_beak)
            # Cap on top
            c.fill_rect(11, 12 + breath, 8, 3, "#2ECC71")

            # Drifting Zzz
            zx = 24 + i * 2
            zy = 10 - i * 2
            # Draw 'z'
            c.fill_rect(zx, zy, 4, 1, "#74B9FF")
            c.set_pixel(zx + 2, zy + 1, "#74B9FF")
            c.set_pixel(zx + 1, zy + 2, "#74B9FF")
            c.fill_rect(zx, zy + 3, 4, 1, "#74B9FF")

            frames.append(c)
        return frames
