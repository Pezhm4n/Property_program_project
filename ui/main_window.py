#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ماژول پنجره اصلی
این ماژول پیاده‌سازی پنجره اصلی برنامه مدیریت املاک را ارائه می‌دهد.
"""

import os
import sys
import logging
from PyQt5.QtWidgets import (
    QMainWindow, QAction, QMenu, QToolBar, QStatusBar, QTabWidget,
    QVBoxLayout, QWidget, QMessageBox, QDockWidget, QLabel, QComboBox
)
from PyQt5.QtCore import Qt, QSettings, QSize, QPoint
from PyQt5.QtGui import QIcon

# وارد کردن ویجت‌های سفارشی
from .residential_tab import ResidentialTab
from .commercial_tab import CommercialTab
from .land_tab import LandTab
from .search_tab import SearchTab
from .report_tab import ReportTab
from .dashboard import Dashboard
from .user_management_dialog import UserManagementDialog
from .settings_dialog import SettingsDialog
from .about_dialog import AboutDialog

# وارد کردن سایر ماژول‌های مورد نیاز
from property_management.report_generator import ReportGenerator
from property_management.user_management import UserManager, User


class MainWindow(QMainWindow):
    """پنجره اصلی برنامه مدیریت املاک"""
    
    def __init__(self, current_user, user_manager, parent=None):
        """سازنده پنجره اصلی
        
        Args:
            current_user (User): کاربر فعلی
            user_manager (UserManager): مدیر کاربر
            parent (QWidget, optional): ویجت والد. پیش‌فرض None.
        """
        super().__init__(parent)
        
        self.logger = logging.getLogger(__name__)
        self.current_user = current_user
        self.user_manager = user_manager
        self.report_generator = ReportGenerator()
        
        # تنظیم عنوان پنجره
        self.setWindowTitle("سیستم مدیریت املاک")
        
        # تنظیم اندازه پنجره
        self.resize(1200, 800)
        
        # بارگیری تنظیمات
        self.settings = QSettings("شرکت مدیریت املاک", "مدیریت املاک")
        self.load_window_settings()
        
        # ایجاد رابط کاربری
        self.init_ui()
        
        # به‌روزرسانی نوار وضعیت
        self.update_status_bar()
        
        self.logger.info("پنجره اصلی ایجاد شد")
    
    def init_ui(self):
        """راه‌اندازی رابط کاربری"""
        # ایجاد ویجت مرکزی
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # ایجاد لایه عمودی
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        
        # ایجاد ویجت تب
        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)
        
        # افزودن داشبورد
        self.dashboard = Dashboard(self.current_user)
        self.tab_widget.addTab(self.dashboard, "داشبورد")
        
        # افزودن تب‌های مدیریت املاک
        self.residential_tab = ResidentialTab(self.current_user)
        self.tab_widget.addTab(self.residential_tab, "املاک مسکونی")
        
        self.commercial_tab = CommercialTab(self.current_user)
        self.tab_widget.addTab(self.commercial_tab, "املاک تجاری")
        
        self.land_tab = LandTab(self.current_user)
        self.tab_widget.addTab(self.land_tab, "زمین")
        
        # افزودن تب جستجو
        self.search_tab = SearchTab(self.current_user, self.report_generator)
        self.tab_widget.addTab(self.search_tab, "جستجوی پیشرفته")
        
        # افزودن تب گزارش‌ها
        self.report_tab = ReportTab(self.current_user, self.report_generator)
        self.tab_widget.addTab(self.report_tab, "گزارش‌ها")
        
        # ایجاد منوها و نوار ابزار
        self.create_menus()
        self.create_toolbar()
        
        # ایجاد نوار وضعیت
        self.create_status_bar()
        
        # ایجاد نوار کناری
        self.create_dock_widgets()
    
    def create_menus(self):
        """ایجاد منوهای برنامه"""
        # منوی فایل
        file_menu = self.menuBar().addMenu("فایل")
        
        # اقدام تنظیمات
        settings_action = QAction(QIcon("resources/icons/settings.png"), "تنظیمات", self)
        settings_action.setShortcut("Ctrl+P")
        settings_action.setStatusTip("تغییر تنظیمات برنامه")
        settings_action.triggered.connect(self.show_settings_dialog)
        file_menu.addAction(settings_action)
        
        file_menu.addSeparator()
        
        # اقدام خروج
        exit_action = QAction(QIcon("resources/icons/exit.png"), "خروج", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setStatusTip("خروج از برنامه")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # منوی گزارش‌ها
        report_menu = self.menuBar().addMenu("گزارش‌ها")
        
        # اقدام گزارش تعداد املاک
        property_count_action = QAction("گزارش تعداد املاک", self)
        property_count_action.setStatusTip("ایجاد گزارش تعداد املاک")
        property_count_action.triggered.connect(lambda: self.report_tab.generate_property_count_report())
        report_menu.addAction(property_count_action)
        
        # اقدام گزارش ارزش املاک
        property_value_action = QAction("گزارش ارزش املاک", self)
        property_value_action.setStatusTip("ایجاد گزارش ارزش املاک")
        property_value_action.triggered.connect(lambda: self.report_tab.generate_property_value_report())
        report_menu.addAction(property_value_action)
        
        # اقدام گزارش منطقه‌ای
        district_report_action = QAction("گزارش منطقه‌ای", self)
        district_report_action.setStatusTip("ایجاد گزارش توزیع املاک بر اساس منطقه")
        district_report_action.triggered.connect(lambda: self.report_tab.generate_district_report())
        report_menu.addAction(district_report_action)
        
        # اقدام گزارش محدوده قیمت
        price_range_action = QAction("گزارش محدوده قیمت", self)
        price_range_action.setStatusTip("ایجاد گزارش توزیع املاک بر اساس محدوده قیمت")
        price_range_action.triggered.connect(lambda: self.report_tab.generate_price_range_report())
        report_menu.addAction(price_range_action)
        
        # منوی مدیریت
        admin_menu = self.menuBar().addMenu("مدیریت")
        
        # اقدام مدیریت کاربران
        user_management_action = QAction(QIcon("resources/icons/users.png"), "مدیریت کاربران", self)
        user_management_action.setStatusTip("مدیریت کاربران سیستم")
        user_management_action.triggered.connect(self.show_user_management_dialog)
        
        # فقط کاربران با دسترسی مدیر می‌توانند مدیریت کاربر را مشاهده کنند
        if self.current_user.is_admin:
            admin_menu.addAction(user_management_action)
        
        # منوی راهنما
        help_menu = self.menuBar().addMenu("راهنما")
        
        # اقدام راهنما
        help_action = QAction(QIcon("resources/icons/help.png"), "راهنمای برنامه", self)
        help_action.setShortcut("F1")
        help_action.setStatusTip("نمایش راهنمای برنامه")
        help_action.triggered.connect(self.show_help)
        help_menu.addAction(help_action)
        
        # اقدام درباره
        about_action = QAction(QIcon("resources/icons/about.png"), "درباره برنامه", self)
        about_action.setStatusTip("نمایش اطلاعات درباره برنامه")
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)
    
    def create_toolbar(self):
        """ایجاد نوار ابزار"""
        self.toolbar = QToolBar("نوار ابزار اصلی")
        self.toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(Qt.TopToolBarArea, self.toolbar)
        
        # اقدام افزودن ملک مسکونی
        add_residential_action = QAction(QIcon("resources/icons/residential.png"), "افزودن ملک مسکونی", self)
        add_residential_action.setStatusTip("ثبت ملک مسکونی جدید")
        add_residential_action.triggered.connect(lambda: self.tab_widget.setCurrentWidget(self.residential_tab))
        self.toolbar.addAction(add_residential_action)
        
        # اقدام افزودن ملک تجاری
        add_commercial_action = QAction(QIcon("resources/icons/commercial.png"), "افزودن ملک تجاری", self)
        add_commercial_action.setStatusTip("ثبت ملک تجاری جدید")
        add_commercial_action.triggered.connect(lambda: self.tab_widget.setCurrentWidget(self.commercial_tab))
        self.toolbar.addAction(add_commercial_action)
        
        # اقدام افزودن زمین
        add_land_action = QAction(QIcon("resources/icons/land.png"), "افزودن زمین", self)
        add_land_action.setStatusTip("ثبت زمین جدید")
        add_land_action.triggered.connect(lambda: self.tab_widget.setCurrentWidget(self.land_tab))
        self.toolbar.addAction(add_land_action)
        
        self.toolbar.addSeparator()
        
        # اقدام جستجو
        search_action = QAction(QIcon("resources/icons/search.png"), "جستجوی پیشرفته", self)
        search_action.setStatusTip("جستجوی پیشرفته املاک")
        search_action.triggered.connect(lambda: self.tab_widget.setCurrentWidget(self.search_tab))
        self.toolbar.addAction(search_action)
        
        # اقدام گزارش‌ها
        report_action = QAction(QIcon("resources/icons/report.png"), "گزارش‌ها", self)
        report_action.setStatusTip("مدیریت گزارش‌ها")
        report_action.triggered.connect(lambda: self.tab_widget.setCurrentWidget(self.report_tab))
        self.toolbar.addAction(report_action)
    
    def create_status_bar(self):
        """ایجاد نوار وضعیت"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # اطلاعات کاربر
        self.user_label = QLabel(f"کاربر: {self.current_user.full_name} ({self.current_user.username})")
        self.status_bar.addPermanentWidget(self.user_label)
        
        # نوع دسترسی
        access_level = "مدیر" if self.current_user.is_admin else "کاربر عادی"
        self.access_label = QLabel(f"دسترسی: {access_level}")
        self.status_bar.addPermanentWidget(self.access_label)
    
    def create_dock_widgets(self):
        """ایجاد ویجت‌های نوار کناری"""
        # ویجت فیلتر سریع
        self.quick_filter_dock = QDockWidget("فیلتر سریع", self)
        self.quick_filter_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        
        filter_widget = QWidget()
        filter_layout = QVBoxLayout(filter_widget)
        
        # افزودن کنترل‌های فیلتر
        filter_layout.addWidget(QLabel("نوع ملک:"))
        property_type_combo = QComboBox()
        property_type_combo.addItems(["همه", "مسکونی", "تجاری", "زمین"])
        filter_layout.addWidget(property_type_combo)
        
        filter_layout.addWidget(QLabel("نوع معامله:"))
        deal_type_combo = QComboBox()
        deal_type_combo.addItems(["همه", "فروش", "اجاره"])
        filter_layout.addWidget(deal_type_combo)
        
        filter_layout.addWidget(QLabel("منطقه:"))
        district_combo = QComboBox()
        district_combo.addItems(["همه", "منطقه 1", "منطقه 2", "منطقه 3", "منطقه 4", "منطقه 5"])
        filter_layout.addWidget(district_combo)
        
        filter_layout.addStretch()
        
        self.quick_filter_dock.setWidget(filter_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, self.quick_filter_dock)
    
    def update_status_bar(self):
        """به‌روزرسانی نوار وضعیت"""
        self.status_bar.showMessage("آماده", 5000)
    
    def generate_property_count_report(self):
        """تولید گزارش تعداد املاک - تغییر یافته برای سازگاری با کد قدیمی"""
        self.tab_widget.setCurrentWidget(self.report_tab)
        self.report_tab.generate_property_count_report()
    
    def generate_property_value_report(self):
        """تولید گزارش ارزش املاک - تغییر یافته برای سازگاری با کد قدیمی"""
        self.tab_widget.setCurrentWidget(self.report_tab)
        self.report_tab.generate_property_value_report()
    
    def generate_district_report(self):
        """تولید گزارش منطقه‌ای - تغییر یافته برای سازگاری با کد قدیمی"""
        self.tab_widget.setCurrentWidget(self.report_tab)
        self.report_tab.generate_district_report()
    
    def show_settings_dialog(self):
        """نمایش دیالوگ تنظیمات"""
        dialog = SettingsDialog(self)
        if dialog.exec_():
            # اعمال تنظیمات جدید
            self.logger.info("تنظیمات به‌روزرسانی شد")
            # به‌روزرسانی رابط کاربری در صورت نیاز
            self.update_ui()
    
    def show_user_management_dialog(self):
        """نمایش دیالوگ مدیریت کاربران"""
        if not self.current_user.is_admin:
            QMessageBox.warning(self, "خطای دسترسی", "شما مجوز دسترسی به این بخش را ندارید.")
            return
        
        dialog = UserManagementDialog(
            current_user=self.current_user,
            parent=self
        )
        dialog.exec_()
        
        # به‌روزرسانی نوار وضعیت در صورت تغییر اطلاعات کاربر
        self.update_status_bar()
    
    def show_help(self):
        """نمایش راهنمای برنامه"""
        help_file = os.path.join(os.path.dirname(__file__), "../property_management", "resources", "help", "index.html")
        if os.path.exists(help_file):
            # باز کردن راهنما در مرورگر
            import webbrowser
            webbrowser.open(help_file)
        else:
            QMessageBox.information(self, "راهنمای برنامه", 
                                   "راهنمای برنامه در حال حاضر در دسترس نیست.")
    
    def show_about_dialog(self):
        """نمایش دیالوگ درباره برنامه"""
        dialog = AboutDialog(self)
        dialog.exec_()
    
    def update_ui(self):
        """به‌روزرسانی رابط کاربری بر اساس تنظیمات جدید"""
        # به‌روزرسانی بخش‌های مختلف رابط کاربری
        pass
    
    def load_window_settings(self):
        """بارگیری تنظیمات پنجره از تنظیمات ذخیره شده"""
        position = self.settings.value("mainwindow/position", QPoint(200, 200))
        size = self.settings.value("mainwindow/size", QSize(1200, 800))
        self.move(position)
        self.resize(size)
    
    def save_window_settings(self):
        """ذخیره تنظیمات پنجره"""
        self.settings.setValue("mainwindow/position", self.pos())
        self.settings.setValue("mainwindow/size", self.size())
    
    def closeEvent(self, event):
        """رویداد بستن پنجره"""
        reply = QMessageBox.question(self, "تایید خروج",
                                     "آیا از خروج از برنامه اطمینان دارید؟",
                                     QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # ذخیره تنظیمات پنجره
            self.save_window_settings()
            
            # بستن اتصالات و آزادسازی منابع
            self.logger.info("خروج از برنامه")
            event.accept()
        else:
            event.ignore() 