#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ماژول ویجت‌های سفارشی برای رابط کاربری سیستم مدیریت املاک

این ماژول شامل ویجت‌های سفارشی مورد استفاده در رابط کاربری Qt برای نمایش و ویرایش داده‌های املاک است.
"""

import os
import logging
from typing import List, Dict, Any, Optional, Union, Callable
from datetime import datetime, date

from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, 
    QCheckBox, QDateEdit, QTextEdit, QPushButton, QDialog, QVBoxLayout, 
    QHBoxLayout, QFormLayout, QGridLayout, QFrame, QGroupBox, QTabWidget,
    QFileDialog, QMessageBox, QTableView, QAbstractItemView, QHeaderView,
    QStyledItemDelegate, QApplication, QScrollArea, QSizePolicy
)
from PyQt5.QtCore import (
    Qt, QSize, QDate, QDateTime, QRegExp, pyqtSignal, QModelIndex,
    QSortFilterProxyModel, QItemSelectionModel, QLocale
)
from PyQt5.QtGui import (
    QIcon, QPixmap, QRegExpValidator, QFont, QColor, QPalette, QBrush,
    QPainter, QFontMetrics
)

from .filter_models import PropertyFilterProxyModel

# تنظیمات لاگینگ
logger = logging.getLogger(__name__)

# ثابت‌های سراسری
FONT_FAMILY = "Vazir"  # فونت فارسی
PRIMARY_COLOR = QColor(25, 118, 210)  # رنگ اصلی (آبی)
SECONDARY_COLOR = QColor(0, 150, 136)  # رنگ ثانویه (سبز)
ERROR_COLOR = QColor(211, 47, 47)  # رنگ خطا (قرمز)
WARNING_COLOR = QColor(255, 152, 0)  # رنگ هشدار (نارنجی)

# تنظیم لوکیل فارسی
QLocale.setDefault(QLocale(QLocale.Persian, QLocale.Iran))


class StyleHelper:
    """
    کلاس کمکی برای اعمال استایل‌های سفارشی به ویجت‌ها
    """
    
    @staticmethod
    def set_font(widget, bold=False, size=None):
        """
        تنظیم فونت فارسی روی ویجت
        
        Args:
            widget: ویجت هدف
            bold (bool, optional): قلم ضخیم
            size (int, optional): اندازه قلم
        """
        font = QFont(FONT_FAMILY)
        if bold:
            font.setBold(True)
        if size:
            font.setPointSize(size)
        widget.setFont(font)
    
    @staticmethod
    def set_line_edit_style(line_edit, is_required=False, placeholder=None):
        """
        تنظیم استایل ویجت QLineEdit
        
        Args:
            line_edit (QLineEdit): ویجت هدف
            is_required (bool, optional): آیا فیلد اجباری است
            placeholder (str, optional): متن راهنما
        """
        line_edit.setMinimumHeight(30)
        StyleHelper.set_font(line_edit)
        
        if placeholder:
            line_edit.setPlaceholderText(placeholder)
        
        if is_required:
            line_edit.setStyleSheet("""
                QLineEdit {
                    border: 1px solid #ccc;
                    border-radius: 4px;
                    padding: 2px 8px;
                    background-color: #fff8e1;
                }
                QLineEdit:focus {
                    border: 2px solid #1976d2;
                    background-color: white;
                }
            """)
        else:
            line_edit.setStyleSheet("""
                QLineEdit {
                    border: 1px solid #ccc;
                    border-radius: 4px;
                    padding: 2px 8px;
                }
                QLineEdit:focus {
                    border: 2px solid #1976d2;
                }
            """)
    
    @staticmethod
    def set_spin_box_style(spin_box):
        """
        تنظیم استایل ویجت QSpinBox یا QDoubleSpinBox
        
        Args:
            spin_box: ویجت هدف
        """
        spin_box.setMinimumHeight(30)
        StyleHelper.set_font(spin_box)
        
        spin_box.setStyleSheet("""
            QAbstractSpinBox {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 2px 8px;
            }
            QAbstractSpinBox:focus {
                border: 2px solid #1976d2;
            }
            QAbstractSpinBox::up-button, QAbstractSpinBox::down-button {
                width: 20px;
                border-radius: 2px;
            }
        """)
    
    @staticmethod
    def set_combo_box_style(combo_box):
        """
        تنظیم استایل ویجت QComboBox
        
        Args:
            combo_box (QComboBox): ویجت هدف
        """
        combo_box.setMinimumHeight(30)
        StyleHelper.set_font(combo_box)
        
        combo_box.setStyleSheet("""
            QComboBox {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 2px 8px;
                min-width: 100px;
            }
            QComboBox:focus, QComboBox:on {
                border: 2px solid #1976d2;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left-width: 1px;
                border-left-color: #ccc;
                border-left-style: solid;
                border-top-right-radius: 3px;
                border-bottom-right-radius: 3px;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #ccc;
                selection-background-color: #1976d2;
                selection-color: white;
                background-color: white;
            }
        """)
    
    @staticmethod
    def set_check_box_style(check_box):
        """
        تنظیم استایل ویجت QCheckBox
        
        Args:
            check_box (QCheckBox): ویجت هدف
        """
        StyleHelper.set_font(check_box)
        
        check_box.setStyleSheet("""
            QCheckBox {
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
            QCheckBox::indicator:unchecked {
                border: 1px solid #ccc;
                border-radius: 3px;
                background-color: white;
            }
            QCheckBox::indicator:checked {
                border: 1px solid #1976d2;
                border-radius: 3px;
                background-color: #1976d2;
            }
        """)
    
    @staticmethod
    def set_button_style(button, primary=True, icon=None):
        """
        تنظیم استایل ویجت QPushButton
        
        Args:
            button (QPushButton): ویجت هدف
            primary (bool, optional): آیا دکمه اصلی است
            icon (str, optional): مسیر آیکون
        """
        button.setMinimumHeight(36)
        StyleHelper.set_font(button, bold=True)
        
        if icon:
            button.setIcon(QIcon(icon))
            button.setIconSize(QSize(20, 20))
        
        if primary:
            button.setStyleSheet("""
                QPushButton {
                    background-color: #1976d2;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 6px 16px;
                }
                QPushButton:hover {
                    background-color: #1565c0;
                }
                QPushButton:pressed {
                    background-color: #0d47a1;
                }
                QPushButton:disabled {
                    background-color: #bbdefb;
                    color: #e1f5fe;
                }
            """)
        else:
            button.setStyleSheet("""
                QPushButton {
                    background-color: white;
                    color: #1976d2;
                    border: 1px solid #1976d2;
                    border-radius: 4px;
                    padding: A6px 16px;
                }
                QPushButton:hover {
                    background-color: #e3f2fd;
                }
                QPushButton:pressed {
                    background-color: #bbdefb;
                }
                QPushButton:disabled {
                    border-color: #bbdefb;
                    color: #bbdefb;
                }
            """)
    
    @staticmethod
    def set_table_view_style(table_view):
        """
        تنظیم استایل ویجت QTableView
        
        Args:
            table_view (QTableView): ویجت هدف
        """
        table_view.setAlternatingRowColors(True)
        table_view.setSelectionBehavior(QAbstractItemView.SelectRows)
        table_view.setSelectionMode(QAbstractItemView.SingleSelection)
        table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        table_view.horizontalHeader().setStretchLastSection(True)
        table_view.verticalHeader().setVisible(False)
        
        # تنظیم فونت سرستون‌ها
        header_font = QFont(FONT_FAMILY)
        header_font.setBold(True)
        table_view.horizontalHeader().setFont(header_font)
        
        # تنظیم استایل با CSS
        table_view.setStyleSheet("""
            QTableView {
                border: 1px solid #ccc;
                border-radius: 4px;
                selection-background-color: #bbdefb;
                selection-color: black;
            }
            QTableView::item {
                padding: 4px;
                border-bottom: 1px solid #eee;
            }
            QHeaderView::section {
                background-color: #f5f5f5;
                padding: 6px;
                border: none;
                border-right: 1px solid #ddd;
                border-bottom: 1px solid #ddd;
            }
        """)
    
    @staticmethod
    def set_group_box_style(group_box, title=None):
        """
        تنظیم استایل ویجت QGroupBox
        
        Args:
            group_box (QGroupBox): ویجت هدف
            title (str, optional): عنوان گروه
        """
        if title:
            group_box.setTitle(title)
        
        title_font = QFont(FONT_FAMILY)
        title_font.setBold(True)
        group_box.setFont(title_font)
        
        group_box.setStyleSheet("""
            QGroupBox {
                border: 1px solid #ccc;
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 8px;
                background-color: white;
                color: #1976d2;
            }
        """)
    
    @staticmethod
    def set_tab_widget_style(tab_widget):
        """
        تنظیم استایل ویجت QTabWidget
        
        Args:
            tab_widget (QTabWidget): ویجت هدف
        """
        tab_font = QFont(FONT_FAMILY)
        tab_font.setBold(True)
        tab_widget.setFont(tab_font)
        
        tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 8px;
            }
            QTabBar::tab {
                background-color: #f5f5f5;
                border: 1px solid #ccc;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: none;
                border-top: 2px solid #1976d2;
            }
            QTabBar::tab:hover:!selected {
                background-color: #e3f2fd;
            }
        """)


