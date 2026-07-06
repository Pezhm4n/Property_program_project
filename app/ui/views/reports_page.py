from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QFrame, QPushButton, QFileDialog, QMessageBox
from PySide6.QtCore import Qt
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'bridge')))
from re_bridge.services import ReportService
from ui.dialogs import show_error_dialog

class ReportsPage(QWidget):
    def __init__(self, session_manager, parent=None):
        super().__init__(parent)
        self.session = session_manager
        self.setObjectName("ReportsPage")
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(12)
        
        # Header
        self.header = QLabel("گزارش‌ها و خروجی‌های سیستم")
        self.header.setObjectName("reportsHeader")
        self.header.setAlignment(Qt.AlignmentFlag.AlignRight)
        main_layout.addWidget(self.header)
        
        # Sub-header explanation
        self.desc = QLabel("دریافت خروجی‌های معتبر و ساختارهای مستند املاک بر اساس فیلترهای جاری:")
        self.desc.setObjectName("reportsDesc")
        self.desc.setAlignment(Qt.AlignmentFlag.AlignRight)
        main_layout.addWidget(self.desc)
        
        # Grid of report card slots
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(16)
        
        # PDF Card
        self.pdf_card = QFrame()
        self.pdf_card.setObjectName("reportsPdfCard")
        pdf_layout = QVBoxLayout(self.pdf_card)
        pdf_layout.setContentsMargins(16, 16, 16, 16)
        pdf_layout.setSpacing(12)
        
        self.pdf_title = QLabel("📄 خروجی گزارش PDF")
        self.pdf_title.setObjectName("reportsPdfTitle")
        self.pdf_title.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        self.pdf_desc = QLabel("امکان دریافت لیست کامل املاک به همراه جزئیات و ساختار کلی در قالب فایل PDF.")
        self.pdf_desc.setObjectName("reportsPdfDesc")
        self.pdf_desc.setWordWrap(True)
        self.pdf_desc.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        self.btn_pdf = QPushButton("صادرات PDF")
        self.btn_pdf.setObjectName("reportsBtnPdf")
        self.btn_pdf.clicked.connect(self._export_pdf)
        self.btn_pdf.setFixedHeight(36)
        
        pdf_layout.addWidget(self.pdf_title)
        pdf_layout.addWidget(self.pdf_desc)
        pdf_layout.addWidget(self.btn_pdf)
        
        # Excel Card
        self.excel_card = QFrame()
        self.excel_card.setObjectName("reportsExcelCard")
        excel_layout = QVBoxLayout(self.excel_card)
        excel_layout.setContentsMargins(16, 16, 16, 16)
        excel_layout.setSpacing(12)
        
        self.excel_title = QLabel("📊 خروجی Excel")
        self.excel_title.setObjectName("reportsExcelTitle")
        self.excel_title.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        self.excel_desc = QLabel("دریافت فایل اکسل کامل شامل متراژ، قیمت و سایر جزئیات ستونی املاک جهت تحلیل مالی.")
        self.excel_desc.setObjectName("reportsExcelDesc")
        self.excel_desc.setWordWrap(True)
        self.excel_desc.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        self.btn_excel = QPushButton("صادرات Excel")
        self.btn_excel.setObjectName("reportsBtnExcel")
        self.btn_excel.clicked.connect(self._export_excel)
        self.btn_excel.setFixedHeight(36)
        
        excel_layout.addWidget(self.excel_title)
        excel_layout.addWidget(self.excel_desc)
        excel_layout.addWidget(self.btn_excel)
        
        cards_layout.addWidget(self.pdf_card)
        cards_layout.addWidget(self.excel_card)
        main_layout.addLayout(cards_layout)
        
        main_layout.addStretch()

    def _export_pdf(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "ذخیره فایل PDF", "", "PDF Files (*.pdf)")
        if file_path:
            try:
                ReportService.export_properties_pdf(self.session.session_token, file_path)
                QMessageBox.information(self, "موفقیت", "فایل PDF با موفقیت ذخیره شد.")
            except Exception as e:
                show_error_dialog(self, e)

    def _export_excel(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "ذخیره فایل Excel", "", "Excel Files (*.xlsx)")
        if file_path:
            try:
                ReportService.export_properties_excel(self.session.session_token, file_path)
                QMessageBox.information(self, "موفقیت", "فایل Excel با موفقیت ذخیره شد.")
            except Exception as e:
                show_error_dialog(self, e)
