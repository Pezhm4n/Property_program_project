#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
این ماژول نقطه ورودی اصلی برنامه سیستم مدیریت املاک است.
این برنامه یک واسط گرافیکی برای سیستم مدیریت املاک ارائه می‌دهد.
"""

import os
import sys
import logging
import traceback
from datetime import datetime

from PyQt5.QtWidgets import QApplication, QSplashScreen, QMessageBox
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, QTranslator, QLocale, QLibraryInfo

# افزودن مسیر اصلی پروژه به sys.path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
    
# واردات ماژول‌های برنامه - اصلاح مسیرها با توجه به ساختار جدید
from ui.main_window import MainWindow
from ui.login_dialog import LoginDialog
from property_management import __version__

# تنظیم لاگر برنامه
def setup_logging():
    """تنظیم سیستم لاگ برنامه"""
    log_dir = os.path.join(project_root, "logs")
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, f"app_{datetime.now().strftime('%Y%m%d')}.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # محدود کردن لاگ‌های کتابخانه‌های خارجی
    logging.getLogger("matplotlib").setLevel(logging.WARNING)
    logging.getLogger("PyQt5").setLevel(logging.WARNING)
    
    return logging.getLogger("property_management")

# ثبت هندلر خطاهای پیش‌بینی نشده
def exception_hook(exctype, value, tb):
    """هندلر خطاهای پیش‌بینی نشده برای ثبت در لاگ"""
    error_msg = ''.join(traceback.format_exception(exctype, value, tb))
    logger.critical(f"خطای پیش‌بینی نشده: {error_msg}")
    sys.__excepthook__(exctype, value, tb)
    
    # نمایش دیالوگ خطا به کاربر
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Critical)
    msg_box.setWindowTitle("خطای پیش‌بینی نشده")
    msg_box.setText("متأسفانه یک خطای پیش‌بینی نشده رخ داده است.")
    msg_box.setInformativeText("جزئیات خطا در فایل لاگ ثبت شده است.")
    msg_box.setDetailedText(error_msg)
    msg_box.exec_()

def main():
    """تابع اصلی برنامه"""
    # تنظیم استایل برنامه
    if "PROPERTY_MANAGEMENT_STYLE" in os.environ:
        os.environ["QT_STYLE_OVERRIDE"] = os.environ["PROPERTY_MANAGEMENT_STYLE"]
    else:
        os.environ["QT_STYLE_OVERRIDE"] = "Fusion"
    
    # ایجاد نمونه از برنامه
    app = QApplication(sys.argv)
    app.setApplicationName("PropertyManagement")
    app.setApplicationVersion(__version__)
    app.setOrganizationName("PropertyManagementTeam")
    app.setOrganizationDomain("property-management.com")
    
    # تنظیم آیکون برنامه - اصلاح مسیر برای ساختار جدید
    icon_path = os.path.join(project_root, "ui", "resources", "icons", "app_icon.png")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    # نمایش صفحه اسپلش - اصلاح مسیر برای ساختار جدید
    splash_path = os.path.join(project_root, "ui", "resources", "images", "splash.png")
    if os.path.exists(splash_path):
        splash_pixmap = QPixmap(splash_path)
        splash = QSplashScreen(splash_pixmap, Qt.WindowStaysOnTopHint)
        splash.show()
        app.processEvents()
    else:
        splash = None
    
    # بارگذاری ترجمه‌های QT
    translator = QTranslator()
    translator.load(QLocale.system(), "qtbase", "_", 
                   QLibraryInfo.location(QLibraryInfo.TranslationsPath))
    app.installTranslator(translator)
    
    try:
        # نمایش دیالوگ ورود
        login_dialog = LoginDialog()
        if splash:
            # کمی تاخیر برای نمایش اسپلش
            from PyQt5.QtCore import QTimer
            QTimer.singleShot(1500, lambda: (splash.finish(login_dialog), login_dialog.exec_()))
        else:
            login_dialog.exec_()
        
        # اگر ورود موفقیت‌آمیز نبود، خروج از برنامه
        if not login_dialog.is_logged_in():
            return 0
        
        # بارگذاری پنجره اصلی برنامه
        main_window = MainWindow(login_dialog.get_username())
        main_window.show()
    except Exception as e:
        logger.error(f"خطا در راه‌اندازی رابط کاربری: {e}")
        traceback.print_exc()
        QMessageBox.critical(None, "خطا", f"خطا در راه‌اندازی برنامه: {str(e)}")
        return 1
    
    # اجرای حلقه رویداد برنامه
    return app.exec_()

if __name__ == "__main__":
    # تنظیم سیستم لاگ
    logger = setup_logging()
    logger.info(f"شروع برنامه مدیریت املاک نسخه {__version__}")
    
    # تنظیم هندلر خطاهای پیش‌بینی نشده
    sys.excepthook = exception_hook
    
    # اجرای تابع اصلی و خروج با کد بازگشتی
    sys.exit(main()) 