class FormField(QWidget):
    """
    کلاس پایه برای فیلدهای فرم
    این کلاس یک ویجت ترکیبی از برچسب و ورودی را ایجاد می‌کند
    """
    
    valueChanged = pyqtSignal(object)  # سیگنال تغییر مقدار
    
    def __init__(self, label_text, parent=None, is_required=False, tooltip=None):
        """
        مقداردهی اولیه
        
        Args:
            label_text (str): متن برچسب
            parent (QWidget, optional): ویجت والد
            is_required (bool, optional): آیا فیلد اجباری است
            tooltip (str, optional): متن راهنما
        """
        super(FormField, self).__init__(parent)
        
        self.is_required = is_required
        self._value = None
        self._input_widget = None
        
        # ایجاد layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(4)
        
        # ایجاد برچسب
        self.label = QLabel(label_text, self)
        StyleHelper.set_font(self.label, bold=True)
        
        if is_required:
            self.label.setText(f"{label_text} *")
            self.label.setStyleSheet("color: #d32f2f;")
        
        self.layout.addWidget(self.label)
        
        # تنظیم راهنما
        if tooltip:
            self.setToolTip(tooltip)
    
    def _create_input_widget(self):
        """
        ایجاد ویجت ورودی - باید توسط کلاس‌های فرزند پیاده‌سازی شود
        """
        raise NotImplementedError("Subclasses must implement _create_input_widget()")
    
    def setup_widget(self):
        """
        راه‌اندازی ویجت ورودی
        """
        self._input_widget = self._create_input_widget()
        self.layout.addWidget(self._input_widget)
    
    def getValue(self):
        """
        دریافت مقدار فیلد
        
        Returns:
            object: مقدار فیلد
        """
        return self._value
    
    def setValue(self, value):
        """
        تنظیم مقدار فیلد
        
        Args:
            value: مقدار جدید
        """
        self._value = value
        self._update_input_widget()
    
    def _update_input_widget(self):
        """
        به‌روزرسانی ویجت ورودی با مقدار فعلی - باید توسط کلاس‌های فرزند پیاده‌سازی شود
        """
        raise NotImplementedError("Subclasses must implement _update_input_widget()")
    
    def setEnabled(self, enabled):
        """
        فعال/غیرفعال کردن فیلد
        
        Args:
            enabled (bool): وضعیت فعال بودن
        """
        super(FormField, self).setEnabled(enabled)
        if self._input_widget:
            self._input_widget.setEnabled(enabled)
    
    def clear(self):
        """
        پاک کردن مقدار فیلد
        """
        self._value = None
        self._update_input_widget()
    
    def isValid(self):
        """
        بررسی معتبر بودن مقدار
        
        Returns:
            bool: آیا مقدار معتبر است
        """
        if self.is_required and (self._value is None or self._value == ""):
            return False
        return True
    
    def showError(self, show=True):
        """
        نمایش حالت خطا
        
        Args:
            show (bool, optional): آیا خطا نمایش داده شود
        """
        if show:
            self.label.setStyleSheet("color: #d32f2f;")
            if hasattr(self._input_widget, 'setStyleSheet'):
                self._input_widget.setStyleSheet("""
                    border: 2px solid #d32f2f;
                    border-radius: 4px;
                    background-color: #ffebee;
                    padding: 2px 8px;
                """)
        else:
            if self.is_required:
                self.label.setStyleSheet("color: #d32f2f;")
            else:
                self.label.setStyleSheet("")
            
            # بازگرداندن استایل پیش‌فرض
            if hasattr(self._input_widget, 'setStyleSheet'):
                self._input_widget.setStyleSheet("")


