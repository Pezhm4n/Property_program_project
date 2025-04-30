#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ماژول دیالوگ مدیریت کاربران
این ماژول پیاده‌سازی دیالوگ مدیریت کاربران را ارائه می‌دهد.
"""

import os
import logging
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QFormLayout, QComboBox, QMessageBox,
    QGroupBox, QSpinBox, QTabWidget, QWidget, QHeaderView, QCheckBox
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QIcon

from bridge.user_bridge import login, register_user, get_all_users, deactivate_user, activate_user

class UserManagementDialog(QDialog):
    """دیالوگ مدیریت کاربران"""
    
    def __init__(self, current_user, parent=None):
        """سازنده دیالوگ مدیریت کاربران
        
        Args:
            current_user (User): کاربر فعلی
            parent (QWidget, optional): ویجت والد. پیش‌فرض None.
        """
        super().__init__(parent)
        
        self.logger = logging.getLogger(__name__)
        self.current_user = current_user
        
        # تنظیم عنوان و ابعاد دیالوگ
        self.setWindowTitle("مدیریت کاربران")
        self.resize(800, 600)
        
        # راه‌اندازی رابط کاربری
        self.init_ui()
        
        # بارگیری لیست کاربران
        self.load_users()
    
    def init_ui(self):
        """راه‌اندازی رابط کاربری"""
        # طرح‌بندی اصلی
        main_layout = QVBoxLayout(self)
        
        # ایجاد زبانه‌ها
        tab_widget = QTabWidget()
        
        # زبانه لیست کاربران
        users_list_widget = self._create_users_list_widget()
        tab_widget.addTab(users_list_widget, "لیست کاربران")
        
        # زبانه افزودن کاربر جدید
        new_user_widget = self._create_new_user_widget()
        tab_widget.addTab(new_user_widget, "افزودن کاربر جدید")
        
        main_layout.addWidget(tab_widget)
        
        # دکمه‌های دیالوگ
        buttons_layout = QHBoxLayout()
        
        close_button = QPushButton("بستن")
        close_button.clicked.connect(self.close)
        buttons_layout.addWidget(close_button)
        
        main_layout.addLayout(buttons_layout)
    
    def _create_users_list_widget(self):
        """ایجاد ویجت لیست کاربران
        
        Returns:
            QWidget: ویجت لیست کاربران
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # جدول کاربران
        self.users_table = QTableWidget()
        self.users_table.setColumnCount(6)
        self.users_table.setHorizontalHeaderLabels([
            "نام کاربری", "نام کامل", "نقش", "ایمیل", "تاریخ ثبت‌نام", "وضعیت"
        ])
        self.users_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.users_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.users_table.setSelectionMode(QTableWidget.SingleSelection)
        self.users_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        layout.addWidget(self.users_table)
        
        # دکمه‌های عملیات
        buttons_layout = QHBoxLayout()
        
        self.activate_button = QPushButton("فعال کردن کاربر")
        self.activate_button.clicked.connect(self._activate_user)
        buttons_layout.addWidget(self.activate_button)
        
        self.deactivate_button = QPushButton("غیرفعال کردن کاربر")
        self.deactivate_button.clicked.connect(self._deactivate_user)
        buttons_layout.addWidget(self.deactivate_button)
        
        buttons_layout.addStretch()
        
        refresh_button = QPushButton("بازنشانی لیست")
        refresh_button.clicked.connect(self.load_users)
        buttons_layout.addWidget(refresh_button)
        
        layout.addLayout(buttons_layout)
        
        return widget
    
    def _create_new_user_widget(self):
        """ایجاد ویجت افزودن کاربر جدید
        
        Returns:
            QWidget: ویجت افزودن کاربر جدید
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # گروه اطلاعات کاربر
        user_info_group = QGroupBox("اطلاعات کاربر")
        form_layout = QFormLayout(user_info_group)
        
        # نام کاربری
        self.username_edit = QLineEdit()
        form_layout.addRow("نام کاربری:", self.username_edit)
        
        # رمز عبور
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        form_layout.addRow("رمز عبور:", self.password_edit)
        
        # تکرار رمز عبور
        self.confirm_password_edit = QLineEdit()
        self.confirm_password_edit.setEchoMode(QLineEdit.Password)
        form_layout.addRow("تکرار رمز عبور:", self.confirm_password_edit)
        
        # نام کامل
        self.fullname_edit = QLineEdit()
        form_layout.addRow("نام کامل:", self.fullname_edit)
        
        # ایمیل
        self.email_edit = QLineEdit()
        form_layout.addRow("ایمیل:", self.email_edit)
        
        # شماره تلفن
        self.phone_edit = QLineEdit()
        form_layout.addRow("شماره تلفن:", self.phone_edit)
        
        # نقش کاربر
        self.role_combo = QComboBox()
        self.role_combo.addItems(["مشتری", "مشاور املاک", "مدیر"])
        form_layout.addRow("نقش کاربر:", self.role_combo)
        
        # وضعیت کاربر
        self.active_check = QCheckBox("کاربر فعال است")
        self.active_check.setChecked(True)
        form_layout.addRow("وضعیت:", self.active_check)
        
        layout.addWidget(user_info_group)
        
        # دکمه‌های عملیات
        buttons_layout = QHBoxLayout()
        
        clear_button = QPushButton("پاک کردن فرم")
        clear_button.clicked.connect(self._clear_form)
        buttons_layout.addWidget(clear_button)
        
        buttons_layout.addStretch()
        
        register_button = QPushButton("ثبت کاربر جدید")
        register_button.clicked.connect(self._register_new_user)
        buttons_layout.addWidget(register_button)
        
        layout.addLayout(buttons_layout)
        
        return widget
    
    def load_users(self):
        """بارگیری لیست کاربران"""
        try:
            # دریافت لیست کاربران
            users = get_all_users() or []
            
            # پاک کردن لیست فعلی
            self.users_table.setRowCount(0)
            
            # افزودن کاربران به جدول
            for user in users:
                row_position = self.users_table.rowCount()
                self.users_table.insertRow(row_position)
                
                self.users_table.setItem(row_position, 0, QTableWidgetItem(user.get("username", "")))
                self.users_table.setItem(row_position, 1, QTableWidgetItem(user.get("fullName", "")))
                self.users_table.setItem(row_position, 2, QTableWidgetItem(user.get("userType", "")))
                self.users_table.setItem(row_position, 3, QTableWidgetItem(user.get("email", "")))
                self.users_table.setItem(row_position, 4, QTableWidgetItem(user.get("registrationDate", "")))
                
                is_active = user.get("isActive", False)
                status_text = "فعال" if is_active else "غیرفعال"
                self.users_table.setItem(row_position, 5, QTableWidgetItem(status_text))
            
            self.logger.info(f"لیست کاربران با موفقیت بارگیری شد: {len(users)} کاربر")
        except Exception as e:
            self.logger.error(f"خطا در بارگیری لیست کاربران: {str(e)}")
            QMessageBox.critical(self, "خطا", f"خطا در بارگیری لیست کاربران: {str(e)}")
    
    def _clear_form(self):
        """پاک کردن فرم افزودن کاربر جدید"""
        self.username_edit.clear()
        self.password_edit.clear()
        self.confirm_password_edit.clear()
        self.fullname_edit.clear()
        self.email_edit.clear()
        self.phone_edit.clear()
        self.role_combo.setCurrentIndex(0)
        self.active_check.setChecked(True)
    
    def _register_new_user(self):
        """ثبت کاربر جدید"""
        # دریافت اطلاعات کاربر از فرم
        username = self.username_edit.text().strip()
        password = self.password_edit.text()
        confirm_password = self.confirm_password_edit.text()
        fullname = self.fullname_edit.text().strip()
        email = self.email_edit.text().strip()
        phone = self.phone_edit.text().strip()
        role = self.role_combo.currentText()
        is_active = self.active_check.isChecked()
        
        # اعتبارسنجی ورودی‌ها
        if not username:
            QMessageBox.warning(self, "هشدار", "نام کاربری نمی‌تواند خالی باشد.")
            return
        
        if not password:
            QMessageBox.warning(self, "هشدار", "رمز عبور نمی‌تواند خالی باشد.")
            return
        
        if password != confirm_password:
            QMessageBox.warning(self, "هشدار", "رمز عبور و تکرار آن باید یکسان باشند.")
            return
        
        # ایجاد دیکشنری اطلاعات کاربر
        user_info = {
            "username": username,
            "password": password,
            "name": fullname,
            "email": email,
            "phone": phone,
            "user_type": role,
            "is_active": is_active
        }
        
        try:
            # ثبت کاربر جدید
            result = register_user(user_info)
            
            if result:
                self.logger.info(f"کاربر جدید با موفقیت ثبت شد: {username}")
                QMessageBox.information(self, "اطلاعات", f"کاربر {username} با موفقیت ثبت شد.")
                
                # پاک کردن فرم
                self._clear_form()
                
                # بازنشانی لیست کاربران
                self.load_users()
            else:
                self.logger.warning(f"خطا در ثبت کاربر جدید: {username}")
                QMessageBox.warning(self, "هشدار", "خطا در ثبت کاربر جدید. لطفاً دوباره تلاش کنید.")
        except Exception as e:
            self.logger.error(f"خطا در ثبت کاربر جدید: {str(e)}")
            QMessageBox.critical(self, "خطا", f"خطا در ثبت کاربر جدید: {str(e)}")
    
    def _activate_user(self):
        """فعال کردن کاربر انتخاب شده"""
        selected_row = self.users_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "هشدار", "لطفاً یک کاربر را انتخاب کنید.")
            return
        
        username = self.users_table.item(selected_row, 0).text()
        
        try:
            result = activate_user(self.current_user.username, username)
            
            if result:
                self.logger.info(f"کاربر با موفقیت فعال شد: {username}")
                QMessageBox.information(self, "اطلاعات", f"کاربر {username} با موفقیت فعال شد.")
                
                # بازنشانی لیست کاربران
                self.load_users()
            else:
                self.logger.warning(f"خطا در فعال کردن کاربر: {username}")
                QMessageBox.warning(self, "هشدار", "خطا در فعال کردن کاربر. لطفاً دوباره تلاش کنید.")
        except Exception as e:
            self.logger.error(f"خطا در فعال کردن کاربر: {str(e)}")
            QMessageBox.critical(self, "خطا", f"خطا در فعال کردن کاربر: {str(e)}")
    
    def _deactivate_user(self):
        """غیرفعال کردن کاربر انتخاب شده"""
        selected_row = self.users_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "هشدار", "لطفاً یک کاربر را انتخاب کنید.")
            return
        
        username = self.users_table.item(selected_row, 0).text()
        
        # نمی‌توان کاربر فعلی را غیرفعال کرد
        if username == self.current_user.username:
            QMessageBox.warning(self, "هشدار", "شما نمی‌توانید خودتان را غیرفعال کنید.")
            return
        
        try:
            result = deactivate_user(self.current_user.username, username)
            
            if result:
                self.logger.info(f"کاربر با موفقیت غیرفعال شد: {username}")
                QMessageBox.information(self, "اطلاعات", f"کاربر {username} با موفقیت غیرفعال شد.")
                
                # بازنشانی لیست کاربران
                self.load_users()
            else:
                self.logger.warning(f"خطا در غیرفعال کردن کاربر: {username}")
                QMessageBox.warning(self, "هشدار", "خطا در غیرفعال کردن کاربر. لطفاً دوباره تلاش کنید.")
        except Exception as e:
            self.logger.error(f"خطا در غیرفعال کردن کاربر: {str(e)}")
            QMessageBox.critical(self, "خطا", f"خطا در غیرفعال کردن کاربر: {str(e)}")