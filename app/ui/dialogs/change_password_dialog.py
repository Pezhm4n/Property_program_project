from PySide6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QLabel, QMessageBox, QWidget
from PySide6.QtCore import Qt
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'bridge')))
from re_bridge.services import AuthService

class ChangePasswordDialog(QDialog):
    def __init__(self, username, parent=None):
        super().__init__(parent)
        self.username = username
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setWindowTitle("تغییر رمز عبور")
        self.resize(360, 240)
        self.setModal(True)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        lbl_info = QLabel("لطفاً رمز عبور فعلی و رمز عبور جدید خود را وارد نمایید:")
        lbl_info.setWordWrap(True)
        lbl_info.setStyleSheet("font-weight: bold; color: #38bdf8;")
        layout.addWidget(lbl_info)
        
        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        
        self.txt_current = QLineEdit()
        self.txt_current.setEchoMode(QLineEdit.EchoMode.Password)
        
        self.txt_new = QLineEdit()
        self.txt_new.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_new.setPlaceholderText("حداقل ۶ کاراکتر")
        
        self.txt_confirm = QLineEdit()
        self.txt_confirm.setEchoMode(QLineEdit.EchoMode.Password)
        
        form.addRow("رمز عبور فعلی:", self.txt_current)
        form.addRow("رمز عبور جدید:", self.txt_new)
        form.addRow("تایید رمز جدید:", self.txt_confirm)
        
        layout.addLayout(form)
        
        # Action Buttons
        self.btn_submit = QPushButton("تغییر رمز عبور")
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
        """)
        self.btn_submit.clicked.connect(self.submit_change)
        layout.addWidget(self.btn_submit)
        
        # Enter key triggers submit
        self.txt_current.returnPressed.connect(self.submit_change)
        self.txt_new.returnPressed.connect(self.submit_change)
        self.txt_confirm.returnPressed.connect(self.submit_change)
        
        # Tab Order
        QWidget.setTabOrder(self.txt_current, self.txt_new)
        QWidget.setTabOrder(self.txt_new, self.txt_confirm)
        QWidget.setTabOrder(self.txt_confirm, self.btn_submit)
        
        # Initial focus
        self.txt_current.setFocus()
        
    def submit_change(self):
        current_pw = self.txt_current.text()
        new_pw = self.txt_new.text()
        confirm = self.txt_confirm.text()
        
        default_style = ""
        error_style = "border: 1.5px solid #ef4444; background-color: #fef2f2;"
        
        self.txt_current.setStyleSheet(default_style)
        self.txt_new.setStyleSheet(default_style)
        self.txt_confirm.setStyleSheet(default_style)
        
        if not current_pw or not new_pw or not confirm:
            if not current_pw: self.txt_current.setStyleSheet(error_style)
            if not new_pw: self.txt_new.setStyleSheet(error_style)
            if not confirm: self.txt_confirm.setStyleSheet(error_style)
            QMessageBox.warning(self, "خطا", "تکمیل تمام فیلدها الزامی است.")
            return
        if len(new_pw) < 6:
            self.txt_new.setStyleSheet(error_style)
            QMessageBox.warning(self, "خطا", "رمز عبور جدید باید حداقل ۶ کاراکتر باشد.")
            return
        if new_pw != confirm:
            self.txt_new.setStyleSheet(error_style)
            self.txt_confirm.setStyleSheet(error_style)
            QMessageBox.warning(self, "خطا", "رمز عبور جدید و تکرار آن همخوانی ندارند.")
            return
            
        try:
            success = AuthService.change_password(self.username, current_pw, new_pw)
            if success:
                QMessageBox.information(self, "موفقیت", "رمز عبور با موفقیت تغییر یافت.")
                self.accept()
            else:
                self.txt_current.setStyleSheet(error_style)
                QMessageBox.critical(self, "خطا", "تغییر رمز عبور با خطا مواجه شد.")
        except Exception as e:
            error_str = str(e)
            self.txt_current.setStyleSheet(error_style)
            if "Authentication failed" in error_str or "RE_ERR_AUTH" in error_str:
                QMessageBox.critical(self, "خطا", "رمز عبور فعلی وارد شده نادرست است.")
            else:
                QMessageBox.critical(self, "خطا", f"خطا در تغییر رمز: {error_str}")
