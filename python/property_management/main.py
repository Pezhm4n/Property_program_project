#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
برنامه مدیریت املاک
این ماژول نقطه ورود اصلی برنامه مدیریت املاک است که رابط کاربری گرافیکی را راه‌اندازی می‌کند.
"""

import os
import sys
import logging
import argparse
from PyQt5.QtWidgets import QApplication, QSplashScreen, QMainWindow
from PyQt5.QtCore import Qt, QTranslator, QLocale, QLibraryInfo, QTimer
from PyQt5.QtGui import QPixmap, QIcon

# تنظیم مسیر برای یافتن ماژول‌های برنامه
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

# وارد کردن ماژول‌های برنامه
from ui.login_dialog import LoginDialog
from ui.main_window import MainWindow
from user_management import UserManager
from utils import setup_logging


def parse_arguments():
    """تجزیه آرگومان‌های خط فرمان"""
    parser = argparse.ArgumentParser(description='سیستم مدیریت املاک')
    parser.add_argument('--debug', action='store_true', help='فعال‌سازی حالت اشکال‌زدایی')
    parser.add_argument('--data-dir', type=str, help='مسیر دایرکتوری داده‌ها')
    parser.add_argument('--config', type=str, help='مسیر فایل پیکربندی')
    return parser.parse_args()


def setup_qt_application():
    """راه‌اندازی برنامه Qt و تنظیم مترجم"""
    app = QApplication(sys.argv)
    app.setApplicationName("مدیریت املاک")
    app.setOrganizationName("شرکت مدیریت املاک")
    app.setOrganizationDomain("property-management.com")
    
    # تنظیم آیکون برنامه
    icon_path = os.path.join(script_dir, 'resources', 'icons', 'app_icon.png')
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    # تنظیم مترجم برای پشتیبانی از زبان فارسی
    translator = QTranslator()
    translator.load("qt_" + QLocale.system().name(),
                  QLibraryInfo.location(QLibraryInfo.TranslationsPath))
    app.installTranslator(translator)
    
    # تنظیم استایل برنامه (اختیاری)
    app.setStyle('Fusion')
    
    return app


def show_splash_screen():
    """نمایش صفحه اسپلش هنگام شروع برنامه"""
    splash_path = os.path.join(script_dir, 'resources', 'images', 'splash.png')
    
    if os.path.exists(splash_path):
        splash_pixmap = QPixmap(splash_path)
        splash = QSplashScreen(splash_pixmap, Qt.WindowStaysOnTopHint)
        splash.show()
        
        # نمایش پیام‌های بارگذاری
        splash.showMessage("در حال بارگذاری ماژول‌ها...", 
                           Qt.AlignBottom | Qt.AlignCenter, Qt.white)
        
        # مطمئن شویم که اسپلش اسکرین نمایش داده شود
        QApplication.processEvents()
        
        return splash
    
    return None


def main():
    """تابع اصلی برنامه"""
    # تجزیه آرگومان‌های خط فرمان
    args = parse_arguments()
    
    # تنظیم سیستم ثبت وقایع
    log_level = logging.DEBUG if args.debug else logging.INFO
    setup_logging(log_level)
    logger = logging.getLogger(__name__)
    
    logger.info("شروع برنامه مدیریت املاک")
    
    try:
        # راه‌اندازی برنامه Qt
        app = setup_qt_application()
        
        # نمایش صفحه اسپلش
        splash = show_splash_screen()
        
        # تنظیم مدیر کاربر
        user_manager = UserManager()
        
        if splash:
            splash.showMessage("در حال بررسی احراز هویت...", 
                               Qt.AlignBottom | Qt.AlignCenter, Qt.white)
        
        # نمایش دیالوگ ورود
        login_dialog = LoginDialog(user_manager)
        
        if splash:
            # یک تاخیر کوتاه برای نمایش اسپلش اسکرین
            QTimer.singleShot(2000, lambda: splash.close())
        
        # اجرای دیالوگ ورود
        if login_dialog.exec_() != LoginDialog.Accepted:
            logger.info("کاربر از ورود به سیستم منصرف شد")
            return 0
        
        # دریافت کاربر تایید شده
        current_user = login_dialog.get_authenticated_user()
        
        if not current_user:
            logger.error("خطا در احراز هویت")
            return 1
        
        logger.info(f"کاربر '{current_user.username}' با موفقیت وارد سیستم شد")
        
        # نمایش پنجره اصلی
        main_window = MainWindow(current_user, user_manager)
        main_window.show()
        
        # اجرای حلقه رویداد
        return app.exec_()
        
    except Exception as e:
        logger.exception(f"خطای ناگهانی در اجرای برنامه: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 