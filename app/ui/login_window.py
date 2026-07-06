from PySide6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel
from PySide6.QtCore import Qt
from ui.base_window import BaseWindow
import sys
import os

# Ensure bridge imports are available
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'bridge')))
from re_bridge.exceptions import REException
from ui.dialogs import show_error_dialog

class LoginWindow(BaseWindow):
    def __init__(self, nav_manager):
        super().__init__(nav_manager)
        self.setWindowTitle("ورود به سیستم مدیریت املاک")
        self.resize(400, 300)
        
        container = QWidget()
        layout = QVBoxLayout(container)
        
        self.lbl_title = QLabel("ورود به سیستم")
        self.lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_title.setObjectName("titleLabel")
        
        self.txt_username = QLineEdit()
        self.txt_username.setPlaceholderText("نام کاربری")
        
        self.txt_password = QLineEdit()
        self.txt_password.setPlaceholderText("رمز عبور")
        self.txt_password.setEchoMode(QLineEdit.EchoMode.Password)
        
        self.btn_login = QPushButton("ورود")
        self.btn_login.clicked.connect(self.handle_login)
        
        layout.addStretch()
        layout.addWidget(self.lbl_title)
        layout.addWidget(self.txt_username)
        layout.addWidget(self.txt_password)
        layout.addWidget(self.btn_login)
        layout.addStretch()
        
        self.setCentralWidget(container)

    def handle_login(self):
        try:
            # Simulate bridge exception if empty
            if not self.txt_username.text():
                raise REException("نام کاربری نمی‌تواند خالی باشد", -1, "فیلد ورودی را بررسی کنید.")
                
            self.nav_manager.show_main_window()
        except Exception as e:
            show_error_dialog(self, e)
