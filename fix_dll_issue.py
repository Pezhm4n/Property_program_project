 #!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
اسکریپت کمکی برای رفع مشکل کتابخانه DLL در برنامه مدیریت املاک
"""

import os
import sys
import platform
import struct
import ctypes

def get_python_architecture():
    """تشخیص معماری پایتون (32 یا 64 بیتی)"""
    return struct.calcsize("P") * 8

def main():
    """نمایش اطلاعات سیستم و راهنمایی برای رفع مشکل کتابخانه DLL"""
    python_bits = get_python_architecture()
    system = platform.system()
    python_version = platform.python_version()
    
    print("=" * 60)
    print("  راهنمای رفع مشکل کتابخانه DLL برنامه مدیریت املاک")
    print("=" * 60)
    print(f"سیستم عامل: {system}")
    print(f"نسخه پایتون: {python_version}")
    print(f"معماری پایتون: {python_bits} بیتی")
    print("-" * 60)
    
    # بررسی وجود فایل DLL
    lib_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lib')
    dll_path = os.path.join(lib_dir, 'property_lib.dll')
    
    if os.path.exists(dll_path):
        print(f"فایل DLL در مسیر {dll_path} یافت شد.")
        
        # تلاش برای بارگیری DLL
        try:
            ctypes.CDLL(dll_path)
            print("بارگیری کتابخانه DLL موفقیت‌آمیز بود.")
        except Exception as e:
            print(f"خطا در بارگیری DLL: {str(e)}")
            print("\nاین خطا معمولاً به این معنی است که DLL با معماری پایتون شما سازگار نیست.")
            
            if python_bits == 64:
                print("شما از پایتون ۶۴ بیتی استفاده می‌کنید و نیاز به DLL ۶۴ بیتی دارید.")
                print("پیشنهاد می‌شود از فایل compile_lib_win64.bat استفاده کنید.")
            else:
                print("شما از پایتون ۳۲ بیتی استفاده می‌کنید و نیاز به DLL ۳۲ بیتی دارید.")
                print("پیشنهاد می‌شود از فایل compile_lib_win32.bat استفاده کنید.")
    else:
        print(f"فایل DLL در مسیر {dll_path} یافت نشد.")
        print("باید کتابخانه C را کامپایل کنید.")
        
        if python_bits == 64:
            print("شما از پایتون ۶۴ بیتی استفاده می‌کنید و نیاز به DLL ۶۴ بیتی دارید.")
            print("پیشنهاد می‌شود از فایل compile_lib_win64.bat استفاده کنید.")
        else:
            print("شما از پایتون ۳۲ بیتی استفاده می‌کنید و نیاز به DLL ۳۲ بیتی دارید.")
            print("پیشنهاد می‌شود از فایل compile_lib_win32.bat استفاده کنید.")
    
    print("-" * 60)
    print("برای اطلاعات بیشتر و راهنمای کامل، فایل TROUBLESHOOTING.md را مطالعه کنید.")
    print("=" * 60)

if __name__ == "__main__":
    main()
    input("\nبرای خروج، کلیدی را فشار دهید...")