from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QListWidget, QListWidgetItem
from PySide6.QtCore import Qt

class RecentActivityWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("RecentActivityWidget")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        
        # Title
        self.title_lbl = QLabel("آخرین فعالیت‌های سیستم")
        self.title_lbl.setObjectName("activityTitle")
        self.title_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.title_lbl)
        
        # List of activities
        self.list_widget = QListWidget()
        self.list_widget.setObjectName("activityList")
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
