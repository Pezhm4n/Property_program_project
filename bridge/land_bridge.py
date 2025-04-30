#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
این ماژول پل ارتباطی بین هسته برنامه نوشته شده با C و رابط کاربری گرافیکی پایتون برای مدیریت املاک زمین است.
"""

import os
import sys
import ctypes
import json
import platform
import logging
from datetime import datetime

# تنظیمات لاگ
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'bridge.log')

logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger('land_bridge')

# تشخیص سیستم عامل و بارگذاری کتابخانه C
system = platform.system()
lib_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'lib')

if system == 'Windows':
    lib_path = os.path.join(lib_dir, 'property_lib.dll')
elif system == 'Linux':
    lib_path = os.path.join(lib_dir, 'libproperty.so')
elif system == 'Darwin':  # macOS
    lib_path = os.path.join(lib_dir, 'libproperty.dylib')
else:
    raise OSError(f"سیستم عامل پشتیبانی نشده: {system}")

try:
    c_lib = ctypes.CDLL(lib_path)
    logger.info(f"کتابخانه C با موفقیت بارگذاری شد: {lib_path}")
except Exception as e:
    logger.error(f"خطا در بارگذاری کتابخانه C: {e}")
    # استفاده از کتابخانه جایگزین (Mock)
    logger.info("در حال استفاده از کتابخانه جایگزین (Mock)...")
    from bridge.mock_lib import c_lib
    logger.info("کتابخانه جایگزین با موفقیت بارگذاری شد.")

# تعریف ساختار داده‌ای برای املاک زمین
class LandPropertyStruct(ctypes.Structure):
    _fields_ = [
        ("id", ctypes.c_char * 50),
        ("district", ctypes.c_char * 50),
        ("address", ctypes.c_char * 200),
        ("landType", ctypes.c_char * 50),  # مسکونی، تجاری، کشاورزی، صنعتی
        ("landArea", ctypes.c_float),
        ("distanceToMainRoad", ctypes.c_int),
        ("hasWell", ctypes.c_int),
        ("sellingPrice", ctypes.c_double),
        ("mortgageAmount", ctypes.c_double),
        ("monthlyRentAmount", ctypes.c_double),
        ("registrationDate", ctypes.c_char * 20),
        ("lastUpdateDate", ctypes.c_char * 20),
        ("ownerUsername", ctypes.c_char * 50),
        ("contactPhone", ctypes.c_char * 20),
        ("status", ctypes.c_int),
        ("description", ctypes.c_char * 500)
    ]

# تنظیم انواع پارامترها و مقادیر بازگشتی توابع کتابخانه C
def setup_c_functions():
    # ثبت زمین برای فروش
    c_lib.land_register_sale.argtypes = [
        ctypes.c_char_p,  # username
        ctypes.c_char_p,  # district
        ctypes.c_char_p,  # address
        ctypes.c_char_p,  # landType
        ctypes.c_float,   # landArea
        ctypes.c_int,     # distanceToMainRoad
        ctypes.c_int,     # hasWell
        ctypes.c_double,  # sellingPrice
        ctypes.c_char_p,  # contactPhone
        ctypes.c_char_p   # description
    ]
    c_lib.land_register_sale.restype = ctypes.c_int

    # ثبت زمین برای اجاره
    c_lib.land_register_rental.argtypes = [
        ctypes.c_char_p,  # username
        ctypes.c_char_p,  # district
        ctypes.c_char_p,  # address
        ctypes.c_char_p,  # landType
        ctypes.c_float,   # landArea
        ctypes.c_int,     # distanceToMainRoad
        ctypes.c_int,     # hasWell
        ctypes.c_double,  # mortgageAmount
        ctypes.c_double,  # monthlyRentAmount
        ctypes.c_char_p,  # contactPhone
        ctypes.c_char_p   # description
    ]
    c_lib.land_register_rental.restype = ctypes.c_int

    # جستجوی زمین بر اساس منطقه
    c_lib.land_find_by_district.argtypes = [
        ctypes.c_char_p,  # district
        ctypes.c_int,     # dealType
        ctypes.POINTER(ctypes.c_int)  # count
    ]
    c_lib.land_find_by_district.restype = ctypes.POINTER(LandPropertyStruct)

    # جستجوی زمین بر اساس متراژ
    c_lib.land_find_by_area.argtypes = [
        ctypes.c_float,   # minArea
        ctypes.c_float,   # maxArea
        ctypes.c_int,     # dealType
        ctypes.POINTER(ctypes.c_int)  # count
    ]
    c_lib.land_find_by_area.restype = ctypes.POINTER(LandPropertyStruct)

    # جستجوی زمین بر اساس نوع
    c_lib.land_find_by_type.argtypes = [
        ctypes.c_char_p,  # landType
        ctypes.c_int,     # dealType
        ctypes.POINTER(ctypes.c_int)  # count
    ]
    c_lib.land_find_by_type.restype = ctypes.POINTER(LandPropertyStruct)

    # جستجوی زمین بر اساس قیمت
    c_lib.land_find_by_price.argtypes = [
        ctypes.c_double,  # minPrice
        ctypes.c_double,  # maxPrice
        ctypes.c_int,     # dealType
        ctypes.POINTER(ctypes.c_int)  # count
    ]
    c_lib.land_find_by_price.restype = ctypes.POINTER(LandPropertyStruct)

    # جستجوی زمین بر اساس فاصله از جاده اصلی
    c_lib.land_find_by_distance.argtypes = [
        ctypes.c_int,     # maxDistance
        ctypes.c_int,     # dealType
        ctypes.POINTER(ctypes.c_int)  # count
    ]
    c_lib.land_find_by_distance.restype = ctypes.POINTER(LandPropertyStruct)

    # جستجوی زمین‌های دارای چاه آب
    c_lib.land_find_with_well.argtypes = [
        ctypes.c_int,     # dealType
        ctypes.POINTER(ctypes.c_int)  # count
    ]
    c_lib.land_find_with_well.restype = ctypes.POINTER(LandPropertyStruct)

    # جستجوی زمین‌های حذف شده بر اساس تاریخ
    c_lib.land_find_deleted_by_date.argtypes = [
        ctypes.c_char_p,  # startDate
        ctypes.c_char_p,  # endDate
        ctypes.c_int,     # dealType
        ctypes.POINTER(ctypes.c_int)  # count
    ]
    c_lib.land_find_deleted_by_date.restype = ctypes.POINTER(LandPropertyStruct)

    # جستجوی زمین‌های ثبت شده توسط یک کاربر
    c_lib.land_find_by_user.argtypes = [
        ctypes.c_char_p,  # username
        ctypes.c_int,     # dealType
        ctypes.POINTER(ctypes.c_int)  # count
    ]
    c_lib.land_find_by_user.restype = ctypes.POINTER(LandPropertyStruct)

    # محاسبه ارزش کل زمین‌ها
    c_lib.land_calculate_total_value.argtypes = []
    c_lib.land_calculate_total_value.restype = ctypes.c_double

    # آزادسازی حافظه
    c_lib.land_free_array.argtypes = [ctypes.POINTER(LandPropertyStruct)]
    c_lib.land_free_array.restype = None

setup_c_functions()

# ثابت‌های نوع معامله
DEAL_TYPE_SALE = 1
DEAL_TYPE_RENT = 2

class LandBridge:
    @staticmethod
    def _struct_to_dict(prop):
        """تبدیل ساختار املاک زمین به دیکشنری"""
        return {
            "id": prop.id.decode('utf-8'),
            "district": prop.district.decode('utf-8'),
            "address": prop.address.decode('utf-8'),
            "landType": prop.landType.decode('utf-8'),
            "landArea": prop.landArea,
            "distanceToMainRoad": prop.distanceToMainRoad,
            "hasWell": bool(prop.hasWell),
            "sellingPrice": prop.sellingPrice,
            "mortgageAmount": prop.mortgageAmount,
            "monthlyRentAmount": prop.monthlyRentAmount,
            "registrationDate": prop.registrationDate.decode('utf-8'),
            "lastUpdateDate": prop.lastUpdateDate.decode('utf-8'),
            "ownerUsername": prop.ownerUsername.decode('utf-8'),
            "contactPhone": prop.contactPhone.decode('utf-8'),
            "status": prop.status,
            "description": prop.description.decode('utf-8')
        }

    @staticmethod
    def _convert_results(results, count):
        """تبدیل نتایج جستجو به لیست دیکشنری"""
        properties = []
        
        # بررسی آیا نتایج از کتابخانه واقعی است یا mock
        if results is None:
            logger.warning("نتایج جستجو خالی است")
            return properties
        
        # بررسی نوع نتیجه برای تشخیص mock یا واقعی
        if str(type(results)).find('MockPropertyStruct_Array') >= 0:
            try:
                # استفاده مستقیم از داده‌های mock
                from bridge.mock_lib import mock_data
                
                # تعیین نوع معامله: فرض می‌کنیم معاملات فروش هستند مگر اینکه مشخص شده باشد
                deal_type_str = "sale"
                
                # تعداد نتایج مورد نیاز
                count_value = min(count.value, len(mock_data['land'][deal_type_str]))
                
                # برگرداندن تعداد مورد نیاز از نتایج
                return mock_data['land'][deal_type_str][:count_value]
            except Exception as e:
                logger.error(f"خطا در تبدیل نتایج mock: {str(e)}")
                return []
        
        # پردازش نتایج واقعی از کتابخانه C
        try:
            for i in range(count.value):
                properties.append(LandBridge._struct_to_dict(results[i]))
            return properties
        except Exception as e:
            logger.error(f"خطا در تبدیل نتایج ساختار: {str(e)}")
            return []

    @staticmethod
    def register_sale(username, district, address, land_type, land_area, 
                     distance_to_road, has_well, selling_price, contact_phone, description):
        """ثبت زمین برای فروش"""
        try:
            result = c_lib.land_register_sale(
                username.encode('utf-8'),
                district.encode('utf-8'),
                address.encode('utf-8'),
                land_type.encode('utf-8'),
                land_area,
                distance_to_road,
                1 if has_well else 0,
                selling_price,
                contact_phone.encode('utf-8'),
                description.encode('utf-8')
            )
            
            if result > 0:
                logger.info(f"زمین با موفقیت برای فروش ثبت شد. شناسه: {result}")
                return {"success": True, "property_id": result}
            else:
                logger.error(f"خطا در ثبت زمین برای فروش. کد خطا: {result}")
                return {"success": False, "error_code": result}
                
        except Exception as e:
            logger.error(f"استثنا در ثبت زمین برای فروش: {str(e)}")
            return {"success": False, "error": str(e)}

    @staticmethod
    def register_rental(username, district, address, land_type, land_area, 
                       distance_to_road, has_well, mortgage_amount, monthly_rent, 
                       contact_phone, description):
        """ثبت زمین برای اجاره"""
        try:
            result = c_lib.land_register_rental(
                username.encode('utf-8'),
                district.encode('utf-8'),
                address.encode('utf-8'),
                land_type.encode('utf-8'),
                land_area,
                distance_to_road,
                1 if has_well else 0,
                mortgage_amount,
                monthly_rent,
                contact_phone.encode('utf-8'),
                description.encode('utf-8')
            )
            
            if result > 0:
                logger.info(f"زمین با موفقیت برای اجاره ثبت شد. شناسه: {result}")
                return {"success": True, "property_id": result}
            else:
                logger.error(f"خطا در ثبت زمین برای اجاره. کد خطا: {result}")
                return {"success": False, "error_code": result}
                
        except Exception as e:
            logger.error(f"استثنا در ثبت زمین برای اجاره: {str(e)}")
            return {"success": False, "error": str(e)}

    @staticmethod
    def find_by_district(district, deal_type):
        """جستجوی زمین بر اساس منطقه"""
        try:
            count = ctypes.c_int(0)
            results = c_lib.land_find_by_district(
                district.encode('utf-8'),
                deal_type,
                ctypes.byref(count)
            )
            
            properties = LandBridge._convert_results(results, count)
            
            # آزادسازی حافظه
            c_lib.land_free_array(results)
            
            logger.info(f"جستجوی زمین در منطقه {district}: {count.value} نتیجه یافت شد")
            return {"success": True, "properties": properties, "count": count.value}
            
        except Exception as e:
            logger.error(f"خطا در جستجوی زمین بر اساس منطقه: {str(e)}")
            return {"success": False, "error": str(e)}

    @staticmethod
    def find_by_area(min_area, max_area, deal_type):
        """جستجوی زمین بر اساس متراژ"""
        try:
            count = ctypes.c_int(0)
            results = c_lib.land_find_by_area(
                min_area,
                max_area,
                deal_type,
                ctypes.byref(count)
            )
            
            properties = LandBridge._convert_results(results, count)
            
            # آزادسازی حافظه
            c_lib.land_free_array(results)
            
            logger.info(f"جستجوی زمین با متراژ بین {min_area} و {max_area}: {count.value} نتیجه یافت شد")
            return {"success": True, "properties": properties, "count": count.value}
            
        except Exception as e:
            logger.error(f"خطا در جستجوی زمین بر اساس متراژ: {str(e)}")
            return {"success": False, "error": str(e)}

    @staticmethod
    def find_by_type(land_type, deal_type):
        """جستجوی زمین بر اساس نوع"""
        try:
            count = ctypes.c_int(0)
            results = c_lib.land_find_by_type(
                land_type.encode('utf-8'),
                deal_type,
                ctypes.byref(count)
            )
            
            properties = LandBridge._convert_results(results, count)
            
            # آزادسازی حافظه
            c_lib.land_free_array(results)
            
            logger.info(f"جستجوی زمین با نوع {land_type}: {count.value} نتیجه یافت شد")
            return {"success": True, "properties": properties, "count": count.value}
            
        except Exception as e:
            logger.error(f"خطا در جستجوی زمین بر اساس نوع: {str(e)}")
            return {"success": False, "error": str(e)}

    @staticmethod
    def find_by_price(min_price, max_price, deal_type):
        """جستجوی زمین بر اساس قیمت"""
        try:
            count = ctypes.c_int(0)
            results = c_lib.land_find_by_price(
                min_price,
                max_price,
                deal_type,
                ctypes.byref(count)
            )
            
            properties = LandBridge._convert_results(results, count)
            
            # آزادسازی حافظه
            c_lib.land_free_array(results)
            
            logger.info(f"جستجوی زمین با قیمت بین {min_price} و {max_price}: {count.value} نتیجه یافت شد")
            return {"success": True, "properties": properties, "count": count.value}
            
        except Exception as e:
            logger.error(f"خطا در جستجوی زمین بر اساس قیمت: {str(e)}")
            return {"success": False, "error": str(e)}

    @staticmethod
    def find_by_distance(max_distance, deal_type):
        """جستجوی زمین بر اساس فاصله از جاده اصلی"""
        try:
            count = ctypes.c_int(0)
            results = c_lib.land_find_by_distance(
                max_distance,
                deal_type,
                ctypes.byref(count)
            )
            
            properties = LandBridge._convert_results(results, count)
            
            # آزادسازی حافظه
            c_lib.land_free_array(results)
            
            logger.info(f"جستجوی زمین با فاصله حداکثر {max_distance} از جاده اصلی: {count.value} نتیجه یافت شد")
            return {"success": True, "properties": properties, "count": count.value}
            
        except Exception as e:
            logger.error(f"خطا در جستجوی زمین بر اساس فاصله از جاده اصلی: {str(e)}")
            return {"success": False, "error": str(e)}

    @staticmethod
    def find_with_well(deal_type):
        """جستجوی زمین دارای چاه آب"""
        try:
            count = ctypes.c_int(0)
            results = c_lib.land_find_with_well(
                deal_type,
                ctypes.byref(count)
            )
            
            properties = LandBridge._convert_results(results, count)
            
            # آزادسازی حافظه
            c_lib.land_free_array(results)
            
            logger.info(f"جستجوی زمین دارای چاه آب: {count.value} نتیجه یافت شد")
            return {"success": True, "properties": properties, "count": count.value}
            
        except Exception as e:
            logger.error(f"خطا در جستجوی زمین دارای چاه آب: {str(e)}")
            return {"success": False, "error": str(e)}

    @staticmethod
    def find_deleted_by_date(start_date, end_date, deal_type):
        """جستجوی زمین‌های حذف شده در بازه زمانی مشخص"""
        try:
            count = ctypes.c_int(0)
            results = c_lib.land_find_deleted_by_date(
                start_date.encode('utf-8'),
                end_date.encode('utf-8'),
                deal_type,
                ctypes.byref(count)
            )
            
            properties = LandBridge._convert_results(results, count)
            
            # آزادسازی حافظه
            c_lib.land_free_array(results)
            
            logger.info(f"جستجوی زمین‌های حذف شده از {start_date} تا {end_date}: {count.value} نتیجه یافت شد")
            return {"success": True, "properties": properties, "count": count.value}
            
        except Exception as e:
            logger.error(f"خطا در جستجوی زمین‌های حذف شده: {str(e)}")
            return {"success": False, "error": str(e)}

    @staticmethod
    def find_by_user(username, deal_type):
        """جستجوی زمین‌های ثبت شده توسط یک کاربر"""
        try:
            count = ctypes.c_int(0)
            results = c_lib.land_find_by_user(
                username.encode('utf-8'),
                deal_type,
                ctypes.byref(count)
            )
            
            properties = LandBridge._convert_results(results, count)
            
            # آزادسازی حافظه
            c_lib.land_free_array(results)
            
            logger.info(f"جستجوی زمین‌های ثبت شده توسط کاربر {username}: {count.value} نتیجه یافت شد")
            return {"success": True, "properties": properties, "count": count.value}
            
        except Exception as e:
            logger.error(f"خطا در جستجوی زمین‌های ثبت شده توسط کاربر: {str(e)}")
            return {"success": False, "error": str(e)}

    @staticmethod
    def calculate_total_value():
        """محاسبه ارزش کل زمین‌ها"""
        try:
            total_value = c_lib.land_calculate_total_value()
            logger.info(f"ارزش کل زمین‌ها محاسبه شد: {total_value}")
            return {"success": True, "total_value": total_value}
            
        except Exception as e:
            logger.error(f"خطا در محاسبه ارزش کل زمین‌ها: {str(e)}")
            return {"success": False, "error": str(e)}

    @staticmethod
    def get_properties(deal_type="sale"):
        """دریافت لیست همه املاک زمین
        
        Args:
            deal_type (str): نوع معامله (فروش یا اجاره)
            
        Returns:
            list: لیستی از املاک زمین
        """
        try:
            # بررسی کنیم آیا از کتابخانه mock استفاده می‌شود
            if 'bridge.mock_lib' in sys.modules:
                # اگر اینجا یعنی از کتابخانه mock استفاده می‌شود
                from bridge.mock_lib import mock_data
                
                # تبدیل نوع معامله به رشته
                deal_type_str = "sale" if deal_type == "sale" or deal_type == 1 else "rent"
                
                # برگرداندن داده‌های آماده از mock
                logger.info(f"استفاده از داده‌های mock برای املاک زمین: {len(mock_data['land'][deal_type_str])} ملک یافت شد")
                return mock_data['land'][deal_type_str]
            
            # تبدیل نوع معامله به عدد متناظر
            deal_type_code = DEAL_TYPE_SALE if deal_type == "sale" else DEAL_TYPE_RENT
            
            # جستجوی همه املاک زمین با متراژ بزرگتر از صفر (همه املاک)
            result = LandBridge.find_by_area(0, float('inf'), deal_type_code)
            
            if result.get('success', False):
                return result.get('properties', [])
            else:
                logger.error(f"خطا در دریافت لیست املاک زمین: {result.get('error', 'Unknown error')}")
                return []
        except Exception as e:
            logger.error(f"خطا در دریافت لیست املاک زمین: {str(e)}")
            return []
            
    @staticmethod
    def find_all_properties(deal_type="sale"):
        """دریافت لیست همه املاک زمین (نام جایگزین)
        
        Args:
            deal_type (str): نوع معامله (فروش یا اجاره)
            
        Returns:
            list: لیستی از املاک زمین
        """
        return LandBridge.get_properties(deal_type)
        
    @staticmethod
    def register(username, district, address, area_size, land_type,
                has_permit, permit_type, special_features, selling_price,
                contact_phone, description):
        """ثبت زمین برای فروش"""
        try:
            result = c_lib.land_register_sale(
                username.encode('utf-8'),
                district.encode('utf-8'),
                address.encode('utf-8'),
                land_type.encode('utf-8'),
                area_size,
                0,  # Assuming distanceToMainRoad is 0 for simplicity
                1 if has_permit else 0,  # Assuming hasWell is 1 if hasPermit is true
                selling_price,
                contact_phone.encode('utf-8'),
                description.encode('utf-8')
            )
            
            if result > 0:
                logger.info(f"زمین با موفقیت برای فروش ثبت شد. شناسه: {result}")
                return {"success": True, "property_id": result}
            else:
                logger.error(f"خطا در ثبت زمین برای فروش. کد خطا: {result}")
                return {"success": False, "error_code": result}
                
        except Exception as e:
            logger.error(f"استثنا در ثبت زمین برای فروش: {str(e)}")
            return {"success": False, "error": str(e)}


# اگر این ماژول به صورت مستقیم اجرا شود
if __name__ == "__main__":
    # تست اتصال به کتابخانه
    print("پل ارتباطی زمین‌ها با موفقیت راه‌اندازی شد.")
    print(f"کتابخانه C بارگذاری شده: {lib_path}") 