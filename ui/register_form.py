#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
فرم ثبت‌نام کاربر جدید در سیستم مدیریت املاک
"""

import sys
import os
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
                           QLabel, QLineEdit, QPushButton, QMessageBox, 
                           QComboBox, QDateEdit)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont, QRegExpValidator
from PyQt5.QtCore import QRegExp

# واردات رابط میانی برای ارتباط با هسته سیستم
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from bridge import user_bridge


class RegisterForm(QDialog):
    """فرم ثبت‌نام کاربر جدید"""
    
    def __init__(self, parent=None):
        super(RegisterForm, self).__init__(parent)
        self.setWindowTitle("ثبت‌نام کاربر جدید")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        self.setLayoutDirection(Qt.RightToLeft)  # راست به چپ برای زبان فارسی
        
        # مقداردهی اولیه متغیرها
        self.username = ""
        
        # تعریف فونت فارسی
        self.farsi_font = QFont()
        self.farsi_font.setFamily("Tahoma")
        self.farsi_font.setPointSize(10)
        self.setFont(self.farsi_font)
        
        # راه‌اندازی رابط کاربری
        self.init_ui()
    
    def init_ui(self):
        """راه‌اندازی رابط کاربری فرم ثبت‌نام"""
        layout = QVBoxLayout()
        
        # عنوان فرم
        title_label = QLabel("ثبت‌نام کاربر جدید")
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setFamily("Tahoma")
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        
        layout.addWidget(title_label)
        layout.addSpacing(20)
        
        # فرم ثبت‌نام
        form_layout = QFormLayout()
        
        # نام کاربری
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("حداقل ۴ حرف (فقط حروف انگلیسی و اعداد)")
        self.username_edit.setMinimumHeight(30)
        username_regex = QRegExp("^[a-zA-Z0-9_]{4,20}$")
        username_validator = QRegExpValidator(username_regex)
        self.username_edit.setValidator(username_validator)
        form_layout.addRow("* نام کاربری:", self.username_edit)
        
        # رمز عبور
        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("حداقل ۶ کاراکتر")
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setMinimumHeight(30)
        form_layout.addRow("* رمز عبور:", self.password_edit)
        
        # تکرار رمز عبور
        self.confirm_password_edit = QLineEdit()
        self.confirm_password_edit.setPlaceholderText("تکرار رمز عبور")
        self.confirm_password_edit.setEchoMode(QLineEdit.Password)
        self.confirm_password_edit.setMinimumHeight(30)
        form_layout.addRow("* تکرار رمز عبور:", self.confirm_password_edit)
        
        # نام و نام خانوادگی
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("نام و نام خانوادگی خود را وارد کنید")
        self.name_edit.setMinimumHeight(30)
        form_layout.addRow("* نام و نام خانوادگی:", self.name_edit)
        
        # شماره تلفن
        self.phone_edit = QLineEdit()
        self.phone_edit.setPlaceholderText("مثال: ۰۹۱۲۳۴۵۶۷۸۹")
        self.phone_edit.setMinimumHeight(30)
        phone_regex = QRegExp("^09[0-9]{9}$")
        phone_validator = QRegExpValidator(phone_regex)
        self.phone_edit.setValidator(phone_validator)
        form_layout.addRow("* شماره تلفن همراه:", self.phone_edit)
        
        # ایمیل
        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText("مثال: example@mail.com")
        self.email_edit.setMinimumHeight(30)
        email_regex = QRegExp("[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}")
        email_validator = QRegExpValidator(email_regex)
        self.email_edit.setValidator(email_validator)
        form_layout.addRow("ایمیل:", self.email_edit)
        
        # تاریخ تولد
        self.birthdate_edit = QDateEdit()
        self.birthdate_edit.setCalendarPopup(True)
        self.birthdate_edit.setDisplayFormat("yyyy/MM/dd")
        default_date = QDate.currentDate().addYears(-18)
        self.birthdate_edit.setDate(default_date)
        self.birthdate_edit.setMinimumHeight(30)
        form_layout.addRow("تاریخ تولد:", self.birthdate_edit)
        
        # نوع کاربر
        self.user_type_combo = QComboBox()
        self.user_type_combo.addItems(["مشتری", "مشاور املاک", "مدیر"])
        self.user_type_combo.setMinimumHeight(30)
        form_layout.addRow("* نوع کاربر:", self.user_type_combo)
        
        # آدرس
        self.address_edit = QLineEdit()
        self.address_edit.setPlaceholderText("آدرس محل سکونت")
        self.address_edit.setMinimumHeight(30)
        form_layout.addRow("آدرس:", self.address_edit)
        
        layout.addLayout(form_layout)
        
        # توضیح فیلدهای ضروری
        required_label = QLabel("فیلدهای ستاره‌دار (*) اجباری هستند")
        required_label.setStyleSheet("color: red;")
        layout.addWidget(required_label)
        
        layout.addSpacing(10)
        
        # دکمه‌های ثبت‌نام و انصراف
        buttons_layout = QHBoxLayout()
        
        self.register_button = QPushButton("ثبت‌نام")
        self.register_button.setMinimumHeight(40)
        self.register_button.clicked.connect(self.register_user)
        
        self.cancel_button = QPushButton("انصراف")
        self.cancel_button.setMinimumHeight(40)
        self.cancel_button.clicked.connect(self.reject)
        
        buttons_layout.addWidget(self.register_button)
        buttons_layout.addWidget(self.cancel_button)
        
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
    
    def register_user(self):
        """ثبت اطلاعات کاربر جدید"""
        # بررسی اعتبار فیلدهای اجباری
        username = self.username_edit.text().strip()
        password = self.password_edit.text()
        confirm_password = self.confirm_password_edit.text()
        name = self.name_edit.text().strip()
        phone = self.phone_edit.text().strip()
        email = self.email_edit.text().strip()
        user_type = self.user_type_combo.currentText()
        address = self.address_edit.text().strip()
        birthdate = self.birthdate_edit.date().toString("yyyy-MM-dd")
        
        # بررسی فیلدهای اجباری
        if not username:
            QMessageBox.warning(self, "خطا", "نام کاربری نمی‌تواند خالی باشد")
            self.username_edit.setFocus()
            return
        
        if not password:
            QMessageBox.warning(self, "خطا", "رمز عبور نمی‌تواند خالی باشد")
            self.password_edit.setFocus()
            return
        
        if len(password) < 6:
            QMessageBox.warning(self, "خطا", "رمز عبور باید حداقل ۶ کاراکتر باشد")
            self.password_edit.setFocus()
            return
        
        if password != confirm_password:
            QMessageBox.warning(self, "خطا", "رمز عبور و تکرار آن باید یکسان باشند")
            self.confirm_password_edit.setFocus()
            return
        
        if not name:
            QMessageBox.warning(self, "خطا", "نام و نام خانوادگی نمی‌تواند خالی باشد")
            self.name_edit.setFocus()
            return
        
        if not phone or len(phone) != 11:
            QMessageBox.warning(self, "خطا", "شماره تلفن همراه باید ۱۱ رقم باشد")
            self.phone_edit.setFocus()
            return
        
        # اگر ایمیل وارد شده، بررسی اعتبار آن
        if email and '@' not in email:
            QMessageBox.warning(self, "خطا", "فرمت ایمیل وارد شده نامعتبر است")
            self.email_edit.setFocus()
            return
        
        # ثبت کاربر با استفاده از رابط میانی
        try:
            user_info = {
                "username": username,
                "password": password,
                "name": name,
                "phone": phone,
                "email": email,
                "birthdate": birthdate,
                "user_type": user_type,
                "address": address
            }
            
            result = user_bridge.register_user(user_info)
            
            if result:
                self.username = username
                self.accept()
            else:
                QMessageBox.critical(self, "خطا", "این نام کاربری قبلاً استفاده شده است")
                self.username_edit.setFocus()
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در ثبت کاربر: {str(e)}")
    
    def get_username(self):
        """بازگرداندن نام کاربری ثبت‌شده"""
        return self.username

if __name__ == "__main__":
    # تست فرم به صورت مستقل
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    app.setLayoutDirection(Qt.RightToLeft)
    
    register = RegisterForm()
    register.show()
    
    sys.exit(app.exec_()) 