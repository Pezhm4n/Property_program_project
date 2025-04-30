#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
برنامه اصلی رابط کاربری گرافیکی سیستم مدیریت املاک
این برنامه واسط کاربری PyQt را برای تعامل با هسته C برنامه مدیریت املاک فراهم می‌کند.
"""

import sys
import os
import ctypes
import logging
from pathlib import Path

# اضافه کردن مسیر پروژه به sys.path برای واردکردن ماژول‌های داخلی
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# تنظیم لاگر
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# نمایش لاگ در کنسول
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# ذخیره لاگ در فایل
log_file = os.path.join(project_root, 'logs', 'ui.log')
os.makedirs(os.path.dirname(log_file), exist_ok=True)
file_handler = logging.FileHandler(log_file)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

try:
    from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                                QHBoxLayout, QPushButton, QLabel, QStackedWidget,
                                QMessageBox, QTabWidget)
    from PyQt5.QtGui import QIcon, QFont, QPixmap
    from PyQt5.QtCore import Qt, QSize
    
    # وارد کردن ماژول‌های رابط کاربری
    from ui.login_form import LoginForm
    from ui.register_form import RegisterForm
    from ui.dashboard import Dashboard
    
    logger.info("ماژول‌های PyQt با موفقیت بارگذاری شدند")
except ImportError as e:
    logger.error(f"خطا در واردسازی ماژول‌ها: {e}")
    print(f"خطا در واردسازی ماژول‌ها: {e}")
    print("لطفاً اطمینان حاصل کنید که PyQt5 نصب شده است.")
    sys.exit(1)

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
        
        try:
            # ایجاد فرم‌های ورود و ثبت‌نام
            self.login_form = LoginForm(self)
            self.register_form = RegisterForm(self)
            
            # داشبورد با پارامتر نام کاربری ایجاد می‌شود
            # در اینجا یک مقدار پیش‌فرض می‌دهیم
            self.dashboard = Dashboard("کاربر", self)
            
            # اضافه کردن صفحات به استک ویجت
            self.stacked_widget.addWidget(self.login_form)
            self.stacked_widget.addWidget(self.register_form)
            self.stacked_widget.addWidget(self.dashboard)
            
            # نمایش فرم ورود به عنوان صفحه اول
            self.stacked_widget.setCurrentWidget(self.login_form)
            
            logger.info("کامپوننت‌های رابط کاربری با موفقیت بارگذاری شدند")
        except Exception as e:
            logger.error(f"خطا در ایجاد کامپوننت‌های رابط کاربری: {e}")
            QMessageBox.critical(self, "خطا", f"خطا در بارگذاری رابط کاربری: {str(e)}")
        
        # اضافه کردن استک ویجت به لایه اصلی
        self.main_layout.addWidget(self.stacked_widget)
        
        # تنظیم استایل و رویدادها
        self.setup_style()
        self.setup_signals()

    def load_c_library(self):
        """بارگذاری کتابخانه C برای دسترسی به توابع سیستم"""
        try:
            # مسیرهای کامپایل احتمالی کتابخانه C در پروژه
            possible_paths = [
                # مسیرهای ویندوز
                os.path.join(project_root, "bin", "property_lib.dll"),
                os.path.join(project_root, "build", "bin", "property_lib.dll"),
                os.path.join(project_root, "build", "property_lib.dll"),
                os.path.join(project_root, "build", "Debug", "property_lib.dll"),
                os.path.join(project_root, "build", "Release", "property_lib.dll"),
                
                # مسیرهای لینوکس/مک
                os.path.join(project_root, "bin", "libproperty.so"),
                os.path.join(project_root, "build", "libproperty.so"),
                os.path.join(project_root, "lib", "libproperty.so"),
                os.path.join(project_root, "build", "lib", "libproperty.so"),
                
                # مسیرهای مک
                os.path.join(project_root, "bin", "libproperty.dylib"),
                os.path.join(project_root, "build", "libproperty.dylib"),
                os.path.join(project_root, "lib", "libproperty.dylib"),
                os.path.join(project_root, "build", "lib", "libproperty.dylib"),
            ]
            
            # چک کردن مسیرهای احتمالی
            lib_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    lib_path = path
                    break
            
            if lib_path is None:
                # کتابخانه C پیدا نشد
                logger.warning("کتابخانه C در مسیرهای مورد انتظار یافت نشد")
                logger.warning("مسیرهای بررسی شده: " + ", ".join(possible_paths))
                print("هشدار: کتابخانه C در مسیرهای مورد انتظار یافت نشد.")
                print("برنامه بدون قابلیت‌های هسته C اجرا می‌شود.")
                
                # آیا نیاز به کامپایل کتابخانه C است؟
                if os.path.exists(os.path.join(project_root, "src")) and os.path.exists(os.path.join(project_root, "include")):
                    print("پیشنهاد: کتابخانه C را با استفاده از Makefile کامپایل کنید:")
                    print("cd " + str(project_root) + " && make")
                
                return
            
            # بارگذاری کتابخانه C
            self.c_lib = ctypes.CDLL(lib_path)
            logger.info(f"کتابخانه C با موفقیت از مسیر {lib_path} بارگذاری شد")
            
            # تنظیم تایپ‌های بازگشتی توابع
            self.setup_function_types()
            
        except Exception as e:
            logger.error(f"خطا در بارگذاری کتابخانه C: {str(e)}")
            print(f"خطا در بارگذاری کتابخانه C: {str(e)}")
            print("برنامه بدون قابلیت‌های هسته C اجرا می‌شود.")
    
    def setup_function_types(self):
        """تنظیم تایپ‌های توابع کتابخانه C"""
        # تنظیم تایپ‌های بازگشتی و پارامترهای توابع
        if hasattr(self, 'c_lib'):
            # تنظیم تایپ‌های توابع مورد نیاز در اینجا
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
        try:
            self.login_form.register_button.clicked.connect(self.show_register_form)
            self.register_form.login_button.clicked.connect(self.show_login_form)
            self.login_form.login_succeeded.connect(self.show_dashboard)
            logger.info("سیگنال‌ها با موفقیت متصل شدند")
        except Exception as e:
            logger.error(f"خطا در تنظیم سیگنال‌ها: {e}")
        
    def show_login_form(self):
        """نمایش فرم ورود"""
        self.stacked_widget.setCurrentWidget(self.login_form)
        
    def show_register_form(self):
        """نمایش فرم ثبت‌نام"""
        self.stacked_widget.setCurrentWidget(self.register_form)
        
    def show_dashboard(self, username):
        """نمایش داشبورد پس از ورود موفق"""
        # ایجاد داشبورد جدید با نام کاربری کاربر فعلی
        try:
            # ایجاد نمونه جدید Dashboard با نام کاربری
            new_dashboard = Dashboard(username, self)
            
            # جایگزینی داشبورد قبلی
            old_dashboard = self.dashboard
            self.stacked_widget.removeWidget(old_dashboard)
            old_dashboard.deleteLater()
            
            # اضافه کردن و نمایش داشبورد جدید
            self.dashboard = new_dashboard
            self.stacked_widget.addWidget(self.dashboard)
            self.stacked_widget.setCurrentWidget(self.dashboard)
            
            logger.info(f"داشبورد برای کاربر {username} با موفقیت نمایش داده شد")
        except Exception as e:
            logger.error(f"خطا در نمایش داشبورد: {e}")
            QMessageBox.warning(self, "خطا", f"خطا در بارگذاری داشبورد: {str(e)}")

# تابع اصلی برنامه
def main():
    try:
        app = QApplication(sys.argv)
        
        # تنظیم فونت فارسی برای کل برنامه
        font = QFont("Tahoma", 10)
        app.setFont(font)
        
        # تنظیم جهت راست به چپ برای زبان فارسی
        app.setLayoutDirection(Qt.RightToLeft)
        
        # ایجاد و نمایش پنجره اصلی
        window = PropertyManagementSystem()
        window.show()
        
        logger.info("برنامه با موفقیت راه‌اندازی شد")
        
        return app.exec_()
    except Exception as e:
        logger.critical(f"خطای اساسی در راه‌اندازی برنامه: {e}")
        print(f"خطای اساسی: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 