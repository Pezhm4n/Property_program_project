from PySide6.QtGui import QFontDatabase, QFont
import os

class FontManager:
    @staticmethod
    def setup_fonts():
        # Get absolute path to assets/fonts
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        regular_path = os.path.join(base_dir, 'assets', 'fonts', 'Vazirmatn-Regular.ttf')
        bold_path = os.path.join(base_dir, 'assets', 'fonts', 'Vazirmatn-Bold.ttf')
        
        if os.path.exists(regular_path):
            QFontDatabase.addApplicationFont(regular_path)
        if os.path.exists(bold_path):
            QFontDatabase.addApplicationFont(bold_path)
            
        font = QFont("Vazirmatn", 10)
        return font
