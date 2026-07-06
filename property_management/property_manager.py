#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ماژول مدیریت املاک

این ماژول شامل کلاس PropertyManager برای مدیریت کلی عملیات مربوط به املاک است.
"""

import os
import logging
import sys
from datetime import datetime, timedelta

class PropertyManager:
    """
    کلاس مدیریت املاک
    
    این کلاس برای مدیریت کلی همه املاک و رابط بین کتابخانه C و بخش‌های مختلف برنامه استفاده می‌شود.
    """
    
    def __init__(self):
        """مقداردهی اولیه مدیریت املاک"""
        self.logger = logging.getLogger(__name__)
        
        # تنظیم مسیر داده‌ها
        self.data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
        
        # مقداردهی اولیه bridges
        try:
            from bridge.residential_bridge import ResidentialBridge
            from bridge.commercial_bridge import CommercialBridge
            from bridge.land_bridge import LandBridge
            
            self.residential_bridge = ResidentialBridge
            self.commercial_bridge = CommercialBridge
            self.land_bridge = LandBridge
            
            self.logger.info("برایج‌های املاک با موفقیت راه‌اندازی شدند")
        except Exception as e:
            self.logger.error(f"خطا در راه‌اندازی برایج‌های املاک: {str(e)}")
            raise
            
        # تنظیم مسیر داده‌ها در کتابخانه C
        try:
            from bridge.lib_handler import get_lib_instance
            c_lib = get_lib_instance()
            result = c_lib.user_set_data_path(self.data_path.encode('utf-8'))
            if result:
                self.logger.info(f"مسیر داده‌ها با موفقیت تنظیم شد: {self.data_path}")
            else:
                self.logger.error(f"خطا در تنظیم مسیر داده‌ها: {self.data_path}")
                raise Exception("خطا در تنظیم مسیر داده‌ها")
        except Exception as e:
            self.logger.error(f"خطا در تنظیم مسیر داده‌ها: {str(e)}")
            
        self.logger.info("مدیریت املاک با موفقیت راه‌اندازی شد")
    
    def get_bridge(self, property_type):
        """
        دریافت برایج مناسب برای نوع ملک
        
        Args:
            property_type (str): نوع ملک ('residential', 'commercial', 'land')
            
        Returns:
            object: برایج مربوط به نوع ملک
            
        Raises:
            ValueError: اگر نوع ملک نامعتبر باشد
        """
        if property_type == 'residential':
            return self.residential_bridge
        elif property_type == 'commercial':
            return self.commercial_bridge
        elif property_type == 'land':
            return self.land_bridge
        else:
            raise ValueError(f"نوع ملک نامعتبر: {property_type}")
    
    def register_property(self, property_type, property_data):
        """
        ثبت ملک جدید
        
        Args:
            property_type (str): نوع ملک (residential, commercial, land)
            property_data (dict): اطلاعات ملک
            
        Returns:
            dict: نتیجه عملیات
        """
        try:
            self.logger.info(f"درخواست ثبت ملک {property_type} دریافت شد")
            
            # بررسی نوع ملک و استفاده از bridge مناسب
            if property_type == 'residential':
                if property_data.get('deal_type') == 'sale':
                    result = self.residential_bridge.register_sale(**property_data)
                else:
                    result = self.residential_bridge.register_rental(**property_data)
            
            elif property_type == 'commercial':
                if property_data.get('deal_type') == 'sale':
                    result = self.commercial_bridge.register_sale(**property_data)
                else:
                    result = self.commercial_bridge.register_rental(**property_data)
            
            elif property_type == 'land':
                if property_data.get('deal_type') == 'sale':
                    result = self.land_bridge.register_sale(**property_data)
                else:
                    result = self.land_bridge.register_rental(**property_data)
            
            else:
                self.logger.error(f"نوع ملک نامعتبر: {property_type}")
                return {"success": False, "error": f"نوع ملک نامعتبر: {property_type}"}
                
            self.logger.info(f"نتیجه ثبت ملک {property_type}: {result}")
            return result
            
        except Exception as e:
            self.logger.error(f"خطا در ثبت ملک: {str(e)}")
            return {"success": False, "error": str(e)} 