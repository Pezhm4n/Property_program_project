#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ماژول موتور جستجوی پیشرفته برای سیستم مدیریت املاک

این ماژول شامل کلاس‌های مورد نیاز برای جستجوی پیشرفته در داده‌های املاک است.
"""

import os
import re
import json
import logging
import datetime
from typing import List, Dict, Any, Optional, Tuple, Union, Callable
from enum import Enum, auto

# وابستگی‌های خارجی
import pandas as pd
from PyQt5.QtCore import Qt, QModelIndex, QSortFilterProxyModel, QRegExp, QDate

# وارد کردن ماژول‌های داخلی سیستم
from .core import get_property_bridge

# تنظیمات لاگینگ
logger = logging.getLogger(__name__)

class SearchOperator(Enum):
    """
    عملگرهای جستجو
    """
    EQUAL = auto()             # ==
    NOT_EQUAL = auto()         # !=
    GREATER_THAN = auto()      # >
    GREATER_EQUAL = auto()     # >=
    LESS_THAN = auto()         # <
    LESS_EQUAL = auto()        # <=
    BETWEEN = auto()           # بین دو مقدار
    CONTAINS = auto()          # شامل
    STARTS_WITH = auto()       # شروع با
    ENDS_WITH = auto()         # پایان با
    REGEX = auto()             # الگوی عبارت منظم
    IS_NULL = auto()           # مقدار خالی
    IS_NOT_NULL = auto()       # مقدار غیر خالی
    IN = auto()                # در لیست
    NOT_IN = auto()            # خارج از لیست
    
    @classmethod
    def from_string(cls, operator_str: str) -> 'SearchOperator':
        """
        تبدیل رشته به عملگر جستجو
        
        Args:
            operator_str (str): رشته عملگر
            
        Returns:
            SearchOperator: عملگر جستجو
        """
        mapping = {
            '=': cls.EQUAL,
            '==': cls.EQUAL,
            '!=': cls.NOT_EQUAL,
            '<>': cls.NOT_EQUAL,
            '>': cls.GREATER_THAN,
            '>=': cls.GREATER_EQUAL,
            '<': cls.LESS_THAN,
            '<=': cls.LESS_EQUAL,
            'between': cls.BETWEEN,
            'contains': cls.CONTAINS,
            'starts_with': cls.STARTS_WITH,
            'ends_with': cls.ENDS_WITH,
            'regex': cls.REGEX,
            'is_null': cls.IS_NULL,
            'is_not_null': cls.IS_NOT_NULL,
            'in': cls.IN,
            'not_in': cls.NOT_IN
        }
        
        return mapping.get(operator_str.lower(), cls.EQUAL)


class SearchCondition:
    """
    شرط جستجو برای یک فیلد
    """
    
    def __init__(self, field: str, operator: SearchOperator = SearchOperator.EQUAL, 
                value: Any = None, value2: Any = None):
        """
        مقداردهی اولیه کلاس SearchCondition
        
        Args:
            field (str): نام فیلد
            operator (SearchOperator, optional): عملگر جستجو
            value (Any, optional): مقدار اول
            value2 (Any, optional): مقدار دوم (برای عملگرهایی مانند BETWEEN)
        """
        self.field = field
        self.operator = operator
        self.value = value
        self.value2 = value2
    
    def evaluate(self, item: Dict) -> bool:
        """
        ارزیابی شرط جستجو بر روی یک آیتم
        
        Args:
            item (Dict): آیتم داده
            
        Returns:
            bool: نتیجه ارزیابی
        """
        # اگر فیلد در آیتم وجود نداشته باشد
        if self.field not in item:
            return False
        
        field_value = item[self.field]
        
        # بررسی مقدار خالی
        if self.operator == SearchOperator.IS_NULL:
            return field_value is None or pd.isna(field_value) or field_value == ""
        
        if self.operator == SearchOperator.IS_NOT_NULL:
            return field_value is not None and not pd.isna(field_value) and field_value != ""
        
        # اگر مقدار فیلد خالی باشد و عملگر بررسی خالی بودن نباشد
        if field_value is None or pd.isna(field_value) or field_value == "":
            return False
        
        # تبدیل نوع داده برای مقایسه صحیح
        compare_value = self._convert_value_type(field_value, self.value)
        
        if self.operator == SearchOperator.EQUAL:
            return field_value == compare_value
        
        elif self.operator == SearchOperator.NOT_EQUAL:
            return field_value != compare_value
        
        elif self.operator == SearchOperator.GREATER_THAN:
            return field_value > compare_value
        
        elif self.operator == SearchOperator.GREATER_EQUAL:
            return field_value >= compare_value
        
        elif self.operator == SearchOperator.LESS_THAN:
            return field_value < compare_value
        
        elif self.operator == SearchOperator.LESS_EQUAL:
            return field_value <= compare_value
        
        elif self.operator == SearchOperator.BETWEEN:
            compare_value2 = self._convert_value_type(field_value, self.value2)
            return compare_value <= field_value <= compare_value2
        
        elif self.operator == SearchOperator.CONTAINS:
            return str(compare_value).lower() in str(field_value).lower()
        
        elif self.operator == SearchOperator.STARTS_WITH:
            return str(field_value).lower().startswith(str(compare_value).lower())
        
        elif self.operator == SearchOperator.ENDS_WITH:
            return str(field_value).lower().endswith(str(compare_value).lower())
        
        elif self.operator == SearchOperator.REGEX:
            try:
                pattern = re.compile(str(compare_value), re.IGNORECASE)
                return bool(pattern.search(str(field_value)))
            except:
                return False
        
        elif self.operator == SearchOperator.IN:
            if not isinstance(compare_value, (list, tuple)):
                compare_value = [compare_value]
            return field_value in compare_value
        
        elif self.operator == SearchOperator.NOT_IN:
            if not isinstance(compare_value, (list, tuple)):
                compare_value = [compare_value]
            return field_value not in compare_value
        
        return False
    
    def _convert_value_type(self, field_value: Any, compare_value: Any) -> Any:
        """
        تبدیل نوع داده مقدار مقایسه به نوع داده فیلد
        
        Args:
            field_value (Any): مقدار فیلد
            compare_value (Any): مقدار مقایسه
            
        Returns:
            Any: مقدار مقایسه تبدیل شده
        """
        if compare_value is None:
            return None
        
        if isinstance(field_value, bool):
            if isinstance(compare_value, str):
                return compare_value.lower() in ('true', 'yes', 'y', '1')
            return bool(compare_value)
        
        elif isinstance(field_value, int):
            try:
                return int(compare_value)
            except:
                return 0
        
        elif isinstance(field_value, float):
            try:
                return float(compare_value)
            except:
                return 0.0
        
        elif isinstance(field_value, (datetime.date, datetime.datetime)):
            if isinstance(compare_value, str):
                try:
                    return datetime.datetime.strptime(compare_value, '%Y-%m-%d').date()
                except:
                    try:
                        return datetime.datetime.strptime(compare_value, '%Y-%m-%d %H:%M:%S')
                    except:
                        return datetime.datetime.now()
            return compare_value
        
        return compare_value
    
    def __str__(self) -> str:
        """
        تبدیل شرط به رشته
        
        Returns:
            str: نمایش متنی شرط
        """
        op_str = {
            SearchOperator.EQUAL: "=",
            SearchOperator.NOT_EQUAL: "!=",
            SearchOperator.GREATER_THAN: ">",
            SearchOperator.GREATER_EQUAL: ">=",
            SearchOperator.LESS_THAN: "<",
            SearchOperator.LESS_EQUAL: "<=",
            SearchOperator.BETWEEN: "between",
            SearchOperator.CONTAINS: "contains",
            SearchOperator.STARTS_WITH: "starts with",
            SearchOperator.ENDS_WITH: "ends with",
            SearchOperator.REGEX: "matches",
            SearchOperator.IS_NULL: "is null",
            SearchOperator.IS_NOT_NULL: "is not null",
            SearchOperator.IN: "in",
            SearchOperator.NOT_IN: "not in"
        }
        
        if self.operator == SearchOperator.BETWEEN:
            return f"{self.field} {op_str[self.operator]} {self.value} and {self.value2}"
        elif self.operator in (SearchOperator.IS_NULL, SearchOperator.IS_NOT_NULL):
            return f"{self.field} {op_str[self.operator]}"
        elif self.operator in (SearchOperator.IN, SearchOperator.NOT_IN):
            return f"{self.field} {op_str[self.operator]} {self.value}"
        else:
            return f"{self.field} {op_str[self.operator]} {self.value}"


class SearchCriteria:
    """
    معیارهای جستجو، شامل چندین شرط و نوع منطقی اتصال آنها
    """
    
    def __init__(self, property_type: str = 'all', deal_type: int = None, 
                conditions: List[SearchCondition] = None, use_and: bool = True,
                max_results: int = 1000):
        """
        مقداردهی اولیه کلاس SearchCriteria
        
        Args:
            property_type (str, optional): نوع ملک ('residential', 'commercial', 'land', 'all')
            deal_type (int, optional): نوع معامله (1: فروش، 2: اجاره)
            conditions (List[SearchCondition], optional): لیست شرط‌های جستجو
            use_and (bool, optional): آیا از عملگر AND برای اتصال شرط‌ها استفاده شود؟
            max_results (int, optional): حداکثر تعداد نتایج
        """
        self.property_type = property_type
        self.deal_type = deal_type
        self.conditions = conditions if conditions else []
        self.use_and = use_and
        self.max_results = max_results
    
    def add_condition(self, condition: SearchCondition) -> None:
        """
        اضافه کردن یک شرط به معیارهای جستجو
        
        Args:
            condition (SearchCondition): شرط جستجو
        """
        self.conditions.append(condition)
    
    def evaluate(self, item: Dict) -> bool:
        """
        ارزیابی معیارهای جستجو بر روی یک آیتم
        
        Args:
            item (Dict): آیتم داده
            
        Returns:
            bool: نتیجه ارزیابی
        """
        if not self.conditions:
            return True
        
        if self.use_and:
            # همه شرط‌ها باید برقرار باشند (AND)
            return all(condition.evaluate(item) for condition in self.conditions)
        else:
            # حداقل یک شرط باید برقرار باشد (OR)
            return any(condition.evaluate(item) for condition in self.conditions)
    
    def to_dict(self) -> Dict:
        """
        تبدیل معیارهای جستجو به دیکشنری
        
        Returns:
            Dict: دیکشنری معیارهای جستجو
        """
        return {
            'property_type': self.property_type,
            'deal_type': self.deal_type,
            'use_and': self.use_and,
            'max_results': self.max_results,
            'conditions': [
                {
                    'field': condition.field,
                    'operator': condition.operator.name,
                    'value': condition.value,
                    'value2': condition.value2
                }
                for condition in self.conditions
            ]
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'SearchCriteria':
        """
        ایجاد معیارهای جستجو از دیکشنری
        
        Args:
            data (Dict): دیکشنری معیارهای جستجو
            
        Returns:
            SearchCriteria: شیء معیارهای جستجو
        """
        criteria = cls(
            property_type=data.get('property_type', 'all'),
            deal_type=data.get('deal_type'),
            use_and=data.get('use_and', True),
            max_results=data.get('max_results', 1000)
        )
        
        for condition_data in data.get('conditions', []):
            operator = SearchOperator[condition_data.get('operator', 'EQUAL')]
            condition = SearchCondition(
                field=condition_data.get('field', ''),
                operator=operator,
                value=condition_data.get('value'),
                value2=condition_data.get('value2')
            )
            criteria.add_condition(condition)
        
        return criteria
    
    def save_to_file(self, filename: str) -> bool:
        """
        ذخیره معیارهای جستجو در فایل
        
        Args:
            filename (str): نام فایل
            
        Returns:
            bool: نتیجه عملیات
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Error saving search criteria to file: {str(e)}")
            return False
    
    @classmethod
    def load_from_file(cls, filename: str) -> Optional['SearchCriteria']:
        """
        بارگذاری معیارهای جستجو از فایل
        
        Args:
            filename (str): نام فایل
            
        Returns:
            Optional[SearchCriteria]: شیء معیارهای جستجو یا None در صورت خطا
        """
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return cls.from_dict(data)
        except Exception as e:
            logger.error(f"Error loading search criteria from file: {str(e)}")
            return None
    
    def __str__(self) -> str:
        """
        تبدیل معیارهای جستجو به رشته
        
        Returns:
            str: نمایش متنی معیارهای جستجو
        """
        connector = " AND " if self.use_and else " OR "
        conditions_str = connector.join(str(condition) for condition in self.conditions)
        
        property_type_str = self.property_type if self.property_type != 'all' else 'All Properties'
        deal_type_str = ''
        if self.deal_type is not None:
            deal_type_str = f" (Sale)" if self.deal_type == 1 else f" (Rent)"
        
        return f"{property_type_str}{deal_type_str}: {conditions_str}"


