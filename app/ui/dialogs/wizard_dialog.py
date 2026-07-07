from PySide6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QLabel, QMessageBox
from PySide6.QtCore import Qt
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'bridge')))
from re_bridge.services import AuthService

class WizardDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setWindowTitle("راه‌اندازی اولیه نرم‌افزار")
        self.resize(380, 260)
        self.setModal(True)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        # Welcoming Label
        lbl_welcome = QLabel("خوش آمدید! لطفاً حساب کاربری مدیر سیستم (Admin) را ایجاد کنید:")
        lbl_welcome.setWordWrap(True)
        lbl_welcome.setStyleSheet("font-weight: bold; font-size: 11pt; color: #38bdf8;")
        layout.addWidget(lbl_welcome)
        
        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        
        self.txt_username = QLineEdit()
        self.txt_username.setPlaceholderText("مثال: admin")
        self.txt_username.setText("admin")
        
        self.txt_password = QLineEdit()
        self.txt_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_password.setPlaceholderText("حداقل ۶ کاراکتر")
        
        self.txt_confirm = QLineEdit()
        self.txt_confirm.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_confirm.setPlaceholderText("تکرار رمز عبور")
        
        form.addRow("نام کاربری:", self.txt_username)
        form.addRow("رمز عبور:", self.txt_password)
        form.addRow("تکرار رمز:", self.txt_confirm)
        
        layout.addLayout(form)
        
        # Confirm Button
        self.btn_submit = QPushButton("ایجاد حساب مدیر و ورود")
        self.btn_submit.setStyleSheet("""
            QPushButton {
                background-color: #0284c7;
                color: white;
                font-weight: bold;
                padding: 8px;
                border-radius: 6px;
                border: none;
            }
            QPushButton:hover {
                background-color: #0369a1;
            }
            QPushButton:pressed {
                background-color: #075985;
            }
        """)
        self.btn_submit.clicked.connect(self.submit_wizard)
        layout.addWidget(self.btn_submit)
        
    def submit_wizard(self):
        username = self.txt_username.text().strip()
        password = self.txt_password.text()
        confirm = self.txt_confirm.text()
        
        if not username:
            QMessageBox.warning(self, "خطا", "نام کاربری نمی‌تواند خالی باشد.")
            return
        if not password:
            QMessageBox.warning(self, "خطا", "رمز عبور نمی‌تواند خالی باشد.")
            return
        if len(password) < 6:
            QMessageBox.warning(self, "خطا", "رمز عبور باید حداقل ۶ کاراکتر باشد.")
            return
        if password != confirm:
            QMessageBox.warning(self, "خطا", "رمز عبور و تکرار آن مطابقت ندارند.")
            return
            
        try:
            success = AuthService.create_initial_admin(username, password)
            if success:
                QMessageBox.information(self, "موفقیت", "حساب کاربری مدیر با موفقیت ایجاد شد.")
                self.accept()
            else:
                QMessageBox.critical(self, "خطا", "خطایی در فرآیند ثبت مدیر اولیه رخ داد.")
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطای سیستمی: {str(e)}")
