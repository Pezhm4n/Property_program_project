#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
این ماژول پل ارتباطی بین هسته برنامه نوشته شده با C و رابط کاربری گرافیکی پایتون برای مدیریت املاک تجاری است.
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

logger = logging.getLogger('commercial_bridge')

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

# تعریف ساختار داده‌ای برای املاک تجاری
class CommercialPropertyStruct(ctypes.Structure):
    _fields_ = [
        ("id", ctypes.c_char * 50),
        ("district", ctypes.c_char * 50),
        ("address", ctypes.c_char * 200),
        ("commercialType", ctypes.c_char * 50),  # مغازه، دفتر کار، انبار، سایر
        ("areaSize", ctypes.c_float),
        ("floor", ctypes.c_int),
        ("hasShowcase", ctypes.c_int),
        ("isActiveBusiness", ctypes.c_int),
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
    # ثبت ملک تجاری برای فروش
    c_lib.commercial_register_sale.argtypes = [
        ctypes.c_char_p,  # username
        ctypes.c_char_p,  # district
        ctypes.c_char_p,  # address
        ctypes.c_char_p,  # commercialType
        ctypes.c_float,   # areaSize
        ctypes.c_int,     # floor
        ctypes.c_int,     # hasShowcase
        ctypes.c_int,     # isActiveBusiness
        ctypes.c_double,  # sellingPrice
        ctypes.c_char_p,  # contactPhone
        ctypes.c_char_p   # description
    ]
    c_lib.commercial_register_sale.restype = ctypes.c_int

    # ثبت ملک تجاری برای اجاره
    c_lib.commercial_register_rental.argtypes = [
        ctypes.c_char_p,  # username
        ctypes.c_char_p,  # district
        ctypes.c_char_p,  # address
        ctypes.c_char_p,  # commercialType
        ctypes.c_float,   # areaSize
        ctypes.c_int,     # floor
        ctypes.c_int,     # hasShowcase
        ctypes.c_int,     # isActiveBusiness
        ctypes.c_double,  # mortgageAmount
        ctypes.c_double,  # monthlyRentAmount
        ctypes.c_char_p,  # contactPhone
        ctypes.c_char_p   # description
    ]
    c_lib.commercial_register_rental.restype = ctypes.c_int

    # جستجوی ملک بر اساس منطقه
    c_lib.commercial_find_by_district.argtypes = [
        ctypes.c_char_p,  # district
        ctypes.c_int,     # dealType
        ctypes.POINTER(ctypes.c_int)  # count
    ]
    c_lib.commercial_find_by_district.restype = ctypes.POINTER(CommercialPropertyStruct)

    # جستجوی ملک بر اساس متراژ
    c_lib.commercial_find_by_area.argtypes = [
        ctypes.c_float,   # minArea
        ctypes.c_float,   # maxArea
        ctypes.c_int,     # dealType
        ctypes.POINTER(ctypes.c_int)  # count
    ]
    c_lib.commercial_find_by_area.restype = ctypes.POINTER(CommercialPropertyStruct)

    # جستجوی ملک بر اساس نوع تجاری
    c_lib.commercial_find_by_type.argtypes = [
        ctypes.c_char_p,  # commercialType
        ctypes.c_int,     # dealType
        ctypes.POINTER(ctypes.c_int)  # count
    ]
    c_lib.commercial_find_by_type.restype = ctypes.POINTER(CommercialPropertyStruct)

    # جستجوی ملک بر اساس قیمت
    c_lib.commercial_find_by_price.argtypes = [
        ctypes.c_double,  # minPrice
        ctypes.c_double,  # maxPrice
        ctypes.c_int,     # dealType
        ctypes.POINTER(ctypes.c_int)  # count
    ]
    c_lib.commercial_find_by_price.restype = ctypes.POINTER(CommercialPropertyStruct)

    # جستجوی ملک بر اساس تعداد اتاق‌های اداری
    c_lib.commercial_find_by_rooms.argtypes = [
        ctypes.c_int,     # minRooms
        ctypes.c_int,     # maxRooms
        ctypes.c_int,     # dealType
        ctypes.POINTER(ctypes.c_int)  # count
    ]
    c_lib.commercial_find_by_rooms.restype = ctypes.POINTER(CommercialPropertyStruct)

    # جستجوی ملک دارای ویترین
    c_lib.commercial_find_with_showcase.argtypes = [
        ctypes.c_int,     # dealType
        ctypes.POINTER(ctypes.c_int)  # count
    ]
    c_lib.commercial_find_with_showcase.restype = ctypes.POINTER(CommercialPropertyStruct)

    # جستجوی املاک حذف شده بر اساس تاریخ
    c_lib.commercial_find_deleted_by_date.argtypes = [
        ctypes.c_char_p,  # startDate
        ctypes.c_char_p,  # endDate
        ctypes.c_int,     # dealType
        ctypes.POINTER(ctypes.c_int)  # count
    ]
    c_lib.commercial_find_deleted_by_date.restype = ctypes.POINTER(CommercialPropertyStruct)

    # جستجوی املاک ثبت شده توسط یک کاربر
    c_lib.commercial_find_by_user.argtypes = [
        ctypes.c_char_p,  # username
        ctypes.c_int,     # dealType
        ctypes.POINTER(ctypes.c_int)  # count
    ]
    c_lib.commercial_find_by_user.restype = ctypes.POINTER(CommercialPropertyStruct)

    # محاسبه ارزش کل املاک تجاری
    c_lib.commercial_calculate_total_value.argtypes = []
    c_lib.commercial_calculate_total_value.restype = ctypes.c_double

    # آزادسازی حافظه
    c_lib.commercial_free_array.argtypes = [ctypes.POINTER(CommercialPropertyStruct)]
    c_lib.commercial_free_array.restype = None

setup_c_functions()

# ثابت‌های نوع معامله
DEAL_TYPE_SALE = 1
DEAL_TYPE_RENT = 2

class CommercialBridge:
    @staticmethod
    def _struct_to_dict(prop):
        """تبدیل ساختار املاک تجاری به دیکشنری"""
        return {
            "id": prop.id.decode('utf-8'),
            "district": prop.district.decode('utf-8'),
            "address": prop.address.decode('utf-8'),
            "commercialType": prop.commercialType.decode('utf-8'),
            "areaSize": prop.areaSize,
            "floor": prop.floor,
            "hasShowcase": bool(prop.hasShowcase),
            "isActiveBusiness": bool(prop.isActiveBusiness),
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
                count_value = min(count.value, len(mock_data['commercial'][deal_type_str]))
                
                # برگرداندن تعداد مورد نیاز از نتایج
                return mock_data['commercial'][deal_type_str][:count_value]
            except Exception as e:
                logger.error(f"خطا در تبدیل نتایج mock: {str(e)}")
                return []
        
        # پردازش نتایج واقعی از کتابخانه C
        try:
            for i in range(count.value):
                properties.append(CommercialBridge._struct_to_dict(results[i]))
            return properties
        except Exception as e:
            logger.error(f"خطا در تبدیل نتایج ساختار: {str(e)}")
            return []

    @staticmethod
    def register_sale(username, district, address, commercial_type, area_size, 
                     floor, has_showcase, is_active_business, selling_price, 
                     contact_phone, description):
        """ثبت ملک تجاری برای فروش"""
        try:
            result = c_lib.commercial_register_sale(
                username.encode('utf-8'),
                district.encode('utf-8'),
                address.encode('utf-8'),
                commercial_type.encode('utf-8'),
                area_size,
                floor,
                1 if has_showcase else 0,
                1 if is_active_business else 0,
                selling_price,
                contact_phone.encode('utf-8'),
                description.encode('utf-8')
            )
            
            if result > 0:
                logger.info(f"ملک تجاری با موفقیت برای فروش ثبت شد. شناسه: {result}")
                return {"success": True, "property_id": result}
            else:
                logger.error(f"خطا در ثبت ملک تجاری برای فروش. کد خطا: {result}")
                return {"success": False, "error_code": result}
                
        except Exception as e:
            logger.error(f"استثنا در ثبت ملک تجاری برای فروش: {str(e)}")
            return {"success": False, "error": str(e)}

    @staticmethod
    def register_rental(username, district, address, commercial_type, area_size, 
                        floor, has_showcase, is_active_business, mortgage_amount, 
                        monthly_rent, contact_phone, description):
        """ثبت ملک تجاری برای اجاره"""
        try:
            result = c_lib.commercial_register_rental(
                username.encode('utf-8'),
                district.encode('utf-8'),
                address.encode('utf-8'),
                commercial_type.encode('utf-8'),
                area_size,
                floor,
                1 if has_showcase else 0,
                1 if is_active_business else 0,
                mortgage_amount,
                monthly_rent,
                contact_phone.encode('utf-8'),
                description.encode('utf-8')
            )
            
            if result > 0:
                logger.info(f"ملک تجاری با موفقیت برای اجاره ثبت شد. شناسه: {result}")
                return {"success": True, "property_id": result}
            else:
                logger.error(f"خطا در ثبت ملک تجاری برای اجاره. کد خطا: {result}")
                return {"success": False, "error_code": result}
                
        except Exception as e:
            logger.error(f"استثنا در ثبت ملک تجاری برای اجاره: {str(e)}")
            return {"success": False, "error": str(e)}

    @staticmethod
    def find_by_district(district, deal_type):
        """جستجوی ملک تجاری بر اساس منطقه"""
        try:
            count = ctypes.c_int(0)
            results = c_lib.commercial_find_by_district(
                district.encode('utf-8'),
                deal_type,
                ctypes.byref(count)
            )
            
            properties = CommercialBridge._convert_results(results, count)
            
            # آزادسازی حافظه
            c_lib.commercial_free_array(results)
            
            logger.info(f"جستجوی ملک تجاری در منطقه {district}: {count.value} نتیجه یافت شد")
            return {"success": True, "properties": properties, "count": count.value}
            
        except Exception as e:
            logger.error(f"خطا در جستجوی ملک تجاری بر اساس منطقه: {str(e)}")
            return {"success": False, "error": str(e)}

    @staticmethod
    def find_by_area(min_area, max_area, deal_type):
        """جستجوی ملک تجاری بر اساس متراژ"""
        try:
            count = ctypes.c_int(0)
            results = c_lib.commercial_find_by_area(
                min_area,
                max_area,
                deal_type,
                ctypes.byref(count)
            )
            
            properties = CommercialBridge._convert_results(results, count)
            
            # آزادسازی حافظه
            c_lib.commercial_free_array(results)
            
            logger.info(f"جستجوی ملک تجاری با متراژ بین {min_area} و {max_area}: {count.value} نتیجه یافت شد")
            return {"success": True, "properties": properties, "count": count.value}
            
        except Exception as e:
            logger.error(f"خطا در جستجوی ملک تجاری بر اساس متراژ: {str(e)}")
            return {"success": False, "error": str(e)}

    @staticmethod
    def find_by_type(commercial_type, deal_type):
        """جستجوی ملک تجاری بر اساس نوع"""
        try:
            count = ctypes.c_int(0)
            results = c_lib.commercial_find_by_type(
                commercial_type.encode('utf-8'),
                deal_type,
                ctypes.byref(count)
            )
            
            properties = CommercialBridge._convert_results(results, count)
            
            # آزادسازی حافظه
            c_lib.commercial_free_array(results)
            
            logger.info(f"جستجوی ملک تجاری با نوع {commercial_type}: {count.value} نتیجه یافت شد")
            return {"success": True, "properties": properties, "count": count.value}
            
        except Exception as e:
            logger.error(f"خطا در جستجوی ملک تجاری بر اساس نوع: {str(e)}")
            return {"success": False, "error": str(e)}

    @staticmethod
    def find_by_price(min_price, max_price, deal_type):
        """جستجوی ملک تجاری بر اساس قیمت"""
        try:
            count = ctypes.c_int(0)
            results = c_lib.commercial_find_by_price(
                min_price,
                max_price,
                deal_type,
                ctypes.byref(count)
            )
            
            properties = CommercialBridge._convert_results(results, count)
            
            # آزادسازی حافظه
            c_lib.commercial_free_array(results)
            
            logger.info(f"جستجوی ملک تجاری با قیمت بین {min_price} و {max_price}: {count.value} نتیجه یافت شد")
            return {"success": True, "properties": properties, "count": count.value}
            
        except Exception as e:
            logger.error(f"خطا در جستجوی ملک تجاری بر اساس قیمت: {str(e)}")
            return {"success": False, "error": str(e)}

    @staticmethod
    def find_by_rooms(min_rooms, max_rooms, deal_type):
        """جستجوی ملک تجاری بر اساس تعداد اتاق‌های اداری"""
        try:
            count = ctypes.c_int(0)
            results = c_lib.commercial_find_by_rooms(
                min_rooms,
                max_rooms,
                deal_type,
                ctypes.byref(count)
            )
            
            properties = CommercialBridge._convert_results(results, count)
            
            # آزادسازی حافظه
            c_lib.commercial_free_array(results)
            
            logger.info(f"جستجوی ملک تجاری با تعداد اتاق بین {min_rooms} و {max_rooms if max_rooms > 0 else 'نامحدود'}: {count.value} نتیجه یافت شد")
            return {"success": True, "properties": properties, "count": count.value}
            
        except Exception as e:
            logger.error(f"خطا در جستجوی ملک تجاری بر اساس تعداد اتاق: {str(e)}")
            return {"success": False, "error": str(e)}

    @staticmethod
    def find_with_showcase(deal_type):
        """جستجوی ملک تجاری دارای ویترین"""
        try:
            count = ctypes.c_int(0)
            results = c_lib.commercial_find_with_showcase(
                deal_type,
                ctypes.byref(count)
            )
            
            properties = CommercialBridge._convert_results(results, count)
            
            # آزادسازی حافظه
            c_lib.commercial_free_array(results)
            
            logger.info(f"جستجوی ملک تجاری دارای ویترین: {count.value} نتیجه یافت شد")
            return {"success": True, "properties": properties, "count": count.value}
            
        except Exception as e:
            logger.error(f"خطا در جستجوی ملک تجاری دارای ویترین: {str(e)}")
            return {"success": False, "error": str(e)}

    @staticmethod
    def find_deleted_by_date(start_date, end_date, deal_type):
        """جستجوی املاک تجاری حذف شده در بازه زمانی مشخص"""
        try:
            count = ctypes.c_int(0)
            results = c_lib.commercial_find_deleted_by_date(
                start_date.encode('utf-8'),
                end_date.encode('utf-8'),
                deal_type,
                ctypes.byref(count)
            )
            
            properties = CommercialBridge._convert_results(results, count)
            
            # آزادسازی حافظه
            c_lib.commercial_free_array(results)
            
            logger.info(f"جستجوی املاک تجاری حذف شده از {start_date} تا {end_date}: {count.value} نتیجه یافت شد")
            return {"success": True, "properties": properties, "count": count.value}
            
        except Exception as e:
            logger.error(f"خطا در جستجوی املاک تجاری حذف شده: {str(e)}")
            return {"success": False, "error": str(e)}

    @staticmethod
    def find_by_user(username, deal_type):
        """جستجوی املاک تجاری ثبت شده توسط یک کاربر"""
        try:
            count = ctypes.c_int(0)
            results = c_lib.commercial_find_by_user(
                username.encode('utf-8'),
                deal_type,
                ctypes.byref(count)
            )
            
            properties = CommercialBridge._convert_results(results, count)
            
            # آزادسازی حافظه
            c_lib.commercial_free_array(results)
            
            logger.info(f"جستجوی املاک تجاری ثبت شده توسط کاربر {username}: {count.value} نتیجه یافت شد")
            return {"success": True, "properties": properties, "count": count.value}
            
        except Exception as e:
            logger.error(f"خطا در جستجوی املاک تجاری ثبت شده توسط کاربر: {str(e)}")
            return {"success": False, "error": str(e)}

    @staticmethod
    def calculate_total_value():
        """محاسبه ارزش کل املاک تجاری"""
        try:
            total_value = c_lib.commercial_calculate_total_value()
            logger.info(f"ارزش کل املاک تجاری محاسبه شد: {total_value}")
            return {"success": True, "total_value": total_value}
            
        except Exception as e:
            logger.error(f"خطا در محاسبه ارزش کل املاک تجاری: {str(e)}")
            return {"success": False, "error": str(e)}

    @staticmethod
    def get_properties(deal_type="sale"):
        """دریافت لیست همه املاک تجاری
        
        Args:
            deal_type (str): نوع معامله (فروش یا اجاره)
            
        Returns:
            list: لیستی از املاک تجاری
        """
        try:
            # بررسی کنیم آیا از کتابخانه mock استفاده می‌شود
            if 'bridge.mock_lib' in sys.modules:
                # اگر اینجا یعنی از کتابخانه mock استفاده می‌شود
                from bridge.mock_lib import mock_data
                
                # تبدیل نوع معامله به رشته
                deal_type_str = "sale" if deal_type == "sale" or deal_type == 1 else "rent"
                
                # برگرداندن داده‌های آماده از mock
                logger.info(f"استفاده از داده‌های mock برای املاک تجاری: {len(mock_data['commercial'][deal_type_str])} ملک یافت شد")
                return mock_data['commercial'][deal_type_str]
            
            # تبدیل نوع معامله به عدد متناظر
            deal_type_code = DEAL_TYPE_SALE if deal_type == "sale" else DEAL_TYPE_RENT
            
            # جستجوی همه املاک تجاری با متراژ بزرگتر از صفر (همه املاک)
            result = CommercialBridge.find_by_area(0, float('inf'), deal_type_code)
            
            if result.get('success', False):
                return result.get('properties', [])
            else:
                logger.error(f"خطا در دریافت لیست املاک تجاری: {result.get('error', 'Unknown error')}")
                return []
        except Exception as e:
            logger.error(f"خطا در دریافت لیست املاک تجاری: {str(e)}")
            return []
            
    @staticmethod
    def find_all_properties(deal_type="sale"):
        """دریافت لیست همه املاک تجاری (نام جایگزین)
        
        Args:
            deal_type (str): نوع معامله (فروش یا اجاره)
            
        Returns:
            list: لیستی از املاک تجاری
        """
        return CommercialBridge.get_properties(deal_type)


# اگر این ماژول به صورت مستقیم اجرا شود
if __name__ == "__main__":
    # تست اتصال به کتابخانه
    print("پل ارتباطی املاک تجاری با موفقیت راه‌اندازی شد.")
    print(f"کتابخانه C بارگذاری شده: {lib_path}") 