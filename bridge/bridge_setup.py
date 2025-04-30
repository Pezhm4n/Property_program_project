#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
این ماژول برای تنظیم و بارگیری کتابخانه C برنامه مدیریت املاک استفاده می‌شود.
این ماژول به صورت خودکار معماری پایتون را تشخیص داده و کتابخانه مناسب را بارگیری می‌کند.
"""

import os
import sys
import platform
import ctypes
import logging
import struct

# تنظیمات لاگ
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'bridge_setup.log')

logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger('bridge_setup')

def get_python_bits():
    """تشخیص 32 یا 64 بیتی بودن پایتون"""
    return struct.calcsize("P") * 8

def find_and_load_library():
    """پیدا کردن و بارگیری کتابخانه C مناسب"""
    python_bits = get_python_bits()
    logger.info(f"معماری پایتون: {python_bits} بیتی")
    
    system = platform.system()
    logger.info(f"سیستم عامل: {system}")
    
    # مسیر پایه کتابخانه
    lib_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'lib')
    c_lib = None
    
    if system == 'Windows':
        # اسامی کتابخانه برای ویندوز
        if python_bits == 64:
            lib_names = ['property_lib.dll', 'property_lib_64.dll']
        else:
            lib_names = ['property_lib_32.dll', 'property_lib.dll']
            
        # مسیرهای جستجو
        search_paths = [
            lib_dir,  # مسیر lib پروژه
            os.path.dirname(os.path.abspath(sys.executable)),  # کنار اجرایی پایتون
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),  # ریشه پروژه
        ]
        
        for lib_name in lib_names:
            for path in search_paths:
                lib_path = os.path.join(path, lib_name)
                if os.path.exists(lib_path):
                    try:
                        c_lib = ctypes.CDLL(lib_path)
                        logger.info(f"کتابخانه C با موفقیت بارگذاری شد: {lib_path}")
                        return c_lib
                    except Exception as e:
                        logger.warning(f"تلاش برای بارگذاری {lib_path} ناموفق بود: {e}")
        
        # در صورت عدم موفقیت، تلاش برای کامپایل خودکار
        if python_bits == 64:
            compile_script = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'compile_lib_win64.bat')
        else:
            compile_script = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'compile_lib_win32.bat')
            
        if os.path.exists(compile_script):
            logger.info(f"تلاش برای کامپایل خودکار با {compile_script}")
            try:
                import subprocess
                subprocess.call(compile_script, shell=True)
                
                # تلاش مجدد برای بارگیری
                for lib_name in lib_names:
                    lib_path = os.path.join(lib_dir, lib_name)
                    if os.path.exists(lib_path):
                        try:
                            c_lib = ctypes.CDLL(lib_path)
                            logger.info(f"کتابخانه C پس از کامپایل با موفقیت بارگذاری شد: {lib_path}")
                            return c_lib
                        except Exception as e:
                            logger.warning(f"تلاش برای بارگذاری {lib_path} پس از کامپایل ناموفق بود: {e}")
            except Exception as e:
                logger.error(f"خطا در کامپایل خودکار: {e}")
                
    elif system == 'Linux':
        # اسامی کتابخانه برای لینوکس
        lib_names = ['libproperty.so']
        lib_path = os.path.join(lib_dir, lib_names[0])
        try:
            c_lib = ctypes.CDLL(lib_path)
            logger.info(f"کتابخانه C با موفقیت بارگذاری شد: {lib_path}")
            return c_lib
        except Exception as e:
            logger.error(f"خطا در بارگذاری کتابخانه C در لینوکس: {e}")
            
    elif system == 'Darwin':  # macOS
        # اسامی کتابخانه برای مک
        lib_names = ['libproperty.dylib']
        lib_path = os.path.join(lib_dir, lib_names[0])
        try:
            c_lib = ctypes.CDLL(lib_path)
            logger.info(f"کتابخانه C با موفقیت بارگذاری شد: {lib_path}")
            return c_lib
        except Exception as e:
            logger.error(f"خطا در بارگذاری کتابخانه C در مک: {e}")
    
    # در صورت عدم موفقیت
    error_msg = "کتابخانه C پیدا نشد یا قابل بارگذاری نیست. لطفاً فایل TROUBLESHOOTING.md را برای اطلاعات بیشتر مطالعه کنید."
    logger.error(error_msg)
    return None

# تلاش برای بارگیری کتابخانه
c_lib = find_and_load_library()

if __name__ == "__main__":
    if c_lib:
        print("کتابخانه C با موفقیت بارگذاری شد.")
    else:
        print("خطا در بارگذاری کتابخانه C. لطفاً فایل لاگ را بررسی کنید.")
        print(f"فایل لاگ: {log_file}") 