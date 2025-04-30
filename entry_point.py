#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
نقطه ورودی اصلی برنامه مدیریت املاک
این اسکریپت برنامه را راه‌اندازی می‌کند و می‌توان از آن برای ایجاد فایل اجرایی استفاده کرد.
"""

import os
import sys
import traceback
import logging
import argparse

# اضافه کردن مسیر کتابخانه به سیستم
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

def setup_logging(debug=False):
    """تنظیم سیستم ثبت وقایع (لاگینگ)"""
    log_level = logging.DEBUG if debug else logging.INFO
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=log_level, format=log_format)

def parse_arguments():
    """تجزیه آرگومان‌های خط فرمان"""
    parser = argparse.ArgumentParser(description='سیستم مدیریت املاک')
    parser.add_argument('--debug', action='store_true', help='فعال‌سازی حالت اشکال‌یابی')
    parser.add_argument('--no-splash', action='store_true', help='عدم نمایش صفحه آغازین')
    parser.add_argument('--style', type=str, help='نام استایل رابط کاربری (مثلاً Fusion)')
    parser.add_argument('--data-path', type=str, help='مسیر پایه ذخیره داده‌ها')
    parser.add_argument('--version', action='store_true', help='نمایش نسخه برنامه و خروج')
    return parser.parse_args()

def main():
    """تابع اصلی برنامه"""
    # تجزیه آرگومان‌های خط فرمان
    args = parse_arguments()
    
    # تنظیم لاگینگ
    setup_logging(args.debug)
    
    # نمایش نسخه برنامه و خروج اگر درخواست شده باشد
    if args.version:
        try:
            from property_management import __version__
            print(f"سیستم مدیریت املاک نسخه {__version__}")
            return 0
        except ImportError:
            print("خطا در بارگذاری اطلاعات نسخه")
            return 1
    
    # تنظیم متغیرهای محیطی بر اساس آرگومان‌ها
    if args.style:
        os.environ["PROPERTY_MANAGEMENT_STYLE"] = args.style
    
    if args.no_splash:
        os.environ["PROPERTY_MANAGEMENT_NO_SPLASH"] = "1"
    
    if args.data_path:
        os.environ["PROPERTY_MANAGEMENT_DATA_PATH"] = args.data_path
    
    if args.debug:
        os.environ["PROPERTY_MANAGEMENT_DEBUG"] = "1"
    
    # راه‌اندازی برنامه اصلی
    try:
        from property_management.main import main as app_main
        return app_main()
    except ImportError as e:
        print(f"خطا در بارگذاری برنامه: {e}")
        traceback.print_exc()
        return 1
    except Exception as e:
        print(f"خطا در اجرای برنامه: {e}")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main()) 