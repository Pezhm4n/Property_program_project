#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
اسکریپت راه‌اندازی و تنظیم محیط برنامه
این اسکریپت بررسی‌های لازم برای اجرای صحیح برنامه را انجام می‌دهد
و به کاربر کمک می‌کند تا مشکلات احتمالی را حل کند.
"""

import os
import sys
import platform
import ctypes
import subprocess
import logging
import shutil
from pathlib import Path
import struct

# تنظیم لاگر
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('setup')

def header(title):
    """نمایش عنوان به صورت مشخص"""
    print("\n" + "=" * 60)
    print(f" {title} ".center(60, "-"))
    print("=" * 60 + "\n")

def is_admin():
    """بررسی دسترسی مدیریتی"""
    try:
        # در ویندوز
        if platform.system() == 'Windows':
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        # در سیستم‌های Unix-like (Linux, macOS)
        else:
            return os.getuid() == 0
    except Exception:
        return False

def check_python_architecture():
    """بررسی معماری پایتون"""
    arch = platform.architecture()[0]
    logger.info(f"معماری پایتون: {arch}")
    return "64bit" if arch == "64bit" else "32bit"

def check_system_architecture():
    """بررسی معماری سیستم"""
    arch = platform.machine()
    is_64bit = platform.architecture()[0] == '64bit'
    logger.info(f"معماری سیستم: {arch}, {'64-bit' if is_64bit else '32-bit'}")
    return "64bit" if is_64bit else "32bit"

def check_dll(dll_path):
    """بررسی وضعیت فایل DLL"""
    if not os.path.exists(dll_path):
        logger.error(f"فایل DLL در مسیر {dll_path} وجود ندارد.")
        return False, "not_found"
    
    # بررسی معماری فایل DLL
    try:
        # امتحان بارگذاری DLL
        dll = ctypes.CDLL(dll_path)
        logger.info(f"فایل DLL با موفقیت بارگذاری شد: {dll_path}")
        return True, "ok"
    except Exception as e:
        error_msg = str(e)
        logger.error(f"خطا در بارگذاری DLL: {error_msg}")
        
        # بررسی نوع خطا
        if "64-bit" in error_msg and "32-bit" in error_msg:
            logger.error("عدم تطابق معماری: کتابخانه DLL با معماری پایتون سازگار نیست.")
            return False, "arch_mismatch"
        elif "0xc1" in error_msg or "193" in error_msg:
            return False, "invalid_dll"
        else:
            return False, "other_error"

def compile_appropriate_dll():
    """کامپایل فایل DLL مناسب برای معماری سیستم"""
    python_arch = check_python_architecture()
    
    # انتخاب اسکریپت کامپایل مناسب
    if python_arch == "64bit":
        compile_script = "compile_lib_win64.bat"
    else:
        compile_script = "compile_lib_win32.bat"
    
    header(f"کامپایل کتابخانه برای پایتون {python_arch}")
    logger.info(f"در حال اجرای اسکریپت کامپایل: {compile_script}")
    
    try:
        result = subprocess.run(compile_script, shell=True, check=True)
        if result.returncode == 0:
            logger.info("کامپایل با موفقیت انجام شد.")
            return True
        else:
            logger.error("خطا در کامپایل کتابخانه.")
            return False
    except subprocess.CalledProcessError as e:
        logger.error(f"خطا در اجرای اسکریپت کامپایل: {e}")
        return False
    except Exception as e:
        logger.error(f"خطای غیرمنتظره: {e}")
        return False

def check_or_create_bridge_init():
    """بررسی یا ایجاد فایل __init__.py در پوشه bridge"""
    init_path = Path("bridge/__init__.py")
    
    if not init_path.exists():
        logger.info("ایجاد فایل bridge/__init__.py...")
        init_path.parent.mkdir(exist_ok=True)
        
        with open(init_path, "w", encoding="utf-8") as f:
            f.write('''"""
