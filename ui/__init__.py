"""
ماژول رابط کاربری گرافیکی برای سیستم مدیریت املاک
این ماژول شامل تمام کلاس‌ها و توابع مربوط به رابط کاربری گرافیکی است.
"""

# واردسازی کلاس‌های پرکاربرد برای استفاده آسان‌تر
from .login_dialog import LoginDialog
from .main_window import MainWindow
from .login_form import LoginForm
from .register_form import RegisterForm
from .dashboard import Dashboard
from .residential_tab import ResidentialTab
from .commercial_tab import CommercialTab
from .land_tab import LandTab
from .search_tab import SearchTab
from .report_tab import ReportTab
from .settings_dialog import SettingsDialog
from .about_dialog import AboutDialog