class TextFormField(FormField):
    """
    فیلد فرم برای ورود متن
    """
    
    def __init__(self, label_text, parent=None, is_required=False, tooltip=None, 
                 placeholder=None, max_length=None, validator=None):
        """
        مقداردهی اولیه
        
        Args:
            label_text (str): متن برچسب
            parent (QWidget, optional): ویجت والد
            is_required (bool, optional): آیا فیلد اجباری است
            tooltip (str, optional): متن راهنما
            placeholder (str, optional): متن راهنمای داخل فیلد
            max_length (int, optional): حداکثر طول متن
            validator (QValidator, optional): اعتبارسنج ورودی
        """
        super(TextFormField, self).__init__(label_text, parent, is_required, tooltip)
        
        self.placeholder = placeholder
        self.max_length = max_length
        self.validator = validator
        
        self.setup_widget()
    
    def _create_input_widget(self):
        """
        ایجاد ویجت ورودی
        
        Returns:
            QLineEdit: ویجت ورودی متن
        """
        input_widget = QLineEdit(self)
        
        StyleHelper.set_line_edit_style(input_widget, self.is_required, self.placeholder)
        
        if self.max_length:
            input_widget.setMaxLength(self.max_length)
        
        if self.validator:
            input_widget.setValidator(self.validator)
        
        input_widget.textChanged.connect(self._on_text_changed)
        
        return input_widget
    
    def _on_text_changed(self, text):
        """
        رویداد تغییر متن
        
        Args:
            text (str): متن جدید
        """
        self._value = text if text else None
        self.valueChanged.emit(self._value)
    
    def _update_input_widget(self):
        """
        به‌روزرسانی ویجت ورودی با مقدار فعلی
        """
        self._input_widget.setText(self._value if self._value is not None else "")


class NumberFormField(FormField):
    """
    فیلد فرم برای ورود اعداد
    """
    
    def __init__(self, label_text, parent=None, is_required=False, tooltip=None,
                 min_value=0, max_value=1000000000, decimals=0, suffix=None):
        """
        مقداردهی اولیه
        
        Args:
            label_text (str): متن برچسب
            parent (QWidget, optional): ویجت والد
            is_required (bool, optional): آیا فیلد اجباری است
            tooltip (str, optional): متن راهنما
            min_value (int/float, optional): حداقل مقدار
            max_value (int/float, optional): حداکثر مقدار
            decimals (int, optional): تعداد اعشار
            suffix (str, optional): پسوند (مثلاً "متر")
        """
        super(NumberFormField, self).__init__(label_text, parent, is_required, tooltip)
        
        self.min_value = min_value
        self.max_value = max_value
        self.decimals = decimals
        self.suffix = suffix
        
        self.setup_widget()
    
    def _create_input_widget(self):
        """
        ایجاد ویجت ورودی
        
        Returns:
            QDoubleSpinBox/QSpinBox: ویجت ورودی عدد
        """
        if self.decimals > 0:
            input_widget = QDoubleSpinBox(self)
            input_widget.setDecimals(self.decimals)
        else:
            input_widget = QSpinBox(self)
        
        input_widget.setMinimum(self.min_value)
        input_widget.setMaximum(self.max_value)
        
        if self.suffix:
            input_widget.setSuffix(f" {self.suffix}")
        
        StyleHelper.set_spin_box_style(input_widget)
        
        input_widget.valueChanged.connect(self._on_value_changed)
        
        return input_widget
    
    def _on_value_changed(self, value):
        """
        رویداد تغییر مقدار
        
        Args:
            value (int/float): مقدار جدید
        """
        self._value = value
        self.valueChanged.emit(self._value)
    
    def _update_input_widget(self):
        """
        به‌روزرسانی ویجت ورودی با مقدار فعلی
        """
        if self._value is not None:
            self._input_widget.setValue(self._value)
        else:
            self._input_widget.setValue(self.min_value)


class DateFormField(FormField):
    """
    فیلد فرم برای ورود تاریخ
    """
    
    def __init__(self, label_text, parent=None, is_required=False, tooltip=None,
                 min_date=None, max_date=None):
        """
        مقداردهی اولیه
        
        Args:
            label_text (str): متن برچسب
            parent (QWidget, optional): ویجت والد
            is_required (bool, optional): آیا فیلد اجباری است
            tooltip (str, optional): متن راهنما
            min_date (QDate/date, optional): حداقل تاریخ
            max_date (QDate/date, optional): حداکثر تاریخ
        """
        super(DateFormField, self).__init__(label_text, parent, is_required, tooltip)
        
        # تبدیل تاریخ‌های پایتون به QDate
        if isinstance(min_date, date):
            self.min_date = QDate(min_date.year, min_date.month, min_date.day)
        else:
            self.min_date = min_date or QDate.currentDate().addYears(-100)
        
        if isinstance(max_date, date):
            self.max_date = QDate(max_date.year, max_date.month, max_date.day)
        else:
            self.max_date = max_date or QDate.currentDate().addYears(100)
        
        self.setup_widget()
    
    def _create_input_widget(self):
        """
        ایجاد ویجت ورودی
        
        Returns:
            QDateEdit: ویجت ورودی تاریخ
        """
        input_widget = QDateEdit(self)
        
        input_widget.setMinimumHeight(30)
        StyleHelper.set_font(input_widget)
        
        input_widget.setMinimumDate(self.min_date)
        input_widget.setMaximumDate(self.max_date)
        input_widget.setDisplayFormat("yyyy/MM/dd")
        input_widget.setCalendarPopup(True)
        
        input_widget.setStyleSheet("""
            QDateEdit {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 2px 8px;
            }
            QDateEdit:focus {
                border: 2px solid #1976d2;
            }
            QDateEdit::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left-width: 1px;
                border-left-color: #ccc;
                border-left-style: solid;
                border-top-right-radius: 3px;
                border-bottom-right-radius: 3px;
            }
        """)
        
        input_widget.dateChanged.connect(self._on_date_changed)
        
        return input_widget
    
    def _on_date_changed(self, date):
        """
        رویداد تغییر تاریخ
        
        Args:
            date (QDate): تاریخ جدید
        """
        # تبدیل QDate به تاریخ پایتون
        self._value = date.toPyDate()
        self.valueChanged.emit(self._value)
    
    def _update_input_widget(self):
        """
        به‌روزرسانی ویجت ورودی با مقدار فعلی
        """
        if self._value is not None:
            if isinstance(self._value, date):
                q_date = QDate(self._value.year, self._value.month, self._value.day)
                self._input_widget.setDate(q_date)
            elif isinstance(self._value, QDate):
                self._input_widget.setDate(self._value)
            elif isinstance(self._value, str):
                try:
                    d = datetime.strptime(self._value, "%Y-%m-%d").date()
                    q_date = QDate(d.year, d.month, d.day)
                    self._input_widget.setDate(q_date)
                except:
                    self._input_widget.setDate(QDate.currentDate())
        else:
            self._input_widget.setDate(QDate.currentDate())


