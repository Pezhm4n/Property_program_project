from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtCore import Qt

class StatisticsCard(QFrame):
    def __init__(self, title: str, value: str, icon: str, description: str, parent=None):
        super().__init__(parent)
        self.setObjectName("StatisticsCard")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(6)
        
        # Header layout (Icon + Title)
        header_layout = QHBoxLayout()
        self.lbl_icon = QLabel(icon)
        self.lbl_icon.setObjectName("statIcon")
        self.lbl_icon.setStyleSheet("font-size: 22px;")
        
        self.lbl_title = QLabel(title)
        self.lbl_title.setObjectName("statTitle")
        self.lbl_title.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        header_layout.addWidget(self.lbl_icon)
        header_layout.addStretch()
        header_layout.addWidget(self.lbl_title)
        layout.addLayout(header_layout)
        
        # Value Label
        self.lbl_value = QLabel(value)
        self.lbl_value.setObjectName("statValue")
        self.lbl_value.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.lbl_value)
        
        # Description Label
        self.lbl_desc = QLabel(description)
        self.lbl_desc.setObjectName("statDesc")
        self.lbl_desc.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.lbl_desc)
        
    def update_value(self, new_value: str):
        self.lbl_value.setText(new_value)
