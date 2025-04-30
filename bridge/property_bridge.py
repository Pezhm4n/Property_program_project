#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
این ماژول پل ارتباطی اصلی برای مدیریت انواع مختلف املاک است.
این ماژول به عنوان واسط کلی بین رابط کاربری و پل‌های اختصاصی هر نوع ملک عمل می‌کند.
"""

import os
import sys
import json
import logging
from datetime import datetime

# وارد کردن ماژول‌های پل ارتباطی مختص به هر نوع ملک
from bridge.residential_bridge import ResidentialBridge, DEAL_TYPE_SALE, DEAL_TYPE_RENT
from bridge.commercial_bridge import CommercialBridge
from bridge.land_bridge import LandBridge

# تنظیمات لاگ
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'bridge.log')

logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger('property_bridge')

# ثابت‌های نوع معامله
DEAL_TYPE_SALE = DEAL_TYPE_SALE  # بازصادرات از ماژول‌های دیگر
DEAL_TYPE_RENT = DEAL_TYPE_RENT

# ثابت‌های نوع ملک
PROPERTY_TYPE_RESIDENTIAL = 'residential'
PROPERTY_TYPE_COMMERCIAL = 'commercial'
PROPERTY_TYPE_LAND = 'land'

def register_property(property_data):
    """
    ثبت ملک جدید در سیستم
    
    property_data باید حاوی اطلاعات زیر باشد:
    - type: نوع ملک (residential, commercial, land)
    - deal_type: نوع معامله (sale, rent)
    - سایر اطلاعات مربوط به هر نوع ملک
    """
    try:
        property_type = property_data.get('type')
        deal_type = property_data.get('deal_type')
        username = property_data.get('username', 'guest')
        
        if not property_type:
            logger.error("نوع ملک مشخص نشده است")
            return {"success": False, "error": "نوع ملک مشخص نشده است"}
            
        if not deal_type:
            logger.error("نوع معامله مشخص نشده است")
            return {"success": False, "error": "نوع معامله مشخص نشده است"}
        
        logger.info(f"شروع ثبت ملک جدید - نوع: {property_type}, معامله: {deal_type}")
        
        # ارسال به پل ارتباطی مربوطه بر اساس نوع ملک
        if property_type == PROPERTY_TYPE_RESIDENTIAL:
            return _register_residential_property(property_data, deal_type, username)
        elif property_type == PROPERTY_TYPE_COMMERCIAL:
            return _register_commercial_property(property_data, deal_type, username)
        elif property_type == PROPERTY_TYPE_LAND:
            return _register_land_property(property_data, deal_type, username)
        else:
            logger.error(f"نوع ملک نامعتبر: {property_type}")
            return {"success": False, "error": f"نوع ملک نامعتبر: {property_type}"}
    
    except Exception as e:
        logger.error(f"خطای ناشناخته در ثبت ملک: {str(e)}")
        return {"success": False, "error": str(e)}

def _register_residential_property(property_data, deal_type, username):
    """ثبت ملک مسکونی"""
    try:
        district = property_data.get('district', '')
        address = property_data.get('address', '')
        building_age = property_data.get('building_age', 0)
        area_size = property_data.get('area', 0.0)
        bedrooms = property_data.get('bedrooms', 0)
        floor = property_data.get('floor', 0)
        total_floors = property_data.get('total_floors', 1)
        has_elevator = property_data.get('has_elevator', False)
        has_parking = property_data.get('has_parking', False)
        has_storage = property_data.get('has_storage', False)
        contact_phone = property_data.get('contact_phone', '')
        description = property_data.get('description', '')
        
        if deal_type == 'sale':
            selling_price = property_data.get('selling_price', 0.0)
            return ResidentialBridge.register_sale(
                username, district, address, building_age, area_size,
                bedrooms, floor, total_floors, has_elevator, has_parking, has_storage,
                selling_price, contact_phone, description
            )
        else:  # rent
            mortgage_amount = property_data.get('mortgage_amount', 0.0)
            monthly_rent = property_data.get('monthly_rent', 0.0)
            return ResidentialBridge.register_rental(
                username, district, address, building_age, area_size,
                bedrooms, floor, total_floors, has_elevator, has_parking, has_storage,
                mortgage_amount, monthly_rent, contact_phone, description
            )
    
    except Exception as e:
        logger.error(f"خطا در ثبت ملک مسکونی: {str(e)}")
        return {"success": False, "error": str(e)}

def _register_commercial_property(property_data, deal_type, username):
    """ثبت ملک تجاری"""
    try:
        district = property_data.get('district', '')
        address = property_data.get('address', '')
        commercial_type = property_data.get('commercial_type', 'مغازه')
        area_size = property_data.get('area', 0.0)
        floor = property_data.get('floor', 0)
        has_showcase = property_data.get('has_showcase', False)
        is_active_business = property_data.get('is_active_business', False)
        contact_phone = property_data.get('contact_phone', '')
        description = property_data.get('description', '')
        
        if deal_type == 'sale':
            selling_price = property_data.get('selling_price', 0.0)
            return CommercialBridge.register_sale(
                username, district, address, commercial_type, area_size,
                floor, has_showcase, is_active_business, selling_price,
                contact_phone, description
            )
        else:  # rent
            mortgage_amount = property_data.get('mortgage_amount', 0.0)
            monthly_rent = property_data.get('monthly_rent', 0.0)
            return CommercialBridge.register_rental(
                username, district, address, commercial_type, area_size,
                floor, has_showcase, is_active_business, mortgage_amount,
                monthly_rent, contact_phone, description
            )
    
    except Exception as e:
        logger.error(f"خطا در ثبت ملک تجاری: {str(e)}")
        return {"success": False, "error": str(e)}

def _register_land_property(property_data, deal_type, username):
    """ثبت ملک زمین"""
    try:
        district = property_data.get('district', '')
        address = property_data.get('address', '')
        land_type = property_data.get('land_type', 'مسکونی')
        land_area = property_data.get('area', 0.0)
        distance_to_road = property_data.get('distance_to_road', 0)
        has_well = property_data.get('has_well', False)
        contact_phone = property_data.get('contact_phone', '')
        description = property_data.get('description', '')
        
        if deal_type == 'sale':
            selling_price = property_data.get('selling_price', 0.0)
            return LandBridge.register_sale(
                username, district, address, land_type, land_area,
                distance_to_road, has_well, selling_price, contact_phone, description
            )
        else:  # rent
            mortgage_amount = property_data.get('mortgage_amount', 0.0)
            monthly_rent = property_data.get('monthly_rent', 0.0)
            return LandBridge.register_rental(
                username, district, address, land_type, land_area,
                distance_to_road, has_well, mortgage_amount, monthly_rent,
                contact_phone, description
            )
    
    except Exception as e:
        logger.error(f"خطا در ثبت زمین: {str(e)}")
        return {"success": False, "error": str(e)}

def search_properties(search_params):
    """
    جستجوی املاک با پارامترهای مختلف
    
    search_params باید حاوی اطلاعات زیر باشد:
    - property_type: نوع ملک (residential, commercial, land)
    - deal_type: نوع معامله (sale, rent)
    - search_type: نوع جستجو (district, area, price, ...)
    - سایر پارامترهای مربوط به جستجو
    """
    try:
        property_type = search_params.get('property_type')
        deal_type = search_params.get('deal_type')
        search_type = search_params.get('search_type')
        
        if not property_type:
            logger.error("نوع ملک مشخص نشده است")
            return {"success": False, "error": "نوع ملک مشخص نشده است"}
            
        if not deal_type:
            logger.error("نوع معامله مشخص نشده است")
            return {"success": False, "error": "نوع معامله مشخص نشده است"}
            
        if not search_type:
            logger.error("نوع جستجو مشخص نشده است")
            return {"success": False, "error": "نوع جستجو مشخص نشده است"}
        
        # تبدیل نوع معامله از متن به عدد
        deal_type_code = DEAL_TYPE_SALE if deal_type == 'sale' else DEAL_TYPE_RENT
        
        logger.info(f"شروع جستجوی املاک - نوع: {property_type}, معامله: {deal_type}, جستجو: {search_type}")
        
        # ارسال به تابع جستجوی مربوطه بر اساس نوع ملک
        if property_type == PROPERTY_TYPE_RESIDENTIAL:
            return _search_residential_properties(search_params, deal_type_code, search_type)
        elif property_type == PROPERTY_TYPE_COMMERCIAL:
            return _search_commercial_properties(search_params, deal_type_code, search_type)
        elif property_type == PROPERTY_TYPE_LAND:
            return _search_land_properties(search_params, deal_type_code, search_type)
        else:
            logger.error(f"نوع ملک نامعتبر: {property_type}")
            return {"success": False, "error": f"نوع ملک نامعتبر: {property_type}"}
    
    except Exception as e:
        logger.error(f"خطای ناشناخته در جستجوی املاک: {str(e)}")
        return {"success": False, "error": str(e)}

def _search_residential_properties(search_params, deal_type_code, search_type):
    """جستجوی املاک مسکونی"""
    try:
        if search_type == 'district':
            district = search_params.get('district', '')
            return ResidentialBridge.find_by_district(district, deal_type_code)
            
        elif search_type == 'area':
            min_area = search_params.get('min_area', 0.0)
            max_area = search_params.get('max_area', float('inf'))
            return ResidentialBridge.find_by_area(min_area, max_area, deal_type_code)
            
        elif search_type == 'price':
            min_price = search_params.get('min_price', 0.0)
            max_price = search_params.get('max_price', float('inf'))
            return ResidentialBridge.find_by_price(min_price, max_price, deal_type_code)
            
        elif search_type == 'bedrooms':
            min_bedrooms = search_params.get('min_bedrooms', 0)
            max_bedrooms = search_params.get('max_bedrooms', 10)
            return ResidentialBridge.find_by_bedrooms(min_bedrooms, max_bedrooms, deal_type_code)
            
        elif search_type == 'floor':
            min_floor = search_params.get('min_floor', 0)
            max_floor = search_params.get('max_floor', 100)
            return ResidentialBridge.find_by_floor(min_floor, max_floor, deal_type_code)
            
        elif search_type == 'age':
            min_age = search_params.get('min_age', 0)
            max_age = search_params.get('max_age', 100)
            return ResidentialBridge.find_by_age(min_age, max_age, deal_type_code)
            
        elif search_type == 'elevator':
            return ResidentialBridge.find_with_elevator(deal_type_code)
            
        elif search_type == 'parking':
            return ResidentialBridge.find_with_parking(deal_type_code)
            
        elif search_type == 'storage':
            return ResidentialBridge.find_with_storage(deal_type_code)
            
        elif search_type == 'user':
            username = search_params.get('username', '')
            return ResidentialBridge.find_by_user(username, deal_type_code)
            
        elif search_type == 'deleted':
            start_date = search_params.get('start_date', '')
            end_date = search_params.get('end_date', '')
            return ResidentialBridge.find_deleted_by_date(start_date, end_date, deal_type_code)
            
        else:
            logger.error(f"نوع جستجوی نامعتبر برای املاک مسکونی: {search_type}")
            return {"success": False, "error": f"نوع جستجوی نامعتبر: {search_type}"}
    
    except Exception as e:
        logger.error(f"خطا در جستجوی املاک مسکونی: {str(e)}")
        return {"success": False, "error": str(e)}

def _search_commercial_properties(search_params, deal_type_code, search_type):
    """جستجوی املاک تجاری"""
    try:
        if search_type == 'district':
            district = search_params.get('district', '')
            return CommercialBridge.find_by_district(district, deal_type_code)
            
        elif search_type == 'area':
            min_area = search_params.get('min_area', 0.0)
            max_area = search_params.get('max_area', float('inf'))
            return CommercialBridge.find_by_area(min_area, max_area, deal_type_code)
            
        elif search_type == 'price':
            min_price = search_params.get('min_price', 0.0)
            max_price = search_params.get('max_price', float('inf'))
            return CommercialBridge.find_by_price(min_price, max_price, deal_type_code)
            
        elif search_type == 'type':
            commercial_type = search_params.get('commercial_type', '')
            return CommercialBridge.find_by_type(commercial_type, deal_type_code)
            
        elif search_type == 'showcase':
            return CommercialBridge.find_with_showcase(deal_type_code)
            
        elif search_type == 'user':
            username = search_params.get('username', '')
            return CommercialBridge.find_by_user(username, deal_type_code)
            
        elif search_type == 'deleted':
            start_date = search_params.get('start_date', '')
            end_date = search_params.get('end_date', '')
            return CommercialBridge.find_deleted_by_date(start_date, end_date, deal_type_code)
            
        else:
            logger.error(f"نوع جستجوی نامعتبر برای املاک تجاری: {search_type}")
            return {"success": False, "error": f"نوع جستجوی نامعتبر: {search_type}"}
    
    except Exception as e:
        logger.error(f"خطا در جستجوی املاک تجاری: {str(e)}")
        return {"success": False, "error": str(e)}

def _search_land_properties(search_params, deal_type_code, search_type):
    """جستجوی زمین‌ها"""
    try:
        if search_type == 'district':
            district = search_params.get('district', '')
            return LandBridge.find_by_district(district, deal_type_code)
            
        elif search_type == 'area':
            min_area = search_params.get('min_area', 0.0)
            max_area = search_params.get('max_area', float('inf'))
            return LandBridge.find_by_area(min_area, max_area, deal_type_code)
            
        elif search_type == 'price':
            min_price = search_params.get('min_price', 0.0)
            max_price = search_params.get('max_price', float('inf'))
            return LandBridge.find_by_price(min_price, max_price, deal_type_code)
            
        elif search_type == 'type':
            land_type = search_params.get('land_type', '')
            return LandBridge.find_by_type(land_type, deal_type_code)
            
        elif search_type == 'distance':
            max_distance = search_params.get('max_distance', 1000)
            return LandBridge.find_by_distance(max_distance, deal_type_code)
            
        elif search_type == 'well':
            return LandBridge.find_with_well(deal_type_code)
            
        elif search_type == 'user':
            username = search_params.get('username', '')
            return LandBridge.find_by_user(username, deal_type_code)
            
        elif search_type == 'deleted':
            start_date = search_params.get('start_date', '')
            end_date = search_params.get('end_date', '')
            return LandBridge.find_deleted_by_date(start_date, end_date, deal_type_code)
            
        else:
            logger.error(f"نوع جستجوی نامعتبر برای زمین‌ها: {search_type}")
            return {"success": False, "error": f"نوع جستجوی نامعتبر: {search_type}"}
    
    except Exception as e:
        logger.error(f"خطا در جستجوی زمین‌ها: {str(e)}")
        return {"success": False, "error": str(e)}

def calculate_total_value(property_type=None):
    """محاسبه ارزش کل املاک"""
    try:
        results = {}
        total = 0
        
        if property_type is None or property_type == PROPERTY_TYPE_RESIDENTIAL:
            residential_result = ResidentialBridge.calculate_total_value()
            if residential_result.get('success'):
                residential_value = residential_result.get('total_value', 0)
                results['residential'] = residential_value
                total += residential_value
        
        if property_type is None or property_type == PROPERTY_TYPE_COMMERCIAL:
            commercial_result = CommercialBridge.calculate_total_value()
            if commercial_result.get('success'):
                commercial_value = commercial_result.get('total_value', 0)
                results['commercial'] = commercial_value
                total += commercial_value
        
        if property_type is None or property_type == PROPERTY_TYPE_LAND:
            land_result = LandBridge.calculate_total_value()
            if land_result.get('success'):
                land_value = land_result.get('total_value', 0)
                results['land'] = land_value
                total += land_value
        
        results['total'] = total
        
        logger.info(f"محاسبه ارزش کل املاک: {results}")
        return {"success": True, "values": results}
    
    except Exception as e:
        logger.error(f"خطا در محاسبه ارزش کل املاک: {str(e)}")
        return {"success": False, "error": str(e)}


# اگر این ماژول به صورت مستقیم اجرا شود
if __name__ == "__main__":
    print("پل ارتباطی مدیریت املاک با موفقیت راه‌اندازی شد.")
    print("این ماژول به عنوان واسط کلی بین رابط کاربری و پل‌های اختصاصی هر نوع ملک عمل می‌کند.") 