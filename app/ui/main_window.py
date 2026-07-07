from PySide6.QtWidgets import (QLabel, QStatusBar, QToolBar, QWidget, 
                                 QVBoxLayout, QHBoxLayout, QPushButton, QStackedWidget, QListWidget, QListWidgetItem)
from PySide6.QtCore import Qt, QSize
from ui.base_window import BaseWindow
from ui.views.property_list_view import PropertyListView
from ui.views.dashboard_page import DashboardPage
from ui.views.reports_page import ReportsPage
from ui.views.settings_page import SettingsPage

class MainWindow(BaseWindow):
    def __init__(self, nav_manager):
        super().__init__(nav_manager)
        self.setWindowTitle("داشبورد مدیریت املاک")
        self.setMinimumSize(1280, 800)
        
        # Central widget and main layout
        central_widget = QWidget()
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar layout container to set modern margins
        sidebar_container = QWidget()
        sidebar_container.setObjectName("sidebarContainer")
        sidebar_container.setFixedWidth(220)
        sidebar_layout = QVBoxLayout(sidebar_container)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)
        
        # Sidebar
        self.sidebar = QListWidget()
        self.sidebar.setObjectName("sidebarWidget")
        self.sidebar.setMaximumWidth(220)
        self.sidebar.addItem("🏠 داشبورد")
        self.sidebar.addItem("🏘 املاک")
        self.sidebar.addItem("📊 گزارش‌ها")
        
        self.sidebar.addItem("⚙ تنظیمات")
        sidebar_layout.addWidget(self.sidebar)
        
        # Content Area
        self.content_stack = QStackedWidget()
        self.content_stack.setContentsMargins(16, 16, 16, 16)
        
        # Dashboard Page
        self.dashboard_page = DashboardPage(self.nav_manager.session)
        self.content_stack.addWidget(self.dashboard_page)
        
        # Property View
        self.property_view = PropertyListView(self.nav_manager.session)
        self.content_stack.addWidget(self.property_view)
        
        # Reports Page
        self.reports_page = ReportsPage(self.nav_manager.session)
        self.content_stack.addWidget(self.reports_page)
        
        # Settings Page
        self.settings_page = SettingsPage(self.nav_manager.session, self)
        self.content_stack.addWidget(self.settings_page)
        
        main_layout.addWidget(sidebar_container, 0)
        main_layout.addWidget(self.content_stack, 1)
        
        self.setCentralWidget(central_widget)
        
        # Toolbar
        self.toolbar = QToolBar("ابزارها")
        self.toolbar.setIconSize(QSize(16, 16))
        self.toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.addToolBar(self.toolbar)
        
        self.act_add = self.toolbar.addAction("➕ افزودن")
        self.act_add.triggered.connect(self.property_view.add_property)
        
        self.act_edit = self.toolbar.addAction("✏️ ویرایش")
        self.act_edit.triggered.connect(self.property_view.edit_property)
        
        self.act_archive = self.toolbar.addAction("📁 آرشیو")
        self.act_archive.triggered.connect(self.property_view.archive_property)
        
        self.act_restore = self.toolbar.addAction("♻️ بازیابی")
        self.act_restore.triggered.connect(self.property_view.restore_property)
        
        self.toolbar_sep1 = self.toolbar.addSeparator()
        self.act_refresh = self.toolbar.addAction("🔄 بروزرسانی")
        self.act_refresh.triggered.connect(self._on_refresh_triggered)
        
        self.toolbar_sep2 = self.toolbar.addSeparator()
        self.act_theme = self.toolbar.addAction("🌓 تغییر تم")
        self.act_theme.triggered.connect(self.toggle_theme)
        
        self.toolbar.addSeparator()
        self.act_logout = self.toolbar.addAction("🚪 خروج")
        self.act_logout.triggered.connect(self.handle_logout)
        
        # Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.update_status_bar()
        
        # Sidebar signals
        self.sidebar.currentRowChanged.connect(self.switch_tab)
        
        # Load default tab
        self.sidebar.setCurrentRow(0) # Dashboard tab

    def switch_tab(self, index):
        self.content_stack.setCurrentIndex(index)
        
        is_property_tab = (index == 1)
        self.act_add.setVisible(is_property_tab)
        self.act_edit.setVisible(is_property_tab)
        self.act_archive.setVisible(is_property_tab)
        self.act_restore.setVisible(is_property_tab)
        
        self.act_refresh.setVisible(index in (0, 1))
        
        if index == 0:
            self.dashboard_page.refresh_data()
        elif index == 1:
            self.property_view.refresh_data()
            
    def _on_refresh_triggered(self):
        index = self.content_stack.currentIndex()
        if index == 0:
            self.dashboard_page.refresh_data()
        elif index == 1:
            self.property_view.refresh_data()
            
    def update_status_bar(self):
        user = self.nav_manager.session.username or "Unknown"
        self.status_bar.showMessage(f"کاربر جاری: {user} | وضعیت نشست: فعال | نسخه: 1.0.0")

    def handle_logout(self):
        self.nav_manager.session.clear_session()
        self.nav_manager.show_login()

    def toggle_theme(self):
        from PySide6.QtWidgets import QApplication
        from core.theme_manager import ThemeManager
        
        new_theme = "light" if self.nav_manager.session.theme == "dark" else "dark"
        self.nav_manager.session.set_theme(new_theme)
        
        theme_manager = ThemeManager()
        theme_manager.apply_theme(QApplication.instance(), new_theme)
