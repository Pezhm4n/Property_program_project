from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton, QLabel, QScrollArea
from PySide6.QtCore import Qt
from ui.widgets.statistics_card import StatisticsCard
from ui.widgets.recent_activity import RecentActivityWidget
from ui.widgets.chart_widget import ChartWidget
from ui.dialogs import show_error_dialog, create_loading_dialog
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'bridge')))
from re_bridge.services import DashboardService

class DashboardPage(QWidget):
    def __init__(self, session_manager, parent=None):
        super().__init__(parent)
        self.session = session_manager
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        
        # Scroll Area for responsive dashboard
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        scroll_content = QWidget()
        scroll_content.setObjectName("dashboardScrollContent")
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        
        # Header Layout
        header_layout = QHBoxLayout()
        self.btn_refresh = QPushButton("🔄 بروزرسانی داشبورد")
        self.btn_refresh.clicked.connect(self.refresh_data)
        
        title_lbl = QLabel("داشبورد مدیریت املاک")
        title_lbl.setObjectName("dashboardTitle")
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        header_layout.addWidget(self.btn_refresh)
        header_layout.addStretch()
        header_layout.addWidget(title_lbl)
        scroll_layout.addLayout(header_layout)
        
        # Grid layout for Stats Cards
        self.card_layout = QGridLayout()
        self.card_layout.setSpacing(12)
        
        self.card_total = StatisticsCard("کل املاک", "0", "🏘", "تعداد کل فایل‌های ثبت شده", self)
        self.card_active = StatisticsCard("املاک فعال", "0", "✅", "املاک آماده معامله", self)
        self.card_archived = StatisticsCard("بایگانی شده", "0", "📁", "املاک فروخته یا اجاره شده", self)
        self.card_users = StatisticsCard("کل کاربران", "0", "👤", "کاربران سیستم", self)
        self.card_agents = StatisticsCard("کل مشاوران", "0", "💼", "کارشناسان فروش فعال", self)
        self.card_last_update = StatisticsCard("آخرین بروزرسانی", "-", "⏱", "زمان آخرین همگام‌سازی", self)
        
        self.card_layout.addWidget(self.card_total, 0, 0)
        self.card_layout.addWidget(self.card_active, 0, 1)
        self.card_layout.addWidget(self.card_archived, 0, 2)
        self.card_layout.addWidget(self.card_users, 1, 0)
        self.card_layout.addWidget(self.card_agents, 1, 1)
        self.card_layout.addWidget(self.card_last_update, 1, 2)
        scroll_layout.addLayout(self.card_layout)
        
        # Charts Layout (Two charts side-by-side)
        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(12)
        self.sales_chart = ChartWidget("روند معاملات فروش (ماهانه)", "bar", self)
        self.sales_chart.setMinimumHeight(350)
        self.rents_chart = ChartWidget("روند معاملات اجاره (ماهانه)", "line", self)
        self.rents_chart.setMinimumHeight(350)
        charts_layout.addWidget(self.sales_chart)
        charts_layout.addWidget(self.rents_chart)
        scroll_layout.addLayout(charts_layout)
        
        # Recent Activity Widget
        self.activity_widget = RecentActivityWidget(self)
        self.activity_widget.setFixedHeight(250)
        scroll_layout.addWidget(self.activity_widget)
        
        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)
        
    def refresh_data(self):
        loading = create_loading_dialog(self, "در حال بارگذاری اطلاعات داشبورد...")
        loading.show()
        try:
            data = DashboardService.get_dashboard_data(self.session.session_token)
            
            # Update stats cards
            self.card_total.update_value(str(data.get("total_properties", 0)))
            self.card_active.update_value(str(data.get("active_properties", 0)))
            self.card_archived.update_value(str(data.get("archived_properties", 0)))
            self.card_users.update_value(str(data.get("total_users", 0)))
            self.card_agents.update_value(str(data.get("total_agents", 0)))
            self.card_last_update.update_value(data.get("last_update", "-"))
            
            # Update activities
            self.activity_widget.update_activities(data.get("recent_activities", []))
            
            # Update charts
            charts = data.get("charts", {})
            self.sales_chart.update_chart_data(charts.get("monthly_sales", []))
            self.rents_chart.update_chart_data(charts.get("monthly_rents", []))
            
        except Exception as e:
            show_error_dialog(self, e)
        finally:
            loading.close()
