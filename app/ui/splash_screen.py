from PySide6.QtWidgets import QSplashScreen, QLabel
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtCore import Qt

class SplashScreen(QSplashScreen):
    def __init__(self):
        # We can load a real pixmap later from ResourceManager
        super().__init__()
        self.resize(500, 300)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet("background-color: #2b2b2b; color: white; font-size: 20px;")
        self.showMessage("در حال بارگذاری سیستم مدیریت املاک...", Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignBottom, Qt.GlobalColor.white)
