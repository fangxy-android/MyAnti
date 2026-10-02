"""CodeBot character - retro CRT robot developer companion."""
from PySide6.QtGui import QPixmap
from engine.pet_state import PetState
from graphics.characters.base import CharacterBase
from graphics.pixel_canvas import PixelCanvas

from graphics.renderer import CrispRenderer

class CodeBotCharacter(CharacterBase):
    name = "codebot"
    display_name = "赛博机人 CodeBot"
    description = "复古CRT显示器机器人，用像素脸表达各种编程状态！"

    def render_frames(self, state: PetState, target_size: int = 128) -> list[QPixmap]:
        return [
            CrispRenderer.render_codebot(state, i, target_size)
            for i in range(4)
        ]

    def _draw_robot_body(self, canvas: PixelCanvas, ox: int, oy: int, antenna_blink: bool = False):
        c_body = "#34495E"
        c_body_dark = "#2C3E50"
        c_screen_bg = "#1A252F"
        c_antenna = "#00F0FF" if antenna_blink else "#16A085"

        # Antenna
        canvas.fill_rect(ox + 16, oy + 2, 2, 4, "#7F8C8D")
        canvas.fill_rect(ox + 15, oy + 0, 4, 3, c_antenna)

        # Head / Monitor casing
        canvas.fill_rect(ox + 7, oy + 6, 20, 15, c_body)
        canvas.fill_rect(ox + 6, oy + 7, 22, 13, c_body)
        # Inner screen
        canvas.fill_rect(ox + 9, oy + 8, 16, 11, c_screen_bg)

        # Body chassis
        canvas.fill_rect(ox + 11, oy + 22, 12, 6, c_body_dark)
        # Chest LED
        canvas.fill_rect(ox + 15, oy + 24, 4, 2, "#2ECC71")

        # Treads / Feet
        canvas.fill_rect(ox + 8, oy + 28, 6, 3, "#7F8C8D")
        canvas.fill_rect(ox + 20, oy + 28, 6, 3, "#7F8C8D")

    def _render_idle(self) -> list[PixelCanvas]:
        frames = []
        for i in range(4):
            c = PixelCanvas(36, 36)
            bob = 1 if i in (1, 3) else 0
            blink = (i == 2)
            self._draw_robot_body(c, 1, 3 + bob, antenna_blink=(i % 2 == 1))
            # Screen Face: [ • ◡ • ]
            c_glow = "#00F0FF"
            if blink:
                c.fill_rect(13, 15 + bob, 3, 1, c_glow)
                c.fill_rect(19, 15 + bob, 3, 1, c_glow)
            else:
                c.fill_rect(13, 14 + bob, 3, 3, c_glow)
                c.fill_rect(19, 14 + bob, 3, 3, c_glow)
            # Smile
            c.draw_pixels(c_glow, [(16, 17 + bob), (17, 18 + bob), (18, 17 + bob)])
            frames.append(c)
        return frames

    def _render_thinking(self) -> list[PixelCanvas]:
        frames = []
        spin_chars = [
            [(16, 13), (16, 15), (16, 17)], # |
            [(14, 13), (16, 15), (18, 17)], # \
            [(14, 15), (16, 15), (18, 15)], # -
            [(18, 13), (16, 15), (14, 17)], # /
        ]
        for i in range(4):
            c = PixelCanvas(36, 36)
            self._draw_robot_body(c, 1, 3, antenna_blink=True)
            c.draw_pixels("#F1C40F", spin_chars[i])
            frames.append(c)
        return frames

    def _render_working(self) -> list[PixelCanvas]:
        frames = []
        patterns = [
            [(12, 13), (15, 14), (18, 13), (21, 16)], # Matrix 1010
            [(13, 16), (16, 13), (19, 15), (22, 14)],
            [(11, 14), (14, 16), (17, 13), (20, 15)],
            [(13, 13), (15, 16), (18, 14), (21, 13)],
        ]
        for i in range(4):
            c = PixelCanvas(36, 36)
            self._draw_robot_body(c, 1, 3, antenna_blink=True)
            # Code streams
            for px, py in patterns[i]:
                c.fill_rect(px, py, 2, 2, "#2ECC71")
            # Mini mechanical arms typing
            if i % 2 == 0:
                c.fill_rect(7, 23, 4, 3, "#BDC3C7")
                c.fill_rect(24, 21, 4, 3, "#BDC3C7")
            else:
                c.fill_rect(7, 21, 4, 3, "#BDC3C7")
                c.fill_rect(24, 23, 4, 3, "#BDC3C7")
            frames.append(c)
        return frames

    def _render_done(self) -> list[PixelCanvas]:
        frames = []
        for i in range(4):
            c = PixelCanvas(36, 36)
            jump = -3 if i in (1, 2) else 0
            self._draw_robot_body(c, 1, 3 + jump, antenna_blink=True)
            # Screen Face: [ ^ ▽ ^ ]
            c_glow = "#2ECC71"
            c.draw_pixels(c_glow, [
                (13, 14 + jump), (14, 13 + jump), (15, 14 + jump),
                (19, 14 + jump), (20, 13 + jump), (21, 14 + jump),
                (16, 16 + jump), (17, 17 + jump), (18, 16 + jump)
            ])
            # Sparkles
            c.fill_rect(4, 5, 2, 2, "#F1C40F")
            c.fill_rect(29, 6, 2, 2, "#00F0FF")
            frames.append(c)
        return frames

    def _render_error(self) -> list[PixelCanvas]:
        frames = []
        for i in range(4):
            c = PixelCanvas(36, 36)
            sh = 1 if i % 2 == 0 else -1
            self._draw_robot_body(c, 1 + sh, 3, antenna_blink=False)
            # BSOD Screen: [ X _ X ]
            c_red = "#E74C3C"
            # Left X
            c.draw_pixels(c_red, [(12, 13), (14, 13), (13, 14), (12, 15), (14, 15)])
            # Right X
            c.draw_pixels(c_red, [(19, 13), (21, 13), (20, 14), (19, 15), (21, 15)])
            # Flat mouth
            c.fill_rect(15, 17, 4, 1, c_red)
            frames.append(c)
        return frames

    def _render_waiting(self) -> list[PixelCanvas]:
        frames = []
        for i in range(4):
            c = PixelCanvas(36, 36)
            self._draw_robot_body(c, 1, 3, antenna_blink=(i % 2 == 0))
            # Screen: [ ! _ ! ]
            c_yellow = "#F39C12"
            c.fill_rect(13, 12, 2, 3, c_yellow)
            c.set_pixel(13, 16, c_yellow)
            c.fill_rect(20, 12, 2, 3, c_yellow)
            c.set_pixel(20, 16, c_yellow)
            frames.append(c)
        return frames

    def _render_clicked(self) -> list[PixelCanvas]:
        frames = []
        for i in range(4):
            c = PixelCanvas(36, 36)
            b = -2 if i in (1, 2) else 0
            self._draw_robot_body(c, 1, 3 + b, antenna_blink=True)
            # Screen: [ ♥ _ ♥ ]
            c_heart = "#E84393"
            # Left heart
            c.draw_pixels(c_heart, [(12, 13 + b), (14, 13 + b), (13, 14 + b), (13, 15 + b)])
            # Right heart
            c.draw_pixels(c_heart, [(19, 13 + b), (21, 13 + b), (20, 14 + b), (20, 15 + b)])
            frames.append(c)
        return frames

    def _render_sleep(self) -> list[PixelCanvas]:
        frames = []
        for i in range(4):
            c = PixelCanvas(36, 36)
            self._draw_robot_body(c, 1, 4, antenna_blink=False)
            # Standby face: [ - _ - ] in dim gray
            c.fill_rect(13, 15, 3, 1, "#7F8C8D")
            c.fill_rect(19, 15, 3, 1, "#7F8C8D")
            zx = 26 + i * 2
            zy = 10 - i * 2
            c.fill_rect(zx, zy, 4, 1, "#74B9FF")
            c.set_pixel(zx + 2, zy + 1, "#74B9FF")
            c.set_pixel(zx + 1, zy + 2, "#74B9FF")
            c.fill_rect(zx, zy + 3, 4, 1, "#74B9FF")
            frames.append(c)
        return frames
