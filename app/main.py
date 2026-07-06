import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

# Ensure custom modules are found
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.theme_manager import ThemeManager
from core.font_manager import FontManager
from core.navigation import NavigationManager

def main():
    # High DPI Scaling Policy
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    
    app = QApplication(sys.argv)
    app.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
    
    # Initialize Fonts
    font = FontManager.setup_fonts()
    app.setFont(font)
    
    # Initialize Theme
    theme_manager = ThemeManager()
    theme_manager.apply_theme(app, "dark")
    
    # Initialize Navigation and launch
    nav = NavigationManager()
    nav.show_login()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