class ComboBoxFormField(FormField):
    """
    فیلد فرم برای انتخاب از لیست
    """
    
    def __init__(self, label_text, parent=None, is_required=False, tooltip=None,
                 items=None, editable=False):
        """
        مقداردهی اولیه
        
        Args:
            label_text (str): متن برچسب
            parent (QWidget, optional): ویجت والد
            is_required (bool, optional): آیا فیلد اجباری است
            tooltip (str, optional): متن راهنما
            items (List/Dict, optional): آیتم‌های لیست
            editable (bool, optional): آیا امکان ویرایش وجود دارد
        """
        super(ComboBoxFormField, self).__init__(label_text, parent, is_required, tooltip)
        
        self.items = items or []
        self.editable = editable
        self._items_dict = {}
        
        self.setup_widget()
    
    def _create_input_widget(self):
        """
        ایجاد ویجت ورودی
        
        Returns:
            QComboBox: ویجت کومبوباکس
        """
        input_widget = QComboBox(self)
        
        StyleHelper.set_combo_box_style(input_widget)
        
        input_widget.setEditable(self.editable)
        
        # افزودن آیتم‌ها
        self._setup_items(input_widget)
        
        input_widget.currentIndexChanged.connect(self._on_index_changed)
        if self.editable:
            input_widget.editTextChanged.connect(self._on_text_changed)
        
        return input_widget
    
    def _setup_items(self, combo_box):
        """
        راه‌اندازی آیتم‌های کومبوباکس
        
        Args:
            combo_box (QComboBox): کومبوباکس
        """
        combo_box.clear()
        self._items_dict = {}
        
        # افزودن آیتم خالی
        if not self.is_required:
            combo_box.addItem("", None)
        
        # افزودن آیتم‌ها
        if isinstance(self.items, dict):
            # آیتم‌ها به صورت دیکشنری {key: display_text}
            for key, text in self.items.items():
                combo_box.addItem(text, key)
                self._items_dict[key] = text
        elif isinstance(self.items, list):
            # آیتم‌ها به صورت لیست [item1, item2, ...]
            for item in self.items:
                if isinstance(item, (list, tuple)) and len(item) >= 2:
                    # آیتم‌ها به صورت [(key1, text1), (key2, text2), ...]
                    key, text = item[0], item[1]
                    combo_box.addItem(text, key)
                    self._items_dict[key] = text
                else:
                    # آیتم‌ها به صورت [item1, item2, ...]
                    combo_box.addItem(str(item), item)
                    self._items_dict[item] = str(item)
    
    def setItems(self, items):
        """
        تنظیم آیتم‌های جدید
        
        Args:
            items (List/Dict): آیتم‌های جدید
        """
        self.items = items or []
        self._setup_items(self._input_widget)
    
    def _on_index_changed(self, index):
        """
        رویداد تغییر اندیس انتخاب شده
        
        Args:
            index (int): اندیس جدید
        """
        if index >= 0:
            self._value = self._input_widget.itemData(index)
            self.valueChanged.emit(self._value)
    
    def _on_text_changed(self, text):
        """
        رویداد تغییر متن (در حالت editable)
        
        Args:
            text (str): متن جدید
        """
        self._value = text if text else None
        self.valueChanged.emit(self._value)
    
    def _update_input_widget(self):
        """
        به‌روزرسانی ویجت ورودی با مقدار فعلی
        """
        if self._value is not None:
            # جستجوی اندیس مطابق با مقدار
            index = self._input_widget.findData(self._value)
            if index >= 0:
                self._input_widget.setCurrentIndex(index)
            elif self.editable and isinstance(self._value, str):
                self._input_widget.setEditText(self._value)
            else:
                self._input_widget.setCurrentIndex(0)
        else:
            self._input_widget.setCurrentIndex(0)


class CheckBoxFormField(FormField):
    """
    فیلد فرم برای چک‌باکس
    """
    
    def __init__(self, label_text, parent=None, tooltip=None, check_text=None):
        """
        مقداردهی اولیه
        
        Args:
            label_text (str): متن برچسب
            parent (QWidget, optional): ویجت والد
            tooltip (str, optional): متن راهنما
            check_text (str, optional): متن چک‌باکس
        """
        super(CheckBoxFormField, self).__init__(label_text, parent, False, tooltip)
        
        self.check_text = check_text
        
        self.setup_widget()
    
    def _create_input_widget(self):
        """
        ایجاد ویجت ورودی
        
        Returns:
            QCheckBox: ویجت چک‌باکس
        """
        input_widget = QCheckBox(self.check_text, self)
        
        StyleHelper.set_check_box_style(input_widget)
        
        input_widget.stateChanged.connect(self._on_state_changed)
        
        return input_widget
    
    def _on_state_changed(self, state):
        """
        رویداد تغییر وضعیت
        
        Args:
            state (int): وضعیت جدید
        """
        self._value = (state == Qt.Checked)
        self.valueChanged.emit(self._value)
    
    def _update_input_widget(self):
        """
        به‌روزرسانی ویجت ورودی با مقدار فعلی
        """
        if self._value is not None:
            self._input_widget.setChecked(self._value)
        else:
            self._input_widget.setChecked(False)


