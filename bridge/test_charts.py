"""
ماژول تست توابع نمودار
"""

import sys
import os
import logging
import pandas as pd

# تنظیم لاگر
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# وارد کردن کتابخانه موک مستقیماً
from mock_lib import c_lib

def main():
    """تست اصلی برای داده‌های نمودار"""
    
    print("=== تست داده‌های منطقه و قیمت برای نمودار ===")
    
    # فراخوانی تابع منطقه و چاپ نتایج
    print("\n1. نتایج تابع داده‌های منطقه:\n")
    
    # اجرای تابع داده‌های منطقه
    try:
        district_data = c_lib.get_district_data_for_chart('all', 'all')
        print(f"نوع داده‌های نمودار منطقه: {type(district_data)}")
        
        # اگر دیتافریم پانداس است
        if hasattr(district_data, 'columns'):
            print(f"ستون‌های دیتافریم: {district_data.columns.tolist()}")
            print(f"تعداد سطرها: {len(district_data)}")
            print(f"نمونه داده‌ها:")
            print(district_data.head(3))
            
            # بررسی سطر Total
            if 'District' in district_data.columns and 'Total' in district_data['District'].values:
                print("\nسطر 'Total' در داده‌ها وجود دارد - باید در داشبورد حذف شود")
            else:
                print("\nسطر 'Total' در داده‌ها وجود ندارد")
        else:
            print("داده‌های برگشتی دیتافریم پانداس نیستند")
    except Exception as e:
        print(f"خطا در اجرای تابع داده‌های منطقه: {str(e)}")
    
    # فراخوانی تابع قیمت و چاپ نتایج
    print("\n2. نتایج تابع داده‌های قیمت:\n")
    
    # اجرای تابع داده‌های قیمت
    try:
        price_data = c_lib.get_price_data_for_chart('all', 'all')
        print(f"نوع داده‌های نمودار قیمت: {type(price_data)}")
        
        # اگر دیتافریم پانداس است
        if hasattr(price_data, 'columns'):
            print(f"ستون‌های دیتافریم: {price_data.columns.tolist()}")
            print(f"تعداد سطرها: {len(price_data)}")
            print(f"نمونه داده‌ها:")
            print(price_data)
        else:
            print("داده‌های برگشتی دیتافریم پانداس نیستند")
    except Exception as e:
        print(f"خطا در اجرای تابع داده‌های قیمت: {str(e)}")
    
    # تست تابع‌های شمارش املاک
    print("\n3. نتایج توابع شمارش املاک:\n")
    
    for prop_type in ['residential', 'commercial', 'land']:
        count_func_name = f"{prop_type}_get_count"
        try:
            count_all = getattr(c_lib, count_func_name)('all')
            count_sale = getattr(c_lib, count_func_name)('sale')
            count_rent = getattr(c_lib, count_func_name)('rent')
            
            print(f"شمارش املاک {prop_type}:")
            print(f"  - همه: {count_all}")
            print(f"  - فروش: {count_sale}")
            print(f"  - اجاره: {count_rent}")
        except Exception as e:
            print(f"خطا در تابع شمارش {prop_type}: {str(e)}")

if __name__ == "__main__":
    main() 