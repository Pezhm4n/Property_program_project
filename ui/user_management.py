#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
این ماژول برای مدیریت کاربران در سیستم مدیریت املاک استفاده می‌شود.
"""

import os
import sys
import json
import logging
from PyQt5.QtWidgets import (QWidget, QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, 
                           QPushButton, QLabel, QMessageBox, QLineEdit, QComboBox, QFormLayout, QGroupBox)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QIcon

# تنظیمات لاگ
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'ui.log')

logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger('user_management')

class UserManagementDialog(QDialog):
    """کلاس دیالوگ مدیریت کاربران"""
    
    def __init__(self, parent=None, user_service=None):
        super().__init__(parent)
        self.user_service = user_service
        self.setWindowTitle("مدیریت کاربران")
        self.setMinimumSize(800, 500)
        self.setLayoutDirection(Qt.RightToLeft)
        
        self.initUI()
        self.load_users()
        
    def initUI(self):
        """راه‌اندازی رابط کاربری"""
        main_layout = QVBoxLayout()
        
        # بخش جستجو
        search_box = QGroupBox("جستجوی کاربر")
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("نام کاربری یا نام کاربر را وارد کنید...")
        self.search_input.textChanged.connect(self.filter_users)
        
        search_btn = QPushButton("جستجو")
        search_btn.clicked.connect(self.filter_users)
        
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_btn)
        search_box.setLayout(search_layout)
        
        # بخش جدول کاربران
        self.users_table = QTableWidget()
        self.users_table.setColumnCount(6)
        self.users_table.setHorizontalHeaderLabels(["نام کاربری", "نام", "نام خانوادگی", "نقش", "وضعیت", "عملیات"])
        self.users_table.horizontalHeader().setStretchLastSection(True)
        self.users_table.verticalHeader().setVisible(False)
        
        # بخش دکمه‌های اصلی
        buttons_layout = QHBoxLayout()
        
        add_btn = QPushButton("افزودن کاربر جدید")
        add_btn.clicked.connect(self.add_user)
        
        refresh_btn = QPushButton("بازخوانی")
        refresh_btn.clicked.connect(self.load_users)
        
        close_btn = QPushButton("بستن")
        close_btn.clicked.connect(self.close)
        
        buttons_layout.addWidget(add_btn)
        buttons_layout.addWidget(refresh_btn)
        buttons_layout.addStretch()
        buttons_layout.addWidget(close_btn)
        
        # افزودن همه به لایوت اصلی
        main_layout.addWidget(search_box)
        main_layout.addWidget(self.users_table)
        main_layout.addLayout(buttons_layout)
        
        self.setLayout(main_layout)
        
    def load_users(self):
        """بارگذاری لیست کاربران از سرویس"""
        try:
            self.users_table.setRowCount(0)
            
            if self.user_service:
                users = self.user_service.get_all_users()
                
                for row, user in enumerate(users):
                    self.users_table.insertRow(row)
                    
                    # نام کاربری
                    username_item = QTableWidgetItem(user.get('username', ''))
                    username_item.setFlags(username_item.flags() & ~Qt.ItemIsEditable)
                    self.users_table.setItem(row, 0, username_item)
                    
                    # نام
                    first_name_item = QTableWidgetItem(user.get('first_name', ''))
                    self.users_table.setItem(row, 1, first_name_item)
                    
                    # نام خانوادگی
                    last_name_item = QTableWidgetItem(user.get('last_name', ''))
                    self.users_table.setItem(row, 2, last_name_item)
                    
                    # نقش
                    role_item = QTableWidgetItem(user.get('role', ''))
                    self.users_table.setItem(row, 3, role_item)
                    
                    # وضعیت
                    status = "فعال" if user.get('is_active', False) else "غیرفعال"
                    status_item = QTableWidgetItem(status)
                    self.users_table.setItem(row, 4, status_item)
                    
                    # دکمه‌های عملیات
                    actions_widget = QWidget()
                    actions_layout = QHBoxLayout()
                    actions_layout.setContentsMargins(0, 0, 0, 0)
                    
                    edit_btn = QPushButton("ویرایش")
                    edit_btn.setProperty("username", user.get('username', ''))
                    edit_btn.clicked.connect(self.edit_user)
                    
                    delete_btn = QPushButton("حذف")
                    delete_btn.setProperty("username", user.get('username', ''))
                    delete_btn.clicked.connect(self.delete_user)
                    
                    actions_layout.addWidget(edit_btn)
                    actions_layout.addWidget(delete_btn)
                    
                    actions_widget.setLayout(actions_layout)
                    self.users_table.setCellWidget(row, 5, actions_widget)
            
            self.users_table.resizeColumnsToContents()
            logger.info("لیست کاربران با موفقیت بارگذاری شد")
            
        except Exception as e:
            logger.error(f"خطا در بارگذاری لیست کاربران: {str(e)}")
            QMessageBox.critical(self, "خطا", f"خطا در بارگذاری لیست کاربران: {str(e)}")
    
    def filter_users(self):
        """فیلتر کردن کاربران بر اساس متن جستجو"""
        search_text = self.search_input.text().lower()
        
        for row in range(self.users_table.rowCount()):
            username = self.users_table.item(row, 0).text().lower()
            first_name = self.users_table.item(row, 1).text().lower()
            last_name = self.users_table.item(row, 2).text().lower()
            
            if (search_text in username or 
                search_text in first_name or 
                search_text in last_name):
                self.users_table.setRowHidden(row, False)
            else:
                self.users_table.setRowHidden(row, True)
    
    def add_user(self):
        """افزودن کاربر جدید"""
        dialog = UserEditDialog(self, self.user_service)
        if dialog.exec_() == QDialog.Accepted:
            self.load_users()
    
    def edit_user(self):
        """ویرایش کاربر انتخاب شده"""
        sender = self.sender()
        username = sender.property("username")
        
        if username and self.user_service:
            user = self.user_service.get_user_by_username(username)
            if user:
                dialog = UserEditDialog(self, self.user_service, user)
                if dialog.exec_() == QDialog.Accepted:
                    self.load_users()
            else:
                QMessageBox.warning(self, "هشدار", "کاربر مورد نظر یافت نشد.")
    
    def delete_user(self):
        """حذف کاربر انتخاب شده"""
        sender = self.sender()
        username = sender.property("username")
        
        if username and self.user_service:
            reply = QMessageBox.question(self, "تایید حذف", 
                                      f"آیا از حذف کاربر '{username}' اطمینان دارید؟",
                                      QMessageBox.Yes | QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                try:
                    result = self.user_service.delete_user(username)
                    if result.get('success', False):
                        QMessageBox.information(self, "موفقیت", "کاربر با موفقیت حذف شد.")
                        self.load_users()
                    else:
                        QMessageBox.warning(self, "خطا", f"خطا در حذف کاربر: {result.get('error', 'خطای نامشخص')}")
                except Exception as e:
                    logger.error(f"خطا در حذف کاربر {username}: {str(e)}")
                    QMessageBox.critical(self, "خطا", f"خطا در حذف کاربر: {str(e)}")


class UserEditDialog(QDialog):
    """دیالوگ افزودن/ویرایش کاربر"""
    
    def __init__(self, parent=None, user_service=None, user=None):
        super().__init__(parent)
        self.user_service = user_service
        self.user = user  # اگر None باشد، حالت افزودن کاربر جدید است
        
        self.setWindowTitle("افزودن کاربر جدید" if not user else "ویرایش کاربر")
        self.setFixedSize(400, 350)
        self.setLayoutDirection(Qt.RightToLeft)
        
        self.initUI()
        
    def initUI(self):
        """راه‌اندازی رابط کاربری"""
        main_layout = QVBoxLayout()
        
        form_layout = QFormLayout()
        
        # فیلدهای ورودی
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.first_name_input = QLineEdit()
        self.last_name_input = QLineEdit()
        
        self.role_combo = QComboBox()
        self.role_combo.addItems(["admin", "agent", "user"])
        
        self.status_combo = QComboBox()
        self.status_combo.addItems(["فعال", "غیرفعال"])
        
        # اگر در حالت ویرایش هستیم، فیلدها را پر کنیم
        if self.user:
            self.username_input.setText(self.user.get('username', ''))
            self.username_input.setEnabled(False)  # نام کاربری نباید تغییر کند
            self.first_name_input.setText(self.user.get('first_name', ''))
            self.last_name_input.setText(self.user.get('last_name', ''))
            
            role_index = self.role_combo.findText(self.user.get('role', 'user'))
            if role_index >= 0:
                self.role_combo.setCurrentIndex(role_index)
                
            status_index = 0 if self.user.get('is_active', True) else 1
            self.status_combo.setCurrentIndex(status_index)
        
        # افزودن فیلدها به فرم
        form_layout.addRow("نام کاربری:", self.username_input)
        form_layout.addRow("رمز عبور:", self.password_input)
        form_layout.addRow("نام:", self.first_name_input)
        form_layout.addRow("نام خانوادگی:", self.last_name_input)
        form_layout.addRow("نقش:", self.role_combo)
        form_layout.addRow("وضعیت:", self.status_combo)
        
        # دکمه‌های اصلی
        buttons_layout = QHBoxLayout()
        
        save_btn = QPushButton("ذخیره")
        save_btn.clicked.connect(self.save_user)
        
        cancel_btn = QPushButton("انصراف")
        cancel_btn.clicked.connect(self.reject)
        
        buttons_layout.addWidget(save_btn)
        buttons_layout.addWidget(cancel_btn)
        
        # افزودن همه به لایوت اصلی
        main_layout.addLayout(form_layout)
        main_layout.addLayout(buttons_layout)
        
        self.setLayout(main_layout)
        
    def save_user(self):
        """ذخیره کاربر (افزودن یا ویرایش)"""
        try:
            username = self.username_input.text().strip()
            password = self.password_input.text()
            first_name = self.first_name_input.text().strip()
            last_name = self.last_name_input.text().strip()
            role = self.role_combo.currentText()
            is_active = self.status_combo.currentIndex() == 0  # فعال یا غیرفعال
            
            # اعتبارسنجی
            if not username:
                QMessageBox.warning(self, "هشدار", "لطفاً نام کاربری را وارد کنید.")
                return
                
            if not self.user and not password:  # در حالت افزودن کاربر جدید، رمز عبور اجباری است
                QMessageBox.warning(self, "هشدار", "لطفاً رمز عبور را وارد کنید.")
                return
            
            # آماده‌سازی داده‌های کاربر
            user_data = {
                'username': username,
                'first_name': first_name,
                'last_name': last_name,
                'role': role,
                'is_active': is_active
            }
            
            if password:  # رمز عبور را فقط اگر وارد شده باشد اضافه کنیم
                user_data['password'] = password
            
            # ذخیره کاربر
            if self.user_service:
                if self.user:  # ویرایش کاربر موجود
                    result = self.user_service.update_user(user_data)
                else:  # افزودن کاربر جدید
                    result = self.user_service.create_user(user_data)
                
                if result.get('success', False):
                    self.accept()  # بستن دیالوگ با وضعیت موفقیت
                else:
                    QMessageBox.warning(self, "خطا", f"خطا در ذخیره کاربر: {result.get('error', 'خطای نامشخص')}")
            else:
                logger.error("سرویس کاربر در دسترس نیست")
                QMessageBox.critical(self, "خطا", "سرویس کاربر در دسترس نیست")
                
        except Exception as e:
            logger.error(f"خطا در ذخیره کاربر: {str(e)}")
            QMessageBox.critical(self, "خطا", f"خطا در ذخیره کاربر: {str(e)}") 