#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ماژول دیالوگ تنظیمات
این ماژول امکان تنظیم پارامترهای مختلف برنامه را فراهم می‌کند.
"""

import os
import sys
import logging
from typing import Dict, Any, Optional

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QMessageBox, QTabWidget, QWidget, QFormLayout,
    QSpinBox, QComboBox, QCheckBox, QColorDialog, QFileDialog,
    QGroupBox, QRadioButton, QButtonGroup, QGridLayout, QSpacerItem,
    QSizePolicy, QFontDialog, QDialogButtonBox
)
from PyQt5.QtGui import QIcon, QFont, QColor
from PyQt5.QtCore import Qt, QSettings, QSize, QLocale, pyqtSignal

class SettingsDialog(QDialog):
    """کلاس دیالوگ تنظیمات سیستم مدیریت املاک"""
    
    settings_changed = pyqtSignal(dict)  # سیگنال تغییر تنظیمات
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.logger = logging.getLogger(__name__)
        self.settings = QSettings("PropertyManagement", "App")
        
        # تنظیم ویژگی‌های دیالوگ
        self.setup_dialog()
        
        # ایجاد رابط کاربری
        self.create_ui()
        
        # بارگذاری تنظیمات فعلی
        self.load_settings()
        
        self.logger.info("دیالوگ تنظیمات ایجاد شد")
    
    def setup_dialog(self):
        """تنظیم ویژگی‌های دیالوگ"""
        self.setWindowTitle("تنظیمات برنامه")
        self.resize(650, 500)
        self.setWindowIcon(QIcon("icons/settings.png"))
        self.setModal(True)
    
    def create_ui(self):
        """ایجاد رابط کاربری دیالوگ تنظیمات"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # ایجاد تب‌های تنظیمات
        self.tabs = QTabWidget()
        
        # تب تنظیمات عمومی
        self.create_general_tab()
        
        # تب تنظیمات مسیرها
        self.create_paths_tab()
        
        # تب تنظیمات ظاهری
        self.create_appearance_tab()
        
        # تب تنظیمات گزارش‌گیری
        self.create_reports_tab()
        
        # افزودن تب‌ها به ویجت تب
        layout.addWidget(self.tabs)
        
        # دکمه‌های پایین دیالوگ
        button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel | QDialogButtonBox.RestoreDefaults)
        button_box.accepted.connect(self.save_settings)
        button_box.rejected.connect(self.reject)
        button_box.button(QDialogButtonBox.RestoreDefaults).clicked.connect(self.restore_defaults)
        layout.addWidget(button_box)
    
    def create_general_tab(self):
        """ایجاد تب تنظیمات عمومی"""
        tab = QWidget()
        layout = QFormLayout(tab)
        layout.setVerticalSpacing(15)
        layout.setLabelAlignment(Qt.AlignRight)
        
        # گروه زبان
        lang_group = QGroupBox("تنظیمات زبان")
        lang_layout = QVBoxLayout(lang_group)
        
        # انتخاب زبان برنامه
        self.language_combo = QComboBox()
        self.language_combo.addItems(["فارسی", "English"])
        lang_layout.addWidget(QLabel("زبان برنامه:"))
        lang_layout.addWidget(self.language_combo)
        
        # انتخاب زبان گزارش‌ها
        self.report_language_combo = QComboBox()
        self.report_language_combo.addItems(["فارسی", "English"])
        lang_layout.addWidget(QLabel("زبان گزارش‌ها:"))
        lang_layout.addWidget(self.report_language_combo)
        
        layout.addRow(lang_group)
        
        # گروه تنظیمات سیستمی
        system_group = QGroupBox("تنظیمات سیستمی")
        system_layout = QFormLayout(system_group)
        
        # تعداد پروپرتی‌های نمایشی در صفحه اصلی
        self.dashboard_items_spin = QSpinBox()
        self.dashboard_items_spin.setRange(5, 50)
        self.dashboard_items_spin.setSingleStep(5)
        system_layout.addRow("تعداد آیتم‌های داشبورد:", self.dashboard_items_spin)
        
        # حداکثر تعداد نتایج جستجو
        self.max_search_results_spin = QSpinBox()
        self.max_search_results_spin.setRange(10, 1000)
        self.max_search_results_spin.setSingleStep(10)
        system_layout.addRow("حداکثر نتایج جستجو:", self.max_search_results_spin)
        
        # فعال‌سازی لاگ تفصیلی
        self.detailed_logging_check = QCheckBox("فعال‌سازی لاگ تفصیلی")
        system_layout.addRow("", self.detailed_logging_check)
        
        # ذخیره خودکار
        self.autosave_check = QCheckBox("ذخیره خودکار اطلاعات")
        system_layout.addRow("", self.autosave_check)
        
        # فاصله زمانی ذخیره خودکار (دقیقه)
        self.autosave_interval_spin = QSpinBox()
        self.autosave_interval_spin.setRange(1, 60)
        system_layout.addRow("فاصله زمانی ذخیره (دقیقه):", self.autosave_interval_spin)
        
        layout.addRow(system_group)
        
        self.tabs.addTab(tab, "عمومی")
    
    def create_paths_tab(self):
        """ایجاد تب تنظیمات مسیرها"""
        tab = QWidget()
        layout = QFormLayout(tab)
        layout.setVerticalSpacing(15)
        layout.setLabelAlignment(Qt.AlignRight)
        
        # مسیر پایه برای ذخیره داده‌ها
        layout.addRow(QLabel("<b>مسیرهای ذخیره اطلاعات</b>"))
        
        path_layout = QHBoxLayout()
        self.data_path_edit = QLineEdit()
        self.data_path_edit.setReadOnly(True)
        path_layout.addWidget(self.data_path_edit)
        
        browse_btn = QPushButton("...")
        browse_btn.setMaximumWidth(30)
        browse_btn.clicked.connect(lambda: self.browse_directory(self.data_path_edit, "انتخاب مسیر پایه داده‌ها"))
        path_layout.addWidget(browse_btn)
        
        layout.addRow("مسیر پایه داده‌ها:", path_layout)
        
        # مسیر ذخیره گزارش‌ها
        report_path_layout = QHBoxLayout()
        self.report_path_edit = QLineEdit()
        self.report_path_edit.setReadOnly(True)
        report_path_layout.addWidget(self.report_path_edit)
        
        report_browse_btn = QPushButton("...")
        report_browse_btn.setMaximumWidth(30)
        report_browse_btn.clicked.connect(lambda: self.browse_directory(self.report_path_edit, "انتخاب مسیر ذخیره گزارش‌ها"))
        report_path_layout.addWidget(report_browse_btn)
        
        layout.addRow("مسیر ذخیره گزارش‌ها:", report_path_layout)
        
        # مسیر ذخیره تصاویر
        image_path_layout = QHBoxLayout()
        self.image_path_edit = QLineEdit()
        self.image_path_edit.setReadOnly(True)
        image_path_layout.addWidget(self.image_path_edit)
        
        image_browse_btn = QPushButton("...")
        image_browse_btn.setMaximumWidth(30)
        image_browse_btn.clicked.connect(lambda: self.browse_directory(self.image_path_edit, "انتخاب مسیر ذخیره تصاویر"))
        image_path_layout.addWidget(image_browse_btn)
        
        layout.addRow("مسیر ذخیره تصاویر:", image_path_layout)
        
        # مسیر ذخیره فایل‌های پشتیبان
        backup_path_layout = QHBoxLayout()
        self.backup_path_edit = QLineEdit()
        self.backup_path_edit.setReadOnly(True)
        backup_path_layout.addWidget(self.backup_path_edit)
        
        backup_browse_btn = QPushButton("...")
        backup_browse_btn.setMaximumWidth(30)
        backup_browse_btn.clicked.connect(lambda: self.browse_directory(self.backup_path_edit, "انتخاب مسیر ذخیره پشتیبان"))
        backup_path_layout.addWidget(backup_browse_btn)
        
        layout.addRow("مسیر ذخیره پشتیبان:", backup_path_layout)
        
        # تنظیمات پشتیبان‌گیری
        backup_group = QGroupBox("تنظیمات پشتیبان‌گیری")
        backup_layout = QFormLayout(backup_group)
        
        # فعال‌سازی پشتیبان‌گیری خودکار
        self.auto_backup_check = QCheckBox("پشتیبان‌گیری خودکار")
        backup_layout.addRow("", self.auto_backup_check)
        
        # تعداد روزهای پشتیبان‌گیری
        self.backup_days_spin = QSpinBox()
        self.backup_days_spin.setRange(1, 30)
        backup_layout.addRow("فاصله پشتیبان‌گیری (روز):", self.backup_days_spin)
        
        # تعداد نسخه‌های پشتیبان
        self.max_backups_spin = QSpinBox()
        self.max_backups_spin.setRange(1, 100)
        backup_layout.addRow("حداکثر تعداد نسخه پشتیبان:", self.max_backups_spin)
        
        layout.addRow(backup_group)
        
        self.tabs.addTab(tab, "مسیرها")
    
    def create_appearance_tab(self):
        """ایجاد تب تنظیمات ظاهری"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        # گروه قالب (تم)
        theme_group = QGroupBox("قالب برنامه")
        theme_layout = QVBoxLayout(theme_group)
        
        # دکمه‌های رادیویی برای انتخاب تم
        self.theme_buttons = QButtonGroup(self)
        
        light_radio = QRadioButton("روشن")
        dark_radio = QRadioButton("تیره")
        system_radio = QRadioButton("پیش‌فرض سیستم")
        
        self.theme_buttons.addButton(light_radio, 0)
        self.theme_buttons.addButton(dark_radio, 1)
        self.theme_buttons.addButton(system_radio, 2)
        
        theme_layout.addWidget(light_radio)
        theme_layout.addWidget(dark_radio)
        theme_layout.addWidget(system_radio)
        
        layout.addWidget(theme_group)
        
        # گروه فونت
        font_group = QGroupBox("فونت برنامه")
        font_layout = QVBoxLayout(font_group)
        
        font_selector_layout = QHBoxLayout()
        self.font_label = QLabel("فونت پیش‌فرض")
        self.font_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        font_selector_layout.addWidget(self.font_label)
        
        self.select_font_btn = QPushButton("انتخاب فونت")
        self.select_font_btn.clicked.connect(self.select_font)
        font_selector_layout.addWidget(self.select_font_btn)
        
        font_layout.addLayout(font_selector_layout)
        
        # اندازه فونت
        font_size_layout = QHBoxLayout()
        font_size_layout.addWidget(QLabel("اندازه فونت:"))
        
        self.font_size_combo = QComboBox()
        self.font_size_combo.addItems(["کوچک", "متوسط", "بزرگ"])
        font_size_layout.addWidget(self.font_size_combo)
        
        font_layout.addLayout(font_size_layout)
        
        layout.addWidget(font_group)
        
        # گروه رنگ‌ها
        colors_group = QGroupBox("رنگ‌های برنامه")
        colors_layout = QGridLayout(colors_group)
        
        # رنگ پس‌زمینه
        colors_layout.addWidget(QLabel("رنگ پس‌زمینه:"), 0, 0)
        self.bg_color_btn = QPushButton()
        self.bg_color_btn.setMinimumWidth(80)
        self.bg_color_btn.clicked.connect(lambda: self.select_color(self.bg_color_btn, "انتخاب رنگ پس‌زمینه"))
        colors_layout.addWidget(self.bg_color_btn, 0, 1)
        
        # رنگ متن
        colors_layout.addWidget(QLabel("رنگ متن:"), 1, 0)
        self.text_color_btn = QPushButton()
        self.text_color_btn.setMinimumWidth(80)
        self.text_color_btn.clicked.connect(lambda: self.select_color(self.text_color_btn, "انتخاب رنگ متن"))
        colors_layout.addWidget(self.text_color_btn, 1, 1)
        
        # رنگ تاکید
        colors_layout.addWidget(QLabel("رنگ تاکید:"), 2, 0)
        self.accent_color_btn = QPushButton()
        self.accent_color_btn.setMinimumWidth(80)
        self.accent_color_btn.clicked.connect(lambda: self.select_color(self.accent_color_btn, "انتخاب رنگ تاکید"))
        colors_layout.addWidget(self.accent_color_btn, 2, 1)
        
        layout.addWidget(colors_group)
        
        # گزینه‌های اضافی
        extra_group = QGroupBox("گزینه‌های اضافی")
        extra_layout = QVBoxLayout(extra_group)
        
        self.show_toolbar_check = QCheckBox("نمایش نوار ابزار")
        self.show_statusbar_check = QCheckBox("نمایش نوار وضعیت")
        self.show_icons_check = QCheckBox("نمایش آیکون‌ها در منوها")
        
        extra_layout.addWidget(self.show_toolbar_check)
        extra_layout.addWidget(self.show_statusbar_check)
        extra_layout.addWidget(self.show_icons_check)
        
        layout.addWidget(extra_group)
        
        layout.addStretch()
        
        self.tabs.addTab(tab, "ظاهر برنامه")
    
    def create_reports_tab(self):
        """ایجاد تب تنظیمات گزارش‌گیری"""
        tab = QWidget()
        layout = QFormLayout(tab)
        layout.setVerticalSpacing(15)
        layout.setLabelAlignment(Qt.AlignRight)
        
        # فرمت پیش‌فرض خروجی گزارش
        self.default_report_format_combo = QComboBox()
        self.default_report_format_combo.addItems(["PDF", "Excel", "CSV", "HTML"])
        layout.addRow("فرمت پیش‌فرض گزارش:", self.default_report_format_combo)
        
        # گروه تنظیمات PDF
        pdf_group = QGroupBox("تنظیمات PDF")
        pdf_layout = QFormLayout(pdf_group)
        
        # اندازه کاغذ PDF
        self.pdf_paper_size_combo = QComboBox()
        self.pdf_paper_size_combo.addItems(["A4", "A5", "Letter", "Legal"])
        pdf_layout.addRow("اندازه کاغذ:", self.pdf_paper_size_combo)
        
        # جهت کاغذ
        self.pdf_orientation_combo = QComboBox()
        self.pdf_orientation_combo.addItems(["عمودی", "افقی"])
        pdf_layout.addRow("جهت کاغذ:", self.pdf_orientation_combo)
        
        # حاشیه‌ها
        self.pdf_margin_spin = QSpinBox()
        self.pdf_margin_spin.setRange(0, 50)
        self.pdf_margin_spin.setSuffix(" mm")
        pdf_layout.addRow("حاشیه:", self.pdf_margin_spin)
        
        # نمایش لوگو
        self.pdf_show_logo_check = QCheckBox()
        pdf_layout.addRow("نمایش لوگو:", self.pdf_show_logo_check)
        
        # مسیر لوگو
        logo_path_layout = QHBoxLayout()
        self.pdf_logo_path_edit = QLineEdit()
        self.pdf_logo_path_edit.setReadOnly(True)
        logo_path_layout.addWidget(self.pdf_logo_path_edit)
        
        logo_browse_btn = QPushButton("...")
        logo_browse_btn.setMaximumWidth(30)
        logo_browse_btn.clicked.connect(self.browse_logo)
        logo_path_layout.addWidget(logo_browse_btn)
        
        pdf_layout.addRow("مسیر لوگو:", logo_path_layout)
        
        layout.addRow(pdf_group)
        
        # گروه تنظیمات نمودارها
        chart_group = QGroupBox("تنظیمات نمودارها")
        chart_layout = QFormLayout(chart_group)
        
        # استایل پیش‌فرض نمودار
        self.chart_style_combo = QComboBox()
        self.chart_style_combo.addItems([
            "پیش‌فرض", "ggplot", "bmh", "seaborn", "seaborn-colorblind", 
            "seaborn-dark", "seaborn-darkgrid", "seaborn-ticks"
        ])
        chart_layout.addRow("استایل پیش‌فرض:", self.chart_style_combo)
        
        # اندازه پیش‌فرض نمودار
        chart_size_layout = QHBoxLayout()
        self.chart_width_spin = QSpinBox()
        self.chart_width_spin.setRange(400, 2000)
        self.chart_width_spin.setSingleStep(100)
        self.chart_width_spin.setSuffix(" px")
        chart_size_layout.addWidget(self.chart_width_spin)
        
        chart_size_layout.addWidget(QLabel("×"))
        
        self.chart_height_spin = QSpinBox()
        self.chart_height_spin.setRange(300, 1500)
        self.chart_height_spin.setSingleStep(100)
        self.chart_height_spin.setSuffix(" px")
        chart_size_layout.addWidget(self.chart_height_spin)
        
        chart_layout.addRow("اندازه پیش‌فرض:", chart_size_layout)
        
        # دقت ارقام
        self.chart_precision_spin = QSpinBox()
        self.chart_precision_spin.setRange(0, 4)
        chart_layout.addRow("دقت اعشاری نمودارها:", self.chart_precision_spin)
        
        # نمایش مقادیر روی نمودار
        self.chart_show_values_check = QCheckBox()
        chart_layout.addRow("نمایش مقادیر روی نمودار:", self.chart_show_values_check)
        
        layout.addRow(chart_group)
        
        self.tabs.addTab(tab, "گزارش‌ها")
    
    def browse_directory(self, line_edit, title):
        """انتخاب مسیر دایرکتوری"""
        current_path = line_edit.text() or os.path.expanduser("~")
        
        directory = QFileDialog.getExistingDirectory(
            self, title, current_path,
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        
        if directory:
            line_edit.setText(directory)
    
    def browse_logo(self):
        """انتخاب فایل لوگو"""
        current_path = self.pdf_logo_path_edit.text() or os.path.expanduser("~")
        
        file_name, _ = QFileDialog.getOpenFileName(
            self, "انتخاب فایل لوگو", current_path,
            "تصاویر (*.png *.jpg *.jpeg *.bmp *.svg)"
        )
        
        if file_name:
            self.pdf_logo_path_edit.setText(file_name)
    
    def select_color(self, button, title):
        """انتخاب رنگ"""
        current_color = button.palette().button().color()
        color = QColorDialog.getColor(current_color, self, title)
        
        if color.isValid():
            style_sheet = f"background-color: {color.name()};"
            button.setStyleSheet(style_sheet)
            button.setProperty("color", color.name())
    
    def select_font(self):
        """انتخاب فونت"""
        current_font = self.font_label.font()
        ok, font = QFontDialog.getFont(current_font, self, "انتخاب فونت برنامه")
        
        if ok:
            self.font_label.setText(f"{font.family()}, {font.pointSize()}pt")
            self.font_label.setFont(font)
            self.font_label.setProperty("selectedFont", font)
    
    def load_settings(self):
        """بارگذاری تنظیمات فعلی"""
        # تنظیمات عمومی
        self.language_combo.setCurrentText(self.settings.value("language", "فارسی"))
        self.report_language_combo.setCurrentText(self.settings.value("report_language", "فارسی"))
        self.dashboard_items_spin.setValue(int(self.settings.value("dashboard_items", 10)))
        self.max_search_results_spin.setValue(int(self.settings.value("max_search_results", 100)))
        self.detailed_logging_check.setChecked(self.settings.value("detailed_logging", False, type=bool))
        self.autosave_check.setChecked(self.settings.value("autosave", True, type=bool))
        self.autosave_interval_spin.setValue(int(self.settings.value("autosave_interval", 5)))
        
        # تنظیمات مسیرها
        self.data_path_edit.setText(self.settings.value("data_path", os.path.expanduser("~/property_data")))
        self.report_path_edit.setText(self.settings.value("report_path", os.path.expanduser("~/property_reports")))
        self.image_path_edit.setText(self.settings.value("image_path", os.path.expanduser("~/property_images")))
        self.backup_path_edit.setText(self.settings.value("backup_path", os.path.expanduser("~/property_backups")))
        self.auto_backup_check.setChecked(self.settings.value("auto_backup", True, type=bool))
        self.backup_days_spin.setValue(int(self.settings.value("backup_days", 7)))
        self.max_backups_spin.setValue(int(self.settings.value("max_backups", 10)))
        
        # تنظیمات ظاهری
        theme_id = int(self.settings.value("theme", 2))  # پیش‌فرض: پیش‌فرض سیستم
        self.theme_buttons.button(theme_id).setChecked(True)
        
        # فونت
        default_font = self.font().family()
        default_size = self.font().pointSize()
        font_str = self.settings.value("font", f"{default_font}, {default_size}pt")
        self.font_label.setText(font_str)
        
        # اندازه فونت
        font_size = self.settings.value("font_size", "متوسط")
        self.font_size_combo.setCurrentText(font_size)
        
        # رنگ‌ها
        bg_color = self.settings.value("bg_color", "#ffffff")
        text_color = self.settings.value("text_color", "#000000")
        accent_color = self.settings.value("accent_color", "#0078d7")
        
        self.bg_color_btn.setStyleSheet(f"background-color: {bg_color};")
        self.bg_color_btn.setProperty("color", bg_color)
        
        self.text_color_btn.setStyleSheet(f"background-color: {text_color};")
        self.text_color_btn.setProperty("color", text_color)
        
        self.accent_color_btn.setStyleSheet(f"background-color: {accent_color};")
        self.accent_color_btn.setProperty("color", accent_color)
        
        # گزینه‌های اضافی
        self.show_toolbar_check.setChecked(self.settings.value("show_toolbar", True, type=bool))
        self.show_statusbar_check.setChecked(self.settings.value("show_statusbar", True, type=bool))
        self.show_icons_check.setChecked(self.settings.value("show_icons", True, type=bool))
        
        # تنظیمات گزارش‌گیری
        self.default_report_format_combo.setCurrentText(self.settings.value("default_report_format", "PDF"))
        self.pdf_paper_size_combo.setCurrentText(self.settings.value("pdf_paper_size", "A4"))
        self.pdf_orientation_combo.setCurrentText(self.settings.value("pdf_orientation", "عمودی"))
        self.pdf_margin_spin.setValue(int(self.settings.value("pdf_margin", 15)))
        self.pdf_show_logo_check.setChecked(self.settings.value("pdf_show_logo", False, type=bool))
        self.pdf_logo_path_edit.setText(self.settings.value("pdf_logo_path", ""))
        
        # تنظیمات نمودارها
        self.chart_style_combo.setCurrentText(self.settings.value("chart_style", "پیش‌فرض"))
        self.chart_width_spin.setValue(int(self.settings.value("chart_width", 800)))
        self.chart_height_spin.setValue(int(self.settings.value("chart_height", 600)))
        self.chart_precision_spin.setValue(int(self.settings.value("chart_precision", 1)))
        self.chart_show_values_check.setChecked(self.settings.value("chart_show_values", True, type=bool))
    
    def save_settings(self):
        """ذخیره تنظیمات"""
        # تنظیمات عمومی
        self.settings.setValue("language", self.language_combo.currentText())
        self.settings.setValue("report_language", self.report_language_combo.currentText())
        self.settings.setValue("dashboard_items", self.dashboard_items_spin.value())
        self.settings.setValue("max_search_results", self.max_search_results_spin.value())
        self.settings.setValue("detailed_logging", self.detailed_logging_check.isChecked())
        self.settings.setValue("autosave", self.autosave_check.isChecked())
        self.settings.setValue("autosave_interval", self.autosave_interval_spin.value())
        
        # تنظیمات مسیرها
        self.settings.setValue("data_path", self.data_path_edit.text())
        self.settings.setValue("report_path", self.report_path_edit.text())
        self.settings.setValue("image_path", self.image_path_edit.text())
        self.settings.setValue("backup_path", self.backup_path_edit.text())
        self.settings.setValue("auto_backup", self.auto_backup_check.isChecked())
        self.settings.setValue("backup_days", self.backup_days_spin.value())
        self.settings.setValue("max_backups", self.max_backups_spin.value())
        
        # تنظیمات ظاهری
        self.settings.setValue("theme", self.theme_buttons.checkedId())
        self.settings.setValue("font", self.font_label.text())
        self.settings.setValue("font_size", self.font_size_combo.currentText())
        
        self.settings.setValue("bg_color", self.bg_color_btn.property("color"))
        self.settings.setValue("text_color", self.text_color_btn.property("color"))
        self.settings.setValue("accent_color", self.accent_color_btn.property("color"))
        
        self.settings.setValue("show_toolbar", self.show_toolbar_check.isChecked())
        self.settings.setValue("show_statusbar", self.show_statusbar_check.isChecked())
        self.settings.setValue("show_icons", self.show_icons_check.isChecked())
        
        # تنظیمات گزارش‌گیری
        self.settings.setValue("default_report_format", self.default_report_format_combo.currentText())
        self.settings.setValue("pdf_paper_size", self.pdf_paper_size_combo.currentText())
        self.settings.setValue("pdf_orientation", self.pdf_orientation_combo.currentText())
        self.settings.setValue("pdf_margin", self.pdf_margin_spin.value())
        self.settings.setValue("pdf_show_logo", self.pdf_show_logo_check.isChecked())
        self.settings.setValue("pdf_logo_path", self.pdf_logo_path_edit.text())
        
        self.settings.setValue("chart_style", self.chart_style_combo.currentText())
        self.settings.setValue("chart_width", self.chart_width_spin.value())
        self.settings.setValue("chart_height", self.chart_height_spin.value())
        self.settings.setValue("chart_precision", self.chart_precision_spin.value())
        self.settings.setValue("chart_show_values", self.chart_show_values_check.isChecked())
        
        # ارسال سیگنال تغییر تنظیمات
        settings_dict = {}
        for key in self.settings.allKeys():
            settings_dict[key] = self.settings.value(key)
        
        self.settings_changed.emit(settings_dict)
        
        self.logger.info("تنظیمات ذخیره شدند")
        self.accept()
    
    def restore_defaults(self):
        """بازگرداندن تنظیمات به حالت پیش‌فرض"""
        reply = QMessageBox.question(
            self, 
            "بازنشانی تنظیمات", 
            "آیا مطمئن هستید که می‌خواهید تمام تنظیمات را به حالت پیش‌فرض برگردانید؟",
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # حذف تنظیمات فعلی
            self.settings.clear()
            
            # بارگذاری مقادیر پیش‌فرض
            self.load_settings()
            
            self.logger.info("تنظیمات به حالت پیش‌فرض بازنشانی شدند")
            
            QMessageBox.information(
                self, 
                "بازنشانی تنظیمات", 
                "تنظیمات به حالت پیش‌فرض بازگردانده شدند."
            ) 