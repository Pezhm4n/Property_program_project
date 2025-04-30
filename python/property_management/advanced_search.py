#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ماژول جستجوی پیشرفته برای سیستم مدیریت املاک

این ماژول امکان جستجوی پیشرفته املاک را با استفاده از معیارهای مختلف فراهم می‌کند.
کلاس اصلی این ماژول، AdvancedSearch، رابط بین موتور جستجو و مدل فیلتر است.

Classes:
    * AdvancedSearch: کلاس اصلی برای جستجوی پیشرفته املاک
    * AdvancedSearchConfig: کلاس تنظیمات جستجوی پیشرفته
    * SearchPresetManager: مدیریت پیش‌تنظیمات جستجو
"""

import os
import json
import logging
import datetime
from typing import Dict, List, Any, Optional, Union, Tuple

import pandas as pd

from .search_engine import SearchEngine, SearchCriteria, SearchCondition, SearchOperator
from .filter_models import PropertyTableModel, PropertyFilterProxyModel
from .export import export_data
from .report_generator import ReportGenerator


class AdvancedSearchConfig:
    """کلاس تنظیمات جستجوی پیشرفته
    
    این کلاس برای نگهداری تنظیمات و معیارهای جستجوی پیشرفته استفاده می‌شود.
    همچنین امکان ذخیره و بارگذاری تنظیمات از فایل را فراهم می‌کند.
    """
    
    def __init__(self, name: str = "جستجوی پیشرفته"):
        """مقداردهی اولیه کلاس تنظیمات جستجوی پیشرفته
        
        Args:
            name: نام تنظیمات جستجو
        """
        self.name = name
        self.description = ""
        self.property_type = "all"  # all, residential, commercial, land
        self.deal_type = "all"  # all, sale, rent
        self.criteria = []  # List of search criteria
        self.sort_by = None
        self.sort_order = "ascending"
        self.created_at = datetime.datetime.now()
        self.updated_at = datetime.datetime.now()
    
    def add_criterion(self, field: str, operator: str, value: Any) -> None:
        """افزودن یک معیار جستجو
        
        Args:
            field: نام فیلد
            operator: عملگر مقایسه
            value: مقدار مورد نظر
        """
        self.criteria.append({
            "field": field,
            "operator": operator,
            "value": value
        })
        self.updated_at = datetime.datetime.now()
    
    def clear_criteria(self) -> None:
        """پاک کردن تمام معیارهای جستجو"""
        self.criteria = []
        self.updated_at = datetime.datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """تبدیل تنظیمات به دیکشنری
        
        Returns:
            دیکشنری حاوی تنظیمات
        """
        return {
            "name": self.name,
            "description": self.description,
            "property_type": self.property_type,
            "deal_type": self.deal_type,
            "criteria": self.criteria,
            "sort_by": self.sort_by,
            "sort_order": self.sort_order,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AdvancedSearchConfig':
        """ایجاد تنظیمات از دیکشنری
        
        Args:
            data: دیکشنری حاوی تنظیمات
            
        Returns:
            یک نمونه از کلاس تنظیمات
        """
        config = cls(name=data.get("name", "جستجوی پیشرفته"))
        config.description = data.get("description", "")
        config.property_type = data.get("property_type", "all")
        config.deal_type = data.get("deal_type", "all")
        config.criteria = data.get("criteria", [])
        config.sort_by = data.get("sort_by")
        config.sort_order = data.get("sort_order", "ascending")
        
        if "created_at" in data:
            try:
                config.created_at = datetime.datetime.fromisoformat(data["created_at"])
            except (ValueError, TypeError):
                config.created_at = datetime.datetime.now()
                
        if "updated_at" in data:
            try:
                config.updated_at = datetime.datetime.fromisoformat(data["updated_at"])
            except (ValueError, TypeError):
                config.updated_at = datetime.datetime.now()
                
        return config
    
    def save_to_file(self, file_path: str) -> bool:
        """ذخیره تنظیمات در فایل
        
        Args:
            file_path: مسیر فایل
            
        Returns:
            نتیجه عملیات ذخیره‌سازی
        """
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logging.error(f"خطا در ذخیره تنظیمات جستجو: {e}")
            return False
    
    @classmethod
    def load_from_file(cls, file_path: str) -> Optional['AdvancedSearchConfig']:
        """بارگذاری تنظیمات از فایل
        
        Args:
            file_path: مسیر فایل
            
        Returns:
            تنظیمات بارگذاری شده یا None در صورت خطا
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return cls.from_dict(data)
        except Exception as e:
            logging.error(f"خطا در بارگذاری تنظیمات جستجو: {e}")
            return None


