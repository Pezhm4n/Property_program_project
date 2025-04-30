#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
این ماژول مسئول بررسی به‌روزرسانی‌های برنامه و نصب آن‌ها است.
امکان بررسی خودکار به‌روزرسانی‌ها، دانلود و نصب آن‌ها را فراهم می‌کند.
"""

import os
import sys
import json
import time
import logging
import platform
import subprocess
import tempfile
import threading
import urllib.request
import urllib.error
from distutils.version import StrictVersion
from datetime import datetime

from PyQt5.QtCore import QObject, pyqtSignal, QThread, QUrl, QSettings
from PyQt5.QtWidgets import QMessageBox, QProgressDialog
from PyQt5.QtGui import QDesktopServices

from property_management import __version__
from property_management.config import config_manager, ConfigSection

# تنظیم لاگر
logger = logging.getLogger(__name__)

# آدرس سرور به‌روزرسانی
UPDATE_SERVER_URL = "https://api.property-management.com/updates"
UPDATE_CHECK_INTERVAL = 24 * 60 * 60  # 24 ساعت (به ثانیه)

class UpdateStatus:
    """وضعیت‌های مختلف به‌روزرسانی"""
    UP_TO_DATE = 0
    UPDATE_AVAILABLE = 1
    UPDATE_DOWNLOADING = 2
    UPDATE_READY = 3
    ERROR = 4

class UpdateWorker(QObject):
    """کلاس کارگر برای بررسی به‌روزرسانی‌ها در یک رشته (thread) جداگانه"""
    
    # سیگنال‌ها
    update_available = pyqtSignal(dict)  # اطلاعات نسخه جدید
    update_not_available = pyqtSignal()
    update_progress = pyqtSignal(int, int)  # مقدار فعلی، مقدار حداکثر
    update_error = pyqtSignal(str)  # پیام خطا
    update_downloaded = pyqtSignal(str)  # مسیر فایل دانلود شده
    
    def __init__(self, parent=None):
        """مقداردهی اولیه کلاس UpdateWorker"""
        super(UpdateWorker, self).__init__(parent)
        self._cancel_requested = False
        self._current_version = StrictVersion(__version__)
    
    def check_for_updates(self, silent=False):
        """
        بررسی وجود به‌روزرسانی‌های جدید
        
        پارامترها:
            silent: عدم نمایش خطا در صورت عدم وجود به‌روزرسانی
        """
        try:
            # ساخت آدرس API با توجه به سیستم عامل
            system = platform.system().lower()
            url = f"{UPDATE_SERVER_URL}/check?version={__version__}&platform={system}"
            
            # ارسال درخواست به سرور
            with urllib.request.urlopen(url, timeout=10) as response:
                data = json.loads(response.read().decode("utf-8"))
            
            if not data.get("success", False):
                if not silent:
                    self.update_error.emit(data.get("message", "خطا در بررسی به‌روزرسانی"))
                return
            
            # بررسی وجود نسخه جدید
            if "version" in data:
                latest_version = StrictVersion(data["version"])
                
                if latest_version > self._current_version:
                    # به‌روزرسانی جدید موجود است
                    self.update_available.emit(data)
                else:
                    # برنامه به‌روز است
                    self.update_not_available.emit()
            else:
                # اطلاعات نامعتبر از سرور
                if not silent:
                    self.update_error.emit("اطلاعات نامعتبر از سرور دریافت شد")
        
        except urllib.error.URLError as e:
            if not silent:
                self.update_error.emit(f"خطا در ارتباط با سرور: {str(e)}")
        except Exception as e:
            if not silent:
                self.update_error.emit(f"خطا در بررسی به‌روزرسانی: {str(e)}")
    
    def download_update(self, download_url, version):
        """
        دانلود فایل به‌روزرسانی
        
        پارامترها:
            download_url: آدرس دانلود فایل
            version: نسخه به‌روزرسانی
        """
        try:
            self._cancel_requested = False
            
            # تعیین مسیر ذخیره فایل
            file_name = download_url.split("/")[-1]
            download_dir = os.path.join(tempfile.gettempdir(), "PropertyManagementUpdates")
            os.makedirs(download_dir, exist_ok=True)
            file_path = os.path.join(download_dir, file_name)
            
            # حذف فایل قبلی در صورت وجود
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except:
                    file_path = os.path.join(download_dir, f"{version}_{file_name}")
            
            # دانلود فایل
            with urllib.request.urlopen(download_url) as response:
                file_size = int(response.headers.get("Content-Length", 0))
                downloaded_size = 0
                block_size = 8192
                
                with open(file_path, "wb") as out_file:
                    self.update_progress.emit(0, file_size)
                    
                    while True:
                        if self._cancel_requested:
                            raise Exception("دانلود لغو شد")
                        
                        buffer = response.read(block_size)
                        if not buffer:
                            break
                        
                        out_file.write(buffer)
                        downloaded_size += len(buffer)
                        self.update_progress.emit(downloaded_size, file_size)
            
            # بررسی صحت فایل دانلود شده
            if os.path.getsize(file_path) != file_size and file_size > 0:
                raise Exception("فایل دانلود شده ناقص است")
            
            # فایل با موفقیت دانلود شد
            self.update_downloaded.emit(file_path)
        
        except Exception as e:
            self.update_error.emit(f"خطا در دانلود به‌روزرسانی: {str(e)}")
    
    def cancel_download(self):
        """لغو دانلود در حال انجام"""
        self._cancel_requested = True

class Updater(QObject):
    """کلاس اصلی مدیریت به‌روزرسانی‌ها"""
    
    # سیگنال‌ها
    status_changed = pyqtSignal(int, dict)  # وضعیت جدید، اطلاعات اضافی
    
    def __init__(self, parent=None):
        """مقداردهی اولیه کلاس Updater"""
        super(Updater, self).__init__(parent)
        
        self._settings = QSettings()
        self._thread = QThread()
        self._worker = UpdateWorker()
        self._worker.moveToThread(self._thread)
        
        # اتصال سیگنال‌ها
        self._worker.update_available.connect(self._on_update_available)
        self._worker.update_not_available.connect(self._on_update_not_available)
        self._worker.update_error.connect(self._on_update_error)
        self._worker.update_progress.connect(self._on_update_progress)
        self._worker.update_downloaded.connect(self._on_update_downloaded)
        
        # شروع رشته (thread)
        self._thread.start()
        
        # تنظیم وضعیت اولیه
        self._status = UpdateStatus.UP_TO_DATE
        self._update_info = {}
        self._progress_value = 0
        self._progress_max = 100
        self._download_path = ""
    
    def __del__(self):
        """پاکسازی منابع هنگام حذف نمونه کلاس"""
        self._worker.cancel_download()
        self._thread.quit()
        self._thread.wait()
    
    def check_for_updates(self, silent=False):
        """
        بررسی وجود به‌روزرسانی‌های جدید
        
        پارامترها:
            silent: عدم نمایش خطا در صورت عدم وجود به‌روزرسانی
        """
        # بررسی آیا نیاز به بررسی به‌روزرسانی است
        if not self._should_check_for_updates() and silent:
            return
        
        # ذخیره زمان آخرین بررسی به‌روزرسانی
        self._settings.setValue("updater/last_check", int(time.time()))
        
        # صدا زدن متد بررسی به‌روزرسانی در کارگر
        QThread.invoke_in_main_thread(self._worker.check_for_updates, silent)
    
    def download_update(self):
        """دانلود به‌روزرسانی"""
        if self._status != UpdateStatus.UPDATE_AVAILABLE:
            logger.warning("امکان دانلود وجود ندارد: وضعیت نامناسب")
            return
        
        download_url = self._update_info.get("download_url", "")
        version = self._update_info.get("version", "")
        
        if not download_url:
            self._on_update_error("آدرس دانلود نامعتبر است")
            return
        
        # تغییر وضعیت به در حال دانلود
        self._status = UpdateStatus.UPDATE_DOWNLOADING
        self.status_changed.emit(self._status, self._update_info)
        
        # صدا زدن متد دانلود در کارگر
        QThread.invoke_in_main_thread(self._worker.download_update, download_url, version)
    
    def cancel_download(self):
        """لغو دانلود در حال انجام"""
        if self._status == UpdateStatus.UPDATE_DOWNLOADING:
            self._worker.cancel_download()
    
    def install_update(self):
        """نصب به‌روزرسانی دانلود شده"""
        if self._status != UpdateStatus.UPDATE_READY or not self._download_path:
            logger.warning("امکان نصب وجود ندارد: وضعیت نامناسب یا فایل دانلود نشده")
            return
        
        # بررسی وجود فایل به‌روزرسانی
        if not os.path.exists(self._download_path):
            self._on_update_error("فایل به‌روزرسانی یافت نشد")
            return
        
        try:
            # تشخیص نوع فایل و نصب آن
            file_ext = os.path.splitext(self._download_path)[1].lower()
            
            if file_ext == ".exe":
                # فایل اجرایی ویندوز
                subprocess.Popen([self._download_path], shell=True)
                sys.exit(0)
            elif file_ext == ".msi":
                # فایل نصب MSI ویندوز
                subprocess.Popen(["msiexec", "/i", self._download_path], shell=True)
                sys.exit(0)
            elif file_ext == ".pkg" or file_ext == ".dmg":
                # فایل نصب macOS
                if platform.system() == "Darwin":
                    subprocess.Popen(["open", self._download_path])
                    sys.exit(0)
                else:
                    raise Exception("این نوع فایل برای سیستم عامل شما پشتیبانی نمی‌شود")
            elif file_ext == ".deb" or file_ext == ".rpm":
                # فایل نصب لینوکس
                if platform.system() == "Linux":
                    if file_ext == ".deb":
                        subprocess.Popen(["pkexec", "apt", "install", "-y", self._download_path], shell=True)
                    else:
                        subprocess.Popen(["pkexec", "rpm", "-U", self._download_path], shell=True)
                    sys.exit(0)
                else:
                    raise Exception("این نوع فایل برای سیستم عامل شما پشتیبانی نمی‌شود")
            elif file_ext == ".zip" or file_ext == ".tar.gz":
                # فایل فشرده
                QDesktopServices.openUrl(QUrl.fromLocalFile(os.path.dirname(self._download_path)))
            else:
                # سایر فایل‌ها
                QDesktopServices.openUrl(QUrl.fromLocalFile(self._download_path))
        
        except Exception as e:
            self._on_update_error(f"خطا در نصب به‌روزرسانی: {str(e)}")
    
    def get_status(self):
        """دریافت وضعیت فعلی به‌روزرسانی"""
        return self._status
    
    def get_update_info(self):
        """دریافت اطلاعات به‌روزرسانی"""
        return self._update_info.copy()
    
    def get_progress(self):
        """دریافت پیشرفت دانلود"""
        return self._progress_value, self._progress_max
    
    def _should_check_for_updates(self):
        """بررسی آیا نیاز به بررسی به‌روزرسانی است"""
        # بررسی آیا به‌روزرسانی خودکار فعال است
        if not config_manager.get_value(ConfigSection.GENERAL, "check_updates", True):
            return False
        
        # بررسی آخرین زمان بررسی به‌روزرسانی
        last_check = self._settings.value("updater/last_check", 0, type=int)
        current_time = int(time.time())
        
        # اگر زمان کافی از آخرین بررسی گذشته باشد
        return (current_time - last_check) >= UPDATE_CHECK_INTERVAL
    
    def _on_update_available(self, update_info):
        """هندلر دریافت به‌روزرسانی جدید"""
        self._status = UpdateStatus.UPDATE_AVAILABLE
        self._update_info = update_info
        self.status_changed.emit(self._status, self._update_info)
    
    def _on_update_not_available(self):
        """هندلر عدم وجود به‌روزرسانی جدید"""
        self._status = UpdateStatus.UP_TO_DATE
        self.status_changed.emit(self._status, {})
    
    def _on_update_error(self, error_message):
        """هندلر خطا در به‌روزرسانی"""
        self._status = UpdateStatus.ERROR
        self._update_info = {"error": error_message}
        self.status_changed.emit(self._status, self._update_info)
    
    def _on_update_progress(self, current, maximum):
        """هندلر پیشرفت دانلود"""
        self._progress_value = current
        self._progress_max = maximum
        
        # به‌روزرسانی وضعیت
        self._update_info["progress"] = current
        self._update_info["progress_max"] = maximum
        
        if maximum > 0:
            self._update_info["progress_percent"] = int(current * 100 / maximum)
        
        self.status_changed.emit(self._status, self._update_info)
    
    def _on_update_downloaded(self, file_path):
        """هندلر دانلود کامل به‌روزرسانی"""
        self._status = UpdateStatus.UPDATE_READY
        self._download_path = file_path
        self._update_info["file_path"] = file_path
        self.status_changed.emit(self._status, self._update_info)

# نمونه تکی از کلاس Updater
updater = Updater() 