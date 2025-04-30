"""
ماژول پنل زمین - بخشی از سیستم مدیریت املاک

این ماژول پنل‌های مربوط به نمایش، ثبت و جستجوی زمین‌ها را پیاده‌سازی می‌کند.
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

from property_management.bridge.land_bridge import LandBridge
from property_management.utils.validation import validate_email, validate_phone

# تنظیم لاگر
logger = logging.getLogger(__name__)

class LandPropertyPanel(QWidget):
    """پنل اصلی مدیریت زمین"""
    
    property_updated = pyqtSignal()  # سیگنال برای اطلاع‌رسانی به‌روزرسانی املاک
    
    # انواع کاربری زمین
    LAND_TYPES = [
        "مسکونی",
        "تجاری",
        "صنعتی",
        "کشاورزی",
        "باغ",
        "سایر"
    ]
    
    def __init__(self, parent=None, current_user=None):
        super().__init__(parent)
        self.current_user = current_user
        self.land_bridge = LandBridge()
        self.initUI()
        
    def initUI(self):
        """راه‌اندازی واسط کاربری"""
        main_layout = QVBoxLayout()
        
        # تب‌های اصلی
        tab_widget = QTabWidget()
        tab_widget.addTab(self.create_register_tab(), "ثبت زمین")
        tab_widget.addTab(self.create_search_tab(), "جستجوی زمین")
        
        main_layout.addWidget(tab_widget)
        self.setLayout(main_layout)
        
    def create_register_tab(self):
        """ایجاد تب ثبت زمین"""
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
        
        self.land_type_combo = QComboBox()
        self.land_type_combo.addItems(self.LAND_TYPES)
        base_layout.addRow("نوع کاربری:", self.land_type_combo)
        
        self.district_edit = QLineEdit()
        base_layout.addRow("منطقه:", self.district_edit)
        
        self.address_edit = QLineEdit()
        base_layout.addRow("آدرس:", self.address_edit)
        
        self.area_spin = QSpinBox()
        self.area_spin.setRange(100, 1000000)
        self.area_spin.setSuffix(" متر مربع")
        base_layout.addRow("متراژ:", self.area_spin)
        
        base_group.setLayout(base_layout)
        layout.addWidget(base_group)
        
        # بخش قیمت‌گذاری
        price_group = QGroupBox("قیمت‌گذاری")
        price_layout = QFormLayout()
        
        self.price_spin = QDoubleSpinBox()
        self.price_spin.setRange(0, 1000000000000)
        self.price_spin.setSuffix(" تومان")
        self.price_spin.setDecimals(0)
        price_layout.addRow("قیمت کل:", self.price_spin)
        
        self.price_per_meter_spin = QDoubleSpinBox()
        self.price_per_meter_spin.setRange(0, 1000000000)
        self.price_per_meter_spin.setSuffix(" تومان")
        self.price_per_meter_spin.setDecimals(0)
        price_layout.addRow("قیمت هر متر مربع:", self.price_per_meter_spin)
        
        self.rent_spin = QDoubleSpinBox()
        self.rent_spin.setRange(0, 1000000000)
        self.rent_spin.setSuffix(" تومان")
        self.rent_spin.setDecimals(0)
        self.rent_spin.setEnabled(False)
        price_layout.addRow("اجاره ماهیانه:", self.rent_spin)
        
        # اتصال سیگنال برای محاسبه خودکار قیمت
        self.area_spin.valueChanged.connect(self.calculate_total_price)
        self.price_per_meter_spin.valueChanged.connect(self.calculate_total_price)
        self.price_spin.valueChanged.connect(self.calculate_per_meter_price)
        
        price_group.setLayout(price_layout)
        layout.addWidget(price_group)
        
        # بخش ویژگی‌ها
        features_group = QGroupBox("ویژگی‌ها")
        features_layout = QVBoxLayout()
        
        # ردیف اول ویژگی‌ها
        features_row1 = QHBoxLayout()
        self.has_permit = QCheckBox("دارای مجوز ساخت")
        self.has_deed = QCheckBox("دارای سند تک برگی")
        
        features_row1.addWidget(self.has_permit)
        features_row1.addWidget(self.has_deed)
        features_row1.addStretch()
        features_layout.addLayout(features_row1)
        
        features_group.setLayout(features_layout)
        layout.addWidget(features_group)
        
        # بخش توضیحات
        desc_group = QGroupBox("توضیحات")
        desc_layout = QVBoxLayout()
        
        self.description_edit = QLineEdit()
        self.description_edit.setPlaceholderText("توضیحات اضافی در مورد زمین...")
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
        
        self.register_btn = QPushButton("ثبت زمین")
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
        """ایجاد تب جستجوی زمین"""
        search_widget = QWidget()
        layout = QVBoxLayout()
        
        # بخش فیلترهای جستجو
        filter_group = QGroupBox("فیلترهای جستجو")
        filter_layout = QVBoxLayout()
        
        filter_form = QFormLayout()
        
        self.search_deal_type = QComboBox()
        self.search_deal_type.addItems(["همه", "فروش", "اجاره"])
        filter_form.addRow("نوع معامله:", self.search_deal_type)
        
        self.search_land_type = QComboBox()
        self.search_land_type.addItems(["همه"] + self.LAND_TYPES)
        filter_form.addRow("نوع کاربری:", self.search_land_type)
        
        self.search_district = QLineEdit()
        filter_form.addRow("منطقه:", self.search_district)
        
        # محدوده متراژ
        area_layout = QHBoxLayout()
        self.min_area = QSpinBox()
        self.min_area.setRange(0, 1000000)
        self.min_area.setSuffix(" متر مربع")
        
        self.max_area = QSpinBox()
        self.max_area.setRange(0, 1000000)
        self.max_area.setSuffix(" متر مربع")
        self.max_area.setValue(10000)
        
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
        self.max_price.setValue(100000000000)
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
            "شناسه", "نوع کاربری", "منطقه", "متراژ", 
            "قیمت کل", "قیمت هر متر", "آدرس", "تماس"
        ])
        self.results_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        layout.addWidget(self.results_table)
        
        search_widget.setLayout(layout)
        return search_widget
    
    def on_deal_type_changed(self, index):
        """تغییر وضعیت فیلدها بر اساس نوع معامله"""
        is_rent = (index == 1)  # آیا اجاره انتخاب شده است
        self.rent_spin.setEnabled(is_rent)
    
    def calculate_total_price(self):
        """محاسبه قیمت کل بر اساس متراژ و قیمت هر متر"""
        area = self.area_spin.value()
        price_per_meter = self.price_per_meter_spin.value()
        
        # جلوگیری از بازگشت بازگشتی
        self.price_spin.blockSignals(True)
        self.price_spin.setValue(area * price_per_meter)
        self.price_spin.blockSignals(False)
    
    def calculate_per_meter_price(self):
        """محاسبه قیمت هر متر بر اساس قیمت کل و متراژ"""
        area = self.area_spin.value()
        total_price = self.price_spin.value()
        
        if area > 0:
            # جلوگیری از بازگشت بازگشتی
            self.price_per_meter_spin.blockSignals(True)
            self.price_per_meter_spin.setValue(total_price / area)
            self.price_per_meter_spin.blockSignals(False)
    
    def register_property(self):
        """ثبت زمین جدید"""
        # اعتبارسنجی ورودی‌ها
        if not self.validate_inputs():
            return
        
        try:
            # جمع‌آوری اطلاعات فرم
            deal_type = "sale" if self.deal_type_combo.currentIndex() == 0 else "rent"
            land_type = self.land_type_combo.currentText()
            district = self.district_edit.text()
            address = self.address_edit.text()
            area = self.area_spin.value()
            price = int(self.price_spin.value())
            rent = int(self.rent_spin.value()) if deal_type == "rent" else 0
            
            # ویژگی‌ها
            has_permit = 1 if self.has_permit.isChecked() else 0
            has_deed = 1 if self.has_deed.isChecked() else 0
            
            # توضیحات
            description = self.description_edit.text()
            
            # اطلاعات تماس
            owner_name = self.owner_name_edit.text()
            phone = self.phone_edit.text()
            email = self.email_edit.text()
            
            # نام کاربری فعلی
            username = self.current_user if self.current_user else "admin"
            
            # فراخوانی تابع ثبت زمین از پل ارتباطی
            if deal_type == "sale":
                result = self.land_bridge.register_sale(
                    username, land_type, district, address, area, 
                    price, has_permit, has_deed, 
                    description, owner_name, phone, email
                )
            else:
                result = self.land_bridge.register_rental(
                    username, land_type, district, address, area, 
                    price, rent, has_permit, has_deed, 
                    description, owner_name, phone, email
                )
            
            if result > 0:
                QMessageBox.information(self, "موفقیت", "زمین با موفقیت ثبت شد.")
                self.clear_form()
                # ارسال سیگنال به‌روزرسانی
                self.property_updated.emit()
            else:
                QMessageBox.warning(self, "خطا", "خطا در ثبت زمین. کد خطا: " + str(result))
                
        except Exception as e:
            logger.error(f"خطا در ثبت زمین: {str(e)}")
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
        """پاک کردن فرم ثبت زمین"""
        self.district_edit.clear()
        self.address_edit.clear()
        self.area_spin.setValue(1000)
        self.price_spin.setValue(0)
        self.price_per_meter_spin.setValue(0)
        self.rent_spin.setValue(0)
        self.has_permit.setChecked(False)
        self.has_deed.setChecked(False)
        self.description_edit.clear()
        self.owner_name_edit.clear()
        self.phone_edit.clear()
        self.email_edit.clear()
    
    def search_properties(self):
        """جستجوی زمین‌ها"""
        try:
            # پاک کردن جدول قبل از جستجوی جدید
            self.results_table.setRowCount(0)
            
            # تعیین نوع معامله
            deal_type_index = self.search_deal_type.currentIndex()
            deal_type = None
            if deal_type_index == 1:  # فروش
                deal_type = "sale"
            elif deal_type_index == 2:  # اجاره
                deal_type = "rent"
            
            # اگر نوع زمین انتخاب شده، جستجو بر اساس نوع
            if self.search_land_type.currentIndex() > 0:
                land_type = self.search_land_type.currentText()
                self.search_by_type(land_type, deal_type)
            
            # اگر منطقه وارد شده، جستجو بر اساس منطقه
            elif self.search_district.text().strip():
                district = self.search_district.text().strip()
                self.search_by_district(district, deal_type)
            
            # اگر محدوده متراژ تعیین شده، جستجو بر اساس متراژ
            elif self.min_area.value() > 0 or self.max_area.value() < 1000000:
                min_area = self.min_area.value()
                max_area = self.max_area.value()
                self.search_by_area(min_area, max_area, deal_type)
            
            # اگر محدوده قیمت تعیین شده، جستجو بر اساس قیمت
            elif self.min_price.value() > 0 or self.max_price.value() < 1000000000000:
                min_price = int(self.min_price.value())
                max_price = int(self.max_price.value())
                self.search_by_price(min_price, max_price, deal_type)
            
            # جستجوی همه زمین‌ها
            else:
                self.search_all_properties(deal_type)
                
        except Exception as e:
            logger.error(f"خطا در جستجوی زمین‌ها: {str(e)}")
            QMessageBox.critical(self, "خطای سیستمی", f"خطای غیرمنتظره: {str(e)}")
    
    def search_by_district(self, district, deal_type):
        """جستجو بر اساس منطقه"""
        try:
            if deal_type is None or deal_type == "sale":
                count = 0
                properties = self.land_bridge.find_by_district(district, "sale", count)
                if properties:
                    self.populate_results_table(properties, count)
                    
            if deal_type is None or deal_type == "rent":
                count = 0
                properties = self.land_bridge.find_by_district(district, "rent", count)
                if properties:
                    self.populate_results_table(properties, count)
        except Exception as e:
            logger.error(f"خطا در جستجوی زمین بر اساس منطقه: {str(e)}")
            raise
    
    def search_by_area(self, min_area, max_area, deal_type):
        """جستجو بر اساس متراژ"""
        try:
            if deal_type is None or deal_type == "sale":
                count = 0
                properties = self.land_bridge.find_by_area(min_area, max_area, "sale", count)
                if properties:
                    self.populate_results_table(properties, count)
                    
            if deal_type is None or deal_type == "rent":
                count = 0
                properties = self.land_bridge.find_by_area(min_area, max_area, "rent", count)
                if properties:
                    self.populate_results_table(properties, count)
        except Exception as e:
            logger.error(f"خطا در جستجوی زمین بر اساس متراژ: {str(e)}")
            raise
    
    def search_by_price(self, min_price, max_price, deal_type):
        """جستجو بر اساس قیمت"""
        try:
            if deal_type is None or deal_type == "sale":
                count = 0
                properties = self.land_bridge.find_by_price(min_price, max_price, "sale", count)
                if properties:
                    self.populate_results_table(properties, count)
                    
            if deal_type is None or deal_type == "rent":
                count = 0
                properties = self.land_bridge.find_by_price(min_price, max_price, "rent", count)
                if properties:
                    self.populate_results_table(properties, count)
        except Exception as e:
            logger.error(f"خطا در جستجوی زمین بر اساس قیمت: {str(e)}")
            raise
    
    def search_by_type(self, land_type, deal_type):
        """جستجو بر اساس نوع زمین"""
        try:
            if deal_type is None or deal_type == "sale":
                count = 0
                properties = self.land_bridge.find_by_type(land_type, "sale", count)
                if properties:
                    self.populate_results_table(properties, count)
                    
            if deal_type is None or deal_type == "rent":
                count = 0
                properties = self.land_bridge.find_by_type(land_type, "rent", count)
                if properties:
                    self.populate_results_table(properties, count)
        except Exception as e:
            logger.error(f"خطا در جستجوی زمین بر اساس نوع: {str(e)}")
            raise
    
    def search_all_properties(self, deal_type):
        """جستجوی همه زمین‌ها"""
        try:
            if deal_type is None or deal_type == "sale":
                count = 0
                properties = self.land_bridge.find_all("sale", count)
                if properties:
                    self.populate_results_table(properties, count)
                    
            if deal_type is None or deal_type == "rent":
                count = 0
                properties = self.land_bridge.find_all("rent", count)
                if properties:
                    self.populate_results_table(properties, count)
        except Exception as e:
            logger.error(f"خطا در جستجوی همه زمین‌ها: {str(e)}")
            raise
    
    def populate_results_table(self, properties, count):
        """پر کردن جدول نتایج با زمین‌های یافت شده"""
        if not properties or count == 0:
            return
            
        current_row_count = self.results_table.rowCount()
        self.results_table.setRowCount(current_row_count + count)
        
        for i in range(count):
            prop = properties[i]
            
            # محاسبه قیمت هر متر مربع
            price_per_meter = prop.price / prop.area if prop.area > 0 else 0
            
            # افزودن اطلاعات زمین به جدول
            self.results_table.setItem(current_row_count + i, 0, QTableWidgetItem(str(prop.id)))
            self.results_table.setItem(current_row_count + i, 1, QTableWidgetItem(prop.land_type))
            self.results_table.setItem(current_row_count + i, 2, QTableWidgetItem(prop.district))
            self.results_table.setItem(current_row_count + i, 3, QTableWidgetItem(str(prop.area)))
            self.results_table.setItem(current_row_count + i, 4, QTableWidgetItem(str(prop.price)))
            self.results_table.setItem(current_row_count + i, 5, QTableWidgetItem(f"{int(price_per_meter):,}"))
            self.results_table.setItem(current_row_count + i, 6, QTableWidgetItem(prop.address))
            self.results_table.setItem(current_row_count + i, 7, QTableWidgetItem(prop.phone))
    
    def reset_search(self):
        """پاک کردن فیلترهای جستجو"""
        self.search_district.clear()
        self.search_land_type.setCurrentIndex(0)
        self.min_area.setValue(0)
        self.max_area.setValue(10000)
        self.min_price.setValue(0)
        self.max_price.setValue(100000000000)
        self.results_table.setRowCount(0) 