پکیج bridge برای ارتباط بین کد پایتون و کتابخانه C
"""

from .lib_handler import get_lib_instance, set_use_mock
''')
        logger.info("فایل bridge/__init__.py با موفقیت ایجاد شد.")
        return True
    else:
        logger.info("فایل bridge/__init__.py از قبل وجود دارد.")
        return True

def check_lib_handler():
    """بررسی وجود ماژول lib_handler"""
    lib_handler_path = Path("bridge/lib_handler.py")
    
    if not lib_handler_path.exists():
        logger.error("ماژول lib_handler.py یافت نشد!")
        logger.info("در حال ایجاد ماژول lib_handler.py...")
        
        with open(lib_handler_path, "w", encoding="utf-8") as f:
            f.write('''# -*- coding: utf-8 -*-
"""
ماژول مدیریت بارگذاری کتابخانه C
این ماژول مسئول بارگذاری کتابخانه C و فراهم کردن دسترسی به توابع آن است.
"""

import os
import sys
import ctypes
import logging
from pathlib import Path

# تنظیم لاگینگ
logger = logging.getLogger(__name__)

# متغیر سراسری برای تعیین استفاده از کتابخانه مجازی
_use_mock = False
_lib_instance = None

def set_use_mock(use_mock=True):
    """تنظیم استفاده از کتابخانه مجازی"""
    global _use_mock
    _use_mock = use_mock
    logger.info(f"استفاده از کتابخانه مجازی: {'فعال' if use_mock else 'غیرفعال'}")

def find_lib_path():
    """یافتن مسیر کتابخانه C"""
    # مسیر پروژه
    base_dir = Path(__file__).parent.parent
    
    # مسیر‌های احتمالی برای کتابخانه
    possible_paths = [
        base_dir / "lib" / "property_lib.dll",
        base_dir / "lib" / "property_lib_32.dll",
        base_dir / "lib" / "property_lib_64.dll",
    ]
    
    for path in possible_paths:
        if path.exists():
            return str(path.resolve())
    
    return None

def load_c_lib():
    """بارگذاری کتابخانه C"""
    lib_path = find_lib_path()
    
    if not lib_path:
        logger.error("کتابخانه C یافت نشد.")
        return None
    
    try:
        logger.info(f"تلاش برای بارگذاری کتابخانه C: {lib_path}")
        c_lib = ctypes.CDLL(lib_path)
        logger.info("کتابخانه C با موفقیت بارگذاری شد.")
        return c_lib
    except Exception as e:
        logger.error(f"خطا در بارگذاری کتابخانه C: {e}")
        return None

def load_mock_lib():
    """بارگذاری کتابخانه مجازی"""
    logger.info("در حال بارگذاری کتابخانه مجازی...")
    
    try:
        from . import mock_lib
        logger.info("کتابخانه مجازی با موفقیت بارگذاری شد.")
        return mock_lib.c_lib
    except Exception as e:
        logger.error(f"خطا در بارگذاری کتابخانه مجازی: {e}")
        return None

def get_lib_instance():
    """دریافت نمونه کتابخانه مناسب"""
    global _lib_instance
    
    if _lib_instance is not None:
        return _lib_instance
    
    if not _use_mock:
        _lib_instance = load_c_lib()
        
        if _lib_instance is None:
            logger.warning("کتابخانه C بارگذاری نشد، استفاده از کتابخانه مجازی...")
            _lib_instance = load_mock_lib()
    else:
        logger.info("استفاده از کتابخانه مجازی...")
        _lib_instance = load_mock_lib()
    
    return _lib_instance
''')
        logger.info("ماژول lib_handler.py با موفقیت ایجاد شد.")
        return True
    else:
        logger.info("ماژول lib_handler.py از قبل وجود دارد.")
        return True

def run_main_program():
    """اجرای برنامه اصلی"""
    try:
        logger.info("در حال اجرای برنامه اصلی...")
        result = subprocess.run([sys.executable, "main.py"], check=False)
        return result.returncode == 0
    except Exception as e:
        logger.error(f"خطا در اجرای برنامه اصلی: {e}")
        return False

def create_directory_structure():
    """ایجاد ساختار پوشه‌های مورد نیاز"""
    logger.info("ایجاد ساختار پوشه‌های مورد نیاز...")
    
    # لیست پوشه‌ها
    directories = [
        "data", 
        "logs", 
        "lib", 
        "reports", 
        "obj",
        "tmp"
    ]
    
    # ایجاد پوشه‌ها
    for directory in directories:
        path = Path(directory)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            logger.info(f"پوشه {directory} ایجاد شد.")
        else:
            logger.info(f"پوشه {directory} از قبل وجود دارد.")
    
    return True

def check_python_version():
    """بررسی نسخه پایتون"""
    logger.info("بررسی نسخه پایتون...")
    
    required_version = (3, 7)
    current_version = sys.version_info
    
    if current_version.major < required_version[0] or \
       (current_version.major == required_version[0] and current_version.minor < required_version[1]):
        logger.error(f"نسخه پایتون باید حداقل {required_version[0]}.{required_version[1]} باشد.")
        logger.error(f"نسخه فعلی: {current_version.major}.{current_version.minor}.{current_version.micro}")
        return False
    
    logger.info(f"نسخه پایتون: {current_version.major}.{current_version.minor}.{current_version.micro}")
    return True

def install_requirements():
    """نصب کتابخانه‌های مورد نیاز"""
    logger.info("نصب کتابخانه‌های مورد نیاز...")
    
    requirements_file = Path("requirements.txt")
    if not requirements_file.exists():
        logger.error("فایل requirements.txt یافت نشد.")
        return False
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        logger.info("کتابخانه‌های مورد نیاز با موفقیت نصب شدند.")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"خطا در نصب کتابخانه‌ها: {e}")
        return False

def check_dll_architecture():
    """بررسی معماری فایل DLL"""
    logger.info("بررسی معماری فایل DLL...")
    
    # مسیر فایل DLL
    dll_path = Path("lib/property_lib.dll")
    
    # اگر فایل DLL وجود ندارد
    if not dll_path.exists():
        logger.warning("فایل DLL یافت نشد. باید آن را کامپایل کنید.")
        return False
    
    # بررسی اندازه فایل (اگر اندازه صفر باشد، فایل خالی است)
    if dll_path.stat().st_size == 0:
        logger.warning("فایل DLL خالی است و باید مجدداً کامپایل شود.")
        return False
    
    # سعی در بارگذاری DLL
    try:
        ctypes.CDLL(str(dll_path))
        logger.info("فایل DLL با موفقیت بارگذاری شد.")
        return True
    except Exception as e:
        logger.error(f"خطا در بارگذاری DLL: {e}")
        
        # بررسی بیشتر معماری فایل DLL
        try:
            # خواندن 2 بایت اول فایل PE برای بررسی معماری
            with open(dll_path, 'rb') as dll_file:
                dll_data = dll_file.read(2)
                # MZ در ابتدای فایل PE (Windows)
                if dll_data == b'MZ':
                    dll_file.seek(60)
                    header_offset = struct.unpack('<I', dll_file.read(4))[0]
                    dll_file.seek(header_offset + 4)
                    machine_type = struct.unpack('<H', dll_file.read(2))[0]
                    
                    if machine_type == 0x8664:  # AMD64/x64
                        logger.info("فایل DLL برای معماری 64 بیت است.")
                    elif machine_type == 0x014c:  # x86/32-bit
                        logger.info("فایل DLL برای معماری 32 بیت است.")
                    else:
                        logger.warning(f"معماری ناشناخته DLL: {machine_type}")
        except Exception as e:
            logger.error(f"خطا در بررسی معماری DLL: {e}")
        
        # تشخیص معماری پایتون
        is_python_64bit = sys.maxsize > 2**32
        if is_python_64bit:
            logger.info("پایتون شما 64 بیت است. باید از DLL 64 بیتی استفاده کنید.")
            logger.info("اجرای اسکریپت compile_lib_win64.bat توصیه می‌شود.")
        else:
            logger.info("پایتون شما 32 بیت است. باید از DLL 32 بیتی استفاده کنید.")
            logger.info("اجرای اسکریپت compile_lib_win32.bat توصیه می‌شود.")
        
        return False

def compile_dll():
    """کامپایل فایل DLL"""
    logger.info("کامپایل فایل DLL...")
    
    system = platform.system()
    is_64bit = sys.maxsize > 2**32
    
    # انتخاب اسکریپت مناسب برای کامپایل
    if system == 'Windows':
        # انتخاب اسکریپت مناسب بر اساس معماری
        if is_64bit:
            compile_script = "compile_lib_win64.bat"
        else:
            compile_script = "compile_lib_win32.bat"
    else:
        compile_script = "compile_lib.sh"
    
    # بررسی وجود اسکریپت کامپایل
    if not Path(compile_script).exists():
        logger.error(f"اسکریپت کامپایل {compile_script} یافت نشد.")
        return False
    
    try:
        # اجرای اسکریپت کامپایل
        if system == 'Windows':
            result = subprocess.run(compile_script, shell=True)
        else:
            result = subprocess.run(['sh', compile_script])
        
        if result.returncode == 0:
            logger.info("کامپایل DLL با موفقیت انجام شد.")
            return True
        else:
            logger.error(f"خطا در کامپایل DLL. کد خطا: {result.returncode}")
            return False
    except Exception as e:
        logger.error(f"خطا در اجرای اسکریپت کامپایل: {e}")
        return False

def setup_data_files():
    """ایجاد فایل‌های داده اولیه"""
    logger.info("ایجاد فایل‌های داده اولیه...")
    
    # مسیر پوشه داده
    data_dir = Path("data")
    
    # لیست فایل‌های داده اولیه
    data_files = [
        "users.csv",
        "residential_properties.csv",
        "commercial_properties.csv",
        "land_properties.csv"
    ]
    
    for file_name in data_files:
        file_path = data_dir / file_name
        if not file_path.exists():
            # ایجاد فایل خالی
            with open(file_path, "w", encoding="utf-8") as f:
                # اضافه کردن هدر CSV
                if file_name == "users.csv":
                    f.write("username,password,name,lastName,nationalCode,phoneNumber,email,registrationDateTime,lastLoginTime,isAdmin\n")
                elif file_name == "residential_properties.csv":
                    f.write("id,dealType,district,address,ownerPhone,registrationDate,isActive,registeredBy,deleteDate,buildingAge,areaSize,bedrooms,floor,totalFloors,hasElevator,hasParking,hasStorage,sellingPrice,mortgageAmount,monthlyRentAmount,description\n")
                elif file_name == "commercial_properties.csv":
                    f.write("id,dealType,district,address,ownerPhone,registrationDate,isActive,registeredBy,deleteDate,propertyType,buildingAge,areaSize,floor,hasShowcase,isActiveBusiness,sellingPrice,mortgageAmount,monthlyRentAmount,description\n")
                elif file_name == "land_properties.csv":
                    f.write("id,dealType,district,address,ownerPhone,registrationDate,isActive,registeredBy,deleteDate,landType,landArea,distanceToMainRoad,hasWell,sellingPrice,mortgageAmount,monthlyRentAmount,description\n")
            
            logger.info(f"فایل {file_name} ایجاد شد.")
        else:
            logger.info(f"فایل {file_name} از قبل وجود دارد.")
    
    return True

def main():
    """تابع اصلی"""
    logger.info("شروع راه‌اندازی برنامه...")
    
    # بررسی و ایجاد ساختار پوشه‌ها
    create_directory_structure()
    
    # بررسی نسخه پایتون
    if not check_python_version():
        logger.error("نسخه پایتون مناسب نیست. حداقل پایتون 3.7 مورد نیاز است.")
        sys.exit(1)
    
    # نصب کتابخانه‌های مورد نیاز
    install_requirements()
    
    # بررسی و ایجاد فایل‌های داده اولیه
    setup_data_files()
    
    # بررسی و ایجاد فایل __init__.py در پوشه bridge
    check_or_create_bridge_init()
    
    # بررسی معماری DLL
    if not check_dll_architecture():
        # پرسش از کاربر برای کامپایل مجدد
        user_input = input("آیا مایل به کامپایل مجدد DLL هستید؟ (y/n): ").strip().lower()
        if user_input == 'y' or user_input == 'yes':
            compile_dll()
        else:
            logger.info("کامپایل DLL انجام نشد. با خطا مواجه می‌شوید اما از نسخه موک استفاده خواهد شد.")
    
    logger.info("راه‌اندازی برنامه با موفقیت به پایان رسید.")
    print("\nبرنامه آماده استفاده است. می‌توانید از طریق اجرای اسکریپت run.py برنامه را اجرا کنید.")

if __name__ == "__main__":
    main() 