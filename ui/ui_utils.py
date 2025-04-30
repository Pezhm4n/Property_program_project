#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
این ماژول شامل توابع کمکی مشترک برای رابط کاربری سیستم مدیریت املاک است.
"""

import os
import sys
import logging
from datetime import datetime
from PyQt5.QtWidgets import (
    QMessageBox, QInputDialog, QFileDialog, QProgressDialog,
    QTableWidget, QTableWidgetItem, QHeaderView, QComboBox, QLineEdit, 
    QDateEdit, QSpinBox, QDoubleSpinBox, QCheckBox, QGroupBox, QLabel,
    QHBoxLayout, QVBoxLayout, QFormLayout, QPushButton, QStyle
)
from PyQt5.QtCore import Qt, QSize, QDate, QPoint, QObject, pyqtSignal
from PyQt5.QtGui import QIcon, QColor, QPixmap, QFont, QPalette

# تنظیم لاگر
logger = logging.getLogger(__name__)

# ثابت‌های رابط کاربری
UI_ICONS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "resources", "icons")
UI_DEFAULT_MARGIN = 10
UI_DEFAULT_SPACING = 6
UI_DEFAULT_BUTTON_SIZE = QSize(100, 30)
UI_LARGE_BUTTON_SIZE = QSize(150, 35)
UI_ICON_SIZE = QSize(16, 16)
UI_LARGE_ICON_SIZE = QSize(32, 32)

# رنگ‌های سیستم
UI_COLOR_PRIMARY = "#2c3e50"
UI_COLOR_SECONDARY = "#34495e"
UI_COLOR_SUCCESS = "#27ae60"
UI_COLOR_INFO = "#2980b9"
UI_COLOR_WARNING = "#f39c12"
UI_COLOR_DANGER = "#e74c3c"
UI_COLOR_LIGHT = "#ecf0f1"
UI_COLOR_DARK = "#7f8c8d"
UI_COLOR_WHITE = "#ffffff"
UI_COLOR_BLACK = "#000000"

class SignalEmitter(QObject):
    """کلاس برای ارسال سیگنال‌های مختلف در برنامه"""
    
    # سیگنال‌های عمومی
    status_message = pyqtSignal(str, int)  # پیام، مدت زمان (ms)
    progress_update = pyqtSignal(int, int)  # مقدار فعلی، مقدار حداکثر
    data_changed = pyqtSignal(str)  # نوع داده تغییر یافته
    
    # سیگنال‌های مربوط به املاک
    property_added = pyqtSignal(str, str)  # نوع ملک، شناسه ملک
    property_updated = pyqtSignal(str, str)  # نوع ملک، شناسه ملک
    property_deleted = pyqtSignal(str, str)  # نوع ملک، شناسه ملک
    
    # سیگنال‌های مربوط به کاربر
    user_logged_in = pyqtSignal(str)  # نام کاربری
    user_logged_out = pyqtSignal()

# ایجاد نمونه سیگنال‌ها برای استفاده در کل برنامه
signal_emitter = SignalEmitter()

def get_icon(icon_name):
    """
    دریافت آیکون از مسیر آیکون‌های برنامه
    
    پارامترها:
        icon_name: نام فایل آیکون
        
    بازگشت:
        QIcon: شیء آیکون
    """
    icon_path = os.path.join(UI_ICONS_PATH, icon_name)
    if os.path.exists(icon_path):
        return QIcon(icon_path)
    else:
        logger.warning(f"آیکون '{icon_name}' در مسیر '{icon_path}' یافت نشد")
        return QIcon()

def setup_form_layout(layout, margin=UI_DEFAULT_MARGIN, spacing=UI_DEFAULT_SPACING):
    """
    تنظیم خصوصیات یک چیدمان فرم
    
    پارامترها:
        layout: شیء QFormLayout 
        margin: حاشیه اطراف چیدمان
        spacing: فاصله بین المان‌ها
    """
    layout.setContentsMargins(margin, margin, margin, margin)
    layout.setSpacing(spacing)
    layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
    layout.setLabelAlignment(Qt.AlignRight)
    layout.setFormAlignment(Qt.AlignLeft | Qt.AlignVCenter)

def setup_table_widget(table, headers, stretch_column=None, sortable=True, alternating_colors=True):
    """
    تنظیم ویژگی‌های یک جدول
    
    پارامترها:
        table: شیء QTableWidget 
        headers: لیست عناوین ستون‌ها
        stretch_column: شماره ستونی که باید کشیده شود (None برای عدم کشش)
        sortable: آیا جدول قابل مرتب‌سازی باشد
        alternating_colors: آیا رنگ‌های متناوب نمایش داده شود
    """
    # تنظیم تعداد ستون‌ها و عناوین
    table.setColumnCount(len(headers))
    table.setHorizontalHeaderLabels(headers)
    
    # تنظیم ویژگی‌های جدول
    table.setSelectionBehavior(QTableWidget.SelectRows)
    table.setEditTriggers(QTableWidget.NoEditTriggers)
    table.setAlternatingRowColors(alternating_colors)
    table.horizontalHeader().setHighlightSections(False)
    table.verticalHeader().setVisible(False)
    
    # تنظیم قابلیت مرتب‌سازی
    table.setSortingEnabled(sortable)
    
    # تنظیم کشش ستون‌ها
    if stretch_column is not None and 0 <= stretch_column < len(headers):
        table.horizontalHeader().setSectionResizeMode(stretch_column, QHeaderView.Stretch)
    else:
        table.horizontalHeader().setStretchLastSection(True)
    
    # تنظیم سایر خصوصیات هدر افقی
    for i in range(len(headers)):
        if i != stretch_column:
            table.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeToContents)

def create_button(text, icon_name=None, slot=None, tooltip=None, size=UI_DEFAULT_BUTTON_SIZE):
    """
    ایجاد یک دکمه با متن و آیکون
    
    پارامترها:
        text: متن دکمه
        icon_name: نام فایل آیکون (اختیاری)
        slot: تابع متصل به سیگنال کلیک (اختیاری)
        tooltip: متن راهنمای ابزار (اختیاری)
        size: اندازه دکمه (اختیاری)
        
    بازگشت:
        QPushButton: دکمه ایجاد شده
    """
    button = QPushButton(text)
    
    if icon_name:
        button.setIcon(get_icon(icon_name))
        button.setIconSize(UI_ICON_SIZE)
    
    if size:
        button.setMinimumSize(size)
    
    if tooltip:
        button.setToolTip(tooltip)
    
    if slot:
        button.clicked.connect(slot)
    
    return button

def confirm_dialog(parent, title, message, detailed_text=None, icon=QMessageBox.Question):
    """
    نمایش دیالوگ تأیید با گزینه‌های بله/خیر
    
    پارامترها:
        parent: ویجت والد
        title: عنوان دیالوگ
        message: پیام اصلی
        detailed_text: متن جزئیات (اختیاری)
        icon: نوع آیکون دیالوگ
        
    بازگشت:
        bool: True در صورت تأیید، False در صورت رد
    """
    msg_box = QMessageBox(parent)
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    msg_box.setDefaultButton(QMessageBox.No)
    msg_box.setIcon(icon)
    
    if detailed_text:
        msg_box.setDetailedText(detailed_text)
    
    return msg_box.exec_() == QMessageBox.Yes

def show_info_message(parent, title, message, detailed_text=None):
    """
    نمایش پیام اطلاعات
    
    پارامترها:
        parent: ویجت والد
        title: عنوان پیام
        message: متن پیام
        detailed_text: متن جزئیات (اختیاری)
    """
    msg_box = QMessageBox(parent)
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    msg_box.setIcon(QMessageBox.Information)
    
    if detailed_text:
        msg_box.setDetailedText(detailed_text)
    
    msg_box.exec_()

def show_error_message(parent, title, message, detailed_text=None):
    """
    نمایش پیام خطا
    
    پارامترها:
        parent: ویجت والد
        title: عنوان پیام
        message: متن پیام
        detailed_text: متن جزئیات (اختیاری)
    """
    msg_box = QMessageBox(parent)
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    msg_box.setIcon(QMessageBox.Critical)
    
    if detailed_text:
        msg_box.setDetailedText(detailed_text)
    
    msg_box.exec_()

def show_warning_message(parent, title, message, detailed_text=None):
    """
    نمایش پیام هشدار
    
    پارامترها:
        parent: ویجت والد
        title: عنوان پیام
        message: متن پیام
        detailed_text: متن جزئیات (اختیاری)
    """
    msg_box = QMessageBox(parent)
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    msg_box.setIcon(QMessageBox.Warning)
    
    if detailed_text:
        msg_box.setDetailedText(detailed_text)
    
    msg_box.exec_()

def get_input_text(parent, title, label, default_text=""):
    """
    دریافت متن از کاربر با استفاده از دیالوگ ورودی
    
    پارامترها:
        parent: ویجت والد
        title: عنوان دیالوگ
        label: برچسب ورودی
        default_text: متن پیش‌فرض
        
    بازگشت:
        tuple: (text, bool) - متن وارد شده و وضعیت تأیید
    """
    text, ok = QInputDialog.getText(parent, title, label, text=default_text)
    return text, ok

def get_save_file_path(parent, title, directory="", filter="", initial_filter=""):
    """
    دریافت مسیر فایل برای ذخیره
    
    پارامترها:
        parent: ویجت والد
        title: عنوان دیالوگ
        directory: دایرکتوری پیش‌فرض
        filter: فیلتر فایل‌ها (مثلا "Excel Files (*.xlsx);;CSV Files (*.csv)")
        initial_filter: فیلتر پیش‌فرض اولیه
        
    بازگشت:
        str: مسیر انتخاب شده (خالی اگر لغو شود)
    """
    options = QFileDialog.Options()
    file_path, _ = QFileDialog.getSaveFileName(
        parent, title, directory, filter, initial_filter, options=options
    )
    return file_path

def get_open_file_path(parent, title, directory="", filter="", initial_filter=""):
    """
    دریافت مسیر فایل برای باز کردن
    
    پارامترها:
        parent: ویجت والد
        title: عنوان دیالوگ
        directory: دایرکتوری پیش‌فرض
        filter: فیلتر فایل‌ها
        initial_filter: فیلتر پیش‌فرض اولیه
        
    بازگشت:
        str: مسیر انتخاب شده (خالی اگر لغو شود)
    """
    options = QFileDialog.Options()
    file_path, _ = QFileDialog.getOpenFileName(
        parent, title, directory, filter, initial_filter, options=options
    )
    return file_path

def qdate_to_string(qdate, format="yyyy-MM-dd"):
    """
    تبدیل QDate به رشته
    
    پارامترها:
        qdate: شیء QDate
        format: قالب تاریخ
        
    بازگشت:
        str: تاریخ به صورت رشته
    """
    if not qdate or not isinstance(qdate, QDate):
        return ""
    return qdate.toString(format)

def string_to_qdate(date_string, format="yyyy-MM-dd"):
    """
    تبدیل رشته به QDate
    
    پارامترها:
        date_string: تاریخ به صورت رشته
        format: قالب تاریخ
        
    بازگشت:
        QDate: شیء QDate
    """
    if not date_string:
        return QDate()
    return QDate.fromString(date_string, format)

def create_progress_dialog(parent, title, label_text, min_value=0, max_value=100, cancellable=True):
    """
    ایجاد دیالوگ پیشرفت
    
    پارامترها:
        parent: ویجت والد
        title: عنوان دیالوگ
        label_text: متن برچسب
        min_value: مقدار حداقل
        max_value: مقدار حداکثر
        cancellable: قابل لغو بودن
        
    بازگشت:
        QProgressDialog: دیالوگ پیشرفت
    """
    progress = QProgressDialog(label_text, "لغو" if cancellable else None, min_value, max_value, parent)
    progress.setWindowTitle(title)
    progress.setWindowModality(Qt.WindowModal)
    progress.setMinimumDuration(500)  # شروع نمایش پس از 500 میلی‌ثانیه
    
    # اگر غیرقابل لغو باشد، دکمه لغو را مخفی می‌کنیم
    if not cancellable:
        progress.setCancelButton(None)
    
    return progress

def apply_stylesheet(widget, style_str):
    """
    اعمال استایل‌شیت به ویجت
    
    پارامترها:
        widget: ویجت مورد نظر
        style_str: رشته استایل‌شیت
    """
    widget.setStyleSheet(style_str)

def create_primary_button(text, slot=None, tooltip=None):
    """
    ایجاد دکمه با سبک اصلی
    
    پارامترها:
        text: متن دکمه
        slot: تابع متصل به سیگنال کلیک (اختیاری)
        tooltip: متن راهنمای ابزار (اختیاری)
        
    بازگشت:
        QPushButton: دکمه ایجاد شده
    """
    button = create_button(text, slot=slot, tooltip=tooltip)
    apply_stylesheet(button, f"""
        QPushButton {{
            background-color: {UI_COLOR_PRIMARY};
            color: {UI_COLOR_WHITE};
            border: none;
            padding: 5px 10px;
            border-radius: 3px;
        }}
        QPushButton:hover {{
            background-color: #3a546d;
        }}
        QPushButton:pressed {{
            background-color: #1e2b39;
        }}
    """)
    return button

def create_secondary_button(text, slot=None, tooltip=None):
    """
    ایجاد دکمه با سبک ثانویه
    
    پارامترها:
        text: متن دکمه
        slot: تابع متصل به سیگنال کلیک (اختیاری)
        tooltip: متن راهنمای ابزار (اختیاری)
        
    بازگشت:
        QPushButton: دکمه ایجاد شده
    """
    button = create_button(text, slot=slot, tooltip=tooltip)
    apply_stylesheet(button, f"""
        QPushButton {{
            background-color: {UI_COLOR_SECONDARY};
            color: {UI_COLOR_WHITE};
            border: none;
            padding: 5px 10px;
            border-radius: 3px;
        }}
        QPushButton:hover {{
            background-color: #435c78;
        }}
        QPushButton:pressed {{
            background-color: #25364a;
        }}
    """)
    return button 