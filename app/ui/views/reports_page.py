from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QFrame, QPushButton, QFileDialog, QMessageBox
from PySide6.QtCore import Qt
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'bridge')))
from re_bridge.services import ReportService

class ReportsPage(QWidget):
    def __init__(self, session_manager, parent=None):
        super().__init__(parent)
        self.session = session_manager
        self.setObjectName("ReportsPage")
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        
        # Header
        header = QLabel("گزارش‌ها و خروجی‌های سیستم")
        header.setStyleSheet("color: white; font-size: 22px; font-weight: bold; margin-bottom: 16px;")
        header.setAlignment(Qt.AlignmentFlag.AlignRight)
        main_layout.addWidget(header)
        
        # Sub-header explanation
        desc = QLabel("دریافت خروجی‌های معتبر و ساختارهای مستند املاک بر اساس فیلترهای جاری:")
        desc.setStyleSheet("color: #A1A1AA; font-size: 13px; margin-bottom: 24px;")
        desc.setAlignment(Qt.AlignmentFlag.AlignRight)
        main_layout.addWidget(desc)
        
        # Grid of report card slots
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(16)
        
        # PDF Card
        pdf_card = QFrame()
        pdf_layout = QVBoxLayout(pdf_card)
        pdf_title = QLabel("📄 خروجی گزارش PDF")
        pdf_title.setStyleSheet("color: #38BDF8; font-size: 16px; font-weight: bold; margin-bottom: 8px;")
        pdf_title.setAlignment(Qt.AlignmentFlag.AlignRight)
        pdf_desc = QLabel("امکان دریافت لیست کامل املاک به همراه جزئیات و ساختار کلی در قالب فایل PDF.")
        pdf_desc.setStyleSheet("color: #D4D4D8; font-size: 12px;")
        pdf_desc.setWordWrap(True)
        pdf_desc.setAlignment(Qt.AlignmentFlag.AlignRight)
        btn_pdf = QPushButton("صادرات PDF")
        btn_pdf.setStyleSheet("background-color: #0284C7; color: white; padding: 6px; border-radius: 4px;")
        btn_pdf.clicked.connect(self._export_pdf)
        pdf_layout.addWidget(pdf_title)
        pdf_layout.addWidget(pdf_desc)
        pdf_layout.addWidget(btn_pdf)
        
        # Excel Card
        excel_card = QFrame()
        excel_layout = QVBoxLayout(excel_card)
        excel_title = QLabel("📊 خروجی Excel")
        excel_title.setStyleSheet("color: #10B981; font-size: 16px; font-weight: bold; margin-bottom: 8px;")
        excel_title.setAlignment(Qt.AlignmentFlag.AlignRight)
        excel_desc = QLabel("دریافت فایل اکسل کامل شامل متراژ، قیمت و سایر جزئیات ستونی املاک جهت تحلیل مالی.")
        excel_desc.setStyleSheet("color: #D4D4D8; font-size: 12px;")
        excel_desc.setWordWrap(True)
        excel_desc.setAlignment(Qt.AlignmentFlag.AlignRight)
        btn_excel = QPushButton("صادرات Excel")
        btn_excel.setStyleSheet("background-color: #059669; color: white; padding: 6px; border-radius: 4px;")
        btn_excel.clicked.connect(self._export_excel)
        excel_layout.addWidget(excel_title)
        excel_layout.addWidget(excel_desc)
        excel_layout.addWidget(btn_excel)
        
        # Styling for cards
        card_style = """
            QFrame {
                background-color: #2D2D30;
                border: 1px solid #3F3F46;
                border-radius: 8px;
                padding: 16px;
            }
            QFrame:hover {
                border-color: #52525B;
            }
        """
        pdf_card.setStyleSheet(card_style)
        excel_card.setStyleSheet(card_style)
        
        cards_layout.addWidget(pdf_card)
        cards_layout.addWidget(excel_card)
        main_layout.addLayout(cards_layout)
        
        main_layout.addStretch()
        
        # Style Sheets
        self.setStyleSheet("""
            #ReportsPage {
                background-color: #1E1E1E;
            }
        """)

    def _export_pdf(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "ذخیره فایل PDF", "", "PDF Files (*.pdf)")
        if file_path:
            try:
                ReportService.export_properties_pdf(self.session.session_token, file_path)
                QMessageBox.information(self, "موفقیت", "فایل PDF با موفقیت ذخیره شد.")
            except Exception as e:
                QMessageBox.critical(self, "خطا", f"خطا در تولید فایل PDF: {e}")

    def _export_excel(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "ذخیره فایل Excel", "", "Excel Files (*.xlsx)")
        if file_path:
            try:
                ReportService.export_properties_excel(self.session.session_token, file_path)
                QMessageBox.information(self, "موفقیت", "فایل Excel با موفقیت ذخیره شد.")
            except Exception as e:
                QMessageBox.critical(self, "خطا", f"خطا در تولید فایل Excel: {e}")
