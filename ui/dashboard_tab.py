#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ماژول تب داشبورد برای سیستم مدیریت املاک
این ماژول شامل کلاس DashboardTab برای نمایش خلاصه وضعیت سیستم و آمار مهم است.
"""

import os
import sys
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QComboBox, QGroupBox,
    QRadioButton, QCheckBox, QSpinBox, QDateEdit,
    QTabWidget, QLineEdit, QFormLayout, QFileDialog,
    QMessageBox, QSplitter, QScrollArea, QFrame,
    QButtonGroup, QToolButton, QMenu, QAction,
    QGraphicsView, QGraphicsScene
)
from PyQt5.QtGui import QIcon, QPixmap, QFont, QPainter, QColor, QPen
from PyQt5.QtCore import Qt, QDate, pyqtSignal, pyqtSlot, QSize, QTimer, QRect, QPoint, QMargins

from property_management.report_generator import ReportGenerator
from property_management.charts import BarChart, PieChart, LineChart, create_chart
from bridge.lib_handler import get_lib_instance

# تنظیم گزارش‌گر برای این ماژول
logger = logging.getLogger(__name__)

def resource_path(relative_path):
    """تبدیل مسیر نسبی به مسیر مطلق برای فایل‌های منابع"""
    try:
        # اگر با PyInstaller ساخته شده باشد
        base_path = sys._MEIPASS
    except Exception:
        # در حالت اجرا از سورس
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

class StatCard(QFrame):
    """کارت نمایش آمار"""
    
    def __init__(self, title, value, icon_path=None, color="#4CAF50", parent=None):
        super().__init__(parent)
        self.title = title
        self.value = value
        self.icon_path = icon_path
        self.color = color
        
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.setMinimumHeight(120)
        self.setMinimumWidth(200)
        self.setStyleSheet(f"""
            StatCard {{
                background-color: white;
                border-radius: 8px;
                border-left: 5px solid {color};
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
            }}
        """)
        
        self.setup_ui()
    
    def setup_ui(self):
        """راه‌اندازی رابط کاربری کارت"""
        layout = QHBoxLayout(self)
        
        # آیکون
        if self.icon_path:
            icon_label = QLabel()
            pixmap = QPixmap(self.icon_path)
            icon_label.setPixmap(pixmap.scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            layout.addWidget(icon_label)
        
        # اطلاعات
        info_layout = QVBoxLayout()
        
        title_label = QLabel(self.title)
        title_font = QFont()
        title_font.setPointSize(10)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignLeft)
        info_layout.addWidget(title_label)
        
        value_label = QLabel(str(self.value))
        value_font = QFont()
        value_font.setPointSize(16)
        value_font.setBold(True)
        value_label.setFont(value_font)
        value_label.setAlignment(Qt.AlignLeft)
        info_layout.addWidget(value_label)
        
        layout.addLayout(info_layout)
        layout.addStretch()
    
    def update_value(self, value):
        """به‌روزرسانی مقدار آمار"""
        self.value = value
        for i in range(self.layout().count()):
            item = self.layout().itemAt(i)
            if isinstance(item, QVBoxLayout):
                value_label = item.itemAt(1).widget()
                if isinstance(value_label, QLabel):
                    value_label.setText(str(value))
                break
    
    def set_value(self, value):
        """به‌روزرسانی مقدار آمار (نام جایگزین)"""
        self.update_value(value)


class ChartWidget(QFrame):
    """ویجت نمایش نمودار"""
    
    def __init__(self, chart_title=None, parent=None):
        super().__init__(parent)
        self.title = chart_title or "نمودار"
        self.logger = logging.getLogger(__name__)
        
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.setMinimumHeight(300)
        self.setMinimumWidth(400)
        self.setStyleSheet("""
            ChartWidget {
                background-color: white;
                border-radius: 8px;
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
            }
        """)
        
        # راه‌اندازی رابط کاربری پایه
        self.main_layout = QVBoxLayout(self)
        
        # عنوان
        title_layout = QHBoxLayout()
        
        self.title_label = QLabel(self.title)
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        title_layout.addWidget(self.title_label)
        
        title_layout.addStretch()
        
        # ابزارها
        self.refresh_btn = QToolButton()
        self.refresh_btn.setIcon(QIcon(resource_path("icons/refresh.png")))
        self.refresh_btn.setToolTip("به‌روزرسانی نمودار")
        self.refresh_btn.clicked.connect(self.refresh_chart)
        title_layout.addWidget(self.refresh_btn)
        
        self.main_layout.addLayout(title_layout)
        
        # محتوای نمودار
        self.chart_container = QWidget()
        self.chart_layout = QVBoxLayout(self.chart_container)
        self.chart_layout.setContentsMargins(0, 0, 0, 0)
        
        self.main_layout.addWidget(self.chart_container)
    
    def create_chart_view(self, chart):
        """ایجاد نمای نمودار"""
        self.logger.debug(f"ایجاد نمای نمودار برای {self.title}")
        chart_view = QGraphicsView()
        chart_view.setScene(QGraphicsScene())
        chart_view.setMinimumHeight(250)
        return chart_view
    
    def refresh_chart(self):
        """به‌روزرسانی نمودار - این متد باید در کلاس‌های فرزند بازنویسی شود"""
        self.logger.debug("متد refresh_chart صدا زده شد و باید در کلاس فرزند بازنویسی شود")
        pass


class PropertyCountChart(ChartWidget):
    """نمودار تعداد املاک بر اساس نوع"""
    
    def __init__(self, parent=None):
        super().__init__(chart_title="تعداد املاک بر اساس نوع", parent=parent)
        self.logger = logging.getLogger(__name__)
        self.deal_type = "all"  # پیش‌فرض برای همه انواع معاملات
        self.setup_ui()
    
    def setup_ui(self):
        """راه‌اندازی رابط کاربری نمودار"""
        # افزودن کنترل‌های فیلتر در بالای نمودار
        filter_layout = QHBoxLayout()
        
        # انتخاب نوع معامله
        self.deal_type_combo = QComboBox()
        self.deal_type_combo.addItem("همه معاملات", "all")
        self.deal_type_combo.addItem("فروش", "sale")
        self.deal_type_combo.addItem("اجاره", "rent")
        self.deal_type_combo.currentIndexChanged.connect(self.on_filter_changed)
        
        filter_layout.addWidget(QLabel("نوع معامله:"))
        filter_layout.addWidget(self.deal_type_combo)
        filter_layout.addStretch()
        
        self.chart_layout.insertLayout(0, filter_layout)
        
        # تنظیم نمودار اصلی
        self.chart = PieChart()
        self.chart_view = self.create_chart_view(self.chart)
        self.chart_layout.addWidget(self.chart_view)
        
        # رفرش اولیه نمودار
        self.refresh_chart()
    
    def on_filter_changed(self):
        """وقتی فیلترها تغییر می‌کنند، نمودار به‌روزرسانی شود"""
        self.deal_type = self.deal_type_combo.currentData()
        self.refresh_chart()
    
    def refresh_chart(self):
        """به‌روزرسانی نمودار با داده‌های جدید"""
        try:
            self.logger.debug(f"به‌روزرسانی نمودار تعداد املاک با فیلتر نوع معامله={self.deal_type}")
            
            # ساخت داده‌های نمودار به صورت مصنوعی
            data = {
                'Type': ['مسکونی', 'تجاری', 'زمین'],
                'Count': [0, 0, 0]
            }
            
            # دریافت تعداد املاک از بریج
            lib = get_lib_instance()
            
            # دریافت تعداد املاک مسکونی
            residential_count = getattr(lib, "residential_get_count")(self.deal_type)
            data['Count'][0] = residential_count
            
            # دریافت تعداد املاک تجاری
            commercial_count = getattr(lib, "commercial_get_count")(self.deal_type)
            data['Count'][1] = commercial_count
            
            # دریافت تعداد زمین‌ها
            land_count = getattr(lib, "land_get_count")(self.deal_type)
            data['Count'][2] = land_count
            
            self.logger.debug(f"داده‌های نمودار تعداد املاک: مسکونی={residential_count}, تجاری={commercial_count}, زمین={land_count}")
            
            # ساخت دیتافریم
            import pandas as pd
            df = pd.DataFrame(data)
            
            if not df['Count'].sum() == 0:  # اگر هیچ ملکی موجود نبود
                # تنظیم نمودار
                self.chart.plot(
                    df,
                    x_column="Type",
                    y_column="Count",
                    label_column="Type",
                    show_values=True,
                    show_percent=True
                )
                self.logger.debug("نمودار تعداد املاک با موفقیت به‌روزرسانی شد")
            else:
                self.logger.warning("هیچ ملکی یافت نشد - نمودار به‌روزرسانی نمی‌شود")
        except Exception as e:
            self.logger.error(f"خطا در به‌روزرسانی نمودار تعداد املاک: {str(e)}", exc_info=True)
            QMessageBox.critical(self, "خطا", f"خطا در نمایش نمودار تعداد املاک: {str(e)}")
            
    def update_chart(self, deal_type=None):
        """برای سازگاری با رابط قبلی"""
        if deal_type is not None:
            self.deal_type = deal_type
        self.refresh_chart()


class DistrictDistributionChart(ChartWidget):
    """نمودار توزیع املاک بر اساس منطقه"""
    
    def __init__(self, parent=None):
        super().__init__(chart_title="توزیع املاک بر اساس منطقه", parent=parent)
        self.logger = logging.getLogger(__name__)
        self.property_type = "all"  # پیش‌فرض برای همه انواع ملک
        self.deal_type = "all"  # پیش‌فرض برای همه انواع معاملات
        self.setup_ui()
    
    def setup_ui(self):
        """راه‌اندازی رابط کاربری نمودار"""
        # افزودن کنترل‌های فیلتر در بالای نمودار
        filter_layout = QHBoxLayout()
        
        # انتخاب نوع ملک
        self.property_type_combo = QComboBox()
        self.property_type_combo.addItem("همه انواع ملک", "all")
        self.property_type_combo.addItem("مسکونی", "residential")
        self.property_type_combo.addItem("تجاری", "commercial")
        self.property_type_combo.addItem("زمین", "land")
        self.property_type_combo.currentIndexChanged.connect(self.on_filter_changed)
        
        # انتخاب نوع معامله
        self.deal_type_combo = QComboBox()
        self.deal_type_combo.addItem("همه معاملات", "all")
        self.deal_type_combo.addItem("فروش", "sale")
        self.deal_type_combo.addItem("اجاره", "rent")
        self.deal_type_combo.currentIndexChanged.connect(self.on_filter_changed)
        
        filter_layout.addWidget(QLabel("نوع ملک:"))
        filter_layout.addWidget(self.property_type_combo)
        filter_layout.addWidget(QLabel("نوع معامله:"))
        filter_layout.addWidget(self.deal_type_combo)
        filter_layout.addStretch()
        
        self.chart_layout.insertLayout(0, filter_layout)
        
        # تنظیم نمودار اصلی
        self.chart = PieChart()
        self.chart_view = self.create_chart_view(self.chart)
        self.chart_layout.addWidget(self.chart_view)
        
        # رفرش اولیه نمودار
        self.refresh_chart()
    
    def on_filter_changed(self):
        """وقتی فیلترها تغییر می‌کنند، نمودار به‌روزرسانی شود"""
        self.property_type = self.property_type_combo.currentData()
        self.deal_type = self.deal_type_combo.currentData()
        self.refresh_chart()
    
    def refresh_chart(self):
        """به‌روزرسانی نمودار با داده‌های جدید"""
        try:
            self.logger.debug(f"به‌روزرسانی نمودار توزیع منطقه با فیلترهای: نوع ملک={self.property_type}، نوع معامله={self.deal_type}")
            
            # دریافت داده‌های منطقه از طریق بریج
            lib = get_lib_instance()
            district_data_func = getattr(lib, "get_district_data_for_chart")
            
            if district_data_func:
                df = district_data_func(self.property_type, self.deal_type)
                
                self.logger.debug(f"داده‌های نمودار منطقه: {df.shape[0]} سطر دریافت شد")
                self.logger.debug(f"ستون‌های موجود: {df.columns.tolist()}")
                
                # حذف سطر Total اگر در دیتافریم وجود داشته باشد
                if 'District' in df.columns and 'Total' in df['District'].values:
                    self.logger.debug("حذف سطر 'Total' از دیتافریم")
                    df = df[df['District'] != 'Total']
                
                if not df.empty:
                    # تنظیم نمودار
                    self.chart.plot(
                        df,
                        x_column="District",
                        y_column="Total",
                        label_column="District",
                        show_values=False,
                        show_percent=True
                    )
                    self.logger.debug("نمودار توزیع منطقه با موفقیت به‌روزرسانی شد")
                else:
                    self.logger.warning("داده‌های منطقه خالی است - نمودار به‌روزرسانی نمی‌شود")
            else:
                self.logger.error("تابع دریافت داده‌های منطقه برای نمودار در دسترس نیست")
        except Exception as e:
            self.logger.error(f"خطا در به‌روزرسانی نمودار توزیع منطقه: {str(e)}", exc_info=True)
            QMessageBox.critical(self, "خطا", f"خطا در نمایش نمودار توزیع منطقه: {str(e)}")
            
    def update_chart(self, deal_type=None):
        """برای سازگاری با رابط قبلی"""
        if deal_type is not None:
            self.deal_type = deal_type
        self.refresh_chart()


class PriceRangeChart(ChartWidget):
    """نمودار توزیع املاک بر اساس محدوده قیمت"""
    
    def __init__(self, parent=None):
        super().__init__(parent, chart_title="توزیع املاک بر اساس قیمت")
        self.logger = logging.getLogger(__name__)
        self.property_type = "all"  # پیش‌فرض برای همه انواع ملک
        self.deal_type = "all"  # پیش‌فرض برای همه انواع معاملات
        self.setup_ui()
    
    def setup_ui(self):
        """راه‌اندازی رابط کاربری نمودار"""
        # افزودن کنترل‌های فیلتر در بالای نمودار
        filter_layout = QHBoxLayout()
        
        # انتخاب نوع ملک
        self.property_type_combo = QComboBox()
        self.property_type_combo.addItem("همه انواع ملک", "all")
        self.property_type_combo.addItem("مسکونی", "residential")
        self.property_type_combo.addItem("تجاری", "commercial")
        self.property_type_combo.addItem("زمین", "land")
        self.property_type_combo.currentIndexChanged.connect(self.on_filter_changed)
        
        # انتخاب نوع معامله
        self.deal_type_combo = QComboBox()
        self.deal_type_combo.addItem("همه معاملات", "all")
        self.deal_type_combo.addItem("فروش", "sale")
        self.deal_type_combo.addItem("اجاره", "rent")
        self.deal_type_combo.currentIndexChanged.connect(self.on_filter_changed)
        
        filter_layout.addWidget(QLabel("نوع ملک:"))
        filter_layout.addWidget(self.property_type_combo)
        filter_layout.addWidget(QLabel("نوع معامله:"))
        filter_layout.addWidget(self.deal_type_combo)
        filter_layout.addStretch()
        
        self.chart_layout.insertLayout(0, filter_layout)
        
        # تنظیم نمودار اصلی
        self.chart = PieChart()
        self.chart_view = self.create_chart_view(self.chart)
        self.chart_layout.addWidget(self.chart_view)
        
        # رفرش اولیه نمودار
        self.refresh_chart()
    
    def on_filter_changed(self):
        """وقتی فیلترها تغییر می‌کنند، نمودار به‌روزرسانی شود"""
        self.property_type = self.property_type_combo.currentData()
        self.deal_type = self.deal_type_combo.currentData()
        self.refresh_chart()
    
    def refresh_chart(self):
        """به‌روزرسانی نمودار با داده‌های جدید"""
        try:
            self.logger.debug(f"به‌روزرسانی نمودار توزیع قیمت با فیلترهای: نوع ملک={self.property_type}، نوع معامله={self.deal_type}")
            
            # دریافت داده‌های قیمت از طریق بریج
            lib = get_lib_instance()
            price_data_func = getattr(lib, "get_price_data_for_chart")
            
            if price_data_func:
                df = price_data_func(self.property_type, self.deal_type)
                
                self.logger.debug(f"داده‌های نمودار قیمت: {df.shape[0]} سطر دریافت شد")
                self.logger.debug(f"ستون‌های موجود: {df.columns.tolist()}")
                
                if not df.empty:
                    # تنظیم نمودار
                    self.chart.plot(
                        df,
                        x_column="PriceRange",
                        y_column="Count",
                        label_column="Percentage",
                        show_values=False,
                        show_percent=True
                    )
                    self.logger.debug("نمودار توزیع قیمت با موفقیت به‌روزرسانی شد")
                else:
                    self.logger.warning("داده‌های قیمت خالی است - نمودار به‌روزرسانی نمی‌شود")
            else:
                self.logger.error("تابع دریافت داده‌های قیمت برای نمودار در دسترس نیست")
        except Exception as e:
            self.logger.error(f"خطا در به‌روزرسانی نمودار توزیع قیمت: {str(e)}", exc_info=True)
            QMessageBox.critical(self, "خطا", f"خطا در نمایش نمودار توزیع قیمت: {str(e)}")


class DashboardTab(QWidget):
    """کلاس تب داشبورد برای سیستم مدیریت املاک"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.logger = logging.getLogger(__name__)
        self.report_generator = ReportGenerator()
        
        # تنظیم رابط کاربری
        self.setup_ui()
        
        # زمان‌بندی به‌روزرسانی
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_all)
        self.refresh_timer.start(300000)  # هر 5 دقیقه به‌روزرسانی
        
        self.logger.info("تب داشبورد ایجاد شد")
    
    def setup_ui(self):
        """راه‌اندازی رابط کاربری"""
        main_layout = QVBoxLayout(self)
        
        # عنوان
        header_layout = QHBoxLayout()
        
        title_label = QLabel("داشبورد مدیریت املاک")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        date_label = QLabel(QDate.currentDate().toString("dddd d MMMM yyyy"))
        date_font = QFont()
        date_font.setPointSize(10)
        date_label.setFont(date_font)
        header_layout.addWidget(date_label)
        
        refresh_button = QPushButton("به‌روزرسانی")
        refresh_button.setIcon(QIcon("icons/refresh.png"))
        refresh_button.clicked.connect(self.refresh_all)
        header_layout.addWidget(refresh_button)
        
        main_layout.addLayout(header_layout)
        
        # بخش کارت‌های آمار
        self.setup_stat_cards()
        main_layout.addLayout(self.stats_layout)
        
        # بخش نمودارها
        self.setup_charts()
        main_layout.addLayout(self.charts_layout, 1)
        
        # بخش آمار سریع
        self.setup_quick_stats()
        main_layout.addWidget(self.quick_stats_group)
    
    def setup_stat_cards(self):
        """راه‌اندازی کارت‌های آمار"""
        self.stats_layout = QHBoxLayout()
        
        self.total_properties_card = StatCard(
            "کل املاک", "0", 
            icon_path="icons/building.png", 
            color="#2196F3"
        )
        self.stats_layout.addWidget(self.total_properties_card)
        
        self.residential_card = StatCard(
            "املاک مسکونی", "0", 
            icon_path="icons/home.png", 
            color="#4CAF50"
        )
        self.stats_layout.addWidget(self.residential_card)
        
        self.commercial_card = StatCard(
            "املاک تجاری", "0", 
            icon_path="icons/store.png", 
            color="#FF9800"
        )
        self.stats_layout.addWidget(self.commercial_card)
        
        self.land_card = StatCard(
            "زمین", "0", 
            icon_path="icons/terrain.png", 
            color="#9C27B0"
        )
        self.stats_layout.addWidget(self.land_card)
        
        self.total_value_card = StatCard(
            "ارزش کل (میلیارد تومان)", "0", 
            icon_path="icons/money.png", 
            color="#F44336"
        )
        self.stats_layout.addWidget(self.total_value_card)
    
    def setup_charts(self):
        """راه‌اندازی نمودارهای داشبورد"""
        self.logger.debug("راه‌اندازی نمودارهای داشبورد")
        
        # لایه‌بندی نمودارها
        self.charts_widget = QWidget()
        self.charts_layout = QGridLayout(self.charts_widget)
        self.charts_layout.setContentsMargins(10, 10, 10, 10)
        self.charts_layout.setSpacing(15)
        
        # نمودار تعداد املاک
        self.property_count_chart = PropertyCountChart()
        self.charts_layout.addWidget(self.property_count_chart, 0, 0)
        
        # نمودار توزیع منطقه
        self.district_chart = DistrictDistributionChart()
        self.charts_layout.addWidget(self.district_chart, 0, 1)
        
        # نمودار توزیع قیمت
        self.price_chart = PriceRangeChart()
        self.charts_layout.addWidget(self.price_chart, 1, 0, 1, 2)
        
        # افزودن به اسکرول اصلی
        self.scroll_content_layout.addWidget(self.charts_widget)
        
        # پیکربندی تایمر به‌روزرسانی خودکار
        self.update_timer = QTimer(self)
        self.update_timer.setInterval(300000)  # هر 5 دقیقه به‌روزرسانی شود
        self.update_timer.timeout.connect(self.refresh_all)
        self.update_timer.start()
    
    def setup_quick_stats(self):
        """راه‌اندازی بخش آمار سریع"""
        self.quick_stats_group = QGroupBox("آمار سریع")
        quick_stats_layout = QHBoxLayout(self.quick_stats_group)
        
        form_layout1 = QFormLayout()
        form_layout1.setLabelAlignment(Qt.AlignRight)
        
        self.newest_property_label = QLabel("-")
        form_layout1.addRow("جدیدترین ملک:", self.newest_property_label)
        
        self.most_expensive_label = QLabel("-")
        form_layout1.addRow("گران‌ترین ملک:", self.most_expensive_label)
        
        self.this_month_count_label = QLabel("-")
        form_layout1.addRow("تعداد املاک این ماه:", self.this_month_count_label)
        
        quick_stats_layout.addLayout(form_layout1)
        
        form_layout2 = QFormLayout()
        form_layout2.setLabelAlignment(Qt.AlignRight)
        
        self.avg_price_label = QLabel("-")
        form_layout2.addRow("میانگین قیمت:", self.avg_price_label)
        
        self.most_properties_district_label = QLabel("-")
        form_layout2.addRow("منطقه با بیشترین املاک:", self.most_properties_district_label)
        
        self.most_valuable_district_label = QLabel("-")
        form_layout2.addRow("منطقه با بیشترین ارزش:", self.most_valuable_district_label)
        
        quick_stats_layout.addLayout(form_layout2)
    
    def refresh_all(self):
        """به‌روزرسانی تمام اطلاعات داشبورد"""
        self.logger.info("در حال به‌روزرسانی داشبورد...")
        
        try:
            # دریافت آمار تعداد کل املاک
            df = self.report_generator.generate_property_count_report(
                deal_type="sale", 
                output_format="dataframe"
            )
            
            if not df.empty:
                total = df['تعداد'].sum()
                self.total_properties_card.set_value(total)
                
                # آمار به تفکیک نوع ملک
                for _, row in df.iterrows():
                    if row['نوع ملک'] == 'مسکونی':
                        self.residential_card.set_value(row['تعداد'])
                    elif row['نوع ملک'] == 'تجاری':
                        self.commercial_card.set_value(row['تعداد'])
                    elif row['نوع ملک'] == 'زمین':
                        self.land_card.set_value(row['تعداد'])
            
            # دریافت آمار ارزش کل املاک
            value_df = self.report_generator.generate_property_value_report(
                deal_type="sale", 
                output_format="dataframe"
            )
            
            if not value_df.empty:
                total_value = value_df['ارزش کل (میلیون تومان)'].sum() / 1000  # تبدیل به میلیارد
                self.total_value_card.set_value(f"{total_value:.2f}")
            
            # به‌روزرسانی نمودارها
            self.property_count_chart.refresh_chart()
            self.district_chart.refresh_chart()
            self.price_chart.refresh_chart()
            
            # دریافت آمار سریع
            self.refresh_quick_stats()
            
            self.logger.info("به‌روزرسانی داشبورد با موفقیت انجام شد")
        except Exception as e:
            self.logger.error(f"خطا در به‌روزرسانی داشبورد: {str(e)}")
            QMessageBox.critical(self, "خطا", f"خطا در به‌روزرسانی داشبورد: {str(e)}")
    
    def refresh_quick_stats(self):
        """به‌روزرسانی آمار سریع"""
        try:
            # جدیدترین ملک
            newest_property = self.report_generator._get_all_properties().get('newest_property', {})
            if newest_property:
                property_type = newest_property.get('property_type', '')
                district = newest_property.get('district', '')
                price = newest_property.get('price', 0)
                self.newest_property_label.setText(f"{property_type} در {district} - {price:,} میلیون تومان")
            
            # گران‌ترین ملک
            most_expensive = self.report_generator._get_all_properties().get('most_expensive', {})
            if most_expensive:
                property_type = most_expensive.get('property_type', '')
                district = most_expensive.get('district', '')
                price = most_expensive.get('price', 0)
                self.most_expensive_label.setText(f"{property_type} در {district} - {price:,} میلیون تومان")
            
            # تعداد املاک این ماه
            this_month = datetime.now().strftime("%Y-%m")
            this_month_count = self.report_generator._get_all_properties().get('this_month_count', 0)
            self.this_month_count_label.setText(f"{this_month_count:,}")
            
            # میانگین قیمت
            avg_price = self.report_generator._get_all_properties().get('avg_price', 0)
            self.avg_price_label.setText(f"{avg_price:,.2f} میلیون تومان")
            
            # منطقه با بیشترین املاک
            district_df = self.report_generator.generate_district_report(
                deal_type="sale", 
                output_format="dataframe"
            )
            
            if not district_df.empty:
                most_properties_district = district_df.loc[district_df['تعداد'].idxmax()]
                self.most_properties_district_label.setText(
                    f"{most_properties_district['منطقه']} ({most_properties_district['تعداد']} ملک)"
                )
            
            # منطقه با بیشترین ارزش
            district_value_df = self.report_generator.generate_district_report(
                deal_type="sale", 
                output_format="dataframe",
                value_based=True
            )
            
            if not district_value_df.empty:
                most_valuable_district = district_value_df.loc[district_value_df['ارزش کل'].idxmax()]
                self.most_valuable_district_label.setText(
                    f"{most_valuable_district['منطقه']} ({most_valuable_district['ارزش کل']:,} میلیون تومان)"
                )
            
        except Exception as e:
            self.logger.error(f"خطا در به‌روزرسانی آمار سریع: {str(e)}")
            # نمایش پیام خطا در وضعیت، نه پنجره مجزا
            for widget in [self.newest_property_label, self.most_expensive_label, 
                          self.this_month_count_label, self.avg_price_label,
                          self.most_properties_district_label, self.most_valuable_district_label]:
                widget.setText("خطا در دریافت داده") 