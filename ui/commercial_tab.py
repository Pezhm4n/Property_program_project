#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ماژول تب تجاری
این ماژول پیاده‌سازی تب مدیریت املاک تجاری را ارائه می‌دهد.
"""

import os
import logging
from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, 
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, 
    QTabWidget, QFormLayout, QSpinBox, QDoubleSpinBox, 
    QGridLayout, QGroupBox, QMessageBox, QHeaderView, 
    QDateEdit, QTextEdit, QCheckBox, QFileDialog
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QIcon, QPixmap, QFont

from bridge.commercial_bridge import CommercialBridge, CommercialPropertyStruct


class CommercialTab(QWidget):
    """ویجت تب مدیریت املاک تجاری"""
    
    # تعریف انواع املاک تجاری
    PROPERTY_TYPES = [
        "مغازه",
        "دفتر کار",
        "انبار",
        "سوله",
        "فروشگاه",
        "مجتمع تجاری",
        "سایر"
    ]
    
    def __init__(self, current_user, parent=None):
        """سازنده تب تجاری
        
        Args:
            current_user (User): کاربر فعلی
            parent (QWidget, optional): ویجت والد. پیش‌فرض None.
        """
        super().__init__(parent)
        
        self.logger = logging.getLogger(__name__)
        self.current_user = current_user
        
        # ایجاد پل ارتباطی با بخش C
        self.commercial_bridge = CommercialBridge()
        
        # لیست املاک
        self.properties_sale = []
        self.properties_rent = []
        
        # راه‌اندازی رابط کاربری
        self.init_ui()
        
        # بارگیری داده‌های اولیه
        self.load_properties()
        
        self.logger.info("تب مدیریت املاک تجاری راه‌اندازی شد")
    
    def init_ui(self):
        """راه‌اندازی رابط کاربری"""
        # ایجاد طرح‌بندی اصلی
        main_layout = QVBoxLayout(self)
        
        # ایجاد ویجت زبانه‌بندی
        tab_widget = QTabWidget()
        
        # اضافه کردن زبانه ثبت ملک جدید
        registration_widget = self._create_registration_widget()
        tab_widget.addTab(registration_widget, "ثبت ملک جدید")
        
        # اضافه کردن زبانه لیست املاک فروشی
        sale_list_widget = self._create_property_list_widget("sale")
        tab_widget.addTab(sale_list_widget, "لیست املاک فروشی")
        
        # اضافه کردن زبانه لیست املاک اجاره‌ای
        rent_list_widget = self._create_property_list_widget("rent")
        tab_widget.addTab(rent_list_widget, "لیست املاک اجاره‌ای")
        
        # اضافه کردن زبانه‌بندی به طرح‌بندی اصلی
        main_layout.addWidget(tab_widget)

    def _create_registration_widget(self):
        """ایجاد ویجت ثبت ملک جدید
        
        Returns:
            QWidget: ویجت ثبت ملک جدید
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # گروه‌بندی اطلاعات ملک
        property_group = QGroupBox("اطلاعات ملک تجاری")
        property_layout = QGridLayout(property_group)
        
        # نوع معامله (فروش یا اجاره)
        property_layout.addWidget(QLabel("نوع معامله:"), 0, 0)
        self.deal_type_combo = QComboBox()
        self.deal_type_combo.addItems(["فروش", "اجاره"])
        property_layout.addWidget(self.deal_type_combo, 0, 1)
        
        # نوع ملک تجاری
        property_layout.addWidget(QLabel("نوع ملک:"), 0, 2)
        self.property_type_combo = QComboBox()
        self.property_type_combo.addItems(self.PROPERTY_TYPES)
        property_layout.addWidget(self.property_type_combo, 0, 3)
        
        # منطقه
        property_layout.addWidget(QLabel("منطقه:"), 1, 0)
        self.district_spin = QSpinBox()
        self.district_spin.setRange(1, 22)
        property_layout.addWidget(self.district_spin, 1, 1)
        
        # متراژ
        property_layout.addWidget(QLabel("متراژ (متر مربع):"), 1, 2)
        self.area_spin = QDoubleSpinBox()
        self.area_spin.setRange(10, 10000)
        self.area_spin.setSingleStep(10)
        property_layout.addWidget(self.area_spin, 1, 3)
        
        # سن بنا
        property_layout.addWidget(QLabel("سن بنا (سال):"), 2, 0)
        self.age_spin = QSpinBox()
        self.age_spin.setRange(0, 100)
        property_layout.addWidget(self.age_spin, 2, 1)
        
        # تعداد اتاق
        property_layout.addWidget(QLabel("تعداد اتاق:"), 2, 2)
        self.rooms_spin = QSpinBox()
        self.rooms_spin.setRange(0, 50)
        property_layout.addWidget(self.rooms_spin, 2, 3)
        
        # قیمت
        property_layout.addWidget(QLabel("قیمت (تومان):"), 3, 0)
        self.price_spin = QDoubleSpinBox()
        self.price_spin.setRange(0, 1000000000000)
        self.price_spin.setSingleStep(10000000)
        property_layout.addWidget(self.price_spin, 3, 1)
        
        # ودیعه (برای اجاره)
        property_layout.addWidget(QLabel("ودیعه (تومان):"), 3, 2)
        self.deposit_spin = QDoubleSpinBox()
        self.deposit_spin.setRange(0, 1000000000000)
        self.deposit_spin.setSingleStep(10000000)
        property_layout.addWidget(self.deposit_spin, 3, 3)
        
        # اجاره ماهیانه (برای اجاره)
        property_layout.addWidget(QLabel("اجاره ماهیانه (تومان):"), 4, 0)
        self.rent_spin = QDoubleSpinBox()
        self.rent_spin.setRange(0, 1000000000)
        self.rent_spin.setSingleStep(1000000)
        property_layout.addWidget(self.rent_spin, 4, 1)
        
        # آدرس
        property_layout.addWidget(QLabel("آدرس:"), 5, 0)
        self.address_edit = QTextEdit()
        self.address_edit.setMaximumHeight(60)
        property_layout.addWidget(self.address_edit, 5, 1, 1, 3)
        
        # امکانات
        property_layout.addWidget(QLabel("امکانات:"), 6, 0, Qt.AlignTop)
        facilities_layout = QGridLayout()
        
        self.has_parking_check = QCheckBox("پارکینگ")
        facilities_layout.addWidget(self.has_parking_check, 0, 0)
        
        self.has_elevator_check = QCheckBox("آسانسور")
        facilities_layout.addWidget(self.has_elevator_check, 0, 1)
        
        self.has_storage_check = QCheckBox("انباری")
        facilities_layout.addWidget(self.has_storage_check, 0, 2)
        
        self.has_showcase_check = QCheckBox("ویترین")
        facilities_layout.addWidget(self.has_showcase_check, 1, 0)
        
        self.has_guard_check = QCheckBox("نگهبان")
        facilities_layout.addWidget(self.has_guard_check, 1, 1)
        
        property_layout.addLayout(facilities_layout, 6, 1, 1, 3)
        
        # اضافه کردن گروه به طرح‌بندی اصلی
        layout.addWidget(property_group)
        
        # گروه‌بندی اطلاعات مالک
        owner_group = QGroupBox("اطلاعات مالک")
        owner_layout = QGridLayout(owner_group)
        
        # نام مالک
        owner_layout.addWidget(QLabel("نام مالک:"), 0, 0)
        self.owner_name_edit = QLineEdit()
        owner_layout.addWidget(self.owner_name_edit, 0, 1)
        
        # شماره تلفن مالک
        owner_layout.addWidget(QLabel("شماره تلفن:"), 0, 2)
        self.owner_phone_edit = QLineEdit()
        owner_layout.addWidget(self.owner_phone_edit, 0, 3)
        
        # ایمیل مالک
        owner_layout.addWidget(QLabel("ایمیل:"), 1, 0)
        self.owner_email_edit = QLineEdit()
        owner_layout.addWidget(self.owner_email_edit, 1, 1)
        
        # توضیحات
        owner_layout.addWidget(QLabel("توضیحات:"), 2, 0)
        self.description_edit = QTextEdit()
        owner_layout.addWidget(self.description_edit, 2, 1, 1, 3)
        
        # اضافه کردن گروه به طرح‌بندی اصلی
        layout.addWidget(owner_group)
        
        # دکمه‌های ثبت و پاک کردن
        buttons_layout = QHBoxLayout()
        
        self.clear_button = QPushButton("پاک کردن")
        self.clear_button.setIcon(QIcon("resources/icons/clear.png"))
        self.clear_button.clicked.connect(self.clear_form)
        buttons_layout.addWidget(self.clear_button)
        
        buttons_layout.addStretch()
        
        self.register_button = QPushButton("ثبت ملک")
        self.register_button.setIcon(QIcon("resources/icons/save.png"))
        self.register_button.clicked.connect(self.register_property)
        buttons_layout.addWidget(self.register_button)
        
        layout.addLayout(buttons_layout)
        layout.addStretch()
        
        # اتصال سیگنال‌ها
        self.deal_type_combo.currentIndexChanged.connect(self._handle_deal_type_change)
        
        # تنظیم وضعیت اولیه فیلدهای مرتبط با نوع معامله
        self._handle_deal_type_change(0)
        
        return widget
    
    def _create_property_list_widget(self, deal_type):
        """ایجاد ویجت لیست املاک
        
        Args:
            deal_type (str): نوع معامله ("sale" یا "rent")
            
        Returns:
            QWidget: ویجت لیست املاک
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # فیلترها
        filter_group = QGroupBox("فیلترها")
        filter_layout = QHBoxLayout(filter_group)
        
        # فیلتر نوع ملک
        filter_layout.addWidget(QLabel("نوع ملک:"))
        self.property_type_filter_combo = QComboBox()
        self.property_type_filter_combo.addItem("همه", "all")
        for prop_type in self.PROPERTY_TYPES:
            self.property_type_filter_combo.addItem(prop_type, prop_type)
        filter_layout.addWidget(self.property_type_filter_combo)
        
        # فیلتر منطقه
        filter_layout.addWidget(QLabel("منطقه:"))
        self.district_filter_combo = QComboBox()
        self.district_filter_combo.addItem("همه", 0)
        for i in range(1, 23):
            self.district_filter_combo.addItem(f"منطقه {i}", i)
        filter_layout.addWidget(self.district_filter_combo)
        
        # فیلتر متراژ
        filter_layout.addWidget(QLabel("حداقل متراژ:"))
        self.min_area_filter_spin = QSpinBox()
        self.min_area_filter_spin.setRange(0, 10000)
        self.min_area_filter_spin.setSingleStep(10)
        filter_layout.addWidget(self.min_area_filter_spin)
        
        filter_layout.addWidget(QLabel("حداکثر متراژ:"))
        self.max_area_filter_spin = QSpinBox()
        self.max_area_filter_spin.setRange(0, 10000)
        self.max_area_filter_spin.setValue(10000)
        self.max_area_filter_spin.setSingleStep(10)
        filter_layout.addWidget(self.max_area_filter_spin)
        
        # دکمه اعمال فیلتر
        self.apply_filter_button = QPushButton("اعمال فیلتر")
        self.apply_filter_button.setIcon(QIcon("resources/icons/filter.png"))
        self.apply_filter_button.clicked.connect(lambda: self.apply_filters(deal_type))
        filter_layout.addWidget(self.apply_filter_button)
        
        # دکمه پاک کردن فیلتر
        self.clear_filter_button = QPushButton("پاک کردن فیلتر")
        self.clear_filter_button.setIcon(QIcon("resources/icons/clear.png"))
        self.clear_filter_button.clicked.connect(lambda: self.clear_filters(deal_type))
        filter_layout.addWidget(self.clear_filter_button)
        
        layout.addWidget(filter_group)
        
        # دکمه‌های مدیریت
        actions_layout = QHBoxLayout()
        
        # دکمه بارگیری مجدد
        self.refresh_button = QPushButton("بارگیری مجدد")
        self.refresh_button.setIcon(QIcon("resources/icons/refresh.png"))
        self.refresh_button.clicked.connect(self.load_properties)
        actions_layout.addWidget(self.refresh_button)
        
        actions_layout.addStretch()
        
        # دکمه حذف ملک
        self.delete_button = QPushButton("حذف ملک")
        self.delete_button.setIcon(QIcon("resources/icons/delete.png"))
        self.delete_button.clicked.connect(lambda: self.delete_property(deal_type))
        actions_layout.addWidget(self.delete_button)
        
        # دکمه ویرایش ملک
        self.edit_button = QPushButton("ویرایش ملک")
        self.edit_button.setIcon(QIcon("resources/icons/edit.png"))
        self.edit_button.clicked.connect(lambda: self.edit_property(deal_type))
        actions_layout.addWidget(self.edit_button)
        
        # دکمه مشاهده جزئیات
        self.view_details_button = QPushButton("مشاهده جزئیات")
        self.view_details_button.setIcon(QIcon("resources/icons/details.png"))
        self.view_details_button.clicked.connect(lambda: self.view_property_details(deal_type))
        actions_layout.addWidget(self.view_details_button)
        
        layout.addLayout(actions_layout)
        
        # جدول املاک
        if deal_type == "sale":
            self.sale_table = QTableWidget(0, 8)
            self.sale_table.setHorizontalHeaderLabels([
                "شناسه", "نوع ملک", "منطقه", "متراژ", "سن بنا", "اتاق", "قیمت (تومان)", "وضعیت"
            ])
            layout.addWidget(self.sale_table)
            
            # تنظیم عرض ستون‌ها
            self.sale_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            
        else:  # rent
            self.rent_table = QTableWidget(0, 9)
            self.rent_table.setHorizontalHeaderLabels([
                "شناسه", "نوع ملک", "منطقه", "متراژ", "سن بنا", "اتاق", 
                "ودیعه (تومان)", "اجاره (تومان)", "وضعیت"
            ])
            layout.addWidget(self.rent_table)
            
            # تنظیم عرض ستون‌ها
            self.rent_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        return widget

    def _handle_deal_type_change(self, index):
        """مدیریت تغییر نوع معامله
        
        Args:
            index (int): شاخص انتخاب شده
        """
        is_rent = index == 1  # اجاره
        
        # فعال/غیرفعال کردن فیلدهای مرتبط با اجاره
        self.deposit_spin.setEnabled(is_rent)
        self.rent_spin.setEnabled(is_rent)
        
        # تغییر برچسب قیمت بر اساس نوع معامله
        if is_rent:
            self.price_spin.setEnabled(False)
        else:
            self.price_spin.setEnabled(True)
    
    def clear_form(self):
        """پاک کردن فرم ثبت ملک"""
        self.deal_type_combo.setCurrentIndex(0)
        self.property_type_combo.setCurrentIndex(0)
        self.district_spin.setValue(1)
        self.area_spin.setValue(50)
        self.age_spin.setValue(0)
        self.rooms_spin.setValue(1)
        self.price_spin.setValue(0)
        self.deposit_spin.setValue(0)
        self.rent_spin.setValue(0)
        self.address_edit.clear()
        self.owner_name_edit.clear()
        self.owner_phone_edit.clear()
        self.owner_email_edit.clear()
        self.description_edit.clear()
        self.has_parking_check.setChecked(False)
        self.has_elevator_check.setChecked(False)
        self.has_storage_check.setChecked(False)
        self.has_showcase_check.setChecked(False)
        self.has_guard_check.setChecked(False)
    
    def register_property(self):
        """ثبت ملک جدید"""
        try:
            # بررسی اعتبار داده‌ها
            if not self.owner_name_edit.text():
                QMessageBox.warning(self, "خطا", "نام مالک نمی‌تواند خالی باشد.")
                return
            
            if not self.owner_phone_edit.text():
                QMessageBox.warning(self, "خطا", "شماره تلفن مالک نمی‌تواند خالی باشد.")
                return
            
            if not self.address_edit.toPlainText():
                QMessageBox.warning(self, "خطا", "آدرس نمی‌تواند خالی باشد.")
                return
            
            # ایجاد ساختار داده‌ای ملک تجاری
            property_data = CommercialPropertyStruct()
            
            # نوع معامله
            deal_type = "sale" if self.deal_type_combo.currentIndex() == 0 else "rent"
            
            # مقداردهی فیلدها
            property_data.username = self.current_user.username.encode('utf-8')
            property_data.property_type = self.property_type_combo.currentText().encode('utf-8')
            property_data.district = self.district_spin.value()
            property_data.area = self.area_spin.value()
            property_data.rooms = self.rooms_spin.value()
            property_data.age = self.age_spin.value()
            property_data.price = int(self.price_spin.value())
            property_data.deposit = int(self.deposit_spin.value())
            property_data.rent = int(self.rent_spin.value())
            property_data.address = self.address_edit.toPlainText().encode('utf-8')
            property_data.owner_name = self.owner_name_edit.text().encode('utf-8')
            property_data.owner_phone = self.owner_phone_edit.text().encode('utf-8')
            property_data.owner_email = self.owner_email_edit.text().encode('utf-8')
            property_data.description = self.description_edit.toPlainText().encode('utf-8')
            property_data.has_parking = 1 if self.has_parking_check.isChecked() else 0
            property_data.has_elevator = 1 if self.has_elevator_check.isChecked() else 0
            property_data.has_storage = 1 if self.has_storage_check.isChecked() else 0
            property_data.has_showcase = 1 if self.has_showcase_check.isChecked() else 0
            property_data.has_guard = 1 if self.has_guard_check.isChecked() else 0
            
            # ثبت ملک
            success = False
            if deal_type == "sale":
                success = self.commercial_bridge.register_sale(property_data)
            else:
                success = self.commercial_bridge.register_rental(property_data)
            
            if success:
                QMessageBox.information(self, "ثبت ملک", f"ملک تجاری با موفقیت برای {deal_type} ثبت شد.")
                self.clear_form()
                self.load_properties()
            else:
                QMessageBox.critical(self, "خطا", "ثبت ملک با خطا مواجه شد.")
        
        except Exception as e:
            self.logger.error(f"خطا در ثبت ملک: {str(e)}")
            QMessageBox.critical(self, "خطا", f"عملیات با خطا مواجه شد: {str(e)}")
    
    def load_properties(self):
        """بارگیری لیست املاک"""
        try:
            # بارگیری املاک فروشی
            self.properties_sale = self.commercial_bridge.find_all_properties("sale")
            self._populate_properties_table("sale", self.properties_sale)
            
            # بارگیری املاک اجاره‌ای
            self.properties_rent = self.commercial_bridge.find_all_properties("rent")
            self._populate_properties_table("rent", self.properties_rent)
            
            self.logger.info("لیست املاک تجاری با موفقیت بارگیری شد")
            
        except Exception as e:
            self.logger.error(f"خطا در بارگیری لیست املاک: {str(e)}")
            QMessageBox.critical(self, "خطا", f"بارگیری لیست املاک با خطا مواجه شد: {str(e)}")
    
    def _populate_properties_table(self, deal_type, properties):
        """پر کردن جدول املاک
        
        Args:
            deal_type (str): نوع معامله ("sale" یا "rent")
            properties (list): لیست املاک
        """
        table = self.sale_table if deal_type == "sale" else self.rent_table
        
        # پاک کردن جدول
        table.setRowCount(0)
        
        if not properties:
            return
        
        # اضافه کردن ردیف‌ها به جدول
        for prop in properties:
            row_position = table.rowCount()
            table.insertRow(row_position)
            
            # شناسه
            table.setItem(row_position, 0, QTableWidgetItem(str(prop.id)))
            
            # نوع ملک
            property_type = prop.property_type
            if hasattr(property_type, 'decode'):
                property_type = property_type.decode('utf-8')
            table.setItem(row_position, 1, QTableWidgetItem(property_type))
            
            # منطقه
            table.setItem(row_position, 2, QTableWidgetItem(str(prop.district)))
            
            # متراژ
            area = prop.area if hasattr(prop, 'area') else 0
            table.setItem(row_position, 3, QTableWidgetItem(f"{area:.1f}"))
            
            # سن بنا
            age = prop.age if hasattr(prop, 'age') else 0
            table.setItem(row_position, 4, QTableWidgetItem(str(age)))
            
            # تعداد اتاق
            rooms = prop.rooms if hasattr(prop, 'rooms') else 0
            table.setItem(row_position, 5, QTableWidgetItem(str(rooms)))
            
            if deal_type == "sale":
                # قیمت
                price = prop.price if hasattr(prop, 'price') else 0
                price_item = QTableWidgetItem(f"{price:,}")
                table.setItem(row_position, 6, price_item)
                
                # وضعیت
                is_active = prop.is_active if hasattr(prop, 'is_active') else True
                status_item = QTableWidgetItem("فعال" if is_active else "غیرفعال")
                table.setItem(row_position, 7, status_item)
            else:
                # ودیعه
                deposit = prop.deposit if hasattr(prop, 'deposit') else 0
                deposit_item = QTableWidgetItem(f"{deposit:,}")
                table.setItem(row_position, 6, deposit_item)
                
                # اجاره
                rent = prop.rent if hasattr(prop, 'rent') else 0
                rent_item = QTableWidgetItem(f"{rent:,}")
                table.setItem(row_position, 7, rent_item)
                
                # وضعیت
                is_active = prop.is_active if hasattr(prop, 'is_active') else True
                status_item = QTableWidgetItem("فعال" if is_active else "غیرفعال")
                table.setItem(row_position, 8, status_item)
    
    def apply_filters(self, deal_type):
        """اعمال فیلترها روی جدول املاک
        
        Args:
            deal_type (str): نوع معامله ("sale" یا "rent")
        """
        try:
            # گرفتن مقادیر فیلترها
            property_type = self.property_type_filter_combo.currentData()
            district = self.district_filter_combo.currentData()
            min_area = self.min_area_filter_spin.value()
            max_area = self.max_area_filter_spin.value()
            
            # فیلتر کردن لیست بر اساس مقادیر فیلترها
            filtered_properties = []
            
            properties = self.properties_sale if deal_type == "sale" else self.properties_rent
            
            for prop in properties:
                # بررسی شرایط فیلتر
                property_type_value = prop.property_type
                if hasattr(property_type_value, 'decode'):
                    property_type_value = property_type_value.decode('utf-8')
                    
                if property_type != "all" and property_type_value != property_type:
                    continue
                    
                if district > 0 and prop.district != district:
                    continue
                    
                if prop.area < min_area or prop.area > max_area:
                    continue
                
                # اضافه کردن به لیست فیلتر شده
                filtered_properties.append(prop)
            
            # نمایش املاک فیلتر شده
            self._populate_properties_table(deal_type, filtered_properties)
            
            self.logger.info(f"فیلترها با موفقیت اعمال شدند. {len(filtered_properties)} ملک یافت شد.")
            
        except Exception as e:
            self.logger.error(f"خطا در اعمال فیلترها: {str(e)}")
            QMessageBox.critical(self, "خطا", f"اعمال فیلترها با خطا مواجه شد: {str(e)}")
    
    def clear_filters(self, deal_type):
        """پاک کردن فیلترها و نمایش تمام املاک
        
        Args:
            deal_type (str): نوع معامله ("sale" یا "rent")
        """
        try:
            # بازنشانی مقادیر فیلترها
            self.property_type_filter_combo.setCurrentIndex(0)
            self.district_filter_combo.setCurrentIndex(0)
            self.min_area_filter_spin.setValue(0)
            self.max_area_filter_spin.setValue(10000)
            
            # نمایش تمام املاک
            properties = self.properties_sale if deal_type == "sale" else self.properties_rent
            self._populate_properties_table(deal_type, properties)
            
            self.logger.info("فیلترها پاک شدند.")
            
        except Exception as e:
            self.logger.error(f"خطا در پاک کردن فیلترها: {str(e)}")
    
    def delete_property(self, deal_type):
        """حذف ملک انتخاب شده
        
        Args:
            deal_type (str): نوع معامله ("sale" یا "rent")
        """
        try:
            table = self.sale_table if deal_type == "sale" else self.rent_table
            selected_row = table.currentRow()
            
            if selected_row < 0:
                QMessageBox.warning(self, "هشدار", "لطفاً یک ملک را انتخاب کنید.")
                return
            
            property_id = int(table.item(selected_row, 0).text())
            
            # تائید حذف
            reply = QMessageBox.question(
                self, "تائید حذف", 
                f"آیا از حذف ملک با شناسه {property_id} اطمینان دارید؟",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # حذف ملک
                success = self.commercial_bridge.delete_property(property_id, deal_type)
                
                if success:
                    QMessageBox.information(self, "حذف ملک", "ملک با موفقیت حذف شد.")
                    self.load_properties()
                else:
                    QMessageBox.critical(self, "خطا", "حذف ملک با خطا مواجه شد.")
        
        except Exception as e:
            self.logger.error(f"خطا در حذف ملک: {str(e)}")
            QMessageBox.critical(self, "خطا", f"حذف ملک با خطا مواجه شد: {str(e)}")
    
    def edit_property(self, deal_type):
        """ویرایش ملک انتخاب شده
        
        Args:
            deal_type (str): نوع معامله ("sale" یا "rent")
        """
        # در نسخه فعلی پیاده‌سازی نشده است
        QMessageBox.information(self, "ویرایش ملک", "ویرایش ملک در نسخه فعلی پیاده‌سازی نشده است.")
    
    def view_property_details(self, deal_type):
        """نمایش جزئیات ملک انتخاب شده
        
        Args:
            deal_type (str): نوع معامله ("sale" یا "rent")
        """
        try:
            table = self.sale_table if deal_type == "sale" else self.rent_table
            selected_row = table.currentRow()
            
            if selected_row < 0:
                QMessageBox.warning(self, "هشدار", "لطفاً یک ملک را انتخاب کنید.")
                return
            
            property_id = int(table.item(selected_row, 0).text())
            
            # پیدا کردن ملک در لیست
            properties = self.properties_sale if deal_type == "sale" else self.properties_rent
            
            selected_property = None
            for prop in properties:
                if prop.id == property_id:
                    selected_property = prop
                    break
            
            if not selected_property:
                QMessageBox.warning(self, "هشدار", "ملک مورد نظر یافت نشد.")
                return
            
            # نمایش پنجره جزئیات
            property_type_value = selected_property.property_type
            if hasattr(property_type_value, 'decode'):
                property_type_value = property_type_value.decode('utf-8')
                
            details_message = f"""
