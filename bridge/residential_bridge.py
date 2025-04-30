#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
این ماژول پل ارتباطی بین هسته برنامه نوشته شده با C و رابط کاربری گرافیکی پایتون برای مدیریت املاک مسکونی است.
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

logger = logging.getLogger('residential_bridge')

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
    raise

# تعریف ساختار داده‌ای برای املاک مسکونی
class ResidentialPropertyStruct(ctypes.Structure):
    _fields_ = [
        ("id", ctypes.c_char * 50),
        ("district", ctypes.c_char * 50),
        ("address", ctypes.c_char * 200),
        ("buildingAge", ctypes.c_int),
        ("areaSize", ctypes.c_float),
        ("bedrooms", ctypes.c_int),
        ("floor", ctypes.c_int),
        ("totalFloors", ctypes.c_int),
        ("hasElevator", ctypes.c_int),
        ("hasParking", ctypes.c_int),
        ("hasStorage", ctypes.c_int),
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
    # ثبت ملک مسکونی برای فروش
    c_lib.residential_register_sale.argtypes = [
        ctypes.c_char_p,  # username
        ctypes.c_char_p,  # district
        ctypes.c_char_p,  # address
        ctypes.c_int,     # buildingAge
        ctypes.c_float,   # areaSize
        ctypes.c_int,     # bedrooms
        ctypes.c_int,     # floor
        ctypes.c_int,     # totalFloors
        ctypes.c_int,     # hasElevator
        ctypes.c_int,     # hasParking
        ctypes.c_int,     # hasStorage
        ctypes.c_double,  # sellingPrice
        ctypes.c_char_p,  # contactPhone
        ctypes.c_char_p   # description
    ]
    c_lib.residential_register_sale.restype = ctypes.c_int

    # ثبت ملک مسکونی برای اجاره
    c_lib.residential_register_rental.argtypes = [
        ctypes.c_char_p,  # username
        ctypes.c_char_p,  # district
        ctypes.c_char_p,  # address
        ctypes.c_int,     # buildingAge
        ctypes.c_float,   # areaSize
        ctypes.c_int,     # bedrooms
        ctypes.c_int,     # floor
        ctypes.c_int,     # totalFloors
        ctypes.c_int,     # hasElevator
        ctypes.c_int,     # hasParking
        ctypes.c_int,     # hasStorage
        ctypes.c_double,  # mortgageAmount
        ctypes.c_double,  # monthlyRentAmount
        ctypes.c_char_p,  # contactPhone
        ctypes.c_char_p   # description
    ]
    c_lib.residential_register_rental.restype = ctypes.c_int

    # جستجوی ملک بر اساس منطقه
    c_lib.residential_find_by_district.argtypes = [
        ctypes.c_char_p,  # district
        ctypes.c_int,     # dealType
        ctypes.POINTER(ctypes.c_int)  # count
    ]
    c_lib.residential_find_by_district.restype = ctypes.POINTER(ResidentialPropertyStruct)

    # جستجوی ملک بر اساس سن ساختمان
    c_lib.residential_find_by_age.argtypes = [
        ctypes.c_int,     # minAge
        ctypes.c_int,     # maxAge
        ctypes.c_int,     # dealType
        ctypes.POINTER(ctypes.c_int)  # count
    ]
    c_lib.residential_find_by_age.restype = ctypes.POINTER(ResidentialPropertyStruct)

    # جستجوی ملک بر اساس متراژ
    c_lib.residential_find_by_area.argtypes = [
        ctypes.c_float,   # minArea
        ctypes.c_float,   # maxArea
        ctypes.c_int,     # dealType
        ctypes.POINTER(ctypes.c_int)  # count
    ]
    c_lib.residential_find_by_area.restype = ctypes.POINTER(ResidentialPropertyStruct)

    # جستجوی ملک بر اساس تعداد اتاق خواب
    c_lib.residential_find_by_bedrooms.argtypes = [
        ctypes.c_int,     # minBedrooms
        ctypes.c_int,     # maxBedrooms
        ctypes.c_int,     # dealType
        ctypes.POINTER(ctypes.c_int)  # count
    ]
    c_lib.residential_find_by_bedrooms.restype = ctypes.POINTER(ResidentialPropertyStruct)

    # جستجوی ملک بر اساس قیمت
    c_lib.residential_find_by_price.argtypes = [
        ctypes.c_double,  # minPrice
        ctypes.c_double,  # maxPrice
        ctypes.c_int,     # dealType
        ctypes.POINTER(ctypes.c_int)  # count
    ]
    c_lib.residential_find_by_price.restype = ctypes.POINTER(ResidentialPropertyStruct)

    # جستجوی ملک بر اساس طبقه
    c_lib.residential_find_by_floor.argtypes = [
        ctypes.c_int,     # minFloor
        ctypes.c_int,     # maxFloor
        ctypes.c_int,     # dealType
        ctypes.POINTER(ctypes.c_int)  # count
    ]
    c_lib.residential_find_by_floor.restype = ctypes.POINTER(ResidentialPropertyStruct)

    # جستجوی ملک دارای آسانسور
    c_lib.residential_find_with_elevator.argtypes = [
        ctypes.c_int,     # dealType
        ctypes.POINTER(ctypes.c_int)  # count
    ]
    c_lib.residential_find_with_elevator.restype = ctypes.POINTER(ResidentialPropertyStruct)

    # جستجوی ملک دارای پارکینگ
    c_lib.residential_find_with_parking.argtypes = [
        ctypes.c_int,     # dealType
        ctypes.POINTER(ctypes.c_int)  # count
    ]
    c_lib.residential_find_with_parking.restype = ctypes.POINTER(ResidentialPropertyStruct)

    # جستجوی ملک دارای انباری
    c_lib.residential_find_with_storage.argtypes = [
        ctypes.c_int,     # dealType
        ctypes.POINTER(ctypes.c_int)  # count
    ]
    c_lib.residential_find_with_storage.restype = ctypes.POINTER(ResidentialPropertyStruct)

    # جستجوی املاک حذف شده بر اساس تاریخ
    c_lib.residential_find_deleted_by_date.argtypes = [
        ctypes.c_char_p,  # startDate
        ctypes.c_char_p,  # endDate
        ctypes.c_int,     # dealType
        ctypes.POINTER(ctypes.c_int)  # count
    ]
    c_lib.residential_find_deleted_by_date.restype = ctypes.POINTER(ResidentialPropertyStruct)

    # جستجوی املاک ثبت شده توسط یک کاربر
    c_lib.residential_find_by_user.argtypes = [
        ctypes.c_char_p,  # username
        ctypes.c_int,     # dealType
        ctypes.POINTER(ctypes.c_int)  # count
    ]
    c_lib.residential_find_by_user.restype = ctypes.POINTER(ResidentialPropertyStruct)

    # محاسبه ارزش کل املاک مسکونی
    c_lib.residential_calculate_total_value.argtypes = []
    c_lib.residential_calculate_total_value.restype = ctypes.c_double

    # آزادسازی حافظه
    c_lib.residential_free_array.argtypes = [ctypes.POINTER(ResidentialPropertyStruct)]
    c_lib.residential_free_array.restype = None

setup_c_functions()

# ثابت‌های نوع معامله
DEAL_TYPE_SALE = 1
DEAL_TYPE_RENT = 2

class ResidentialBridge:
    @staticmethod
    def _struct_to_dict(prop):
        """تبدیل ساختار املاک مسکونی به دیکشنری"""
        return {
            "id": prop.id.decode('utf-8'),
            "district": prop.district.decode('utf-8'),
            "address": prop.address.decode('utf-8'),
            "buildingAge": prop.buildingAge,
            "areaSize": prop.areaSize,
            "bedrooms": prop.bedrooms,
            "floor": prop.floor,
            "totalFloors": prop.totalFloors,
            "hasElevator": bool(prop.hasElevator),
            "hasParking": bool(prop.hasParking),
            "hasStorage": bool(prop.hasStorage),
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
        for i in range(count.value):
            properties.append(ResidentialBridge._struct_to_dict(results[i]))
        return properties

    @staticmethod
    def register_sale(username, district, address, building_age, area_size, bedrooms, 
                    floor, total_floors, has_elevator, has_parking, has_storage, 
                    selling_price, contact_phone, description):
        """ثبت ملک مسکونی برای فروش"""
        try:
            result = c_lib.residential_register_sale(
                username.encode('utf-8'),
                district.encode('utf-8'),
                address.encode('utf-8'),
                building_age,
                area_size,
                bedrooms,
                floor,
                total_floors,
                1 if has_elevator else 0,
                1 if has_parking else 0,
                1 if has_storage else 0,
                selling_price,
                contact_phone.encode('utf-8'),
                description.encode('utf-8')
            )
            
            if result > 0:
                logger.info(f"ملک مسکونی با موفقیت برای فروش ثبت شد. شناسه: {result}")
                return {"success": True, "property_id": result}
            else:
                logger.error(f"خطا در ثبت ملک مسکونی برای فروش. کد خطا: {result}")
                return {"success": False, "error_code": result}
                
        except Exception as e:
            logger.error(f"استثنا در ثبت ملک مسکونی برای فروش: {str(e)}")
            return {"success": False, "error": str(e)}

    @staticmethod
    def register_rental(username, district, address, building_age, area_size, bedrooms, 
                       floor, total_floors, has_elevator, has_parking, has_storage, 
                       mortgage_amount, monthly_rent, contact_phone, description):
        """ثبت ملک مسکونی برای اجاره"""
        try:
            result = c_lib.residential_register_rental(
                username.encode('utf-8'),
                district.encode('utf-8'),
                address.encode('utf-8'),
                building_age,
                area_size,
                bedrooms,
                floor,
                total_floors,
                1 if has_elevator else 0,
                1 if has_parking else 0,
                1 if has_storage else 0,
                mortgage_amount,
                monthly_rent,
                contact_phone.encode('utf-8'),
                description.encode('utf-8')
            )
            
            if result > 0:
                logger.info(f"ملک مسکونی با موفقیت برای اجاره ثبت شد. شناسه: {result}")
                return {"success": True, "property_id": result}
            else:
                logger.error(f"خطا در ثبت ملک مسکونی برای اجاره. کد خطا: {result}")
                return {"success": False, "error_code": result}
                
        except Exception as e:
            logger.error(f"استثنا در ثبت ملک مسکونی برای اجاره: {str(e)}")
            return {"success": False, "error": str(e)}

    @staticmethod
    def find_by_district(district, deal_type):
        """جستجوی ملک مسکونی بر اساس منطقه"""
        try:
            count = ctypes.c_int(0)
            results = c_lib.residential_find_by_district(
                district.encode('utf-8'),
                deal_type,
                ctypes.byref(count)
            )
            
            properties = ResidentialBridge._convert_results(results, count)
            
            # آزادسازی حافظه
            c_lib.residential_free_array(results)
            
            logger.info(f"جستجوی ملک مسکونی در منطقه {district}: {count.value} نتیجه یافت شد")
            return {"success": True, "properties": properties, "count": count.value}
            
        except Exception as e:
            logger.error(f"خطا در جستجوی ملک مسکونی بر اساس منطقه: {str(e)}")
            return {"success": False, "error": str(e)}

    @staticmethod
    def find_by_age(min_age, max_age, deal_type):
        """جستجوی ملک مسکونی بر اساس سن ساختمان"""
        try:
            count = ctypes.c_int(0)
            results = c_lib.residential_find_by_age(
                min_age,
                max_age,
                deal_type,
                ctypes.byref(count)
            )
            
            properties = ResidentialBridge._convert_results(results, count)
            
            # آزادسازی حافظه
            c_lib.residential_free_array(results)
            
            logger.info(f"جستجوی ملک مسکونی با سن بین {min_age} و {max_age}: {count.value} نتیجه یافت شد")
            return {"success": True, "properties": properties, "count": count.value}
            
        except Exception as e:
            logger.error(f"خطا در جستجوی ملک مسکونی بر اساس سن: {str(e)}")
            return {"success": False, "error": str(e)}

    @staticmethod
    def find_by_area(min_area, max_area, deal_type):
        """جستجوی ملک مسکونی بر اساس متراژ"""
        try:
            count = ctypes.c_int(0)
            results = c_lib.residential_find_by_area(
                min_area,
                max_area,
                deal_type,
                ctypes.byref(count)
            )
            
            properties = ResidentialBridge._convert_results(results, count)
            
            # آزادسازی حافظه
            c_lib.residential_free_array(results)
            
            logger.info(f"جستجوی ملک مسکونی با متراژ بین {min_area} و {max_area}: {count.value} نتیجه یافت شد")
            return {"success": True, "properties": properties, "count": count.value}
            
        except Exception as e:
            logger.error(f"خطا در جستجوی ملک مسکونی بر اساس متراژ: {str(e)}")
            return {"success": False, "error": str(e)}

    @staticmethod
    def find_by_bedrooms(min_bedrooms, max_bedrooms, deal_type):
        """جستجوی ملک مسکونی بر اساس تعداد اتاق خواب"""
        try:
            count = ctypes.c_int(0)
            results = c_lib.residential_find_by_bedrooms(
                min_bedrooms,
                max_bedrooms,
                deal_type,
                ctypes.byref(count)
            )
            
            properties = ResidentialBridge._convert_results(results, count)
            
            # آزادسازی حافظه
            c_lib.residential_free_array(results)
            
            logger.info(f"جستجوی ملک مسکونی با تعداد اتاق خواب بین {min_bedrooms} و {max_bedrooms}: {count.value} نتیجه یافت شد")
            return {"success": True, "properties": properties, "count": count.value}
            
        except Exception as e:
            logger.error(f"خطا در جستجوی ملک مسکونی بر اساس تعداد اتاق خواب: {str(e)}")
            return {"success": False, "error": str(e)}

    @staticmethod
    def find_by_price(min_price, max_price, deal_type):
        """جستجوی ملک مسکونی بر اساس قیمت"""
        try:
            count = ctypes.c_int(0)
            results = c_lib.residential_find_by_price(
                min_price,
                max_price,
                deal_type,
                ctypes.byref(count)
            )
            
            properties = ResidentialBridge._convert_results(results, count)
            
            # آزادسازی حافظه
            c_lib.residential_free_array(results)
            
            logger.info(f"جستجوی ملک مسکونی با قیمت بین {min_price} و {max_price}: {count.value} نتیجه یافت شد")
            return {"success": True, "properties": properties, "count": count.value}
            
        except Exception as e:
            logger.error(f"خطا در جستجوی ملک مسکونی بر اساس قیمت: {str(e)}")
            return {"success": False, "error": str(e)}

    @staticmethod
    def find_by_floor(min_floor, max_floor, deal_type):
        """جستجوی ملک مسکونی بر اساس طبقه"""
        try:
            count = ctypes.c_int(0)
            results = c_lib.residential_find_by_floor(
                min_floor,
                max_floor,
                deal_type,
                ctypes.byref(count)
            )
            
            properties = ResidentialBridge._convert_results(results, count)
            
            # آزادسازی حافظه
            c_lib.residential_free_array(results)
            
            logger.info(f"جستجوی ملک مسکونی در طبقات {min_floor} تا {max_floor}: {count.value} نتیجه یافت شد")
            return {"success": True, "properties": properties, "count": count.value}
            
        except Exception as e:
            logger.error(f"خطا در جستجوی ملک مسکونی بر اساس طبقه: {str(e)}")
            return {"success": False, "error": str(e)}

    @staticmethod
    def find_with_elevator(deal_type):
        """جستجوی ملک مسکونی دارای آسانسور"""
        try:
            count = ctypes.c_int(0)
            results = c_lib.residential_find_with_elevator(
                deal_type,
                ctypes.byref(count)
            )
            
            properties = ResidentialBridge._convert_results(results, count)
            
            # آزادسازی حافظه
            c_lib.residential_free_array(results)
            
            logger.info(f"جستجوی ملک مسکونی دارای آسانسور: {count.value} نتیجه یافت شد")
            return {"success": True, "properties": properties, "count": count.value}
            
        except Exception as e:
            logger.error(f"خطا در جستجوی ملک مسکونی دارای آسانسور: {str(e)}")
            return {"success": False, "error": str(e)}

    @staticmethod
    def find_with_parking(deal_type):
        """جستجوی ملک مسکونی دارای پارکینگ"""
        try:
            count = ctypes.c_int(0)
            results = c_lib.residential_find_with_parking(
                deal_type,
                ctypes.byref(count)
            )
            
            properties = ResidentialBridge._convert_results(results, count)
            
            # آزادسازی حافظه
            c_lib.residential_free_array(results)
            
            logger.info(f"جستجوی ملک مسکونی دارای پارکینگ: {count.value} نتیجه یافت شد")
            return {"success": True, "properties": properties, "count": count.value}
            
        except Exception as e:
            logger.error(f"خطا در جستجوی ملک مسکونی دارای پارکینگ: {str(e)}")
            return {"success": False, "error": str(e)}

    @staticmethod
    def find_with_storage(deal_type):
        """جستجوی ملک مسکونی دارای انباری"""
        try:
            count = ctypes.c_int(0)
            results = c_lib.residential_find_with_storage(
                deal_type,
                ctypes.byref(count)
            )
            
            properties = ResidentialBridge._convert_results(results, count)
            
            # آزادسازی حافظه
            c_lib.residential_free_array(results)
            
            logger.info(f"جستجوی ملک مسکونی دارای انباری: {count.value} نتیجه یافت شد")
            return {"success": True, "properties": properties, "count": count.value}
            
        except Exception as e:
            logger.error(f"خطا در جستجوی ملک مسکونی دارای انباری: {str(e)}")
            return {"success": False, "error": str(e)}

    @staticmethod
    def find_deleted_by_date(start_date, end_date, deal_type):
        """جستجوی املاک مسکونی حذف شده در بازه زمانی مشخص"""
        try:
            count = ctypes.c_int(0)
            results = c_lib.residential_find_deleted_by_date(
                start_date.encode('utf-8'),
                end_date.encode('utf-8'),
                deal_type,
                ctypes.byref(count)
            )
            
            properties = ResidentialBridge._convert_results(results, count)
            
            # آزادسازی حافظه
            c_lib.residential_free_array(results)
            
            logger.info(f"جستجوی املاک مسکونی حذف شده از {start_date} تا {end_date}: {count.value} نتیجه یافت شد")
            return {"success": True, "properties": properties, "count": count.value}
            
        except Exception as e:
            logger.error(f"خطا در جستجوی املاک مسکونی حذف شده: {str(e)}")
            return {"success": False, "error": str(e)}

    @staticmethod
    def find_by_user(username, deal_type):
        """جستجوی املاک مسکونی ثبت شده توسط یک کاربر"""
        try:
            count = ctypes.c_int(0)
            results = c_lib.residential_find_by_user(
                username.encode('utf-8'),
                deal_type,
                ctypes.byref(count)
            )
            
            properties = ResidentialBridge._convert_results(results, count)
            
            # آزادسازی حافظه
            c_lib.residential_free_array(results)
            
            logger.info(f"جستجوی املاک مسکونی ثبت شده توسط کاربر {username}: {count.value} نتیجه یافت شد")
            return {"success": True, "properties": properties, "count": count.value}
            
        except Exception as e:
            logger.error(f"خطا در جستجوی املاک مسکونی ثبت شده توسط کاربر: {str(e)}")
            return {"success": False, "error": str(e)}

    @staticmethod
    def calculate_total_value():
        """محاسبه ارزش کل املاک مسکونی"""
        try:
            total_value = c_lib.residential_calculate_total_value()
            logger.info(f"ارزش کل املاک مسکونی محاسبه شد: {total_value}")
            return {"success": True, "total_value": total_value}
            
        except Exception as e:
            logger.error(f"خطا در محاسبه ارزش کل املاک مسکونی: {str(e)}")
            return {"success": False, "error": str(e)}


# اگر این ماژول به صورت مستقیم اجرا شود
if __name__ == "__main__":
    # تست اتصال به کتابخانه
    print("پل ارتباطی املاک مسکونی با موفقیت راه‌اندازی شد.")
    print(f"کتابخانه C بارگذاری شده: {lib_path}") 