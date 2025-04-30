#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
فرم ورود کاربر به سیستم مدیریت املاک
"""

import sys
import os
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
                           QLabel, QLineEdit, QPushButton, QMessageBox, 
                           QCheckBox)
from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtGui import QFont

# واردات رابط میانی برای ارتباط با هسته سیستم
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from bridge import user_bridge


class LoginForm(QDialog):
    """فرم ورود کاربر به سیستم"""
    
    def __init__(self, parent=None):
        super(LoginForm, self).__init__(parent)
        self.setWindowTitle("ورود به سیستم")
        self.setMinimumWidth(400)
        self.setMaximumHeight(300)
        self.setLayoutDirection(Qt.RightToLeft)  # راست به چپ برای زبان فارسی
        
        # مقداردهی اولیه متغیرها
        self.username = ""
        self.user_data = None
        self.settings = QSettings("PropertyManagement", "Login")
        
        # تعریف فونت فارسی
        self.farsi_font = QFont()
        self.farsi_font.setFamily("Tahoma")
        self.farsi_font.setPointSize(10)
        self.setFont(self.farsi_font)
        
        # راه‌اندازی رابط کاربری
        self.init_ui()
        
        # بارگذاری نام کاربری ذخیره شده (در صورت وجود)
        self.load_saved_username()
    
    def init_ui(self):
        """راه‌اندازی رابط کاربری فرم ورود"""
        layout = QVBoxLayout()
        
        # عنوان فرم
        title_label = QLabel("ورود به سیستم مدیریت املاک")
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setFamily("Tahoma")
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        
        layout.addWidget(title_label)
        layout.addSpacing(20)
        
        # فرم ورود
        form_layout = QFormLayout()
        
        # نام کاربری
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("نام کاربری خود را وارد کنید")
        self.username_edit.setMinimumHeight(30)
        form_layout.addRow("نام کاربری:", self.username_edit)
        
        # رمز عبور
        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("رمز عبور خود را وارد کنید")
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setMinimumHeight(30)
        form_layout.addRow("رمز عبور:", self.password_edit)
        
        layout.addLayout(form_layout)
        
        # گزینه به خاطر سپردن نام کاربری
        self.remember_checkbox = QCheckBox("نام کاربری من را به خاطر بسپار")
        layout.addWidget(self.remember_checkbox)
        
        layout.addSpacing(10)
        
        # دکمه‌های ورود و انصراف
        buttons_layout = QHBoxLayout()
        
        self.login_button = QPushButton("ورود")
        self.login_button.setMinimumHeight(40)
        self.login_button.clicked.connect(self.login)
        
        self.register_button = QPushButton("ثبت‌نام")
        self.register_button.setMinimumHeight(40)
        self.register_button.clicked.connect(self.register)
        
        self.cancel_button = QPushButton("انصراف")
        self.cancel_button.setMinimumHeight(40)
        self.cancel_button.clicked.connect(self.reject)
        
        buttons_layout.addWidget(self.login_button)
        buttons_layout.addWidget(self.register_button)
        buttons_layout.addWidget(self.cancel_button)
        
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
    
    def load_saved_username(self):
        """بارگذاری نام کاربری ذخیره شده"""
        saved_username = self.settings.value("username", "")
        if saved_username:
            self.username_edit.setText(saved_username)
            self.remember_checkbox.setChecked(True)
    
    def save_username(self):
        """ذخیره‌سازی نام کاربری"""
        if self.remember_checkbox.isChecked():
            self.settings.setValue("username", self.username_edit.text())
        else:
            self.settings.remove("username")
    
    def login(self):
        """اعتبارسنجی و ورود کاربر"""
        username = self.username_edit.text().strip()
        password = self.password_edit.text()
        
        if not username:
            QMessageBox.warning(self, "خطا", "لطفاً نام کاربری خود را وارد کنید")
            self.username_edit.setFocus()
            return
        
        if not password:
            QMessageBox.warning(self, "خطا", "لطفاً رمز عبور خود را وارد کنید")
            self.password_edit.setFocus()
            return
        
        # اعتبارسنجی کاربر با استفاده از رابط میانی
        try:
            user_data = user_bridge.authenticate_user(username, password)
            if user_data:
                self.username = username
                self.user_data = user_data
                self.save_username()
                QMessageBox.information(self, "موفقیت", f"خوش آمدید، {username}!")
                self.accept()
            else:
                QMessageBox.critical(self, "خطا", "نام کاربری یا رمز عبور اشتباه است")
                self.password_edit.clear()
                self.password_edit.setFocus()
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در ورود به سیستم: {str(e)}")
    
    def register(self):
        """نمایش صفحه ثبت‌نام کاربر جدید"""
        from register_form import RegisterForm
        register_form = RegisterForm(self)
        if register_form.exec_() == RegisterForm.Accepted:
            # اطلاعات کاربر جدید را در فرم ورود قرار می‌دهیم
            self.username_edit.setText(register_form.get_username())
            QMessageBox.information(self, "ثبت‌نام موفق", 
                                   "ثبت‌نام با موفقیت انجام شد. اکنون می‌توانید وارد شوید.")
            self.password_edit.setFocus()
    
    def get_username(self):
        """دریافت نام کاربری"""
        return self.username
    
    def get_user_data(self):
        """دریافت اطلاعات کاربر"""
        return self.user_data

if __name__ == "__main__":
    # تست فرم به صورت مستقل
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    app.setLayoutDirection(Qt.RightToLeft)
    
    login = LoginForm()
    login.show()
    
    sys.exit(app.exec_()) 