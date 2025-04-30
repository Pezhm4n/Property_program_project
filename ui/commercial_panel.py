"""
ماژول پنل املاک تجاری - بخشی از سیستم مدیریت املاک

این ماژول پنل‌های مربوط به نمایش، ثبت و جستجوی املاک تجاری را پیاده‌سازی می‌کند.
"""

import os
import sys
import logging
from datetime import datetime

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QComboBox, QPushButton, QTableWidget, 
                            QTableWidgetItem, QSpinBox, QDoubleSpinBox, 
                            QMessageBox, QTabWidget, QFormLayout, QGroupBox,
                            QCheckBox, QDateEdit, QFileDialog)
from PyQt5.QtCore import Qt, QDate, pyqtSignal

# افزودن مسیر اصلی پروژه به sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../python/')))

from property_management.bridge.commercial_bridge import CommercialBridge
from property_management.utils.validation import validate_email, validate_phone

# تنظیم لاگر
logger = logging.getLogger(__name__)

class CommercialPropertyPanel(QWidget):
    """پنل اصلی مدیریت املاک تجاری"""
    
    property_updated = pyqtSignal()  # سیگنال برای اطلاع‌رسانی به‌روزرسانی املاک
    
    # انواع ملک تجاری
    PROPERTY_TYPES = [
        "مغازه",
        "دفتر کار",
        "انبار",
        "کارگاه",
        "سوله",
        "مجتمع تجاری",
        "سایر"
    ]
    
    def __init__(self, parent=None, current_user=None):
        super().__init__(parent)
        self.current_user = current_user
        self.commercial_bridge = CommercialBridge()
        self.initUI()
        
    def initUI(self):
        """راه‌اندازی واسط کاربری"""
        main_layout = QVBoxLayout()
        
        # تب‌های اصلی
        tab_widget = QTabWidget()
        tab_widget.addTab(self.create_register_tab(), "ثبت ملک تجاری")
        tab_widget.addTab(self.create_search_tab(), "جستجوی املاک تجاری")
        
        main_layout.addWidget(tab_widget)
        self.setLayout(main_layout)
        
    def create_register_tab(self):
        """ایجاد تب ثبت ملک تجاری"""
        register_widget = QWidget()
        layout = QVBoxLayout()
        
        # فرم مشخصات
        form_layout = QFormLayout()
        
        # بخش اطلاعات پایه
        base_group = QGroupBox("اطلاعات پایه")
        base_layout = QFormLayout()
        
        self.deal_type_combo = QComboBox()
        self.deal_type_combo.addItems(["فروش", "اجاره"])
        base_layout.addRow("نوع معامله:", self.deal_type_combo)
        
        self.property_type_combo = QComboBox()
        self.property_type_combo.addItems(self.PROPERTY_TYPES)
        base_layout.addRow("نوع ملک تجاری:", self.property_type_combo)
        
        self.district_edit = QLineEdit()
        base_layout.addRow("منطقه:", self.district_edit)
        
        self.address_edit = QLineEdit()
        base_layout.addRow("آدرس:", self.address_edit)
        
        self.area_spin = QSpinBox()
        self.area_spin.setRange(10, 10000)
        self.area_spin.setSuffix(" متر مربع")
        base_layout.addRow("متراژ:", self.area_spin)
        
        self.age_spin = QSpinBox()
        self.age_spin.setRange(0, 100)
        self.age_spin.setSuffix(" سال")
        base_layout.addRow("سن بنا:", self.age_spin)
        
        base_group.setLayout(base_layout)
        layout.addWidget(base_group)
        
        # بخش قیمت‌گذاری
        price_group = QGroupBox("قیمت‌گذاری")
        price_layout = QFormLayout()
        
        self.price_spin = QDoubleSpinBox()
        self.price_spin.setRange(0, 1000000000000)
        self.price_spin.setSuffix(" تومان")
        self.price_spin.setDecimals(0)
        price_layout.addRow("قیمت فروش/رهن:", self.price_spin)
        
        self.rent_spin = QDoubleSpinBox()
        self.rent_spin.setRange(0, 1000000000)
        self.rent_spin.setSuffix(" تومان")
        self.rent_spin.setDecimals(0)
        self.rent_spin.setEnabled(False)
        price_layout.addRow("اجاره ماهیانه:", self.rent_spin)
        
        price_group.setLayout(price_layout)
        layout.addWidget(price_group)
        
        # بخش ویژگی‌ها
        features_group = QGroupBox("ویژگی‌ها")
        features_layout = QVBoxLayout()
        
        # ردیف اول ویژگی‌ها
        features_row1 = QHBoxLayout()
        self.has_parking = QCheckBox("پارکینگ")
        self.is_active_business = QCheckBox("کسب و کار فعال")
        self.has_elevator = QCheckBox("آسانسور")
        
        features_row1.addWidget(self.has_parking)
        features_row1.addWidget(self.is_active_business)
        features_row1.addWidget(self.has_elevator)
        features_layout.addLayout(features_row1)
        
        # ردیف دوم ویژگی‌ها
        features_row2 = QHBoxLayout()
        self.has_warehouse = QCheckBox("انباری")
        self.is_owner = QCheckBox("سرقفلی")
        
        features_row2.addWidget(self.has_warehouse)
        features_row2.addWidget(self.is_owner)
        features_row2.addStretch()
        features_layout.addLayout(features_row2)
        
        features_group.setLayout(features_layout)
        layout.addWidget(features_group)
        
        # بخش توضیحات
        desc_group = QGroupBox("توضیحات")
        desc_layout = QVBoxLayout()
        
        self.description_edit = QLineEdit()
        self.description_edit.setPlaceholderText("توضیحات اضافی در مورد ملک...")
        desc_layout.addWidget(self.description_edit)
        
        desc_group.setLayout(desc_layout)
        layout.addWidget(desc_group)
        
        # بخش اطلاعات تماس
        contact_group = QGroupBox("اطلاعات تماس")
        contact_layout = QFormLayout()
        
        self.owner_name_edit = QLineEdit()
        contact_layout.addRow("نام مالک:", self.owner_name_edit)
        
        self.phone_edit = QLineEdit()
        contact_layout.addRow("شماره تماس:", self.phone_edit)
        
        self.email_edit = QLineEdit()
        contact_layout.addRow("ایمیل:", self.email_edit)
        
        contact_group.setLayout(contact_layout)
        layout.addWidget(contact_group)
        
        # دکمه‌های عملیات
        buttons_layout = QHBoxLayout()
        
        self.register_btn = QPushButton("ثبت ملک")
        self.register_btn.clicked.connect(self.register_property)
        
        self.clear_btn = QPushButton("پاک کردن")
        self.clear_btn.clicked.connect(self.clear_form)
        
        buttons_layout.addWidget(self.register_btn)
        buttons_layout.addWidget(self.clear_btn)
        
        layout.addLayout(buttons_layout)
        
        # اتصال سیگنال‌ها
        self.deal_type_combo.currentIndexChanged.connect(self.on_deal_type_changed)
        
        register_widget.setLayout(layout)
        return register_widget
    
    def create_search_tab(self):
        """ایجاد تب جستجوی املاک تجاری"""
        search_widget = QWidget()
        layout = QVBoxLayout()
        
        # بخش فیلترهای جستجو
        filter_group = QGroupBox("فیلترهای جستجو")
        filter_layout = QVBoxLayout()
        
        filter_form = QFormLayout()
        
        self.search_deal_type = QComboBox()
        self.search_deal_type.addItems(["همه", "فروش", "اجاره"])
        filter_form.addRow("نوع معامله:", self.search_deal_type)
        
        self.search_property_type = QComboBox()
        self.search_property_type.addItems(["همه"] + self.PROPERTY_TYPES)
        filter_form.addRow("نوع ملک تجاری:", self.search_property_type)
        
        self.search_district = QLineEdit()
        filter_form.addRow("منطقه:", self.search_district)
        
        # محدوده متراژ
        area_layout = QHBoxLayout()
        self.min_area = QSpinBox()
        self.min_area.setRange(0, 10000)
        self.min_area.setSuffix(" متر مربع")
        
        self.max_area = QSpinBox()
        self.max_area.setRange(0, 10000)
        self.max_area.setSuffix(" متر مربع")
        self.max_area.setValue(500)
        
        area_layout.addWidget(QLabel("از"))
        area_layout.addWidget(self.min_area)
        area_layout.addWidget(QLabel("تا"))
        area_layout.addWidget(self.max_area)
        
        filter_form.addRow("متراژ:", area_layout)
        
        # محدوده قیمت
        price_layout = QHBoxLayout()
        self.min_price = QDoubleSpinBox()
        self.min_price.setRange(0, 1000000000000)
        self.min_price.setSuffix(" تومان")
        self.min_price.setDecimals(0)
        
        self.max_price = QDoubleSpinBox()
        self.max_price.setRange(0, 1000000000000)
        self.max_price.setValue(10000000000)
        self.max_price.setSuffix(" تومان")
        self.max_price.setDecimals(0)
        
        price_layout.addWidget(QLabel("از"))
        price_layout.addWidget(self.min_price)
        price_layout.addWidget(QLabel("تا"))
        price_layout.addWidget(self.max_price)
        
        filter_form.addRow("قیمت:", price_layout)
        
        filter_layout.addLayout(filter_form)
        
        # دکمه‌های جستجو
        search_buttons = QHBoxLayout()
        
        self.search_btn = QPushButton("جستجو")
        self.search_btn.clicked.connect(self.search_properties)
        
        self.reset_search_btn = QPushButton("پاک کردن")
        self.reset_search_btn.clicked.connect(self.reset_search)
        
        search_buttons.addWidget(self.search_btn)
        search_buttons.addWidget(self.reset_search_btn)
        
        filter_layout.addLayout(search_buttons)
        filter_group.setLayout(filter_layout)
        
        layout.addWidget(filter_group)
        
        # جدول نتایج
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(8)
        self.results_table.setHorizontalHeaderLabels([
            "شناسه", "نوع", "منطقه", "متراژ", "سن بنا", 
            "قیمت", "اجاره", "آدرس"
        ])
        self.results_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        layout.addWidget(self.results_table)
        
        search_widget.setLayout(layout)
        return search_widget
    
    def on_deal_type_changed(self, index):
        """تغییر وضعیت فیلدها بر اساس نوع معامله"""
        is_rent = (index == 1)  # آیا اجاره انتخاب شده است
        self.rent_spin.setEnabled(is_rent)
        
        # تغییر برچسب قیمت بر اساس نوع معامله
        if is_rent:
            self.price_spin.setSuffix(" تومان (ودیعه)")
        else:
            self.price_spin.setSuffix(" تومان")
    
    def register_property(self):
        """ثبت ملک تجاری جدید"""
        # اعتبارسنجی ورودی‌ها
        if not self.validate_inputs():
            return
        
        try:
            # جمع‌آوری اطلاعات فرم
            deal_type = "sale" if self.deal_type_combo.currentIndex() == 0 else "rent"
            property_type = self.property_type_combo.currentText()
            district = self.district_edit.text()
            address = self.address_edit.text()
            area = self.area_spin.value()
            age = self.age_spin.value()
            price = int(self.price_spin.value())
            rent = int(self.rent_spin.value()) if deal_type == "rent" else 0
            
            # ویژگی‌ها
            has_parking = 1 if self.has_parking.isChecked() else 0
            is_active_business = 1 if self.is_active_business.isChecked() else 0
            has_elevator = 1 if self.has_elevator.isChecked() else 0
            has_warehouse = 1 if self.has_warehouse.isChecked() else 0
            is_owner = 1 if self.is_owner.isChecked() else 0
            
            # توضیحات
            description = self.description_edit.text()
            
            # اطلاعات تماس
            owner_name = self.owner_name_edit.text()
            phone = self.phone_edit.text()
            email = self.email_edit.text()
            
            # نام کاربری فعلی
            username = self.current_user if self.current_user else "admin"
            
            # فراخوانی تابع ثبت ملک از پل ارتباطی
            if deal_type == "sale":
                result = self.commercial_bridge.register_sale(
                    username, property_type, district, address, area, 
                    age, price, has_parking, is_active_business, 
                    has_elevator, has_warehouse, is_owner, 
                    description, owner_name, phone, email
                )
            else:
                result = self.commercial_bridge.register_rental(
                    username, property_type, district, address, area, 
                    age, price, rent, has_parking, is_active_business, 
                    has_elevator, has_warehouse, is_owner, 
                    description, owner_name, phone, email
                )
            
            if result > 0:
                QMessageBox.information(self, "موفقیت", "ملک تجاری با موفقیت ثبت شد.")
                self.clear_form()
                # ارسال سیگنال به‌روزرسانی
                self.property_updated.emit()
            else:
                QMessageBox.warning(self, "خطا", "خطا در ثبت ملک. کد خطا: " + str(result))
                
        except Exception as e:
            logger.error(f"خطا در ثبت ملک تجاری: {str(e)}")
            QMessageBox.critical(self, "خطای سیستمی", f"خطای غیرمنتظره: {str(e)}")
    
    def validate_inputs(self):
        """اعتبارسنجی ورودی‌های فرم"""
        # بررسی منطقه
        if not self.district_edit.text().strip():
            QMessageBox.warning(self, "خطای اعتبارسنجی", "لطفاً منطقه را وارد کنید.")
            return False
            
        # بررسی آدرس
        if not self.address_edit.text().strip():
            QMessageBox.warning(self, "خطای اعتبارسنجی", "لطفاً آدرس را وارد کنید.")
            return False
        
        # بررسی نام مالک
        if not self.owner_name_edit.text().strip():
            QMessageBox.warning(self, "خطای اعتبارسنجی", "لطفاً نام مالک را وارد کنید.")
            return False
        
        # بررسی شماره تماس
        phone = self.phone_edit.text().strip()
        if not phone or not validate_phone(phone):
            QMessageBox.warning(self, "خطای اعتبارسنجی", "لطفاً شماره تماس معتبر وارد کنید.")
            return False
        
        # بررسی ایمیل (اگر وارد شده باشد)
        email = self.email_edit.text().strip()
        if email and not validate_email(email):
            QMessageBox.warning(self, "خطای اعتبارسنجی", "لطفاً ایمیل معتبر وارد کنید.")
            return False
        
        # بررسی قیمت اجاره (برای اجاره)
        if self.deal_type_combo.currentIndex() == 1 and self.rent_spin.value() <= 0:
            QMessageBox.warning(self, "خطای اعتبارسنجی", "لطفاً مبلغ اجاره ماهیانه را وارد کنید.")
            return False
            
        return True
    
    def clear_form(self):
        """پاک کردن فرم ثبت ملک"""
        self.district_edit.clear()
        self.address_edit.clear()
        self.area_spin.setValue(100)
        self.age_spin.setValue(0)
        self.price_spin.setValue(0)
        self.rent_spin.setValue(0)
        self.has_parking.setChecked(False)
        self.is_active_business.setChecked(False)
        self.has_elevator.setChecked(False)
        self.has_warehouse.setChecked(False)
        self.is_owner.setChecked(False)
        self.description_edit.clear()
        self.owner_name_edit.clear()
        self.phone_edit.clear()
        self.email_edit.clear()
    
    def search_properties(self):
        """جستجوی املاک تجاری"""
        try:
            # تعیین نوع معامله
            deal_type_index = self.search_deal_type.currentIndex()
            deal_type = None
            if deal_type_index == 1:  # فروش
                deal_type = "sale"
            elif deal_type_index == 2:  # اجاره
                deal_type = "rent"
            
            # پاک کردن جدول قبل از جستجوی جدید
            self.results_table.setRowCount(0)
            
            # اگر نوع ملک انتخاب شده، جستجو بر اساس نوع
            if self.search_property_type.currentIndex() > 0:
                property_type = self.search_property_type.currentText()
                self.search_by_type(property_type, deal_type)
            
            # اگر منطقه وارد شده، جستجو بر اساس منطقه
            elif self.search_district.text().strip():
                district = self.search_district.text().strip()
                self.search_by_district(district, deal_type)
            
            # اگر محدوده متراژ تعیین شده، جستجو بر اساس متراژ
            elif self.min_area.value() > 0 or self.max_area.value() < 10000:
                min_area = self.min_area.value()
                max_area = self.max_area.value()
                self.search_by_area(min_area, max_area, deal_type)
            
            # اگر محدوده قیمت تعیین شده، جستجو بر اساس قیمت
            elif self.min_price.value() > 0 or self.max_price.value() < 1000000000000:
                min_price = int(self.min_price.value())
                max_price = int(self.max_price.value())
                self.search_by_price(min_price, max_price, deal_type)
            
            # جستجوی همه املاک
            else:
                self.search_all_properties(deal_type)
                
        except Exception as e:
            logger.error(f"خطا در جستجوی املاک تجاری: {str(e)}")
            QMessageBox.critical(self, "خطای سیستمی", f"خطای غیرمنتظره: {str(e)}")
    
    def search_by_district(self, district, deal_type):
        """جستجو بر اساس منطقه"""
        try:
            if deal_type is None or deal_type == "sale":
                count = 0
                properties = self.commercial_bridge.find_by_district(district, "sale", count)
                if properties:
                    self.populate_results_table(properties, count)
                    
            if deal_type is None or deal_type == "rent":
                count = 0
                properties = self.commercial_bridge.find_by_district(district, "rent", count)
                if properties:
                    self.populate_results_table(properties, count)
        except Exception as e:
            logger.error(f"خطا در جستجوی املاک تجاری بر اساس منطقه: {str(e)}")
            raise
    
    def search_by_area(self, min_area, max_area, deal_type):
        """جستجو بر اساس متراژ"""
        try:
            if deal_type is None or deal_type == "sale":
                count = 0
                properties = self.commercial_bridge.find_by_area(min_area, max_area, "sale", count)
                if properties:
                    self.populate_results_table(properties, count)
                    
            if deal_type is None or deal_type == "rent":
                count = 0
                properties = self.commercial_bridge.find_by_area(min_area, max_area, "rent", count)
                if properties:
                    self.populate_results_table(properties, count)
        except Exception as e:
            logger.error(f"خطا در جستجوی املاک تجاری بر اساس متراژ: {str(e)}")
            raise
    
    def search_by_price(self, min_price, max_price, deal_type):
        """جستجو بر اساس قیمت"""
        try:
            if deal_type is None or deal_type == "sale":
                count = 0
                properties = self.commercial_bridge.find_by_price(min_price, max_price, "sale", count)
                if properties:
                    self.populate_results_table(properties, count)
                    
            if deal_type is None or deal_type == "rent":
                count = 0
                properties = self.commercial_bridge.find_by_price(min_price, max_price, "rent", count)
                if properties:
                    self.populate_results_table(properties, count)
        except Exception as e:
            logger.error(f"خطا در جستجوی املاک تجاری بر اساس قیمت: {str(e)}")
            raise
    
    def search_by_type(self, property_type, deal_type):
        """جستجو بر اساس نوع ملک"""
        try:
            if deal_type is None or deal_type == "sale":
                count = 0
                properties = self.commercial_bridge.find_by_type(property_type, "sale", count)
                if properties:
                    self.populate_results_table(properties, count)
                    
            if deal_type is None or deal_type == "rent":
                count = 0
                properties = self.commercial_bridge.find_by_type(property_type, "rent", count)
                if properties:
                    self.populate_results_table(properties, count)
        except Exception as e:
            logger.error(f"خطا در جستجوی املاک تجاری بر اساس نوع: {str(e)}")
            raise
    
    def search_all_properties(self, deal_type):
        """جستجوی همه املاک"""
        try:
            if deal_type is None or deal_type == "sale":
                count = 0
                properties = self.commercial_bridge.find_all("sale", count)
                if properties:
                    self.populate_results_table(properties, count)
                    
            if deal_type is None or deal_type == "rent":
                count = 0
                properties = self.commercial_bridge.find_all("rent", count)
                if properties:
                    self.populate_results_table(properties, count)
        except Exception as e:
            logger.error(f"خطا در جستجوی همه املاک تجاری: {str(e)}")
            raise
    
    def populate_results_table(self, properties, count):
        """پر کردن جدول نتایج با املاک یافت شده"""
        if not properties or count == 0:
            return
            
        current_row_count = self.results_table.rowCount()
        self.results_table.setRowCount(current_row_count + count)
        
        for i in range(count):
            prop = properties[i]
            
            # افزودن اطلاعات ملک به جدول
            self.results_table.setItem(current_row_count + i, 0, QTableWidgetItem(str(prop.id)))
            self.results_table.setItem(current_row_count + i, 1, QTableWidgetItem(prop.property_type))
            self.results_table.setItem(current_row_count + i, 2, QTableWidgetItem(prop.district))
            self.results_table.setItem(current_row_count + i, 3, QTableWidgetItem(str(prop.area)))
            self.results_table.setItem(current_row_count + i, 4, QTableWidgetItem(str(prop.age)))
            self.results_table.setItem(current_row_count + i, 5, QTableWidgetItem(str(prop.price)))
            
            # اگر اجاره‌ای است مقدار اجاره را نمایش بده
            rent_value = str(prop.rent) if hasattr(prop, 'rent') and prop.rent > 0 else "-"
            self.results_table.setItem(current_row_count + i, 6, QTableWidgetItem(rent_value))
            
            self.results_table.setItem(current_row_count + i, 7, QTableWidgetItem(prop.address))
    
    def reset_search(self):
        """پاک کردن فیلترهای جستجو"""
        self.search_district.clear()
        self.search_property_type.setCurrentIndex(0)
        self.min_area.setValue(0)
        self.max_area.setValue(500)
        self.min_price.setValue(0)
        self.max_price.setValue(10000000000)
        self.results_table.setRowCount(0) 