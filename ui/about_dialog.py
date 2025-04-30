#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ماژول دیالوگ درباره ما
این ماژول اطلاعات مربوط به برنامه و سازندگان آن را نمایش می‌دهد.
"""

import os
import sys
import logging
from typing import Optional, List

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTabWidget, QWidget, QFormLayout,
    QTextEdit, QGridLayout, QSpacerItem, QSizePolicy
)
from PyQt5.QtGui import QIcon, QPixmap, QFont, QFontMetrics, QDesktopServices
from PyQt5.QtCore import Qt, QSize, QUrl

class AboutDialog(QDialog):
    """کلاس دیالوگ درباره ما برای سیستم مدیریت املاک"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.logger = logging.getLogger(__name__)
        
        # تنظیم ویژگی‌های دیالوگ
        self.setup_dialog()
        
        # ایجاد رابط کاربری
        self.create_ui()
        
        self.logger.info("دیالوگ درباره ما ایجاد شد")
    
    def setup_dialog(self):
        """تنظیم ویژگی‌های دیالوگ"""
        self.setWindowTitle("درباره برنامه")
        self.resize(600, 400)
        self.setWindowIcon(QIcon("icons/about.png"))
        self.setModal(True)
    
    def create_ui(self):
        """ایجاد رابط کاربری دیالوگ درباره ما"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # نوار بالایی با لوگو و عنوان
        self.create_header()
        layout.addLayout(self.header_layout)
        
        # تب‌های اطلاعات
        self.tabs = QTabWidget()
        
        # تب اطلاعات نرم‌افزار
        self.create_about_tab()
        
        # تب اعتبارات و توسعه‌دهندگان
        self.create_credits_tab()
        
        # تب مجوز
        self.create_license_tab()
        
        layout.addWidget(self.tabs)
        
        # دکمه بستن
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.close_button = QPushButton("بستن")
        self.close_button.clicked.connect(self.accept)
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
    
    def create_header(self):
        """ایجاد بخش هدر دیالوگ"""
        self.header_layout = QHBoxLayout()
        
        # لوگوی برنامه
        logo_label = QLabel()
        logo_path = os.path.join("icons", "app_logo.png")
        
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            scaled_pixmap = pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
        else:
            logo_label.setText("🏢")
            logo_label.setFont(QFont("Arial", 36))
        
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setMinimumSize(80, 80)
        self.header_layout.addWidget(logo_label)
        
        # عنوان و نسخه
        title_layout = QVBoxLayout()
        
        app_name_label = QLabel("سیستم مدیریت املاک")
        app_name_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_layout.addWidget(app_name_label)
        
        version_label = QLabel("نسخه ۱.۰.۰")
        version_font = QFont()
        version_font.setPointSize(10)
        version_label.setFont(version_font)
        title_layout.addWidget(version_label)
        
        # تاریخ ساخت
        build_label = QLabel("تاریخ ساخت: ۱۴۰۳/۰۵/۰۱")
        build_font = QFont()
        build_font.setPointSize(8)
        build_label.setFont(build_font)
        title_layout.addWidget(build_label)
        
        self.header_layout.addLayout(title_layout)
        self.header_layout.addStretch(1)
    
    def create_about_tab(self):
        """ایجاد تب اطلاعات نرم‌افزار"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # توضیحات نرم‌افزار
        description_text = """
        <html>
        <body style="font-family: Arial; text-align: justify;">
            <h3 style="text-align: center;">سیستم مدیریت املاک</h3>
            <p>
            این نرم‌افزار یک سیستم جامع برای مدیریت املاک است که امکانات زیر را فراهم می‌کند:
            </p>
            <ul>
                <li>ثبت و مدیریت املاک مسکونی، تجاری و زمین</li>
                <li>جستجوی پیشرفته بر اساس معیارهای مختلف</li>
                <li>تولید گزارش‌های متنوع و نمودارهای آماری</li>
                <li>مدیریت کاربران با سطوح دسترسی مختلف</li>
                <li>پشتیبان‌گیری خودکار از داده‌ها</li>
                <li>رابط کاربری چندزبانه و قابل تنظیم</li>
            </ul>
            <p>
            این نرم‌افزار با استفاده از زبان برنامه‌نویسی C برای هسته اصلی و Python برای رابط کاربری توسعه داده شده است.
            </p>
        </body>
        </html>
        """
        
        description_label = QLabel(description_text)
        description_label.setWordWrap(True)
        description_label.setOpenExternalLinks(True)
        description_label.setTextFormat(Qt.RichText)
        layout.addWidget(description_label)
        
        # اطلاعات سیستم
        system_group_layout = QFormLayout()
        system_group_layout.setVerticalSpacing(10)
        system_group_layout.setLabelAlignment(Qt.AlignRight)
        
        try:
            import platform
            system_info = f"{platform.system()} {platform.release()}"
            python_version = platform.python_version()
            
            from PyQt5.QtCore import QT_VERSION_STR
            qt_version = QT_VERSION_STR
        except ImportError:
            system_info = "اطلاعات در دسترس نیست"
            python_version = "اطلاعات در دسترس نیست"
            qt_version = "اطلاعات در دسترس نیست"
        
        system_group_layout.addRow("سیستم عامل:", QLabel(system_info))
        system_group_layout.addRow("نسخه Python:", QLabel(python_version))
        system_group_layout.addRow("نسخه Qt:", QLabel(qt_version))
        
        layout.addLayout(system_group_layout)
        layout.addStretch(1)
        
        # وب‌سایت و تماس
        contact_layout = QHBoxLayout()
        
        website_btn = QPushButton("وب‌سایت")
        website_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://www.example.com")))
        contact_layout.addWidget(website_btn)
        
        support_btn = QPushButton("پشتیبانی")
        support_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("mailto:support@example.com")))
        contact_layout.addWidget(support_btn)
        
        layout.addLayout(contact_layout)
        
        self.tabs.addTab(tab, "درباره برنامه")
    
    def create_credits_tab(self):
        """ایجاد تب اعتبارات و توسعه‌دهندگان"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        credits_text = """
        <html>
        <body style="font-family: Arial;">
            <h3 style="text-align: center;">تیم توسعه</h3>
            
            <div style="margin: 10px 0;">
                <h4>برنامه‌نویسان:</h4>
                <ul>
                    <li>محمد محمدی - توسعه هسته اصلی (C)</li>
                    <li>علی علوی - توسعه رابط کاربری (Python/PyQt)</li>
                    <li>زهرا زارعی - طراحی پایگاه داده و گزارش‌گیری</li>
                </ul>
            </div>
            
            <div style="margin: 10px 0;">
                <h4>طراحان گرافیک:</h4>
                <ul>
                    <li>سارا صادقی - طراحی رابط کاربری و آیکون‌ها</li>
                    <li>حسین حسینی - طراحی لوگو و عناصر گرافیکی</li>
                </ul>
            </div>
            
            <div style="margin: 10px 0;">
                <h4>آزمایش‌کنندگان:</h4>
                <ul>
                    <li>فاطمه فاطمی</li>
                    <li>رضا رضایی</li>
                    <li>مریم مرادی</li>
                </ul>
            </div>
            
            <div style="margin: 15px 0;">
                <h4>کتابخانه‌های استفاده شده:</h4>
                <ul>
                    <li>PyQt5 - رابط کاربری گرافیکی</li>
                    <li>Matplotlib - رسم نمودارها</li>
                    <li>Pandas - تحلیل داده‌ها</li>
                    <li>NumPy - محاسبات عددی</li>
                    <li>Reportlab - تولید گزارش‌های PDF</li>
                    <li>XlsxWriter - خروجی Excel</li>
                </ul>
            </div>
            
            <p style="text-align: center; font-style: italic; margin-top: 20px;">
                با تشکر از همه افرادی که در توسعه این نرم‌افزار مشارکت داشته‌اند.
            </p>
        </body>
        </html>
        """
        
        credits_label = QLabel(credits_text)
        credits_label.setWordWrap(True)
        credits_label.setOpenExternalLinks(True)
        credits_label.setTextFormat(Qt.RichText)
        layout.addWidget(credits_label)
        
        self.tabs.addTab(tab, "توسعه‌دهندگان")
    
    def create_license_tab(self):
        """ایجاد تب مجوز"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        license_text_edit = QTextEdit()
        license_text_edit.setReadOnly(True)
        
        license_text = """
        مجوز استفاده از نرم‌افزار سیستم مدیریت املاک
        ==================================

        نسخه ۱.۰ - ۱۴۰۳
        
        ۱. شرایط استفاده
        ----------------
        استفاده از این نرم‌افزار به معنی پذیرش تمامی شرایط این مجوز است. این نرم‌افزار تحت مجوز MIT منتشر شده است.
        
        ۲. مجوز MIT
        -----------
        
        Copyright (c) ۱۴۰۳ گروه توسعه نرم‌افزار مدیریت املاک
        
        بدینوسیله به هر شخصی که نسخه‌ای از این نرم‌افزار و فایل‌های مستندات مرتبط با آن ("نرم‌افزار") را دریافت می‌کند، 
        اجازه داده می‌شود تا بدون محدودیت با نرم‌افزار کار کند، از جمله بدون محدودیت حقوق استفاده، کپی، اصلاح، ادغام، 
        انتشار، توزیع، اعطای مجوز فرعی و/یا فروش نسخه‌هایی از نرم‌افزار و اجازه دادن به اشخاصی که نرم‌افزار به آنها ارائه 
        می‌شود که همین کار را انجام دهند، با رعایت شرایط زیر:
        
        اطلاعیه کپی‌رایت فوق و این اطلاعیه مجوز باید در تمام نسخه‌ها یا بخش‌های عمده نرم‌افزار گنجانده شود.
        
        نرم‌افزار "همانطور که هست" ارائه می‌شود، بدون هیچگونه ضمانت، صریح یا ضمنی، از جمله اما نه محدود به 
        ضمانت‌های قابلیت فروش، مناسب بودن برای یک هدف خاص و عدم نقض. در هیچ موردی، نویسندگان یا دارندگان 
        حق نشر مسئول هیچگونه ادعا، خسارت یا مسئولیت دیگری، چه در اقدام قراردادی، شبه جرم یا موارد دیگر، 
        ناشی از، خارج از یا در ارتباط با نرم‌افزار یا استفاده یا سایر معاملات در نرم‌افزار نیستند.
        
        ۳. محدودیت‌های مسئولیت
        -----------------
        در هیچ صورتی، توسعه‌دهندگان یا دارندگان حق نشر این نرم‌افزار مسئول خسارات ناشی از استفاده یا عدم استفاده از این 
        نرم‌افزار نیستند. کاربر مسئولیت کامل استفاده از این نرم‌افزار را می‌پذیرد.
        
        ۴. پشتیبانی و بروزرسانی
        ----------------------
        توسعه‌دهندگان هیچ تعهدی به ارائه پشتیبانی یا بروزرسانی برای این نرم‌افزار ندارند، مگر اینکه به صورت قراردادی 
        جداگانه توافق شده باشد.
        """
        
        license_text_edit.setPlainText(license_text)
        layout.addWidget(license_text_edit)
        
        self.tabs.addTab(tab, "مجوز استفاده") 