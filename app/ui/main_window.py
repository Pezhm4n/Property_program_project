from PySide6.QtWidgets import (QStatusBar, QToolBar, QWidget, 
                                 QVBoxLayout, QHBoxLayout, QStackedWidget, QListWidget)
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
        
        session = self.nav_manager.session
        
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
        
        # Sidebar — build dynamically based on RBAC permissions
        self.sidebar = QListWidget()
        self.sidebar.setObjectName("sidebarWidget")
        self.sidebar.setMaximumWidth(220)
        
        # Map sidebar index -> page index
        self._sidebar_page_map = []
        
        self.sidebar.addItem("🏠 داشبورد")
        self._sidebar_page_map.append("dashboard")
        
        self.sidebar.addItem("🏘 املاک")
        self._sidebar_page_map.append("properties")
        
        if session.has_permission("VIEW_REPORTS"):
            self.sidebar.addItem("📊 گزارش‌ها")
            self._sidebar_page_map.append("reports")
            
        if session.has_permission("MANAGE_USERS"):
            self.sidebar.addItem("👥 مدیریت کاربران")
            self._sidebar_page_map.append("users")
        
        if session.has_permission("VIEW_SETTINGS"):
            self.sidebar.addItem("⚙ تنظیمات")
            self._sidebar_page_map.append("settings")
        
        sidebar_layout.addWidget(self.sidebar)
        
        # Content Area
        self.content_stack = QStackedWidget()
        self.content_stack.setContentsMargins(16, 16, 16, 16)
        
        # Page index tracking
        self._page_indices = {}
        page_idx = 0
        
        # Dashboard Page (always visible)
        self.dashboard_page = DashboardPage(session)
        self.content_stack.addWidget(self.dashboard_page)
        self._page_indices["dashboard"] = page_idx
        page_idx += 1
        
        # Property View (always visible)
        self.property_view = PropertyListView(session)
        self.content_stack.addWidget(self.property_view)
        self._page_indices["properties"] = page_idx
        page_idx += 1
        
        # Reports Page (permission-gated)
        if session.has_permission("VIEW_REPORTS"):
            self.reports_page = ReportsPage(session)
            self.content_stack.addWidget(self.reports_page)
            self._page_indices["reports"] = page_idx
            page_idx += 1
        
        # User Management Page (permission-gated)
        if session.has_permission("MANAGE_USERS"):
            from ui.views.user_management_view import UserManagementView
            self.user_management_view = UserManagementView(session)
            self.content_stack.addWidget(self.user_management_view)
            self._page_indices["users"] = page_idx
            page_idx += 1
        
        # Settings Page (permission-gated)
        if session.has_permission("VIEW_SETTINGS"):
            self.settings_page = SettingsPage(session, self)
            self.content_stack.addWidget(self.settings_page)
            self._page_indices["settings"] = page_idx
            page_idx += 1
        
        main_layout.addWidget(sidebar_container, 0)
        main_layout.addWidget(self.content_stack, 1)
        
        self.setCentralWidget(central_widget)
        
        # Toolbar
        self.toolbar = QToolBar("ابزارها")
        self.toolbar.setIconSize(QSize(16, 16))
        self.toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.addToolBar(self.toolbar)
        
        # Property actions (permission-gated)
        if session.has_permission("CREATE_PROPERTY"):
            self.act_add = self.toolbar.addAction("➕ افزودن")
            self.act_add.triggered.connect(self.property_view.add_property)
        else:
            self.act_add = None
            
        if session.has_permission("EDIT_PROPERTY"):
            self.act_edit = self.toolbar.addAction("✏️ ویرایش")
            self.act_edit.triggered.connect(self.property_view.edit_property)
        else:
            self.act_edit = None
            
        if session.has_permission("ARCHIVE_PROPERTY"):
            self.act_archive = self.toolbar.addAction("📁 آرشیو")
            self.act_archive.triggered.connect(self.property_view.archive_property)
        else:
            self.act_archive = None
            
        if session.has_permission("RESTORE_PROPERTY"):
            self.act_restore = self.toolbar.addAction("♻️ بازیابی")
            self.act_restore.triggered.connect(self.property_view.restore_property)
        else:
            self.act_restore = None
        
        self.toolbar.addSeparator()
        self.act_refresh = self.toolbar.addAction("🔄 بروزرسانی")
        self.act_refresh.triggered.connect(self._on_refresh_triggered)
        
        self.toolbar.addSeparator()
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

    def switch_tab(self, sidebar_index):
        if sidebar_index < 0 or sidebar_index >= len(self._sidebar_page_map):
            return
            
        page_name = self._sidebar_page_map[sidebar_index]
        page_idx = self._page_indices.get(page_name, 0)
        self.content_stack.setCurrentIndex(page_idx)
        
        is_property_tab = (page_name == "properties")
        if self.act_add: self.act_add.setVisible(is_property_tab)
        if self.act_edit: self.act_edit.setVisible(is_property_tab)
        if self.act_archive: self.act_archive.setVisible(is_property_tab)
        if self.act_restore: self.act_restore.setVisible(is_property_tab)
        
        self.act_refresh.setVisible(page_name in ("dashboard", "properties"))
        
        if page_name == "dashboard":
            self.dashboard_page.refresh_data()
        elif page_name == "properties":
            self.property_view.refresh_data()
        elif page_name == "users" and hasattr(self, 'user_management_view'):
            self.user_management_view.refresh_data()
            
    def _on_refresh_triggered(self):
        sidebar_index = self.sidebar.currentRow()
        if sidebar_index < 0 or sidebar_index >= len(self._sidebar_page_map):
            return
        page_name = self._sidebar_page_map[sidebar_index]
        if page_name == "dashboard":
            self.dashboard_page.refresh_data()
        elif page_name == "properties":
            self.property_view.refresh_data()
            
    def update_status_bar(self):
        user = self.nav_manager.session.username or "Unknown"
        role = self.nav_manager.session.role or "N/A"
        self.status_bar.showMessage(f"کاربر: {user} | نقش: {role} | نسخه: 2.0.0")

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
