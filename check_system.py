#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
این اسکریپت وضعیت سیستم و کتابخانه DLL را بررسی می‌کند.
"""

import os
import sys
import platform
import ctypes
import struct
import logging
import locale
import subprocess
from pathlib import Path
from datetime import datetime

# تنظیم لاگ
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f"system_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file, encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("system_check")

# رنگ‌های کنسول
class Colors:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    RESET = "\033[0m"

def print_color(text, color):
    """متن را با رنگ نمایش می‌دهد"""
    print(f"{color}{text}{Colors.RESET}")

def print_header(text):
    """هدر نمایش می‌دهد"""
    line = "=" * 50
    print_color(line, Colors.CYAN)
    print_color(f" {text} ".center(50), Colors.CYAN + Colors.BOLD)
    print_color(line, Colors.CYAN)

def check_os():
    """اطلاعات سیستم عامل را بررسی می‌کند"""
    print_header("بررسی سیستم عامل")
    
    system = platform.system()
    if system == "Windows":
        release = platform.release()
        version = platform.version()
        is_64bit = platform.machine().endswith('64')
        
        print_color(f"سیستم عامل: Windows {release}", Colors.GREEN)
        print_color(f"نسخه: {version}", Colors.GREEN)
        print_color(f"معماری: {'64 بیتی' if is_64bit else '32 بیتی'}", Colors.GREEN)
        
        # بررسی زبان سیستم
        loc = locale.getlocale()
        print_color(f"تنظیمات محلی: {loc[0]} - {loc[1]}", Colors.GREEN)
        
        return {"system": system, "release": release, "is_64bit": is_64bit}
    else:
        print_color(f"سیستم عامل: {system}", Colors.YELLOW)
        print_color("هشدار: این برنامه برای ویندوز بهینه‌سازی شده است.", Colors.YELLOW)
        return {"system": system, "is_64bit": platform.machine().endswith('64')}

def get_python_bits():
    """معماری پایتون را بررسی می‌کند"""
    return 64 if sys.maxsize > 2**32 else 32

def check_python():
    """اطلاعات پایتون را بررسی می‌کند"""
    print_header("بررسی پایتون")
    
    version = platform.python_version()
    implementation = platform.python_implementation()
    bits = get_python_bits()
    
    print_color(f"نسخه پایتون: {version}", Colors.GREEN)
    print_color(f"پیاده‌سازی: {implementation}", Colors.GREEN)
    print_color(f"معماری: {bits} بیتی", Colors.GREEN)
    
    # بررسی وابستگی‌های نصب شده
    print("بررسی وابستگی‌های اصلی...")
    
    try:
        import PyQt5
        print_color("PyQt5: نصب شده", Colors.GREEN)
    except ImportError:
        print_color("PyQt5: نصب نشده! (مورد نیاز برای رابط کاربری)", Colors.RED)
    
    try:
        import cffi
        print_color("CFFI: نصب شده", Colors.GREEN)
    except ImportError:
        print_color("CFFI: نصب نشده! (مورد نیاز برای ارتباط با کتابخانه C)", Colors.RED)
    
    return {"version": version, "bits": bits}

def check_compiler():
    """وجود کامپایلرهای مورد نیاز را بررسی می‌کند"""
    print_header("بررسی کامپایلرها")
    
    compilers = {
        "MSVC": False,
        "GCC": False
    }
    
    # بررسی MSVC
    try:
        # امتحان اجرای cl.exe
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        result = subprocess.run(["where", "cl.exe"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=si)
        if result.returncode == 0:
            compilers["MSVC"] = True
            print_color("Visual C++ (MSVC): یافت شد", Colors.GREEN)
            print(f"    مسیر: {result.stdout.decode('utf-8', errors='ignore').strip()}")
        else:
            print_color("Visual C++ (MSVC): یافت نشد", Colors.YELLOW)
            print("    برای استفاده از MSVC، Visual Studio را با گزینه 'Desktop development with C++' نصب کنید.")
    except Exception as e:
        print_color("خطا در بررسی MSVC:", Colors.RED)
        print(f"    {str(e)}")
    
    # بررسی GCC/MinGW
    try:
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        result = subprocess.run(["where", "gcc.exe"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=si)
        if result.returncode == 0:
            compilers["GCC"] = True
            print_color("GCC/MinGW: یافت شد", Colors.GREEN)
            print(f"    مسیر: {result.stdout.decode('utf-8', errors='ignore').strip()}")
            
            # بررسی نسخه GCC
            try:
                version_result = subprocess.run(["gcc", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, startupinfo=si)
                version = version_result.stdout.decode('utf-8', errors='ignore').split('\n')[0]
                print(f"    نسخه: {version}")
            except:
                pass
        else:
            print_color("GCC/MinGW: یافت نشد", Colors.YELLOW)
            print("    برای استفاده از GCC، MinGW یا MinGW-w64 را نصب کنید.")
    except Exception as e:
        print_color("خطا در بررسی GCC/MinGW:", Colors.RED)
        print(f"    {str(e)}")
    
    return compilers

def is_dll_64bit(dll_path):
    """بررسی می‌کند آیا فایل DLL 64 بیتی است یا خیر"""
    try:
        with open(dll_path, 'rb') as f:
            doshdr = f.read(64)
            magic = struct.unpack('H', doshdr[0:2])[0]
            if magic != 0x5A4D:  # 'MZ'
                return None  # Not a valid PE file
            
            pe_offset = struct.unpack('I', doshdr[60:64])[0]
            f.seek(pe_offset)
            pe_header = f.read(6)
            
            if pe_header[0:4] != b'PE\0\0':
                return None  # Not a valid PE file
                
            machine_type = struct.unpack('H', pe_header[4:6])[0]
            return machine_type == 0x8664  # 0x8664 is for x64, 0x014c is for x86
    except Exception as e:
        logger.error(f"خطا در بررسی معماری DLL: {e}")
        return None

def check_dll():
    """وضعیت کتابخانه DLL را بررسی می‌کند"""
    print_header("بررسی کتابخانه DLL")
    
    # مسیرهای احتمالی DLL
    dll_paths = [
        os.path.join("lib", "property_lib.dll"),
        os.path.join(".", "property_lib.dll"),
        os.path.join("..", "lib", "property_lib.dll")
    ]
    
    dll_info = {"found": False, "path": None, "is_64bit": None}
    
    # بررسی وجود DLL
    for path in dll_paths:
        if os.path.exists(path):
            dll_info["found"] = True
            dll_info["path"] = os.path.abspath(path)
            
            # بررسی معماری DLL
            is_64bit = is_dll_64bit(path)
            dll_info["is_64bit"] = is_64bit
            
            size = os.path.getsize(path) / 1024  # به کیلوبایت
            
            print_color(f"کتابخانه DLL یافت شد:", Colors.GREEN)
            print(f"    مسیر: {dll_info['path']}")
            print(f"    اندازه: {size:.2f} KB")
            
            if is_64bit is not None:
                dll_arch = "64 بیتی" if is_64bit else "32 بیتی"
                python_bits = get_python_bits()
                
                print(f"    معماری: {dll_arch}")
                
                if (is_64bit and python_bits == 64) or (not is_64bit and python_bits == 32):
                    print_color("    مطابقت معماری: بله (DLL و پایتون سازگار هستند)", Colors.GREEN)
                else:
                    print_color("    مطابقت معماری: خیر (DLL و پایتون سازگار نیستند)", Colors.RED)
                    print_color(f"    هشدار: DLL {dll_arch} با پایتون {python_bits} بیتی سازگار نیست!", Colors.RED)
            
            break
    
    if not dll_info["found"]:
        print_color("کتابخانه DLL یافت نشد!", Colors.YELLOW)
        print("    لطفاً اسکریپت setup_property.py را اجرا کنید تا کتابخانه DLL کامپایل شود.")
        print("    یا از حالت شبیه‌سازی (mock) استفاده کنید:")
        print("        python setup_property.py --use-mock")
    
    return dll_info

def display_recommendations(os_info, python_info, compilers, dll_info):
    """توصیه‌هایی بر اساس اطلاعات سیستم نمایش می‌دهد"""
    print_header("توصیه‌ها")
    
    has_issues = False
    
    # بررسی سازگاری معماری
    if python_info["bits"] != (64 if os_info.get("is_64bit", False) else 32):
        has_issues = True
        print_color("هشدار: معماری پایتون با معماری سیستم عامل مطابقت ندارد.", Colors.YELLOW)
        print(f"    سیستم عامل: {'64 بیتی' if os_info.get('is_64bit', False) else '32 بیتی'}")
        print(f"    پایتون: {python_info['bits']} بیتی")
        print("    برای بهترین عملکرد، توصیه می‌شود از پایتون با معماری مشابه سیستم عامل استفاده کنید.")
    
    # بررسی DLL
    if dll_info["found"]:
        if dll_info["is_64bit"] is not None and dll_info["is_64bit"] != (python_info["bits"] == 64):
            has_issues = True
            print_color("خطا: معماری DLL با معماری پایتون مطابقت ندارد.", Colors.RED)
            print(f"    DLL: {'64 بیتی' if dll_info['is_64bit'] else '32 بیتی'}")
            print(f"    پایتون: {python_info['bits']} بیتی")
            print("    لطفاً DLL را با معماری مناسب کامپایل کنید:")
            
            if python_info["bits"] == 64:
                print("        compile_lib_win64.bat")
            else:
                print("        compile_lib_win32.bat")
    else:
        has_issues = True
        print_color("هشدار: کتابخانه DLL یافت نشد.", Colors.YELLOW)
        
        # توصیه بر اساس کامپایلرهای موجود
        if compilers["MSVC"]:
            print("    برای کامپایل DLL با MSVC:")
            if python_info["bits"] == 64:
                print("        x64 Native Tools Command Prompt for VS را باز کنید")
                print("        به دایرکتوری پروژه بروید")
                print("        compile_lib_win64.bat را اجرا کنید")
            else:
                print("        x86 Native Tools Command Prompt for VS را باز کنید")
                print("        به دایرکتوری پروژه بروید")
                print("        compile_lib_win32.bat را اجرا کنید")
        elif compilers["GCC"]:
            print("    برای کامپایل DLL با GCC/MinGW:")
            print("        compile_lib_mingw.bat را اجرا کنید")
        else:
            print("    هیچ کامپایلر C مناسبی یافت نشد. لطفاً یکی از موارد زیر را نصب کنید:")
            print("        - Visual Studio با گزینه 'Desktop development with C++'")
            print("        - MinGW-w64")
            print("")
            print("    یا می‌توانید از حالت شبیه‌سازی (mock) استفاده کنید:")
            print("        python setup_property.py --use-mock")
    
    # توصیه کلی
    if not has_issues:
        print_color("سیستم شما آماده برای اجرای برنامه است.", Colors.GREEN)
        print("    برای راه‌اندازی برنامه:")
        print("        python setup_property.py")
        print("        python run.py")
    else:
        print("")
        print("پس از رفع مشکلات، برنامه را با دستورات زیر راه‌اندازی کنید:")
        print("    python setup_property.py")
        print("    python run.py")
        print("")
        print("یا می‌توانید از اسکریپت راه‌اندازی خودکار استفاده کنید:")
        print("    start_app_farsi.bat")

def main():
    """تابع اصلی"""
    try:
        # فعال‌سازی رنگ‌ها در کنسول ویندوز
        if platform.system() == "Windows":
            os.system('color')
            ctypes.windll.kernel32.SetConsoleCP(65001)
            ctypes.windll.kernel32.SetConsoleOutputCP(65001)
        
        print_color("\n*** بررسی وضعیت سیستم برای برنامه مدیریت املاک ***\n", Colors.CYAN + Colors.BOLD)
        
        logger.info("شروع بررسی سیستم")
        
        os_info = check_os()
        print("")
        
        python_info = check_python()
        print("")
        
        compilers = check_compiler()
        print("")
        
        dll_info = check_dll()
        print("")
        
        display_recommendations(os_info, python_info, compilers, dll_info)
        
        logger.info("بررسی سیستم با موفقیت به پایان رسید")
        print("")
        print_color(f"لاگ کامل در: {log_file}", Colors.CYAN)
        
    except Exception as e:
        logger.error(f"خطا در بررسی سیستم: {e}", exc_info=True)
        print_color(f"\nخطا در بررسی سیستم: {e}", Colors.RED)
        print_color(f"لطفاً لاگ را بررسی کنید: {log_file}", Colors.RED)
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 