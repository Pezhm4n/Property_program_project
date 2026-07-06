import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

# Ensure custom modules are found
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.theme_manager import ThemeManager
from core.font_manager import FontManager
from core.navigation import NavigationManager
from core.resource_manager import ResourceManager

def main():
    # High DPI Scaling Policy
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    
    app = QApplication(sys.argv)
    app.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
    app.setWindowIcon(ResourceManager.get_app_icon())
    
    # Initialize Fonts
    font = FontManager.setup_fonts()
    app.setFont(font)
    
    # Initialize Theme
    theme_manager = ThemeManager()
    theme_manager.apply_theme(app, "dark")
    
    # Initialize Core DLL Database and Migrations
    from re_bridge.services import re_init, re_close
    re_init("real_estate.db", "core/migrations")
    
    # Initialize Navigation and launch
    nav = NavigationManager()
    nav.show_login()
    
    try:
        sys.exit(app.exec())
    finally:
        re_close()

if __name__ == "__main__":
    main()
