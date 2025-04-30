#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
مثالی برای استفاده از کتابخانه مدیریت املاک
"""
import sys
import os
import datetime

# افزودن مسیر پروژه به sys.path برای امکان import
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from property_management import (
    PropertyManager,
    ResidentialManager,
    CommercialManager,
    LandManager,
    UserManager
)

def main():
    """
    تابع اصلی برنامه
    """
    print("برنامه مدیریت املاک")
    print("=" * 30)
    
    # نمونه‌سازی از مدیرهای مختلف
    user_manager = UserManager()
    residential_manager = ResidentialManager()
    commercial_manager = CommercialManager()
    land_manager = LandManager()
    
    # ثبت نام یک کاربر
    try:
        result = user_manager.register({
            'username': 'admin',
            'password': 'admin123',
            'fullName': 'مدیر سیستم',
            'email': 'admin@example.com',
            'phone': '09123456789',
            'role': 'admin'
        })
        print(f"ثبت نام کاربر: {'موفق' if result else 'ناموفق'}")
    except Exception as e:
        print(f"خطا در ثبت نام کاربر: {e}")
    
    # ورود به سیستم
    try:
        result = user_manager.login('admin', 'admin123')
        print(f"ورود به سیستم: {'موفق' if result else 'ناموفق'}")
        
        if not result:
            print("کاربر قبلاً ثبت شده است. از اطلاعات موجود استفاده می‌کنیم.")
    except Exception as e:
        print(f"خطا در ورود به سیستم: {e}")
    
    # ثبت چند ملک مسکونی
    try:
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        
        # ثبت ملک مسکونی برای فروش
        residential1 = {
            'district': 'منطقه ۱',
            'buildingAge': 5,
            'areaSize': 120.0,
            'bedrooms': 2,
            'floor': 3,
            'totalFloors': 5,
            'hasElevator': 1,
            'hasParking': 1,
            'hasStorage': 1,
            'sellingPrice': 1000000000.0,
            'ownerName': 'علی محمدی',
            'ownerContact': '09123456789',
            'description': 'آپارتمان دو خوابه نوساز با امکانات کامل',
            'registrationDate': today
        }
        
        result = residential_manager.register_sale('admin', residential1)
        print(f"ثبت ملک مسکونی برای فروش: {'موفق' if result else 'ناموفق'}")
        
        # ثبت ملک مسکونی برای اجاره
        residential2 = {
            'district': 'منطقه ۲',
            'buildingAge': 8,
            'areaSize': 90.0,
            'bedrooms': 1,
            'floor': 2,
            'totalFloors': 4,
            'hasElevator': 0,
            'hasParking': 1,
            'hasStorage': 0,
            'mortgageAmount': 100000000.0,
            'monthlyRentAmount': 3000000.0,
            'ownerName': 'محمد علوی',
            'ownerContact': '09123456780',
            'description': 'آپارتمان یک خوابه با پارکینگ',
            'registrationDate': today
        }
        
        result = residential_manager.register_rental('admin', residential2)
        print(f"ثبت ملک مسکونی برای اجاره: {'موفق' if result else 'ناموفق'}")
    except Exception as e:
        print(f"خطا در ثبت ملک مسکونی: {e}")
    
    # ثبت یک ملک تجاری
    try:
        commercial1 = {
            'district': 'منطقه ۳',
            'buildingAge': 3,
            'areaSize': 150.0,
            'hasParking': 1,
            'commercialType': 'مغازه',
            'sellingPrice': 2000000000.0,
            'ownerName': 'حسین رضایی',
            'ownerContact': '09123456790',
            'description': 'مغازه تجاری نوساز در موقعیت عالی',
            'registrationDate': today
        }
        
        result = commercial_manager.register_sale('admin', commercial1)
        print(f"ثبت ملک تجاری برای فروش: {'موفق' if result else 'ناموفق'}")
    except Exception as e:
        print(f"خطا در ثبت ملک تجاری: {e}")
    
    # ثبت یک زمین
    try:
        land1 = {
            'district': 'منطقه ۴',
            'landType': 'کشاورزی',
            'landArea': 1000.0,
            'distanceToMainRoad': 200.0,
            'hasWell': 1,
            'sellingPrice': 500000000.0,
            'ownerName': 'مجید کریمی',
            'ownerContact': '09123456700',
            'description': 'زمین کشاورزی حاصلخیز با چاه آب',
            'registrationDate': today
        }
        
        result = land_manager.register_sale('admin', land1)
        print(f"ثبت زمین برای فروش: {'موفق' if result else 'ناموفق'}")
    except Exception as e:
        print(f"خطا در ثبت زمین: {e}")
    
    # جستجوی املاک مسکونی
    try:
        print("\nجستجوی املاک مسکونی در منطقه ۱ برای فروش:")
        properties = residential_manager.find_by_district('منطقه ۱', residential_manager.deal_type_sale)
        
        if properties:
            for i, prop in enumerate(properties, 1):
                print(f"{i}. {prop['description']} - قیمت: {prop['sellingPrice']:,} ریال")
        else:
            print("هیچ ملکی یافت نشد.")
        
        print("\nجستجوی املاک مسکونی دارای آسانسور برای فروش:")
        properties = residential_manager.find_with_elevator(residential_manager.deal_type_sale)
        
        if properties:
            for i, prop in enumerate(properties, 1):
                print(f"{i}. {prop['description']} - قیمت: {prop['sellingPrice']:,} ریال")
        else:
            print("هیچ ملکی یافت نشد.")
    except Exception as e:
        print(f"خطا در جستجوی املاک مسکونی: {e}")
    
    # جستجوی املاک تجاری
    try:
        print("\nجستجوی املاک تجاری نوع 'مغازه' برای فروش:")
        properties = commercial_manager.find_by_type('مغازه', commercial_manager.deal_type_sale)
        
        if properties:
            for i, prop in enumerate(properties, 1):
                print(f"{i}. {prop['description']} - قیمت: {prop['sellingPrice']:,} ریال")
        else:
            print("هیچ ملکی یافت نشد.")
    except Exception as e:
        print(f"خطا در جستجوی املاک تجاری: {e}")
    
    # جستجوی زمین
    try:
        print("\nجستجوی زمین‌های دارای چاه برای فروش:")
        properties = land_manager.find_with_well(land_manager.deal_type_sale)
        
        if properties:
            for i, prop in enumerate(properties, 1):
                print(f"{i}. {prop['description']} - قیمت: {prop['sellingPrice']:,} ریال")
        else:
            print("هیچ زمینی یافت نشد.")
    except Exception as e:
        print(f"خطا در جستجوی زمین: {e}")
    
    # دریافت ارزش کل املاک مسکونی
    try:
        total_value = residential_manager.calculate_total_value()
        print(f"\nارزش کل املاک مسکونی برای فروش: {total_value:,} ریال")
    except Exception as e:
        print(f"خطا در محاسبه ارزش کل املاک: {e}")

if __name__ == "__main__":
    main() 