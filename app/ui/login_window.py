from PySide6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QHBoxLayout, QCheckBox
from PySide6.QtCore import Qt
from ui.base_window import BaseWindow
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'bridge')))
from re_bridge.exceptions import REException
from re_bridge.services import AuthService
from re_bridge.models import LoginRequest
from ui.dialogs import show_error_dialog, create_loading_dialog

class LoginWindow(BaseWindow):
    def __init__(self, nav_manager):
        super().__init__(nav_manager)
        self.setWindowTitle("ورود به سیستم مدیریت املاک")
        self.setMinimumSize(480, 620)
        
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
        
        self.chk_show_pass = QCheckBox("نمایش رمز عبور")
        self.chk_show_pass.stateChanged.connect(self.toggle_password_visibility)
        
        self.chk_remember = QCheckBox("مرا به خاطر بسپار")
        
        self.btn_login = QPushButton("ورود")
        self.btn_login.clicked.connect(self.handle_login)
        
        layout.addStretch()
        layout.addWidget(self.lbl_title)
        layout.addWidget(self.txt_username)
        layout.addWidget(self.txt_password)
        layout.addWidget(self.chk_show_pass)
        layout.addWidget(self.chk_remember)
        layout.addWidget(self.btn_login)
        layout.addStretch()
        
        self.setCentralWidget(container)
        self._load_saved_credentials()

    def toggle_password_visibility(self, state):
        if self.chk_show_pass.isChecked():
            self.txt_password.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.txt_password.setEchoMode(QLineEdit.EchoMode.Password)

    def _load_saved_credentials(self):
        saved_user = self.nav_manager.session.username
        if saved_user:
            self.txt_username.setText(saved_user)
            self.chk_remember.setChecked(True)

    def handle_login(self):
        user = self.txt_username.text()
        pwd = self.txt_password.text()
        remember = self.chk_remember.isChecked()
        
        self.btn_login.setEnabled(False)
        loading = create_loading_dialog(self, "در حال احراز هویت...")
        loading.show()
        
        try:
            # Delegate entirely to bridge
            req = LoginRequest(username=user, password=pwd)
            res = AuthService.login(req)
            
            self.nav_manager.session.set_session(res.token, user, remember)
            loading.close()
            self.nav_manager.show_main_window()
        except Exception as e:
            loading.close()
            show_error_dialog(self, e)
        finally:
            self.btn_login.setEnabled(True)
