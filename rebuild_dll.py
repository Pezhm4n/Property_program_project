#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
اسکریپت بازسازی و کامپایل مجدد DLL برای برنامه مدیریت املاک
این اسکریپت مشکل عدم تطابق معماری DLL را شناسایی و رفع می‌کند
"""

import os
import sys
import shutil
import platform
import struct
import subprocess
import logging
import ctypes
from pathlib import Path

# تنظیم لاگینگ
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)
log_file = log_dir / "rebuild_dll.log"

logging.basicConfig(
    filename=str(log_file),
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("rebuild_dll")

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

def get_python_bits():
    """تشخیص 32 یا 64 بیتی بودن پایتون"""
    return struct.calcsize("P") * 8

def check_compiler():
    """بررسی وجود کامپایلرهای موجود"""
    compilers = {
        'msvc': {
            'name': 'MSVC (Visual C++)',
            'check_cmd': 'cl.exe /?',
            'compile_script': 'compile_lib_win64.bat' if get_python_bits() == 64 else 'compile_lib_win32.bat'
        },
        'gcc': {
            'name': 'GCC (MinGW)',
            'check_cmd': 'gcc --version',
            'compile_script': 'compile_lib_mingw.bat'
        }
    }
    
    available_compilers = []
    
    for key, compiler in compilers.items():
        try:
            subprocess.run(
                compiler['check_cmd'], 
                check=False, 
                shell=True, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE
            )
            logger.info(f"کامپایلر {compiler['name']} یافت شد")
            available_compilers.append((key, compiler))
        except Exception:
            logger.debug(f"کامپایلر {compiler['name']} یافت نشد")
    
    return available_compilers

def clean_obj_files():
    """پاکسازی فایل‌های موقت و قدیمی"""
    obj_dir = Path("obj")
    if obj_dir.exists():
        logger.info("پاکسازی فایل‌های موقت قبلی")
        for file in obj_dir.glob("*.obj"):
            file.unlink()
        for file in obj_dir.glob("*.o"):
            file.unlink()
    else:
        obj_dir.mkdir()
        logger.info("پوشه obj ایجاد شد")

def backup_existing_dll():
    """ایجاد نسخه پشتیبان از DLL موجود"""
    lib_dir = Path("lib")
    lib_dir.mkdir(exist_ok=True)
    
    dll_path = lib_dir / "property_lib.dll"
    if dll_path.exists():
        backup_dir = Path("backups")
        backup_dir.mkdir(exist_ok=True)
        
        backup_path = backup_dir / f"property_lib_backup_{os.getpid()}.dll"
        shutil.copy2(dll_path, backup_path)
        logger.info(f"نسخه پشتیبان DLL در {backup_path} ذخیره شد")
        return True
    return False

def verify_source_files():
    """بررسی وجود فایل‌های منبع"""
    src_dir = Path("src")
    include_dir = Path("include")
    
    if not src_dir.exists():
        logger.error("پوشه src یافت نشد")
        return False
    
    if not include_dir.exists():
        logger.error("پوشه include یافت نشد")
        return False
    
    c_files = list(src_dir.glob("*.c"))
    h_files = list(include_dir.glob("*.h"))
    
    if not c_files:
        logger.error("هیچ فایل .c در پوشه src یافت نشد")
        return False
    
    if not h_files:
        logger.error("هیچ فایل .h در پوشه include یافت نشد")
        return False
    
    logger.info(f"{len(c_files)} فایل .c و {len(h_files)} فایل .h یافت شد")
    return True

def compile_dll_manually():
    """کامپایل کتابخانه به صورت دستی"""
    python_bits = get_python_bits()
    logger.info(f"معماری پایتون: {python_bits} بیتی")
    
    # مسیرهای مورد نیاز
    src_dir = Path("src")
    include_dir = Path("include")
    lib_dir = Path("lib")
    obj_dir = Path("obj")
    
    lib_dir.mkdir(exist_ok=True)
    obj_dir.mkdir(exist_ok=True)
    
    # پاکسازی فایل‌های قبلی
    dll_path = lib_dir / "property_lib.dll"
    if dll_path.exists():
        os.unlink(dll_path)
    
    # لیست فایل‌های منبع
    c_files = list(src_dir.glob("*.c"))
    
    # انتخاب دستور کامپایل مناسب
    if platform.system() == 'Windows':
        try:
            # تلاش با MSVC
            architecture_flag = "x64" if python_bits == 64 else "x86"
            includes = f'/I"{include_dir}"'
            obj_files = []
            
            # کامپایل هر فایل منبع
            for c_file in c_files:
                obj_file = obj_dir / f"{c_file.stem}.obj"
                obj_files.append(str(obj_file))
                
                cmd = f'cl.exe /c /MD /DWIN32 /D_WINDOWS /W3 /nologo {includes} /Fo"{obj_file}" "{c_file}"'
                logger.info(f"کامپایل {c_file.name}")
                
                result = subprocess.run(cmd, shell=True, check=False, 
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                
                if result.returncode != 0:
                    logger.error(f"خطا در کامپایل {c_file.name}: {result.stderr.decode()}")
                    return False
            
            # ساخت DLL
            cmd = f'link.exe /DLL /OUT:"{dll_path}" /MACHINE:{architecture_flag} {" ".join(obj_files)}'
            logger.info("ساخت فایل DLL")
            
            result = subprocess.run(cmd, shell=True, check=False,
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            if result.returncode != 0:
                logger.error(f"خطا در ساخت DLL: {result.stderr.decode()}")
                return False
            
            logger.info(f"DLL با موفقیت ساخته شد: {dll_path}")
            return True
            
        except Exception as e:
            logger.error(f"خطا در کامپایل با MSVC: {e}")
            # اگر MSVC شکست خورد، سعی می‌کنیم با GCC (MinGW)
    
    # تلاش با GCC (MinGW)
    try:
        architecture_flag = "-m64" if python_bits == 64 else "-m32"
        includes = f'-I"{include_dir}"'
        source_files = " ".join([f'"{f}"' for f in c_files])
        
        cmd = f'gcc {architecture_flag} -shared -o "{dll_path}" {includes} {source_files} -Wl,--out-implib,"{lib_dir}/property_lib.a"'
        logger.info("کامپایل با GCC")
        
        result = subprocess.run(cmd, shell=True, check=False,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        if result.returncode != 0:
            logger.error(f"خطا در کامپایل با GCC: {result.stderr.decode()}")
            return False
        
        logger.info(f"DLL با موفقیت با GCC ساخته شد: {dll_path}")
        return True
        
    except Exception as e:
        logger.error(f"خطا در کامپایل با GCC: {e}")
        return False

def compile_with_script(compiler_info):
    """کامپایل با استفاده از اسکریپت موجود"""
    key, compiler = compiler_info
    script_path = Path(compiler['compile_script'])
    
    if not script_path.exists():
        logger.error(f"اسکریپت کامپایل {script_path} یافت نشد!")
        return False
    
    logger.info(f"کامپایل با استفاده از {compiler['name']}")
    
    try:
        result = subprocess.run(
            str(script_path), 
            shell=True, 
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
        
        if result.returncode != 0:
            logger.error(f"خطا در اجرای اسکریپت کامپایل: {result.stdout.decode('utf-8', errors='replace')}")
            return False
        
        logger.info("اسکریپت کامپایل با موفقیت اجرا شد")
        return True
    except Exception as e:
        logger.error(f"خطا در اجرای اسکریپت کامپایل: {e}")
        return False

def verify_dll(dll_path):
    """بررسی صحت DLL کامپایل شده"""
    if not os.path.exists(dll_path):
        logger.error(f"DLL در مسیر {dll_path} یافت نشد")
        return False
    
    # بررسی اندازه فایل
    file_size = os.path.getsize(dll_path)
    if file_size < 1000:  # یک DLL معمولی باید بزرگتر از 1KB باشد
        logger.error(f"DLL خیلی کوچک است ({file_size} بایت). احتمالاً کامپایل ناموفق بوده است.")
        return False
    
    logger.info(f"اندازه DLL: {file_size} بایت")
    
    # بررسی بارگذاری DLL
    try:
        python_bits = get_python_bits()
        logger.info(f"در حال تلاش برای بارگذاری DLL در پایتون {python_bits} بیتی")
        
        dll = ctypes.CDLL(dll_path)
        logger.info("DLL با موفقیت بارگذاری شد")
        
        # سعی در دسترسی به یکی از توابع DLL
        try:
            if hasattr(dll, 'property_set_data_path'):
                logger.info("تابع property_set_data_path در DLL یافت شد")
            elif hasattr(dll, 'user_login'):
                logger.info("تابع user_login در DLL یافت شد")
            elif hasattr(dll, 'residential_register_sale'):
                logger.info("تابع residential_register_sale در DLL یافت شد")
            else:
                logger.warning("توابع استاندارد در DLL یافت نشد، اما DLL قابل بارگذاری است")
        except Exception as e:
            logger.warning(f"نمی‌توان به توابع DLL دسترسی پیدا کرد: {e}")
        
        return True
    except Exception as e:
        logger.error(f"خطا در بارگذاری DLL: {e}")
        return False

def ensure_dll_in_path():
    """اطمینان از کپی DLL در مسیرهای مورد نیاز"""
    dll_path = Path("lib/property_lib.dll")
    
    if not dll_path.exists():
        logger.error("DLL برای کپی کردن یافت نشد")
        return False
    
    # کپی به روت پروژه برای اطمینان
    root_dll = Path("property_lib.dll") 
    shutil.copy2(dll_path, root_dll)
    logger.info(f"DLL به {root_dll} کپی شد")
    
    # اطمینان از فایل dll_ready برای اطلاع به برنامه
    with open("lib/dll_ready", "w") as f:
        f.write("1")
    
    return True

def update_bridge_file():
    """به‌روزرسانی فایل bridge/__init__.py برای استفاده از کتابخانه C واقعی"""
    bridge_init = Path("bridge/__init__.py")
    
    if not bridge_init.exists():
        logger.error("فایل bridge/__init__.py یافت نشد")
        return False
    
    try:
        with open(bridge_init, "r", encoding="utf-8") as f:
            content = f.read()
        
        # آپدیت محتوا برای استفاده از کتابخانه C واقعی
        if "# Use mock_lib instead of real C library" in content:
            content = content.replace(
                "# Use mock_lib instead of real C library\nfrom .mock_lib import c_lib",
                "# Use real C library\nfrom .lib_handler import get_lib_instance\n\n# Get C library instance\nc_lib = get_lib_instance()"
            )
            
            with open(bridge_init, "w", encoding="utf-8") as f:
                f.write(content)
                
            logger.info("فایل bridge/__init__.py به‌روزرسانی شد برای استفاده از کتابخانه C واقعی")
            return True
    except Exception as e:
        logger.error(f"خطا در به‌روزرسانی bridge/__init__.py: {e}")
    
    return False

def update_lib_handler():
    """به‌روزرسانی lib_handler.py برای عدم استفاده از mock_lib"""
    lib_handler = Path("bridge/lib_handler.py")
    
    if not lib_handler.exists():
        logger.error("فایل bridge/lib_handler.py یافت نشد")
        return False
    
    try:
        with open(lib_handler, "r", encoding="utf-8") as f:
            content = f.read()
        
        # مطمئن شویم که حالت mock غیرفعال است
        if "_use_mock = True" in content:
            content = content.replace("_use_mock = True", "_use_mock = False")
            
            with open(lib_handler, "w", encoding="utf-8") as f:
                f.write(content)
            
            logger.info("حالت mock در lib_handler.py غیرفعال شد")
        
        return True
    except Exception as e:
        logger.error(f"خطا در به‌روزرسانی lib_handler.py: {e}")
    
    return False

def main():
    """تابع اصلی برنامه"""
    print_header("بازسازی و کامپایل مجدد DLL")
    logger.info("شروع فرآیند بازسازی DLL")
    
    if not verify_source_files():
        logger.error("فایل‌های منبع مورد نیاز یافت نشدند")
        return 1
    
    # پشتیبان‌گیری از DLL فعلی (اگر وجود دارد)
    backup_existing_dll()
    
    # پاکسازی فایل‌های موقت
    clean_obj_files()
    
    # بررسی کامپایلرهای موجود
    available_compilers = check_compiler()
    
    if not available_compilers:
        logger.error("هیچ کامپایلر مناسبی یافت نشد")
        print("برای کامپایل DLL به یکی از کامپایلرهای زیر نیاز دارید:")
        print("1. Visual C++ Compiler (MSVC) - بخشی از Visual Studio")
        print("2. MinGW-w64 GCC Compiler")
        return 1
    
    # انتخاب کامپایلر
    selected_compiler = None
    
    if len(available_compilers) == 1:
        selected_compiler = available_compilers[0]
        logger.info(f"استفاده از تنها کامپایلر موجود: {selected_compiler[1]['name']}")
    else:
        print("\nکامپایلرهای موجود:")
        for i, (key, compiler) in enumerate(available_compilers):
            print(f"{i+1}. {compiler['name']}")
        
        try:
            choice = int(input("\nشماره کامپایلر را وارد کنید (پیش‌فرض: 1): ") or "1")
            if 1 <= choice <= len(available_compilers):
                selected_compiler = available_compilers[choice-1]
                logger.info(f"استفاده از کامپایلر: {selected_compiler[1]['name']}")
            else:
                selected_compiler = available_compilers[0]
                logger.info(f"انتخاب نامعتبر. استفاده از کامپایلر پیش‌فرض: {selected_compiler[1]['name']}")
        except ValueError:
            selected_compiler = available_compilers[0]
            logger.info(f"ورودی نامعتبر. استفاده از کامپایلر پیش‌فرض: {selected_compiler[1]['name']}")
    
    # کامپایل DLL
    success = False
    
    if selected_compiler[0] == 'msvc':
        logger.info("کامپایل با MSVC")
        success = compile_with_script(selected_compiler)
        if not success:
            logger.warning("کامپایل با اسکریپت MSVC ناموفق بود، تلاش به صورت دستی...")
            success = compile_dll_manually()
    else:
        logger.info("کامپایل با GCC")
        success = compile_with_script(selected_compiler)
        if not success:
            logger.warning("کامپایل با اسکریپت GCC ناموفق بود، تلاش به صورت دستی...")
            success = compile_dll_manually()
    
    if not success:
        logger.error("تمام تلاش‌ها برای کامپایل DLL ناموفق بود")
        return 1
    
    # بررسی صحت DLL
    dll_path = "lib/property_lib.dll"
    if not verify_dll(dll_path):
        logger.error("DLL کامپایل شده قابل استفاده نیست")
        return 1
    
    # اطمینان از وجود DLL در مسیرهای مورد نیاز
    ensure_dll_in_path()
    
    # به‌روزرسانی فایل‌های برنامه برای استفاده از DLL واقعی
    update_bridge_file()
    update_lib_handler()
    
    logger.info("فرآیند بازسازی DLL با موفقیت به پایان رسید")
    print("\nDLL با موفقیت بازسازی شد. اکنون می‌توانید برنامه را با DLL واقعی اجرا کنید.")
    print("برای اجرای برنامه از دستور زیر استفاده کنید:")
    print("    python run.py")
    
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