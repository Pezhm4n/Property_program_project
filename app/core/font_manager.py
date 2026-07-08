from PySide6.QtGui import QFontDatabase, QFont
import os

class FontManager:
    @staticmethod
    def setup_fonts():
        from core.resource_manager import ResourceManager
        regular_path = ResourceManager.resolve_path(os.path.join('assets', 'fonts', 'Vazirmatn-Regular.ttf'))
        bold_path = ResourceManager.resolve_path(os.path.join('assets', 'fonts', 'Vazirmatn-Bold.ttf'))
        
        if os.path.exists(regular_path):
            QFontDatabase.addApplicationFont(regular_path)
        if os.path.exists(bold_path):
            QFontDatabase.addApplicationFont(bold_path)
            
        font = QFont("Vazirmatn", 10)
        return font
