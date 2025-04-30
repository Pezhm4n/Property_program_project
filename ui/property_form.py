#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
فرم ثبت املاک در سیستم مدیریت املاک
این فرم برای ثبت انواع مختلف املاک (مسکونی، تجاری و زمین) استفاده می‌شود
"""

import sys
import os
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QLineEdit, QPushButton, QComboBox,
                             QSpinBox, QDoubleSpinBox, QCheckBox, QTabWidget,
                             QMessageBox, QFormLayout, QGroupBox,
                             QRadioButton, QButtonGroup)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

# واردات کتابخانه‌های لازم برای ارتباط با هسته سیستم
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from bridge import property_bridge


class PropertyForm(QWidget):
    """کلاس فرم ثبت ملک جدید"""
    
    def __init__(self, username=None, parent=None):
        super(PropertyForm, self).__init__(parent)
        self.username = username
        self.setWindowTitle("ثبت ملک جدید")
        self.setMinimumSize(800, 600)
        self.setLayoutDirection(Qt.RightToLeft)  # راست به چپ برای زبان فارسی
        
        # تعریف فونت فارسی
        self.farsi_font = QFont()
        self.farsi_font.setFamily("Tahoma")
        self.farsi_font.setPointSize(10)
        self.setFont(self.farsi_font)
        
        self.init_ui()
    
    def init_ui(self):
        """راه‌اندازی رابط کاربری"""
        main_layout = QVBoxLayout()
        
        # انتخاب نوع معامله
        deal_group = QGroupBox("نوع معامله")
        deal_layout = QHBoxLayout()
        
        self.deal_type_group = QButtonGroup(self)
        self.sale_radio = QRadioButton("فروش")
        self.rent_radio = QRadioButton("اجاره")
        self.sale_radio.setChecked(True)
        
        self.deal_type_group.addButton(self.sale_radio, 1)
        self.deal_type_group.addButton(self.rent_radio, 2)
        
        deal_layout.addWidget(self.sale_radio)
        deal_layout.addWidget(self.rent_radio)
        deal_group.setLayout(deal_layout)
        
        # انتخاب نوع ملک
        property_type_group = QGroupBox("نوع ملک")
        property_type_layout = QHBoxLayout()
        
        self.property_type = QComboBox()
        self.property_type.addItems(["مسکونی", "تجاری", "زمین"])
        self.property_type.currentIndexChanged.connect(self.change_property_form)
        
        property_type_layout.addWidget(self.property_type)
        property_type_group.setLayout(property_type_layout)
        
        # اطلاعات کلی ملک
        general_group = QGroupBox("اطلاعات کلی ملک")
        general_layout = QFormLayout()
        
        self.district_input = QLineEdit()
        self.address_input = QLineEdit()
        self.area_input = QDoubleSpinBox()
        self.area_input.setRange(10, 10000)
        self.area_input.setSuffix(" متر مربع")
        
        general_layout.addRow("منطقه:", self.district_input)
        general_layout.addRow("آدرس:", self.address_input)
        general_layout.addRow("متراژ:", self.area_input)
        
        general_group.setLayout(general_layout)
        
        # تب‌های مخصوص هر نوع ملک
        self.property_tabs = QTabWidget()
        
        # فرم مسکونی
        self.residential_widget = QWidget()
        residential_layout = QFormLayout()
        
        self.building_age = QSpinBox()
        self.building_age.setRange(0, 100)
        self.building_age.setSuffix(" سال")
        
        self.bedrooms = QSpinBox()
        self.bedrooms.setRange(0, 10)
        
        self.floor = QSpinBox()
        self.floor.setRange(-1, 100)
        
        self.total_floors = QSpinBox()
        self.total_floors.setRange(1, 100)
        
        self.has_elevator = QCheckBox("دارد")
        self.has_parking = QCheckBox("دارد")
        self.has_storage = QCheckBox("دارد")
        
        residential_layout.addRow("سن بنا:", self.building_age)
        residential_layout.addRow("تعداد اتاق خواب:", self.bedrooms)
        residential_layout.addRow("طبقه:", self.floor)
        residential_layout.addRow("تعداد کل طبقات:", self.total_floors)
        residential_layout.addRow("آسانسور:", self.has_elevator)
        residential_layout.addRow("پارکینگ:", self.has_parking)
        residential_layout.addRow("انباری:", self.has_storage)
        
        self.residential_widget.setLayout(residential_layout)
        
        # فرم تجاری
        self.commercial_widget = QWidget()
        commercial_layout = QFormLayout()
        
        self.commercial_type = QComboBox()
        self.commercial_type.addItems(["مغازه", "دفتر کار", "انبار", "سایر"])
        
        self.has_showcase = QCheckBox("دارد")
        self.commercial_floor = QSpinBox()
        self.commercial_floor.setRange(-2, 100)
        
        self.is_active_business = QCheckBox("در حال فعالیت است")
        
        commercial_layout.addRow("نوع واحد تجاری:", self.commercial_type)
        commercial_layout.addRow("ویترین:", self.has_showcase)
        commercial_layout.addRow("طبقه:", self.commercial_floor)
        commercial_layout.addRow("وضعیت کسب و کار:", self.is_active_business)
        
        self.commercial_widget.setLayout(commercial_layout)
        
        # فرم زمین
        self.land_widget = QWidget()
        land_layout = QFormLayout()
        
        self.land_type = QComboBox()
        self.land_type.addItems(["مسکونی", "تجاری", "کشاورزی", "صنعتی"])
        
        self.distance_to_road = QSpinBox()
        self.distance_to_road.setRange(0, 10000)
        self.distance_to_road.setSuffix(" متر")
        
        self.has_well = QCheckBox("دارد")
        
        land_layout.addRow("نوع کاربری زمین:", self.land_type)
        land_layout.addRow("فاصله تا جاده اصلی:", self.distance_to_road)
        land_layout.addRow("چاه آب:", self.has_well)
        
        self.land_widget.setLayout(land_layout)
        
        # اضافه کردن تب‌ها
        self.property_tabs.addTab(self.residential_widget, "مسکونی")
        self.property_tabs.addTab(self.commercial_widget, "تجاری")
        self.property_tabs.addTab(self.land_widget, "زمین")
        
        # گروه قیمت‌گذاری
        pricing_group = QGroupBox("قیمت‌گذاری")
        self.pricing_layout = QVBoxLayout()
        
        # فرم قیمت برای فروش
        self.sale_form = QFormLayout()
        self.selling_price = QDoubleSpinBox()
        self.selling_price.setRange(0, 1000000000000)  # حداکثر ۱ تریلیون
        self.selling_price.setSuffix(" تومان")
        self.selling_price.setGroupSeparatorShown(True)
        self.sale_form.addRow("قیمت فروش:", self.selling_price)
        
        # فرم قیمت برای اجاره
        self.rent_form = QFormLayout()
        self.rent_widget = QWidget()
        rent_form_layout = QFormLayout()
        
        self.mortgage_amount = QDoubleSpinBox()
        self.mortgage_amount.setRange(0, 10000000000)  # حداکثر ۱۰ میلیارد
        self.mortgage_amount.setSuffix(" تومان")
        self.mortgage_amount.setGroupSeparatorShown(True)
        
        self.monthly_rent = QDoubleSpinBox()
        self.monthly_rent.setRange(0, 1000000000)  # حداکثر ۱ میلیارد
        self.monthly_rent.setSuffix(" تومان")
        self.monthly_rent.setGroupSeparatorShown(True)
        
        rent_form_layout.addRow("مبلغ ودیعه:", self.mortgage_amount)
        rent_form_layout.addRow("اجاره ماهیانه:", self.monthly_rent)
        
        self.rent_widget.setLayout(rent_form_layout)
        self.rent_widget.hide()  # در ابتدا مخفی است
        
        # اضافه کردن فرم‌های قیمت به لایوت
        self.pricing_layout.addLayout(self.sale_form)
        self.pricing_layout.addWidget(self.rent_widget)
        
        pricing_group.setLayout(self.pricing_layout)
        
        # اتصال رادیو باتن‌ها به تغییر فرم قیمت
        self.sale_radio.toggled.connect(self.toggle_price_form)
        
        # دکمه‌های عملیاتی
        buttons_layout = QHBoxLayout()
        
        self.submit_button = QPushButton("ثبت اطلاعات")
        self.submit_button.setMinimumHeight(40)
        self.submit_button.clicked.connect(self.submit_property)
        
        self.clear_button = QPushButton("پاک کردن")
        self.clear_button.clicked.connect(self.clear_form)
        
        self.cancel_button = QPushButton("انصراف")
        self.cancel_button.clicked.connect(self.close)
        
        buttons_layout.addWidget(self.submit_button)
        buttons_layout.addWidget(self.clear_button)
        buttons_layout.addWidget(self.cancel_button)
        
        # اضافه کردن همه عناصر به لایوت اصلی
        main_layout.addWidget(deal_group)
        main_layout.addWidget(property_type_group)
        main_layout.addWidget(general_group)
        main_layout.addWidget(self.property_tabs)
        main_layout.addWidget(pricing_group)
        main_layout.addLayout(buttons_layout)
        
        self.setLayout(main_layout)
        
        # تنظیم تب فعال براساس کومبوباکس نوع ملک
        self.change_property_form(0)
    
    def change_property_form(self, index):
        """تغییر فرم اطلاعات بر اساس نوع ملک"""
        self.property_tabs.setCurrentIndex(index)
    
    def toggle_price_form(self):
        """تغییر فرم قیمت بر اساس نوع معامله"""
        if self.sale_radio.isChecked():
            self.rent_widget.hide()
        else:
            self.rent_widget.show()
    
    def clear_form(self):
        """پاک کردن فرم‌ها"""
        self.district_input.clear()
        self.address_input.clear()
        self.area_input.setValue(0)
        
        # پاک کردن فرم مسکونی
        self.building_age.setValue(0)
        self.bedrooms.setValue(0)
        self.floor.setValue(0)
        self.total_floors.setValue(1)
        self.has_elevator.setChecked(False)
        self.has_parking.setChecked(False)
        self.has_storage.setChecked(False)
        
        # پاک کردن فرم تجاری
        self.commercial_type.setCurrentIndex(0)
        self.has_showcase.setChecked(False)
        self.commercial_floor.setValue(0)
        self.is_active_business.setChecked(False)
        
        # پاک کردن فرم زمین
        self.land_type.setCurrentIndex(0)
        self.distance_to_road.setValue(0)
        self.has_well.setChecked(False)
        
        # پاک کردن فرم قیمت
        self.selling_price.setValue(0)
        self.mortgage_amount.setValue(0)
        self.monthly_rent.setValue(0)
        
    def validate_inputs(self):
        """اعتبارسنجی ورودی‌ها"""
        if not self.district_input.text():
            QMessageBox.warning(self, "خطا", "لطفاً منطقه را وارد کنید")
            return False
            
        if not self.address_input.text():
            QMessageBox.warning(self, "خطا", "لطفاً آدرس را وارد کنید")
            return False
            
        if self.area_input.value() <= 0:
            QMessageBox.warning(self, "خطا", "لطفاً متراژ معتبر وارد کنید")
            return False
            
        # بررسی نوع معامله و قیمت‌ها
        if self.sale_radio.isChecked() and self.selling_price.value() <= 0:
            QMessageBox.warning(self, "خطا", "لطفاً قیمت فروش را وارد کنید")
            return False
            
        if self.rent_radio.isChecked() and self.mortgage_amount.value() <= 0 and self.monthly_rent.value() <= 0:
            QMessageBox.warning(self, "خطا", "لطفاً مبلغ ودیعه یا اجاره ماهیانه را وارد کنید")
            return False
            
        return True
    
    def submit_property(self):
        """ثبت ملک در سیستم"""
        if not self.validate_inputs():
            return
            
        try:
            # اطلاعات عمومی
            property_data = {
                "district": self.district_input.text(),
                "address": self.address_input.text(),
                "area": self.area_input.value(),
                "deal_type": "sale" if self.sale_radio.isChecked() else "rent"
            }
            
            # افزودن اطلاعات قیمت
            if property_data["deal_type"] == "sale":
                property_data["selling_price"] = self.selling_price.value()
            else:
                property_data["mortgage_amount"] = self.mortgage_amount.value()
                property_data["monthly_rent"] = self.monthly_rent.value()
            
            # افزودن اطلاعات اختصاصی بر اساس نوع ملک
            property_type = self.property_type.currentText()
            
            if property_type == "مسکونی":
                property_data["type"] = "residential"
                property_data["building_age"] = self.building_age.value()
                property_data["bedrooms"] = self.bedrooms.value()
                property_data["floor"] = self.floor.value()
                property_data["total_floors"] = self.total_floors.value()
                property_data["has_elevator"] = self.has_elevator.isChecked()
                property_data["has_parking"] = self.has_parking.isChecked()
                property_data["has_storage"] = self.has_storage.isChecked()
                
            elif property_type == "تجاری":
                property_data["type"] = "commercial"
                property_data["commercial_type"] = self.commercial_type.currentText()
                property_data["has_showcase"] = self.has_showcase.isChecked()
                property_data["floor"] = self.commercial_floor.value()
                property_data["is_active_business"] = self.is_active_business.isChecked()
                
            elif property_type == "زمین":
                property_data["type"] = "land"
                property_data["land_type"] = self.land_type.currentText()
                property_data["distance_to_road"] = self.distance_to_road.value()
                property_data["has_well"] = self.has_well.isChecked()
                
            # اضافه کردن نام کاربری
            if self.username:
                property_data["username"] = self.username
            
            # فراخوانی تابع ثبت ملک از bridge
            result = property_bridge.register_property(property_data)
            
            if result and result.get("success"):
                QMessageBox.information(self, "موفقیت", f"ملک با شناسه {result.get('property_id')} با موفقیت ثبت شد")
                self.clear_form()
            else:
                error_message = result.get("error", "خطای نامشخص در ثبت ملک")
                QMessageBox.critical(self, "خطا", error_message)
                
        except Exception as e:
            QMessageBox.critical(self, "خطای سیستم", f"خطا در ثبت ملک: {str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # تنظیم استایل برنامه
    app.setStyle("Fusion")
    
    form = PropertyForm("test_user")
    form.show()
    
    sys.exit(app.exec_()) 