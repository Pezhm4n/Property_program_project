from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt
from ui.base_window import BaseWindow

class MainWindow(BaseWindow):
    def __init__(self, nav_manager):
        super().__init__(nav_manager)
        self.setWindowTitle("داشبورد مدیریت املاک")
        self.resize(800, 600)
        
        lbl = QLabel("به سیستم مدیریت املاک خوش آمدید (Phase 5 Skeleton)")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setCentralWidget(lbl)
