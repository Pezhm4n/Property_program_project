from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QFrame
from PySide6.QtCore import Qt

class ReportsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ReportsPage")
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        
        # Header
        header = QLabel("گزارش‌ها و تحلیل‌های مالی")
        header.setStyleSheet("color: white; font-size: 22px; font-weight: bold; margin-bottom: 16px;")
        header.setAlignment(Qt.AlignmentFlag.AlignRight)
        main_layout.addWidget(header)
        
        # Sub-header explanation
        desc = QLabel("این بخش در فازهای آینده (Phase 6.3/6.4 Core) فعال خواهد شد. ساختار و نوع گزارش‌های قابل دریافت در زیر مشخص گردیده است:")
        desc.setStyleSheet("color: #A1A1AA; font-size: 13px; margin-bottom: 24px;")
        desc.setAlignment(Qt.AlignmentFlag.AlignRight)
        main_layout.addWidget(desc)
        
        # Grid of future report card slots
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(16)
        
        pdf_card = self.create_placeholder_card("📄 خروجی گزارش PDF", "امکان دریافت لیست فیلتر شده املاک به همراه لوگو و امضای آژانس در قالب PDF جهت پرینت.")
        excel_card = self.create_placeholder_card("📊 خروجی Excel", "دریافت فایل اکسل چندبرگه شامل محاسبات کمیسیون، متراژ کل و تفکیک بر اساس مشاوران.")
        print_card = self.create_placeholder_card("🖨 چاپ مستقیم فیش", "امکان پرینت مستقیم اطلاعات خلاصه ملک به روی فیش پرینتر برای ارائه به مشتری.")
        
        cards_layout.addWidget(pdf_card)
        cards_layout.addWidget(excel_card)
        cards_layout.addWidget(print_card)
        main_layout.addLayout(cards_layout)
        
        main_layout.addStretch()
        
        # Style Sheets
        self.setStyleSheet("""
            #ReportsPage {
                background-color: #1E1E1E;
            }
        """)

    def create_placeholder_card(self, title: str, text: str) -> QFrame:
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #2D2D30;
                border: 1px dashed #3F3F46;
                border-radius: 8px;
                padding: 16px;
            }
            QFrame:hover {
                border-color: #0E7490;
            }
        """)
        
        layout = QVBoxLayout(card)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("color: #38BDF8; font-size: 16px; font-weight: bold; margin-bottom: 8px;")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(lbl_title)
        
        lbl_desc = QLabel(text)
        lbl_desc.setStyleSheet("color: #D4D4D8; font-size: 12px; line-height: 18px;")
        lbl_desc.setWordWrap(True)
        lbl_desc.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(lbl_desc)
        
        # Add a placeholder label "در حال توسعه"
        lbl_badge = QLabel("در حال توسعه (غیرفعال)")
        lbl_badge.setStyleSheet("color: #EF4444; font-size: 10px; font-weight: bold; border: 1px solid #EF4444; border-radius: 4px; padding: 2px 6px; margin-top: 12px;")
        lbl_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_badge, alignment=Qt.AlignmentFlag.AlignLeft)
        
        return card
