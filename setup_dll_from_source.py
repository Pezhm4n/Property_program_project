#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اسکریپت تنظیم و کامپایل کتابخانه DLL از کد منبع
این اسکریپت به کاربر کمک می‌کند تا کتابخانه DLL را از کد منبع کامپایل کند
و مشکلات احتمالی را شناسایی و برطرف کند.
"""

import os
import sys
import platform
import subprocess
import ctypes
import shutil
import logging
from datetime import datetime

# تنظیم لاگینگ
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger('setup_dll')

def check_compiler():
    """بررسی وجود کامپایلر MSVC یا MinGW"""
    
    compilers = {
        'msvc': {'command': 'cl.exe', 'name': 'MSVC', 'compile_script': 'compile_lib_win64.bat'},
        'mingw': {'command': 'gcc.exe', 'name': 'MinGW GCC', 'compile_script': 'compile_lib_mingw.bat'}
    }
    
    available_compilers = []
    
    for key, compiler in compilers.items():
        try:
            subprocess.run([compiler['command'], '--version'], 
                          stdout=subprocess.PIPE, 
                          stderr=subprocess.PIPE, 
                          shell=True, 
                          check=False)
            logger.info(f"کامپایلر {compiler['name']} یافت شد.")
            available_compilers.append((key, compiler))
        except Exception:
            logger.debug(f"کامپایلر {compiler['name']} یافت نشد.")
    
    return available_compilers

def check_source_files():
    """بررسی وجود فایل‌های منبع و هدر"""
    src_dir = os.path.join(os.getcwd(), 'src')
    include_dir = os.path.join(os.getcwd(), 'include')
    
    if not os.path.exists(src_dir):
        logger.error("پوشه src یافت نشد!")
        return False
    
    if not os.path.exists(include_dir):
        logger.error("پوشه include یافت نشد!")
        return False
    
    src_files = [f for f in os.listdir(src_dir) if f.endswith('.c')]
    header_files = [f for f in os.listdir(include_dir) if f.endswith('.h')]
    
    if not src_files:
        logger.error("هیچ فایل .c در پوشه src یافت نشد!")
        return False
    
    if not header_files:
        logger.error("هیچ فایل .h در پوشه include یافت نشد!")
        return False
    
    logger.info(f"تعداد {len(src_files)} فایل منبع .c و {len(header_files)} فایل هدر .h یافت شد.")
    return True

def compile_dll(compiler_info):
    """کامپایل DLL با استفاده از اسکریپت مناسب"""
    key, compiler = compiler_info
    script_path = os.path.join(os.getcwd(), compiler['compile_script'])
    
    if not os.path.exists(script_path):
        logger.error(f"اسکریپت کامپایل {compiler['compile_script']} یافت نشد!")
        return False
    
    logger.info(f"در حال کامپایل DLL با استفاده از {compiler['name']}...")
    try:
        process = subprocess.Popen(
            script_path, 
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            shell=True,
            universal_newlines=True,
            bufsize=1
        )
        
        # نمایش خروجی کامپایل به صورت زنده
        for line in process.stdout:
            print(line, end='')
        
        process.wait()
        
        if process.returncode != 0:
            logger.error(f"خطا در کامپایل DLL. کد خطا: {process.returncode}")
            return False
        
        logger.info("کامپایل DLL با موفقیت انجام شد.")
        return True
    except Exception as e:
        logger.error(f"خطا در اجرای اسکریپت کامپایل: {e}")
        return False

def verify_dll(dll_path):
    """بررسی صحت DLL کامپایل شده"""
    if not os.path.exists(dll_path):
        logger.error(f"فایل DLL در مسیر {dll_path} یافت نشد!")
        return False
    
    dll_size = os.path.getsize(dll_path)
    if dll_size == 0:
        logger.error("فایل DLL خالی است!")
        return False
    
    logger.info(f"فایل DLL با اندازه {dll_size} بایت ایجاد شده است.")
    
    # تلاش برای بارگذاری DLL
    try:
        if platform.system() == 'Windows':
            dll = ctypes.WinDLL(dll_path)
        else:
            dll = ctypes.CDLL(dll_path)
        logger.info("فایل DLL با موفقیت بارگذاری شد.")
        return True
    except Exception as e:
        logger.error(f"خطا در بارگذاری DLL: {e}")
        return False

def create_backup(dll_path):
    """ایجاد نسخه پشتیبان از DLL قبلی"""
    if os.path.exists(dll_path) and os.path.getsize(dll_path) > 0:
        backup_dir = os.path.join(os.getcwd(), 'backups')
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = os.path.join(backup_dir, f'property_lib_{timestamp}.dll')
        
        try:
            shutil.copy2(dll_path, backup_path)
            logger.info(f"نسخه پشتیبان از DLL قبلی در {backup_path} ایجاد شد.")
            return True
        except Exception as e:
            logger.error(f"خطا در ایجاد نسخه پشتیبان: {e}")
            return False
    
    return False

def main():
    """تابع اصلی برنامه"""
    logger.info("شروع فرآیند تنظیم و کامپایل کتابخانه DLL...")
    
    # بررسی ساختار پوشه‌ها
    lib_dir = os.path.join(os.getcwd(), 'lib')
    if not os.path.exists(lib_dir):
        os.makedirs(lib_dir)
        logger.info("پوشه lib ایجاد شد.")
    
    tmp_dir = os.path.join(os.getcwd(), 'tmp')
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)
        logger.info("پوشه tmp ایجاد شد.")
    
    # بررسی فایل‌های منبع
    if not check_source_files():
        logger.error("خطا در بررسی فایل‌های منبع و هدر.")
        return 1
    
    # بررسی کامپایلر
    available_compilers = check_compiler()
    if not available_compilers:
        logger.error("هیچ کامپایلر سازگاری (MSVC یا MinGW GCC) یافت نشد.")
        logger.error("لطفاً Visual Studio با ابزارهای ++C یا MinGW را نصب کنید.")
        return 1
    
    # انتخاب کامپایلر
    selected_compiler = None
    if len(available_compilers) == 1:
        selected_compiler = available_compilers[0]
    else:
        print("\nکامپایلرهای در دسترس:")
        for i, (key, compiler) in enumerate(available_compilers):
            print(f"{i+1}. {compiler['name']}")
        
        choice = input("\nلطفاً شماره کامپایلر مورد نظر را وارد کنید: ")
        try:
            index = int(choice) - 1
            if 0 <= index < len(available_compilers):
                selected_compiler = available_compilers[index]
            else:
                logger.error("انتخاب نامعتبر.")
                return 1
        except ValueError:
            logger.error("لطفاً یک عدد صحیح وارد کنید.")
            return 1
    
    logger.info(f"کامپایلر انتخاب شده: {selected_compiler[1]['name']}")
    
    # مسیر DLL
    dll_path = os.path.join(lib_dir, 'property_lib.dll')
    
    # ایجاد نسخه پشتیبان
    create_backup(dll_path)
    
    # کامپایل DLL
    if not compile_dll(selected_compiler):
        logger.error("خطا در کامپایل DLL.")
        return 1
    
    # بررسی صحت DLL
    if not verify_dll(dll_path):
        logger.error("خطا در بررسی صحت DLL.")
        return 1
    
    logger.info("فرآیند تنظیم و کامپایل کتابخانه DLL با موفقیت به پایان رسید.")
    logger.info(f"مسیر فایل DLL: {dll_path}")
    
    # پیشنهاد مرحله بعد
    logger.info("اکنون می‌توانید برنامه اصلی را با استفاده از 'python run.py' یا 'start_app.bat' اجرا کنید.")
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        logger.info("عملیات توسط کاربر لغو شد.")
        sys.exit(1)
    except Exception as e:
        logger.exception(f"خطای پیش‌بینی نشده: {e}")
        sys.exit(1) 