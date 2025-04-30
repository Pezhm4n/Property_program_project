#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ماژول برگه گزارش‌ها برای سیستم مدیریت املاک

این ماژول شامل کلاس ReportTab برای ایجاد رابط کاربری گزارش‌گیری از سیستم مدیریت املاک است.
کاربر می‌تواند انواع گزارش‌های مختلف تولید کرده و در قالب‌های مختلف خروجی بگیرد.
"""

import os
import logging
from datetime import datetime
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
                           QLabel, QPushButton, QComboBox, QRadioButton,
                           QButtonGroup, QTableWidget, QTableWidgetItem,
                           QHeaderView, QFileDialog, QMessageBox, QTabWidget,
                           QFormLayout, QSpinBox, QCheckBox, QSplitter)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QIcon, QPixmap

from property_management.report_generator import ReportGenerator
from property_management.charts import create_chart
from property_management.export import export_data

class ChartWidget(QWidget):
    """ویجت نمایش نمودار با قابلیت ذخیره‌سازی"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.chart = None
        self.init_ui()
        
    def init_ui(self):
        """راه‌اندازی رابط کاربری"""
        self.layout = QVBoxLayout(self)
        
        # منطقه نمودار
        self.chart_container = QWidget()
        self.chart_layout = QVBoxLayout(self.chart_container)
        
        # دکمه‌های کنترلی
        self.button_layout = QHBoxLayout()
        self.save_btn = QPushButton("ذخیره نمودار")
        self.save_btn.setIcon(QIcon.fromTheme("document-save"))
        self.save_btn.clicked.connect(self.save_chart)
        
        self.button_layout.addWidget(self.save_btn)
        self.button_layout.addStretch()
        
        self.layout.addWidget(self.chart_container)
        self.layout.addLayout(self.button_layout)
    
    def set_chart(self, chart):
        """تنظیم نمودار جدید"""
        self.chart = chart
        
        # پاکسازی منطقه نمودار قبلی
        for i in reversed(range(self.chart_layout.count())): 
            widget = self.chart_layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)
        
        # افزودن نمودار جدید
        if chart:
            canvas = chart.get_qt_canvas()
            self.chart_layout.addWidget(canvas)
    
    def save_chart(self):
        """ذخیره نمودار در فایل"""
        if not self.chart:
            QMessageBox.warning(self, "خطا", "هیچ نموداری برای ذخیره‌سازی وجود ندارد.")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "ذخیره نمودار",
            os.path.expanduser("~/Documents"),
            "تصاویر (*.png *.jpg *.pdf)"
        )
        
        if file_path:
            try:
                self.chart.save(file_path)
                QMessageBox.information(self, "ذخیره نمودار", f"نمودار با موفقیت در مسیر {file_path} ذخیره شد.")
            except Exception as e:
                logging.error(f"خطا در ذخیره نمودار: {str(e)}")
                QMessageBox.critical(self, "خطا", f"خطا در ذخیره نمودار: {str(e)}")

