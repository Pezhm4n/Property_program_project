"""
ماژول تست توابع چارت
این اسکریپت تابع‌های مورد استفاده برای نمودارها در کلاس MockCLib را تست می‌کند
"""

import sys
import os
import logging

# تنظیم لاگر
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# وارد کردن کتابخانه موک مستقیماً
from mock_lib import c_lib

def test_district_chart():
    """تست تابع داده‌های منطقه برای نمودار"""
    logger.info("تست تابع get_district_data_for_chart")
    
    # دریافت تابع داده‌های منطقه
    district_data_func = getattr(c_lib, "get_district_data_for_chart", None)
    
    if district_data_func:
        # گرفتن داده‌ها برای حالت‌های مختلف
        logger.info("فراخوانی تابع با آرگومان‌های مختلف")
        
        # فراخوانی تابع برگشتی از getattr
        func = district_data_func
        df_all = func('all', 'all')
        df_residential = func('residential', 'all')
        df_commercial = func('commercial', 'sale')
        
        # نمایش اطلاعات داده‌ها
        print(f"داده‌های همه انواع ملک: {df_all.shape[0]} سطر، ستون‌ها: {df_all.columns.tolist()}")
        print("نمونه داده‌ها:")
        print(df_all.head(3))
        
        print(f"\nداده‌های املاک مسکونی: {df_residential.shape[0]} سطر")
        print(df_residential.head(2))
        
        print(f"\nداده‌های املاک تجاری فروشی: {df_commercial.shape[0]} سطر")
        print(df_commercial.head(2))
        
        # بررسی کنیم آیا سطر 'Total' در داده‌ها وجود دارد
        if 'District' in df_all.columns and 'Total' in df_all['District'].values:
            print("\nسطر 'Total' در داده‌ها وجود دارد - باید در داشبورد حذف شود")
        else:
            print("\nسطر 'Total' در داده‌ها وجود ندارد")
    else:
        logger.error("تابع داده‌های منطقه برای نمودار یافت نشد")

def test_price_chart():
    """تست تابع داده‌های قیمت برای نمودار"""
    logger.info("تست تابع get_price_data_for_chart")
    
    # دریافت تابع داده‌های قیمت
    price_data_func = getattr(c_lib, "get_price_data_for_chart", None)
    
    if price_data_func:
        # گرفتن داده‌ها برای حالت‌های مختلف
        logger.info("فراخوانی تابع با آرگومان‌های مختلف")
        
        # فراخوانی تابع برگشتی از getattr
        func = price_data_func
        df_all = func('all', 'all')
        df_residential = func('residential', 'all')
        df_commercial = func('commercial', 'sale')
        
        # نمایش اطلاعات داده‌ها
        print(f"داده‌های همه انواع ملک: {df_all.shape[0]} سطر، ستون‌ها: {df_all.columns.tolist()}")
        print("نمونه داده‌ها:")
        print(df_all)
        
        print(f"\nداده‌های املاک مسکونی: {df_residential.shape[0]} سطر")
        print(df_residential.head(2))
        
        print(f"\nداده‌های املاک تجاری فروشی: {df_commercial.shape[0]} سطر")
        print(df_commercial.head(2))
    else:
        logger.error("تابع داده‌های قیمت برای نمودار یافت نشد")

def test_property_count():
    """تست توابع شمارش املاک"""
    logger.info("تست توابع شمارش املاک")
    
    # تست شمارنده‌های هر نوع ملک
    for property_type in ['residential', 'commercial', 'land']:
        count_func_name = f"{property_type}_get_count"
        count_func = getattr(c_lib, count_func_name, None)
        
        if count_func:
            # تست شمارش برای انواع معاملات
            count_all = count_func('all')
            count_sale = count_func('sale')
            count_rent = count_func('rent')
            
            print(f"شمارش املاک {property_type}:")
            print(f"  - همه: {count_all}")
            print(f"  - فروشی: {count_sale}")
            print(f"  - اجاره‌ای: {count_rent}")
        else:
            logger.error(f"تابع شمارش برای {property_type} یافت نشد")

if __name__ == "__main__":
    logger.info("شروع تست توابع نمودار...")
    
    print("\n=== تست داده‌های منطقه برای نمودار ===")
    test_district_chart()
    
    print("\n=== تست داده‌های قیمت برای نمودار ===")
    test_price_chart()
    
    print("\n=== تست توابع شمارش املاک ===")
    test_property_count()
    
    logger.info("تست توابع نمودار به پایان رسید.") 