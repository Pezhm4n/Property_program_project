from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QListWidgetItem
from PySide6.QtCore import Qt

class RecentActivityWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("RecentActivityWidget")
        self.setStyleSheet("""
            #RecentActivityWidget {
                background-color: #2D2D30;
                border: 1px solid #3F3F46;
                border-radius: 8px;
                padding: 12px;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        # Title
        title_lbl = QLabel("آخرین فعالیت‌های سیستم")
        title_lbl.setStyleSheet("color: #FFFFFF; font-size: 14px; font-weight: bold; margin-bottom: 8px;")
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(title_lbl)
        
        # List of activities
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("""
            QListWidget {
                background: transparent;
                border: none;
                color: #D4D4D8;
            }
            QListWidget::item {
                border-bottom: 1px solid #3F3F46;
                padding: 8px;
            }
            QListWidget::item:hover {
                background-color: #3F3F46;
                border-radius: 4px;
            }
        """)
        self.list_widget.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        layout.addWidget(self.list_widget)
        
    def update_activities(self, activities: list):
        self.list_widget.clear()
        if not activities:
            item = QListWidgetItem("هیچ فعالیتی ثبت نشده است.")
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.list_widget.addItem(item)
            return
            
        for act in activities:
            # Format: [timestamp] user: action - details
            text = f"[{act.get('timestamp', '')}] {act.get('user', '')}: {act.get('action', '')} ({act.get('details', '')})"
            item = QListWidgetItem(text)
            self.list_widget.addItem(item)
