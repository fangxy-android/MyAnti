"""High-DPI Vector-Pixel Character Renderer.
Generates razor-sharp, smooth, vibrant character animations at any display scale.
"""
from PySide6.QtGui import QPixmap, QPainter, QColor, QBrush, QPen, QPainterPath, QFont, QRadialGradient, QLinearGradient
from PySide6.QtCore import Qt, QRectF, QPointF
from engine.pet_state import PetState

class CrispRenderer:
    @staticmethod
    def create_canvas(size: int) -> tuple[QPixmap, QPainter]:
        pm = QPixmap(size, size)
        pm.fill(Qt.GlobalColor.transparent)
        p = QPainter(pm)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        p.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)
        return pm, p

    # ==================== DEWEY THE DUCK ====================
    @classmethod
    def render_dewey(cls, state: PetState, frame_idx: int, size: int) -> QPixmap:
        pm, p = cls.create_canvas(size)
        s = size / 128.0 # Normalization scale based on 128px

        # Animation offsets
        bob_y = 0.0
        if state == PetState.IDLE:
            bob_y = [0, 2, 0, -2][frame_idx % 4] * s
        elif state == PetState.WORKING:
            bob_y = [0, -1, 1, 0][frame_idx % 4] * s
        elif state == PetState.DONE:
            bob_y = [0, -8, -12, -4][frame_idx % 4] * s
        elif state == PetState.CLICKED:
            bob_y = [0, -6, -4, 0][frame_idx % 4] * s

        # Duck Center Coordinates
        cx = 64 * s
        cy = (68 * s) + bob_y

        # 1. Shadow under duck
        shadow_w = (42 if state != PetState.DONE else 28) * s
        p.setBrush(QColor(0, 0, 0, 35))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(QPointF(cx, 114 * s), shadow_w, 6 * s)

        # 2. Feet (Orange)
        if state != PetState.SLEEP:
            p.setBrush(QColor("#E67E22"))
            p.setPen(QPen(QColor("#D35400"), 1.5 * s))
            p.drawRoundedRect(QRectF(cx - 18 * s, cy + 32 * s, 14 * s, 8 * s), 4 * s, 4 * s)
            p.drawRoundedRect(QRectF(cx + 4 * s, cy + 32 * s, 14 * s, 8 * s), 4 * s, 4 * s)

        # 3. Body (Yellow)
        body_grad = QLinearGradient(cx, cy - 20 * s, cx, cy + 36 * s)
        body_grad.setColorAt(0.0, QColor("#FFE066"))
        body_grad.setColorAt(1.0, QColor("#F5B041"))
        p.setBrush(body_grad)
        p.setPen(QPen(QColor("#E67E22"), 2 * s))

        if state == PetState.SLEEP:
            # Curled up puffball
            p.drawEllipse(QPointF(cx, cy + 10 * s), 36 * s, 26 * s)
        else:
            # Main round body
            p.drawEllipse(QPointF(cx, cy + 12 * s), 30 * s, 26 * s)
            # Head
            head_grad = QLinearGradient(cx, cy - 36 * s, cx, cy + 4 * s)
            head_grad.setColorAt(0.0, QColor("#FFF3B0"))
            head_grad.setColorAt(1.0, QColor("#F9D342"))
            p.setBrush(head_grad)
            p.drawEllipse(QPointF(cx, cy - 14 * s), 25 * s, 23 * s)

        # 4. Cap (Green Baseball Cap)
        cap_color = QColor("#2ECC71")
        cap_dark = QColor("#27AE60")
        p.setBrush(cap_color)
        p.setPen(QPen(cap_dark, 1.5 * s))

        cap_y = (cy - 30 * s) if state != PetState.SLEEP else (cy - 12 * s)
        p.drawChord(QRectF(cx - 20 * s, cap_y, 40 * s, 24 * s), 0, 180 * 16) # Dome
        # Cap visor
        p.drawRoundedRect(QRectF(cx + 4 * s, cap_y + 10 * s, 20 * s, 6 * s), 3 * s, 3 * s)
        # Cap button
        p.setBrush(cap_dark)
        p.drawEllipse(QPointF(cx, cap_y + 2 * s), 3 * s, 3 * s)

        # 5. Eyes
        eye_y = cy - 16 * s
        if state == PetState.DONE or state == PetState.CLICKED:
            # Happy smiling ^ ^ eyes
            p.setPen(QPen(QColor("#2C3E50"), 3 * s, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            p.setBrush(Qt.BrushStyle.NoBrush)
            # Left arc
            path_l = QPainterPath()
            path_l.moveTo(cx - 14 * s, eye_y + 2 * s)
            path_l.quadTo(cx - 9 * s, eye_y - 6 * s, cx - 4 * s, eye_y + 2 * s)
            p.drawPath(path_l)
            # Right arc
            path_r = QPainterPath()
            path_r.moveTo(cx + 4 * s, eye_y + 2 * s)
            path_r.quadTo(cx + 9 * s, eye_y - 6 * s, cx + 14 * s, eye_y + 2 * s)
            p.drawPath(path_r)

        elif state == PetState.ERROR:
            # Dizzy spiral / shock eyes
            p.setPen(QPen(QColor("#C0392B"), 2.5 * s, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            p.setBrush(Qt.BrushStyle.NoBrush)
            # Left X
            p.drawLine(QPointF(cx - 14 * s, eye_y - 4 * s), QPointF(cx - 6 * s, eye_y + 4 * s))
            p.drawLine(QPointF(cx - 6 * s, eye_y - 4 * s), QPointF(cx - 14 * s, eye_y + 4 * s))
            # Right X
            p.drawLine(QPointF(cx + 6 * s, eye_y - 4 * s), QPointF(cx + 14 * s, eye_y + 4 * s))
            p.drawLine(QPointF(cx + 14 * s, eye_y - 4 * s), QPointF(cx + 6 * s, eye_y + 4 * s))

        elif state == PetState.SLEEP or (state == PetState.IDLE and frame_idx == 2):
            # Closed calm line
            p.setPen(QPen(QColor("#2C3E50"), 2.5 * s, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            p.drawLine(QPointF(cx - 14 * s, eye_y), QPointF(cx - 4 * s, eye_y))
            p.drawLine(QPointF(cx + 4 * s, eye_y), QPointF(cx + 14 * s, eye_y))

        else:
            # Big shiny anime eyes
            p.setBrush(QColor("#1A252F"))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(QPointF(cx - 9 * s, eye_y), 5 * s, 7 * s)
            p.drawEllipse(QPointF(cx + 9 * s, eye_y), 5 * s, 7 * s)
            # White sparkles
            p.setBrush(QColor("#FFFFFF"))
            p.drawEllipse(QPointF(cx - 10 * s, eye_y - 2 * s), 2.2 * s, 3 * s)
            p.drawEllipse(QPointF(cx + 8 * s, eye_y - 2 * s), 2.2 * s, 3 * s)
            p.drawEllipse(QPointF(cx - 8 * s, eye_y + 3 * s), 1.2 * s, 1.2 * s)
            p.drawEllipse(QPointF(cx + 10 * s, eye_y + 3 * s), 1.2 * s, 1.2 * s)

        # 6. Beak (Orange)
        beak_y = (cy - 6 * s) if state != PetState.SLEEP else (cy + 2 * s)
        beak_grad = QLinearGradient(cx, beak_y - 4 * s, cx, beak_y + 8 * s)
        beak_grad.setColorAt(0.0, QColor("#F39C12"))
        beak_grad.setColorAt(1.0, QColor("#D35400"))
        p.setBrush(beak_grad)
        p.setPen(QPen(QColor("#BA4A00"), 1.5 * s))
        p.drawRoundedRect(QRectF(cx + 6 * s, beak_y, 18 * s, 10 * s), 5 * s, 5 * s)

        # 7. Blush (if clicked / happy)
        if state in (PetState.CLICKED, PetState.DONE):
            p.setBrush(QColor(255, 118, 117, 180))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(QPointF(cx - 16 * s, cy - 6 * s), 6 * s, 3.5 * s)
            p.drawEllipse(QPointF(cx + 16 * s, cy - 6 * s), 6 * s, 3.5 * s)

        # 8. State-specific props:
        # A. Working: Laptop + Typing Wings + Flying Code Particles
        if state == PetState.WORKING:
            # Mini silver/dark laptop
            p.setBrush(QColor("#2C3E50"))
            p.setPen(QPen(QColor("#1A252F"), 1.5 * s))
            # Screen
            p.drawRoundedRect(QRectF(cx + 14 * s, cy - 2 * s, 6 * s, 26 * s), 2 * s, 2 * s)
            # Glowing cyan screen front
            p.setBrush(QColor("#00F0FF"))
            p.drawRect(QRectF(cx + 18 * s, cy + 1 * s, 2 * s, 20 * s))
            # Laptop base / keyboard
            p.setBrush(QColor("#7F8C8D"))
            p.drawRoundedRect(QRectF(cx + 6 * s, cy + 22 * s, 26 * s, 5 * s), 2 * s, 2 * s)

            # Wings typing alternating
            p.setBrush(QColor("#F5B041"))
            p.setPen(QPen(QColor("#E67E22"), 1.5 * s))
            w_offset = (frame_idx % 2) * 4 * s
            p.drawEllipse(QPointF(cx - 6 * s, cy + 18 * s - w_offset), 8 * s, 6 * s)
            p.drawEllipse(QPointF(cx + 10 * s, cy + 16 * s + w_offset), 8 * s, 6 * s)

            # Flying code particles `< / >` `{ }`
            p.setPen(QPen(QColor("#00F0FF"), 1.5 * s))
            p.setFont(QFont("Consolas", int(10 * s), QFont.Weight.Bold))
            particles = [
                ("{ }", cx + 22 * s, cy - 8 * s),
                ("</>", cx + 28 * s, cy - 18 * s),
                ("01", cx + 20 * s, cy - 24 * s),
                ("=>", cx + 30 * s, cy - 10 * s),
            ]
            tag, tx, ty = particles[frame_idx % 4]
            p.drawText(QPointF(tx, ty), tag)

        # B. Thinking: Floating Lightbulb / Gears / Bubbles
        elif state == PetState.THINKING:
            # Thinking bubble
            p.setBrush(QColor(0, 206, 201, 210))
            p.setPen(QPen(QColor("#00CEC9"), 1.5 * s))
            p.drawEllipse(QPointF(cx + 26 * s, cy - 36 * s), 12 * s, 12 * s)
            p.drawEllipse(QPointF(cx + 18 * s, cy - 24 * s), 5 * s, 5 * s)
            p.drawEllipse(QPointF(cx + 12 * s, cy - 16 * s), 3 * s, 3 * s)

            # Lightbulb icon inside
            p.setPen(QPen(QColor("#FFEAA7"), 2 * s))
            p.setFont(QFont("Segoe UI Emoji", int(11 * s), QFont.Weight.Bold))
            p.drawText(QRectF(cx + 16 * s, cy - 46 * s, 20 * s, 20 * s), Qt.AlignmentFlag.AlignCenter, "💡")

        # C. Done: Victory Stars & Sparkles
        elif state == PetState.DONE:
            # Open wings in V shape
            p.setBrush(QColor("#F5B041"))
            p.setPen(QPen(QColor("#E67E22"), 1.5 * s))
            p.drawEllipse(QPointF(cx - 26 * s, cy + 6 * s), 10 * s, 7 * s)
            p.drawEllipse(QPointF(cx + 26 * s, cy + 6 * s), 10 * s, 7 * s)

            # Golden Stars
            stars = [
                (cx - 30 * s, cy - 28 * s),
                (cx + 30 * s, cy - 28 * s),
                (cx, cy - 46 * s),
                (cx + 24 * s, cy - 40 * s)
            ]
            p.setFont(QFont("Segoe UI Emoji", int(14 * s)))
            p.setPen(QColor("#F1C40F"))
            for sx, sy in stars:
                p.drawText(QPointF(sx, sy), "✨")

        # D. Error: Big Blue Sweat Drop & Exclamation
        elif state == PetState.ERROR:
            # Sweat drop
            p.setBrush(QColor("#3498DB"))
            p.setPen(QPen(QColor("#2980B9"), 1.5 * s))
            p.drawEllipse(QPointF(cx + 26 * s, cy - 14 * s + (frame_idx * 3 * s)), 5 * s, 7 * s)

        # E. Clicked: Floating Hearts
        elif state == PetState.CLICKED:
            p.setFont(QFont("Segoe UI Emoji", int(14 * s)))
            p.setPen(QColor("#E84393"))
            p.drawText(QPointF(cx + 18 * s, cy - 24 * s - (frame_idx * 4 * s)), "❤️")

        # F. Sleep: Floating Zzz
        elif state == PetState.SLEEP:
            p.setFont(QFont("Segoe UI", int(12 * s), QFont.Weight.Bold))
            p.setPen(QColor("#74B9FF"))
            zy = cy - 14 * s - (frame_idx * 4 * s)
            p.drawText(QPointF(cx + 20 * s, zy), "Z")
            p.drawText(QPointF(cx + 28 * s, zy - 8 * s), "z")

        p.end()
        return pm

    # ==================== FIREBALL ====================
    @classmethod
    def render_fireball(cls, state: PetState, frame_idx: int, size: int) -> QPixmap:
        pm, p = cls.create_canvas(size)
        s = size / 128.0

        bob_y = [0, -2, 2, 0][frame_idx % 4] * s
        cx = 64 * s
        cy = (68 * s) + bob_y

        # Shadow
        p.setBrush(QColor(0, 0, 0, 30))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(QPointF(cx, 114 * s), 36 * s, 6 * s)

        # Palette selection based on state
        if state == PetState.THINKING:
            c_outer = QColor("#0984E3")
            c_mid = QColor("#00CEC9")
            c_core = QColor("#E0F7FA")
        elif state == PetState.ERROR:
            c_outer = QColor("#636E72")
            c_mid = QColor("#B2BEC3")
            c_core = QColor("#DFE6E9")
        elif state == PetState.CLICKED:
            c_outer = QColor("#D63031")
            c_mid = QColor("#FD79A8")
            c_core = QColor("#FFF0F5")
        else:
            c_outer = QColor("#E17055")
            c_mid = QColor("#F39C12")
            c_core = QColor("#FFF9E6")

        # Outer Flame Path
        tip_shift = [-4, 0, 4, 1][frame_idx % 4] * s
        flame_path = QPainterPath()
        flame_path.moveTo(cx - 32 * s, cy + 20 * s)
        flame_path.cubicTo(cx - 40 * s, cy - 10 * s, cx - 20 * s, cy - 30 * s, cx + tip_shift, cy - 50 * s)
        flame_path.cubicTo(cx + 10 * s, cy - 36 * s, cx + 40 * s, cy - 10 * s, cx + 32 * s, cy + 20 * s)
        flame_path.cubicTo(cx + 24 * s, cy + 42 * s, cx - 24 * s, cy + 42 * s, cx - 32 * s, cy + 20 * s)

        p.setBrush(c_outer)
        p.setPen(Qt.PenStyle.NoPen)
        p.drawPath(flame_path)

        # Mid Flame
        mid_path = QPainterPath()
        mid_path.moveTo(cx - 24 * s, cy + 18 * s)
        mid_path.cubicTo(cx - 28 * s, cy - 4 * s, cx - 12 * s, cy - 20 * s, cx + tip_shift * 0.7, cy - 36 * s)
        mid_path.cubicTo(cx + 8 * s, cy - 24 * s, cx + 28 * s, cy - 4 * s, cx + 24 * s, cy + 18 * s)
        mid_path.cubicTo(cx + 16 * s, cy + 34 * s, cx - 16 * s, cy + 34 * s, cx - 24 * s, cy + 18 * s)
        p.setBrush(c_mid)
        p.drawPath(mid_path)

        # Inner Glowing Core
        p.setBrush(c_core)
        p.drawEllipse(QPointF(cx, cy + 8 * s), 16 * s, 18 * s)

        # Eyes
        eye_y = cy + 6 * s
        if state in (PetState.DONE, PetState.CLICKED):
            p.setPen(QPen(QColor("#2D3436"), 2.5 * s, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawArc(QRectF(cx - 15 * s, eye_y - 6 * s, 10 * s, 8 * s), 0, 180 * 16)
            p.drawArc(QRectF(cx + 5 * s, eye_y - 6 * s, 10 * s, 8 * s), 0, 180 * 16)
        elif state == PetState.ERROR:
            p.setPen(QPen(QColor("#2D3436"), 2 * s))
            p.drawLine(QPointF(cx - 14 * s, eye_y - 4 * s), QPointF(cx - 6 * s, eye_y + 4 * s))
            p.drawLine(QPointF(cx - 6 * s, eye_y - 4 * s), QPointF(cx - 14 * s, eye_y + 4 * s))
            p.drawLine(QPointF(cx + 6 * s, eye_y - 4 * s), QPointF(cx + 14 * s, eye_y + 4 * s))
            p.drawLine(QPointF(cx + 14 * s, eye_y - 4 * s), QPointF(cx + 6 * s, eye_y + 4 * s))
        else:
            p.setBrush(QColor("#2D3436"))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(QPointF(cx - 10 * s, eye_y), 4.5 * s, 6.5 * s)
            p.drawEllipse(QPointF(cx + 10 * s, eye_y), 4.5 * s, 6.5 * s)
            p.setBrush(QColor("#FFFFFF"))
            p.drawEllipse(QPointF(cx - 11 * s, eye_y - 2 * s), 2 * s, 2.5 * s)
            p.drawEllipse(QPointF(cx + 9 * s, eye_y - 2 * s), 2 * s, 2.5 * s)

        # State Props
        if state == PetState.WORKING:
            # Sparks
            p.setFont(QFont("Segoe UI Emoji", int(12 * s)))
            p.setPen(QColor("#F1C40F"))
            p.drawText(QPointF(cx + 26 * s, cy - 18 * s), "⚡")
        elif state == PetState.DONE:
            p.setFont(QFont("Segoe UI Emoji", int(14 * s)))
            p.setPen(QColor("#F1C40F"))
            p.drawText(QPointF(cx - 28 * s, cy - 24 * s), "🎉")
            p.drawText(QPointF(cx + 22 * s, cy - 28 * s), "✨")

        p.end()
        return pm

    # ==================== CODEBOT ====================
    @classmethod
    def render_codebot(cls, state: PetState, frame_idx: int, size: int) -> QPixmap:
        pm, p = cls.create_canvas(size)
        s = size / 128.0

        bob_y = [0, 2, 0, -2][frame_idx % 4] * s
        cx = 64 * s
        cy = (66 * s) + bob_y

        # Shadow
        p.setBrush(QColor(0, 0, 0, 35))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(QPointF(cx, 114 * s), 36 * s, 6 * s)

        # Antenna
        p.setPen(QPen(QColor("#7F8C8D"), 3 * s))
        p.drawLine(QPointF(cx, cy - 32 * s), QPointF(cx, cy - 46 * s))
        # Antenna LED
        led_color = QColor("#00F0FF" if frame_idx % 2 == 0 else "#2ECC71")
        p.setBrush(led_color)
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(QPointF(cx, cy - 48 * s), 5 * s, 5 * s)

        # CRT Monitor Head
        p.setBrush(QColor("#2C3E50"))
        p.setPen(QPen(QColor("#1A252F"), 2.5 * s))
        p.drawRoundedRect(QRectF(cx - 36 * s, cy - 32 * s, 72 * s, 52 * s), 12 * s, 12 * s)

        # Screen (Dark Slate)
        p.setBrush(QColor("#0F172A"))
        p.setPen(QPen(QColor("#334155"), 1.5 * s))
        p.drawRoundedRect(QRectF(cx - 30 * s, cy - 26 * s, 60 * s, 40 * s), 8 * s, 8 * s)

        # Chassis base & feet
        p.setBrush(QColor("#34495E"))
        p.setPen(QPen(QColor("#1A252F"), 2 * s))
        p.drawRoundedRect(QRectF(cx - 24 * s, cy + 22 * s, 48 * s, 18 * s), 6 * s, 6 * s)
        # Feet
        p.setBrush(QColor("#7F8C8D"))
        p.drawRoundedRect(QRectF(cx - 28 * s, cy + 40 * s, 18 * s, 8 * s), 4 * s, 4 * s)
        p.drawRoundedRect(QRectF(cx + 10 * s, cy + 40 * s, 18 * s, 8 * s), 4 * s, 4 * s)

        # Phosphor Screen Face Expression
        face_color = QColor("#00F0FF")
        p.setFont(QFont("Consolas", int(14 * s), QFont.Weight.Bold))
        screen_rect = QRectF(cx - 30 * s, cy - 26 * s, 60 * s, 40 * s)

        if state == PetState.WORKING:
            p.setPen(QColor("#2ECC71"))
            streams = ["[ 1 0 1 ]", "[ 0 1 0 ]", "[ > _ < ]", "[ 1 1 0 ]"]
            p.drawText(screen_rect, Qt.AlignmentFlag.AlignCenter, streams[frame_idx % 4])
        elif state == PetState.DONE:
            p.setPen(QColor("#2ECC71"))
            p.drawText(screen_rect, Qt.AlignmentFlag.AlignCenter, "^ ▽ ^")
        elif state == PetState.ERROR:
            p.setPen(QColor("#E74C3C"))
            p.drawText(screen_rect, Qt.AlignmentFlag.AlignCenter, "X _ X")
        elif state == PetState.THINKING:
            p.setPen(QColor("#F1C40F"))
            spins = ["[ / ]", "[ - ]", "[ \\ ]", "[ | ]"]
            p.drawText(screen_rect, Qt.AlignmentFlag.AlignCenter, spins[frame_idx % 4])
        elif state == PetState.CLICKED:
            p.setPen(QColor("#E84393"))
            p.drawText(screen_rect, Qt.AlignmentFlag.AlignCenter, "♥ _ ♥")
        elif state == PetState.WAITING:
            p.setPen(QColor("#F39C12"))
            p.drawText(screen_rect, Qt.AlignmentFlag.AlignCenter, "? _ ?" if frame_idx % 2 == 0 else "! _ !")
        elif state == PetState.SLEEP:
            p.setPen(QColor("#64748B"))
            p.drawText(screen_rect, Qt.AlignmentFlag.AlignCenter, "- _ -")
        else: # IDLE
            p.setPen(face_color)
            blink = (frame_idx == 2)
            p.drawText(screen_rect, Qt.AlignmentFlag.AlignCenter, "- ◡ -" if blink else "• ◡ •")

        p.end()
        return pm

    # ==================== NEKO ====================
    @classmethod
    def render_neko(cls, state: PetState, frame_idx: int, size: int) -> QPixmap:
        pm, p = cls.create_canvas(size)
        s = size / 128.0

        bob_y = [0, 2, 0, -2][frame_idx % 4] * s
        cx = 64 * s
        cy = (68 * s) + bob_y

        # Shadow
        p.setBrush(QColor(0, 0, 0, 35))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(QPointF(cx, 114 * s), 36 * s, 6 * s)

        # Tail
        tail_path = QPainterPath()
        tail_shift = [-8, 0, 8, 2][frame_idx % 4] * s
        tail_path.moveTo(cx + 24 * s, cy + 24 * s)
        tail_path.quadTo(cx + 42 * s + tail_shift, cy + 10 * s, cx + 36 * s + tail_shift, cy - 6 * s)
        p.setPen(QPen(QColor("#2C3E50"), 6 * s, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawPath(tail_path)

        # Ears (Pointy)
        ear_path = QPainterPath()
        # Left ear
        ear_path.moveTo(cx - 24 * s, cy - 14 * s)
        ear_path.lineTo(cx - 20 * s, cy - 40 * s)
        ear_path.lineTo(cx - 6 * s, cy - 22 * s)
        ear_path.closeSubpath()
        # Right ear
        ear_path.moveTo(cx + 6 * s, cy - 22 * s)
        ear_path.lineTo(cx + 20 * s, cy - 40 * s)
        ear_path.lineTo(cx + 24 * s, cy - 14 * s)
        ear_path.closeSubpath()

        p.setBrush(QColor("#2C3E50"))
        p.setPen(QPen(QColor("#1A252F"), 1.5 * s))
        p.drawPath(ear_path)

        # Inner Pink Ears
        p.setBrush(QColor("#FF7675"))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawPolygon([QPointF(cx - 20 * s, cy - 18 * s), QPointF(cx - 18 * s, cy - 34 * s), QPointF(cx - 10 * s, cy - 22 * s)])
        p.drawPolygon([QPointF(cx + 10 * s, cy - 22 * s), QPointF(cx + 18 * s, cy - 34 * s), QPointF(cx + 20 * s, cy - 18 * s)])

        # Body & Head
        p.setBrush(QColor("#2C3E50"))
        p.setPen(QPen(QColor("#1A252F"), 2 * s))
        # Body
        p.drawEllipse(QPointF(cx, cy + 16 * s), 28 * s, 24 * s)
        # Head
        p.drawEllipse(QPointF(cx, cy - 12 * s), 26 * s, 22 * s)

        # White muzzle & chest
        p.setBrush(QColor("#FFFFFF"))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(QPointF(cx, cy - 4 * s), 14 * s, 10 * s)
        p.drawEllipse(QPointF(cx, cy + 20 * s), 14 * s, 16 * s)

        # Pink nose
        p.setBrush(QColor("#FF7675"))
        p.drawEllipse(QPointF(cx, cy - 7 * s), 3 * s, 2 * s)

        # Whiskers
        p.setPen(QPen(QColor("#FFFFFF"), 1.5 * s, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        p.drawLine(QPointF(cx - 14 * s, cy - 6 * s), QPointF(cx - 30 * s, cy - 8 * s))
        p.drawLine(QPointF(cx - 14 * s, cy - 2 * s), QPointF(cx - 28 * s, cy + 2 * s))
        p.drawLine(QPointF(cx + 14 * s, cy - 6 * s), QPointF(cx + 30 * s, cy - 8 * s))
        p.drawLine(QPointF(cx + 14 * s, cy - 2 * s), QPointF(cx + 28 * s, cy + 2 * s))

        # Eyes (Emerald Green Cat Eyes)
        eye_y = cy - 14 * s
        if state in (PetState.DONE, PetState.CLICKED):
            p.setPen(QPen(QColor("#FFFFFF"), 2.5 * s, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            p.drawArc(QRectF(cx - 16 * s, eye_y - 4 * s, 10 * s, 8 * s), 0, 180 * 16)
            p.drawArc(QRectF(cx + 6 * s, eye_y - 4 * s, 10 * s, 8 * s), 0, 180 * 16)
        else:
            p.setBrush(QColor("#2ECC71"))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(QPointF(cx - 11 * s, eye_y), 5 * s, 7 * s)
            p.drawEllipse(QPointF(cx + 11 * s, eye_y), 5 * s, 7 * s)
            # Slit pupil
            p.setBrush(QColor("#1A252F"))
            p.drawEllipse(QPointF(cx - 11 * s, eye_y), 1.8 * s, 6 * s)
            p.drawEllipse(QPointF(cx + 11 * s, eye_y), 1.8 * s, 6 * s)

        # State Props
        if state == PetState.WORKING:
            # Laptop
            p.setBrush(QColor("#34495E"))
            p.drawRoundedRect(QRectF(cx + 8 * s, cy + 18 * s, 26 * s, 5 * s), 2 * s, 2 * s)
            p.setBrush(QColor("#00F0FF"))
            p.drawRect(QRectF(cx + 18 * s, cy + 2 * s, 2 * s, 18 * s))
        elif state == PetState.DONE:
            p.setFont(QFont("Segoe UI Emoji", int(14 * s)))
            p.setPen(QColor("#3498DB"))
            p.drawText(QPointF(cx + 20 * s, cy - 24 * s), "🐟")

        p.end()
        return pm

    # ==================== SLIME ====================
    @classmethod
    def render_slime(cls, state: PetState, frame_idx: int, size: int) -> QPixmap:
        pm, p = cls.create_canvas(size)
        s = size / 128.0

        cx = 64 * s
        cy = 76 * s

        # Squash & stretch physics
        sw, sh = [(0, 0), (6, -6), (0, 0), (-6, 6)][frame_idx % 4]
        if state == PetState.DONE:
            cy -= [0, 8, 14, 4][frame_idx % 4] * s
        elif state == PetState.ERROR:
            sw, sh = (14, -14)

        rx = (34 + sw) * s
        ry = (26 + sh) * s

        # Shadow
        p.setBrush(QColor(0, 0, 0, 30))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(QPointF(cx, 114 * s), rx * 1.1, 7 * s)

        # Translucent Jelly Gradient
        grad = QLinearGradient(cx, cy - ry, cx, cy + ry)
        grad.setColorAt(0.0, QColor("#81ECEC"))
        grad.setColorAt(0.7, QColor("#00CEC9"))
        grad.setColorAt(1.0, QColor("#0984E3"))

        p.setBrush(grad)
        p.setPen(QPen(QColor("#00B894"), 2 * s))
        p.drawEllipse(QPointF(cx, cy), rx, ry)

        # Specular shine
        p.setBrush(QColor(255, 255, 255, 180))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(QPointF(cx - rx * 0.45, cy - ry * 0.45), 7 * s, 4 * s)

        # Eyes
        eye_y = cy - 2 * s
        if state in (PetState.DONE, PetState.CLICKED):
            p.setPen(QPen(QColor("#2D3436"), 2.5 * s, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawArc(QRectF(cx - 15 * s, eye_y - 4 * s, 9 * s, 7 * s), 0, 180 * 16)
            p.drawArc(QRectF(cx + 6 * s, eye_y - 4 * s, 9 * s, 7 * s), 0, 180 * 16)
        elif state == PetState.ERROR:
            p.setPen(QPen(QColor("#2D3436"), 2 * s))
            p.drawLine(QPointF(cx - 14 * s, eye_y - 3 * s), QPointF(cx - 6 * s, eye_y + 3 * s))
            p.drawLine(QPointF(cx - 6 * s, eye_y - 3 * s), QPointF(cx - 14 * s, eye_y + 3 * s))
            p.drawLine(QPointF(cx + 6 * s, eye_y - 3 * s), QPointF(cx + 14 * s, eye_y + 3 * s))
            p.drawLine(QPointF(cx + 14 * s, eye_y - 3 * s), QPointF(cx + 6 * s, eye_y + 3 * s))
        else:
            p.setBrush(QColor("#2D3436"))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(QPointF(cx - 10 * s, eye_y), 4.5 * s, 6 * s)
            p.drawEllipse(QPointF(cx + 10 * s, eye_y), 4.5 * s, 6 * s)
            p.setBrush(QColor("#FFFFFF"))
            p.drawEllipse(QPointF(cx - 11 * s, eye_y - 2 * s), 1.8 * s, 2.2 * s)
            p.drawEllipse(QPointF(cx + 9 * s, eye_y - 2 * s), 1.8 * s, 2.2 * s)

        # Crown (if DONE)
        if state == PetState.DONE:
            p.setFont(QFont("Segoe UI Emoji", int(16 * s)))
            p.setPen(QColor("#F1C40F"))
            p.drawText(QPointF(cx - 10 * s, cy - ry - 4 * s), "👑")

        p.end()
        return pm

    # ==================== SAKURA (二次元动漫少女) ====================
    @classmethod
    def render_sakura(cls, state: PetState, frame_idx: int, size: int) -> QPixmap:
        pm, p = cls.create_canvas(size)
        s = size / 128.0

        # Animation offsets
        bob_y = 0.0
        if state == PetState.IDLE:
            bob_y = [0, 2, 0, -2][frame_idx % 4] * s
        elif state == PetState.WORKING:
            bob_y = [0, -1, 1, 0][frame_idx % 4] * s
        elif state == PetState.DONE:
            bob_y = [0, -10, -14, -4][frame_idx % 4] * s
        elif state == PetState.CLICKED:
            bob_y = [0, -6, -4, 0][frame_idx % 4] * s

        cx = 64 * s
        cy = (64 * s) + bob_y

        # 1. Ground Shadow
        p.setBrush(QColor(0, 0, 0, 30))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(QPointF(cx, 114 * s), 34 * s, 6 * s)

        # 2. Flowing Twin Tails (Back layer)
        tail_shift = [-4, 0, 4, 1][frame_idx % 4] * s
        hair_color = QColor("#FF758F")
        hair_dark = QColor("#E05670")
        hair_light = QColor("#FFA8BA")

        # Left Twin Tail
        lt_path = QPainterPath()
        lt_path.moveTo(cx - 22 * s, cy - 14 * s)
        lt_path.cubicTo(cx - 44 * s + tail_shift, cy - 6 * s, cx - 46 * s - tail_shift, cy + 24 * s, cx - 32 * s + tail_shift, cy + 38 * s)
        lt_path.cubicTo(cx - 36 * s + tail_shift, cy + 20 * s, cx - 30 * s, cy + 6 * s, cx - 18 * s, cy - 6 * s)
        p.setBrush(hair_color)
        p.setPen(QPen(hair_dark, 1.5 * s))
        p.drawPath(lt_path)

        # Right Twin Tail
        rt_path = QPainterPath()
        rt_path.moveTo(cx + 22 * s, cy - 14 * s)
        rt_path.cubicTo(cx + 44 * s - tail_shift, cy - 6 * s, cx + 46 * s + tail_shift, cy + 24 * s, cx + 32 * s - tail_shift, cy + 38 * s)
        rt_path.cubicTo(cx + 36 * s - tail_shift, cy + 20 * s, cx + 30 * s, cy + 6 * s, cx + 18 * s, cy - 6 * s)
        p.drawPath(rt_path)

        # Hair Ribbons (Red/Crimson)
        p.setBrush(QColor("#D63031"))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(QPointF(cx - 22 * s, cy - 14 * s), 5 * s, 4 * s)
        p.drawEllipse(QPointF(cx + 22 * s, cy - 14 * s), 5 * s, 4 * s)

        # 3. Body & Sailor Uniform
        # Legs / Shoes
        p.setBrush(QColor("#FFEAA7")) # Fair skin
        p.drawRoundedRect(QRectF(cx - 10 * s, cy + 34 * s, 7 * s, 12 * s), 3 * s, 3 * s)
        p.drawRoundedRect(QRectF(cx + 3 * s, cy + 34 * s, 7 * s, 12 * s), 3 * s, 3 * s)
        # Brown Loafers
        p.setBrush(QColor("#6D4C41"))
        p.drawRoundedRect(QRectF(cx - 11 * s, cy + 42 * s, 9 * s, 6 * s), 2.5 * s, 2.5 * s)
        p.drawRoundedRect(QRectF(cx + 2 * s, cy + 42 * s, 9 * s, 6 * s), 2.5 * s, 2.5 * s)

        # Pleated Skirt (Navy Blue)
        p.setBrush(QColor("#1E3799"))
        p.setPen(QPen(QColor("#0C2461"), 1.2 * s))
        skirt_path = QPainterPath()
        skirt_path.moveTo(cx - 14 * s, cy + 24 * s)
        skirt_path.lineTo(cx + 14 * s, cy + 24 * s)
        skirt_path.lineTo(cx + 18 * s, cy + 35 * s)
        skirt_path.lineTo(cx - 18 * s, cy + 35 * s)
        skirt_path.closeSubpath()
        p.drawPath(skirt_path)

        # White Sailor Blouse & Collar
        p.setBrush(QColor("#F8FAFC"))
        p.drawRoundedRect(QRectF(cx - 13 * s, cy + 12 * s, 26 * s, 14 * s), 4 * s, 4 * s)
        # Navy blue sailor collar
        p.setBrush(QColor("#1E3799"))
        p.drawPolygon([QPointF(cx - 12 * s, cy + 12 * s), QPointF(cx, cy + 20 * s), QPointF(cx + 12 * s, cy + 12 * s)])
        # Red Ribbon Tie
        p.setBrush(QColor("#FF4757"))
        p.drawEllipse(QPointF(cx, cy + 17 * s), 3.5 * s, 3 * s)

        # 4. Chibi Anime Head & Face
        skin_grad = QLinearGradient(cx, cy - 30 * s, cx, cy + 12 * s)
        skin_grad.setColorAt(0.0, QColor("#FFF4EE"))
        skin_grad.setColorAt(1.0, QColor("#FFE4D6"))
        p.setBrush(skin_grad)
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(QPointF(cx, cy - 6 * s), 23 * s, 20 * s)

        # 5. Big Jewel-like Anime Eyes
        eye_y = cy - 6 * s
        if state in (PetState.DONE, PetState.CLICKED):
            # Happy closed crescent curve eyes
            p.setPen(QPen(QColor("#2D3436"), 2.8 * s, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawArc(QRectF(cx - 17 * s, eye_y - 6 * s, 12 * s, 10 * s), 0, 180 * 16)
            p.drawArc(QRectF(cx + 5 * s, eye_y - 6 * s, 12 * s, 10 * s), 0, 180 * 16)
            # Happy smiling small open mouth
            p.setBrush(QColor("#FF6B81"))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawChord(QRectF(cx - 4 * s, eye_y + 6 * s, 8 * s, 6 * s), 180 * 16, 180 * 16)

        elif state == PetState.ERROR:
            # Teary anime eyes
            p.setPen(QPen(QColor("#2D3436"), 2.5 * s))
            p.drawLine(QPointF(cx - 15 * s, eye_y - 3 * s), QPointF(cx - 6 * s, eye_y + 3 * s))
            p.drawLine(QPointF(cx - 6 * s, eye_y - 3 * s), QPointF(cx - 15 * s, eye_y + 3 * s))
            p.drawLine(QPointF(cx + 6 * s, eye_y - 3 * s), QPointF(cx + 15 * s, eye_y + 3 * s))
            p.drawLine(QPointF(cx + 15 * s, eye_y - 3 * s), QPointF(cx + 6 * s, eye_y + 3 * s))
            # Tears streaming
            p.setBrush(QColor("#54A0FF"))
            p.drawEllipse(QPointF(cx - 14 * s, eye_y + 7 * s), 3 * s, 4 * s)
            p.drawEllipse(QPointF(cx + 14 * s, eye_y + 7 * s), 3 * s, 4 * s)

        elif state == PetState.SLEEP or (state == PetState.IDLE and frame_idx == 2):
            # Cute closed curved sleeping lines
            p.setPen(QPen(QColor("#2D3436"), 2.2 * s, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawArc(QRectF(cx - 16 * s, eye_y - 2 * s, 10 * s, 6 * s), 0, 180 * 16)
            p.drawArc(QRectF(cx + 6 * s, eye_y - 2 * s, 10 * s, 6 * s), 0, 180 * 16)

        else:
            # Gorgeous Jewel Anime Eyes (Violet/Rose Gradient)
            eye_grad = QLinearGradient(cx, eye_y - 8 * s, cx, eye_y + 8 * s)
            eye_grad.setColorAt(0.0, QColor("#6C5CE7"))
            eye_grad.setColorAt(0.6, QColor("#A29BFE"))
            eye_grad.setColorAt(1.0, QColor("#FD79A8"))

            p.setBrush(eye_grad)
            p.setPen(QPen(QColor("#2D3436"), 1.8 * s)) # Upper lash line
            p.drawEllipse(QPointF(cx - 11 * s, eye_y), 5.5 * s, 7.5 * s)
            p.drawEllipse(QPointF(cx + 11 * s, eye_y), 5.5 * s, 7.5 * s)

            # Eyelash flickers
            p.setPen(QPen(QColor("#2D3436"), 2 * s))
            p.drawLine(QPointF(cx - 16 * s, eye_y - 5 * s), QPointF(cx - 18 * s, eye_y - 7 * s))
            p.drawLine(QPointF(cx + 16 * s, eye_y - 5 * s), QPointF(cx + 18 * s, eye_y - 7 * s))

            # Sparkle Highlights (Large white circle + small star sparkle)
            p.setBrush(QColor("#FFFFFF"))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(QPointF(cx - 12 * s, eye_y - 3 * s), 2.6 * s, 3.2 * s)
            p.drawEllipse(QPointF(cx + 10 * s, eye_y - 3 * s), 2.6 * s, 3.2 * s)
            p.drawEllipse(QPointF(cx - 9 * s, eye_y + 3 * s), 1.5 * s, 1.5 * s)
            p.drawEllipse(QPointF(cx + 13 * s, eye_y + 3 * s), 1.5 * s, 1.5 * s)

            # Tiny cute mouth
            p.setPen(QPen(QColor("#FF7675"), 1.5 * s))
            p.drawArc(QRectF(cx - 2.5 * s, eye_y + 5 * s, 5 * s, 3 * s), 180 * 16, 180 * 16)

        # 6. Rosy Anime Blush Cheeks
        p.setBrush(QColor(255, 118, 117, 140))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(QPointF(cx - 15 * s, eye_y + 4 * s), 4.5 * s, 2.5 * s)
        p.drawEllipse(QPointF(cx + 15 * s, eye_y + 4 * s), 4.5 * s, 2.5 * s)

        # 7. Front Anime Bangs (前刘海 + 呆毛)
        bangs_path = QPainterPath()
        bangs_path.moveTo(cx - 24 * s, cy - 14 * s)
        bangs_path.quadTo(cx - 16 * s, cy - 8 * s, cx - 12 * s, cy - 2 * s)
        bangs_path.quadTo(cx - 8 * s, cy - 10 * s, cx - 4 * s, cy - 3 * s)
        bangs_path.quadTo(cx, cy - 12 * s, cx + 4 * s, cy - 3 * s)
        bangs_path.quadTo(cx + 8 * s, cy - 10 * s, cx + 12 * s, cy - 2 * s)
        bangs_path.quadTo(cx + 16 * s, cy - 8 * s, cx + 24 * s, cy - 14 * s)
        bangs_path.cubicTo(cx + 20 * s, cy - 32 * s, cx - 20 * s, cy - 32 * s, cx - 24 * s, cy - 14 * s)

        p.setBrush(hair_color)
        p.setPen(QPen(hair_dark, 1.5 * s))
        p.drawPath(bangs_path)

        # Anime Hair Shine Band (天使之环高光)
        p.setPen(QPen(QColor(255, 255, 255, 160), 2.2 * s, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        p.drawLine(QPointF(cx - 14 * s, cy - 18 * s), QPointF(cx + 14 * s, cy - 18 * s))

        # Cute Ahoge (呆毛 - bouncy)
        ahoge_shift = [2, 0, -2, 1][frame_idx % 4] * s
        ahoge = QPainterPath()
        ahoge.moveTo(cx, cy - 26 * s)
        ahoge.cubicTo(cx + 8 * s + ahoge_shift, cy - 38 * s, cx - 6 * s + ahoge_shift, cy - 44 * s, cx + 4 * s + ahoge_shift, cy - 48 * s)
        p.setPen(QPen(hair_dark, 2 * s, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawPath(ahoge)

        # 8. State-specific props & animations
        # A. Working: Pink Cute Laptop + Fast Typing Paws + Sakura Code Petals
        if state == PetState.WORKING:
            # Cute Cyber Pink Laptop
            p.setBrush(QColor("#FF758F"))
            p.setPen(QPen(QColor("#C0392B"), 1.2 * s))
            p.drawRoundedRect(QRectF(cx + 10 * s, cy + 10 * s, 5 * s, 22 * s), 2 * s, 2 * s)
            # Glowing screen
            p.setBrush(QColor("#00F0FF"))
            p.drawRect(QRectF(cx + 13 * s, cy + 12 * s, 2 * s, 18 * s))
            # Laptop base
            p.setBrush(QColor("#E2E8F0"))
            p.drawRoundedRect(QRectF(cx + 4 * s, cy + 28 * s, 24 * s, 5 * s), 2 * s, 2 * s)

            # Tiny hands typing
            p.setBrush(QColor("#FFEAA7"))
            h_alt = (frame_idx % 2) * 3 * s
            p.drawEllipse(QPointF(cx + 6 * s, cy + 24 * s - h_alt), 4 * s, 4 * s)
            p.drawEllipse(QPointF(cx + 14 * s, cy + 24 * s + h_alt), 4 * s, 4 * s)

            # Floating Sakura Petals & Code Symbols
            p.setFont(QFont("Segoe UI Emoji", int(11 * s)))
            p.setPen(QColor("#FF758F"))
            petals = [
                ("🌸", cx + 22 * s, cy - 8 * s),
                ("</>", cx + 28 * s, cy - 18 * s),
                ("✨", cx + 18 * s, cy - 24 * s),
                ("{ }", cx + 30 * s, cy - 10 * s)
            ]
            tag, tx, ty = petals[frame_idx % 4]
            p.drawText(QPointF(tx, ty), tag)

        # B. Done: Double Peace Signs (✌️ ✌️) & Celebration Sakura Shower
        elif state == PetState.DONE:
            # Peace sign hands up!
            p.setFont(QFont("Segoe UI Emoji", int(14 * s)))
            p.drawText(QPointF(cx - 28 * s, cy + 6 * s), "✌️")
            p.drawText(QPointF(cx + 18 * s, cy + 6 * s), "✌️")
            # Celebration sparkles & flowers
            p.drawText(QPointF(cx - 28 * s, cy - 26 * s), "🌸")
            p.drawText(QPointF(cx + 22 * s, cy - 28 * s), "✨")
            p.drawText(QPointF(cx, cy - 46 * s), "🎉")

        # C. Thinking: Hand on chin & cute thinking bubble
        elif state == PetState.THINKING:
            p.setBrush(QColor("#FFEAA7"))
            p.drawEllipse(QPointF(cx + 6 * s, cy + 2 * s), 4 * s, 4 * s)
            # Question mark
            p.setFont(QFont("Segoe UI", int(14 * s), QFont.Weight.Bold))
            p.setPen(QColor("#FF7675"))
            p.drawText(QPointF(cx + 20 * s, cy - 26 * s), "❓")

        # D. Error: Rainy cloud
        elif state == PetState.ERROR:
            p.setFont(QFont("Segoe UI Emoji", int(16 * s)))
            p.drawText(QPointF(cx - 10 * s, cy - 42 * s), "🌧️")

        # E. Clicked: Heart explosions
        elif state == PetState.CLICKED:
            p.setFont(QFont("Segoe UI Emoji", int(14 * s)))
            p.setPen(QColor("#E84393"))
            p.drawText(QPointF(cx + 18 * s, cy - 22 * s - (frame_idx * 4 * s)), "💖")
            p.drawText(QPointF(cx - 26 * s, cy - 18 * s - (frame_idx * 4 * s)), "💕")

        # F. Sleep: Cat plushie & Zzz
        elif state == PetState.SLEEP:
            # Little cat plushie in arms
            p.setBrush(QColor("#FFFFFF"))
            p.setPen(QPen(QColor("#CBD5E1"), 1.2 * s))
            p.drawEllipse(QPointF(cx, cy + 18 * s), 10 * s, 8 * s)
            p.setBrush(QColor("#FF7675"))
            p.drawEllipse(QPointF(cx, cy + 18 * s), 2 * s, 1.5 * s) # Nose
            # Floating Zzz
            p.setFont(QFont("Segoe UI", int(13 * s), QFont.Weight.Bold))
            p.setPen(QColor("#FD79A8"))
            zy = cy - 14 * s - (frame_idx * 4 * s)
            p.drawText(QPointF(cx + 18 * s, zy), "Z")
            p.drawText(QPointF(cx + 26 * s, zy - 8 * s), "z")

        p.end()
        return pm
