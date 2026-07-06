from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt

class EmptyStateWidget(QWidget):
    def __init__(self, message="هیچ داده‌ای برای نمایش وجود ندارد.", hint="برای ثبت داده جدید از نوار ابزار بالا استفاده کنید.", parent=None):
        super().__init__(parent)
        self.setObjectName("EmptyStateWidget")
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Icon/Illustration Placeholder
        self.lbl_icon = QLabel("📂")
        self.lbl_icon.setStyleSheet("font-size: 48px; margin-bottom: 8px;")
        self.lbl_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_icon)
        
        # Primary Message
        self.lbl_message = QLabel(message)
        self.lbl_message.setStyleSheet("color: #FFFFFF; font-size: 16px; font-weight: bold;")
        self.lbl_message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_message)
        
        # Helper hint
        self.lbl_hint = QLabel(hint)
        self.lbl_hint.setStyleSheet("color: #71717A; font-size: 12px; margin-top: 4px;")
        self.lbl_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_hint)
        
        # CSS Styling
        self.setStyleSheet("""
            #EmptyStateWidget {
                background-color: #1E1E1E;
                border: 1px dashed #3F3F46;
                border-radius: 8px;
            }
        """)