class SearchEngine:
    """
    موتور جستجو برای اعمال معیارهای جستجو بر روی داده‌های املاک
    """
    
    def __init__(self):
        """
        مقداردهی اولیه کلاس SearchEngine
        """
        self.property_bridge = get_property_bridge()
        self.criteria = None
        self.results = []
        self.total_results = 0
        
        logger.info("Search engine initialized")
    
    def set_criteria(self, criteria: SearchCriteria) -> None:
        """
        تنظیم معیارهای جستجو
        
        Args:
            criteria (SearchCriteria): معیارهای جستجو
        """
        self.criteria = criteria
    
    def search(self, criteria: SearchCriteria = None) -> List[Dict]:
        """
        جستجو بر اساس معیارهای تعیین شده
        
        Args:
            criteria (SearchCriteria, optional): معیارهای جستجو
            
        Returns:
            List[Dict]: نتایج جستجو
        """
        if criteria:
            self.set_criteria(criteria)
        
        if not self.criteria:
            logger.warning("No search criteria set")
            return []
        
        self.results = []
        self.total_results = 0
        
        try:
            # دریافت داده‌ها از پل ارتباطی
            deal_type = self.criteria.deal_type
            property_type = self.criteria.property_type
            
            # جستجو در املاک مسکونی
            if property_type == 'all' or property_type == 'residential':
                self._search_residential(deal_type)
            
            # جستجو در املاک تجاری
            if property_type == 'all' or property_type == 'commercial':
                self._search_commercial(deal_type)
            
            # جستجو در زمین‌ها
            if property_type == 'all' or property_type == 'land':
                self._search_land(deal_type)
            
            # اعمال محدودیت تعداد نتایج
            if len(self.results) > self.criteria.max_results:
                self.results = self.results[:self.criteria.max_results]
            
            logger.info(f"Search completed. Found {self.total_results} results, returning {len(self.results)}")
            return self.results
            
        except Exception as e:
            logger.error(f"Error during search: {str(e)}")
            return []
    
    def _search_residential(self, deal_type: int = None) -> None:
        """
        جستجو در املاک مسکونی
        
        Args:
            deal_type (int, optional): نوع معامله
        """
        try:
            # تعیین نوع‌های معامله برای جستجو
            deal_types = [1, 2] if deal_type is None else [deal_type]
            
            for dt in deal_types:
                # جستجوی تمام املاک مسکونی
                all_properties_response = self.property_bridge.residential_bridge.find_by_district("*", dt)
                
                if all_properties_response.get("success", False):
                    properties = all_properties_response.get("properties", [])
                    
                    # اعمال معیارهای جستجو
                    for prop in properties:
                        # اضافه کردن فیلد نوع ملک برای تفکیک نتایج
                        prop['property_type'] = 'residential'
                        
                        if self.criteria.evaluate(prop):
                            self.results.append(prop)
                    
                    self.total_results += len(properties)
        except Exception as e:
            logger.error(f"Error searching residential properties: {str(e)}")
    
    def _search_commercial(self, deal_type: int = None) -> None:
        """
        جستجو در املاک تجاری
        
        Args:
            deal_type (int, optional): نوع معامله
        """
        try:
            # تعیین نوع‌های معامله برای جستجو
            deal_types = [1, 2] if deal_type is None else [deal_type]
            
            for dt in deal_types:
                # جستجوی تمام املاک تجاری
                all_properties_response = self.property_bridge.commercial_bridge.find_by_district("*", dt)
                
                if all_properties_response.get("success", False):
                    properties = all_properties_response.get("properties", [])
                    
                    # اعمال معیارهای جستجو
                    for prop in properties:
                        # اضافه کردن فیلد نوع ملک برای تفکیک نتایج
                        prop['property_type'] = 'commercial'
                        
                        if self.criteria.evaluate(prop):
                            self.results.append(prop)
                    
                    self.total_results += len(properties)
        except Exception as e:
            logger.error(f"Error searching commercial properties: {str(e)}")
    
    def _search_land(self, deal_type: int = None) -> None:
        """
        جستجو در زمین‌ها
        
        Args:
            deal_type (int, optional): نوع معامله
        """
        try:
            # تعیین نوع‌های معامله برای جستجو
            deal_types = [1, 2] if deal_type is None else [deal_type]
            
            for dt in deal_types:
                # جستجوی تمام زمین‌ها
                all_properties_response = self.property_bridge.land_bridge.find_by_district("*", dt)
                
                if all_properties_response.get("success", False):
                    properties = all_properties_response.get("properties", [])
                    
                    # اعمال معیارهای جستجو
                    for prop in properties:
                        # اضافه کردن فیلد نوع ملک برای تفکیک نتایج
                        prop['property_type'] = 'land'
                        
                        if self.criteria.evaluate(prop):
                            self.results.append(prop)
                    
                    self.total_results += len(properties)
        except Exception as e:
            logger.error(f"Error searching land properties: {str(e)}")
    
    def sort_results(self, field: str, ascending: bool = True) -> List[Dict]:
        """
        مرتب‌سازی نتایج جستجو
        
        Args:
            field (str): فیلد مرتب‌سازی
            ascending (bool, optional): ترتیب صعودی؟
            
        Returns:
            List[Dict]: نتایج مرتب شده
        """
        try:
            # تبدیل به دیتافریم برای مرتب‌سازی آسان‌تر
            df = pd.DataFrame(self.results)
            
            if field in df.columns:
                df.sort_values(by=field, ascending=ascending, inplace=True)
                
                # تبدیل به لیست دیکشنری
                self.results = df.to_dict('records')
            
            return self.results
        except Exception as e:
            logger.error(f"Error sorting results: {str(e)}")
            return self.results
    
    def group_results(self, field: str) -> Dict[str, List[Dict]]:
        """
        گروه‌بندی نتایج جستجو
        
        Args:
            field (str): فیلد گروه‌بندی
            
        Returns:
            Dict[str, List[Dict]]: نتایج گروه‌بندی شده
        """
        try:
            groups = {}
            
            for item in self.results:
                group_key = item.get(field, 'Unknown')
                
                if group_key not in groups:
                    groups[group_key] = []
                
                groups[group_key].append(item)
            
            return groups
        except Exception as e:
            logger.error(f"Error grouping results: {str(e)}")
            return {}
    
    def to_dataframe(self) -> pd.DataFrame:
        """
        تبدیل نتایج به دیتافریم pandas
        
        Returns:
            pd.DataFrame: دیتافریم نتایج
        """
        return pd.DataFrame(self.results)
    
    def get_summary_stats(self) -> Dict:
        """
        دریافت آمار خلاصه از نتایج
        
        Returns:
            Dict: آمار خلاصه
        """
        stats = {
            'total_count': len(self.results),
            'property_types': {}
        }
        
        # شمارش انواع املاک
        for item in self.results:
            prop_type = item.get('property_type', 'unknown')
            
            if prop_type not in stats['property_types']:
                stats['property_types'][prop_type] = 0
            
            stats['property_types'][prop_type] += 1
        
        # آمار قیمت
        if self.results:
            df = self.to_dataframe()
            
            # قیمت فروش
            if 'sellingPrice' in df.columns:
                price_stats = df['sellingPrice'].describe().to_dict()
                stats['selling_price'] = {
                    'min': price_stats['min'],
                    'max': price_stats['max'],
                    'avg': price_stats['mean'],
                    'median': price_stats['50%']
                }
            
            # قیمت رهن
            if 'mortgageAmount' in df.columns:
                price_stats = df['mortgageAmount'].describe().to_dict()
                stats['mortgage_amount'] = {
                    'min': price_stats['min'],
                    'max': price_stats['max'],
                    'avg': price_stats['mean'],
                    'median': price_stats['50%']
                }
            
            # قیمت اجاره
            if 'monthlyRentAmount' in df.columns:
                price_stats = df['monthlyRentAmount'].describe().to_dict()
                stats['monthly_rent'] = {
                    'min': price_stats['min'],
                    'max': price_stats['max'],
                    'avg': price_stats['mean'],
                    'median': price_stats['50%']
                }
        
        return stats 