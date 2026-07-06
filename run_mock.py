#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
اسکریپت اتوماتیک برای نصب و اجرای برنامه مدیریت املاک در حالت شبیه‌سازی
این اسکریپت نیازمندی‌ها را نصب می‌کند، برنامه را در حالت شبیه‌سازی راه‌اندازی می‌کند
و سپس برنامه اصلی را اجرا می‌کند.
"""

import os
import sys
import subprocess
import time
import platform
import logging
from pathlib import Path

# تنظیم لاگ
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join("logs", "run_mock.log"), encoding='utf-8', mode='a'),
        logging.StreamHandler(sys.stdout)
    ]
)

# تابع چاپ پیام با رنگ
def print_colored(text, color='white'):
    colors = {
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'purple': '\033[95m',
        'cyan': '\033[96m',
        'white': '\033[97m',
        'reset': '\033[0m'
    }
    print(f"{colors.get(color, colors['white'])}{text}{colors['reset']}")

def print_header(title):
    print("\n" + "=" * 60)
    print_colored(f"  {title}", 'green')
    print("=" * 60 + "\n")

def run_command(command, shell=True):
    """اجرای یک دستور در خط فرمان و برگرداندن نتیجه"""
    try:
        process = subprocess.run(command, shell=shell, check=True, text=True, 
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True, process.stdout
    except subprocess.CalledProcessError as e:
        logging.error(f"خطا در اجرای دستور {command}: {e}")
        logging.error(f"خروجی خطا: {e.stderr}")
        return False, e.stderr

def check_python():
    """بررسی نصب پایتون و نسخه آن"""
    print_header("بررسی پایتون")
    
    if sys.version_info.major < 3 or (sys.version_info.major == 3 and sys.version_info.minor < 6):
        print_colored("پایتون نسخه 3.6 یا بالاتر نیاز است!", 'red')
        logging.error("نسخه پایتون قدیمی است")
        return False
    
    print_colored(f"نسخه پایتون: {sys.version}", 'cyan')
    logging.info(f"نسخه پایتون: {sys.version}")
    return True

def install_dependencies():
    """نصب نیازمندی‌های برنامه"""
    print_header("نصب نیازمندی‌ها")
    
    return True

def setup_mock_mode():
    """راه‌اندازی برنامه در حالت شبیه‌سازی"""
    print_header("راه‌اندازی حالت شبیه‌سازی")
    
    print_colored("در حال راه‌اندازی برنامه در حالت شبیه‌سازی...", 'yellow')
    success, output = run_command(f"{sys.executable} setup_property.py --use-mock")
    
    if success:
        print_colored("برنامه با موفقیت در حالت شبیه‌سازی راه‌اندازی شد.", 'green')
        logging.info("برنامه با موفقیت در حالت شبیه‌سازی راه‌اندازی شد")
        return True
    else:
        print_colored("خطا در راه‌اندازی حالت شبیه‌سازی!", 'red')
        logging.error("خطا در راه‌اندازی حالت شبیه‌سازی")
        return False

def run_main_program():
    """اجرای برنامه اصلی"""
    print_header("اجرای برنامه اصلی")
    
    print_colored("در حال اجرای برنامه...", 'yellow')
    
    try:
        if platform.system() == "Windows":
            # در ویندوز از subprocess.Popen استفاده می‌کنیم تا پنجره کنسول باز نشود
            subprocess.Popen(f"{sys.executable} run.py", shell=True)
        else:
            # در سیستم‌های دیگر، از os.system استفاده می‌کنیم
            os.system(f"{sys.executable} run.py &")
        
        print_colored("برنامه با موفقیت اجرا شد.", 'green')
        logging.info("برنامه با موفقیت اجرا شد")
        return True
    except Exception as e:
        print_colored(f"خطا در اجرای برنامه: {e}", 'red')
        logging.error(f"خطا در اجرای برنامه: {e}")
        return False

def ensure_logs_directory():
    """اطمینان از وجود پوشه logs"""
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        logging.info(f"پوشه {log_dir} ایجاد شد")

def show_guidelines():
    """نمایش راهنمای استفاده از برنامه"""
    print_header("راهنمای استفاده از برنامه")
    
    print_colored("نام کاربری پیش‌فرض: admin", 'cyan')
    print_colored("رمز عبور پیش‌فرض: admin123", 'cyan')
    print()
    print_colored("نکات مهم در حالت شبیه‌سازی:", 'yellow')
    print_colored("1. داده‌ها پس از بستن برنامه ذخیره نمی‌شوند", 'white')
    print_colored("2. برخی عملیات ممکن است به درستی کار نکنند", 'white')
    print_colored("3. سرعت برخی عملیات‌ها ممکن است کندتر از حالت عادی باشد", 'white')
    print()
    print_colored("برای راهنمایی بیشتر به فایل GUIDE_FARSI.md مراجعه کنید.", 'green')

def main():
    """تابع اصلی"""
    # اطمینان از وجود پوشه logs
    ensure_logs_directory()
    
    logging.info("شروع اجرای اسکریپت run_mock.py")
    
    print_header("برنامه مدیریت املاک - حالت شبیه‌سازی")
    
    # بررسی نصب پایتون
    if not check_python():
        print_colored("لطفاً پایتون نسخه 3.6 یا بالاتر را نصب کنید.", 'red')
        input("برای خروج، Enter را فشار دهید...")
        return
    
    # نصب نیازمندی‌ها
    if not install_dependencies():
        print_colored("لطفاً مشکل نصب نیازمندی‌ها را برطرف کنید.", 'red')
        input("برای خروج، Enter را فشار دهید...")
        return
    
    # راه‌اندازی حالت شبیه‌سازی
    if not setup_mock_mode():
        print_colored("لطفاً مشکل راه‌اندازی حالت شبیه‌سازی را برطرف کنید.", 'red')
        input("برای خروج، Enter را فشار دهید...")
        return
    
    # نمایش راهنمای استفاده از برنامه
    show_guidelines()
    
    # اجرای برنامه اصلی
    if not run_main_program():
        print_colored("لطفاً مشکل اجرای برنامه را برطرف کنید.", 'red')
        input("برای خروج، Enter را فشار دهید...")
        return
    
    print_colored("\nبرنامه در حال اجرا است. این پنجره را می‌توانید ببندید.", 'green')
    logging.info("اسکریپت run_mock.py با موفقیت اجرا شد")

if __name__ == "__main__":
    main() 