class SearchPresetManager:
    """مدیریت پیش‌تنظیمات جستجو
    
    این کلاس برای مدیریت پیش‌تنظیمات جستجو استفاده می‌شود و امکان
    ذخیره، بارگذاری و حذف پیش‌تنظیمات را فراهم می‌کند.
    """
    
    def __init__(self, presets_dir: str = None):
        """مقداردهی اولیه مدیریت پیش‌تنظیمات
        
        Args:
            presets_dir: دایرکتوری پیش‌تنظیمات
        """
        if presets_dir is None:
            presets_dir = os.path.join(os.path.expanduser("~"), 
                                      "property_management", "search_presets")
        self.presets_dir = presets_dir
        os.makedirs(self.presets_dir, exist_ok=True)
        self._presets = {}
        self._load_presets()
    
    def _load_presets(self) -> None:
        """بارگذاری تمام پیش‌تنظیمات از دایرکتوری"""
        self._presets = {}
        if not os.path.exists(self.presets_dir):
            return
            
        for filename in os.listdir(self.presets_dir):
            if filename.endswith('.json'):
                file_path = os.path.join(self.presets_dir, filename)
                preset = AdvancedSearchConfig.load_from_file(file_path)
                if preset:
                    self._presets[preset.name] = preset
    
    def get_presets(self) -> Dict[str, AdvancedSearchConfig]:
        """دریافت تمام پیش‌تنظیمات
        
        Returns:
            دیکشنری از پیش‌تنظیمات
        """
        return self._presets
    
    def get_preset_names(self) -> List[str]:
        """دریافت نام تمام پیش‌تنظیمات
        
        Returns:
            لیست نام پیش‌تنظیمات
        """
        return list(self._presets.keys())
    
    def get_preset(self, name: str) -> Optional[AdvancedSearchConfig]:
        """دریافت یک پیش‌تنظیم با نام مشخص
        
        Args:
            name: نام پیش‌تنظیم
            
        Returns:
            پیش‌تنظیم یا None اگر یافت نشد
        """
        return self._presets.get(name)
    
    def save_preset(self, config: AdvancedSearchConfig) -> bool:
        """ذخیره یک پیش‌تنظیم
        
        Args:
            config: تنظیمات جستجو
            
        Returns:
            نتیجه عملیات ذخیره‌سازی
        """
        file_path = os.path.join(self.presets_dir, f"{config.name}.json")
        result = config.save_to_file(file_path)
        if result:
            self._presets[config.name] = config
        return result
    
    def delete_preset(self, name: str) -> bool:
        """حذف یک پیش‌تنظیم
        
        Args:
            name: نام پیش‌تنظیم
            
        Returns:
            نتیجه عملیات حذف
        """
        if name not in self._presets:
            return False
            
        file_path = os.path.join(self.presets_dir, f"{name}.json")
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
            del self._presets[name]
            return True
        except Exception as e:
            logging.error(f"خطا در حذف پیش‌تنظیم: {e}")
            return False


