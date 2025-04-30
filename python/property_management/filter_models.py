#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ماژول مدل‌های فیلتر برای سیستم مدیریت املاک

این ماژول شامل مدل‌های فیلتر مورد استفاده در رابط کاربری Qt برای نمایش و فیلتر کردن داده‌های املاک است.
"""

import logging
from typing import List, Dict, Any, Optional, Union, Callable
from datetime import datetime

from PyQt5.QtCore import (Qt, QAbstractTableModel, QSortFilterProxyModel, 
                         QModelIndex, QVariant, QRegExp, pyqtSignal, QDate)
from PyQt5.QtGui import QColor, QBrush

# تنظیمات لاگینگ
logger = logging.getLogger(__name__)

class PropertyTableModel(QAbstractTableModel):
    """
    مدل داده برای نمایش مشخصات املاک در یک جدول
    """
    
    def __init__(self, properties=None, parent=None):
        """
        مقداردهی اولیه مدل جدول املاک
        
        Args:
            properties (List[Dict], optional): لیست املاک
            parent (QObject, optional): والد QT
        """
        super(PropertyTableModel, self).__init__(parent)
        self._properties = properties if properties else []
        self._headers = []
        self._column_map = {}
        self._setup_columns()
    
    def _setup_columns(self):
        """
        تنظیم اطلاعات ستون‌ها برای نمایش در جدول
        """
        # تعریف ستون‌های پیش‌فرض برای نمایش
        # هر آیتم شامل (عنوان ستون، کلید در دیکشنری داده، تابع تبدیل نمایش)
        columns = [
            {"title": "شناسه", "key": "id", "display": lambda x: str(x)},
            {"title": "منطقه", "key": "district", "display": lambda x: str(x)},
            {"title": "نوع ملک", "key": "property_type", "display": self._format_property_type},
            {"title": "متراژ", "key": "area", "display": lambda x: f"{x} متر مربع" if x else ""},
            {"title": "قیمت فروش", "key": "sellingPrice", "display": self._format_price},
            {"title": "مبلغ رهن", "key": "mortgageAmount", "display": self._format_price},
            {"title": "اجاره ماهانه", "key": "monthlyRentAmount", "display": self._format_price},
            {"title": "تعداد اتاق", "key": "bedrooms", "display": lambda x: str(x) if x else ""},
            {"title": "سن بنا", "key": "age", "display": lambda x: f"{x} سال" if x is not None else ""},
            {"title": "آدرس", "key": "address", "display": lambda x: str(x) if x else ""},
            {"title": "تاریخ ثبت", "key": "registrationDate", "display": self._format_date},
            {"title": "کاربر ثبت کننده", "key": "username", "display": lambda x: str(x) if x else ""},
        ]
        
        self._headers = [col["title"] for col in columns]
        
        # ایجاد نگاشت بین شماره ستون و اطلاعات آن
        for i, col in enumerate(columns):
            self._column_map[i] = col
    
    def _format_property_type(self, value):
        """
        تبدیل نوع ملک به نمایش فارسی
        
        Args:
            value (str): نوع ملک
            
        Returns:
            str: نمایش فارسی نوع ملک
        """
        type_map = {
            'residential': 'مسکونی',
            'commercial': 'تجاری',
            'land': 'زمین'
        }
        return type_map.get(value, value)
    
    def _format_price(self, value):
        """
        قالب‌بندی قیمت با جداکننده هزارگان
        
        Args:
            value (int): قیمت
            
        Returns:
            str: قیمت قالب‌بندی شده
        """
        if value is None or value == 0:
            return ""
        
        return f"{value:,} تومان"
    
    def _format_date(self, value):
        """
        قالب‌بندی تاریخ
        
        Args:
            value (str): تاریخ به فرمت ISO
            
        Returns:
            str: تاریخ قالب‌بندی شده
        """
        if not value:
            return ""
        
        try:
            date_obj = datetime.strptime(value, "%Y-%m-%d")
            return date_obj.strftime("%Y/%m/%d")
        except:
            return value
    
    def rowCount(self, parent=QModelIndex()):
        """
        تعداد سطرهای جدول
        
        Args:
            parent (QModelIndex, optional): اندیس والد
            
        Returns:
            int: تعداد سطرها
        """
        return len(self._properties)
    
    def columnCount(self, parent=QModelIndex()):
        """
        تعداد ستون‌های جدول
        
        Args:
            parent (QModelIndex, optional): اندیس والد
            
        Returns:
            int: تعداد ستون‌ها
        """
        return len(self._headers)
    
    def data(self, index, role=Qt.DisplayRole):
        """
        دریافت داده برای نمایش در جدول
        
        Args:
            index (QModelIndex): اندیس آیتم
            role (int, optional): نقش داده
            
        Returns:
            QVariant: داده مورد نظر
        """
        if not index.isValid() or not (0 <= index.row() < len(self._properties)):
            return QVariant()
        
        property_item = self._properties[index.row()]
        column = index.column()
        column_info = self._column_map.get(column)
        
        if column_info is None:
            return QVariant()
        
        if role == Qt.DisplayRole:
            # داده برای نمایش
            value = property_item.get(column_info["key"])
            display_func = column_info.get("display", lambda x: str(x) if x is not None else "")
            return display_func(value)
        
        elif role == Qt.BackgroundRole:
            # رنگ پس‌زمینه برای ردیف‌های زوج/فرد
            return QBrush(QColor(240, 240, 240)) if index.row() % 2 == 0 else QBrush(QColor(255, 255, 255))
        
        return QVariant()
    
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        """
        دریافت داده برای نمایش در سرستون‌ها
        
        Args:
            section (int): شماره بخش
            orientation (Qt.Orientation): جهت
            role (int, optional): نقش داده
            
        Returns:
            QVariant: داده مورد نظر
        """
        if role != Qt.DisplayRole:
            return QVariant()
        
        if orientation == Qt.Horizontal:
            # سرستون‌های افقی
            return self._headers[section] if 0 <= section < len(self._headers) else QVariant()
        
        return QVariant()
    
    def flags(self, index):
        """
        پرچم‌های مربوط به آیتم
        
        Args:
            index (QModelIndex): اندیس آیتم
            
        Returns:
            Qt.ItemFlags: پرچم‌های آیتم
        """
        if not index.isValid():
            return Qt.NoItemFlags
        
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable
    
    def setProperties(self, properties):
        """
        تنظیم لیست املاک جدید
        
        Args:
            properties (List[Dict]): لیست املاک
        """
        self.beginResetModel()
        self._properties = properties if properties else []
        self.endResetModel()
    
    def getProperty(self, row):
        """
        دریافت اطلاعات یک ملک با شماره ردیف
        
        Args:
            row (int): شماره ردیف
            
        Returns:
            Dict: اطلاعات ملک یا None
        """
        if 0 <= row < len(self._properties):
            return self._properties[row]
        return None
    
    def getDataKey(self, column):
        """
        دریافت کلید داده مرتبط با یک ستون
        
        Args:
            column (int): شماره ستون
            
        Returns:
            str: کلید داده یا None
        """
        column_info = self._column_map.get(column)
        if column_info:
            return column_info.get("key")
        return None


class PropertyFilterProxyModel(QSortFilterProxyModel):
    """
    مدل پروکسی برای فیلتر کردن و مرتب‌سازی داده‌های املاک
    """
    
    def __init__(self, parent=None):
        """
        مقداردهی اولیه مدل پروکسی
        
        Args:
            parent (QObject, optional): والد QT
        """
        super(PropertyFilterProxyModel, self).__init__(parent)
        
        # فیلترهای عددی
        self._min_price = None
        self._max_price = None
        self._min_area = None
        self._max_area = None
        self._min_bedrooms = None
        self._max_bedrooms = None
        self._min_age = None
        self._max_age = None
        
        # فیلترهای رشته‌ای
        self._district_filter = None
        self._property_type_filter = None
        self._username_filter = None
        
        # فیلترهای تاریخ
        self._min_date = None
        self._max_date = None
        
        # نوع معامله
        self._deal_type = None  # 1: فروش، 2: اجاره
        
        # تنظیم حساسیت به بزرگی و کوچکی حروف
        self.setFilterCaseSensitivity(Qt.CaseInsensitive)
    
    def filterAcceptsRow(self, source_row, source_parent):
        """
        تعیین می‌کند آیا ردیف مورد نظر با فیلترها مطابقت دارد
        
        Args:
            source_row (int): شماره ردیف در مدل اصلی
            source_parent (QModelIndex): اندیس والد
            
        Returns:
            bool: آیا ردیف با فیلترها مطابقت دارد
        """
        source_model = self.sourceModel()
        property_item = source_model.getProperty(source_row)
        
        if not property_item:
            return False
        
        # بررسی نوع معامله
        if self._deal_type is not None:
            # برای فروش، sellingPrice باید موجود باشد
            # برای اجاره، mortgageAmount یا monthlyRentAmount باید موجود باشد
            if self._deal_type == 1:  # فروش
                selling_price = property_item.get('sellingPrice', 0)
                if not selling_price or selling_price <= 0:
                    return False
            elif self._deal_type == 2:  # اجاره
                mortgage = property_item.get('mortgageAmount', 0)
                rent = property_item.get('monthlyRentAmount', 0)
                if (not mortgage and not rent) or (mortgage <= 0 and rent <= 0):
                    return False
        
        # بررسی نوع ملک
        if self._property_type_filter and property_item.get('property_type') != self._property_type_filter:
            return False
        
        # بررسی منطقه
        if self._district_filter and self._district_filter != "*":
            district = property_item.get('district', '')
            if district.lower() != self._district_filter.lower():
                return False
        
        # بررسی کاربر
        if self._username_filter:
            username = property_item.get('username', '')
            if username.lower() != self._username_filter.lower():
                return False
        
        # بررسی متراژ
        area = property_item.get('area', 0)
        if (self._min_area is not None and area < self._min_area) or \
           (self._max_area is not None and area > self._max_area):
            return False
        
        # بررسی قیمت فروش
        selling_price = property_item.get('sellingPrice', 0)
        if self._deal_type == 1 and ((self._min_price is not None and selling_price < self._min_price) or \
           (self._max_price is not None and selling_price > self._max_price)):
            return False
        
        # بررسی مبلغ رهن و اجاره
        if self._deal_type == 2:
            mortgage = property_item.get('mortgageAmount', 0)
            rent = property_item.get('monthlyRentAmount', 0)
            
            # محاسبه قیمت معادل (مبلغ رهن + 100 برابر اجاره ماهانه)
            equivalent_price = mortgage + (rent * 100)
            
            if ((self._min_price is not None and equivalent_price < self._min_price) or \
               (self._max_price is not None and equivalent_price > self._max_price)):
                return False
        
        # بررسی تعداد اتاق‌خواب (فقط برای املاک مسکونی)
        if property_item.get('property_type') == 'residential':
            bedrooms = property_item.get('bedrooms', 0)
            if (self._min_bedrooms is not None and bedrooms < self._min_bedrooms) or \
               (self._max_bedrooms is not None and bedrooms > self._max_bedrooms):
                return False
        
        # بررسی سن بنا
        age = property_item.get('age', 0)
        if (self._min_age is not None and age < self._min_age) or \
           (self._max_age is not None and age > self._max_age):
            return False
        
        # بررسی تاریخ ثبت
        reg_date_str = property_item.get('registrationDate', '')
        if reg_date_str and (self._min_date is not None or self._max_date is not None):
            try:
                reg_date = datetime.strptime(reg_date_str, "%Y-%m-%d").date()
                
                if self._min_date is not None and reg_date < self._min_date.toPyDate():
                    return False
                
                if self._max_date is not None and reg_date > self._max_date.toPyDate():
                    return False
            except:
                # اگر تاریخ قابل تبدیل نبود، فیلتر را نادیده می‌گیریم
                pass
        
        # اعمال فیلتر عمومی (متن جستجو در همه فیلدها)
        regexp = self.filterRegExp()
        if not regexp.isEmpty():
            # جستجو در تمام فیلدهای متنی
            text_fields = ['id', 'district', 'address', 'username', 'description']
            match_found = False
            
            for field in text_fields:
                value = str(property_item.get(field, ''))
                if regexp.indexIn(value) != -1:
                    match_found = True
                    break
            
            if not match_found:
                return False
        
        return True
    
    def setMinPrice(self, value):
        """
        تنظیم حداقل قیمت
        
        Args:
            value (int): حداقل قیمت
        """
        self._min_price = value
        self.invalidateFilter()
    
    def setMaxPrice(self, value):
        """
        تنظیم حداکثر قیمت
        
        Args:
            value (int): حداکثر قیمت
        """
        self._max_price = value
        self.invalidateFilter()
    
    def setMinArea(self, value):
        """
        تنظیم حداقل متراژ
        
        Args:
            value (int): حداقل متراژ
        """
        self._min_area = value
        self.invalidateFilter()
    
    def setMaxArea(self, value):
        """
        تنظیم حداکثر متراژ
        
        Args:
            value (int): حداکثر متراژ
        """
        self._max_area = value
        self.invalidateFilter()
    
    def setMinBedrooms(self, value):
        """
        تنظیم حداقل تعداد اتاق‌خواب
        
        Args:
            value (int): حداقل تعداد اتاق‌خواب
        """
        self._min_bedrooms = value
        self.invalidateFilter()
    
    def setMaxBedrooms(self, value):
        """
        تنظیم حداکثر تعداد اتاق‌خواب
        
        Args:
            value (int): حداکثر تعداد اتاق‌خواب
        """
        self._max_bedrooms = value
        self.invalidateFilter()
    
    def setMinAge(self, value):
        """
        تنظیم حداقل سن بنا
        
        Args:
            value (int): حداقل سن بنا
        """
        self._min_age = value
        self.invalidateFilter()
    
    def setMaxAge(self, value):
        """
        تنظیم حداکثر سن بنا
        
        Args:
            value (int): حداکثر سن بنا
        """
        self._max_age = value
        self.invalidateFilter()
    
    def setDistrictFilter(self, district):
        """
        تنظیم فیلتر منطقه
        
        Args:
            district (str): منطقه
        """
        self._district_filter = district
        self.invalidateFilter()
    
    def setPropertyTypeFilter(self, property_type):
        """
        تنظیم فیلتر نوع ملک
        
        Args:
            property_type (str): نوع ملک
        """
        self._property_type_filter = property_type
        self.invalidateFilter()
    
    def setUsernameFilter(self, username):
        """
        تنظیم فیلتر کاربر
        
        Args:
            username (str): نام کاربری
        """
        self._username_filter = username
        self.invalidateFilter()
    
    def setMinDate(self, date):
        """
        تنظیم حداقل تاریخ
        
        Args:
            date (QDate): حداقل تاریخ
        """
        self._min_date = date
        self.invalidateFilter()
    
    def setMaxDate(self, date):
        """
        تنظیم حداکثر تاریخ
        
        Args:
            date (QDate): حداکثر تاریخ
        """
        self._max_date = date
        self.invalidateFilter()
    
    def setDealType(self, deal_type):
        """
        تنظیم نوع معامله
        
        Args:
            deal_type (int): نوع معامله (1: فروش، 2: اجاره)
        """
        self._deal_type = deal_type
        self.invalidateFilter()
    
    def resetFilters(self):
        """
        بازنشانی تمام فیلترها
        """
        self._min_price = None
        self._max_price = None
        self._min_area = None
        self._max_area = None
        self._min_bedrooms = None
        self._max_bedrooms = None
        self._min_age = None
        self._max_age = None
        self._district_filter = None
        self._property_type_filter = None
        self._username_filter = None
        self._min_date = None
        self._max_date = None
        self._deal_type = None
        
        self.setFilterRegExp("")
        self.invalidateFilter()


class ComboBoxProxyModel(QSortFilterProxyModel):
    """
    مدل پروکسی برای نمایش در کومبوباکس
    """
    
    def __init__(self, parent=None):
        """
        مقداردهی اولیه
        
        Args:
            parent (QObject, optional): والد QT
        """
        super(ComboBoxProxyModel, self).__init__(parent)
        self._value_column = 0
        self._display_column = 0
    
    def setValueColumn(self, column):
        """
        تنظیم ستون مقدار
        
        Args:
            column (int): شماره ستون مقدار
        """
        self._value_column = column
    
    def setDisplayColumn(self, column):
        """
        تنظیم ستون نمایش
        
        Args:
            column (int): شماره ستون نمایش
        """
        self._display_column = column
    
    def data(self, index, role=Qt.DisplayRole):
        """
        دریافت داده برای نمایش
        
        Args:
            index (QModelIndex): اندیس آیتم
            role (int, optional): نقش داده
            
        Returns:
            QVariant: داده مورد نظر
        """
        if not index.isValid():
            return QVariant()
        
        if role == Qt.DisplayRole:
            # برای نمایش، از ستون نمایش استفاده می‌کنیم
            display_index = self.index(index.row(), self._display_column)
            return super(ComboBoxProxyModel, self).data(display_index, role)
        
        elif role == Qt.UserRole:
            # برای مقدار داخلی، از ستون مقدار استفاده می‌کنیم
            value_index = self.index(index.row(), self._value_column)
            return super(ComboBoxProxyModel, self).data(value_index, Qt.DisplayRole)
        
        return super(ComboBoxProxyModel, self).data(index, role) 