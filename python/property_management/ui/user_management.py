#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ماژول مدیریت کاربران
این ماژول امکانات مدیریت کاربران در سیستم مدیریت املاک را پیاده‌سازی می‌کند.
"""

import os
import sys
import logging
import json
import hashlib
from typing import Dict, Any, Optional, List, Tuple

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QMessageBox, QTableWidget, QTableWidgetItem,
    QComboBox, QCheckBox, QGridLayout, QHeaderView, QAbstractItemView,
    QFrame, QSizePolicy, QSpacerItem, QInputDialog, QToolButton
)
from PyQt5.QtGui import QIcon, QFont, QPalette, QColor
from PyQt5.QtCore import Qt, QSize, QSettings, pyqtSignal

class UserManagementDialog(QDialog):
    """کلاس دیالوگ مدیریت کاربران سیستم مدیریت املاک"""
    
    user_updated = pyqtSignal()  # سیگنال برای اطلاع‌رسانی تغییرات کاربران
    
    def __init__(self, current_username: str, is_admin: bool, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        
        # تنظیم متغیرهای عضو
        self.users_file = os.path.expanduser("~/property_management_users.json")
        self.current_username = current_username
        self.is_admin = is_admin
        self.users = self.load_users()
        
        # تنظیم ویژگی‌های دیالوگ
        self.setup_dialog()
        
        # ایجاد رابط کاربری
        self.create_ui()
        
        # بارگذاری لیست کاربران
        self.load_users_table()
        
        self.logger.info("دیالوگ مدیریت کاربران ایجاد شد")
    
    def setup_dialog(self):
        """تنظیم ویژگی‌های دیالوگ"""
        self.setWindowTitle("مدیریت کاربران")
        self.resize(700, 500)
        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint | Qt.WindowTitleHint)
        self.setModal(True)
    
    def create_ui(self):
        """ایجاد رابط کاربری دیالوگ مدیریت کاربران"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # عنوان صفحه
        title_label = QLabel("مدیریت کاربران سیستم")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # خط جداکننده
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)
        
        # بخش اضافه کردن کاربر جدید (فقط برای مدیران)
        if self.is_admin:
            self.create_add_user_section(layout)
        
        # جدول نمایش کاربران
        self.create_users_table(layout)
        
        # بخش دکمه‌های پایین
        buttons_layout = QHBoxLayout()
        
        # دکمه تغییر کلمه عبور خود کاربر
        change_password_button = QPushButton("تغییر کلمه عبور")
        change_password_button.setIcon(QIcon("icons/password.png"))
        change_password_button.clicked.connect(self.change_own_password)
        buttons_layout.addWidget(change_password_button)
        
        # فضای خالی
        buttons_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        
        # دکمه بستن
        close_button = QPushButton("بستن")
        close_button.clicked.connect(self.accept)
        buttons_layout.addWidget(close_button)
        
        layout.addLayout(buttons_layout)
    
    def create_add_user_section(self, parent_layout):
        """ایجاد بخش اضافه کردن کاربر جدید"""
        group_layout = QGridLayout()
        group_layout.setVerticalSpacing(10)
        group_layout.setHorizontalSpacing(10)
        
        # عنوان بخش
        add_user_label = QLabel("افزودن کاربر جدید")
        add_user_label.setFont(QFont("Arial", 11, QFont.Bold))
        group_layout.addWidget(add_user_label, 0, 0, 1, 4)
        
        # فیلدهای ورودی
        # نام کاربری
        username_label = QLabel("نام کاربری:")
        group_layout.addWidget(username_label, 1, 0)
        
        self.new_username = QLineEdit()
        self.new_username.setPlaceholderText("نام کاربری")
        group_layout.addWidget(self.new_username, 1, 1)
        
        # کلمه عبور
        password_label = QLabel("کلمه عبور:")
        group_layout.addWidget(password_label, 1, 2)
        
        self.new_password = QLineEdit()
        self.new_password.setPlaceholderText("کلمه عبور")
        self.new_password.setEchoMode(QLineEdit.Password)
        group_layout.addWidget(self.new_password, 1, 3)
        
        # نام کامل
        fullname_label = QLabel("نام کامل:")
        group_layout.addWidget(fullname_label, 2, 0)
        
        self.new_fullname = QLineEdit()
        self.new_fullname.setPlaceholderText("نام و نام خانوادگی")
        group_layout.addWidget(self.new_fullname, 2, 1)
        
        # نقش
        role_label = QLabel("نقش:")
        group_layout.addWidget(role_label, 2, 2)
        
        self.new_role = QComboBox()
        self.new_role.addItems(["کاربر عادی", "مدیر"])
        group_layout.addWidget(self.new_role, 2, 3)
        
        # دکمه افزودن
        add_button = QPushButton("افزودن کاربر")
        add_button.setIcon(QIcon("icons/add_user.png"))
        add_button.clicked.connect(self.add_new_user)
        group_layout.addWidget(add_button, 3, 3)
        
        parent_layout.addLayout(group_layout)
        
        # خط جداکننده
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        parent_layout.addWidget(line)
    
    def create_users_table(self, parent_layout):
        """ایجاد جدول نمایش کاربران"""
        # عنوان بخش
        users_label = QLabel("لیست کاربران")
        users_label.setFont(QFont("Arial", 11, QFont.Bold))
        parent_layout.addWidget(users_label)
        
        # جدول کاربران
        self.users_table = QTableWidget()
        self.users_table.setColumnCount(5)
        self.users_table.setHorizontalHeaderLabels([
            "نام کاربری", "نام کامل", "نقش", "تاریخ ایجاد", "عملیات"
        ])
        self.users_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.users_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.users_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.users_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        parent_layout.addWidget(self.users_table)
    
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
    
    def save_users(self):
        """ذخیره لیست کاربران در فایل"""
        try:
            # اطمینان از وجود دایرکتوری
            os.makedirs(os.path.dirname(self.users_file), exist_ok=True)
            
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump(self.users, f, ensure_ascii=False, indent=4)
                
            self.logger.info("اطلاعات کاربران با موفقیت ذخیره شد")
        except Exception as e:
            self.logger.error(f"خطا در ذخیره فایل کاربران: {str(e)}")
    
    def hash_password(self, password: str) -> str:
        """تبدیل کلمه عبور به هش"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def load_users_table(self):
        """بارگذاری اطلاعات کاربران در جدول"""
        self.users_table.setRowCount(0)
        
        row = 0
        for username, user_data in self.users.items():
            self.users_table.insertRow(row)
            
            # نام کاربری
            username_item = QTableWidgetItem(username)
            self.users_table.setItem(row, 0, username_item)
            
            # نام کامل
            fullname = user_data.get('fullname', '')
            fullname_item = QTableWidgetItem(fullname)
            self.users_table.setItem(row, 1, fullname_item)
            
            # نقش
            role = "مدیر" if user_data.get('is_admin', False) else "کاربر عادی"
            role_item = QTableWidgetItem(role)
            self.users_table.setItem(row, 2, role_item)
            
            # تاریخ ایجاد
            created_date = user_data.get('created_date', 'نامشخص')
            date_item = QTableWidgetItem(created_date)
            self.users_table.setItem(row, 3, date_item)
            
            # ستون عملیات
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(0, 0, 0, 0)
            action_layout.setSpacing(2)
            
            # اگر مدیر باشیم یا کاربر خودمان باشد
            if self.is_admin or username == self.current_username:
                # دکمه تغییر کلمه عبور
                change_pwd_btn = self.create_table_button("icons/password.png", "تغییر کلمه عبور")
                change_pwd_btn.clicked.connect(lambda checked, u=username: self.change_user_password(u))
                action_layout.addWidget(change_pwd_btn)
            
            # فقط مدیر بتواند کاربران دیگر را ویرایش یا حذف کند
            if self.is_admin and username != self.current_username:
                # دکمه تغییر نقش
                change_role_btn = self.create_table_button("icons/role.png", "تغییر نقش")
                change_role_btn.clicked.connect(lambda checked, u=username, r=role: self.toggle_user_role(u, r))
                action_layout.addWidget(change_role_btn)
                
                # دکمه حذف کاربر
                delete_btn = self.create_table_button("icons/delete.png", "حذف کاربر")
                delete_btn.clicked.connect(lambda checked, u=username: self.delete_user(u))
                action_layout.addWidget(delete_btn)
            
            action_layout.addStretch()
            self.users_table.setCellWidget(row, 4, action_widget)
            
            row += 1
    
    def create_table_button(self, icon_path, tooltip):
        """ایجاد دکمه برای جدول"""
        button = QToolButton()
        button.setIcon(QIcon(icon_path))
        button.setToolTip(tooltip)
        button.setIconSize(QSize(16, 16))
        button.setMaximumSize(QSize(24, 24))
        return button
    
    def add_new_user(self):
        """افزودن کاربر جدید"""
        username = self.new_username.text().strip()
        password = self.new_password.text()
        fullname = self.new_fullname.text().strip()
        is_admin = self.new_role.currentText() == "مدیر"
        
        # اعتبارسنجی ورودی‌ها
        if not username or not password:
            QMessageBox.warning(
                self, 
                "خطای ورودی", 
                "نام کاربری و کلمه عبور نمی‌توانند خالی باشند."
            )
            return
        
        # بررسی تکراری نبودن نام کاربری
        if username in self.users:
            QMessageBox.warning(
                self, 
                "خطای افزودن کاربر", 
                "این نام کاربری قبلا در سیستم ثبت شده است."
            )
            return
        
        # افزودن کاربر جدید
        from datetime import datetime
        current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        self.users[username] = {
            'password': self.hash_password(password),
            'fullname': fullname,
            'is_admin': is_admin,
            'created_date': current_date,
            'created_by': self.current_username
        }
        
        # ذخیره تغییرات
        self.save_users()
        
        # به‌روزرسانی جدول
        self.load_users_table()
        
        # پاک کردن فیلدها
        self.new_username.clear()
        self.new_password.clear()
        self.new_fullname.clear()
        self.new_role.setCurrentIndex(0)
        
        # نمایش پیام موفقیت
        QMessageBox.information(
            self, 
            "افزودن کاربر", 
            f"کاربر {username} با موفقیت به سیستم اضافه شد."
        )
        
        # ارسال سیگنال تغییر کاربران
        self.user_updated.emit()
    
    def change_user_password(self, username: str):
        """تغییر کلمه عبور کاربر"""
        # پرسش کلمه عبور جدید
        new_password, ok = QInputDialog.getText(
            self,
            "تغییر کلمه عبور",
            f"کلمه عبور جدید برای {username} را وارد کنید:",
            QLineEdit.Password
        )
        
        if not ok or not new_password:
            return
        
        # تغییر کلمه عبور
        if username in self.users:
            self.users[username]['password'] = self.hash_password(new_password)
            self.save_users()
            
            QMessageBox.information(
                self,
                "تغییر کلمه عبور",
                f"کلمه عبور کاربر {username} با موفقیت تغییر کرد."
            )
            
            # ارسال سیگنال تغییر کاربران
            self.user_updated.emit()
    
    def change_own_password(self):
        """تغییر کلمه عبور کاربر جاری"""
        # پرسش کلمه عبور فعلی
        current_password, ok = QInputDialog.getText(
            self,
            "تغییر کلمه عبور",
            "کلمه عبور فعلی خود را وارد کنید:",
            QLineEdit.Password
        )
        
        if not ok or not current_password:
            return
        
        # بررسی صحت کلمه عبور فعلی
        if self.users[self.current_username]['password'] != self.hash_password(current_password):
            QMessageBox.warning(
                self,
                "خطای کلمه عبور",
                "کلمه عبور فعلی صحیح نیست."
            )
            return
        
        # پرسش کلمه عبور جدید
        new_password, ok = QInputDialog.getText(
            self,
            "تغییر کلمه عبور",
            "کلمه عبور جدید را وارد کنید:",
            QLineEdit.Password
        )
        
        if not ok or not new_password:
            return
        
        # تأیید مجدد کلمه عبور جدید
        confirm_password, ok = QInputDialog.getText(
            self,
            "تغییر کلمه عبور",
            "کلمه عبور جدید را مجدداً وارد کنید:",
            QLineEdit.Password
        )
        
        if not ok or new_password != confirm_password:
            QMessageBox.warning(
                self,
                "خطای کلمه عبور",
                "کلمه عبور جدید و تکرار آن مطابقت ندارند."
            )
            return
        
        # تغییر کلمه عبور
        self.users[self.current_username]['password'] = self.hash_password(new_password)
        self.save_users()
        
        QMessageBox.information(
            self,
            "تغییر کلمه عبور",
            "کلمه عبور شما با موفقیت تغییر کرد."
        )
        
        # ارسال سیگنال تغییر کاربران
        self.user_updated.emit()
    
    def toggle_user_role(self, username: str, current_role: str):
        """تغییر نقش کاربر بین مدیر و کاربر عادی"""
        is_admin = current_role != "مدیر"
        new_role = "مدیر" if is_admin else "کاربر عادی"
        
        # تأیید تغییر نقش
        reply = QMessageBox.question(
            self,
            "تغییر نقش کاربر",
            f"آیا از تغییر نقش کاربر {username} به {new_role} اطمینان دارید؟",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        # اعمال تغییر
        self.users[username]['is_admin'] = is_admin
        self.save_users()
        
        # به‌روزرسانی جدول
        self.load_users_table()
        
        # ارسال سیگنال تغییر کاربران
        self.user_updated.emit()
    
    def delete_user(self, username: str):
        """حذف کاربر از سیستم"""
        # تأیید حذف کاربر
        reply = QMessageBox.question(
            self,
            "حذف کاربر",
            f"آیا از حذف کاربر {username} اطمینان دارید؟\nاین عمل غیرقابل بازگشت است.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        # حذف کاربر
        if username in self.users:
            del self.users[username]
            self.save_users()
            
            # به‌روزرسانی جدول
            self.load_users_table()
            
            QMessageBox.information(
                self,
                "حذف کاربر",
                f"کاربر {username} با موفقیت از سیستم حذف شد."
            )
            
            # ارسال سیگنال تغییر کاربران
            self.user_updated.emit() 