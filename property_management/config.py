#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
این ماژول برای مدیریت پیکربندی برنامه استفاده می‌شود.
تنظیمات برنامه را ذخیره و بازیابی می‌کند و همچنین پیکربندی پیش‌فرض را تعریف می‌کند.
"""

import os
import json
import logging
import platform
from enum import Enum

from PyQt5.QtCore import QSettings, QStandardPaths

logger = logging.getLogger(__name__)

class ConfigSection(Enum):
    """بخش‌های مختلف پیکربندی"""
    GENERAL = "general"
    DATABASE = "database"
    APPEARANCE = "appearance"
    SECURITY = "security"
    REPORTS = "reports"
    ADVANCED = "advanced"

class Config:
    """کلاس مدیریت پیکربندی برنامه"""
    
    # مقادیر پیش‌فرض
    DEFAULT_CONFIG = {
        ConfigSection.GENERAL.value: {
            "language": "fa_IR",
            "startup_tab": "dashboard",
            "auto_login": False,
            "last_username": "",
            "last_login_time": "",
            "check_updates": True,
            "show_welcome": True,
        },
        ConfigSection.DATABASE.value: {
            "data_path": "",  # مسیر خودکار با استفاده از _get_default_data_path() تنظیم می‌شود
            "backup_enabled": True,
            "backup_interval": 7,  # روز
            "backup_count": 5,  # تعداد نسخه‌های پشتیبان
            "backup_path": "",  # مسیر خودکار با استفاده از _get_default_backup_path() تنظیم می‌شود
        },
        ConfigSection.APPEARANCE.value: {
            "theme": "system",  # روشن، تیره، سیستم، سفارشی
            "font_family": "",  # بر اساس سیستم عامل تنظیم می‌شود
            "font_size": "medium",  # کوچک، متوسط، بزرگ، سفارشی
            "custom_font_size": 10,
            "icon_size": "medium",  # کوچک، متوسط، بزرگ
            "show_status_bar": True,
            "show_toolbar": True,
            "toolbar_style": "icon_text",  # آیکون، متن، آیکون_متن
        },
        ConfigSection.SECURITY.value: {
            "login_required": True,
            "session_timeout": 30,  # دقیقه، 0 برای غیرفعال
            "password_expiry": 90,  # روز، 0 برای غیرفعال
            "failed_login_limit": 5,  # تعداد تلاش‌های ناموفق، 0 برای غیرفعال
            "lockout_duration": 15,  # دقیقه
            "enforce_password_policy": True,
        },
        ConfigSection.REPORTS.value: {
            "default_report_format": "pdf",  # pdf، excel، html، csv
            "default_chart_type": "bar",  # نمودار ستونی، دایره‌ای، خطی
            "default_report_path": "",  # مسیر خودکار با استفاده از _get_default_reports_path() تنظیم می‌شود
            "include_logo": True,
            "include_date": True,
            "include_page_numbers": True,
            "default_page_size": "A4",  # A4، A5، Letter
        },
        ConfigSection.ADVANCED.value: {
            "debug_mode": False,
            "log_level": "info",  # debug، info، warning، error، critical
            "cache_enabled": True,
            "cache_size": 100,  # مگابایت
            "concurrent_connections": 5,
            "timeout": 30,  # ثانیه
            "enable_analytics": False,
        }
    }
    
    def __init__(self):
        """مقداردهی اولیه کلاس Config"""
        self._settings = QSettings()
        self._config = {}
        
        # تنظیم مسیرهای پیش‌فرض
        self.DEFAULT_CONFIG[ConfigSection.DATABASE.value]["data_path"] = self._get_default_data_path()
        self.DEFAULT_CONFIG[ConfigSection.DATABASE.value]["backup_path"] = self._get_default_backup_path()
        self.DEFAULT_CONFIG[ConfigSection.REPORTS.value]["default_report_path"] = self._get_default_reports_path()
        
        # تنظیم فونت پیش‌فرض بر اساس سیستم عامل
        self._set_default_font()
        
        # بارگذاری تنظیمات
        self._load_config()
    
    def _set_default_font(self):
        """تنظیم فونت پیش‌فرض بر اساس سیستم عامل"""
        system = platform.system().lower()
        if system == "windows":
            default_font = "Segoe UI"
        elif system == "darwin":  # macOS
            default_font = "Lucida Grande"
        elif system == "linux":
            default_font = "DejaVu Sans"
        else:
            default_font = "Sans-Serif"
        
        self.DEFAULT_CONFIG[ConfigSection.APPEARANCE.value]["font_family"] = default_font
    
    def _get_default_data_path(self):
        """تعیین مسیر پیش‌فرض داده‌ها"""
        base_path = QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)
        return os.path.join(base_path, "PropertyManagement", "data")
    
    def _get_default_backup_path(self):
        """تعیین مسیر پیش‌فرض نسخه‌های پشتیبان"""
        base_path = QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)
        return os.path.join(base_path, "PropertyManagement", "backups")
    
    def _get_default_reports_path(self):
        """تعیین مسیر پیش‌فرض گزارش‌ها"""
        documents_path = QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation)
        return os.path.join(documents_path, "PropertyManagement", "reports")
    
    def _load_config(self):
        """بارگذاری پیکربندی از تنظیمات ذخیره شده"""
        # ابتدا پیکربندی پیش‌فرض را کپی می‌کنیم
        self._config = self._deep_copy_dict(self.DEFAULT_CONFIG)
        
        # سپس مقادیر ذخیره شده را بارگذاری می‌کنیم
        for section_name, section_defaults in self.DEFAULT_CONFIG.items():
            for key, default_value in section_defaults.items():
                setting_key = f"{section_name}/{key}"
                saved_value = self._settings.value(setting_key, None)
                
                if saved_value is not None:
                    # تبدیل مقدار به نوع داده صحیح
                    if isinstance(default_value, bool):
                        if isinstance(saved_value, str):
                            saved_value = saved_value.lower() in ("true", "1", "yes")
                        else:
                            saved_value = bool(saved_value)
                    elif isinstance(default_value, int):
                        try:
                            saved_value = int(saved_value)
                        except (ValueError, TypeError):
                            saved_value = default_value
                            logger.warning(f"مقدار نامعتبر برای {setting_key}: {saved_value}")
                    elif isinstance(default_value, float):
                        try:
                            saved_value = float(saved_value)
                        except (ValueError, TypeError):
                            saved_value = default_value
                            logger.warning(f"مقدار نامعتبر برای {setting_key}: {saved_value}")
                    
                    # ذخیره مقدار در پیکربندی
                    self._config[section_name][key] = saved_value
    
    def _deep_copy_dict(self, source_dict):
        """ایجاد یک کپی عمیق از دیکشنری"""
        return json.loads(json.dumps(source_dict))
    
    def save_config(self):
        """ذخیره پیکربندی در تنظیمات"""
        for section_name, section_values in self._config.items():
            for key, value in section_values.items():
                setting_key = f"{section_name}/{key}"
                self._settings.setValue(setting_key, value)
    
    def get_value(self, section, key, default=None):
        """
        دریافت یک مقدار از پیکربندی
        
        پارامترها:
            section: بخش پیکربندی (ConfigSection یا رشته)
            key: کلید تنظیم
            default: مقدار پیش‌فرض در صورت عدم وجود کلید
            
        بازگشت:
            مقدار تنظیم یا مقدار پیش‌فرض
        """
        if isinstance(section, ConfigSection):
            section = section.value
        
        if section not in self._config:
            logger.warning(f"بخش نامعتبر: {section}")
            return default
        
        return self._config[section].get(key, default)
    
    def set_value(self, section, key, value):
        """
        تنظیم یک مقدار در پیکربندی
        
        پارامترها:
            section: بخش پیکربندی (ConfigSection یا رشته)
            key: کلید تنظیم
            value: مقدار جدید
        """
        if isinstance(section, ConfigSection):
            section = section.value
        
        if section not in self._config:
            logger.warning(f"بخش نامعتبر: {section}")
            self._config[section] = {}
        
        self._config[section][key] = value
        
        # ذخیره تنظیم
        setting_key = f"{section}/{key}"
        self._settings.setValue(setting_key, value)
    
    def get_section(self, section):
        """
        دریافت تمام مقادیر یک بخش
        
        پارامترها:
            section: بخش پیکربندی (ConfigSection یا رشته)
            
        بازگشت:
            دیکشنری شامل تمام تنظیمات بخش
        """
        if isinstance(section, ConfigSection):
            section = section.value
        
        if section not in self._config:
            logger.warning(f"بخش نامعتبر: {section}")
            return {}
        
        return self._config[section].copy()
    
    def set_section(self, section, values):
        """
        تنظیم مقادیر یک بخش کامل
        
        پارامترها:
            section: بخش پیکربندی (ConfigSection یا رشته)
            values: دیکشنری شامل مقادیر جدید
        """
        if isinstance(section, ConfigSection):
            section = section.value
        
        if not isinstance(values, dict):
            logger.error(f"مقادیر ارسال شده باید دیکشنری باشند: {values}")
            return
        
        # اگر بخش وجود ندارد، آن را ایجاد می‌کنیم
        if section not in self._config:
            self._config[section] = {}
        
        # به‌روزرسانی مقادیر
        for key, value in values.items():
            self._config[section][key] = value
            setting_key = f"{section}/{key}"
            self._settings.setValue(setting_key, value)
    
    def reset_to_defaults(self, section=None):
        """
        بازنشانی تنظیمات به مقادیر پیش‌فرض
        
        پارامترها:
            section: بخشی که باید بازنشانی شود (None برای تمام بخش‌ها)
        """
        if section:
            if isinstance(section, ConfigSection):
                section = section.value
            
            if section in self.DEFAULT_CONFIG:
                self._config[section] = self._deep_copy_dict(self.DEFAULT_CONFIG[section])
                
                # ذخیره مقادیر پیش‌فرض
                for key, value in self._config[section].items():
                    setting_key = f"{section}/{key}"
                    self._settings.setValue(setting_key, value)
            else:
                logger.warning(f"بخش نامعتبر برای بازنشانی: {section}")
        else:
            # بازنشانی تمام تنظیمات
            self._config = self._deep_copy_dict(self.DEFAULT_CONFIG)
            self.save_config()
    
    def export_config(self, file_path):
        """
        صدور تنظیمات به یک فایل JSON
        
        پارامترها:
            file_path: مسیر فایل JSON
            
        بازگشت:
            bool: موفقیت عملیات
        """
        try:
            # ایجاد دایرکتوری‌های مورد نیاز
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
            
            # نوشتن تنظیمات در فایل
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=4, ensure_ascii=False)
            
            logger.info(f"تنظیمات با موفقیت در {file_path} صادر شد")
            return True
        except Exception as e:
            logger.error(f"خطا در صدور تنظیمات: {str(e)}")
            return False
    
    def import_config(self, file_path):
        """
        ورود تنظیمات از یک فایل JSON
        
        پارامترها:
            file_path: مسیر فایل JSON
            
        بازگشت:
            bool: موفقیت عملیات
        """
        try:
            # خواندن تنظیمات از فایل
            with open(file_path, 'r', encoding='utf-8') as f:
                imported_config = json.load(f)
            
            # اعتبارسنجی ساختار
            if not isinstance(imported_config, dict):
                logger.error(f"فایل تنظیمات نامعتبر است: {file_path}")
                return False
            
            # اعمال تنظیمات وارد شده
            for section_name, section_values in imported_config.items():
                if section_name in self._config and isinstance(section_values, dict):
                    for key, value in section_values.items():
                        # بررسی تطابق نوع داده با مقادیر پیش‌فرض
                        if section_name in self.DEFAULT_CONFIG and key in self.DEFAULT_CONFIG[section_name]:
                            default_value = self.DEFAULT_CONFIG[section_name][key]
                            if isinstance(default_value, bool) and not isinstance(value, bool):
                                if isinstance(value, str):
                                    value = value.lower() in ("true", "1", "yes")
                                else:
                                    value = bool(value)
                            elif isinstance(default_value, int) and not isinstance(value, int):
                                try:
                                    value = int(value)
                                except (ValueError, TypeError):
                                    logger.warning(f"مقدار نامعتبر برای {section_name}/{key}: {value}")
                                    continue
                            elif isinstance(default_value, float) and not isinstance(value, float):
                                try:
                                    value = float(value)
                                except (ValueError, TypeError):
                                    logger.warning(f"مقدار نامعتبر برای {section_name}/{key}: {value}")
                                    continue
                        
                        # ذخیره مقدار
                        self._config[section_name][key] = value
            
            # ذخیره تنظیمات جدید
            self.save_config()
            
            logger.info(f"تنظیمات با موفقیت از {file_path} وارد شد")
            return True
        except Exception as e:
            logger.error(f"خطا در ورود تنظیمات: {str(e)}")
            return False

# نمونه تکی از کلاس Config
config_manager = Config() 