"""
تست بسیار ساده توابع نمودار
"""

import sys
import os
import logging
import time

# تنظیم لاگر
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# وارد کردن کتابخانه
from mock_lib import c_lib

def main():
    """تست اصلی"""
    
    logger.info("شروع تست توابع نمودار")
    
    # تست تابع منطقه
    logger.info("تست تابع داده‌های منطقه")
    try:
        district_data = c_lib.get_district_data_for_chart('all', 'all')
        logger.info(f"داده‌های منطقه دریافت شد - نوع: {type(district_data)}")
        time.sleep(0.5)  # تأخیر کوتاه برای جلوگیری از تداخل لاگ‌ها
    except Exception as e:
        logger.error(f"خطا در دریافت داده‌های منطقه: {e}")
    
    # تست تابع قیمت
    logger.info("تست تابع داده‌های قیمت")
    try:
        price_data = c_lib.get_price_data_for_chart('all', 'all')
        logger.info(f"داده‌های قیمت دریافت شد - نوع: {type(price_data)}")
        time.sleep(0.5)  # تأخیر کوتاه برای جلوگیری از تداخل لاگ‌ها
    except Exception as e:
        logger.error(f"خطا در دریافت داده‌های قیمت: {e}")
    
    # تست شمارش
    logger.info("تست توابع شمارش املاک")
    try:
        count = c_lib.residential_get_count('all')
        logger.info(f"شمارش املاک مسکونی: {count}")
        time.sleep(0.5)  # تأخیر کوتاه برای جلوگیری از تداخل لاگ‌ها
    except Exception as e:
        logger.error(f"خطا در شمارش املاک مسکونی: {e}")
    
    logger.info("تست‌ها به پایان رسید")

if __name__ == "__main__":
    main() 