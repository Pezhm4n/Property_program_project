 #!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
این اسکریپت برای تشخیص و رفع خودکار مشکل کتابخانه DLL استفاده می‌شود.
"""

import os
import sys
import platform
import struct
import subprocess
import time
import ctypes

def get_python_bits():
    """تشخیص 32 یا 64 بیتی بودن پایتون"""
    return struct.calcsize("P") * 8

def check_gcc_installed():
    """بررسی نصب بودن GCC"""
    try:
        result = subprocess.run(['gcc', '--version'], 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE,
                               text=True)
        return result.returncode == 0
    except:
        return False

def create_compilation_script(is_64bit):
    """ایجاد اسکریپت کامپایل مناسب برای معماری سیستم"""
    script_name = "compile_lib_win64.bat" if is_64bit else "compile_lib_win32.bat"
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), script_name)
    
    arch_flag = "-m64" if is_64bit else "-m32"
    
    with open(script_path, 'w') as f:
        f.write(f"""@echo off
echo در حال ساخت کتابخانه property_lib برای ویندوز {"64" if is_64bit else "32"} بیتی...

REM ایجاد دایرکتوری خروجی اگر وجود ندارد
if not exist "lib" mkdir lib

echo در حال کامپایل فایل‌های منبع C...
gcc -c {arch_flag} src/property_lib.c -I include -o property_lib.o
if %ERRORLEVEL% NEQ 0 goto error

gcc -c {arch_flag} src/commercial.c -I include -o commercial.o
if %ERRORLEVEL% NEQ 0 goto error

gcc -c {arch_flag} src/residential.c -I include -o residential.o
if %ERRORLEVEL% NEQ 0 goto error

gcc -c {arch_flag} src/land.c -I include -o land.o
if %ERRORLEVEL% NEQ 0 goto error

gcc -c {arch_flag} src/report.c -I include -o report.o
if %ERRORLEVEL% NEQ 0 goto error

gcc -c {arch_flag} src/data_manager.c -I include -o data_manager.o
if %ERRORLEVEL% NEQ 0 goto error

echo در حال ساخت DLL...
gcc {arch_flag} -shared -o lib/property_lib.dll property_lib.o commercial.o residential.o land.o report.o data_manager.o -Wl,--out-implib,lib/libproperty.a
if %ERRORLEVEL% NEQ 0 goto error

echo در حال پاکسازی فایل‌های موقتی...
del *.o

echo.
echo ساخت کتابخانه با موفقیت انجام شد.
echo کتابخانه {"64" if is_64bit else "32"} بیتی در مسیر lib/property_lib.dll قرار دارد.
goto end

:error
echo خطا در فرآیند کامپایل رخ داد.
exit /b 1

:end
""")
    
    return script_path

def setup_mock_mode():
    """تنظیم برنامه در حالت شبیه‌سازی"""
    # مسیر فایل __init__.py در پکیج bridge
    init_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bridge', '__init__.py')
    
    if os.path.exists(init_file):
        with open(init_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # جایگزینی import
        if "from .property_bridge import" in content:
            modified_content = content.replace(
                "from .property_bridge import", 
                "# استفاده از شبیه‌ساز به جای کتابخانه C\n" +
                "from .mock_lib import c_lib\n\n" +
                "from .property_bridge import"
            )
            
            with open(init_file, 'w', encoding='utf-8') as f:
                f.write(modified_content)
            
            print("✅ حالت شبیه‌سازی با موفقیت تنظیم شد.")
            return True
    
    print("❌ خطا در تنظیم حالت شبیه‌سازی.")
    return False

def check_dll():
    """بررسی وضعیت فایل DLL"""
    # مسیر فایل DLL
    lib_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lib')
    dll_path = os.path.join(lib_dir, 'property_lib.dll')
    
    if not os.path.exists(lib_dir):
        os.makedirs(lib_dir)
        print(f"✅ پوشه {lib_dir} ایجاد شد.")
    
    if os.path.exists(dll_path):
        print(f"✅ فایل DLL در مسیر {dll_path} وجود دارد.")
        
        # تلاش برای بارگیری DLL
        try:
            ctypes.CDLL(dll_path)
            print("✅ فایل DLL با موفقیت بارگیری شد.")
            return True
        except Exception as e:
            print(f"❌ خطا در بارگیری DLL: {str(e)}")
            return False
    else:
        print(f"❌ فایل DLL در مسیر {dll_path} پیدا نشد.")
        return False

def main():
    """تابع اصلی برنامه"""
    print("🔍 بررسی وضعیت کتابخانه DLL برنامه مدیریت املاک...\n")
    
    # بررسی معماری پایتون
    python_bits = get_python_bits()
    print(f"📊 معماری پایتون: {python_bits} بیتی")
    
    # بررسی سیستم عامل
    system = platform.system()
    print(f"💻 سیستم عامل: {system}")
    
    if system != 'Windows':
        print("⚠️ این اسکریپت فقط برای ویندوز طراحی شده است.")
        return
    
    # بررسی وضعیت فعلی DLL
    dll_ok = check_dll()
    
    if dll_ok:
        print("\n✅ کتابخانه DLL به درستی پیکربندی شده است و نیازی به اقدام بیشتر نیست.")
        return
    
    print("\n🔧 در حال تلاش برای رفع مشکل...")
    
    # بررسی GCC
    gcc_installed = check_gcc_installed()
    
    if gcc_installed:
        print("✅ کامپایلر GCC یافت شد.")
        
        # ایجاد اسکریپت کامپایل
        script_path = create_compilation_script(python_bits == 64)
        print(f"✅ اسکریپت کامپایل در مسیر {script_path} ایجاد شد.")
        
        # اجرای اسکریپت کامپایل
        print("\n🛠️ در حال کامپایل کتابخانه... (ممکن است چند دقیقه طول بکشد)")
        subprocess.run([script_path], shell=True)
        
        # بررسی مجدد DLL
        print("\n🔍 بررسی مجدد وضعیت DLL...")
        dll_ok = check_dll()
        
        if dll_ok:
            print("\n✅ کتابخانه با موفقیت کامپایل و نصب شد.")
            return
        else:
            print("\n⚠️ کامپایل ناموفق بود.")
    else:
        print("❌ کامپایلر GCC یافت نشد.")
    
    # در صورت عدم موفقیت در کامپایل، پیشنهاد حالت شبیه‌سازی
    print("\n⚠️ امکان کامپایل کتابخانه C وجود ندارد.")
    choice = input("🔄 آیا مایلید برنامه را در حالت شبیه‌سازی اجرا کنید؟ (بله/خیر) ")
    
    if choice.lower() in ['بله', 'y', 'yes', 'بلی', 'آره']:
        setup_mock_mode()
        print("\n✅ برنامه برای اجرا در حالت شبیه‌سازی آماده است.")
        print("⚠️ توجه: در این حالت، تمام عملیات مرتبط با کتابخانه C شبیه‌سازی می‌شوند و داده‌ها ذخیره نخواهند شد.")
    else:
        print("\n❌ برنامه بدون کتابخانه C قابل اجرا نیست.")
        print("📋 لطفاً راهنمای عیب‌یابی را در فایل TROUBLESHOOTING.md مطالعه کنید.")

if __name__ == "__main__":
    main()
    print("\n🏁 عملیات پایان یافت.")
    input("برای خروج، کلیدی را فشار دهید...")