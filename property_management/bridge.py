#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ماژول پل ارتباطی با کتابخانه C

این ماژول مسئول بارگذاری کتابخانه C و ارائه یک رابط پایتونی برای توابع C است.
"""

import os
import sys
import platform
import ctypes
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# مسیرهای احتمالی برای کتابخانه C
def find_library_paths(project_dir):
    """یافتن مسیرهای احتمالی کتابخانه C"""
    if platform.system().lower() == "windows":
        lib_name = "property_lib.dll"
    elif platform.system().lower() == "darwin":
        lib_name = "libproperty.dylib"
    else:
        lib_name = "libproperty.so"
    
    # لیست مسیرهای احتمالی برای کتابخانه
    possible_paths = [
        os.path.join(project_dir, "lib", lib_name),
        os.path.join(project_dir, "bin", lib_name),
        os.path.join(project_dir, lib_name),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib", lib_name),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "bin", lib_name),
    ]
    
    # برای ویندوز، مسیرهای اضافی را بررسی می‌کنیم
    if platform.system().lower() == "windows":
        possible_paths.extend([
            os.path.join(os.environ.get("PROGRAMFILES", "C:\\Program Files"), "Property Management", lib_name),
            os.path.join(os.environ.get("PROGRAMFILES(X86)", "C:\\Program Files (x86)"), "Property Management", lib_name),
            os.path.join(os.environ.get("LOCALAPPDATA", "C:\\Users\\User\\AppData\\Local"), "Property Management", lib_name),
        ])
    
    return possible_paths


def load_library(project_dir=None):
    """بارگذاری کتابخانه C"""
    if project_dir is None:
        # تلاش برای یافتن مسیر پروژه به صورت خودکار
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_dir = os.path.abspath(os.path.join(current_dir, ".."))
    
    logger.info(f"تلاش برای بارگذاری کتابخانه C از مسیر پروژه: {project_dir}")
    
    # یافتن مسیرهای احتمالی کتابخانه
    possible_paths = find_library_paths(project_dir)
    
    # تلاش برای بارگذاری کتابخانه از مسیرهای مختلف
    errors = []
    for lib_path in possible_paths:
        if os.path.exists(lib_path):
            try:
                logger.info(f"تلاش برای بارگذاری کتابخانه از مسیر: {lib_path}")
                library = ctypes.CDLL(lib_path)
                logger.info(f"کتابخانه C با موفقیت از مسیر {lib_path} بارگذاری شد.")
                return library
            except Exception as e:
                error_msg = f"خطا در بارگذاری کتابخانه از مسیر {lib_path}: {str(e)}"
                logger.warning(error_msg)
                errors.append(error_msg)
        else:
            logger.debug(f"مسیر کتابخانه موجود نیست: {lib_path}")
    
    # اگر به اینجا رسیدیم، کتابخانه پیدا نشده است
    error_message = f"خطا: کتابخانه C یافت نشد. لطفاً با اجرای 'compile_lib.py' کتابخانه را کامپایل کنید.\n"
    error_message += "مسیرهای بررسی شده:\n"
    for path in possible_paths:
        error_message += f"  - {path}\n"
    error_message += "\nخطاهای بارگذاری:\n"
    for error in errors:
        error_message += f"  - {error}\n"
    
    logger.error(error_message)
    raise FileNotFoundError(error_message)


class PropertyLibrary:
    """کلاس رابط با کتابخانه C"""
    
    def __init__(self, project_dir=None):
        """مقداردهی اولیه و بارگذاری کتابخانه"""
        self.lib = load_library(project_dir)
        self._setup_function_signatures()
    
    def _setup_function_signatures(self):
        """تنظیم تایپ‌های ورودی و خروجی توابع کتابخانه C"""
        # مثال:
        # self.lib.add_property.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_double]
        # self.lib.add_property.restype = ctypes.c_int
        
        # تنظیم تایپ‌های توابع املاک مسکونی
        self.lib.add_residential_property.argtypes = [
            ctypes.c_char_p,  # id
            ctypes.c_char_p,  # title
            ctypes.c_double,  # price
            ctypes.c_double,  # area
            ctypes.c_int,     # rooms
            ctypes.c_int,     # year_built
            ctypes.c_char_p,  # address
            ctypes.c_char_p   # description
        ]
        self.lib.add_residential_property.restype = ctypes.c_int
        
        self.lib.get_residential_property.argtypes = [ctypes.c_char_p]
        self.lib.get_residential_property.restype = ctypes.c_void_p
        
        self.lib.update_residential_property.argtypes = [
            ctypes.c_char_p,  # id
            ctypes.c_char_p,  # title
            ctypes.c_double,  # price
            ctypes.c_double,  # area
            ctypes.c_int,     # rooms
            ctypes.c_int,     # year_built
            ctypes.c_char_p,  # address
            ctypes.c_char_p   # description
        ]
        self.lib.update_residential_property.restype = ctypes.c_int
        
        self.lib.delete_residential_property.argtypes = [ctypes.c_char_p]
        self.lib.delete_residential_property.restype = ctypes.c_int
        
        # تنظیم تایپ‌های توابع املاک تجاری
        self.lib.add_commercial_property.argtypes = [
            ctypes.c_char_p,  # id
            ctypes.c_char_p,  # title
            ctypes.c_double,  # price
            ctypes.c_double,  # area
            ctypes.c_char_p,  # property_type
            ctypes.c_int,     # floor_count
            ctypes.c_char_p,  # address
            ctypes.c_char_p   # description
        ]
        self.lib.add_commercial_property.restype = ctypes.c_int
        
        self.lib.get_commercial_property.argtypes = [ctypes.c_char_p]
        self.lib.get_commercial_property.restype = ctypes.c_void_p
        
        self.lib.update_commercial_property.argtypes = [
            ctypes.c_char_p,  # id
            ctypes.c_char_p,  # title
            ctypes.c_double,  # price
            ctypes.c_double,  # area
            ctypes.c_char_p,  # property_type
            ctypes.c_int,     # floor_count
            ctypes.c_char_p,  # address
            ctypes.c_char_p   # description
        ]
        self.lib.update_commercial_property.restype = ctypes.c_int
        
        self.lib.delete_commercial_property.argtypes = [ctypes.c_char_p]
        self.lib.delete_commercial_property.restype = ctypes.c_int
        
        # تنظیم تایپ‌های توابع زمین
        self.lib.add_land_property.argtypes = [
            ctypes.c_char_p,  # id
            ctypes.c_char_p,  # title
            ctypes.c_double,  # price
            ctypes.c_double,  # area
            ctypes.c_char_p,  # land_type
            ctypes.c_char_p,  # zoning
            ctypes.c_char_p,  # address
            ctypes.c_char_p   # description
        ]
        self.lib.add_land_property.restype = ctypes.c_int
        
        self.lib.get_land_property.argtypes = [ctypes.c_char_p]
        self.lib.get_land_property.restype = ctypes.c_void_p
        
        self.lib.update_land_property.argtypes = [
            ctypes.c_char_p,  # id
            ctypes.c_char_p,  # title
            ctypes.c_double,  # price
            ctypes.c_double,  # area
            ctypes.c_char_p,  # land_type
            ctypes.c_char_p,  # zoning
            ctypes.c_char_p,  # address
            ctypes.c_char_p   # description
        ]
        self.lib.update_land_property.restype = ctypes.c_int
        
        self.lib.delete_land_property.argtypes = [ctypes.c_char_p]
        self.lib.delete_land_property.restype = ctypes.c_int
        
        # تنظیم تایپ‌های توابع جستجو
        self.lib.search_properties.argtypes = [
            ctypes.c_char_p,  # property_type
            ctypes.c_double,  # min_price
            ctypes.c_double,  # max_price
            ctypes.c_double,  # min_area
            ctypes.c_double,  # max_area
            ctypes.c_char_p,  # location
            ctypes.c_char_p   # keywords
        ]
        self.lib.search_properties.restype = ctypes.c_void_p
        
        # تنظیم تایپ‌های توابع گزارش‌گیری
        self.lib.generate_report.argtypes = [
            ctypes.c_char_p,  # report_type
            ctypes.c_char_p,  # output_path
            ctypes.c_char_p   # params
        ]
        self.lib.generate_report.restype = ctypes.c_int

    # متدهای مربوط به املاک مسکونی
    def add_residential_property(self, prop_id, title, price, area, rooms, year_built, address, description):
        """افزودن یک ملک مسکونی جدید"""
        return self.lib.add_residential_property(
            prop_id.encode('utf-8'),
            title.encode('utf-8'),
            price,
            area,
            rooms,
            year_built,
            address.encode('utf-8'),
            description.encode('utf-8')
        )
    
    def get_residential_property(self, prop_id):
        """بازیابی اطلاعات یک ملک مسکونی با شناسه"""
        result = self.lib.get_residential_property(prop_id.encode('utf-8'))
        if result:
            # پردازش نتیجه و تبدیل به دیکشنری پایتون
            # این بخش باید بر اساس ساختار داده‌ای که کتابخانه C برمی‌گرداند پیاده‌سازی شود
            pass
        return None
    
    def update_residential_property(self, prop_id, title, price, area, rooms, year_built, address, description):
        """به‌روزرسانی یک ملک مسکونی موجود"""
        return self.lib.update_residential_property(
            prop_id.encode('utf-8'),
            title.encode('utf-8'),
            price,
            area,
            rooms,
            year_built,
            address.encode('utf-8'),
            description.encode('utf-8')
        )
    
    def delete_residential_property(self, prop_id):
        """حذف یک ملک مسکونی با شناسه"""
        return self.lib.delete_residential_property(prop_id.encode('utf-8'))

    # متدهای مربوط به املاک تجاری
    def add_commercial_property(self, prop_id, title, price, area, property_type, floor_count, address, description):
        """افزودن یک ملک تجاری جدید"""
        return self.lib.add_commercial_property(
            prop_id.encode('utf-8'),
            title.encode('utf-8'),
            price,
            area,
            property_type.encode('utf-8'),
            floor_count,
            address.encode('utf-8'),
            description.encode('utf-8')
        )
    
    def get_commercial_property(self, prop_id):
        """بازیابی اطلاعات یک ملک تجاری با شناسه"""
        result = self.lib.get_commercial_property(prop_id.encode('utf-8'))
        if result:
            # پردازش نتیجه و تبدیل به دیکشنری پایتون
            pass
        return None
    
    def update_commercial_property(self, prop_id, title, price, area, property_type, floor_count, address, description):
        """به‌روزرسانی یک ملک تجاری موجود"""
        return self.lib.update_commercial_property(
            prop_id.encode('utf-8'),
            title.encode('utf-8'),
            price,
            area,
            property_type.encode('utf-8'),
            floor_count,
            address.encode('utf-8'),
            description.encode('utf-8')
        )
    
    def delete_commercial_property(self, prop_id):
        """حذف یک ملک تجاری با شناسه"""
        return self.lib.delete_commercial_property(prop_id.encode('utf-8'))

    # متدهای مربوط به زمین
    def add_land_property(self, prop_id, title, price, area, land_type, zoning, address, description):
        """افزودن یک زمین جدید"""
        return self.lib.add_land_property(
            prop_id.encode('utf-8'),
            title.encode('utf-8'),
            price,
            area,
            land_type.encode('utf-8'),
            zoning.encode('utf-8'),
            address.encode('utf-8'),
            description.encode('utf-8')
        )
    
    def get_land_property(self, prop_id):
        """بازیابی اطلاعات یک زمین با شناسه"""
        result = self.lib.get_land_property(prop_id.encode('utf-8'))
        if result:
            # پردازش نتیجه و تبدیل به دیکشنری پایتون
            pass
        return None
    
    def update_land_property(self, prop_id, title, price, area, land_type, zoning, address, description):
        """به‌روزرسانی یک زمین موجود"""
        return self.lib.update_land_property(
            prop_id.encode('utf-8'),
            title.encode('utf-8'),
            price,
            area,
            land_type.encode('utf-8'),
            zoning.encode('utf-8'),
            address.encode('utf-8'),
            description.encode('utf-8')
        )
    
    def delete_land_property(self, prop_id):
        """حذف یک زمین با شناسه"""
        return self.lib.delete_land_property(prop_id.encode('utf-8'))

    # متدهای جستجو
    def search_properties(self, property_type, min_price, max_price, min_area, max_area, location, keywords):
        """جستجوی املاک بر اساس معیارهای مختلف"""
        result = self.lib.search_properties(
            property_type.encode('utf-8'),
            min_price,
            max_price,
            min_area,
            max_area,
            location.encode('utf-8'),
            keywords.encode('utf-8')
        )
        if result:
            # پردازش نتیجه و تبدیل به لیست پایتون
            pass
        return []

    # متدهای گزارش‌گیری
    def generate_report(self, report_type, output_path, params=None):
        """تولید گزارش از نوع مشخص شده"""
        params_str = "" if params is None else json.dumps(params)
        return self.lib.generate_report(
            report_type.encode('utf-8'),
            output_path.encode('utf-8'),
            params_str.encode('utf-8')
        )


# نمونه عمومی از کلاس برای استفاده در برنامه
_instance = None

def get_library_instance(project_dir=None):
    """دریافت نمونه واحد از کتابخانه"""
    global _instance
    if _instance is None:
        try:
            _instance = PropertyLibrary(project_dir)
        except Exception as e:
            logger.error(f"خطا در بارگذاری کتابخانه C: {str(e)}")
            raise
    return _instance 