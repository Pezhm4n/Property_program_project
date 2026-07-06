from PySide6.QtWidgets import QLabel, QStatusBar, QToolBar, QWidget, QVBoxLayout, QPushButton
from PySide6.QtCore import Qt
from ui.base_window import BaseWindow

class MainWindow(BaseWindow):
    def __init__(self, nav_manager):
        super().__init__(nav_manager)
        self.setWindowTitle("داشبورد مدیریت املاک")
        self.setMinimumSize(1280, 800)
        
        # Central widget
        container = QWidget()
        layout = QVBoxLayout(container)
        
        lbl = QLabel("داشبورد مدیریت املاک (در حال توسعه)")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        btn_logout = QPushButton("خروج از حساب کاربری")
        btn_logout.clicked.connect(self.handle_logout)
        
        layout.addStretch()
        layout.addWidget(lbl)
        layout.addWidget(btn_logout, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch()
        
        self.setCentralWidget(container)
        
        # Status Bar Placeholder
        self.status_bar = QStatusBar()
        self.status_bar.showMessage("آماده به کار...")
        self.setStatusBar(self.status_bar)

    def handle_logout(self):
        # Delegate logout to NavigationManager -> SessionManager
        self.nav_manager.session.clear_session()
        self.nav_manager.show_login()