اطلاعات ملک تجاری:
--------------------
شناسه: {selected_property.id}
نوع ملک: {property_type_value}
منطقه: {selected_property.district}
متراژ: {selected_property.area} متر مربع
تعداد اتاق: {selected_property.rooms}
سن بنا: {selected_property.age} سال

آدرس: {selected_property.address.decode('utf-8')}

مالک: {selected_property.owner_name.decode('utf-8')}
تلفن: {selected_property.owner_phone.decode('utf-8')}
ایمیل: {selected_property.owner_email.decode('utf-8')}

امکانات:
- پارکینگ: {'دارد' if selected_property.has_parking else 'ندارد'}
- آسانسور: {'دارد' if selected_property.has_elevator else 'ندارد'}
- انباری: {'دارد' if selected_property.has_storage else 'ندارد'}
- ویترین: {'دارد' if selected_property.has_showcase else 'ندارد'}
- نگهبان: {'دارد' if selected_property.has_guard else 'ندارد'}

توضیحات: {selected_property.description.decode('utf-8')}
"""
            
            if deal_type == "sale":
                details_message += f"\nقیمت: {selected_property.price:,} تومان"
            else:
                details_message += f"\nودیعه: {selected_property.deposit:,} تومان"
                details_message += f"\nاجاره ماهیانه: {selected_property.rent:,} تومان"
            
            # نمایش پیغام
            msg_box = QMessageBox()
            msg_box.setWindowTitle("جزئیات ملک تجاری")
            msg_box.setText(details_message)
            msg_box.setIcon(QMessageBox.Information)
            msg_box.exec_()
            
        except Exception as e:
            self.logger.error(f"خطا در نمایش جزئیات ملک: {str(e)}")
            QMessageBox.critical(self, "خطا", f"نمایش جزئیات با خطا مواجه شد: {str(e)}") 