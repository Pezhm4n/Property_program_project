from PySide6.QtGui import QFontDatabase, QFont

class FontManager:
    @staticmethod
    def setup_fonts():
        # Fallback system font; Phase 6 will map to embedded resources
        font = QFont("Segoe UI", 10)
        return font
