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
        self.setMinimumSize(500, 650)
        
        # Main root layout to center the login card
        root_widget = QWidget()
        root_layout = QVBoxLayout(root_widget)
        root_layout.setContentsMargins(0, 0, 0, 0)
        
        # Center horizontally and vertically
        h_layout = QHBoxLayout()
        h_layout.addStretch()
        
        self.card = QWidget()
        self.card.setObjectName("loginCard")
        self.card.setFixedSize(380, 480)
        
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(28, 36, 28, 36)
        card_layout.setSpacing(16)
        
        # Header title
        self.lbl_title = QLabel("ورود به سیستم")
        self.lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_title.setObjectName("loginTitle")
        
        # Username input
        self.txt_username = QLineEdit()
        self.txt_username.setPlaceholderText("نام کاربری *")
        
        # Password input
        self.txt_password = QLineEdit()
        self.txt_password.setPlaceholderText("رمز عبور *")
        self.txt_password.setEchoMode(QLineEdit.EchoMode.Password)
        
        # Checkboxes Layout
        chk_layout = QVBoxLayout()
        chk_layout.setSpacing(8)
        self.chk_show_pass = QCheckBox("نمایش رمز عبور")
        self.chk_show_pass.stateChanged.connect(self.toggle_password_visibility)
        self.chk_remember = QCheckBox("مرا به خاطر بسپار")
        chk_layout.addWidget(self.chk_show_pass)
        chk_layout.addWidget(self.chk_remember)
        
        # Error Label for inline validation messages
        self.lbl_error = QLabel("")
        self.lbl_error.setObjectName("loginErrorLabel")
        self.lbl_error.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.lbl_error.setWordWrap(True)
        self.lbl_error.setStyleSheet("color: #ef4444; font-size: 12px; font-weight: bold;")
        
        # Login Button
        self.btn_login = QPushButton("ورود به پنل")
        self.btn_login.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_login.clicked.connect(self.handle_login)
        self.btn_login.setFixedHeight(40)
        
        card_layout.addWidget(self.lbl_title)
        card_layout.addSpacing(12)
        card_layout.addWidget(self.txt_username)
        card_layout.addWidget(self.txt_password)
        card_layout.addLayout(chk_layout)
        card_layout.addWidget(self.lbl_error)
        card_layout.addWidget(self.btn_login)
        card_layout.addStretch()
        
        h_layout.addWidget(self.card)
        h_layout.addStretch()
        
        root_layout.addStretch()
        root_layout.addLayout(h_layout)
        root_layout.addStretch()
        
        self.setCentralWidget(root_widget)
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
        user = self.txt_username.text().strip()
        pwd = self.txt_password.text().strip()
        remember = self.chk_remember.isChecked()
        
        # Simple client side validation
        if not user or not pwd:
            self.lbl_error.setText("لطفاً نام کاربری و رمز عبور را وارد کنید.")
            return
            
        self.lbl_error.setText("")
        self.btn_login.setEnabled(False)
        loading = create_loading_dialog(self, "در حال احراز هویت...")
        loading.show()
        
        try:
            req = LoginRequest(username=user, password=pwd)
            res = AuthService.login(req)
            
            self.nav_manager.session.set_session(res.token, user, remember)
            loading.close()
            self.nav_manager.show_main_window()
        except Exception as e:
            loading.close()
            self.lbl_error.setText(str(e))
        finally:
            self.btn_login.setEnabled(True)
