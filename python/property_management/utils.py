#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
توابع کمکی برای سیستم مدیریت املاک

این ماژول شامل توابع کمکی مختلف مورد استفاده در سیستم مدیریت املاک است.
"""

import os
import json
import logging
import datetime
from pathlib import Path
from typing import Dict, Any, Optional


def setup_logging(log_file: str, log_level: str = 'INFO') -> None:
    """تنظیم سیستم گزارش‌دهی
    
    Args:
        log_file: مسیر فایل گزارش
        log_level: سطح گزارش‌دهی
    """
    # تبدیل رشته سطح گزارش‌دهی به ثابت‌های logging
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        numeric_level = logging.INFO
    
    # ایجاد دایرکتوری فایل گزارش اگر وجود ندارد
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # تنظیم پیکربندی logging
    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )


def load_config(config_file: str) -> Dict[str, Any]:
    """بارگذاری فایل پیکربندی
    
    Args:
        config_file: مسیر فایل پیکربندی
        
    Returns:
        دیکشنری حاوی تنظیمات پیکربندی
    """
    # پیکربندی پیش‌فرض
    default_config = {
        "appearance": {
            "theme": "system",  # system, light, dark
            "font_family": "Vazir",
            "font_size": 10,
            "icon_size": "medium"  # small, medium, large
        },
        "locale": {
            "language": "fa_IR",
            "date_format": "yyyy/MM/dd",
            "time_format": "HH:mm:ss",
            "currency": "تومان"
        },
        "paths": {
            "data_dir": "",
            "reports_dir": "",
            "export_dir": "",
            "backup_dir": ""
        },
        "application": {
            "backup_interval_days": 7,
            "auto_save": True,
            "check_updates": True,
            "recent_files_limit": 10
        },
        "security": {
            "require_login": False,
            "session_timeout_minutes": 30,
            "password_expiry_days": 90
        }
    }
    
    # اگر فایل پیکربندی وجود دارد، آن را بارگذاری کن
    config = default_config.copy()
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                loaded_config = json.load(f)
            
            # ادغام پیکربندی بارگذاری شده با پیکربندی پیش‌فرض
            merge_dicts(config, loaded_config)
            logging.info(f"پیکربندی از {config_file} بارگذاری شد")
        except Exception as e:
            logging.error(f"خطا در بارگذاری پیکربندی: {e}")
    else:
        # ایجاد فایل پیکربندی با مقادیر پیش‌فرض
        try:
            os.makedirs(os.path.dirname(config_file), exist_ok=True)
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, ensure_ascii=False, indent=2)
            logging.info(f"فایل پیکربندی پیش‌فرض در {config_file} ایجاد شد")
        except Exception as e:
            logging.error(f"خطا در ایجاد فایل پیکربندی پیش‌فرض: {e}")
    
    return config


def save_config(config: Dict[str, Any], config_file: str) -> bool:
    """ذخیره پیکربندی در فایل
    
    Args:
        config: دیکشنری حاوی تنظیمات پیکربندی
        config_file: مسیر فایل پیکربندی
        
    Returns:
        نتیجه عملیات ذخیره‌سازی
    """
    try:
        os.makedirs(os.path.dirname(config_file), exist_ok=True)
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        logging.info(f"پیکربندی در {config_file} ذخیره شد")
        return True
    except Exception as e:
        logging.error(f"خطا در ذخیره پیکربندی: {e}")
        return False


def merge_dicts(target: Dict[str, Any], source: Dict[str, Any]) -> None:
    """ادغام دو دیکشنری به صورت بازگشتی
    
    این تابع دیکشنری منبع را در دیکشنری هدف ادغام می‌کند.
    برای زیردیکشنری‌ها، به جای جایگزینی کامل، ادغام انجام می‌شود.
    
    Args:
        target: دیکشنری هدف (تغییر می‌کند)
        source: دیکشنری منبع
    """
    for key, value in source.items():
        if key in target and isinstance(target[key], dict) and isinstance(value, dict):
            merge_dicts(target[key], value)
        else:
            target[key] = value


def format_currency(amount: float, currency: str = "تومان") -> str:
    """قالب‌بندی مبلغ به صورت پولی
    
    Args:
        amount: مبلغ
        currency: واحد پول
        
    Returns:
        رشته قالب‌بندی شده
    """
    formatted = "{:,}".format(int(amount))
    return f"{formatted} {currency}"


def create_backup(source_dir: str, backup_dir: str) -> Optional[str]:
    """ایجاد نسخه پشتیبان از دایرکتوری داده‌ها
    
    Args:
        source_dir: دایرکتوری منبع
        backup_dir: دایرکتوری نسخه پشتیبان
        
    Returns:
        مسیر فایل پشتیبان یا None در صورت خطا
    """
    import shutil
    import zipfile
    
    try:
        # ایجاد دایرکتوری پشتیبان اگر وجود ندارد
        os.makedirs(backup_dir, exist_ok=True)
        
        # ایجاد نام فایل پشتیبان با تاریخ و زمان
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"property_management_backup_{timestamp}.zip"
        backup_path = os.path.join(backup_dir, backup_filename)
        
        # ایجاد فایل فشرده
        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(source_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    zipf.write(
                        file_path, 
                        os.path.relpath(file_path, os.path.dirname(source_dir))
                    )
        
        logging.info(f"نسخه پشتیبان در {backup_path} ایجاد شد")
        return backup_path
    except Exception as e:
        logging.error(f"خطا در ایجاد نسخه پشتیبان: {e}")
        return None


def restore_backup(backup_file: str, target_dir: str) -> bool:
    """بازیابی نسخه پشتیبان
    
    Args:
        backup_file: مسیر فایل پشتیبان
        target_dir: دایرکتوری هدف
        
    Returns:
        نتیجه عملیات بازیابی
    """
    import zipfile
    
    try:
        # بررسی وجود فایل پشتیبان
        if not os.path.exists(backup_file):
            logging.error(f"فایل پشتیبان {backup_file} یافت نشد")
            return False
        
        # ایجاد دایرکتوری هدف اگر وجود ندارد
        os.makedirs(target_dir, exist_ok=True)
        
        # استخراج فایل‌ها
        with zipfile.ZipFile(backup_file, 'r') as zipf:
            zipf.extractall(target_dir)
        
        logging.info(f"نسخه پشتیبان از {backup_file} به {target_dir} بازیابی شد")
        return True
    except Exception as e:
        logging.error(f"خطا در بازیابی نسخه پشتیبان: {e}")
        return False


def validate_email(email: str) -> bool:
    """اعتبارسنجی آدرس ایمیل
    
    Args:
        email: آدرس ایمیل
        
    Returns:
        معتبر بودن آدرس ایمیل
    """
    import re
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def validate_phone_number(phone: str) -> bool:
    """اعتبارسنجی شماره تلفن
    
    Args:
        phone: شماره تلفن
        
    Returns:
        معتبر بودن شماره تلفن
    """
    import re
    # الگو برای شماره‌های تلفن ایران (شامل موبایل و ثابت)
    pattern = r"^(0|\+98|98)?9\d{9}$|^0\d{2,3}\d{8}$"
    return bool(re.match(pattern, phone))


def get_current_persian_date() -> str:
    """دریافت تاریخ فعلی شمسی
    
    Returns:
        تاریخ فعلی به صورت شمسی
    """
    from persiantools.jdatetime import JalaliDateTime
    now = JalaliDateTime.now()
    return now.strftime("%Y/%m/%d")


def get_current_persian_datetime() -> str:
    """دریافت تاریخ و زمان فعلی شمسی
    
    Returns:
        تاریخ و زمان فعلی به صورت شمسی
    """
    from persiantools.jdatetime import JalaliDateTime
    now = JalaliDateTime.now()
    return now.strftime("%Y/%m/%d %H:%M:%S")


def convert_to_persian_date(date_str: str, input_format: str = "%Y-%m-%d") -> str:
    """تبدیل تاریخ میلادی به شمسی
    
    Args:
        date_str: رشته تاریخ میلادی
        input_format: قالب تاریخ ورودی
        
    Returns:
        تاریخ شمسی
    """
    from persiantools.jdatetime import JalaliDateTime
    import datetime
    
    try:
        date_obj = datetime.datetime.strptime(date_str, input_format)
        jalali_date = JalaliDateTime.to_jalali(date_obj)
        return jalali_date.strftime("%Y/%m/%d")
    except Exception as e:
        logging.error(f"خطا در تبدیل تاریخ: {e}")
        return date_str


def convert_to_gregorian_date(jalali_date_str: str, input_format: str = "%Y/%m/%d") -> str:
    """تبدیل تاریخ شمسی به میلادی
    
    Args:
        jalali_date_str: رشته تاریخ شمسی
        input_format: قالب تاریخ ورودی
        
    Returns:
        تاریخ میلادی
    """
    from persiantools.jdatetime import JalaliDateTime
    
    try:
        year, month, day = map(int, jalali_date_str.split('/'))
        jalali_date = JalaliDateTime(year, month, day, 0, 0, 0, 0)
        gregorian_date = jalali_date.to_gregorian()
        return gregorian_date.strftime("%Y-%m-%d")
    except Exception as e:
        logging.error(f"خطا در تبدیل تاریخ: {e}")
        return jalali_date_str 