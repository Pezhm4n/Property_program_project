#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ماژول تب داشبورد برای سیستم مدیریت املاک
این ماژول شامل کلاس DashboardTab برای نمایش خلاصه وضعیت سیستم و آمار مهم است.
"""

import os
import sys
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QComboBox, QGroupBox,
    QRadioButton, QCheckBox, QSpinBox, QDateEdit,
    QTabWidget, QLineEdit, QFormLayout, QFileDialog,
    QMessageBox, QSplitter, QScrollArea, QFrame,
    QButtonGroup, QToolButton, QMenu, QAction
)
from PyQt5.QtGui import QIcon, QPixmap, QFont, QPainter, QColor, QPen
from PyQt5.QtCore import Qt, QDate, pyqtSignal, pyqtSlot, QSize, QTimer, QRect

from property_management.report_generator import ReportGenerator
from property_management.charts import BarChart, PieChart, LineChart, create_chart


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
    
    def __init__(self, title, chart_type, parent=None):
        super().__init__(parent)
        self.title = title
        self.chart_type = chart_type
        self.chart_object = None
        
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
        
        self.setup_ui()
    
    def setup_ui(self):
        """راه‌اندازی رابط کاربری ویجت نمودار"""
        layout = QVBoxLayout(self)
        
        # عنوان
        title_layout = QHBoxLayout()
        
        title_label = QLabel(self.title)
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_layout.addWidget(title_label)
        
        title_layout.addStretch()
        
        # ابزارها
        self.refresh_btn = QToolButton()
        self.refresh_btn.setIcon(QIcon("icons/refresh.png"))
        self.refresh_btn.setToolTip("به‌روزرسانی نمودار")
        self.refresh_btn.clicked.connect(self.refresh_chart)
        title_layout.addWidget(self.refresh_btn)
        
        self.options_btn = QToolButton()
        self.options_btn.setIcon(QIcon("icons/settings.png"))
        self.options_btn.setToolTip("تنظیمات نمودار")
        
        options_menu = QMenu(self)
        export_action = QAction("ذخیره نمودار...", self)
        export_action.triggered.connect(self.export_chart)
        options_menu.addAction(export_action)
        
        self.options_btn.setMenu(options_menu)
        self.options_btn.setPopupMode(QToolButton.InstantPopup)
        title_layout.addWidget(self.options_btn)
        
        layout.addLayout(title_layout)
        
        # محتوای نمودار
        self.chart_container = QWidget()
        self.chart_container.setMinimumHeight(250)
        chart_layout = QVBoxLayout(self.chart_container)
        chart_layout.setContentsMargins(0, 0, 0, 0)
        
        self.placeholder_label = QLabel("در حال بارگذاری نمودار...")
        self.placeholder_label.setAlignment(Qt.AlignCenter)
        chart_layout.addWidget(self.placeholder_label)
        
        layout.addWidget(self.chart_container)
    
    def set_chart(self, chart_data, chart_params=None):
        """تنظیم داده‌های نمودار و نمایش آن"""
        # پاک کردن چیدمان فعلی
        for i in reversed(range(self.chart_container.layout().count())): 
            widget = self.chart_container.layout().itemAt(i).widget()
            if widget:
                widget.setParent(None)
        
        if not chart_data.empty:
            # تنظیم پارامترهای پیش‌فرض
            base_params = {
                "title": self.title,
                "figsize": (8, 4),
                "dpi": 100
            }
            
            # پارامترهای مخصوص متد plot
            plot_params = {}
            
            # اعمال پارامترهای سفارشی
            if chart_params:
                # جدا کردن پارامترهای سازنده و متد plot
                for key, value in chart_params.items():
                    if key in ['title', 'figsize', 'dpi', 'donut']:
                        base_params[key] = value
                    else:
                        plot_params[key] = value
            
            try:
                if self.chart_type == "bar":
                    self.chart_object = BarChart(**base_params)
                    self.chart_object.plot(chart_data, **plot_params)
                elif self.chart_type == "pie":
                    self.chart_object = PieChart(**base_params)
                    self.chart_object.plot(chart_data, **plot_params)
                elif self.chart_type == "line":
                    self.chart_object = LineChart(**base_params)
                    self.chart_object.plot(chart_data, **plot_params)
                
                # افزودن ویجت نمودار
                if hasattr(self.chart_object, 'get_qt_widget'):
                    chart_widget = self.chart_object.get_qt_widget()
                    self.chart_container.layout().addWidget(chart_widget)
                else:
                    self.placeholder_label = QLabel("خطا در بارگذاری نمودار")
                    self.placeholder_label.setAlignment(Qt.AlignCenter)
                    self.chart_container.layout().addWidget(self.placeholder_label)
            except Exception as e:
                logging.error(f"خطا در ایجاد نمودار: {str(e)}")
                self.placeholder_label = QLabel(f"خطا در ایجاد نمودار: {str(e)}")
                self.placeholder_label.setAlignment(Qt.AlignCenter)
                self.placeholder_label.setWordWrap(True)
                self.chart_container.layout().addWidget(self.placeholder_label)
        else:
            self.placeholder_label = QLabel("داده‌ای برای نمایش وجود ندارد")
            self.placeholder_label.setAlignment(Qt.AlignCenter)
            self.chart_container.layout().addWidget(self.placeholder_label)
    
    def refresh_chart(self):
        """به‌روزرسانی نمودار"""
        # این متد باید در کلاس فرزند بازنویسی شود
        pass
    
    def export_chart(self):
        """ذخیره نمودار به عنوان یک فایل تصویری"""
        if not hasattr(self, 'chart_object'):
            QMessageBox.warning(self, "خطا", "هیچ نموداری برای ذخیره وجود ندارد.")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "ذخیره نمودار", "", 
            "تصویر PNG (*.png);;تصویر JPG (*.jpg);;تصویر PDF (*.pdf)"
        )
        
        if file_path:
            try:
                self.chart_object.save(file_path)
                QMessageBox.information(self, "اطلاع", f"نمودار با موفقیت در {file_path} ذخیره شد.")
            except Exception as e:
                logging.error(f"خطا در ذخیره نمودار: {str(e)}")
                QMessageBox.critical(self, "خطا", f"خطا در ذخیره نمودار: {str(e)}")


class PropertyCountChart(ChartWidget):
    """نمودار تعداد املاک بر اساس نوع"""
    
    def __init__(self, report_generator, parent=None):
        super().__init__("تعداد املاک بر اساس نوع", "pie", parent)
        self.report_generator = report_generator
        self.refresh_chart()
    
    def refresh_chart(self):
        """به‌روزرسانی نمودار"""
        try:
            df = self.report_generator.generate_property_count_report(
                deal_type="sale", 
                output_format="dataframe"
            )
            
            self.set_chart(df, {
                "show_values": True,
                "donut": True,
                "figsize": (6, 4)
            })
        except Exception as e:
            logging.error(f"خطا در دریافت داده‌های نمودار تعداد املاک: {str(e)}")
            QMessageBox.critical(self, "خطا", f"خطا در دریافت داده‌های نمودار تعداد املاک: {str(e)}")
    
    def update_chart(self, deal_type=None):
        """برای سازگاری با کلاس dashboard.py"""
        self.refresh_chart()


class DistrictDistributionChart(ChartWidget):
    """نمودار توزیع املاک در مناطق"""
    
    def __init__(self, report_generator, parent=None):
        super().__init__("توزیع املاک در مناطق", "bar", parent)
        self.report_generator = report_generator
        self.refresh_chart()
    
    def refresh_chart(self):
        """به‌روزرسانی نمودار"""
        try:
            df = self.report_generator.generate_district_report(
                deal_type="sale", 
                output_format="dataframe"
            )
            
            # حذف سطر مجموع (Total) از دیتافریم
            if 'District' in df.columns and 'Total' in df['District'].values:
                df = df[df['District'] != 'Total']
            
            self.set_chart(df, {
                "horizontal": True,
                "show_values": True,
                "figsize": (6, 4)
            })
        except Exception as e:
            logging.error(f"خطا در دریافت داده‌های نمودار توزیع املاک: {str(e)}")
            QMessageBox.critical(self, "خطا", f"خطا در دریافت داده‌های نمودار توزیع املاک: {str(e)}")
    
    def update_chart(self, deal_type=None):
        """برای سازگاری با کلاس dashboard.py"""
        self.refresh_chart()


class PriceRangeChart(ChartWidget):
    """نمودار توزیع قیمت املاک"""
    
    def __init__(self, report_generator, parent=None):
        super().__init__("توزیع قیمت املاک", "bar", parent)
        self.report_generator = report_generator
        self.refresh_chart()
    
    def refresh_chart(self):
        """به‌روزرسانی نمودار"""
        try:
            df = self.report_generator.generate_price_range_report(
                deal_type="sale", 
                output_format="dataframe"
            )
            
            self.set_chart(df, {
                "show_values": True,
                "figsize": (6, 4)
            })
        except Exception as e:
            logging.error(f"خطا در دریافت داده‌های نمودار توزیع قیمت: {str(e)}")
            QMessageBox.critical(self, "خطا", f"خطا در دریافت داده‌های نمودار توزیع قیمت: {str(e)}")
    
    def update_chart(self, deal_type=None):
        """برای سازگاری با کلاس dashboard.py"""
        self.refresh_chart()


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
        """راه‌اندازی نمودارها"""
        self.charts_layout = QGridLayout()
        
        # نمودار تعداد املاک
        self.property_count_chart = PropertyCountChart(self.report_generator)
        self.charts_layout.addWidget(self.property_count_chart, 0, 0)
        
        # نمودار توزیع منطقه‌ای
        self.district_chart = DistrictDistributionChart(self.report_generator)
        self.charts_layout.addWidget(self.district_chart, 0, 1)
        
        # نمودار توزیع قیمت
        self.price_chart = PriceRangeChart(self.report_generator)
        self.charts_layout.addWidget(self.price_chart, 1, 0, 1, 2)
    
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