#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ماژول تب جستجو برای سیستم مدیریت املاک
این ماژول شامل کلاس SearchTab برای جستجوی انواع املاک بر اساس معیارهای مختلف است.
"""

import os
import sys
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QComboBox, QGroupBox,
    QRadioButton, QCheckBox, QSpinBox, QDateEdit,
    QTabWidget, QLineEdit, QFormLayout, QTableWidget,
    QTableWidgetItem, QHeaderView, QFileDialog, QMessageBox,
    QAbstractItemView, QSplitter, QScrollArea, QMenu,
    QAction, QToolButton, QStackedWidget, QSpacerItem, QSizePolicy,
    QButtonGroup, QDialog
)
from PyQt5.QtGui import QIcon, QFont, QColor, QBrush
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QSize

from property_management.residential_bridge import ResidentialBridge
from property_management.commercial_bridge import CommercialBridge
from property_management.land_bridge import LandBridge
from property_management.export import export_data


class ResultTable(QTableWidget):
    """جدول نمایش نتایج جستجو"""
    
    property_selected = pyqtSignal(dict, str)  # سیگنال انتخاب ملک (داده‌های ملک، نوع ملک)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setAlternatingRowColors(True)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.horizontalHeader().setStretchLastSection(True)
        self.setSortingEnabled(True)
        
        self.property_data = []  # ذخیره داده‌های کامل املاک
        self.property_type = ""  # نوع ملک جاری
        
        self.itemDoubleClicked.connect(self.on_item_double_clicked)
        
        # ایجاد منوی راست کلیک
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
    
    def set_residential_results(self, properties):
        """تنظیم نتایج جستجوی املاک مسکونی"""
        self.property_data = properties
        self.property_type = "residential"
        
        self.setRowCount(0)
        self.setColumnCount(7)
        self.setHorizontalHeaderLabels([
            "شناسه", "منطقه", "متراژ", "تعداد اتاق", "سن بنا", "نوع معامله", "قیمت/اجاره"
        ])
        
        for prop in properties:
            row = self.rowCount()
            self.insertRow(row)
            
            self.setItem(row, 0, QTableWidgetItem(prop.get('id', '')))
            self.setItem(row, 1, QTableWidgetItem(prop.get('district', '')))
            self.setItem(row, 2, QTableWidgetItem(str(prop.get('area', 0))))
            self.setItem(row, 3, QTableWidgetItem(str(prop.get('bedrooms', 0))))
            self.setItem(row, 4, QTableWidgetItem(str(prop.get('age', 0))))
            
            deal_type = "فروش" if prop.get('deal_type') == 'sale' else "اجاره"
            self.setItem(row, 5, QTableWidgetItem(deal_type))
            
            price_text = f"{prop.get('price', 0):,}" if deal_type == "فروش" else f"{prop.get('rent', 0):,}"
            self.setItem(row, 6, QTableWidgetItem(price_text))
            
        self.resizeColumnsToContents()
    
    def set_commercial_results(self, properties):
        """تنظیم نتایج جستجوی املاک تجاری"""
        self.property_data = properties
        self.property_type = "commercial"
        
        self.setRowCount(0)
        self.setColumnCount(7)
        self.setHorizontalHeaderLabels([
            "شناسه", "منطقه", "متراژ", "کاربری", "دارای انباری", "نوع معامله", "قیمت/اجاره"
        ])
        
        for prop in properties:
            row = self.rowCount()
            self.insertRow(row)
            
            self.setItem(row, 0, QTableWidgetItem(prop.get('id', '')))
            self.setItem(row, 1, QTableWidgetItem(prop.get('district', '')))
            self.setItem(row, 2, QTableWidgetItem(str(prop.get('area', 0))))
            self.setItem(row, 3, QTableWidgetItem(prop.get('usage_type', '')))
            
            has_storage = "بله" if prop.get('has_storage') else "خیر"
            self.setItem(row, 4, QTableWidgetItem(has_storage))
            
            deal_type = "فروش" if prop.get('deal_type') == 'sale' else "اجاره"
            self.setItem(row, 5, QTableWidgetItem(deal_type))
            
            price_text = f"{prop.get('price', 0):,}" if deal_type == "فروش" else f"{prop.get('rent', 0):,}"
            self.setItem(row, 6, QTableWidgetItem(price_text))
            
        self.resizeColumnsToContents()
    
    def set_land_results(self, properties):
        """تنظیم نتایج جستجوی زمین"""
        self.property_data = properties
        self.property_type = "land"
        
        self.setRowCount(0)
        self.setColumnCount(6)
        self.setHorizontalHeaderLabels([
            "شناسه", "منطقه", "متراژ", "کاربری", "نوع معامله", "قیمت/اجاره"
        ])
        
        for prop in properties:
            row = self.rowCount()
            self.insertRow(row)
            
            self.setItem(row, 0, QTableWidgetItem(prop.get('id', '')))
            self.setItem(row, 1, QTableWidgetItem(prop.get('district', '')))
            self.setItem(row, 2, QTableWidgetItem(str(prop.get('area', 0))))
            self.setItem(row, 3, QTableWidgetItem(prop.get('usage_type', '')))
            
            deal_type = "فروش" if prop.get('deal_type') == 'sale' else "اجاره"
            self.setItem(row, 4, QTableWidgetItem(deal_type))
            
            price_text = f"{prop.get('price', 0):,}" if deal_type == "فروش" else f"{prop.get('rent', 0):,}"
            self.setItem(row, 5, QTableWidgetItem(price_text))
            
        self.resizeColumnsToContents()
    
    def clear_results(self):
        """پاک کردن نتایج جستجو"""
        self.setRowCount(0)
        self.property_data = []
        self.property_type = ""
    
    def on_item_double_clicked(self, item):
        """رویداد دابل کلیک روی آیتم"""
        row = item.row()
        if 0 <= row < len(self.property_data):
            self.property_selected.emit(self.property_data[row], self.property_type)
    
    def export_results(self, file_path, export_format="excel"):
        """صدور نتایج جستجو به فرمت‌های مختلف"""
        if not self.property_data:
            QMessageBox.warning(self, "خطا", "نتیجه‌ای برای صدور وجود ندارد.")
            return False
        
        try:
            # تبدیل داده به فرمت مناسب برای صدور
            export_title = f"نتایج جستجوی {self.get_property_type_fa()}"
            
            # ایجاد دیکشنری برای متادیتا
            metadata = {
                "title": export_title,
                "author": "سیستم مدیریت املاک",
                "subject": "گزارش نتایج جستجو",
                "created_at": "now"
            }
            
            # صدور داده
            export_data(
                self.property_data, 
                file_path, 
                export_format=export_format,
                metadata=metadata
            )
            
            return True
        except Exception as e:
            logging.error(f"خطا در صدور نتایج: {str(e)}")
            QMessageBox.critical(self, "خطا", f"خطا در صدور نتایج: {str(e)}")
            return False
    
    def get_property_type_fa(self):
        """دریافت نام فارسی نوع ملک"""
        if self.property_type == "residential":
            return "املاک مسکونی"
        elif self.property_type == "commercial":
            return "املاک تجاری"
        elif self.property_type == "land":
            return "زمین"
        return "املاک"
    
    def show_context_menu(self, position):
        """نمایش منوی راست کلیک"""
        if self.rowCount() == 0:
            return
            
        menu = QMenu(self)
        view_action = menu.addAction("مشاهده جزئیات")
        export_action = menu.addAction("خروجی نتایج")
        
        action = menu.exec_(self.mapToGlobal(position))
        
        if action == view_action:
            row = self.currentRow()
            if row >= 0 and row < len(self.property_data):
                self.property_selected.emit(self.property_data[row], self.property_type)
        elif action == export_action:
            # ارسال سیگنال به والد برای خروجی گرفتن
            self.parent().export_results()


class SearchTab(QWidget):
    """کلاس تب جستجو برای سیستم مدیریت املاک"""
    
    property_selected = pyqtSignal(dict, str)  # سیگنال انتخاب ملک (داده‌های ملک، نوع ملک)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        
        # ایجاد پل‌های ارتباطی
        self.residential_bridge = ResidentialBridge()
        self.commercial_bridge = CommercialBridge()
        self.land_bridge = LandBridge()
        
        # تنظیم رابط کاربری
        self.setup_ui()
        
        self.logger.info("تب جستجو ایجاد شد")
    
    def setup_ui(self):
        """راه‌اندازی رابط کاربری"""
        main_layout = QVBoxLayout(self)
        
        # عنوان
        title_layout = QHBoxLayout()
        
        title_label = QLabel("جستجوی پیشرفته املاک")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_layout.addWidget(title_label)
        
        title_layout.addStretch()
        
        # دکمه‌های عملیات
        search_button = QPushButton("جستجو")
        search_button.setIcon(QIcon("icons/search.png"))
        search_button.clicked.connect(self.search_properties)
        title_layout.addWidget(search_button)
        
        clear_button = QPushButton("پاک کردن")
        clear_button.setIcon(QIcon("icons/clear.png"))
        clear_button.clicked.connect(self.clear_search)
        title_layout.addWidget(clear_button)
        
        export_button = QPushButton("خروجی")
        export_button.setIcon(QIcon("icons/export.png"))
        export_button.clicked.connect(self.export_results)
        title_layout.addWidget(export_button)
        
        main_layout.addLayout(title_layout)
        
        # اسپلیتر اصلی (جداکننده فیلترها و نتایج)
        splitter = QSplitter(Qt.Vertical)
        
        # ویجت فیلترهای جستجو
        search_filters_widget = QWidget()
        filters_layout = QVBoxLayout(search_filters_widget)
        self.setup_search_filters(filters_layout)
        splitter.addWidget(search_filters_widget)
        
        # ویجت نتایج جستجو
        results_widget = QWidget()
        results_layout = QVBoxLayout(results_widget)
        
        results_label = QLabel("نتایج جستجو")
        results_font = QFont()
        results_font.setPointSize(12)
        results_font.setBold(True)
        results_label.setFont(results_font)
        results_layout.addWidget(results_label)
        
        self.results_table = ResultTable()
        self.results_table.property_selected.connect(self.on_property_selected)
        results_layout.addWidget(self.results_table)
        
        splitter.addWidget(results_widget)
        
        # تنظیم نسبت اندازه
        splitter.setSizes([200, 400])
        
        main_layout.addWidget(splitter)
    
    def setup_search_filters(self, layout):
        """راه‌اندازی فیلترهای جستجو"""
        # گروه‌بندی انتخاب نوع ملک و نوع معامله
        type_group = QGroupBox("نوع ملک و معامله")
        type_layout = QGridLayout(type_group)
        
        # نوع ملک
        property_type_label = QLabel("نوع ملک:")
        type_layout.addWidget(property_type_label, 0, 0)
        
        self.property_type_combo = QComboBox()
        self.property_type_combo.addItems(["مسکونی", "تجاری", "زمین"])
        self.property_type_combo.currentIndexChanged.connect(self.on_property_type_changed)
        type_layout.addWidget(self.property_type_combo, 0, 1)
        
        # نوع معامله
        deal_type_label = QLabel("نوع معامله:")
        type_layout.addWidget(deal_type_label, 0, 2)
        
        self.deal_type_group = QButtonGroup(self)
        
        self.sale_radio = QRadioButton("فروش")
        self.sale_radio.setChecked(True)
        self.deal_type_group.addButton(self.sale_radio)
        type_layout.addWidget(self.sale_radio, 0, 3)
        
        self.rent_radio = QRadioButton("اجاره")
        self.deal_type_group.addButton(self.rent_radio)
        type_layout.addWidget(self.rent_radio, 0, 4)
        
        layout.addWidget(type_group)
        
        # گروه‌بندی فیلترهای عمومی
        common_group = QGroupBox("فیلترهای عمومی")
        common_layout = QGridLayout(common_group)
        
        # منطقه
        district_label = QLabel("منطقه:")
        common_layout.addWidget(district_label, 0, 0)
        
        self.district_combo = QComboBox()
        self.district_combo.addItem("همه مناطق", "")
        # افزودن مناطق
        for i in range(1, 23):
            self.district_combo.addItem(f"منطقه {i}", str(i))
        common_layout.addWidget(self.district_combo, 0, 1)
        
        # محدوده متراژ
        area_label = QLabel("متراژ (از):")
        common_layout.addWidget(area_label, 0, 2)
        
        self.min_area_spin = QSpinBox()
        self.min_area_spin.setRange(0, 10000)
        self.min_area_spin.setSingleStep(10)
        common_layout.addWidget(self.min_area_spin, 0, 3)
        
        area_to_label = QLabel("تا:")
        common_layout.addWidget(area_to_label, 0, 4)
        
        self.max_area_spin = QSpinBox()
        self.max_area_spin.setRange(0, 10000)
        self.max_area_spin.setSingleStep(10)
        self.max_area_spin.setValue(1000)
        common_layout.addWidget(self.max_area_spin, 0, 5)
        
        # محدوده قیمت
        price_label = QLabel("قیمت (از):")
        common_layout.addWidget(price_label, 1, 0)
        
        self.min_price_spin = QSpinBox()
        self.min_price_spin.setRange(0, 1000000)
        self.min_price_spin.setSingleStep(100)
        self.min_price_spin.setSuffix(" میلیون")
        common_layout.addWidget(self.min_price_spin, 1, 1)
        
        price_to_label = QLabel("تا:")
        common_layout.addWidget(price_to_label, 1, 2)
        
        self.max_price_spin = QSpinBox()
        self.max_price_spin.setRange(0, 1000000)
        self.max_price_spin.setSingleStep(100)
        self.max_price_spin.setValue(10000)
        self.max_price_spin.setSuffix(" میلیون")
        common_layout.addWidget(self.max_price_spin, 1, 3)
        
        # آدرس
        address_label = QLabel("آدرس:")
        common_layout.addWidget(address_label, 2, 0)
        
        self.address_edit = QLineEdit()
        self.address_edit.setPlaceholderText("بخشی از آدرس را وارد کنید")
        common_layout.addWidget(self.address_edit, 2, 1, 1, 5)
        
        layout.addWidget(common_group)
        
        # ویجت استک برای فیلترهای اختصاصی هر نوع ملک
        self.property_filters_stack = QStackedWidget()
        
        # ایجاد فیلترهای اختصاصی برای هر نوع ملک
        self.setup_residential_filters()
        self.setup_commercial_filters()
        self.setup_land_filters()
        
        layout.addWidget(self.property_filters_stack)
        
        # تنظیم حالت اولیه فیلترها بر اساس نوع ملک انتخاب شده
        self.on_property_type_changed(0)
    
    def setup_residential_filters(self):
        """راه‌اندازی فیلترهای مختص املاک مسکونی"""
        widget = QWidget()
        layout = QGridLayout(widget)
        
        # گروه فیلترهای مسکونی
        group = QGroupBox("فیلترهای ویژه املاک مسکونی")
        residential_layout = QGridLayout(group)
        
        # تعداد اتاق
        bedrooms_label = QLabel("تعداد اتاق:")
        residential_layout.addWidget(bedrooms_label, 0, 0)
        
        self.bedrooms_combo = QComboBox()
        self.bedrooms_combo.addItem("همه", 0)
        for i in range(1, 7):
            self.bedrooms_combo.addItem(str(i), i)
        self.bedrooms_combo.addItem("7+", 7)
        residential_layout.addWidget(self.bedrooms_combo, 0, 1)
        
        # حداکثر سن بنا
        age_label = QLabel("حداکثر سن بنا:")
        residential_layout.addWidget(age_label, 0, 2)
        
        self.max_age_spin = QSpinBox()
        self.max_age_spin.setRange(0, 100)
        self.max_age_spin.setValue(30)
        self.max_age_spin.setSuffix(" سال")
        residential_layout.addWidget(self.max_age_spin, 0, 3)
        
        # طبقه
        floor_label = QLabel("طبقه:")
        residential_layout.addWidget(floor_label, 1, 0)
        
        self.floor_combo = QComboBox()
        self.floor_combo.addItem("همه", -1)
        self.floor_combo.addItem("همکف", 0)
        for i in range(1, 11):
            self.floor_combo.addItem(str(i), i)
        self.floor_combo.addItem("11+", 11)
        residential_layout.addWidget(self.floor_combo, 1, 1)
        
        # امکانات
        has_elevator_check = QCheckBox("آسانسور")
        residential_layout.addWidget(has_elevator_check, 1, 2)
        self.has_elevator_check = has_elevator_check
        
        has_parking_check = QCheckBox("پارکینگ")
        residential_layout.addWidget(has_parking_check, 1, 3)
        self.has_parking_check = has_parking_check
        
        has_storage_check = QCheckBox("انباری")
        residential_layout.addWidget(has_storage_check, 2, 0)
        self.has_storage_check = has_storage_check
        
        has_balcony_check = QCheckBox("بالکن")
        residential_layout.addWidget(has_balcony_check, 2, 1)
        self.has_balcony_check = has_balcony_check
        
        layout.addWidget(group)
        self.property_filters_stack.addWidget(widget)
    
    def setup_commercial_filters(self):
        """راه‌اندازی فیلترهای مختص املاک تجاری"""
        widget = QWidget()
        layout = QGridLayout(widget)
        
        # گروه فیلترهای تجاری
        group = QGroupBox("فیلترهای ویژه املاک تجاری")
        commercial_layout = QGridLayout(group)
        
        # نوع ملک تجاری
        type_label = QLabel("نوع ملک تجاری:")
        commercial_layout.addWidget(type_label, 0, 0)
        
        self.commercial_type_combo = QComboBox()
        self.commercial_type_combo.addItem("همه", "")
        self.commercial_type_combo.addItem("مغازه", "shop")
        self.commercial_type_combo.addItem("دفتر کار", "office")
        self.commercial_type_combo.addItem("صنعتی", "industrial")
        commercial_layout.addWidget(self.commercial_type_combo, 0, 1)
        
        # ویژگی‌ها
        has_showcase_check = QCheckBox("ویترین")
        commercial_layout.addWidget(has_showcase_check, 0, 2)
        self.has_showcase_check = has_showcase_check
        
        has_toilet_check = QCheckBox("سرویس بهداشتی")
        commercial_layout.addWidget(has_toilet_check, 0, 3)
        self.has_toilet_check = has_toilet_check
        
        layout.addWidget(group)
        self.property_filters_stack.addWidget(widget)
    
    def setup_land_filters(self):
        """راه‌اندازی فیلترهای مختص زمین"""
        widget = QWidget()
        layout = QGridLayout(widget)
        
        # گروه فیلترهای زمین
        group = QGroupBox("فیلترهای ویژه زمین")
        land_layout = QGridLayout(group)
        
        # کاربری زمین
        land_type_label = QLabel("کاربری زمین:")
        land_layout.addWidget(land_type_label, 0, 0)
        
        self.land_type_combo = QComboBox()
        self.land_type_combo.addItem("همه", "")
        self.land_type_combo.addItem("مسکونی", "residential")
        self.land_type_combo.addItem("تجاری", "commercial")
        self.land_type_combo.addItem("صنعتی", "industrial")
        self.land_type_combo.addItem("کشاورزی", "agricultural")
        self.land_type_combo.addItem("باغ", "garden")
        land_layout.addWidget(self.land_type_combo, 0, 1)
        
        # وضعیت دسترسی
        has_road_access_check = QCheckBox("دسترسی به جاده اصلی")
        land_layout.addWidget(has_road_access_check, 0, 2)
        self.has_road_access_check = has_road_access_check
        
        layout.addWidget(group)
        self.property_filters_stack.addWidget(widget)
    
    def remove_property_specific_filters(self):
        """حذف تمام ویجت‌های فیلترهای اختصاصی"""
        while self.property_filters_stack.count() > 0:
            widget = self.property_filters_stack.widget(0)
            self.property_filters_stack.removeWidget(widget)
            widget.deleteLater()
    
    def on_property_type_changed(self, index):
        """تغییر فیلترهای اختصاصی بر اساس نوع ملک انتخاب شده"""
        # تنظیم ویجت استک به ایندکس مناسب
        if self.property_filters_stack.count() > index:
            self.property_filters_stack.setCurrentIndex(index)
        
        # پاک کردن نتایج جستجوی قبلی
        self.results_table.clear_results()
    
    def get_deal_type(self):
        """دریافت نوع معامله انتخاب شده"""
        return "sale" if self.sale_radio.isChecked() else "rent"
    
    def search_properties(self):
        """جستجوی املاک بر اساس فیلترهای انتخاب شده"""
        self.logger.info("در حال انجام جستجو...")
        
        # دریافت مقادیر فیلترهای عمومی
        property_type_index = self.property_type_combo.currentIndex()
        deal_type = self.get_deal_type()
        
        district = self.district_combo.currentData()
        min_area = self.min_area_spin.value()
        max_area = self.max_area_spin.value()
        min_price = self.min_price_spin.value()
        max_price = self.max_price_spin.value()
        address = self.address_edit.text().strip()
        
        # بررسی معتبر بودن فیلترها
        if min_area > max_area and max_area > 0:
            QMessageBox.warning(
                self, 
                "خطای فیلتر", 
                "حداقل متراژ نمی‌تواند بیشتر از حداکثر متراژ باشد."
            )
            return
        
        if min_price > max_price and max_price > 0:
            QMessageBox.warning(
                self, 
                "خطای فیلتر", 
                "حداقل قیمت نمی‌تواند بیشتر از حداکثر قیمت باشد."
            )
            return
        
        # اعمال جستجو بر اساس نوع ملک
        if property_type_index == 0:  # مسکونی
            self.search_residential_properties(
                deal_type, district, min_area, max_area, min_price, max_price, address
            )
        elif property_type_index == 1:  # تجاری
            self.search_commercial_properties(
                deal_type, district, min_area, max_area, min_price, max_price, address
            )
        elif property_type_index == 2:  # زمین
            self.search_land_properties(
                deal_type, district, min_area, max_area, min_price, max_price, address
            )
    
    def search_residential_properties(self, deal_type, district, min_area, max_area, min_price, max_price, address):
        """جستجوی املاک مسکونی"""
        try:
            # دریافت مقادیر فیلترهای اختصاصی
            bedrooms = self.bedrooms_combo.currentData()
            max_building_age = self.max_age_spin.value()
            floor = self.floor_combo.currentData()
            has_elevator = self.has_elevator_check.isChecked()
            has_parking = self.has_parking_check.isChecked()
            has_storage = self.has_storage_check.isChecked()
            has_balcony = self.has_balcony_check.isChecked()
            
            # اعمال جستجو بر اساس نوع معامله
            if district:
                # جستجو بر اساس منطقه
                properties = self.residential_bridge.find_by_district(
                    district, deal_type
                )
            elif min_area > 0 or max_area > 0:
                # جستجو بر اساس متراژ
                properties = self.residential_bridge.find_by_area(
                    min_area, max_area, deal_type
                )
            elif bedrooms > 0:
                # جستجو بر اساس تعداد اتاق
                properties = self.residential_bridge.find_by_bedrooms(
                    bedrooms, deal_type
                )
            elif max_building_age > 0:
                # جستجو بر اساس سن بنا
                properties = self.residential_bridge.find_by_age(
                    0, max_building_age, deal_type
                )
            elif min_price > 0 or max_price > 0:
                # جستجو بر اساس قیمت
                properties = self.residential_bridge.find_by_price(
                    min_price, max_price, deal_type
                )
            else:
                # دریافت همه املاک مسکونی
                properties = self.residential_bridge.get_all_properties(deal_type)
            
            # فیلتر نتایج
            filtered_properties = []
            for prop in properties:
                # اعمال فیلتر متراژ
                if (min_area > 0 and prop.get("area", 0) < min_area) or \
                   (max_area > 0 and prop.get("area", 0) > max_area):
                    continue
                
                # اعمال فیلتر قیمت
                if (min_price > 0 and prop.get("price", 0) < min_price) or \
                   (max_price > 0 and prop.get("price", 0) > max_price):
                    continue
                
                # اعمال فیلتر تعداد اتاق
                if bedrooms > 0 and prop.get("bedrooms", 0) != bedrooms:
                    continue
                
                # اعمال فیلتر سن بنا
                if max_building_age > 0 and prop.get("building_age", 0) > max_building_age:
                    continue
                
                # اعمال فیلتر طبقه
                if floor >= 0 and prop.get("floor", -1) != floor:
                    continue
                
                # اعمال فیلتر منطقه
                if district and prop.get("district", "") != district:
                    continue
                
                # اعمال فیلتر آدرس
                if address and address.lower() not in prop.get("address", "").lower():
                    continue
                
                # اعمال فیلتر امکانات
                if has_elevator and not prop.get("has_elevator", False):
                    continue
                if has_parking and not prop.get("has_parking", False):
                    continue
                if has_storage and not prop.get("has_storage", False):
                    continue
                if has_balcony and not prop.get("has_balcony", False):
                    continue
                
                filtered_properties.append(prop)
            
            # نمایش نتایج
            self.results_table.set_residential_results(filtered_properties)
            
        except Exception as e:
            self.logger.error(f"خطا در جستجوی املاک مسکونی: {str(e)}")
            QMessageBox.critical(self, "خطا", f"خطا در جستجوی املاک مسکونی: {str(e)}")
            self.results_table.clear_results()
    
    def search_commercial_properties(self, deal_type, district, min_area, max_area, min_price, max_price, address):
        """جستجوی املاک تجاری"""
        try:
            # دریافت مقادیر فیلترهای اختصاصی
            commercial_type = self.commercial_type_combo.currentData()
            has_showcase = self.has_showcase_check.isChecked()
            has_toilet = self.has_toilet_check.isChecked()
            
            # اعمال جستجو بر اساس نوع معامله
            if district:
                # جستجو بر اساس منطقه
                properties = self.commercial_bridge.find_by_district(
                    district, deal_type
                )
            elif min_area > 0 or max_area > 0:
                # جستجو بر اساس متراژ
                properties = self.commercial_bridge.find_by_area(
                    min_area, max_area, deal_type
                )
            elif commercial_type:
                # جستجو بر اساس نوع تجاری
                properties = self.commercial_bridge.find_by_type(
                    commercial_type, deal_type
                )
            elif min_price > 0 or max_price > 0:
                # جستجو بر اساس قیمت
                properties = self.commercial_bridge.find_by_price(
                    min_price, max_price, deal_type
                )
            else:
                # دریافت همه املاک تجاری
                properties = self.commercial_bridge.get_all_properties(deal_type)
            
            # فیلتر نتایج
            filtered_properties = []
            for prop in properties:
                # اعمال فیلتر متراژ
                if (min_area > 0 and prop.get("area", 0) < min_area) or \
                   (max_area > 0 and prop.get("area", 0) > max_area):
                    continue
                
                # اعمال فیلتر قیمت
                if (min_price > 0 and prop.get("price", 0) < min_price) or \
                   (max_price > 0 and prop.get("price", 0) > max_price):
                    continue
                
                # اعمال فیلتر نوع تجاری
                if commercial_type and prop.get("commercial_type", "") != commercial_type:
                    continue
                
                # اعمال فیلتر منطقه
                if district and prop.get("district", "") != district:
                    continue
                
                # اعمال فیلتر آدرس
                if address and address.lower() not in prop.get("address", "").lower():
                    continue
                
                # اعمال فیلتر ویژگی‌ها
                if has_showcase and not prop.get("has_showcase", False):
                    continue
                if has_toilet and not prop.get("has_toilet", False):
                    continue
                
                filtered_properties.append(prop)
            
            # نمایش نتایج
            self.results_table.set_commercial_results(filtered_properties)
            
        except Exception as e:
            self.logger.error(f"خطا در جستجوی املاک تجاری: {str(e)}")
            QMessageBox.critical(self, "خطا", f"خطا در جستجوی املاک تجاری: {str(e)}")
            self.results_table.clear_results()
    
    def search_land_properties(self, deal_type, district, min_area, max_area, min_price, max_price, address):
        """جستجوی زمین‌ها"""
        try:
            # دریافت مقادیر فیلترهای اختصاصی
            land_type = self.land_type_combo.currentData()
            has_road_access = self.has_road_access_check.isChecked()
            
            # اعمال جستجو بر اساس نوع معامله
            if district:
                # جستجو بر اساس منطقه
                properties = self.land_bridge.find_by_district(
                    district, deal_type
                )
            elif min_area > 0 or max_area > 0:
                # جستجو بر اساس متراژ
                properties = self.land_bridge.find_by_area(
                    min_area, max_area, deal_type
                )
            elif min_price > 0 or max_price > 0:
                # جستجو بر اساس قیمت
                properties = self.land_bridge.find_by_price(
                    min_price, max_price, deal_type
                )
            else:
                # دریافت همه زمین‌ها
                properties = self.land_bridge.get_all_properties(deal_type)
            
            # فیلتر نتایج
            filtered_properties = []
            for prop in properties:
                # اعمال فیلتر متراژ
                if (min_area > 0 and prop.get("area", 0) < min_area) or \
                   (max_area > 0 and prop.get("area", 0) > max_area):
                    continue
                
                # اعمال فیلتر قیمت
                if (min_price > 0 and prop.get("price", 0) < min_price) or \
                   (max_price > 0 and prop.get("price", 0) > max_price):
                    continue
                
                # اعمال فیلتر نوع زمین
                if land_type and prop.get("land_type", "") != land_type:
                    continue
                
                # اعمال فیلتر منطقه
                if district and prop.get("district", "") != district:
                    continue
                
                # اعمال فیلتر آدرس
                if address and address.lower() not in prop.get("address", "").lower():
                    continue
                
                # اعمال فیلتر دسترسی
                if has_road_access and not prop.get("has_road_access", False):
                    continue
                
                filtered_properties.append(prop)
            
            # نمایش نتایج
            self.results_table.set_land_results(filtered_properties)
            
        except Exception as e:
            self.logger.error(f"خطا در جستجوی زمین‌ها: {str(e)}")
            QMessageBox.critical(self, "خطا", f"خطا در جستجوی زمین‌ها: {str(e)}")
            self.results_table.clear_results()
    
    def clear_search(self):
        """پاک کردن فیلترها و نتایج جستجو"""
        # پاک کردن فیلترهای عمومی
        self.district_combo.setCurrentIndex(0)
        self.min_area_spin.setValue(0)
        self.max_area_spin.setValue(1000)
        self.min_price_spin.setValue(0)
        self.max_price_spin.setValue(10000)
        self.address_edit.clear()
        
        # پاک کردن فیلترهای اختصاصی بر اساس نوع ملک
        property_type_index = self.property_type_combo.currentIndex()
        
        if property_type_index == 0:  # مسکونی
            self.bedrooms_combo.setCurrentIndex(0)
            self.max_age_spin.setValue(30)
            self.floor_combo.setCurrentIndex(0)
            self.has_elevator_check.setChecked(False)
            self.has_parking_check.setChecked(False)
            self.has_storage_check.setChecked(False)
            self.has_balcony_check.setChecked(False)
            
        elif property_type_index == 1:  # تجاری
            self.commercial_type_combo.setCurrentIndex(0)
            self.has_showcase_check.setChecked(False)
            self.has_toilet_check.setChecked(False)
            
        elif property_type_index == 2:  # زمین
            self.land_type_combo.setCurrentIndex(0)
            self.has_road_access_check.setChecked(False)
        
        # پاک کردن نتایج جستجو
        self.results_table.clear_results()
    
    def export_results(self):
        """صدور نتایج جستجو به فایل"""
        # بررسی وجود نتایج
        if self.results_table.property_data is None or len(self.results_table.property_data) == 0:
            QMessageBox.warning(self, "هشدار", "نتیجه‌ای برای صدور وجود ندارد.")
            return
            
        # تعیین نوع فایل
        file_formats = {
            "Excel": ("Excel Files (*.xlsx)", "excel"),
            "CSV": ("CSV Files (*.csv)", "csv"),
            "PDF": ("PDF Files (*.pdf)", "pdf"),
            "متنی": ("Text Files (*.txt)", "text")
        }
        
        # تعیین نام پیش‌فرض فایل بر اساس نوع ملک
        property_type = self.results_table.get_property_type_fa()
        default_name = f"نتایج_جستجوی_{property_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # انتخاب فرمت و مسیر فایل
        format_dialog = QDialog(self)
        format_dialog.setWindowTitle("انتخاب قالب خروجی")
        format_dialog.setMinimumWidth(300)
        
        layout = QVBoxLayout(format_dialog)
        
        format_combo = QComboBox()
        format_combo.addItems(file_formats.keys())
        layout.addWidget(QLabel("قالب فایل خروجی:"))
        layout.addWidget(format_combo)
        
        button_layout = QHBoxLayout()
        ok_button = QPushButton("تأیید")
        ok_button.clicked.connect(format_dialog.accept)
        button_layout.addWidget(ok_button)
        
        cancel_button = QPushButton("انصراف")
        cancel_button.clicked.connect(format_dialog.reject)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        
        if format_dialog.exec_() != QDialog.Accepted:
            return
            
        selected_format = format_combo.currentText()
        file_filter, export_format = file_formats[selected_format]
        
        # انتخاب مسیر ذخیره فایل
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "ذخیره نتایج جستجو",
            os.path.expanduser(f"~/Documents/{default_name}"),
            file_filter
        )
        
        if not file_path:
            return
            
        # صدور فایل
        try:
            success = self.results_table.export_results(file_path, export_format)
            
            if success:
                QMessageBox.information(
                    self, 
                    "صدور نتایج", 
                    f"نتایج جستجو با موفقیت در {file_path} ذخیره شد."
                )
            else:
                QMessageBox.critical(
                    self, 
                    "خطا", 
                    "خطا در صدور نتایج جستجو."
                )
                
        except Exception as e:
            self.logger.error(f"خطا در صدور نتایج جستجو: {str(e)}")
            QMessageBox.critical(self, "خطا", f"خطا در صدور نتایج جستجو: {str(e)}")
    
    def on_property_selected(self, property_data, property_type):
        """رویداد انتخاب یک ملک از نتایج جستجو"""
        # ارسال سیگنال به کلاس والد
        self.property_selected.emit(property_data, property_type) 