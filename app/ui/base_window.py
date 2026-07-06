from PySide6.QtWidgets import QMainWindow
from PySide6.QtCore import Qt

class BaseWindow(QMainWindow):
    def __init__(self, nav_manager=None):
        super().__init__()
        self.nav_manager = nav_manager
        # Global RTL enforcement for all descending windows
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
