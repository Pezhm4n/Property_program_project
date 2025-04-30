#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
این ماژول برای مدیریت قالب و ظاهر برنامه استفاده می‌شود.
تمام تنظیمات مربوط به رنگ‌ها، فونت‌ها و سبک‌های برنامه در اینجا تعریف شده است.
"""

import os
import logging
from enum import Enum

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QPalette, QColor, QFont
from PyQt5.QtCore import Qt, QSettings

# تنظیم لاگر
logger = logging.getLogger(__name__)

class ThemeType(Enum):
    """انواع قالب‌های قابل استفاده در برنامه"""
    LIGHT = "روشن"
    DARK = "تیره"
    SYSTEM = "سیستم"
    CUSTOM = "سفارشی"

class FontSize(Enum):
    """اندازه‌های فونت قابل استفاده در برنامه"""
    SMALL = "کوچک"
    MEDIUM = "متوسط"
    LARGE = "بزرگ"
    CUSTOM = "سفارشی"

class Theme:
    """کلاس اصلی برای مدیریت قالب و ظاهر برنامه"""
    
    # رنگ‌های پیش‌فرض قالب روشن
    LIGHT_COLORS = {
        "background": "#f5f5f5",
        "foreground": "#212121",
        "primary": "#2c3e50",
        "secondary": "#34495e",
        "success": "#27ae60",
        "info": "#2980b9",
        "warning": "#f39c12",
        "danger": "#e74c3c",
        "light": "#ecf0f1",
        "dark": "#7f8c8d",
        "disabled": "#bdc3c7",
        "highlight": "#3498db",
        "accent": "#9b59b6",
    }
    
    # رنگ‌های پیش‌فرض قالب تیره
    DARK_COLORS = {
        "background": "#2d2d2d",
        "foreground": "#f5f5f5",
        "primary": "#3498db",
        "secondary": "#2c3e50",
        "success": "#2ecc71",
        "info": "#3498db",
        "warning": "#f39c12",
        "danger": "#e74c3c",
        "light": "#7f8c8d",
        "dark": "#2c3e50",
        "disabled": "#555555",
        "highlight": "#16a085",
        "accent": "#9b59b6",
    }
    
    # اندازه‌های فونت
    FONT_SIZES = {
        FontSize.SMALL: 9,
        FontSize.MEDIUM: 10,
        FontSize.LARGE: 12,
    }
    
    # فونت‌های پیش‌فرض
    DEFAULT_FONTS = {
        "windows": "Segoe UI",
        "linux": "DejaVu Sans",
        "darwin": "Lucida Grande",
    }
    
    def __init__(self):
        """مقداردهی اولیه کلاس"""
        self._settings = QSettings()
        self._current_theme = None
        self._current_font_size = None
        self._current_font_family = None
        self._custom_colors = {}
        
        # بارگذاری تنظیمات ذخیره شده
        self._load_settings()
    
    def _load_settings(self):
        """بارگذاری تنظیمات ذخیره شده"""
        # بارگذاری نوع قالب
        theme_name = self._settings.value("theme/type", ThemeType.SYSTEM.name)
        try:
            self._current_theme = ThemeType[theme_name]
        except (KeyError, TypeError):
            self._current_theme = ThemeType.SYSTEM
            logger.warning(f"نوع قالب نامعتبر: {theme_name}. استفاده از قالب پیش‌فرض.")
        
        # بارگذاری اندازه فونت
        font_size_name = self._settings.value("theme/font_size", FontSize.MEDIUM.name)
        try:
            self._current_font_size = FontSize[font_size_name]
        except (KeyError, TypeError):
            self._current_font_size = FontSize.MEDIUM
            logger.warning(f"اندازه فونت نامعتبر: {font_size_name}. استفاده از اندازه پیش‌فرض.")
        
        # بارگذاری خانواده فونت
        import platform
        system = platform.system().lower()
        default_font = self.DEFAULT_FONTS.get(system, "Sans-Serif")
        self._current_font_family = self._settings.value("theme/font_family", default_font)
        
        # بارگذاری رنگ‌های سفارشی
        if self._current_theme == ThemeType.CUSTOM:
            for color_name in self.LIGHT_COLORS.keys():
                saved_color = self._settings.value(f"theme/custom_colors/{color_name}", None)
                if saved_color:
                    self._custom_colors[color_name] = saved_color
    
    def _save_settings(self):
        """ذخیره تنظیمات قالب"""
        self._settings.setValue("theme/type", self._current_theme.name)
        self._settings.setValue("theme/font_size", self._current_font_size.name)
        self._settings.setValue("theme/font_family", self._current_font_family)
        
        # ذخیره رنگ‌های سفارشی
        if self._current_theme == ThemeType.CUSTOM:
            for color_name, color_value in self._custom_colors.items():
                self._settings.setValue(f"theme/custom_colors/{color_name}", color_value)
    
    def get_theme_type(self):
        """دریافت نوع قالب فعلی"""
        return self._current_theme
    
    def set_theme_type(self, theme_type):
        """تنظیم نوع قالب"""
        if not isinstance(theme_type, ThemeType):
            raise TypeError("نوع قالب باید از نوع ThemeType باشد")
        
        self._current_theme = theme_type
        self._save_settings()
        self.apply_theme()
    
    def get_font_size(self):
        """دریافت اندازه فونت فعلی"""
        return self._current_font_size
    
    def set_font_size(self, font_size, custom_size=None):
        """تنظیم اندازه فونت"""
        if not isinstance(font_size, FontSize):
            raise TypeError("اندازه فونت باید از نوع FontSize باشد")
        
        self._current_font_size = font_size
        if font_size == FontSize.CUSTOM and custom_size:
            self._settings.setValue("theme/custom_font_size", custom_size)
        
        self._save_settings()
        self.apply_font()
    
    def get_font_family(self):
        """دریافت خانواده فونت فعلی"""
        return self._current_font_family
    
    def set_font_family(self, font_family):
        """تنظیم خانواده فونت"""
        self._current_font_family = font_family
        self._save_settings()
        self.apply_font()
    
    def get_custom_color(self, color_name):
        """دریافت یک رنگ سفارشی"""
        return self._custom_colors.get(color_name, self.get_color(color_name))
    
    def set_custom_color(self, color_name, color_value):
        """تنظیم یک رنگ سفارشی"""
        if color_name not in self.LIGHT_COLORS:
            raise ValueError(f"نام رنگ نامعتبر: {color_name}")
        
        self._custom_colors[color_name] = color_value
        self._save_settings()
        
        # اگر قالب سفارشی فعال است، قالب را دوباره اعمال می‌کنیم
        if self._current_theme == ThemeType.CUSTOM:
            self.apply_theme()
    
    def get_color(self, color_name):
        """دریافت یک رنگ از قالب فعلی"""
        if self._current_theme == ThemeType.DARK:
            return self.DARK_COLORS.get(color_name, "#ffffff")
        elif self._current_theme == ThemeType.CUSTOM:
            return self._custom_colors.get(color_name, self.LIGHT_COLORS.get(color_name, "#ffffff"))
        else:  # LIGHT یا SYSTEM
            return self.LIGHT_COLORS.get(color_name, "#ffffff")
    
    def apply_theme(self):
        """اعمال قالب به برنامه"""
        app = QApplication.instance()
        if not app:
            logger.error("نمونه QApplication یافت نشد.")
            return
        
        palette = QPalette()
        
        # تنظیم رنگ‌های اصلی پالت
        if self._current_theme == ThemeType.DARK:
            # قالب تیره
            palette.setColor(QPalette.Window, QColor(self.get_color("background")))
            palette.setColor(QPalette.WindowText, QColor(self.get_color("foreground")))
            palette.setColor(QPalette.Base, QColor(self.get_color("background")).darker(110))
            palette.setColor(QPalette.AlternateBase, QColor(self.get_color("background")).darker(120))
            palette.setColor(QPalette.ToolTipBase, QColor(self.get_color("primary")))
            palette.setColor(QPalette.ToolTipText, QColor(self.get_color("foreground")))
            palette.setColor(QPalette.Text, QColor(self.get_color("foreground")))
            palette.setColor(QPalette.Button, QColor(self.get_color("background")))
            palette.setColor(QPalette.ButtonText, QColor(self.get_color("foreground")))
            palette.setColor(QPalette.BrightText, Qt.red)
            palette.setColor(QPalette.Link, QColor(self.get_color("highlight")))
            palette.setColor(QPalette.Highlight, QColor(self.get_color("primary")))
            palette.setColor(QPalette.HighlightedText, QColor(self.get_color("light")))
            palette.setColor(QPalette.Disabled, QPalette.Text, QColor(self.get_color("disabled")))
            palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(self.get_color("disabled")))
        elif self._current_theme == ThemeType.CUSTOM:
            # قالب سفارشی
            palette.setColor(QPalette.Window, QColor(self.get_color("background")))
            palette.setColor(QPalette.WindowText, QColor(self.get_color("foreground")))
            palette.setColor(QPalette.Base, QColor(self.get_color("background")).lighter(110))
            palette.setColor(QPalette.AlternateBase, QColor(self.get_color("background")).lighter(120))
            palette.setColor(QPalette.ToolTipBase, QColor(self.get_color("primary")))
            palette.setColor(QPalette.ToolTipText, QColor(self.get_color("foreground")))
            palette.setColor(QPalette.Text, QColor(self.get_color("foreground")))
            palette.setColor(QPalette.Button, QColor(self.get_color("background")))
            palette.setColor(QPalette.ButtonText, QColor(self.get_color("foreground")))
            palette.setColor(QPalette.BrightText, Qt.red)
            palette.setColor(QPalette.Link, QColor(self.get_color("highlight")))
            palette.setColor(QPalette.Highlight, QColor(self.get_color("primary")))
            palette.setColor(QPalette.HighlightedText, QColor(self.get_color("light")))
            palette.setColor(QPalette.Disabled, QPalette.Text, QColor(self.get_color("disabled")))
            palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(self.get_color("disabled")))
        else:  # LIGHT یا SYSTEM
            # در حالت سیستم، اگر سیستم عامل از حالت تاریک پشتیبانی می‌کند، از آن استفاده می‌کنیم
            if self._current_theme == ThemeType.SYSTEM:
                # بررسی حالت تاریک سیستم عامل
                import platform
                if platform.system() == "Windows":
                    import winreg
                    try:
                        registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
                        key = winreg.OpenKey(registry, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
                        value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
                        if value == 0:  # حالت تاریک
                            self._apply_dark_theme_palette(palette)
                            app.setPalette(palette)
                            return
                    except:
                        pass
                elif platform.system() == "Darwin":  # macOS
                    try:
                        import subprocess
                        result = subprocess.run(
                            ["defaults", "read", "-g", "AppleInterfaceStyle"],
                            capture_output=True, text=True
                        )
                        if result.stdout.strip() == "Dark":
                            self._apply_dark_theme_palette(palette)
                            app.setPalette(palette)
                            return
                    except:
                        pass
            
            # قالب روشن (پیش‌فرض)
            palette.setColor(QPalette.Window, QColor(self.get_color("background")))
            palette.setColor(QPalette.WindowText, QColor(self.get_color("foreground")))
            palette.setColor(QPalette.Base, Qt.white)
            palette.setColor(QPalette.AlternateBase, QColor(self.get_color("background")))
            palette.setColor(QPalette.ToolTipBase, QColor(self.get_color("light")))
            palette.setColor(QPalette.ToolTipText, QColor(self.get_color("dark")))
            palette.setColor(QPalette.Text, QColor(self.get_color("foreground")))
            palette.setColor(QPalette.Button, QColor(self.get_color("background")))
            palette.setColor(QPalette.ButtonText, QColor(self.get_color("foreground")))
            palette.setColor(QPalette.BrightText, Qt.red)
            palette.setColor(QPalette.Link, QColor(self.get_color("primary")))
            palette.setColor(QPalette.Highlight, QColor(self.get_color("primary")))
            palette.setColor(QPalette.HighlightedText, Qt.white)
            palette.setColor(QPalette.Disabled, QPalette.Text, QColor(self.get_color("disabled")))
            palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(self.get_color("disabled")))
        
        # اعمال پالت به برنامه
        app.setPalette(palette)
        
        # اعمال استایل‌شیت
        self._apply_stylesheet()
    
    def _apply_dark_theme_palette(self, palette):
        """اعمال پالت تیره به پالت داده شده"""
        palette.setColor(QPalette.Window, QColor(self.DARK_COLORS["background"]))
        palette.setColor(QPalette.WindowText, QColor(self.DARK_COLORS["foreground"]))
        palette.setColor(QPalette.Base, QColor(self.DARK_COLORS["background"]).darker(110))
        palette.setColor(QPalette.AlternateBase, QColor(self.DARK_COLORS["background"]).darker(120))
        palette.setColor(QPalette.ToolTipBase, QColor(self.DARK_COLORS["primary"]))
        palette.setColor(QPalette.ToolTipText, QColor(self.DARK_COLORS["foreground"]))
        palette.setColor(QPalette.Text, QColor(self.DARK_COLORS["foreground"]))
        palette.setColor(QPalette.Button, QColor(self.DARK_COLORS["background"]))
        palette.setColor(QPalette.ButtonText, QColor(self.DARK_COLORS["foreground"]))
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Link, QColor(self.DARK_COLORS["highlight"]))
        palette.setColor(QPalette.Highlight, QColor(self.DARK_COLORS["primary"]))
        palette.setColor(QPalette.HighlightedText, QColor(self.DARK_COLORS["light"]))
        palette.setColor(QPalette.Disabled, QPalette.Text, QColor(self.DARK_COLORS["disabled"]))
        palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(self.DARK_COLORS["disabled"]))
    
    def _apply_stylesheet(self):
        """اعمال استایل‌شیت به برنامه بر اساس قالب فعلی"""
        app = QApplication.instance()
        if not app:
            return
        
        # استایل‌شیت عمومی
        stylesheet = f"""
            QToolTip {{
                background-color: {self.get_color("background")};
                color: {self.get_color("foreground")};
                border: 1px solid {self.get_color("primary")};
                padding: 5px;
            }}
            
            QTableView {{
                gridline-color: {self.get_color("light")};
                selection-background-color: {self.get_color("primary")};
                selection-color: {self.get_color("light")};
            }}
            
            QTableView::item:hover {{
                background-color: {self.get_color("highlight")};
                color: {self.get_color("light")};
            }}
            
            QHeaderView::section {{
                background-color: {self.get_color("background")};
                color: {self.get_color("foreground")};
                padding: 5px;
                border: 1px solid {self.get_color("light")};
            }}
            
            QPushButton {{
                background-color: {self.get_color("background")};
                color: {self.get_color("foreground")};
                border: 1px solid {self.get_color("primary")};
                padding: 5px 10px;
                border-radius: 3px;
            }}
            
            QPushButton:hover {{
                background-color: {self.get_color("primary")};
                color: {self.get_color("light")};
            }}
            
            QPushButton:pressed {{
                background-color: {self.get_color("secondary")};
            }}
            
            QPushButton:disabled {{
                background-color: {self.get_color("background")};
                color: {self.get_color("disabled")};
                border: 1px solid {self.get_color("disabled")};
            }}
            
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit {{
                border: 1px solid {self.get_color("primary")};
                border-radius: 3px;
                padding: 3px;
                selection-background-color: {self.get_color("highlight")};
                selection-color: {self.get_color("light")};
            }}
            
            QTabWidget::pane {{
                border: 1px solid {self.get_color("light")};
            }}
            
            QTabBar::tab {{
                background-color: {self.get_color("background")};
                color: {self.get_color("foreground")};
                border: 1px solid {self.get_color("light")};
                padding: 5px 10px;
                margin-right: 2px;
            }}
            
            QTabBar::tab:selected {{
                background-color: {self.get_color("primary")};
                color: {self.get_color("light")};
            }}
            
            QTabBar::tab:hover:!selected {{
                background-color: {self.get_color("highlight")};
                color: {self.get_color("light")};
            }}
            
            QScrollBar:vertical {{
                border: none;
                background-color: {self.get_color("background")};
                width: 12px;
                margin: 0px;
            }}
            
            QScrollBar::handle:vertical {{
                background-color: {self.get_color("primary")};
                min-height: 20px;
                border-radius: 6px;
            }}
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                border: none;
                background: none;
                height: 0px;
            }}
            
            QScrollBar:horizontal {{
                border: none;
                background-color: {self.get_color("background")};
                height: 12px;
                margin: 0px;
            }}
            
            QScrollBar::handle:horizontal {{
                background-color: {self.get_color("primary")};
                min-width: 20px;
                border-radius: 6px;
            }}
            
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                border: none;
                background: none;
                width: 0px;
            }}
            
            QMenu {{
                background-color: {self.get_color("background")};
                color: {self.get_color("foreground")};
                border: 1px solid {self.get_color("light")};
            }}
            
            QMenu::item:selected {{
                background-color: {self.get_color("primary")};
                color: {self.get_color("light")};
            }}
            
            QMenuBar {{
                background-color: {self.get_color("background")};
                color: {self.get_color("foreground")};
            }}
            
            QMenuBar::item:selected {{
                background-color: {self.get_color("primary")};
                color: {self.get_color("light")};
            }}
            
            QToolBar {{
                background-color: {self.get_color("background")};
                border-bottom: 1px solid {self.get_color("light")};
                spacing: 3px;
            }}
            
            QStatusBar {{
                background-color: {self.get_color("background")};
                color: {self.get_color("foreground")};
                border-top: 1px solid {self.get_color("light")};
            }}
            
            QProgressBar {{
                border: 1px solid {self.get_color("light")};
                border-radius: 3px;
                text-align: center;
                color: {self.get_color("foreground")};
            }}
            
            QProgressBar::chunk {{
                background-color: {self.get_color("success")};
                width: 10px;
            }}
            
            QGroupBox {{
                border: 1px solid {self.get_color("light")};
                border-radius: 5px;
                margin-top: 20px;
                font-weight: bold;
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
                color: {self.get_color("foreground")};
            }}
        """
        
        app.setStyleSheet(stylesheet)
    
    def apply_font(self):
        """اعمال فونت به برنامه"""
        app = QApplication.instance()
        if not app:
            logger.error("نمونه QApplication یافت نشد.")
            return
        
        # تعیین اندازه فونت
        if self._current_font_size == FontSize.CUSTOM:
            size = self._settings.value("theme/custom_font_size", 10, type=int)
        else:
            size = self.FONT_SIZES.get(self._current_font_size, 10)
        
        # ایجاد و تنظیم فونت
        font = QFont(self._current_font_family, size)
        app.setFont(font)
    
    def reset_to_defaults(self):
        """بازگرداندن تمام تنظیمات به حالت پیش‌فرض"""
        self._current_theme = ThemeType.SYSTEM
        self._current_font_size = FontSize.MEDIUM
        
        import platform
        system = platform.system().lower()
        self._current_font_family = self.DEFAULT_FONTS.get(system, "Sans-Serif")
        
        self._custom_colors = {}
        
        self._save_settings()
        self.apply_theme()
        self.apply_font()

# نمونه واحد جهانی از کلاس Theme
theme_manager = Theme() 