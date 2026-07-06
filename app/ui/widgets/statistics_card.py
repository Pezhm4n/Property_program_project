from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

class StatisticsCard(QFrame):
    def __init__(self, title: str, value: str, icon: str, description: str, parent=None):
        super().__init__(parent)
        self.setObjectName("StatisticsCard")
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Raised)
        
        # Premium styling
        self.setStyleSheet("""
            #StatisticsCard {
                background-color: #2D2D30;
                border: 1px solid #3F3F46;
                border-radius: 8px;
                padding: 12px;
            }
            #StatisticsCard:hover {
                background-color: #323236;
                border-color: #52525B;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Header layout (Icon + Title)
        header_layout = QHBoxLayout()
        self.lbl_icon = QLabel(icon)
        self.lbl_icon.setStyleSheet("font-size: 20px;")
        
        self.lbl_title = QLabel(title)
        self.lbl_title.setStyleSheet("color: #A1A1AA; font-size: 13px; font-weight: bold;")
        self.lbl_title.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        header_layout.addWidget(self.lbl_icon)
        header_layout.addStretch()
        header_layout.addWidget(self.lbl_title)
        layout.addLayout(header_layout)
        
        # Value Label
        self.lbl_value = QLabel(value)
        self.lbl_value.setStyleSheet("color: #FFFFFF; font-size: 24px; font-weight: bold; margin-top: 4px;")
        self.lbl_value.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.lbl_value)
        
        # Description Label
        self.lbl_desc = QLabel(description)
        self.lbl_desc.setStyleSheet("color: #71717A; font-size: 11px; margin-top: 2px;")
        self.lbl_desc.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.lbl_desc)
        
    def update_value(self, new_value: str):
        self.lbl_value.setText(new_value)
