#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
این ماژول شامل کلاس Dashboard است که داشبورد اصلی برنامه را مدیریت می‌کند.
این داشبورد اطلاعات آماری و خلاصه‌ای از وضعیت سیستم را نمایش می‌دهد.
"""

import os
import logging
from datetime import datetime, timedelta

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QComboBox, QGroupBox,
    QMessageBox, QScrollArea, QFrame
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QTimer

# تغییر مسیرهای واردسازی
from bridge.residential_bridge import ResidentialBridge
from bridge.commercial_bridge import CommercialBridge
from bridge.land_bridge import LandBridge
from property_management.report_generator import ReportGenerator
from property_management.config import config_manager, ConfigSection
from ui.dashboard_tab import (
    StatCard, PropertyCountChart,
    DistrictDistributionChart, PriceRangeChart
)

# تنظیم لاگر
logger = logging.getLogger(__name__)

class Dashboard(QWidget):
    """
    کلاس اصلی داشبورد برنامه
    
    این کلاس اطلاعات آماری و خلاصه‌ای از وضعیت سیستم را نمایش می‌دهد
    و امکان دسترسی سریع به بخش‌های مختلف برنامه را فراهم می‌کند.
    """
    
    # سیگنال‌های داشبورد
    navigate_to_residential = pyqtSignal()
    navigate_to_commercial = pyqtSignal()
    navigate_to_land = pyqtSignal()
    navigate_to_search = pyqtSignal()
    navigate_to_reports = pyqtSignal()
    
    def __init__(self, username: str, parent=None):
        """
        مقداردهی اولیه داشبورد
        
        پارامترها:
            username: نام کاربری کاربر فعلی
            parent: ویجت والد
        """
        super().__init__(parent)
        self.username = username
        
        try:
            # ایجاد اتصال‌های پل (bridge) با مدیریت خطا
            try:
                self.report_generator = ReportGenerator()
            except Exception as e:
                logger.error(f"خطا در ایجاد ReportGenerator: {e}")
                self.report_generator = None
            
            try:
                self.residential_bridge = ResidentialBridge()
            except Exception as e:
                logger.error(f"خطا در ایجاد ResidentialBridge: {e}")
                self.residential_bridge = None
            
            try:
                self.commercial_bridge = CommercialBridge()
            except Exception as e:
                logger.error(f"خطا در ایجاد CommercialBridge: {e}")
                self.commercial_bridge = None
            
            try:
                self.land_bridge = LandBridge()
            except Exception as e:
                logger.error(f"خطا در ایجاد LandBridge: {e}")
                self.land_bridge = None
        
            # تنظیم دوره‌های زمانی
            self.time_periods = {
                "امروز": (datetime.now().replace(hour=0, minute=0, second=0), datetime.now()),
                "هفته جاری": (datetime.now() - timedelta(days=datetime.now().weekday()), datetime.now()),
                "ماه جاری": (datetime.now().replace(day=1), datetime.now()),
                "سه ماه اخیر": (datetime.now() - timedelta(days=90), datetime.now()),
                "سال جاری": (datetime.now().replace(month=1, day=1), datetime.now()),
                "کل": (datetime(2000, 1, 1), datetime.now())
            }
            
            # دوره زمانی فعلی
            self.current_period = "ماه جاری"
            
            # نوع معامله فعلی
            self.current_deal_type = "sale"  # یا "rent"
            
            # داده‌های آماری
            self.stats_data = {
                "total_properties": 0,
                "total_value": 0,
                "recent_listings": 0,
                "recent_transactions": 0,
                "popular_districts": [],
                "price_trends": [],
                "property_distributions": {}
            }
            
            # راه‌اندازی رابط کاربری
            self.setup_ui()
            
            # به‌روزرسانی اولیه داده‌ها
            self.refresh_dashboard()
            
            # تنظیم تایمر برای به‌روزرسانی خودکار
            self.refresh_timer = QTimer(self)
            self.refresh_timer.timeout.connect(self.refresh_dashboard)
            
            # تعیین فاصله به‌روزرسانی بر اساس تنظیمات
            try:
                refresh_interval = config_manager.get_value(
                    ConfigSection.GENERAL, "dashboard_refresh_interval", 5
                )
                # تبدیل دقیقه به میلی‌ثانیه
                self.refresh_timer.start(refresh_interval * 60 * 1000)
            except Exception as e:
                logger.error(f"خطا در تنظیم تایمر به‌روزرسانی: {e}")
                # مقدار پیش‌فرض 5 دقیقه
                self.refresh_timer.start(5 * 60 * 1000)
        
        except Exception as e:
            logger.error(f"خطا در مقداردهی Dashboard: {e}")
            QMessageBox.warning(self, "خطا", f"خطا در بارگذاری داشبورد: {str(e)}")
    
    def setup_ui(self):
        """راه‌اندازی رابط کاربری داشبورد"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # هدر داشبورد
        header_layout = self.create_header()
        main_layout.addLayout(header_layout)
        
        # محتوای اصلی داشبورد
        content_widget = QScrollArea()
        content_widget.setWidgetResizable(True)
        content_widget.setFrameShape(QFrame.NoFrame)
        
        dashboard_content = QWidget()
        content_layout = QVBoxLayout(dashboard_content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(15)
        
        # بخش کارت‌های آماری
        stats_group = QGroupBox("آمار کلی")
        stats_layout = QGridLayout(stats_group)
        
        # کارت آماری تعداد کل املاک
        self.total_properties_card = StatCard(
            "تعداد کل املاک", "...", 
            icon_path=os.path.join("resources", "icons", "home.png"),
            color="#2196F3"
        )
        stats_layout.addWidget(self.total_properties_card, 0, 0)
        
        # کارت آماری ارزش کل املاک
        self.total_value_card = StatCard(
            "ارزش کل املاک (تومان)", "...", 
            icon_path=os.path.join("resources", "icons", "money.png"),
            color="#4CAF50"
        )
        stats_layout.addWidget(self.total_value_card, 0, 1)
        
        # کارت آماری تعداد املاک جدید
        self.recent_listings_card = StatCard(
            "املاک جدید", "...", 
            icon_path=os.path.join("resources", "icons", "new.png"),
            color="#FF9800"
        )
        stats_layout.addWidget(self.recent_listings_card, 0, 2)
        
        # کارت آماری تعداد معاملات اخیر
        self.recent_transactions_card = StatCard(
            "معاملات اخیر", "...", 
            icon_path=os.path.join("resources", "icons", "transaction.png"),
            color="#E91E63"
        )
        stats_layout.addWidget(self.recent_transactions_card, 0, 3)
        
        content_layout.addWidget(stats_group)
        
        # بخش نمودارها
        charts_layout = QGridLayout()
        charts_layout.setSpacing(10)
        
        try:
            # نمودار توزیع انواع املاک
            self.property_count_chart = PropertyCountChart(self.report_generator)
            charts_layout.addWidget(self.property_count_chart, 0, 0)
            
            # نمودار توزیع املاک بر اساس منطقه
            self.district_distribution_chart = DistrictDistributionChart(self.report_generator)
            charts_layout.addWidget(self.district_distribution_chart, 0, 1)
            
            # نمودار توزیع قیمت
            self.price_range_chart = PriceRangeChart(self.report_generator)
            charts_layout.addWidget(self.price_range_chart, 1, 0, 1, 2)
        except Exception as e:
            logger.error(f"خطا در ایجاد نمودارها: {e}")
            error_label = QLabel(f"خطا در بارگذاری نمودارها: {str(e)}")
            error_label.setStyleSheet("color: red;")
            charts_layout.addWidget(error_label, 0, 0, 2, 2)
        
        content_layout.addLayout(charts_layout)
        
        # بخش دسترسی سریع
        quick_access_group = QGroupBox("دسترسی سریع")
        quick_access_layout = QHBoxLayout(quick_access_group)
        
        # دکمه‌های دسترسی سریع
        self.create_quick_button(
            quick_access_layout, "ثبت ملک مسکونی", 
            "home.png", self.navigate_to_residential.emit
        )
        self.create_quick_button(
            quick_access_layout, "ثبت ملک تجاری", 
            "store.png", self.navigate_to_commercial.emit
        )
        self.create_quick_button(
            quick_access_layout, "ثبت زمین", 
            "land.png", self.navigate_to_land.emit
        )
        self.create_quick_button(
            quick_access_layout, "جستجوی پیشرفته", 
            "search.png", self.navigate_to_search.emit
        )
        self.create_quick_button(
            quick_access_layout, "گزارش‌ها", 
            "report.png", self.navigate_to_reports.emit
        )
        
        content_layout.addWidget(quick_access_group)
        
        content_widget.setWidget(dashboard_content)
        main_layout.addWidget(content_widget)
        
        # نمایش نام کاربر
        user_label = QLabel(f"کاربر: {self.username}")
        user_label.setAlignment(Qt.AlignCenter)
        user_label.setStyleSheet("font-weight: bold; color: #555;")
        main_layout.addWidget(user_label)
    
    def create_header(self):
        """ایجاد هدر داشبورد با فیلترها و دکمه‌های کنترلی"""
        header_layout = QHBoxLayout()
        
        # عنوان داشبورد
        title_label = QLabel("داشبورد مدیریت املاک")
        title_label.setStyleSheet("font-size: 18pt; font-weight: bold; color: #333;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # انتخاب دوره زمانی
        period_layout = QHBoxLayout()
        period_label = QLabel("دوره زمانی:")
        period_layout.addWidget(period_label)
        
        self.period_combo = QComboBox()
        for period in self.time_periods:
            self.period_combo.addItem(period)
        self.period_combo.setCurrentText(self.current_period)
        self.period_combo.currentTextChanged.connect(self.on_period_changed)
        period_layout.addWidget(self.period_combo)
        
        header_layout.addLayout(period_layout)
        
        # انتخاب نوع معامله
        deal_layout = QHBoxLayout()
        deal_label = QLabel("نوع معامله:")
        deal_layout.addWidget(deal_label)
        
        self.deal_combo = QComboBox()
        self.deal_combo.addItem("فروش", "sale")
        self.deal_combo.addItem("اجاره", "rent")
        self.deal_combo.currentIndexChanged.connect(self.on_deal_type_changed)
        deal_layout.addWidget(self.deal_combo)
        
        header_layout.addLayout(deal_layout)
        
        # دکمه بروزرسانی
        refresh_button = QPushButton("بروزرسانی")
        refresh_button.setIcon(QIcon(os.path.join("resources", "icons", "refresh.png")))
        refresh_button.clicked.connect(self.refresh_dashboard)
        header_layout.addWidget(refresh_button)
        
        return header_layout
    
    def create_quick_button(self, layout, text, icon_name, callback):
        """ایجاد دکمه دسترسی سریع"""
        button = QPushButton(text)
        icon_path = os.path.join("resources", "icons", icon_name)
        if os.path.exists(icon_path):
            button.setIcon(QIcon(icon_path))
        
        button.setMinimumWidth(120)
        button.setMinimumHeight(80)
        button.setIconSize(QSize(32, 32))
        button.clicked.connect(callback)
        layout.addWidget(button)
        
        return button
    
    def refresh_dashboard(self):
        """به‌روزرسانی داده‌های داشبورد"""
        try:
            logger.info("به‌روزرسانی داشبورد...")
            
            # دریافت دوره زمانی فعلی
            period_name = self.period_combo.currentText()
            start_date, end_date = self.time_periods[period_name]
            
            # دریافت نوع معامله فعلی
            deal_type = self.deal_combo.currentData()
            
            # به‌روزرسانی آمار کلی
            self.update_general_stats(start_date, end_date, deal_type)
            
            # به‌روزرسانی نمودارها
            if hasattr(self, 'property_count_chart'):
                self.property_count_chart.update_chart(deal_type)
            
            if hasattr(self, 'district_distribution_chart'):
                self.district_distribution_chart.update_chart(deal_type)
            
            if hasattr(self, 'price_range_chart'):
                self.price_range_chart.update_chart(deal_type)
            
            logger.info("به‌روزرسانی داشبورد با موفقیت انجام شد")
        
        except Exception as e:
            logger.error(f"خطا در به‌روزرسانی داشبورد: {e}")
            QMessageBox.warning(self, "خطا", f"خطا در به‌روزرسانی داشبورد: {str(e)}")
    
    def update_general_stats(self, start_date, end_date, deal_type):
        """به‌روزرسانی آمار کلی داشبورد"""
        try:
            # دریافت املاک از bridge ها
            residential_properties = []
            commercial_properties = []
            land_properties = []
            
            if hasattr(self, 'residential_bridge') and self.residential_bridge:
                try:
                    residential_properties = self.residential_bridge.get_properties(deal_type=deal_type)
                except Exception as e:
                    logger.error(f"خطا در دریافت املاک مسکونی: {e}")
            
            if hasattr(self, 'commercial_bridge') and self.commercial_bridge:
                try:
                    commercial_properties = self.commercial_bridge.get_properties(deal_type=deal_type)
                except Exception as e:
                    logger.error(f"خطا در دریافت املاک تجاری: {e}")
            
            if hasattr(self, 'land_bridge') and self.land_bridge:
                try:
                    land_properties = self.land_bridge.get_properties(deal_type=deal_type)
                except Exception as e:
                    logger.error(f"خطا در دریافت زمین‌ها: {e}")
            
            # محاسبه آمار
            total_properties = len(residential_properties) + len(commercial_properties) + len(land_properties)
            
            # محاسبه ارزش کل املاک (فقط برای فروش)
            total_value = 0
            if deal_type == "sale":
                for prop in residential_properties + commercial_properties + land_properties:
                    if "price" in prop and prop["price"]:
                        total_value += prop["price"]
            
            # تعداد املاک جدید در دوره زمانی
            recent_listings = (
                self.count_recent_properties(residential_properties, start_date) +
                self.count_recent_properties(commercial_properties, start_date) +
                self.count_recent_properties(land_properties, start_date)
            )
            
            # تعداد معاملات در دوره زمانی (نمونه)
            recent_transactions = recent_listings // 3  # مقدار نمونه
            
            # به‌روزرسانی کارت‌های آماری
            self.total_properties_card.set_value(str(total_properties))
            
            # فرمت کردن ارزش کل
            formatted_value = f"{total_value:,}"
            self.total_value_card.set_value(formatted_value)
            
            self.recent_listings_card.set_value(str(recent_listings))
            self.recent_transactions_card.set_value(str(recent_transactions))
            
            # ذخیره آمار برای استفاده بعدی
            self.stats_data["total_properties"] = total_properties
            self.stats_data["total_value"] = total_value
            self.stats_data["recent_listings"] = recent_listings
            self.stats_data["recent_transactions"] = recent_transactions
        
        except Exception as e:
            logger.error(f"خطا در به‌روزرسانی آمار کلی: {e}")
            raise
    
    def count_recent_properties(self, properties_list, start_date):
        """شمارش تعداد املاک ثبت شده بعد از تاریخ مشخص"""
        count = 0
        for prop in properties_list:
            if "creation_date" in prop and prop["creation_date"]:
                try:
                    # تبدیل رشته تاریخ به شیء تاریخ
                    if isinstance(prop["creation_date"], str):
                        creation_date = datetime.strptime(prop["creation_date"], "%Y-%m-%d")
                    else:
                        creation_date = prop["creation_date"]
                    
                    if creation_date >= start_date:
                        count += 1
                except Exception as e:
                    logger.error(f"خطا در تبدیل تاریخ: {e}")
        
        return count
    
    def on_period_changed(self, period):
        """رویداد تغییر دوره زمانی"""
        self.current_period = period
        logger.info(f"دوره زمانی تغییر کرد به: {period}")
        self.refresh_dashboard()
    
    def on_deal_type_changed(self, index):
        """رویداد تغییر نوع معامله"""
        deal_type = self.deal_combo.currentData()
        logger.info(f"نوع معامله تغییر کرد به: {deal_type}")
        self.current_deal_type = deal_type
        self.refresh_dashboard()
        
    def set_username(self, username):
        """تنظیم نام کاربری جدید"""
        self.username = username
        # به‌روزرسانی UI برای نمایش نام کاربری جدید
        for i in range(self.layout().count()):
            item = self.layout().itemAt(i)
            if isinstance(item.widget(), QLabel) and item.widget().text().startswith("کاربر:"):
                item.widget().setText(f"کاربر: {username}")
                break 