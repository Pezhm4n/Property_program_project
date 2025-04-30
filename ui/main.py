#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
برنامه اصلی رابط کاربری گرافیکی سیستم مدیریت املاک
این برنامه واسط کاربری PyQt را برای تعامل با هسته C برنامه مدیریت املاک فراهم می‌کند.
"""

import sys
import os
import ctypes
from pathlib import Path
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QStackedWidget,
                            QMessageBox, QTabWidget)
from PyQt5.QtGui import QIcon, QFont, QPixmap
from PyQt5.QtCore import Qt, QSize

# اضافه کردن مسیر پروژه به sys.path برای واردکردن ماژول‌های داخلی
root_path = Path(__file__).parent.parent
sys.path.append(str(root_path))

# وارد کردن ماژول‌های رابط کاربری
from ui.login_form import LoginForm
from ui.register_form import RegisterForm
from ui.dashboard import Dashboard

class PropertyManagementSystem(QMainWindow):
    """پنجره اصلی برنامه مدیریت املاک"""
    
    def __init__(self):
        super().__init__()
        
        # تنظیم عنوان و اندازه پنجره اصلی
        self.setWindowTitle("سیستم مدیریت املاک")
        self.setMinimumSize(1024, 768)
        
        # بارگذاری کتابخانه C
        self.load_c_library()
        
        # ایجاد ویجت مرکزی و چیدمان اصلی
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # ایجاد استک ویجت برای تغییر بین صفحات مختلف
        self.stacked_widget = QStackedWidget()
        
        # ایجاد فرم‌های ورود و ثبت‌نام
        self.login_form = LoginForm(self)
        self.register_form = RegisterForm(self)
        self.dashboard = Dashboard(self)
        
        # اضافه کردن صفحات به استک ویجت
        self.stacked_widget.addWidget(self.login_form)
        self.stacked_widget.addWidget(self.register_form)
        self.stacked_widget.addWidget(self.dashboard)
        
        # نمایش فرم ورود به عنوان صفحه اول
        self.stacked_widget.setCurrentWidget(self.login_form)
        
        # اضافه کردن استک ویجت به لایه اصلی
        self.main_layout.addWidget(self.stacked_widget)
        
        # تنظیم استایل و رویدادها
        self.setup_style()
        self.setup_signals()

    def load_c_library(self):
        """بارگذاری کتابخانه C برای دسترسی به توابع سیستم"""
        try:
            lib_path = os.path.join(root_path, "build", "property_lib.dll")
            self.c_lib = ctypes.CDLL(lib_path)
            print("کتابخانه C با موفقیت بارگذاری شد.")
            
            # تنظیم تایپ‌های بازگشتی توابع
            self.setup_function_types()
            
        except Exception as e:
            QMessageBox.critical(self, "خطا در بارگذاری کتابخانه", 
                               f"خطا در بارگذاری کتابخانه C: {str(e)}")
            sys.exit(1)
    
    def setup_function_types(self):
        """تنظیم تایپ‌های توابع کتابخانه C"""
        # تنظیم تایپ‌های بازگشتی و پارامترهای توابع
        pass
        
    def setup_style(self):
        """تنظیم استایل و ظاهر برنامه"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QLabel {
                font-size: 12pt;
            }
            QPushButton {
                font-size: 11pt;
                padding: 8px 16px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 11pt;
            }
        """)
        
    def setup_signals(self):
        """تنظیم سیگنال‌ها و اسلات‌های برنامه"""
        self.login_form.register_button.clicked.connect(self.show_register_form)
        self.register_form.login_button.clicked.connect(self.show_login_form)
        self.login_form.login_succeeded.connect(self.show_dashboard)
        
    def show_login_form(self):
        """نمایش فرم ورود"""
        self.stacked_widget.setCurrentWidget(self.login_form)
        
    def show_register_form(self):
        """نمایش فرم ثبت‌نام"""
        self.stacked_widget.setCurrentWidget(self.register_form)
        
    def show_dashboard(self, username):
        """نمایش داشبورد پس از ورود موفق"""
        self.dashboard.set_username(username)
        self.stacked_widget.setCurrentWidget(self.dashboard)

# تابع اصلی برنامه
def main():
    app = QApplication(sys.argv)
    
    # تنظیم فونت فارسی برای کل برنامه
    font = QFont("Tahoma", 10)
    app.setFont(font)
    
    # تنظیم جهت راست به چپ برای زبان فارسی
    app.setLayoutDirection(Qt.RightToLeft)
    
    # ایجاد و نمایش پنجره اصلی
    window = PropertyManagementSystem()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 