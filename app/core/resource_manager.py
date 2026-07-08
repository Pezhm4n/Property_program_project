import sys
import os
from PySide6.QtGui import QIcon

class ResourceManager:
    @staticmethod
    def resolve_path(relative_path: str) -> str:
        if getattr(sys, 'frozen', False):
            # Running inside PyInstaller package (sys._MEIPASS)
            base_path = sys._MEIPASS
        else:
            # Running in standard Python development mode
            # Root is three levels up from app/core/resource_manager.py
            current_dir = os.path.dirname(os.path.abspath(__file__))
            base_path = os.path.dirname(os.path.dirname(current_dir))
            
        return os.path.abspath(os.path.join(base_path, relative_path))

    @staticmethod
    def get_app_icon():
        icon_path = ResourceManager.resolve_path(os.path.join("assets", "icon.png"))
        if os.path.exists(icon_path):
            return QIcon(icon_path)
        # Fallback to empty icon
        return QIcon()
        
    @staticmethod
    def get_icon(name: str):
        return QIcon()
