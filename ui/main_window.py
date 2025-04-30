#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
پنجره اصلی برنامه مدیریت املاک
"""

import os
import ctypes
import sys
from PyQt5.QtWidgets import (QMainWindow, QAction, QToolBar, QStackedWidget, QWidget, 
                           QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMenu, 
                           QStatusBar, QMessageBox, QToolButton, QSplitter, QFrame)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QPixmap, QFont

from login_form import LoginForm
from register_form import RegisterForm
from property_form import PropertyForm
from property_search_form import PropertySearchForm

class MainWindow(QMainWindow):
    """پنجره اصلی برنامه مدیریت املاک"""
    
    def __init__(self):
        super().__init__()
        
        # بارگذاری کتابخانه C
        self.load_library()
        
        # تنظیم مشخصات پنجره
        self.setWindowTitle("سیستم جامع مدیریت املاک")
        self.setMinimumSize(1200, 800)
        
        # تنظیم استایل کلی
        self.set_style()
        
        # پیاده‌سازی رابط کاربری
        self.init_ui()
        
    def load_library(self):
        """بارگذاری کتابخانه C"""
        try:
            # تعیین مسیر فایل کتابخانه بر اساس سیستم عامل
            if sys.platform.startswith('win'):
                lib_path = os.path.abspath('property_lib.dll')
            elif sys.platform.startswith('linux'):
                lib_path = os.path.abspath('libproperty.so')
            else:  # macOS
                lib_path = os.path.abspath('libproperty.dylib')
                
            if os.path.exists(lib_path):
                self.c_lib = ctypes.CDLL(lib_path)
                
                # تعریف انواع داده‌های بازگشتی توابع
                self.c_lib.user_login.restype = ctypes.c_int
                self.c_lib.user_register.restype = ctypes.c_int
                
                print(f"کتابخانه C با موفقیت بارگذاری شد: {lib_path}")
            else:
                print(f"هشدار: فایل کتابخانه '{lib_path}' یافت نشد. برنامه در حالت تست اجرا می‌شود.")
                self.c_lib = None
        except Exception as e:
            print(f"خطا در بارگذاری کتابخانه C: {str(e)}")
            self.c_lib = None
            
    def set_style(self):
        """تنظیم استایل کلی برنامه"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QToolBar {
                background-color: #2c3e50;
                spacing: 10px;
                padding: 5px;
            }
            QToolButton {
                color: white;
                background-color: transparent;
                border: none;
                padding: 8px;
                border-radius: 4px;
            }
            QToolButton:hover {
                background-color: #34495e;
            }
            QStatusBar {
                background-color: #34495e;
                color: white;
            }
            QLabel {
                color: #2c3e50;
            }
            QStackedWidget {
                background-color: #f5f5f5;
            }
        """)
    
    def init_ui(self):
        """ایجاد رابط کاربری اصلی"""
        
        # ایجاد منوی برنامه
        self.create_menus()
        
        # ایجاد نوار ابزار
        self.create_toolbar()
        
        # ایجاد نوار وضعیت
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("به سیستم مدیریت املاک خوش آمدید")
        
        # ایجاد استک برای صفحات مختلف
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        
        # ایجاد فرم‌های مختلف
        self.welcome_page = self.create_welcome_page()
        self.login_form = LoginForm(parent=self)
        self.register_form = RegisterForm(parent=self)
        self.property_form = PropertyForm(parent=self)
        self.property_search_form = PropertySearchForm(parent=self)
        
        # اتصال سیگنال‌ها
        self.login_form.login_succeeded.connect(self.on_login_success)
        self.register_form.register_succeeded.connect(self.on_register_success)
        self.register_form.back_button.clicked.connect(lambda: self.stack.setCurrentWidget(self.login_form))
        
        # افزودن فرم‌ها به استک
        self.stack.addWidget(self.welcome_page)
        self.stack.addWidget(self.login_form)
        self.stack.addWidget(self.register_form)
        self.stack.addWidget(self.property_form)
        self.stack.addWidget(self.property_search_form)
        
        # نمایش صفحه خوشامدگویی
        self.stack.setCurrentWidget(self.welcome_page)
    
    def create_menus(self):
        """ایجاد منوهای برنامه"""
        # منوی فایل
        self.file_menu = self.menuBar().addMenu("فایل")
        
        login_action = QAction(QIcon("icons/login.png"), "ورود", self)
        login_action.triggered.connect(self.show_login_form)
        self.file_menu.addAction(login_action)
        
        register_action = QAction(QIcon("icons/register.png"), "ثبت‌نام", self)
        register_action.triggered.connect(self.show_register_form)
        self.file_menu.addAction(register_action)
        
        self.file_menu.addSeparator()
        
        exit_action = QAction(QIcon("icons/exit.png"), "خروج", self)
        exit_action.triggered.connect(self.close)
        self.file_menu.addAction(exit_action)
        
        # منوی املاک
        self.property_menu = self.menuBar().addMenu("املاک")
        
        add_property_action = QAction(QIcon("icons/add.png"), "ثبت ملک جدید", self)
        add_property_action.triggered.connect(self.show_property_form)
        self.property_menu.addAction(add_property_action)
        
        search_property_action = QAction(QIcon("icons/search.png"), "جستجوی ملک", self)
        search_property_action.triggered.connect(self.show_property_search_form)
        self.property_menu.addAction(search_property_action)
        
        # منوی گزارش‌ها
        self.reports_menu = self.menuBar().addMenu("گزارش‌ها")
        
        sales_report_action = QAction(QIcon("icons/report.png"), "گزارش فروش", self)
        self.reports_menu.addAction(sales_report_action)
        
        rentals_report_action = QAction(QIcon("icons/report.png"), "گزارش اجاره", self)
        self.reports_menu.addAction(rentals_report_action)
        
        # منوی راهنما
        self.help_menu = self.menuBar().addMenu("راهنما")
        
        about_action = QAction(QIcon("icons/about.png"), "درباره برنامه", self)
        about_action.triggered.connect(self.show_about)
        self.help_menu.addAction(about_action)
        
        help_action = QAction(QIcon("icons/help.png"), "راهنمای برنامه", self)
        self.help_menu.addAction(help_action)
    
    def create_toolbar(self):
        """ایجاد نوار ابزار"""
        self.toolbar = QToolBar("نوار ابزار اصلی")
        self.toolbar.setIconSize(QSize(32, 32))
        self.toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.addToolBar(self.toolbar)
        
        # دکمه ورود
        login_btn = QAction(QIcon("icons/login.png"), "ورود", self)
        login_btn.triggered.connect(self.show_login_form)
        self.toolbar.addAction(login_btn)
        
        # دکمه ثبت‌نام
        register_btn = QAction(QIcon("icons/register.png"), "ثبت‌نام", self)
        register_btn.triggered.connect(self.show_register_form)
        self.toolbar.addAction(register_btn)
        
        self.toolbar.addSeparator()
        
        # دکمه ثبت ملک
        add_property_btn = QAction(QIcon("icons/add.png"), "ثبت ملک", self)
        add_property_btn.triggered.connect(self.show_property_form)
        self.toolbar.addAction(add_property_btn)
        
        # دکمه جستجوی ملک
        search_property_btn = QAction(QIcon("icons/search.png"), "جستجوی ملک", self)
        search_property_btn.triggered.connect(self.show_property_search_form)
        self.toolbar.addAction(search_property_btn)
        
        self.toolbar.addSeparator()
        
        # دکمه خروج
        exit_btn = QAction(QIcon("icons/exit.png"), "خروج", self)
        exit_btn.triggered.connect(self.close)
        self.toolbar.addAction(exit_btn)
    
    def create_welcome_page(self):
        """ایجاد صفحه خوشامدگویی"""
        welcome_widget = QWidget()
        layout = QVBoxLayout(welcome_widget)
        
        # فریم مرکزی
        center_frame = QFrame()
        center_frame.setFrameShape(QFrame.StyledPanel)
        center_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 15px;
                border: 1px solid #ddd;
            }
        """)
        
        center_layout = QVBoxLayout(center_frame)
        center_layout.setContentsMargins(40, 40, 40, 40)
        center_layout.setSpacing(30)
        
        # لوگو
        logo_label = QLabel()
        logo_pixmap = QPixmap("icons/logo.png")
        if not logo_pixmap.isNull():
            logo_label.setPixmap(logo_pixmap.scaled(300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            logo_label.setAlignment(Qt.AlignCenter)
        else:
            # استفاده از متن به جای تصویر
            logo_label.setText("سیستم مدیریت املاک")
            logo_label.setStyleSheet("font-size: 36pt; font-weight: bold; color: #2c3e50;")
            logo_label.setAlignment(Qt.AlignCenter)
        
        center_layout.addWidget(logo_label)
        
        # عنوان
        title_label = QLabel("به سیستم جامع مدیریت املاک خوش آمدید")
        title_label.setStyleSheet("font-size: 24pt; font-weight: bold; color: #2c3e50;")
        title_label.setAlignment(Qt.AlignCenter)
        center_layout.addWidget(title_label)
        
        # توضیحات
        description_label = QLabel(
            "با استفاده از این سیستم می‌توانید به راحتی املاک خود را مدیریت کرده، "
            "ملک جدید ثبت کنید و یا ملک مورد نظر خود را جستجو نمایید."
        )
        description_label.setStyleSheet("font-size: 14pt; color: #34495e;")
        description_label.setAlignment(Qt.AlignCenter)
        description_label.setWordWrap(True)
        center_layout.addWidget(description_label)
        
        # دکمه‌ها
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(20)
        
        login_button = QPushButton("ورود به سیستم")
        login_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 15px 30px;
                font-size: 14pt;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        login_button.setMinimumWidth(200)
        login_button.clicked.connect(self.show_login_form)
        buttons_layout.addWidget(login_button)
        
        register_button = QPushButton("ثبت‌نام")
        register_button.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                padding: 15px 30px;
                font-size: 14pt;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        register_button.setMinimumWidth(200)
        register_button.clicked.connect(self.show_register_form)
        buttons_layout.addWidget(register_button)
        
        center_layout.addLayout(buttons_layout)
        
        # قرار دادن فریم مرکزی در لایه اصلی
        layout.addStretch(1)
        layout.addWidget(center_frame)
        layout.addStretch(1)
        
        return welcome_widget
    
    def show_login_form(self):
        """نمایش فرم ورود"""
        self.stack.setCurrentWidget(self.login_form)
        self.statusBar.showMessage("لطفاً نام کاربری و رمز عبور خود را وارد کنید")
    
    def show_register_form(self):
        """نمایش فرم ثبت‌نام"""
        self.stack.setCurrentWidget(self.register_form)
        self.statusBar.showMessage("لطفاً اطلاعات خود را برای ثبت‌نام وارد کنید")
    
    def show_property_form(self):
        """نمایش فرم ثبت ملک جدید"""
        # بررسی وضعیت ورود کاربر
        if hasattr(self, 'current_user') and self.current_user:
            self.stack.setCurrentWidget(self.property_form)
            self.statusBar.showMessage("ثبت ملک جدید")
        else:
            QMessageBox.warning(self, "خطا", "ابتدا وارد سیستم شوید")
            self.show_login_form()
    
    def show_property_search_form(self):
        """نمایش فرم جستجوی ملک"""
        # بررسی وضعیت ورود کاربر
        if hasattr(self, 'current_user') and self.current_user:
            self.stack.setCurrentWidget(self.property_search_form)
            self.statusBar.showMessage("جستجوی ملک")
        else:
            QMessageBox.warning(self, "خطا", "ابتدا وارد سیستم شوید")
            self.show_login_form()
    
    def on_login_success(self, username):
        """پس از ورود موفق"""
        self.current_user = username
        self.statusBar.showMessage(f"کاربر {username} وارد سیستم شد")
        QMessageBox.information(self, "ورود موفق", f"کاربر گرامی {username}، خوش آمدید!")
        
        # نمایش صفحه اصلی پس از ورود
        self.welcome_page = self.create_welcome_page()
        self.stack.insertWidget(0, self.welcome_page)
        self.stack.setCurrentWidget(self.welcome_page)
    
    def on_register_success(self, username):
        """پس از ثبت‌نام موفق"""
        self.show_login_form()
    
    def show_about(self):
        """نمایش اطلاعات درباره برنامه"""
        QMessageBox.about(self, "درباره برنامه", 
            """<h1>سیستم جامع مدیریت املاک</h1>
            <p>نسخه ۱.۰</p>
            <p>این برنامه با هدف مدیریت اطلاعات املاک طراحی شده است.</p>
            <p>امکانات این برنامه شامل:</p>
            <ul>
                <li>ثبت املاک مسکونی، تجاری و زمین</li>
                <li>جستجوی پیشرفته املاک با معیارهای مختلف</li>
                <li>مدیریت کاربران</li>
                <li>تهیه گزارش‌های متنوع</li>
            </ul>
            """
        )
        
if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # تنظیم جهت راست به چپ برای رابط کاربری
    app.setLayoutDirection(Qt.RightToLeft)
    
    # اطمینان از وجود پوشه آیکون‌ها
    if not os.path.exists("icons"):
        os.makedirs("icons")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_()) 