class TextAreaFormField(FormField):
    """
    فیلد فرم برای ورود متن چند خطی
    """
    
    def __init__(self, label_text, parent=None, is_required=False, tooltip=None,
                 placeholder=None, max_length=None):
        """
        مقداردهی اولیه
        
        Args:
            label_text (str): متن برچسب
            parent (QWidget, optional): ویجت والد
            is_required (bool, optional): آیا فیلد اجباری است
            tooltip (str, optional): متن راهنما
            placeholder (str, optional): متن راهنمای داخل فیلد
            max_length (int, optional): حداکثر طول متن
        """
        super(TextAreaFormField, self).__init__(label_text, parent, is_required, tooltip)
        
        self.placeholder = placeholder
        self.max_length = max_length
        
        self.setup_widget()
    
    def _create_input_widget(self):
        """
        ایجاد ویجت ورودی
        
        Returns:
            QTextEdit: ویجت ویرایش متن چند خطی
        """
        input_widget = QTextEdit(self)
        
        input_widget.setMinimumHeight(80)
        StyleHelper.set_font(input_widget)
        
        if self.placeholder:
            input_widget.setPlaceholderText(self.placeholder)
        
        input_widget.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 4px 8px;
            }
            QTextEdit:focus {
                border: 2px solid #1976d2;
            }
        """)
        
        input_widget.textChanged.connect(self._on_text_changed)
        
        return input_widget
    
    def _on_text_changed(self):
        """
        رویداد تغییر متن
        """
        text = self._input_widget.toPlainText()
        
        # اعمال محدودیت طول
        if self.max_length and len(text) > self.max_length:
            cursor = self._input_widget.textCursor()
            cursor_pos = cursor.position()
            text = text[:self.max_length]
            self._input_widget.setPlainText(text)
            if cursor_pos <= self.max_length:
                cursor.setPosition(cursor_pos)
                self._input_widget.setTextCursor(cursor)
        
        self._value = text if text else None
        self.valueChanged.emit(self._value)
    
    def _update_input_widget(self):
        """
        به‌روزرسانی ویجت ورودی با مقدار فعلی
        """
        self._input_widget.setPlainText(self._value if self._value is not None else "")


class PropertyFormDialog(QDialog):
    """
    دیالوگ فرم پایه برای ثبت و ویرایش ملک
    """
    
    def __init__(self, parent=None, property_type="residential", edit_mode=False):
        """
        مقداردهی اولیه
        
        Args:
            parent (QWidget, optional): ویجت والد
            property_type (str, optional): نوع ملک (residential, commercial, land)
            edit_mode (bool, optional): حالت ویرایش
        """
        super(PropertyFormDialog, self).__init__(parent)
        
        self.property_type = property_type
        self.edit_mode = edit_mode
        self.property_data = {}
        self.result_data = {}
        self.fields = {}
        
        # عنوان دیالوگ
        property_type_map = {
            "residential": "مسکونی",
            "commercial": "تجاری",
            "land": "زمین"
        }
        
        mode_text = "ویرایش" if edit_mode else "ثبت"
        type_text = property_type_map.get(property_type, property_type)
        
        self.setWindowTitle(f"{mode_text} ملک {type_text}")
        self.setMinimumWidth(600)
        
        # ایجاد ساختار دیالوگ
        self._setup_ui()
    
    def _setup_ui(self):
        """
        راه‌اندازی رابط کاربری
        """
        # ایجاد طرح‌بندی اصلی
        main_layout = QVBoxLayout(self)
        
        # ایجاد محتوا
        content_widget = QWidget(self)
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # منطقه قابل اسکرول
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(content_widget)
        
        # افزودن فیلدها
        self._create_form_fields(content_layout)
        
        # افزودن دکمه‌ها
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_button = QPushButton("انصراف", self)
        StyleHelper.set_button_style(self.cancel_button, primary=False)
        self.cancel_button.clicked.connect(self.reject)
        
        save_text = "ذخیره تغییرات" if self.edit_mode else "ثبت ملک"
        self.save_button = QPushButton(save_text, self)
        StyleHelper.set_button_style(self.save_button, primary=True)
        self.save_button.clicked.connect(self._on_save)
        
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.save_button)
        
        # اضافه کردن به چیدمان اصلی
        main_layout.addWidget(scroll_area)
        main_layout.addLayout(button_layout)
    
    def _create_form_fields(self, layout):
        """
        ایجاد فیلدهای فرم - باید توسط کلاس‌های فرزند پیاده‌سازی شود
        
        Args:
            layout (QLayout): طرح‌بندی محتوا
        """
        raise NotImplementedError("Subclasses must implement _create_form_fields()")
    
    def set_property_data(self, data):
        """
        تنظیم داده‌های ملک
        
        Args:
            data (dict): داده‌های ملک
        """
        self.property_data = data or {}
        
        # پر کردن فیلدها با داده‌های موجود
        for field_name, field_widget in self.fields.items():
            if field_name in self.property_data:
                field_widget.setValue(self.property_data[field_name])
    
    def _validate_form(self):
        """
        اعتبارسنجی فرم
        
        Returns:
            bool: آیا فرم معتبر است
        """
        is_valid = True
        
        for field_name, field_widget in self.fields.items():
            if not field_widget.isValid():
                field_widget.showError(True)
                is_valid = False
            else:
                field_widget.showError(False)
        
        return is_valid
    
    def _collect_form_data(self):
        """
        جمع‌آوری داده‌های فرم
        
        Returns:
            dict: داده‌های جمع‌آوری شده
        """
        form_data = {}
        
        for field_name, field_widget in self.fields.items():
            value = field_widget.getValue()
            form_data[field_name] = value
        
        return form_data
    
    def _on_save(self):
        """
        رویداد کلیک بر روی دکمه ذخیره
        """
        if self._validate_form():
            self.result_data = self._collect_form_data()
            self.accept()
    
    def get_result(self):
        """
        دریافت نتیجه دیالوگ
        
        Returns:
            dict: داده‌های جمع‌آوری شده
        """
        return self.result_data


class ResidentialPropertyFormDialog(PropertyFormDialog):
    """
    دیالوگ فرم ثبت و ویرایش املاک مسکونی
    """
    
    def __init__(self, parent=None, edit_mode=False, deal_type=1):
        """
        مقداردهی اولیه
        
        Args:
            parent (QWidget, optional): ویجت والد
            edit_mode (bool, optional): حالت ویرایش
            deal_type (int, optional): نوع معامله (1: فروش، 2: اجاره)
        """
        super(ResidentialPropertyFormDialog, self).__init__(
            parent, "residential", edit_mode
        )
        
        self.deal_type = deal_type
        self.setWindowTitle(f"{'ویرایش' if edit_mode else 'ثبت'} ملک مسکونی برای {'فروش' if deal_type == 1 else 'اجاره'}")
    
    def _create_form_fields(self, layout):
        """
        ایجاد فیلدهای فرم
        
        Args:
            layout (QLayout): طرح‌بندی محتوا
        """
        # طرح‌بندی فرم
        form_layout = QFormLayout()
        form_layout.setSpacing(16)
        
        # گروه‌بندی اطلاعات اصلی
        main_info_group = QGroupBox("اطلاعات اصلی ملک", self)
        StyleHelper.set_group_box_style(main_info_group)
        main_info_layout = QFormLayout(main_info_group)
        main_info_layout.setSpacing(16)
        
        # منطقه
        district_field = TextFormField("منطقه", self, True, "منطقه یا ناحیه ملک را وارد کنید")
        self.fields["district"] = district_field
        main_info_layout.addRow("", district_field)
        
        # آدرس
        address_field = TextAreaFormField("آدرس", self, True, "آدرس کامل ملک را وارد کنید")
        self.fields["address"] = address_field
        main_info_layout.addRow("", address_field)
        
        # سن بنا
        age_field = NumberFormField("سن بنا", self, True, "سن بنا بر حسب سال",
                                     min_value=0, max_value=100, suffix="سال")
        self.fields["age"] = age_field
        main_info_layout.addRow("", age_field)
        
        # متراژ
        area_field = NumberFormField("متراژ", self, True, "متراژ کل ملک بر حسب متر مربع",
                                     min_value=0, max_value=10000, suffix="متر مربع")
        self.fields["area"] = area_field
        main_info_layout.addRow("", area_field)
        
        # تعداد اتاق‌خواب
        bedrooms_field = NumberFormField("تعداد اتاق‌خواب", self, True, "تعداد اتاق‌خواب‌های ملک",
                                         min_value=0, max_value=10)
        self.fields["bedrooms"] = bedrooms_field
        main_info_layout.addRow("", bedrooms_field)
        
        # طبقه
        floor_field = NumberFormField("طبقه", self, False, "شماره طبقه (0 برای همکف، -1 برای زیرزمین)",
                                     min_value=-2, max_value=100)
        self.fields["floor"] = floor_field
        main_info_layout.addRow("", floor_field)
        
        # گروه‌بندی ویژگی‌ها
        features_group = QGroupBox("ویژگی‌های ملک", self)
        StyleHelper.set_group_box_style(features_group)
        features_layout = QVBoxLayout(features_group)
        
        # آسانسور
        elevator_field = CheckBoxFormField("آسانسور", self, "آیا ساختمان آسانسور دارد؟", "دارای آسانسور")
        self.fields["hasElevator"] = elevator_field
        features_layout.addWidget(elevator_field)
        
        # پارکینگ
        parking_field = CheckBoxFormField("پارکینگ", self, "آیا ملک پارکینگ دارد؟", "دارای پارکینگ")
        self.fields["hasParking"] = parking_field
        features_layout.addWidget(parking_field)
        
        # انباری
        storage_field = CheckBoxFormField("انباری", self, "آیا ملک انباری دارد؟", "دارای انباری")
        self.fields["hasStorage"] = storage_field
        features_layout.addWidget(storage_field)
        
        # گروه‌بندی قیمت‌گذاری
        pricing_group = QGroupBox("اطلاعات قیمت‌گذاری", self)
        StyleHelper.set_group_box_style(pricing_group)
        pricing_layout = QFormLayout(pricing_group)
        pricing_layout.setSpacing(16)
        
        # قیمت فروش (فقط در حالت فروش)
        if self.deal_type == 1:
            selling_price_field = NumberFormField("قیمت فروش", self, True, "قیمت فروش بر حسب تومان",
                                                 min_value=0, max_value=1000000000000, suffix="تومان")
            self.fields["sellingPrice"] = selling_price_field
            pricing_layout.addRow("", selling_price_field)
        
        # مبلغ رهن (فقط در حالت اجاره)
        if self.deal_type == 2:
            mortgage_field = NumberFormField("مبلغ رهن", self, False, "مبلغ رهن بر حسب تومان",
                                            min_value=0, max_value=1000000000000, suffix="تومان")
            self.fields["mortgageAmount"] = mortgage_field
            pricing_layout.addRow("", mortgage_field)
            
            # مبلغ اجاره ماهانه (فقط در حالت اجاره)
            rent_field = NumberFormField("اجاره ماهانه", self, True, "مبلغ اجاره ماهانه بر حسب تومان",
                                        min_value=0, max_value=1000000000, suffix="تومان")
            self.fields["monthlyRentAmount"] = rent_field
            pricing_layout.addRow("", rent_field)
        
        # اضافه کردن گروه‌ها به طرح‌بندی اصلی
        layout.addWidget(main_info_group)
        layout.addWidget(features_group)
        layout.addWidget(pricing_group)
        
        # اضافه کردن فیلد توضیحات
        description_field = TextAreaFormField("توضیحات", self, False, "توضیحات اضافی در مورد ملک",
                                             placeholder="توضیحات خود را اینجا وارد کنید...")
        self.fields["description"] = description_field
        layout.addWidget(description_field)
        
        # تنظیم اسکرول به بالا
        layout.addStretch()
    
    def _validate_form(self):
        """
        اعتبارسنجی اختصاصی فرم
        
        Returns:
            bool: آیا فرم معتبر است
        """
        is_valid = super(ResidentialPropertyFormDialog, self)._validate_form()
        
        # بررسی‌های اضافی خاص املاک مسکونی
        if is_valid and self.deal_type == 2:
            # در حالت اجاره، یا رهن یا اجاره ماهانه باید مقدار داشته باشد
            mortgage_field = self.fields.get("mortgageAmount")
            rent_field = self.fields.get("monthlyRentAmount")
            
            mortgage_value = mortgage_field.getValue() if mortgage_field else 0
            rent_value = rent_field.getValue() if rent_field else 0
            
            if (mortgage_value is None or mortgage_value == 0) and (rent_value is None or rent_value == 0):
                QMessageBox.warning(self, "خطای اعتبارسنجی", 
                                   "حداقل یکی از مقادیر رهن یا اجاره ماهانه باید بیشتر از صفر باشد.")
                return False
        
        return is_valid


class CommercialPropertyFormDialog(PropertyFormDialog):
    """
    دیالوگ فرم ثبت و ویرایش املاک تجاری
    """
    
    def __init__(self, parent=None, edit_mode=False, deal_type=1):
        """
        مقداردهی اولیه
        
        Args:
            parent (QWidget, optional): ویجت والد
            edit_mode (bool, optional): حالت ویرایش
            deal_type (int, optional): نوع معامله (1: فروش، 2: اجاره)
        """
        super(CommercialPropertyFormDialog, self).__init__(
            parent, "commercial", edit_mode
        )
        
        self.deal_type = deal_type
        self.setWindowTitle(f"{'ویرایش' if edit_mode else 'ثبت'} ملک تجاری برای {'فروش' if deal_type == 1 else 'اجاره'}")
    
    def _create_form_fields(self, layout):
        """
        ایجاد فیلدهای فرم
        
        Args:
            layout (QLayout): طرح‌بندی محتوا
        """
        # طرح‌بندی فرم
        form_layout = QFormLayout()
        form_layout.setSpacing(16)
        
        # گروه‌بندی اطلاعات اصلی
        main_info_group = QGroupBox("اطلاعات اصلی ملک", self)
        StyleHelper.set_group_box_style(main_info_group)
        main_info_layout = QFormLayout(main_info_group)
        main_info_layout.setSpacing(16)
        
        # منطقه
        district_field = TextFormField("منطقه", self, True, "منطقه یا ناحیه ملک را وارد کنید")
        self.fields["district"] = district_field
        main_info_layout.addRow("", district_field)
        
        # آدرس
        address_field = TextAreaFormField("آدرس", self, True, "آدرس کامل ملک را وارد کنید")
        self.fields["address"] = address_field
        main_info_layout.addRow("", address_field)
        
        # نوع کاربری
        property_types = [
            "مغازه", "دفتر کار", "انبار", "سوله صنعتی", "واحد اداری", "مجتمع تجاری", "سایر"
        ]
        type_field = ComboBoxFormField("نوع کاربری", self, True, "نوع کاربری ملک تجاری را انتخاب کنید", 
                                      items=property_types)
        self.fields["commercialType"] = type_field
        main_info_layout.addRow("", type_field)
        
        # سن بنا
        age_field = NumberFormField("سن بنا", self, True, "سن بنا بر حسب سال",
                                     min_value=0, max_value=100, suffix="سال")
        self.fields["age"] = age_field
        main_info_layout.addRow("", age_field)
        
        # متراژ
        area_field = NumberFormField("متراژ", self, True, "متراژ کل ملک بر حسب متر مربع",
                                     min_value=0, max_value=100000, suffix="متر مربع")
        self.fields["area"] = area_field
        main_info_layout.addRow("", area_field)
        
        # طبقه
        floor_field = NumberFormField("طبقه", self, False, "شماره طبقه (0 برای همکف، -1 برای زیرزمین)",
                                     min_value=-2, max_value=100)
        self.fields["floor"] = floor_field
        main_info_layout.addRow("", floor_field)
        
        # متراژ بر
        frontage_field = NumberFormField("متراژ بر", self, False, "متراژ بر ملک به متر",
                                        min_value=0, max_value=1000, suffix="متر")
        self.fields["frontage"] = frontage_field
        main_info_layout.addRow("", frontage_field)
        
        # ارتفاع سقف
        height_field = NumberFormField("ارتفاع سقف", self, False, "ارتفاع سقف به متر",
                                      min_value=0, max_value=20, decimals=2, suffix="متر")
        self.fields["ceilingHeight"] = height_field
        main_info_layout.addRow("", height_field)
        
        # گروه‌بندی ویژگی‌ها
        features_group = QGroupBox("ویژگی‌های ملک", self)
        StyleHelper.set_group_box_style(features_group)
        features_layout = QVBoxLayout(features_group)
        
        # آسانسور
        elevator_field = CheckBoxFormField("آسانسور", self, "آیا ساختمان آسانسور دارد؟", "دارای آسانسور")
        self.fields["hasElevator"] = elevator_field
        features_layout.addWidget(elevator_field)
        
        # پارکینگ
        parking_field = CheckBoxFormField("پارکینگ", self, "آیا ملک پارکینگ دارد؟", "دارای پارکینگ")
        self.fields["hasParking"] = parking_field
        features_layout.addWidget(parking_field)
        
        # انباری
        storage_field = CheckBoxFormField("انبار", self, "آیا ملک انبار دارد؟", "دارای انبار")
        self.fields["hasStorage"] = storage_field
        features_layout.addWidget(storage_field)
        
        # سرویس بهداشتی مستقل
        bathroom_field = CheckBoxFormField("سرویس بهداشتی", self, "آیا ملک سرویس بهداشتی مستقل دارد؟", "دارای سرویس بهداشتی مستقل")
        self.fields["hasBathroom"] = bathroom_field
        features_layout.addWidget(bathroom_field)
        
        # ویترین
        vitrine_field = CheckBoxFormField("ویترین", self, "آیا ملک دارای ویترین است؟", "دارای ویترین")
        self.fields["hasVitrine"] = vitrine_field
        features_layout.addWidget(vitrine_field)
        
        # گروه‌بندی قیمت‌گذاری
        pricing_group = QGroupBox("اطلاعات قیمت‌گذاری", self)
        StyleHelper.set_group_box_style(pricing_group)
        pricing_layout = QFormLayout(pricing_group)
        pricing_layout.setSpacing(16)
        
        # قیمت فروش (فقط در حالت فروش)
        if self.deal_type == 1:
            selling_price_field = NumberFormField("قیمت فروش", self, True, "قیمت فروش بر حسب تومان",
                                                 min_value=0, max_value=1000000000000, suffix="تومان")
            self.fields["sellingPrice"] = selling_price_field
            pricing_layout.addRow("", selling_price_field)
            
            # قیمت هر متر مربع (اختیاری)
            price_per_meter_field = NumberFormField("قیمت هر متر مربع", self, False, "قیمت هر متر مربع بر حسب تومان",
                                                  min_value=0, max_value=1000000000, suffix="تومان")
            self.fields["pricePerMeter"] = price_per_meter_field
            pricing_layout.addRow("", price_per_meter_field)
        
        # مبلغ رهن (فقط در حالت اجاره)
        if self.deal_type == 2:
            mortgage_field = NumberFormField("مبلغ رهن", self, False, "مبلغ رهن بر حسب تومان",
                                            min_value=0, max_value=1000000000000, suffix="تومان")
            self.fields["mortgageAmount"] = mortgage_field
            pricing_layout.addRow("", mortgage_field)
            
            # مبلغ اجاره ماهانه (فقط در حالت اجاره)
            rent_field = NumberFormField("اجاره ماهانه", self, True, "مبلغ اجاره ماهانه بر حسب تومان",
                                        min_value=0, max_value=1000000000, suffix="تومان")
            self.fields["monthlyRentAmount"] = rent_field
            pricing_layout.addRow("", rent_field)
        
        # اضافه کردن گروه‌ها به طرح‌بندی اصلی
        layout.addWidget(main_info_group)
        layout.addWidget(features_group)
        layout.addWidget(pricing_group)
        
        # اضافه کردن فیلد توضیحات
        description_field = TextAreaFormField("توضیحات", self, False, "توضیحات اضافی در مورد ملک",
                                             placeholder="توضیحات خود را اینجا وارد کنید...")
        self.fields["description"] = description_field
        layout.addWidget(description_field)
        
        # تنظیم اسکرول به بالا
        layout.addStretch()
    
    def _validate_form(self):
        """
        اعتبارسنجی اختصاصی فرم
        
        Returns:
            bool: آیا فرم معتبر است
        """
        is_valid = super(CommercialPropertyFormDialog, self)._validate_form()
        
        # بررسی‌های اضافی خاص املاک تجاری
        if is_valid and self.deal_type == 2:
            # در حالت اجاره، یا رهن یا اجاره ماهانه باید مقدار داشته باشد
            mortgage_field = self.fields.get("mortgageAmount")
            rent_field = self.fields.get("monthlyRentAmount")
            
            mortgage_value = mortgage_field.getValue() if mortgage_field else 0
            rent_value = rent_field.getValue() if rent_field else 0
            
            if (mortgage_value is None or mortgage_value == 0) and (rent_value is None or rent_value == 0):
                QMessageBox.warning(self, "خطای اعتبارسنجی", 
                                   "حداقل یکی از مقادیر رهن یا اجاره ماهانه باید بیشتر از صفر باشد.")
                return False
        
        return is_valid


class LandPropertyFormDialog(PropertyFormDialog):
    """
    دیالوگ فرم ثبت و ویرایش زمین
    """
    
    def __init__(self, parent=None, edit_mode=False, deal_type=1):
        """
        مقداردهی اولیه
        
        Args:
            parent (QWidget, optional): ویجت والد
            edit_mode (bool, optional): حالت ویرایش
            deal_type (int, optional): نوع معامله (1: فروش، 2: اجاره)
        """
        super(LandPropertyFormDialog, self).__init__(
            parent, "land", edit_mode
        )
        
        self.deal_type = deal_type
        self.setWindowTitle(f"{'ویرایش' if edit_mode else 'ثبت'} زمین برای {'فروش' if deal_type == 1 else 'اجاره'}")
    
    def _create_form_fields(self, layout):
        """
        ایجاد فیلدهای فرم
        
        Args:
            layout (QLayout): طرح‌بندی محتوا
        """
        # گروه‌بندی اطلاعات اصلی
        main_info_group = QGroupBox("اطلاعات اصلی زمین", self)
        StyleHelper.set_group_box_style(main_info_group)
        main_info_layout = QFormLayout(main_info_group)
        main_info_layout.setSpacing(16)
        
        # منطقه
        district_field = TextFormField("منطقه", self, True, "منطقه یا ناحیه زمین را وارد کنید")
        self.fields["district"] = district_field
        main_info_layout.addRow("", district_field)
        
        # آدرس
        address_field = TextAreaFormField("آدرس", self, True, "آدرس کامل زمین را وارد کنید")
        self.fields["address"] = address_field
        main_info_layout.addRow("", address_field)
        
        # نوع کاربری
        land_types = [
            "مسکونی", "تجاری", "اداری", "صنعتی", "کشاورزی", "باغ", "سایر"
        ]
        type_field = ComboBoxFormField("نوع کاربری", self, True, "نوع کاربری زمین را انتخاب کنید", 
                                      items=land_types)
        self.fields["landType"] = type_field
        main_info_layout.addRow("", type_field)
        
        # متراژ
        area_field = NumberFormField("متراژ", self, True, "متراژ کل زمین بر حسب متر مربع",
                                     min_value=0, max_value=1000000, suffix="متر مربع")
        self.fields["area"] = area_field
        main_info_layout.addRow("", area_field)
        
        # ابعاد زمین
        dimensions_field = TextFormField("ابعاد", self, False, "ابعاد زمین را وارد کنید (مثال: 20×30)",
                                       placeholder="طول × عرض")
        self.fields["dimensions"] = dimensions_field
        main_info_layout.addRow("", dimensions_field)
        
        # متراژ بر
        frontage_field = NumberFormField("متراژ بر", self, False, "متراژ بر زمین به متر",
                                        min_value=0, max_value=1000, suffix="متر")
        self.fields["frontage"] = frontage_field
        main_info_layout.addRow("", frontage_field)
        
        # موقعیت
        positions = ["شمالی", "جنوبی", "شرقی", "غربی", "دو بر", "سه بر", "چهار بر"]
        position_field = ComboBoxFormField("موقعیت", self, False, "موقعیت زمین را انتخاب کنید",
                                          items=positions)
        self.fields["position"] = position_field
        main_info_layout.addRow("", position_field)
        
        # گروه‌بندی ویژگی‌ها
        features_group = QGroupBox("ویژگی‌های زمین", self)
        StyleHelper.set_group_box_style(features_group)
        features_layout = QVBoxLayout(features_group)
        
        # سند شش دانگ
        document_field = CheckBoxFormField("سند", self, "آیا زمین سند شش دانگ دارد؟", "دارای سند شش دانگ")
        self.fields["hasDocument"] = document_field
        features_layout.addWidget(document_field)
        
        # مجوز ساخت
        permit_field = CheckBoxFormField("مجوز ساخت", self, "آیا زمین مجوز ساخت دارد؟", "دارای مجوز ساخت")
        self.fields["hasBuildingPermit"] = permit_field
        features_layout.addWidget(permit_field)
        
        # تراکم
        density_types = ["کم", "متوسط", "زیاد"]
        density_field = ComboBoxFormField("تراکم", self, False, "تراکم مجاز برای ساخت را انتخاب کنید",
                                         items=density_types)
        self.fields["density"] = density_field
        main_info_layout.addRow("", density_field)
        
        # حداکثر طبقات مجاز
        floors_field = NumberFormField("حداکثر طبقات مجاز", self, False, "حداکثر تعداد طبقات مجاز برای ساخت",
                                      min_value=0, max_value=100)
        self.fields["maxAllowedFloors"] = floors_field
        main_info_layout.addRow("", floors_field)
        
        # گروه‌بندی قیمت‌گذاری
        pricing_group = QGroupBox("اطلاعات قیمت‌گذاری", self)
        StyleHelper.set_group_box_style(pricing_group)
        pricing_layout = QFormLayout(pricing_group)
        pricing_layout.setSpacing(16)
        
        # قیمت فروش (فقط در حالت فروش)
        if self.deal_type == 1:
            selling_price_field = NumberFormField("قیمت کل", self, True, "قیمت کل زمین بر حسب تومان",
                                                 min_value=0, max_value=1000000000000, suffix="تومان")
            self.fields["sellingPrice"] = selling_price_field
            pricing_layout.addRow("", selling_price_field)
            
            # قیمت هر متر مربع
            price_per_meter_field = NumberFormField("قیمت هر متر مربع", self, False, "قیمت هر متر مربع بر حسب تومان",
                                                  min_value=0, max_value=1000000000, suffix="تومان")
            self.fields["pricePerMeter"] = price_per_meter_field
            pricing_layout.addRow("", price_per_meter_field)
        
        # مبلغ رهن (فقط در حالت اجاره)
        if self.deal_type == 2:
            mortgage_field = NumberFormField("مبلغ رهن", self, False, "مبلغ رهن بر حسب تومان",
                                            min_value=0, max_value=1000000000000, suffix="تومان")
            self.fields["mortgageAmount"] = mortgage_field
            pricing_layout.addRow("", mortgage_field)
            
            # مبلغ اجاره ماهانه (فقط در حالت اجاره)
            rent_field = NumberFormField("اجاره ماهانه", self, True, "مبلغ اجاره ماهانه بر حسب تومان",
                                        min_value=0, max_value=1000000000, suffix="تومان")
            self.fields["monthlyRentAmount"] = rent_field
            pricing_layout.addRow("", rent_field)
        
        # اضافه کردن گروه‌ها به طرح‌بندی اصلی
        layout.addWidget(main_info_group)
        layout.addWidget(features_group)
        layout.addWidget(pricing_group)
        
        # اضافه کردن فیلد توضیحات
        description_field = TextAreaFormField("توضیحات", self, False, "توضیحات اضافی در مورد زمین",
                                             placeholder="توضیحات خود را اینجا وارد کنید...")
        self.fields["description"] = description_field
        layout.addWidget(description_field)
        
        # تنظیم اسکرول به بالا
        layout.addStretch()
    
    def _validate_form(self):
        """
        اعتبارسنجی اختصاصی فرم
        
        Returns:
            bool: آیا فرم معتبر است
        """
        is_valid = super(LandPropertyFormDialog, self)._validate_form()
        
        # بررسی‌های اضافی خاص زمین
        if is_valid and self.deal_type == 2:
            # در حالت اجاره، یا رهن یا اجاره ماهانه باید مقدار داشته باشد
            mortgage_field = self.fields.get("mortgageAmount")
            rent_field = self.fields.get("monthlyRentAmount")
            
            mortgage_value = mortgage_field.getValue() if mortgage_field else 0
            rent_value = rent_field.getValue() if rent_field else 0
            
            if (mortgage_value is None or mortgage_value == 0) and (rent_value is None or rent_value == 0):
                QMessageBox.warning(self, "خطای اعتبارسنجی", 
                                   "حداقل یکی از مقادیر رهن یا اجاره ماهانه باید بیشتر از صفر باشد.")
                return False
        
        return is_valid 