class ReportTab(QWidget):
    """برگه گزارش‌گیری از سیستم مدیریت املاک"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.report_generator = ReportGenerator()
        self.init_ui()
        
    def init_ui(self):
        """راه‌اندازی رابط کاربری"""
        main_layout = QHBoxLayout(self)
        
        # بخش تنظیمات گزارش در سمت راست
        settings_group = QGroupBox("تنظیمات گزارش")
        settings_layout = QVBoxLayout(settings_group)
        
        # نوع گزارش
        report_type_layout = QFormLayout()
        self.report_type_combo = QComboBox()
        self.report_type_combo.addItems([
            "تعداد املاک", 
            "ارزش املاک", 
            "گزارش منطقه‌ای", 
            "گزارش محدوده قیمت"
        ])
        self.report_type_combo.currentIndexChanged.connect(self.on_report_type_changed)
        report_type_layout.addRow("نوع گزارش:", self.report_type_combo)
        
        # نوع معامله
        self.deal_type_combo = QComboBox()
        self.deal_type_combo.addItems(["فروش", "اجاره", "همه"])
        report_type_layout.addRow("نوع معامله:", self.deal_type_combo)
        
        settings_layout.addLayout(report_type_layout)
        
        # تنظیمات خاص برای هر نوع گزارش
        self.report_specific_settings = QGroupBox("تنظیمات اختصاصی")
        self.report_specific_layout = QVBoxLayout(self.report_specific_settings)
        settings_layout.addWidget(self.report_specific_settings)
        
        # قالب خروجی
        output_format_group = QGroupBox("قالب خروجی")
        output_format_layout = QVBoxLayout(output_format_group)
        
        self.output_format_combo = QComboBox()
        self.output_format_combo.addItems(["نمایش", "Excel", "PDF", "CSV", "متنی"])
        output_format_layout.addWidget(self.output_format_combo)
        
        settings_layout.addWidget(output_format_group)
        
        # نوع نمودار
        chart_group = QGroupBox("نمودار")
        chart_layout = QVBoxLayout(chart_group)
        
        self.chart_type_combo = QComboBox()
        self.chart_type_combo.addItems(["نمودار میله‌ای", "نمودار دایره‌ای", "نمودار خطی", "بدون نمودار"])
        chart_layout.addWidget(self.chart_type_combo)
        
        settings_layout.addWidget(chart_group)
        
        # دکمه‌های اقدام
        action_layout = QHBoxLayout()
        
        self.generate_btn = QPushButton("تولید گزارش")
        self.generate_btn.setIcon(QIcon.fromTheme("document-new"))
        self.generate_btn.clicked.connect(self.generate_report)
        
        self.export_btn = QPushButton("خروجی")
        self.export_btn.setIcon(QIcon.fromTheme("document-save"))
        self.export_btn.clicked.connect(self.export_report)
        
        self.clear_btn = QPushButton("پاک کردن")
        self.clear_btn.setIcon(QIcon.fromTheme("edit-clear"))
        self.clear_btn.clicked.connect(self.clear_report)
        
        action_layout.addWidget(self.generate_btn)
        action_layout.addWidget(self.export_btn)
        action_layout.addWidget(self.clear_btn)
        
        settings_layout.addLayout(action_layout)
        settings_layout.addStretch()
        
        # اضافه کردن بخش تنظیمات به طرح اصلی
        main_layout.addWidget(settings_group)
        
        # بخش نمایش گزارش و نمودار در سمت چپ
        display_widget = QWidget()
        display_layout = QVBoxLayout(display_widget)
        
        # تب‌های نمایش گزارش و نمودار
        self.display_tabs = QTabWidget()
        
        # تب گزارش
        self.report_widget = QWidget()
        report_layout = QVBoxLayout(self.report_widget)
        
        self.result_table = QTableWidget()
        self.result_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.result_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        report_layout.addWidget(self.result_table)
        
        # تب نمودار
        self.chart_widget = ChartWidget()
        
        # اضافه کردن تب‌ها
        self.display_tabs.addTab(self.report_widget, "گزارش")
        self.display_tabs.addTab(self.chart_widget, "نمودار")
        
        display_layout.addWidget(self.display_tabs)
        
        # اضافه کردن بخش نمایش به طرح اصلی
        main_layout.addWidget(display_widget, 2)  # با نسبت 2 به 1
        
        # تنظیم اولیه رابط کاربری
        self.on_report_type_changed(0)
        self.report_data = None  # برای نگهداری داده‌های گزارش فعلی
    
    def on_report_type_changed(self, index):
        """تغییر تنظیمات خاص بر اساس نوع گزارش انتخاب شده"""
        # پاکسازی تنظیمات قبلی
        for i in reversed(range(self.report_specific_layout.count())): 
            widget = self.report_specific_layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)
            
        if index == 0:  # تعداد املاک
            label = QLabel("گزارش تعداد املاک به تفکیک نوع ملک را نمایش می‌دهد.")
            self.report_specific_layout.addWidget(label)
            
        elif index == 1:  # ارزش املاک
            label = QLabel("گزارش ارزش کل املاک به تفکیک نوع ملک را نمایش می‌دهد.")
            self.report_specific_layout.addWidget(label)
            
        elif index == 2:  # گزارش منطقه‌ای
            label = QLabel("گزارش تعداد املاک به تفکیک منطقه را نمایش می‌دهد.")
            self.report_specific_layout.addWidget(label)
            
        elif index == 3:  # گزارش محدوده قیمت
            price_layout = QFormLayout()
            
            self.min_range_spin = QSpinBox()
            self.min_range_spin.setRange(0, 100000000)
            self.min_range_spin.setSingleStep(1000000)
            self.min_range_spin.setValue(0)
            
            self.max_range_spin = QSpinBox()
            self.max_range_spin.setRange(0, 1000000000)
            self.max_range_spin.setSingleStep(10000000)
            self.max_range_spin.setValue(100000000)
            
            self.range_count_spin = QSpinBox()
            self.range_count_spin.setRange(2, 10)
            self.range_count_spin.setValue(5)
            
            price_layout.addRow("حداقل قیمت:", self.min_range_spin)
            price_layout.addRow("حداکثر قیمت:", self.max_range_spin)
            price_layout.addRow("تعداد دسته‌ها:", self.range_count_spin)
            
            self.report_specific_layout.addLayout(price_layout)

    def generate_report(self):
        """تولید گزارش بر اساس تنظیمات انتخاب شده"""
        report_type = self.report_type_combo.currentIndex()
        deal_type = self.deal_type_combo.currentText()
        
        # تبدیل نوع معامله به فرمت مناسب
        if deal_type == "فروش":
            deal_type = "sale"
        elif deal_type == "اجاره":
            deal_type = "rent"
        else:  # همه
            deal_type = None
            
        try:
            # تولید گزارش بر اساس نوع انتخاب شده
            if report_type == 0:  # تعداد املاک
                self.report_data = self.report_generator.generate_property_count_report(
                    deal_type=deal_type, 
                    output_format="df"
                )
                self.display_report_data(["نوع ملک", "تعداد", "درصد"])
                
            elif report_type == 1:  # ارزش املاک
                self.report_data = self.report_generator.generate_property_value_report(
                    deal_type="sale" if deal_type in [None, "sale"] else deal_type,
                    output_format="df"
                )
                self.display_report_data(["نوع ملک", "ارزش کل", "میانگین قیمت", "درصد ارزش کل"])
                
            elif report_type == 2:  # گزارش منطقه‌ای
                self.report_data = self.report_generator.generate_district_report(
                    deal_type=deal_type,
                    output_format="df"
                )
                self.display_report_data(["منطقه", "مسکونی", "تجاری", "زمین", "مجموع"])
                
            elif report_type == 3:  # گزارش محدوده قیمت
                min_price = self.min_range_spin.value()
                max_price = self.max_range_spin.value()
                num_bins = self.range_count_spin.value()
                
                self.report_data = self.report_generator.generate_price_range_report(
                    min_price=min_price,
                    max_price=max_price,
                    num_bins=num_bins,
                    deal_type=deal_type,
                    output_format="df"
                )
                self.display_report_data(["محدوده قیمت", "مسکونی", "تجاری", "زمین", "مجموع", "درصد"])
            
            # تولید نمودار اگر نیاز است
            self.generate_chart()
            
            # نمایش تب گزارش
            self.display_tabs.setCurrentIndex(0)
            
        except Exception as e:
            logging.error(f"خطا در تولید گزارش: {str(e)}")
            QMessageBox.critical(self, "خطا", f"خطا در تولید گزارش: {str(e)}")
    
    def display_report_data(self, headers):
        """نمایش داده‌های گزارش در جدول"""
        if self.report_data is None or len(self.report_data) == 0:
            QMessageBox.warning(self, "هشدار", "داده‌ای برای نمایش وجود ندارد.")
            return
            
        # تنظیم ستون‌های جدول
        self.result_table.setColumnCount(len(headers))
        self.result_table.setHorizontalHeaderLabels(headers)
        
        # تنظیم ردیف‌های جدول
        rows = len(self.report_data)
        self.result_table.setRowCount(rows)
        
        # پر کردن جدول با داده‌ها
        for row in range(rows):
            for col in range(len(headers)):
                try:
                    value = self.report_data.iloc[row, col]
                    # فرمت‌بندی اعداد
                    if isinstance(value, (int, float)):
                        if 'قیمت' in headers[col] or 'ارزش' in headers[col]:
                            item = QTableWidgetItem(f"{value:,.0f}")
                        elif 'درصد' in headers[col]:
                            item = QTableWidgetItem(f"{value:.2f}%")
                        else:
                            item = QTableWidgetItem(f"{value:,}")
                    else:
                        item = QTableWidgetItem(str(value))
                    
                    item.setTextAlignment(Qt.AlignCenter)
                    self.result_table.setItem(row, col, item)
                except (IndexError, KeyError):
                    continue
        
        # تنظیم عرض ستون‌ها
        self.result_table.resizeColumnsToContents()
    
    def generate_chart(self):
        """تولید نمودار بر اساس داده‌های گزارش"""
        if self.report_data is None or len(self.report_data) == 0:
            self.chart_widget.set_chart(None)
            return
            
        chart_type = self.chart_type_combo.currentText()
        if chart_type == "بدون نمودار":
            self.chart_widget.set_chart(None)
            return
            
        try:
            report_type = self.report_type_combo.currentIndex()
            
            # تعیین نوع نمودار
            chart_type_map = {
                "نمودار میله‌ای": "bar",
                "نمودار دایره‌ای": "pie",
                "نمودار خطی": "line"
            }
            chart_type = chart_type_map.get(chart_type, "bar")
            
            # تنظیم داده‌های نمودار و عنوان بر اساس نوع گزارش
            if report_type == 0:  # تعداد املاک
                data = self.report_data.iloc[:, :2]  # نوع ملک و تعداد
                title = "تعداد املاک به تفکیک نوع"
                
            elif report_type == 1:  # ارزش املاک
                data = self.report_data.iloc[:, :2]  # نوع ملک و ارزش کل
                title = "ارزش کل املاک به تفکیک نوع"
                
            elif report_type == 2:  # گزارش منطقه‌ای
                if chart_type == "pie":
                    data = self.report_data.iloc[:, [0, -1]]  # منطقه و مجموع
                else:
                    data = self.report_data.iloc[:, :-1]  # همه ستون‌ها به جز آخری
                title = "تعداد املاک به تفکیک منطقه"
                
            elif report_type == 3:  # گزارش محدوده قیمت
                if chart_type == "pie":
                    data = self.report_data.iloc[:, [0, -2]]  # محدوده قیمت و مجموع
                else:
                    data = self.report_data.iloc[:, :-2]  # بدون دو ستون آخر
                title = "تعداد املاک به تفکیک محدوده قیمت"
            
            # تولید نمودار
            chart = create_chart(
                chart_type=chart_type,
                data=data,
                title=title,
                figsize=(10, 6),
                x_label="دسته‌بندی",
                y_label="تعداد" if report_type in [0, 2, 3] else "ارزش (تومان)",
                grid=True
            )
            
            # نمایش نمودار
            self.chart_widget.set_chart(chart)
            
        except Exception as e:
            logging.error(f"خطا در تولید نمودار: {str(e)}")
            QMessageBox.critical(self, "خطا", f"خطا در تولید نمودار: {str(e)}")
    
    def export_report(self):
        """صدور گزارش به فرمت انتخاب شده"""
        if self.report_data is None or len(self.report_data) == 0:
            QMessageBox.warning(self, "هشدار", "داده‌ای برای صدور وجود ندارد.")
            return
            
        output_format = self.output_format_combo.currentText()
        
        # اگر فرمت نمایش باشد، نیازی به صدور نیست
        if output_format == "نمایش":
            return
            
        # تعیین نوع فایل و پسوند بر اساس فرمت خروجی
        if output_format == "Excel":
            file_format = "Excel Files (*.xlsx)"
            default_ext = ".xlsx"
            export_format = "excel"
        elif output_format == "PDF":
            file_format = "PDF Files (*.pdf)"
            default_ext = ".pdf"
            export_format = "pdf"
        elif output_format == "CSV":
            file_format = "CSV Files (*.csv)"
            default_ext = ".csv"
            export_format = "csv"
        else:  # متنی
            file_format = "Text Files (*.txt)"
            default_ext = ".txt"
            export_format = "text"
            
        # تعیین نام پیش‌فرض فایل
        report_type = self.report_type_combo.currentText()
        default_name = f"گزارش_{report_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{default_ext}"
        
        # دریافت مسیر فایل از کاربر
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "ذخیره گزارش",
            os.path.join(os.path.expanduser("~/Documents"), default_name),
            file_format
        )
        
        if not file_path:
            return
            
        try:
            # تولید عنوان گزارش
            report_title = f"گزارش {report_type} - {datetime.now().strftime('%Y/%m/%d')}"
            
            # صدور گزارش با استفاده از تابع export_data
            export_data(
                data=self.report_data,
                output_path=file_path,
                title=report_title,
                format=export_format
            )
            
            QMessageBox.information(self, "صدور گزارش", f"گزارش با موفقیت در مسیر {file_path} ذخیره شد.")
            
        except Exception as e:
            logging.error(f"خطا در صدور گزارش: {str(e)}")
            QMessageBox.critical(self, "خطا", f"خطا در صدور گزارش: {str(e)}")
    
    def clear_report(self):
        """پاکسازی گزارش و نمودار"""
        # پاکسازی داده‌ها
        self.report_data = None
        
        # پاکسازی جدول نتایج
        self.result_table.setRowCount(0)
        
        # پاکسازی نمودار
        self.chart_widget.set_chart(None)
        
        # بازنشانی تنظیمات
        self.report_type_combo.setCurrentIndex(0)
        self.deal_type_combo.setCurrentIndex(0)
        self.output_format_combo.setCurrentIndex(0)
        self.chart_type_combo.setCurrentIndex(0) 