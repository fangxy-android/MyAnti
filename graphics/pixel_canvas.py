"""Pixel Art Canvas helper for crisp, scalable retro sprites."""
from PySide6.QtGui import QImage, QPainter, QColor, QPixmap
from PySide6.QtCore import Qt, QRect

class PixelCanvas:
    """A canvas of fixed low-resolution pixel dimensions (e.g. 36x36) that can be drawn on
    using exact pixel coordinates and colors, and rendered to crisp QPixmap at any scale."""
    def __init__(self, width: int = 36, height: int = 36):
        self.w = width
        self.h = height
        self.image = QImage(width, height, QImage.Format.Format_ARGB32_Premultiplied)
        self.image.fill(Qt.GlobalColor.transparent)

    def clear(self):
        self.image.fill(Qt.GlobalColor.transparent)

    def set_pixel(self, x: int, y: int, color: str or QColor):
        if 0 <= x < self.w and 0 <= y < self.h:
            c = QColor(color) if isinstance(color, str) else color
            self.image.setPixelColor(x, y, c)

    def fill_rect(self, x: int, y: int, w: int, h: int, color: str or QColor):
        c = QColor(color) if isinstance(color, str) else color
        painter = QPainter(self.image)
        painter.fillRect(x, y, w, h, c)
        painter.end()

    def draw_pixels(self, color: str or QColor, coords: list):
        c = QColor(color) if isinstance(color, str) else color
        for x, y in coords:
            if 0 <= x < self.w and 0 <= y < self.h:
                self.image.setPixelColor(x, y, c)

    def draw_pattern(self, x_offset: int, y_offset: int, color_map: dict, pattern: list):
        """Draw an ASCII pixel pattern.
        pattern is a list of strings.
        color_map maps characters to hex colors or None for transparent.
        """
        for r, row in enumerate(pattern):
            for c, char in enumerate(row):
                if char in color_map and color_map[char] is not None:
                    self.set_pixel(x_offset + c, y_offset + r, color_map[char])

    def to_pixmap(self, target_size: int = 128) -> QPixmap:
        """Scale to target size using Nearest Neighbor for crisp pixel art."""
        scaled = self.image.scaled(
            target_size,
            target_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.FastTransformation
        )
        return QPixmap.fromImage(scaled)
