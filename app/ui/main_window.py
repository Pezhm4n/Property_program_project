from PySide6.QtWidgets import (QLabel, QStatusBar, QToolBar, QWidget, 
                                 QVBoxLayout, QHBoxLayout, QPushButton, QStackedWidget, QListWidget, QListWidgetItem)
from PySide6.QtCore import Qt, QSize
from ui.base_window import BaseWindow
from ui.views.property_list_view import PropertyListView
from ui.views.dashboard_page import DashboardPage
from ui.views.reports_page import ReportsPage

class MainWindow(BaseWindow):
    def __init__(self, nav_manager):
        super().__init__(nav_manager)
        self.setWindowTitle("داشبورد مدیریت املاک")
        self.setMinimumSize(1280, 800)
        
        # Central widget and main layout
        central_widget = QWidget()
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Sidebar
        self.sidebar = QListWidget()
        self.sidebar.setMaximumWidth(200)
        self.sidebar.addItem("🏠 داشبورد")
        self.sidebar.addItem("🏘 املاک")
        self.sidebar.addItem("📊 گزارش‌ها")
        
        item_settings = QListWidgetItem("⚙ تنظیمات")
        item_settings.setFlags(item_settings.flags() & ~Qt.ItemFlag.ItemIsEnabled)
        self.sidebar.addItem(item_settings)
        
        self.sidebar.currentRowChanged.connect(self.switch_tab)
        
        # Content Area
        self.content_stack = QStackedWidget()
        
        # Dashboard Page
        self.dashboard_page = DashboardPage(self.nav_manager.session)
        self.content_stack.addWidget(self.dashboard_page)
        
        # Property View
        self.property_view = PropertyListView(self.nav_manager.session)
        self.content_stack.addWidget(self.property_view)
        
        # Reports Page
        self.reports_page = ReportsPage()
        self.content_stack.addWidget(self.reports_page)
        
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.content_stack)
        
        self.setCentralWidget(central_widget)
        
        # Toolbar
        self.toolbar = QToolBar("ابزارها")
        self.toolbar.setIconSize(QSize(16, 16))
        self.toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.addToolBar(self.toolbar)
        
        act_add = self.toolbar.addAction("➕ افزودن")
        act_add.triggered.connect(self.property_view.add_property)
        
        act_edit = self.toolbar.addAction("✏️ ویرایش")
        act_edit.triggered.connect(self.property_view.edit_property)
        
        act_archive = self.toolbar.addAction("📁 آرشیو")
        act_archive.triggered.connect(self.property_view.archive_property)
        
        act_restore = self.toolbar.addAction("♻️ بازیابی")
        act_restore.triggered.connect(self.property_view.restore_property)
        
        self.toolbar.addSeparator()
        act_refresh = self.toolbar.addAction("🔄 بروزرسانی")
        act_refresh.triggered.connect(self.property_view.refresh_data)
        
        self.toolbar.addSeparator()
        act_logout = self.toolbar.addAction("🚪 خروج")
        act_logout.triggered.connect(self.handle_logout)
        
        # Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.update_status_bar()
        
        # Load default tab
        self.sidebar.setCurrentRow(0) # Dashboard tab

    def switch_tab(self, index):
        self.content_stack.setCurrentIndex(index)
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