class AdvancedSearch:
    """کلاس جستجوی پیشرفته املاک
    
    این کلاس رابط بین موتور جستجو و مدل فیلتر است و
    برای جستجوی پیشرفته املاک استفاده می‌شود.
    """
    
    def __init__(self, data_dir: str = None):
        """مقداردهی اولیه کلاس جستجوی پیشرفته
        
        Args:
            data_dir: دایرکتوری داده‌ها
        """
        self.search_engine = SearchEngine()
        self.report_generator = ReportGenerator()
        self.preset_manager = SearchPresetManager()
        self.config = AdvancedSearchConfig()
        self._results = None
        self._results_df = None
        
        # تنظیم دایرکتوری داده‌ها اگر ارائه شده باشد
        if data_dir:
            self.search_engine.set_data_dir(data_dir)
            self.report_generator.set_output_dir(os.path.join(data_dir, "reports"))
    
    def set_property_type(self, property_type: str) -> None:
        """تنظیم نوع ملک
        
        Args:
            property_type: نوع ملک (residential, commercial, land, all)
        """
        if property_type not in ["residential", "commercial", "land", "all"]:
            raise ValueError("نوع ملک نامعتبر است")
        self.config.property_type = property_type
    
    def set_deal_type(self, deal_type: str) -> None:
        """تنظیم نوع معامله
        
        Args:
            deal_type: نوع معامله (sale, rent, all)
        """
        if deal_type not in ["sale", "rent", "all"]:
            raise ValueError("نوع معامله نامعتبر است")
        self.config.deal_type = deal_type
    
    def add_criterion(self, field: str, operator: str, value: Any) -> None:
        """افزودن یک معیار جستجو
        
        Args:
            field: نام فیلد
            operator: عملگر مقایسه
            value: مقدار مورد نظر
        """
        self.config.add_criterion(field, operator, value)
    
    def clear_criteria(self) -> None:
        """پاک کردن تمام معیارهای جستجو"""
        self.config.clear_criteria()
    
    def set_sort(self, field: str, order: str = "ascending") -> None:
        """تنظیم مرتب‌سازی نتایج
        
        Args:
            field: فیلد مرتب‌سازی
            order: ترتیب مرتب‌سازی (ascending, descending)
        """
        if order not in ["ascending", "descending"]:
            raise ValueError("ترتیب مرتب‌سازی نامعتبر است")
        self.config.sort_by = field
        self.config.sort_order = order
    
    def _build_search_criteria(self) -> SearchCriteria:
        """ساخت معیارهای جستجو برای موتور جستجو
        
        Returns:
            معیارهای جستجو
        """
        criteria = SearchCriteria()
        
        # اضافه کردن معیارهای جستجو
        for criterion in self.config.criteria:
            field = criterion["field"]
            operator_str = criterion["operator"]
            value = criterion["value"]
            
            # تبدیل عملگر رشته‌ای به عملگر شیء
            operator = SearchOperator.from_string(operator_str)
            
            # اضافه کردن شرط به معیارهای جستجو
            condition = SearchCondition(field, operator, value)
            criteria.add_condition(condition)
        
        return criteria
    
    def search(self) -> pd.DataFrame:
        """اجرای جستجو بر اساس معیارهای تنظیم شده
        
        Returns:
            دیتافریم حاوی نتایج جستجو
        """
        # ساخت معیارهای جستجو
        criteria = self._build_search_criteria()
        
        # تنظیم نوع ملک
        property_types = []
        if self.config.property_type == "all":
            property_types = ["residential", "commercial", "land"]
        else:
            property_types = [self.config.property_type]
        
        # تنظیم نوع معامله
        deal_types = []
        if self.config.deal_type == "all":
            deal_types = ["sale", "rent"]
        else:
            deal_types = [self.config.deal_type]
        
        # اجرای جستجو و ذخیره نتایج
        self._results = self.search_engine.search(
            criteria=criteria,
            property_types=property_types,
            deal_types=deal_types
        )
        
        # تبدیل نتایج به دیتافریم
        self._results_df = self._results.to_dataframe()
        
        # مرتب‌سازی نتایج اگر فیلد مرتب‌سازی تنظیم شده باشد
        if self.config.sort_by and self.config.sort_by in self._results_df.columns:
            ascending = self.config.sort_order == "ascending"
            self._results_df = self._results_df.sort_values(
                by=self.config.sort_by, 
                ascending=ascending
            )
        
        return self._results_df
    
    def get_results_dataframe(self) -> Optional[pd.DataFrame]:
        """دریافت نتایج جستجو به صورت دیتافریم
        
        Returns:
            دیتافریم نتایج یا None اگر جستجو انجام نشده باشد
        """
        return self._results_df
    
    def get_results(self) -> Optional[Any]:
        """دریافت نتایج جستجو
        
        Returns:
            نتایج خام جستجو یا None اگر جستجو انجام نشده باشد
        """
        return self._results
    
    def create_table_model(self) -> Optional[PropertyTableModel]:
        """ایجاد مدل جدول برای نتایج جستجو
        
        Returns:
            مدل جدول یا None اگر جستجو انجام نشده باشد
        """
        if self._results_df is None:
            return None
            
        model = PropertyTableModel()
        model.set_dataframe(self._results_df)
        return model
    
    def export_results(self, format_type: str, file_path: str = None, 
                       metadata: Dict[str, str] = None) -> bool:
        """صادر کردن نتایج جستجو
        
        Args:
            format_type: نوع فرمت (excel, pdf)
            file_path: مسیر فایل خروجی
            metadata: اطلاعات توضیحی
            
        Returns:
            نتیجه عملیات صادرسازی
        """
        if self._results_df is None or self._results_df.empty:
            logging.warning("نتایج جستجو خالی است")
            return False
            
        if not metadata:
            metadata = {
                "title": f"نتایج جستجوی {self.config.name}",
                "description": self.config.description or "نتایج جستجوی پیشرفته املاک",
                "author": "سیستم مدیریت املاک",
                "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
        # اگر مسیر فایل ارائه نشده باشد، یک مسیر پیش‌فرض تولید کن
        if not file_path:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"search_results_{timestamp}.{format_type}"
            file_path = os.path.join(
                self.report_generator.output_dir, 
                filename
            )
            
        # صادر کردن داده‌ها
        try:
            export_data(
                self._results_df,
                format_type=format_type,
                file_path=file_path,
                metadata=metadata
            )
            logging.info(f"نتایج جستجو با موفقیت در {file_path} ذخیره شد")
            return True
        except Exception as e:
            logging.error(f"خطا در صادر کردن نتایج: {e}")
            return False
    
    def load_preset(self, name: str) -> bool:
        """بارگذاری یک پیش‌تنظیم جستجو
        
        Args:
            name: نام پیش‌تنظیم
            
        Returns:
            نتیجه عملیات بارگذاری
        """
        preset = self.preset_manager.get_preset(name)
        if not preset:
            logging.warning(f"پیش‌تنظیم {name} یافت نشد")
            return False
            
        self.config = preset
        return True
    
    def save_preset(self, name: str = None, description: str = None) -> bool:
        """ذخیره تنظیمات فعلی به عنوان یک پیش‌تنظیم
        
        Args:
            name: نام پیش‌تنظیم
            description: توضیحات پیش‌تنظیم
            
        Returns:
            نتیجه عملیات ذخیره‌سازی
        """
        if name:
            self.config.name = name
        if description:
            self.config.description = description
            
        return self.preset_manager.save_preset(self.config)
    
    def generate_analysis_report(self, report_type: str, 
                                format_type: str = "excel",
                                file_path: str = None) -> bool:
        """تولید گزارش تحلیلی از نتایج جستجو
        
        Args:
            report_type: نوع گزارش (district, price_range, property_count, property_value)
            format_type: نوع فرمت خروجی (text, csv, excel, pdf)
            file_path: مسیر فایل خروجی
            
        Returns:
            نتیجه عملیات تولید گزارش
        """
        if self._results_df is None or self._results_df.empty:
            logging.warning("نتایج جستجو خالی است")
            return False
            
        # تنظیم مسیر فایل خروجی اگر ارائه نشده باشد
        if not file_path:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{report_type}_report_{timestamp}.{format_type}"
            file_path = os.path.join(
                self.report_generator.output_dir, 
                filename
            )
            
        # تولید گزارش بر اساس نوع گزارش
        try:
            if report_type == "district":
                self.report_generator.generate_district_report(
                    deal_type=self.config.deal_type,
                    output_format=format_type,
                    output_file=file_path,
                    properties_df=self._results_df
                )
            elif report_type == "price_range":
                self.report_generator.generate_price_range_report(
                    deal_type=self.config.deal_type,
                    output_format=format_type,
                    output_file=file_path,
                    properties_df=self._results_df
                )
            elif report_type == "property_count":
                self.report_generator.generate_property_count_report(
                    deal_type=self.config.deal_type,
                    output_format=format_type,
                    output_file=file_path,
                    properties_df=self._results_df
                )
            elif report_type == "property_value":
                self.report_generator.generate_property_value_report(
                    deal_type="sale",  # فقط برای املاک فروشی
                    output_format=format_type,
                    output_file=file_path,
                    properties_df=self._results_df
                )
            else:
                logging.error(f"نوع گزارش {report_type} نامعتبر است")
                return False
                
            logging.info(f"گزارش {report_type} با موفقیت در {file_path} ذخیره شد")
            return True
        except Exception as e:
            logging.error(f"خطا در تولید گزارش {report_type}: {e}")
            return False 