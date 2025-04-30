#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ماژول تب مسکونی
این ماژول پیاده‌سازی تب مدیریت املاک مسکونی را ارائه می‌دهد.
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

from bridge.residential_bridge import ResidentialBridge, ResidentialPropertyStruct


class ResidentialTab(QWidget):
    """ویجت تب مدیریت املاک مسکونی"""
    
    def __init__(self, current_user, parent=None):
        """سازنده تب مسکونی
        
        Args:
            current_user (User): کاربر فعلی
            parent (QWidget, optional): ویجت والد. پیش‌فرض None.
        """
        super().__init__(parent)
        
        self.logger = logging.getLogger(__name__)
        self.current_user = current_user
        
        # ایجاد پل ارتباطی با بخش C
        self.residential_bridge = ResidentialBridge()
        
        # لیست املاک
        self.properties_sale = []
        self.properties_rent = []
        
        # راه‌اندازی رابط کاربری
        self.init_ui()
        
        # بارگیری داده‌های اولیه
        self.load_properties()
        
        self.logger.info("تب مدیریت املاک مسکونی راه‌اندازی شد")
    
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
        property_group = QGroupBox("اطلاعات ملک")
        property_layout = QGridLayout(property_group)
        
        # نوع معامله (فروش یا اجاره)
        property_layout.addWidget(QLabel("نوع معامله:"), 0, 0)
        self.deal_type_combo = QComboBox()
        self.deal_type_combo.addItems(["فروش", "اجاره"])
        property_layout.addWidget(self.deal_type_combo, 0, 1)
        
        # منطقه
        property_layout.addWidget(QLabel("منطقه:"), 0, 2)
        self.district_spin = QSpinBox()
        self.district_spin.setRange(1, 22)
        property_layout.addWidget(self.district_spin, 0, 3)
        
        # متراژ
        property_layout.addWidget(QLabel("متراژ (متر مربع):"), 1, 0)
        self.area_spin = QDoubleSpinBox()
        self.area_spin.setRange(20, 1000)
        self.area_spin.setSingleStep(5)
        property_layout.addWidget(self.area_spin, 1, 1)
        
        # سن بنا
        property_layout.addWidget(QLabel("سن بنا (سال):"), 1, 2)
        self.age_spin = QSpinBox()
        self.age_spin.setRange(0, 100)
        property_layout.addWidget(self.age_spin, 1, 3)
        
        # تعداد اتاق خواب
        property_layout.addWidget(QLabel("تعداد اتاق خواب:"), 2, 0)
        self.bedrooms_spin = QSpinBox()
        self.bedrooms_spin.setRange(0, 10)
        property_layout.addWidget(self.bedrooms_spin, 2, 1)
        
        # طبقه
        property_layout.addWidget(QLabel("طبقه:"), 2, 2)
        self.floor_spin = QSpinBox()
        self.floor_spin.setRange(-1, 100)
        property_layout.addWidget(self.floor_spin, 2, 3)
        
        # قیمت
        property_layout.addWidget(QLabel("قیمت (تومان):"), 3, 0)
        self.price_spin = QDoubleSpinBox()
        self.price_spin.setRange(0, 1000000000000)
        self.price_spin.setSingleStep(1000000)
        property_layout.addWidget(self.price_spin, 3, 1)
        
        # ودیعه (برای اجاره)
        property_layout.addWidget(QLabel("ودیعه (تومان):"), 3, 2)
        self.deposit_spin = QDoubleSpinBox()
        self.deposit_spin.setRange(0, 1000000000000)
        self.deposit_spin.setSingleStep(1000000)
        property_layout.addWidget(self.deposit_spin, 3, 3)
        
        # اجاره ماهیانه (برای اجاره)
        property_layout.addWidget(QLabel("اجاره ماهیانه (تومان):"), 4, 0)
        self.rent_spin = QDoubleSpinBox()
        self.rent_spin.setRange(0, 1000000000)
        self.rent_spin.setSingleStep(100000)
        property_layout.addWidget(self.rent_spin, 4, 1)
        
        # آدرس
        property_layout.addWidget(QLabel("آدرس:"), 5, 0)
        self.address_edit = QTextEdit()
        self.address_edit.setMaximumHeight(60)
        property_layout.addWidget(self.address_edit, 5, 1, 1, 3)
        
        # امکانات
        property_layout.addWidget(QLabel("امکانات:"), 6, 0, Qt.AlignTop)
        facilities_layout = QGridLayout()
        
        self.has_elevator_check = QCheckBox("آسانسور")
        facilities_layout.addWidget(self.has_elevator_check, 0, 0)
        
        self.has_parking_check = QCheckBox("پارکینگ")
        facilities_layout.addWidget(self.has_parking_check, 0, 1)
        
        self.has_storage_check = QCheckBox("انباری")
        facilities_layout.addWidget(self.has_storage_check, 0, 2)
        
        self.has_balcony_check = QCheckBox("بالکن")
        facilities_layout.addWidget(self.has_balcony_check, 1, 0)
        
        self.is_furnished_check = QCheckBox("مبله")
        facilities_layout.addWidget(self.is_furnished_check, 1, 1)
        
        self.has_ac_check = QCheckBox("سیستم تهویه")
        facilities_layout.addWidget(self.has_ac_check, 1, 2)
        
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
        self.min_area_filter_spin.setRange(0, 1000)
        self.min_area_filter_spin.setSingleStep(10)
        filter_layout.addWidget(self.min_area_filter_spin)
        
        filter_layout.addWidget(QLabel("حداکثر متراژ:"))
        self.max_area_filter_spin = QSpinBox()
        self.max_area_filter_spin.setRange(0, 1000)
        self.max_area_filter_spin.setValue(1000)
        self.max_area_filter_spin.setSingleStep(10)
        filter_layout.addWidget(self.max_area_filter_spin)
        
        # فیلتر اتاق خواب
        filter_layout.addWidget(QLabel("اتاق خواب:"))
        self.bedrooms_filter_combo = QComboBox()
        self.bedrooms_filter_combo.addItem("همه", -1)
        for i in range(0, 6):
            self.bedrooms_filter_combo.addItem(str(i), i)
        self.bedrooms_filter_combo.addItem("6+", 6)
        filter_layout.addWidget(self.bedrooms_filter_combo)
        
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
                "شناسه", "منطقه", "متراژ", "اتاق خواب", "سن بنا", "طبقه", "قیمت (تومان)", "وضعیت"
            ])
            layout.addWidget(self.sale_table)
            
            # تنظیم عرض ستون‌ها
            self.sale_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            
        else:  # rent
            self.rent_table = QTableWidget(0, 9)
            self.rent_table.setHorizontalHeaderLabels([
                "شناسه", "منطقه", "متراژ", "اتاق خواب", "سن بنا", "طبقه", 
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
        self.district_spin.setValue(1)
        self.area_spin.setValue(50)
        self.age_spin.setValue(0)
        self.bedrooms_spin.setValue(1)
        self.floor_spin.setValue(0)
        self.price_spin.setValue(0)
        self.deposit_spin.setValue(0)
        self.rent_spin.setValue(0)
        self.address_edit.clear()
        self.owner_name_edit.clear()
        self.owner_phone_edit.clear()
        self.owner_email_edit.clear()
        self.description_edit.clear()
        self.has_elevator_check.setChecked(False)
        self.has_parking_check.setChecked(False)
        self.has_storage_check.setChecked(False)
        self.has_balcony_check.setChecked(False)
        self.is_furnished_check.setChecked(False)
        self.has_ac_check.setChecked(False)
    
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
            
            # نوع معامله
            deal_type = "sale" if self.deal_type_combo.currentIndex() == 0 else "rent"
            
            # به جای استفاده از ResidentialPropertyStruct، از پارامترهای مستقیم استفاده می‌کنیم
            username = self.current_user.username
            district = str(self.district_spin.value())  # تبدیل به رشته
            address = self.address_edit.toPlainText()
            building_age = self.age_spin.value()
            area_size = float(self.area_spin.value())
            bedrooms = self.bedrooms_spin.value()
            floor = self.floor_spin.value()
            total_floors = 10  # مقدار پیش‌فرض
            
            has_elevator = 1 if self.has_elevator_check.isChecked() else 0
            has_parking = 1 if self.has_parking_check.isChecked() else 0
            has_storage = 1 if self.has_storage_check.isChecked() else 0
            
            contact_phone = self.owner_phone_edit.text()
            description = self.description_edit.toPlainText()
            
            # ثبت ملک
            result = None
            if deal_type == "sale":
                selling_price = int(self.price_spin.value())
                result = self.residential_bridge.register_sale(
                    username, district, address, building_age, area_size,
                    bedrooms, floor, total_floors, has_elevator, has_parking,
                    has_storage, selling_price, contact_phone, description
                )
            else:
                mortgage_amount = int(self.deposit_spin.value())
                monthly_rent = int(self.rent_spin.value())
                result = self.residential_bridge.register_rental(
                    username, district, address, building_age, area_size,
                    bedrooms, floor, total_floors, has_elevator, has_parking,
                    has_storage, mortgage_amount, monthly_rent, contact_phone, description
                )
            
            if result and result.get("success", False):
                QMessageBox.information(self, "ثبت ملک", f"ملک مسکونی با موفقیت برای {deal_type} ثبت شد.")
                self.clear_form()
                self.load_properties()
            else:
                error_msg = result.get("error", "خطای نامشخص") if result else "خطای نامشخص"
                QMessageBox.critical(self, "خطا", f"ثبت ملک با خطا مواجه شد: {error_msg}")
        
        except Exception as e:
            self.logger.error(f"خطا در ثبت ملک: {str(e)}")
            QMessageBox.critical(self, "خطا", f"عملیات با خطا مواجه شد: {str(e)}")
    
    def load_properties(self):
        """بارگیری لیست املاک"""
        try:
            # بارگیری املاک فروشی
            self.properties_sale = self.residential_bridge.find_all_properties("sale")
            self._populate_properties_table("sale", self.properties_sale)
            
            # بارگیری املاک اجاره‌ای
            self.properties_rent = self.residential_bridge.find_all_properties("rent")
            self._populate_properties_table("rent", self.properties_rent)
            
            self.logger.info("لیست املاک مسکونی با موفقیت بارگیری شد")
            
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
            
            # منطقه
            table.setItem(row_position, 1, QTableWidgetItem(str(prop.district)))
            
            # متراژ
            table.setItem(row_position, 2, QTableWidgetItem(f"{prop.area:.1f}"))
            
            # اتاق خواب
            table.setItem(row_position, 3, QTableWidgetItem(str(prop.bedrooms)))
            
            # سن بنا
            table.setItem(row_position, 4, QTableWidgetItem(str(prop.age)))
            
            # طبقه
            table.setItem(row_position, 5, QTableWidgetItem(str(prop.floor)))
            
            if deal_type == "sale":
                # قیمت
                price_item = QTableWidgetItem(f"{prop.price:,}")
                table.setItem(row_position, 6, price_item)
                
                # وضعیت
                status_item = QTableWidgetItem("فعال" if prop.is_active else "غیرفعال")
                table.setItem(row_position, 7, status_item)
            else:
                # ودیعه
                deposit_item = QTableWidgetItem(f"{prop.deposit:,}")
                table.setItem(row_position, 6, deposit_item)
                
                # اجاره
                rent_item = QTableWidgetItem(f"{prop.rent:,}")
                table.setItem(row_position, 7, rent_item)
                
                # وضعیت
                status_item = QTableWidgetItem("فعال" if prop.is_active else "غیرفعال")
                table.setItem(row_position, 8, status_item)
    
    def apply_filters(self, deal_type):
        """اعمال فیلترها روی جدول املاک
        
        Args:
            deal_type (str): نوع معامله ("sale" یا "rent")
        """
        try:
            # گرفتن مقادیر فیلترها
            district = self.district_filter_combo.currentData()
            min_area = self.min_area_filter_spin.value()
            max_area = self.max_area_filter_spin.value()
            bedrooms = self.bedrooms_filter_combo.currentData()
            
            # فیلتر کردن لیست بر اساس مقادیر فیلترها
            filtered_properties = []
            
            properties = self.properties_sale if deal_type == "sale" else self.properties_rent
            
            for prop in properties:
                # بررسی شرایط فیلتر
                if district > 0 and prop.district != district:
                    continue
                    
                if prop.area < min_area or prop.area > max_area:
                    continue
                    
                if bedrooms >= 0:
                    if bedrooms == 6:  # 6+
                        if prop.bedrooms < 6:
                            continue
                    elif prop.bedrooms != bedrooms:
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
            self.district_filter_combo.setCurrentIndex(0)
            self.min_area_filter_spin.setValue(0)
            self.max_area_filter_spin.setValue(1000)
            self.bedrooms_filter_combo.setCurrentIndex(0)
            
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
                success = self.residential_bridge.delete_property(property_id, deal_type)
                
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
            details_message = f"""
اطلاعات ملک مسکونی:
--------------------
شناسه: {selected_property.id}
منطقه: {selected_property.district}
متراژ: {selected_property.area} متر مربع
تعداد اتاق خواب: {selected_property.bedrooms}
سن بنا: {selected_property.age} سال
طبقه: {selected_property.floor}

آدرس: {selected_property.address.decode('utf-8')}

مالک: {selected_property.owner_name.decode('utf-8')}
تلفن: {selected_property.owner_phone.decode('utf-8')}
ایمیل: {selected_property.owner_email.decode('utf-8')}

امکانات:
- آسانسور: {'دارد' if selected_property.has_elevator else 'ندارد'}
- پارکینگ: {'دارد' if selected_property.has_parking else 'ندارد'}
- انباری: {'دارد' if selected_property.has_storage else 'ندارد'}
- بالکن: {'دارد' if selected_property.has_balcony else 'ندارد'}
- مبله: {'است' if selected_property.is_furnished else 'نیست'}
- سیستم تهویه: {'دارد' if selected_property.has_ac else 'ندارد'}

توضیحات: {selected_property.description.decode('utf-8')}
"""
            
            if deal_type == "sale":
                details_message += f"\nقیمت: {selected_property.price:,} تومان"
            else:
                details_message += f"\nودیعه: {selected_property.deposit:,} تومان"
                details_message += f"\nاجاره ماهیانه: {selected_property.rent:,} تومان"
            
            # نمایش پیغام
            msg_box = QMessageBox()
            msg_box.setWindowTitle("جزئیات ملک مسکونی")
            msg_box.setText(details_message)
            msg_box.setIcon(QMessageBox.Information)
            msg_box.exec_()
            
        except Exception as e:
            self.logger.error(f"خطا در نمایش جزئیات ملک: {str(e)}")
            QMessageBox.critical(self, "خطا", f"نمایش جزئیات با خطا مواجه شد: {str(e)}") 