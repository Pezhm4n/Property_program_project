#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
اسکریپت رفع مشکل DLL برای برنامه مدیریت املاک
این اسکریپت به صورت خودکار مشکل WinError 193 را شناسایی و برطرف می‌کند
"""

import os
import sys
import platform
import struct
import subprocess
import logging
import shutil
import ctypes
from pathlib import Path

# تنظیم لاگینگ
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)
log_file = log_dir / "fix_dll.log"

logging.basicConfig(
    filename=str(log_file),
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("fix_dll")

# اضافه کردن لاگر کنسول
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(levelname)s: %(message)s')
console.setFormatter(formatter)
logger.addHandler(console)

def print_header(title):
    """نمایش هدر با فرمت خاص"""
    print("\n" + "=" * 60)
    print(f" {title} ".center(60, "-"))
    print("=" * 60 + "\n")

def get_python_architecture():
    """تشخیص معماری پایتون (32 یا 64 بیتی)"""
    return 8 * struct.calcsize("P")  # P for pointer size

def check_dll_architecture(dll_path):
    """بررسی معماری فایل DLL"""
    if not os.path.exists(dll_path):
        logger.error(f"فایل DLL در مسیر {dll_path} یافت نشد")
        return None
    
    try:
        with open(dll_path, 'rb') as f:
            # خواندن MZ header
            if f.read(2) != b'MZ':
                logger.error(f"فایل {dll_path} یک فایل اجرایی PE معتبر نیست")
                return None
            
            # حرکت به آفست PE signature
            f.seek(60)
            pe_offset = int.from_bytes(f.read(4), byteorder='little')
            
            # خواندن PE signature
            f.seek(pe_offset)
            if f.read(4) != b'PE\0\0':
                logger.error(f"فایل {dll_path} یک فایل PE معتبر نیست")
                return None
            
            # خواندن Machine field
            machine_type = int.from_bytes(f.read(2), byteorder='little')
            
            if machine_type == 0x014c:  # IMAGE_FILE_MACHINE_I386
                return 32
            elif machine_type == 0x8664:  # IMAGE_FILE_MACHINE_AMD64
                return 64
            else:
                logger.warning(f"نوع معماری ناشناخته: 0x{machine_type:04x}")
                return None
    except Exception as e:
        logger.error(f"خطا در تشخیص معماری DLL: {e}")
        return None

def is_dll_loadable(dll_path):
    """بررسی قابلیت بارگذاری DLL"""
    if not os.path.exists(dll_path):
        return False
    
    try:
        ctypes.CDLL(dll_path)
        return True
    except Exception as e:
        logger.error(f"خطا در بارگذاری DLL: {e}")
        return False

def run_command(command, shell=True):
    """اجرای دستور در خط فرمان"""
    try:
        process = subprocess.run(
            command,
            shell=shell,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        return process.returncode, process.stdout, process.stderr
    except Exception as e:
        logger.error(f"خطا در اجرای دستور {command}: {e}")
        return -1, "", str(e)

def compile_dll():
    """کامپایل DLL با اسکریپت compile_fix.bat"""
    compile_script = Path("compile_fix.bat")
    
    if not compile_script.exists():
        logger.error("فایل compile_fix.bat یافت نشد")
        return False
    
    print("در حال کامپایل DLL با معماری مناسب...")
    logger.info("اجرای اسکریپت compile_fix.bat")
    
    return_code, stdout, stderr = run_command(str(compile_script))
    
    if return_code != 0:
        logger.error(f"خطا در کامپایل DLL: {stderr}")
        return False
    
    print(stdout)
    logger.info("DLL با موفقیت کامپایل شد")
    return True

def check_and_fix_dll():
    """بررسی و رفع مشکل DLL"""
    print_header("بررسی وضعیت DLL")
    
    python_arch = get_python_architecture()
    print(f"معماری پایتون: {python_arch} بیتی")
    logger.info(f"معماری پایتون: {python_arch} بیتی")
    
    # مسیرهای احتمالی DLL
    dll_paths = [
        Path("lib/property_lib.dll"),
        Path("property_lib.dll")
    ]
    
    dll_path = None
    for path in dll_paths:
        if path.exists():
            dll_path = path
            break
    
    if dll_path is None:
        print("فایل DLL یافت نشد. باید آن را کامپایل کنیم.")
        logger.info("فایل DLL یافت نشد")
        return compile_dll()
    
    print(f"DLL یافت شد: {dll_path}")
    
    # بررسی اندازه فایل
    file_size = os.path.getsize(dll_path)
    if file_size < 1000:  # یک DLL معتبر باید بزرگتر از 1KB باشد
        print(f"فایل DLL مشکل دارد (اندازه: {file_size} بایت). نیاز به کامپایل مجدد.")
        logger.warning(f"اندازه DLL خیلی کوچک است: {file_size} بایت")
        return compile_dll()
    
    # بررسی معماری DLL
    dll_arch = check_dll_architecture(dll_path)
    
    if dll_arch is None:
        print("نمی‌توان معماری DLL را تشخیص داد. نیاز به کامپایل مجدد.")
        logger.warning("معماری DLL قابل تشخیص نیست")
        return compile_dll()
    
    print(f"معماری DLL: {dll_arch} بیتی")
    logger.info(f"معماری DLL: {dll_arch} بیتی")
    
    # بررسی تطابق معماری
    if dll_arch != python_arch:
        print(f"عدم تطابق معماری: پایتون {python_arch} بیتی، DLL {dll_arch} بیتی")
        print("نیاز به کامپایل مجدد DLL با معماری مناسب...")
        logger.warning(f"عدم تطابق معماری: پایتون {python_arch} بیتی، DLL {dll_arch} بیتی")
        return compile_dll()
    
    # بررسی قابلیت بارگذاری
    if not is_dll_loadable(dll_path):
        print("DLL نمی‌تواند بارگذاری شود. نیاز به کامپایل مجدد.")
        logger.warning("DLL قابل بارگذاری نیست")
        return compile_dll()
    
    print("DLL با معماری مناسب و قابل بارگذاری است.")
    logger.info("DLL سالم است و نیازی به کامپایل مجدد ندارد")
    return True

def update_bridge_settings():
    """به‌روزرسانی تنظیمات پل ارتباطی برای استفاده از DLL واقعی"""
    print_header("به‌روزرسانی تنظیمات")
    
    # بررسی و به‌روزرسانی lib_handler.py
    lib_handler = Path("bridge/lib_handler.py")
    if lib_handler.exists():
        try:
            with open(lib_handler, "r", encoding="utf-8") as f:
                content = f.read()
            
            # تغییر _use_mock به False
            if "_use_mock = True" in content:
                content = content.replace("_use_mock = True", "_use_mock = False")
                
                with open(lib_handler, "w", encoding="utf-8") as f:
                    f.write(content)
                
                print("فایل lib_handler.py به‌روزرسانی شد.")
                logger.info("حالت mock در lib_handler.py غیرفعال شد")
        except Exception as e:
            logger.error(f"خطا در به‌روزرسانی lib_handler.py: {e}")
    
    # بررسی و به‌روزرسانی bridge/__init__.py
    bridge_init = Path("bridge/__init__.py")
    if bridge_init.exists():
        try:
            with open(bridge_init, "r", encoding="utf-8") as f:
                content = f.read()
            
            if "from .mock_lib import c_lib" in content:
                content = content.replace(
                    "from .mock_lib import c_lib",
                    "from .lib_handler import get_lib_instance\n\n# Get instance of C library\nc_lib = get_lib_instance()"
                )
                
                with open(bridge_init, "w", encoding="utf-8") as f:
                    f.write(content)
                
                print("فایل bridge/__init__.py به‌روزرسانی شد.")
                logger.info("فایل bridge/__init__.py برای استفاده از کتابخانه C واقعی تنظیم شد")
        except Exception as e:
            logger.error(f"خطا در به‌روزرسانی bridge/__init__.py: {e}")

def main():
    """تابع اصلی برنامه"""
    print_header("رفع مشکل DLL برای برنامه مدیریت املاک")
    logger.info("شروع فرآیند رفع مشکل DLL")
    
    # بررسی و رفع مشکل DLL
    if not check_and_fix_dll():
        print("مشکل در رفع خطای DLL. لطفاً لاگ را بررسی کنید.")
        logger.error("مشکل در رفع خطای DLL")
        return 1
    
    # به‌روزرسانی تنظیمات برنامه
    update_bridge_settings()
    
    print_header("فرآیند رفع مشکل با موفقیت انجام شد")
    print("\nبرنامه اکنون آماده استفاده با کتابخانه C واقعی است.")
    print("برای اجرای برنامه از دستور زیر استفاده کنید:")
    print("    python run.py")
    
    logger.info("فرآیند رفع مشکل DLL با موفقیت به پایان رسید")
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        logger.info("عملیات توسط کاربر لغو شد")
        sys.exit(1)
    except Exception as e:
        logger.exception(f"خطای پیش‌بینی نشده: {e}")
        sys.exit(1) 