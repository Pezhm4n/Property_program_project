#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
اسکریپت اجرای سریع برنامه مدیریت املاک
این اسکریپت، برنامه مدیریت املاک را مستقیماً از پوشه اصلی پروژه اجرا می‌کند.
"""

import os
import sys
import importlib.util

def main():
    """
    تابع اصلی اجرای برنامه
    """
    # تنظیم مسیر سیستمی برای پیدا کردن ماژول‌های برنامه
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # افزودن مسیر اصلی پروژه به PYTHONPATH
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    # بررسی وجود ماژول entry_point
    entry_point_path = os.path.join(current_dir, "entry_point.py")
    if os.path.exists(entry_point_path):
        try:
            # بارگذاری ماژول entry_point و اجرای تابع main آن
            spec = importlib.util.spec_from_file_location("entry_point", entry_point_path)
            entry_point = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(entry_point)
            return entry_point.main()
        except Exception as e:
            print(f"خطا در اجرای برنامه: {e}")
            import traceback
            traceback.print_exc()
            return 1
    else:
        print(f"خطا: فایل {entry_point_path} پیدا نشد.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 