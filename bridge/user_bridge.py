#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
رابط میانی مدیریت کاربران
این ماژول ارتباط بین هسته C برنامه و رابط کاربری گرافیکی را برقرار می‌کند
"""

import os
import sys
import ctypes
import json
import platform
import logging
from datetime import datetime

# تنظیم مسیر برای یافتن هسته C
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
lib_dir = os.path.join(root_dir, 'lib')
data_dir = os.path.join(root_dir, 'data')

# تنظیم لاگر
logging.basicConfig(
    filename=os.path.join(root_dir, 'logs', 'bridge.log'),
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('user_bridge')

# تشخیص سیستم عامل و بارگذاری کتابخانه مناسب
if platform.system() == 'Windows':
    lib_path = os.path.join(lib_dir, 'property_lib.dll')
    if not os.path.exists(lib_path):
        lib_path = os.path.join(root_dir, 'property_lib.dll')
elif platform.system() == 'Linux':
    lib_path = os.path.join(lib_dir, 'libproperty.so')
else:  # MacOS
    lib_path = os.path.join(lib_dir, 'libproperty.dylib')

# لود کردن کتابخانه C
try:
    property_lib = ctypes.CDLL(lib_path)
    logger.info(f"کتابخانه از مسیر {lib_path} با موفقیت بارگذاری شد")
except Exception as e:
    logger.error(f"خطا در بارگذاری کتابخانه از مسیر {lib_path}: {str(e)}")
    # استفاده از کتابخانه جایگزین (Mock)
    logger.info("در حال استفاده از کتابخانه جایگزین (Mock)...")
    from bridge.mock_lib import c_lib as property_lib
    logger.info("کتابخانه جایگزین با موفقیت بارگذاری شد.")

# تعریف ساختارهای C برای استفاده در پایتون
class UserStruct(ctypes.Structure):
    _fields_ = [
        ("username", ctypes.c_char * 50),
        ("password", ctypes.c_char * 100),
        ("fullName", ctypes.c_char * 100),
        ("phoneNumber", ctypes.c_char * 20),
        ("email", ctypes.c_char * 100),
        ("birthDate", ctypes.c_char * 20),
        ("userType", ctypes.c_int),
        ("registrationDate", ctypes.c_char * 20),
        ("lastLoginDate", ctypes.c_char * 20),
        ("isActive", ctypes.c_int),
        ("address", ctypes.c_char * 200)
    ]

# نگاشت نوع کاربر از متن به عدد
user_type_map = {
    "مشتری": 0,
    "مشاور املاک": 1,
    "مدیر": 2
}

# نگاشت معکوس نوع کاربر از عدد به متن
user_type_reverse_map = {
    0: "مشتری",
    1: "مشاور املاک",
    2: "مدیر"
}

def _str_to_bytes(s, max_len=None):
    """تبدیل رشته به بایت‌ها برای استفاده در C"""
    if s is None:
        s = ""
    b = s.encode('utf-8')
    if max_len and len(b) >= max_len:
        b = b[:max_len-1]
    return b

def _bytes_to_str(b):
    """تبدیل بایت‌ها به رشته برای استفاده در پایتون"""
    if b:
        return b.decode('utf-8').rstrip('\0')
    return ""

def initialize():
    """راه‌اندازی سیستم کاربران"""
    if property_lib is None:
        logger.error("کتابخانه بارگذاری نشده است")
        return False
    
    try:
        # تنظیم مسیر داده‌ها
        property_lib.user_set_data_path.argtypes = [ctypes.c_char_p]
        property_lib.user_set_data_path.restype = ctypes.c_int
        
        result = property_lib.user_set_data_path(_str_to_bytes(data_dir))
        if result != 1:
            logger.error(f"خطا در تنظیم مسیر داده‌ها: {data_dir}")
            return False
        
        logger.info("سیستم کاربران با موفقیت راه‌اندازی شد")
        return True
    except Exception as e:
        logger.error(f"خطا در راه‌اندازی سیستم کاربران: {str(e)}")
        return False

def login(username, password):
    """ورود کاربر به سیستم"""
    if property_lib is None:
        logger.error("کتابخانه بارگذاری نشده است")
        return None
    
    try:
        # فراخوانی تابع ورود از کتابخانه C
        property_lib.user_login.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.POINTER(UserStruct)]
        property_lib.user_login.restype = ctypes.c_int
        
        user_data = UserStruct()
        result = property_lib.user_login(
            _str_to_bytes(username, 50),
            _str_to_bytes(password, 100),
            ctypes.byref(user_data)
        )
        
        if result == 1:  # ورود موفق
            # تبدیل داده‌های کاربر به دیکشنری
            user_info = {
                "username": _bytes_to_str(user_data.username),
                "fullName": _bytes_to_str(user_data.fullName),
                "phoneNumber": _bytes_to_str(user_data.phoneNumber),
                "email": _bytes_to_str(user_data.email),
                "birthDate": _bytes_to_str(user_data.birthDate),
                "userType": user_type_reverse_map.get(user_data.userType, "مشتری"),
                "registrationDate": _bytes_to_str(user_data.registrationDate),
                "lastLoginDate": _bytes_to_str(user_data.lastLoginDate),
                "isActive": bool(user_data.isActive),
                "address": _bytes_to_str(user_data.address)
            }
            
            logger.info(f"ورود موفق کاربر: {username}")
            return user_info
        else:  # خطا در ورود
            logger.warning(f"تلاش ناموفق برای ورود با نام کاربری: {username}")
            return None
    except Exception as e:
        logger.error(f"خطا در فرآیند ورود کاربر {username}: {str(e)}")
        return None

def register_user(user_info):
    """ثبت‌نام کاربر جدید"""
    if property_lib is None:
        logger.error("کتابخانه بارگذاری نشده است")
        return False
    
    try:
        # تبدیل اطلاعات کاربر به فرمت مناسب برای C
        user_data = UserStruct()
        
        user_data.username = _str_to_bytes(user_info.get("username", ""), 50)
        user_data.password = _str_to_bytes(user_info.get("password", ""), 100)
        user_data.fullName = _str_to_bytes(user_info.get("name", ""), 100)
        user_data.phoneNumber = _str_to_bytes(user_info.get("phone", ""), 20)
        user_data.email = _str_to_bytes(user_info.get("email", ""), 100)
        user_data.birthDate = _str_to_bytes(user_info.get("birthdate", ""), 20)
        
        # تبدیل نوع کاربر از متن به عدد
        user_type_text = user_info.get("user_type", "مشتری")
        user_data.userType = ctypes.c_int(user_type_map.get(user_type_text, 0))
        
        # تاریخ ثبت‌نام و آخرین ورود
        current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        user_data.registrationDate = _str_to_bytes(current_date, 20)
        user_data.lastLoginDate = _str_to_bytes(current_date, 20)
        
        # فعال بودن کاربر
        user_data.isActive = ctypes.c_int(1)
        
        # آدرس
        user_data.address = _str_to_bytes(user_info.get("address", ""), 200)
        
        # فراخوانی تابع ثبت‌نام از کتابخانه C
        property_lib.user_register.argtypes = [ctypes.POINTER(UserStruct)]
        property_lib.user_register.restype = ctypes.c_int
        
        result = property_lib.user_register(ctypes.byref(user_data))
        
        if result == 1:  # ثبت‌نام موفق
            logger.info(f"ثبت‌نام موفق کاربر جدید: {user_info.get('username')}")
            return True
        else:  # خطا در ثبت‌نام
            logger.warning(f"خطا در ثبت‌نام کاربر: {user_info.get('username')}")
            return False
    except Exception as e:
        logger.error(f"خطا در فرآیند ثبت‌نام کاربر {user_info.get('username')}: {str(e)}")
        return False

def change_password(username, old_password, new_password):
    """تغییر رمز عبور کاربر"""
    if property_lib is None:
        logger.error("کتابخانه بارگذاری نشده است")
        return False
    
    try:
        # فراخوانی تابع تغییر رمز عبور از کتابخانه C
        property_lib.user_change_password.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p]
        property_lib.user_change_password.restype = ctypes.c_int
        
        result = property_lib.user_change_password(
            _str_to_bytes(username, 50),
            _str_to_bytes(old_password, 100),
            _str_to_bytes(new_password, 100)
        )
        
        if result == 1:  # تغییر رمز موفق
            logger.info(f"تغییر رمز عبور موفق برای کاربر: {username}")
            return True
        else:  # خطا در تغییر رمز
            logger.warning(f"خطا در تغییر رمز عبور برای کاربر: {username}")
            return False
    except Exception as e:
        logger.error(f"خطا در فرآیند تغییر رمز عبور کاربر {username}: {str(e)}")
        return False

def update_profile(username, user_info):
    """به‌روزرسانی پروفایل کاربر"""
    if property_lib is None:
        logger.error("کتابخانه بارگذاری نشده است")
        return False
    
    try:
        # تبدیل اطلاعات کاربر به فرمت مناسب برای C
        user_data = UserStruct()
        
        user_data.username = _str_to_bytes(username, 50)
        user_data.fullName = _str_to_bytes(user_info.get("name", ""), 100)
        user_data.phoneNumber = _str_to_bytes(user_info.get("phone", ""), 20)
        user_data.email = _str_to_bytes(user_info.get("email", ""), 100)
        user_data.birthDate = _str_to_bytes(user_info.get("birthdate", ""), 20)
        
        # آدرس
        user_data.address = _str_to_bytes(user_info.get("address", ""), 200)
        
        # فراخوانی تابع به‌روزرسانی پروفایل از کتابخانه C
        property_lib.user_update_profile.argtypes = [ctypes.POINTER(UserStruct)]
        property_lib.user_update_profile.restype = ctypes.c_int
        
        result = property_lib.user_update_profile(ctypes.byref(user_data))
        
        if result == 1:  # به‌روزرسانی موفق
            logger.info(f"به‌روزرسانی موفق پروفایل کاربر: {username}")
            return True
        else:  # خطا در به‌روزرسانی
            logger.warning(f"خطا در به‌روزرسانی پروفایل کاربر: {username}")
            return False
    except Exception as e:
        logger.error(f"خطا در فرآیند به‌روزرسانی پروفایل کاربر {username}: {str(e)}")
        return False

def get_user_info(username):
    """دریافت اطلاعات کاربر"""
    if property_lib is None:
        logger.error("کتابخانه بارگذاری نشده است")
        return None
    
    try:
        # فراخوانی تابع دریافت اطلاعات کاربر از کتابخانه C
        property_lib.user_get_info.argtypes = [ctypes.c_char_p, ctypes.POINTER(UserStruct)]
        property_lib.user_get_info.restype = ctypes.c_int
        
        user_data = UserStruct()
        result = property_lib.user_get_info(
            _str_to_bytes(username, 50),
            ctypes.byref(user_data)
        )
        
        if result == 1:  # دریافت موفق
            # تبدیل داده‌های کاربر به دیکشنری
            user_info = {
                "username": _bytes_to_str(user_data.username),
                "fullName": _bytes_to_str(user_data.fullName),
                "phoneNumber": _bytes_to_str(user_data.phoneNumber),
                "email": _bytes_to_str(user_data.email),
                "birthDate": _bytes_to_str(user_data.birthDate),
                "userType": user_type_reverse_map.get(user_data.userType, "مشتری"),
                "registrationDate": _bytes_to_str(user_data.registrationDate),
                "lastLoginDate": _bytes_to_str(user_data.lastLoginDate),
                "isActive": bool(user_data.isActive),
                "address": _bytes_to_str(user_data.address)
            }
            
            logger.info(f"دریافت موفق اطلاعات کاربر: {username}")
            return user_info
        else:  # خطا در دریافت
            logger.warning(f"خطا در دریافت اطلاعات کاربر: {username}")
            return None
    except Exception as e:
        logger.error(f"خطا در فرآیند دریافت اطلاعات کاربر {username}: {str(e)}")
        return None

def get_all_users():
    """دریافت لیست تمام کاربران - مخصوص مدیران سیستم"""
    if property_lib is None:
        logger.error("کتابخانه بارگذاری نشده است")
        return []
    
    try:
        # فراخوانی تابع دریافت تعداد کاربران از کتابخانه C
        property_lib.user_get_count.argtypes = []
        property_lib.user_get_count.restype = ctypes.c_int
        
        user_count = property_lib.user_get_count()
        
        if user_count <= 0:
            logger.info("هیچ کاربری یافت نشد")
            return []
        
        # تعریف آرایه برای ذخیره اطلاعات کاربران
        UserArray = UserStruct * user_count
        users_data = UserArray()
        
        # فراخوانی تابع دریافت همه کاربران از کتابخانه C
        property_lib.user_get_all.argtypes = [ctypes.POINTER(UserStruct), ctypes.c_int]
        property_lib.user_get_all.restype = ctypes.c_int
        
        result = property_lib.user_get_all(users_data, user_count)
        
        if result > 0:  # دریافت موفق
            users_list = []
            
            for i in range(result):
                user_info = {
                    "username": _bytes_to_str(users_data[i].username),
                    "fullName": _bytes_to_str(users_data[i].fullName),
                    "phoneNumber": _bytes_to_str(users_data[i].phoneNumber),
                    "email": _bytes_to_str(users_data[i].email),
                    "birthDate": _bytes_to_str(users_data[i].birthDate),
                    "userType": user_type_reverse_map.get(users_data[i].userType, "مشتری"),
                    "registrationDate": _bytes_to_str(users_data[i].registrationDate),
                    "lastLoginDate": _bytes_to_str(users_data[i].lastLoginDate),
                    "isActive": bool(users_data[i].isActive),
                    "address": _bytes_to_str(users_data[i].address)
                }
                users_list.append(user_info)
            
            logger.info(f"دریافت موفق لیست کاربران: {result} کاربر")
            return users_list
        else:  # خطا در دریافت
            logger.warning("خطا در دریافت لیست کاربران")
            return []
    except Exception as e:
        logger.error(f"خطا در فرآیند دریافت لیست کاربران: {str(e)}")
        return []

def deactivate_user(admin_username, target_username):
    """غیرفعال‌سازی کاربر - فقط برای مدیران سیستم"""
    if property_lib is None:
        logger.error("کتابخانه بارگذاری نشده است")
        return False
    
    try:
        # فراخوانی تابع غیرفعال‌سازی کاربر از کتابخانه C
        property_lib.user_deactivate.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
        property_lib.user_deactivate.restype = ctypes.c_int
        
        result = property_lib.user_deactivate(
            _str_to_bytes(admin_username, 50),
            _str_to_bytes(target_username, 50)
        )
        
        if result == 1:  # غیرفعال‌سازی موفق
            logger.info(f"غیرفعال‌سازی موفق کاربر {target_username} توسط مدیر {admin_username}")
            return True
        else:  # خطا در غیرفعال‌سازی
            logger.warning(f"خطا در غیرفعال‌سازی کاربر {target_username} توسط مدیر {admin_username}")
            return False
    except Exception as e:
        logger.error(f"خطا در فرآیند غیرفعال‌سازی کاربر {target_username}: {str(e)}")
        return False

def activate_user(admin_username, target_username):
    """فعال‌سازی کاربر - فقط برای مدیران سیستم"""
    if property_lib is None:
        logger.error("کتابخانه بارگذاری نشده است")
        return False
    
    try:
        # فراخوانی تابع فعال‌سازی کاربر از کتابخانه C
        property_lib.user_activate.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
        property_lib.user_activate.restype = ctypes.c_int
        
        result = property_lib.user_activate(
            _str_to_bytes(admin_username, 50),
            _str_to_bytes(target_username, 50)
        )
        
        if result == 1:  # فعال‌سازی موفق
            logger.info(f"فعال‌سازی موفق کاربر {target_username} توسط مدیر {admin_username}")
            return True
        else:  # خطا در فعال‌سازی
            logger.warning(f"خطا در فعال‌سازی کاربر {target_username} توسط مدیر {admin_username}")
            return False
    except Exception as e:
        logger.error(f"خطا در فرآیند فعال‌سازی کاربر {target_username}: {str(e)}")
        return False

# راه‌اندازی اولیه سیستم کاربران هنگام بارگذاری ماژول
if property_lib:
    initialize() 