#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ماژول دیالوگ ورود به سیستم
این ماژول دیالوگ ورود به سیستم مدیریت املاک را پیاده‌سازی می‌کند.
"""

import os
import sys
import logging
import json
import hashlib
from typing import Dict, Any, Optional, Tuple

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QMessageBox, QCheckBox, QGridLayout, 
    QFrame, QSizePolicy, QSpacerItem
)
from PyQt5.QtGui import QIcon, QPixmap, QFont, QPalette, QColor
from PyQt5.QtCore import Qt, QSize, QSettings

class LoginDialog(QDialog):
    """کلاس دیالوگ ورود به سیستم مدیریت املاک"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        
        # تنظیم متغیرهای عضو
        self.users_file = os.path.expanduser("~/property_management_users.json")
        self.current_user = None
        self.is_admin = False
        
        # تنظیم ویژگی‌های دیالوگ
        self.setup_dialog()
        
        # ایجاد رابط کاربری
        self.create_ui()
        
        # بارگذاری اطلاعات ذخیره شده
        self.load_saved_credentials()
        
        self.logger.info("دیالوگ ورود ایجاد شد")
    
    def setup_dialog(self):
        """تنظیم ویژگی‌های دیالوگ"""
        self.setWindowTitle("ورود به سیستم مدیریت املاک")
        self.setFixedSize(450, 500)
        self.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)
        self.setModal(True)
    
    def create_ui(self):
        """ایجاد رابط کاربری دیالوگ ورود"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # لوگو و عنوان
        header_layout = QVBoxLayout()
        
        # جایگزین کردن با لوگوی واقعی
        logo_label = QLabel()
        logo_pixmap = QPixmap("icons/logo.png")
        if not logo_pixmap.isNull():
            logo_label.setPixmap(logo_pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            # اگر لوگو پیدا نشد یک متن نمایش می‌دهیم
            logo_label.setText("سیستم مدیریت املاک")
            logo_label.setFont(QFont("Arial", 16, QFont.Bold))
        
        logo_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(logo_label)
        
        title_label = QLabel("ورود به سیستم مدیریت املاک")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title_label)
        
        layout.addLayout(header_layout)
        
        # خط جداکننده
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)
        
        # فرم ورود
        form_layout = QGridLayout()
        form_layout.setVerticalSpacing(15)
        form_layout.setHorizontalSpacing(10)
        
        # نام کاربری
        username_label = QLabel("نام کاربری:")
        username_label.setFont(QFont("Arial", 10))
        form_layout.addWidget(username_label, 0, 0)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("نام کاربری خود را وارد کنید")
        self.username_input.setMinimumHeight(35)
        form_layout.addWidget(self.username_input, 0, 1)
        
        # کلمه عبور
        password_label = QLabel("کلمه عبور:")
        password_label.setFont(QFont("Arial", 10))
        form_layout.addWidget(password_label, 1, 0)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("کلمه عبور خود را وارد کنید")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumHeight(35)
        form_layout.addWidget(self.password_input, 1, 1)
        
        # مرا به خاطر بسپار
        self.remember_me = QCheckBox("مرا به خاطر بسپار")
        form_layout.addWidget(self.remember_me, 2, 1)
        
        layout.addLayout(form_layout)
        
        # دکمه‌های اقدام
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        
        self.login_button = QPushButton("ورود")
        self.login_button.setMinimumHeight(40)
        self.login_button.setFont(QFont("Arial", 11, QFont.Bold))
        self.login_button.clicked.connect(self.login)
        buttons_layout.addWidget(self.login_button)
        
        self.create_admin_button = QPushButton("ایجاد حساب مدیر")
        self.create_admin_button.setMinimumHeight(40)
        self.create_admin_button.setFont(QFont("Arial", 11))
        self.create_admin_button.clicked.connect(self.create_admin_account)
        buttons_layout.addWidget(self.create_admin_button)
        
        layout.addLayout(buttons_layout)
        
        # اضافه کردن فضای خالی در انتها
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        # تنظیم فوکوس ابتدایی
        self.username_input.setFocus()
    
    def load_saved_credentials(self):
        """بارگذاری اطلاعات کاربری ذخیره شده"""
        settings = QSettings("PropertyManagement", "Login")
        if settings.contains("username"):
            username = settings.value("username")
            self.username_input.setText(username)
            self.remember_me.setChecked(True)
    
    def save_credentials(self, username: str):
        """ذخیره اطلاعات کاربری"""
        settings = QSettings("PropertyManagement", "Login")
        if self.remember_me.isChecked():
            settings.setValue("username", username)
        else:
            settings.remove("username")
    
    def load_users(self) -> Dict[str, Any]:
        """بارگذاری لیست کاربران از فایل"""
        if not os.path.exists(self.users_file):
            return {}
        
        try:
            with open(self.users_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            self.logger.error(f"خطا در بارگذاری فایل کاربران: {self.users_file}")
            return {}
    
    def save_users(self, users: Dict[str, Any]):
        """ذخیره لیست کاربران در فایل"""
        try:
            # اطمینان از وجود دایرکتوری
            os.makedirs(os.path.dirname(self.users_file), exist_ok=True)
            
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump(users, f, ensure_ascii=False, indent=4)
        except Exception as e:
            self.logger.error(f"خطا در ذخیره فایل کاربران: {str(e)}")
    
    def hash_password(self, password: str) -> str:
        """تبدیل کلمه عبور به هش"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def login(self):
        """تلاش برای ورود به سیستم"""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        if not username or not password:
            QMessageBox.warning(
                self, 
                "خطای ورود", 
                "لطفا نام کاربری و کلمه عبور را وارد کنید."
            )
            return
        
        users = self.load_users()
        
        if username not in users:
            QMessageBox.warning(
                self, 
                "خطای ورود", 
                "نام کاربری یا کلمه عبور اشتباه است."
            )
            return
        
        user_data = users[username]
        hashed_password = self.hash_password(password)
        
        if hashed_password != user_data.get("password"):
            QMessageBox.warning(
                self, 
                "خطای ورود", 
                "نام کاربری یا کلمه عبور اشتباه است."
            )
            return
        
        # ذخیره اطلاعات کاربری در صورت انتخاب گزینه "مرا به خاطر بسپار"
        self.save_credentials(username)
        
        # تنظیم کاربر جاری
        self.current_user = username
        self.is_admin = user_data.get("is_admin", False)
        
        self.logger.info(f"کاربر {username} با موفقیت وارد سیستم شد")
        
        # بستن دیالوگ با وضعیت موفقیت
        self.accept()
    
    def create_admin_account(self):
        """ایجاد حساب کاربری مدیر"""
        users = self.load_users()
        
        # بررسی آیا قبلا حساب مدیر وجود دارد
        admin_exists = any(user.get("is_admin", False) for user in users.values())
        
        if admin_exists:
            QMessageBox.warning(
                self, 
                "خطای ایجاد حساب", 
                "یک حساب مدیر قبلا ایجاد شده است."
            )
            return
        
        # اخذ اطلاعات حساب مدیر
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        if not username or not password:
            QMessageBox.warning(
                self, 
                "خطای ایجاد حساب", 
                "لطفا نام کاربری و کلمه عبور را وارد کنید."
            )
            return
        
        if username in users:
            QMessageBox.warning(
                self, 
                "خطای ایجاد حساب", 
                "این نام کاربری قبلا ثبت شده است."
            )
            return
        
        if len(password) < 6:
            QMessageBox.warning(
                self, 
                "خطای ایجاد حساب", 
                "کلمه عبور باید حداقل ۶ کاراکتر باشد."
            )
            return
        
        # ایجاد حساب مدیر
        users[username] = {
            "username": username,
            "password": self.hash_password(password),
            "is_admin": True,
            "created_at": ""  # اینجا باید تاریخ فعلی به شکل مناسب درج شود
        }
        
        # ذخیره تغییرات
        self.save_users(users)
        
        QMessageBox.information(
            self,
            "ایجاد حساب مدیر",
            f"حساب مدیر با نام کاربری {username} با موفقیت ایجاد شد."
        )
        
        self.logger.info(f"حساب مدیر با نام کاربری {username} ایجاد شد")
    
    def get_user_info(self) -> Tuple[str, bool]:
        """دریافت اطلاعات کاربر وارد شده"""
        return self.current_user, self.is_admin 