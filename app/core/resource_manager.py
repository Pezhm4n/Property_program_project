from PySide6.QtGui import QIcon

class ResourceManager:
    @staticmethod
    def get_app_icon():
        # Fallback to empty icon until Phase 6 graphical assets are added
        return QIcon()
        
    @staticmethod
    def get_icon(name: str):
        # Skeleton for Phase 6 resource loading
        return QIcon()
