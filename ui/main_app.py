#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
برنامه اصلی مدیریت املاک با رابط کاربری گرافیکی
این برنامه امکان مدیریت املاک، جستجو و گزارش‌گیری را فراهم می‌کند
"""

import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTabWidget, QWidget, 
                            QPushButton, QVBoxLayout, QHBoxLayout, QLabel, 
                            QStackedWidget, QMessageBox, QAction, QToolBar,
                            QStatusBar, QFrame, QSplitter, QTreeWidget, QTreeWidgetItem)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QIcon, QPixmap

# واردات فرم‌های مورد نیاز
from property_form import PropertyForm
from search_form import SearchForm
from login_form import LoginForm
from user_profile import UserProfile

# واردات رابط میانی برای ارتباط با هسته سیستم
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from bridge import user_bridge


class MainWindow(QMainWindow):
    """پنجره اصلی برنامه مدیریت املاک"""
    
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("سیستم مدیریت املاک")
        self.setMinimumSize(1200, 800)
        self.setLayoutDirection(Qt.RightToLeft)  # راست به چپ برای زبان فارسی
        
        # تعریف فونت فارسی
        self.farsi_font = QFont()
        self.farsi_font.setFamily("Tahoma")
        self.farsi_font.setPointSize(10)
        self.setFont(self.farsi_font)
        
        # تنظیم اطلاعات کاربر
        self.current_user = None
        self.user_data = None
        
        # راه‌اندازی رابط کاربری
        self.init_ui()
        
        # در ابتدا، فرم ورود را نمایش می‌دهیم
        self.show_login_form()
    
    def init_ui(self):
        """راه‌اندازی رابط کاربری اصلی"""
        # منوی اصلی
        self.create_menu()
        
        # نوار ابزار
        self.create_toolbar()
        
        # پنل مرکزی
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # استفاده از QStackedWidget برای مدیریت صفحات مختلف
        main_layout = QVBoxLayout(self.central_widget)
        
        self.stacked_widget = QStackedWidget()
        
        # صفحه خوش‌آمدگویی
        self.welcome_widget = QWidget()
        welcome_layout = QVBoxLayout()
        
        # لوگو و عنوان
        logo_label = QLabel()
        # logo_label.setPixmap(QPixmap("logo.png").scaled(200, 200, Qt.KeepAspectRatio))
        logo_label.setAlignment(Qt.AlignCenter)
        
        title_label = QLabel("سیستم مدیریت املاک")
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setFamily("Tahoma")
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        
        welcome_layout.addWidget(logo_label)
        welcome_layout.addWidget(title_label)
        welcome_layout.addStretch(1)
        
        # دکمه‌های سریع
        buttons_layout = QHBoxLayout()
        
        quick_property_btn = QPushButton("ثبت ملک جدید")
        quick_property_btn.setMinimumHeight(50)
        quick_property_btn.clicked.connect(self.show_property_form)
        
        quick_search_btn = QPushButton("جستجوی ملک")
        quick_search_btn.setMinimumHeight(50)
        quick_search_btn.clicked.connect(self.show_search_form)
        
        quick_reports_btn = QPushButton("گزارش‌ها")
        quick_reports_btn.setMinimumHeight(50)
        quick_reports_btn.clicked.connect(self.show_reports)
        
        buttons_layout.addWidget(quick_property_btn)
        buttons_layout.addWidget(quick_search_btn)
        buttons_layout.addWidget(quick_reports_btn)
        
        welcome_layout.addLayout(buttons_layout)
        welcome_layout.addStretch(1)
        
        # وضعیت سیستم
        status_group = QFrame()
        status_group.setFrameShape(QFrame.StyledPanel)
        status_layout = QVBoxLayout(status_group)
        
        status_title = QLabel("وضعیت سیستم")
        status_title.setAlignment(Qt.AlignCenter)
        status_font = QFont()
        status_font.setBold(True)
        status_title.setFont(status_font)
        
        status_layout.addWidget(status_title)
        
        # اطلاعات املاک ثبت شده
        property_count_label = QLabel("تعداد کل املاک ثبت شده: در حال بارگذاری...")
        status_layout.addWidget(property_count_label)
        
        # اطلاعات کاربر
        self.user_status_label = QLabel("کاربر فعلی: وارد نشده")
        status_layout.addWidget(self.user_status_label)
        
        welcome_layout.addWidget(status_group)
        
        self.welcome_widget.setLayout(welcome_layout)
        
        # اضافه کردن ویجت‌ها به stacked widget
        self.stacked_widget.addWidget(self.welcome_widget)
        
        # محیط داشبورد اصلی
        self.dashboard_widget = QWidget()
        dashboard_layout = QHBoxLayout()
        
        # پنل سمت راست (منوی درختی)
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabel("منوی اصلی")
        self.tree_widget.setMinimumWidth(250)
        self.tree_widget.setMaximumWidth(300)
        
        # ایجاد آیتم‌های منو
        self.create_menu_tree()
        
        # اتصال کلیک بر روی درخت منو به تابع مربوطه
        self.tree_widget.itemClicked.connect(self.on_tree_item_clicked)
        
        # پنل مرکزی (محتوای اصلی)
        self.content_stack = QStackedWidget()
        
        # تقسیم‌کننده بین منو و محتوا
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.tree_widget)
        splitter.addWidget(self.content_stack)
        splitter.setSizes([250, 950])
        
        dashboard_layout.addWidget(splitter)
        self.dashboard_widget.setLayout(dashboard_layout)
        
        self.stacked_widget.addWidget(self.dashboard_widget)
        
        # اضافه کردن stacked widget به layout اصلی
        main_layout.addWidget(self.stacked_widget)
        
        # نوار وضعیت
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("آماده")
    
    def create_menu(self):
        """ایجاد منوی اصلی برنامه"""
        menubar = self.menuBar()
        
        # منوی فایل
        file_menu = menubar.addMenu("فایل")
        
        new_property_action = QAction("ثبت ملک جدید", self)
        new_property_action.triggered.connect(self.show_property_form)
        file_menu.addAction(new_property_action)
        
        search_action = QAction("جستجوی ملک", self)
        search_action.triggered.connect(self.show_search_form)
        file_menu.addAction(search_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("خروج", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # منوی کاربر
        user_menu = menubar.addMenu("کاربر")
        
        self.login_action = QAction("ورود", self)
        self.login_action.triggered.connect(self.show_login_form)
        user_menu.addAction(self.login_action)
        
        self.profile_action = QAction("پروفایل کاربری", self)
        self.profile_action.triggered.connect(self.show_user_profile)
        self.profile_action.setEnabled(False)
        user_menu.addAction(self.profile_action)
        
        self.logout_action = QAction("خروج از حساب", self)
        self.logout_action.triggered.connect(self.logout)
        self.logout_action.setEnabled(False)
        user_menu.addAction(self.logout_action)
        
        # منوی گزارش‌ها
        reports_menu = menubar.addMenu("گزارش‌ها")
        
        property_stats_action = QAction("آمار املاک", self)
        property_stats_action.triggered.connect(self.show_property_stats)
        reports_menu.addAction(property_stats_action)
        
        sales_report_action = QAction("گزارش فروش", self)
        sales_report_action.triggered.connect(self.show_sales_report)
        reports_menu.addAction(sales_report_action)
        
        rental_report_action = QAction("گزارش اجاره", self)
        rental_report_action.triggered.connect(self.show_rental_report)
        reports_menu.addAction(rental_report_action)
        
        # منوی راهنما
        help_menu = menubar.addMenu("راهنما")
        
        about_action = QAction("درباره برنامه", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        help_action = QAction("راهنما", self)
        help_action.triggered.connect(self.show_help)
        help_menu.addAction(help_action)
    
    def create_toolbar(self):
        """ایجاد نوار ابزار"""
        toolbar = QToolBar("نوار ابزار اصلی")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(32, 32))
        self.addToolBar(toolbar)
        
        new_property_action = QAction(QIcon("icons/property.png"), "ملک جدید", self)
        new_property_action.triggered.connect(self.show_property_form)
        toolbar.addAction(new_property_action)
        
        search_action = QAction(QIcon("icons/search.png"), "جستجو", self)
        search_action.triggered.connect(self.show_search_form)
        toolbar.addAction(search_action)
        
        toolbar.addSeparator()
        
        profile_action = QAction(QIcon("icons/user.png"), "پروفایل", self)
        profile_action.triggered.connect(self.show_user_profile)
        toolbar.addAction(profile_action)
        
        logout_action = QAction(QIcon("icons/logout.png"), "خروج از حساب", self)
        logout_action.triggered.connect(self.logout)
        toolbar.addAction(logout_action)
        
        toolbar.addSeparator()
        
        reports_action = QAction(QIcon("icons/report.png"), "گزارش‌ها", self)
        reports_action.triggered.connect(self.show_reports)
        toolbar.addAction(reports_action)
        
        help_action = QAction(QIcon("icons/help.png"), "راهنما", self)
        help_action.triggered.connect(self.show_help)
        toolbar.addAction(help_action)
    
    def create_menu_tree(self):
        """ایجاد منوی درختی"""
        # مدیریت املاک
        property_item = QTreeWidgetItem(self.tree_widget, ["مدیریت املاک"])
        property_item.setData(0, Qt.UserRole, "property_management")
        
        property_add = QTreeWidgetItem(property_item, ["ثبت ملک جدید"])
        property_add.setData(0, Qt.UserRole, "add_property")
        
        property_list = QTreeWidgetItem(property_item, ["لیست املاک"])
        property_list.setData(0, Qt.UserRole, "property_list")
        
        property_search = QTreeWidgetItem(property_item, ["جستجوی ملک"])
        property_search.setData(0, Qt.UserRole, "property_search")
        
        # املاک مسکونی
        residential_item = QTreeWidgetItem(self.tree_widget, ["املاک مسکونی"])
        residential_item.setData(0, Qt.UserRole, "residential")
        
        residential_list = QTreeWidgetItem(residential_item, ["لیست املاک مسکونی"])
        residential_list.setData(0, Qt.UserRole, "residential_list")
        
        residential_search = QTreeWidgetItem(residential_item, ["جستجوی ملک مسکونی"])
        residential_search.setData(0, Qt.UserRole, "residential_search")
        
        # املاک تجاری
        commercial_item = QTreeWidgetItem(self.tree_widget, ["املاک تجاری"])
        commercial_item.setData(0, Qt.UserRole, "commercial")
        
        commercial_list = QTreeWidgetItem(commercial_item, ["لیست املاک تجاری"])
        commercial_list.setData(0, Qt.UserRole, "commercial_list")
        
        commercial_search = QTreeWidgetItem(commercial_item, ["جستجوی ملک تجاری"])
        commercial_search.setData(0, Qt.UserRole, "commercial_search")
        
        # زمین
        land_item = QTreeWidgetItem(self.tree_widget, ["زمین"])
        land_item.setData(0, Qt.UserRole, "land")
        
        land_list = QTreeWidgetItem(land_item, ["لیست زمین‌ها"])
        land_list.setData(0, Qt.UserRole, "land_list")
        
        land_search = QTreeWidgetItem(land_item, ["جستجوی زمین"])
        land_search.setData(0, Qt.UserRole, "land_search")
        
        # گزارش‌ها
        reports_item = QTreeWidgetItem(self.tree_widget, ["گزارش‌ها"])
        reports_item.setData(0, Qt.UserRole, "reports")
        
        reports_property = QTreeWidgetItem(reports_item, ["آمار املاک"])
        reports_property.setData(0, Qt.UserRole, "property_stats")
        
        reports_sales = QTreeWidgetItem(reports_item, ["گزارش فروش"])
        reports_sales.setData(0, Qt.UserRole, "sales_report")
        
        reports_rental = QTreeWidgetItem(reports_item, ["گزارش اجاره"])
        reports_rental.setData(0, Qt.UserRole, "rental_report")
        
        # مدیریت کاربران
        users_item = QTreeWidgetItem(self.tree_widget, ["مدیریت کاربران"])
        users_item.setData(0, Qt.UserRole, "users")
        
        users_profile = QTreeWidgetItem(users_item, ["پروفایل کاربری"])
        users_profile.setData(0, Qt.UserRole, "user_profile")
        
        # تنظیمات
        settings_item = QTreeWidgetItem(self.tree_widget, ["تنظیمات"])
        settings_item.setData(0, Qt.UserRole, "settings")
        
        # باز کردن منوی ثبت ملک به صورت پیش‌فرض
        self.tree_widget.expandItem(property_item)
    
    def on_tree_item_clicked(self, item, column):
        """عملکرد کلیک روی آیتم‌های منوی درختی"""
        action = item.data(0, Qt.UserRole)
        
        if action == "add_property":
            self.show_property_form()
        elif action == "property_search":
            self.show_search_form()
        elif action == "property_stats":
            self.show_property_stats()
        elif action == "sales_report":
            self.show_sales_report()
        elif action == "rental_report":
            self.show_rental_report()
        elif action == "user_profile":
            self.show_user_profile()
        elif action == "residential_search":
            self.show_search_form("residential")
        elif action == "commercial_search":
            self.show_search_form("commercial")
        elif action == "land_search":
            self.show_search_form("land")
        elif action == "property_list":
            self.show_property_list()
        elif action == "residential_list":
            self.show_property_list("residential")
        elif action == "commercial_list":
            self.show_property_list("commercial")
        elif action == "land_list":
            self.show_property_list("land")
    
    def show_login_form(self):
        """نمایش فرم ورود"""
        login_form = LoginForm(self)
        if login_form.exec_() == LoginForm.Accepted:
            # کاربر با موفقیت وارد شده است
            self.current_user = login_form.get_username()
            self.user_data = login_form.get_user_data()
            self.update_user_status()
            
            # فعال کردن عملیات‌های مربوط به کاربر
            self.login_action.setEnabled(False)
            self.profile_action.setEnabled(True)
            self.logout_action.setEnabled(True)
            
            # نمایش داشبورد اصلی
            self.stacked_widget.setCurrentIndex(1)  # داشبورد
        else:
            # کاربر نتوانسته وارد شود، در صفحه خوش‌آمدگویی می‌ماند
            self.stacked_widget.setCurrentIndex(0)  # صفحه خوش‌آمد
    
    def update_user_status(self):
        """به‌روزرسانی وضعیت کاربر"""
        if self.current_user:
            self.user_status_label.setText(f"کاربر فعلی: {self.current_user}")
            self.status_bar.showMessage(f"خوش آمدید، {self.current_user}")
        else:
            self.user_status_label.setText("کاربر فعلی: وارد نشده")
            self.status_bar.showMessage("آماده")
    
    def show_user_profile(self):
        """نمایش پروفایل کاربر"""
        if not self.current_user:
            QMessageBox.warning(self, "خطا", "ابتدا وارد حساب کاربری خود شوید")
            return
            
        profile_form = UserProfile(self.current_user, self)
        profile_form.exec_()
    
    def logout(self):
        """خروج از حساب کاربری"""
        if not self.current_user:
            return
            
        reply = QMessageBox.question(self, "خروج از حساب", 
                                   "آیا از خروج از حساب کاربری خود اطمینان دارید؟",
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.current_user = None
            self.user_data = None
            self.update_user_status()
            
            # غیرفعال کردن عملیات‌های مربوط به کاربر
            self.login_action.setEnabled(True)
            self.profile_action.setEnabled(False)
            self.logout_action.setEnabled(False)
            
            # نمایش صفحه خوش‌آمد
            self.stacked_widget.setCurrentIndex(0)
            
            QMessageBox.information(self, "خروج از حساب", "با موفقیت از حساب کاربری خود خارج شدید")
    
    def show_property_form(self):
        """نمایش فرم ثبت ملک جدید"""
        if not self.current_user:
            QMessageBox.warning(self, "خطا", "برای ثبت ملک جدید ابتدا وارد حساب کاربری خود شوید")
            self.show_login_form()
            return
            
        property_form = PropertyForm(self.current_user, self)
        property_form.exec_()
    
    def show_search_form(self, property_type=None):
        """نمایش فرم جستجوی ملک"""
        search_form = SearchForm(property_type, self)
        search_form.exec_()
    
    def show_property_list(self, property_type=None):
        """نمایش لیست املاک"""
        # این تابع باید پیاده‌سازی شود
        QMessageBox.information(self, "اطلاعیه", "این قابلیت در حال پیاده‌سازی است")
    
    def show_reports(self):
        """نمایش صفحه گزارش‌ها"""
        # این تابع باید پیاده‌سازی شود
        QMessageBox.information(self, "اطلاعیه", "صفحه گزارش‌ها در حال پیاده‌سازی است")
    
    def show_property_stats(self):
        """نمایش آمار املاک"""
        # این تابع باید پیاده‌سازی شود
        QMessageBox.information(self, "اطلاعیه", "آمار املاک در حال پیاده‌سازی است")
    
    def show_sales_report(self):
        """نمایش گزارش فروش"""
        # این تابع باید پیاده‌سازی شود
        QMessageBox.information(self, "اطلاعیه", "گزارش فروش در حال پیاده‌سازی است")
    
    def show_rental_report(self):
        """نمایش گزارش اجاره"""
        # این تابع باید پیاده‌سازی شود
        QMessageBox.information(self, "اطلاعیه", "گزارش اجاره در حال پیاده‌سازی است")
    
    def show_about(self):
        """نمایش اطلاعات درباره برنامه"""
        QMessageBox.about(self, "درباره برنامه", 
                       "سیستم مدیریت املاک\n"
                       "نسخه 1.0\n"
                       "توسعه‌دهنده: تیم برنامه‌نویسی املاک\n\n"
                       "این برنامه برای مدیریت اطلاعات املاک، جستجو و گزارش‌گیری طراحی شده است.")
    
    def show_help(self):
        """نمایش راهنمای برنامه"""
        QMessageBox.information(self, "راهنما", 
                             "برای استفاده از برنامه، ابتدا وارد حساب کاربری خود شوید.\n"
                             "سپس می‌توانید از منوی سمت راست یا نوار ابزار بالا، عملیات مختلف را انجام دهید.\n\n"
                             "برای ثبت ملک جدید، گزینه «ثبت ملک جدید» را انتخاب کنید.\n"
                             "برای جستجوی املاک، گزینه «جستجوی ملک» را انتخاب کنید.\n"
                             "برای مشاهده گزارش‌ها، از منوی «گزارش‌ها» استفاده کنید.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # تنظیم استایل برنامه
    app.setStyle("Fusion")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_()) 