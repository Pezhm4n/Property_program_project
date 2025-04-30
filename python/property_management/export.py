#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ماژول صدور خروجی برای سیستم مدیریت املاک

این ماژول شامل کلاس‌های مختلف برای صدور خروجی در فرمت‌های مختلف
مانند Excel و PDF است.
"""

import os
import csv
import logging
import datetime
from typing import List, Dict, Any, Optional, Tuple, Union

# وابستگی‌های خارجی
import pandas as pd
import xlsxwriter
from xlsxwriter.utility import xl_rowcol_to_cell
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch, cm
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# تنظیمات لاگینگ
logger = logging.getLogger(__name__)

class BaseExporter:
    """
    کلاس پایه برای تمام صادرکننده‌ها
    """
    
    def __init__(self, output_dir: str = None):
        """
        مقداردهی اولیه کلاس BaseExporter
        
        Args:
            output_dir (str, optional): مسیر دایرکتوری برای ذخیره خروجی‌ها. اگر None باشد،
                                       از دایرکتوری 'reports' در مسیر جاری استفاده می‌شود.
        """
        # تنظیم مسیر خروجی
        if output_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            self.output_dir = os.path.join(base_dir, 'reports')
        else:
            self.output_dir = output_dir
            
        # اطمینان از وجود دایرکتوری خروجی
        os.makedirs(self.output_dir, exist_ok=True)
        
        # متادیتای گزارش
        self.title = "Property Management Report"
        self.author = "Property Management System"
        self.subject = "Property Report"
        self.keywords = "property, real estate, report"
        self.created_at = datetime.datetime.now()
        
        logger.info(f"Exporter initialized with output directory: {self.output_dir}")
    
    def set_metadata(self, title: str = None, author: str = None, 
                   subject: str = None, keywords: str = None) -> None:
        """
        تنظیم متادیتای گزارش
        
        Args:
            title (str, optional): عنوان گزارش
            author (str, optional): نویسنده گزارش
            subject (str, optional): موضوع گزارش
            keywords (str, optional): کلمات کلیدی گزارش
        """
        if title:
            self.title = title
        if author:
            self.author = author
        if subject:
            self.subject = subject
        if keywords:
            self.keywords = keywords
    
    def _get_default_filename(self, name: str, extension: str) -> str:
        """
        ایجاد نام فایل پیش‌فرض با تاریخ و زمان
        
        Args:
            name (str): بخش اصلی نام فایل
            extension (str): پسوند فایل
            
        Returns:
            str: نام فایل کامل
        """
        timestamp = self.created_at.strftime('%Y%m%d_%H%M%S')
        return os.path.join(self.output_dir, f"{name}_{timestamp}.{extension}")
    
    def export(self, data: Union[pd.DataFrame, List[Dict]], filename: str = None) -> str:
        """
        صدور داده‌ها به یک فایل
        
        Args:
            data (Union[pd.DataFrame, List[Dict]]): داده‌ها برای صدور
            filename (str, optional): نام فایل خروجی
            
        Returns:
            str: مسیر فایل ذخیره شده
        """
        raise NotImplementedError("Subclasses must implement export method")


class ExcelExporter(BaseExporter):
    """
    کلاس صدور به فرمت Excel
    """
    
    def __init__(self, output_dir: str = None):
        """
        مقداردهی اولیه کلاس ExcelExporter
        
        Args:
            output_dir (str, optional): مسیر دایرکتوری برای ذخیره خروجی‌ها
        """
        super().__init__(output_dir)
        
        # تنظیمات پیش‌فرض Excel
        self.header_format = None
        self.title_format = None
        self.date_format = None
        self.number_format = None
        self.currency_format = None
        self.percent_format = None
        self.border_format = None
        self.text_wrap_format = None
        self.total_row_format = None
        
        # تنظیمات برگه‌ها
        self.sheet_name = "Sheet1"
        self.freeze_panes = True
        self.autofilter = True
        self.chart_sheet = False  # آیا نمودار در برگه جداگانه رسم شود؟
        
        # تنظیمات اضافی
        self.include_totals = True
        self.adjust_column_width = True
        self.include_metadata = True
        
        logger.info("Excel exporter initialized")
    
    def _setup_formats(self, workbook: xlsxwriter.Workbook) -> None:
        """
        تنظیم فرمت‌های مختلف برای کتاب کار Excel
        
        Args:
            workbook (xlsxwriter.Workbook): کتاب کار Excel
        """
        # فرمت عنوان
        self.title_format = workbook.add_format({
            'bold': True,
            'font_size': 14,
            'align': 'center',
            'valign': 'vcenter',
            'border': 0
        })
        
        # فرمت هدر جدول
        self.header_format = workbook.add_format({
            'bold': True,
            'font_size': 12,
            'align': 'center',
            'valign': 'vcenter',
            'fg_color': '#4F81BD',
            'color': 'white',
            'border': 1
        })
        
        # فرمت تاریخ
        self.date_format = workbook.add_format({
            'num_format': 'yyyy-mm-dd',
            'align': 'center',
            'border': 1
        })
        
        # فرمت عدد
        self.number_format = workbook.add_format({
            'num_format': '#,##0',
            'align': 'right',
            'border': 1
        })
        
        # فرمت پول
        self.currency_format = workbook.add_format({
            'num_format': '$#,##0.00',
            'align': 'right',
            'border': 1
        })
        
        # فرمت درصد
        self.percent_format = workbook.add_format({
            'num_format': '0.0%',
            'align': 'right',
            'border': 1
        })
        
        # فرمت حاشیه
        self.border_format = workbook.add_format({
            'border': 1
        })
        
        # فرمت چند خطی
        self.text_wrap_format = workbook.add_format({
            'text_wrap': True,
            'valign': 'top',
            'border': 1
        })
        
        # فرمت ردیف مجموع
        self.total_row_format = workbook.add_format({
            'bold': True,
            'font_size': 12,
            'align': 'right',
            'fg_color': '#F2F2F2',
            'border': 1,
            'top': 2,
            'bottom': 2
        })
    
    def _create_title_section(self, worksheet, data: pd.DataFrame) -> int:
        """
        ایجاد بخش عنوان در برگه Excel
        
        Args:
            worksheet: برگه Excel
            data (pd.DataFrame): داده‌ها
            
        Returns:
            int: شماره آخرین ردیف اضافه شده
        """
        # اضافه کردن عنوان
        row = 0
        worksheet.merge_range(row, 0, row, len(data.columns) - 1, self.title, self.title_format)
        row += 1
        
        # اضافه کردن تاریخ و زمان تولید
        date_text = f"Generated on: {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
        worksheet.merge_range(row, 0, row, len(data.columns) - 1, date_text, workbook.add_format({
            'align': 'center',
            'italic': True
        }))
        row += 2  # فضای خالی اضافی
        
        return row
    
    def _create_summary_section(self, worksheet, data: pd.DataFrame, start_row: int) -> int:
        """
        ایجاد بخش خلاصه در برگه Excel
        
        Args:
            worksheet: برگه Excel
            data (pd.DataFrame): داده‌ها
            start_row (int): شماره ردیف شروع
            
        Returns:
            int: شماره آخرین ردیف اضافه شده
        """
        row = start_row
        
        # اضافه کردن اطلاعات خلاصه
        worksheet.merge_range(row, 0, row, 1, "Summary Information", workbook.add_format({
            'bold': True,
            'font_size': 12,
            'underline': True
        }))
        row += 1
        
        # تعداد رکوردها
        worksheet.write(row, 0, "Total Records:", workbook.add_format({'bold': True}))
        worksheet.write(row, 1, len(data))
        row += 1
        
        # اطلاعات اضافی خلاصه
        if 'Price' in data.columns or 'Value' in data.columns or 'sellingPrice' in data.columns:
            price_col = next(col for col in ['Price', 'Value', 'sellingPrice'] if col in data.columns)
            
            worksheet.write(row, 0, "Min Price:", workbook.add_format({'bold': True}))
            worksheet.write(row, 1, data[price_col].min(), self.currency_format)
            row += 1
            
            worksheet.write(row, 0, "Max Price:", workbook.add_format({'bold': True}))
            worksheet.write(row, 1, data[price_col].max(), self.currency_format)
            row += 1
            
            worksheet.write(row, 0, "Average Price:", workbook.add_format({'bold': True}))
            worksheet.write(row, 1, data[price_col].mean(), self.currency_format)
            row += 1
        
        row += 1  # فضای خالی اضافی
        return row
    
    def _add_data_table(self, worksheet, data: pd.DataFrame, start_row: int) -> int:
        """
        اضافه کردن جدول داده‌ها به برگه Excel
        
        Args:
            worksheet: برگه Excel
            data (pd.DataFrame): داده‌ها
            start_row (int): شماره ردیف شروع
            
        Returns:
            int: شماره آخرین ردیف اضافه شده
        """
        row = start_row
        
        # نوشتن هدر ستون‌ها
        for col_idx, column in enumerate(data.columns):
            worksheet.write(row, col_idx, column, self.header_format)
        
        # تنظیم یخ زدن پنل‌ها (برای اینکه هدر همیشه قابل مشاهده باشد)
        if self.freeze_panes:
            worksheet.freeze_panes(row + 1, 0)
        
        # نوشتن داده‌ها
        row += 1
        for idx, data_row in data.iterrows():
            for col_idx, column in enumerate(data.columns):
                value = data_row[column]
                
                # اعمال فرمت مناسب بر اساس نوع داده
                if pd.isna(value):
                    worksheet.write(row, col_idx, "", self.border_format)
                
                elif isinstance(value, datetime.datetime) or isinstance(value, datetime.date):
                    worksheet.write_datetime(row, col_idx, value, self.date_format)
                
                elif isinstance(value, (int, float)):
                    if 'price' in column.lower() or 'value' in column.lower() or 'amount' in column.lower():
                        worksheet.write_number(row, col_idx, value, self.currency_format)
                    elif 'percent' in column.lower() or column.lower().endswith('pct'):
                        worksheet.write_number(row, col_idx, value / 100 if value > 1 else value, self.percent_format)
                    else:
                        worksheet.write_number(row, col_idx, value, self.number_format)
                
                elif isinstance(value, str) and len(value) > 50:
                    worksheet.write(row, col_idx, value, self.text_wrap_format)
                
                else:
                    worksheet.write(row, col_idx, value, self.border_format)
            
            row += 1
        
        # اضافه کردن ردیف مجموع
        if self.include_totals:
            for col_idx, column in enumerate(data.columns):
                if col_idx == 0:
                    worksheet.write(row, col_idx, "Total", self.total_row_format)
                elif data[column].dtype in [int, float] and not ('percent' in column.lower() or column.lower().endswith('pct')):
                    worksheet.write_formula(row, col_idx, 
                                         f'=SUM({xl_rowcol_to_cell(start_row + 1, col_idx)}:{xl_rowcol_to_cell(row - 1, col_idx)})',
                                         self.total_row_format)
                else:
                    worksheet.write(row, col_idx, "", self.total_row_format)
            row += 1
        
        # اضافه کردن فیلتر خودکار
        if self.autofilter:
            worksheet.autofilter(start_row, 0, row - 2, len(data.columns) - 1)
        
        return row
    
    def _adjust_column_widths(self, worksheet, data: pd.DataFrame) -> None:
        """
        تنظیم عرض ستون‌ها بر اساس محتوا
        
        Args:
            worksheet: برگه Excel
            data (pd.DataFrame): داده‌ها
        """
        if not self.adjust_column_width:
            return
        
        # تنظیم عرض ستون‌ها
        for col_idx, column in enumerate(data.columns):
            max_len = len(str(column)) + 2  # عرض پیش‌فرض بر اساس هدر
            
            # بررسی عرض مورد نیاز برای هر سلول
            for value in data[column].dropna():
                if isinstance(value, (int, float)):
                    max_len = max(max_len, len(f"{value:,.2f}") + 2)
                else:
                    cell_len = len(str(value))
                    if cell_len > 100:  # برای متن‌های طولانی محدودیت قائل می‌شویم
                        max_len = max(max_len, 50)
                    else:
                        max_len = max(max_len, cell_len + 2)
            
            worksheet.set_column(col_idx, col_idx, max_len)
    
    def export(self, data: Union[pd.DataFrame, List[Dict]], filename: str = None) -> str:
        """
        صدور داده‌ها به یک فایل Excel
        
        Args:
            data (Union[pd.DataFrame, List[Dict]]): داده‌ها برای صدور
            filename (str, optional): نام فایل خروجی
            
        Returns:
            str: مسیر فایل ذخیره شده
        """
        try:
            # تبدیل به دیتافریم اگر لازم باشد
            if not isinstance(data, pd.DataFrame):
                data = pd.DataFrame(data)
            
            # ایجاد نام فایل اگر ارائه نشده باشد
            if filename is None:
                filename = self._get_default_filename("report", "xlsx")
            elif not filename.lower().endswith('.xlsx'):
                filename += '.xlsx'
            
            # اطمینان از وجود مسیر کامل
            if not os.path.isabs(filename):
                filename = os.path.join(self.output_dir, filename)
            
            # ایجاد دایرکتوری اگر وجود نداشته باشد
            os.makedirs(os.path.dirname(os.path.abspath(filename)), exist_ok=True)
            
            # ایجاد کتاب کار Excel
            with xlsxwriter.Workbook(filename) as workbook:
                # تنظیم متادیتا
                if self.include_metadata:
                    workbook.set_properties({
                        'title': self.title,
                        'author': self.author,
                        'subject': self.subject,
                        'keywords': self.keywords,
                        'created': self.created_at
                    })
                
                # تنظیم فرمت‌ها
                self._setup_formats(workbook)
                
                # ایجاد برگه اصلی
                worksheet = workbook.add_worksheet(self.sheet_name)
                
                # ایجاد بخش عنوان
                row = self._create_title_section(worksheet, data)
                
                # ایجاد بخش خلاصه
                row = self._create_summary_section(worksheet, data, row)
                
                # اضافه کردن جدول داده
                row = self._add_data_table(worksheet, data, row)
                
                # تنظیم عرض ستون‌ها
                self._adjust_column_widths(worksheet, data)
            
            logger.info(f"Excel report exported to {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Error exporting to Excel: {str(e)}")
            return ""


class PDFExporter(BaseExporter):
    """
    کلاس صدور به فرمت PDF
    """
    
    def __init__(self, output_dir: str = None):
        """
        مقداردهی اولیه کلاس PDFExporter
        
        Args:
            output_dir (str, optional): مسیر دایرکتوری برای ذخیره خروجی‌ها
        """
        super().__init__(output_dir)
        
        # تنظیمات PDF
        self.pagesize = A4
        self.margin = 1 * cm
        self.styles = getSampleStyleSheet()
        
        # تنظیم استایل‌های اضافی
        self._setup_styles()
        
        # تنظیمات صفحه‌بندی
        self.include_toc = False  # فهرست مطالب
        self.include_page_numbers = True
        self.include_header_footer = True
        
        # تنظیمات اضافی
        self.table_repeat_rows = 1  # تعداد ردیف‌های هدر که باید در هر صفحه تکرار شوند
        
        logger.info("PDF exporter initialized")
    
    def _setup_styles(self) -> None:
        """
        تنظیم استایل‌های مختلف برای PDF
        """
        # استایل عنوان اصلی
        self.styles.add(ParagraphStyle(
            name='Title',
            parent=self.styles['Title'],
            fontSize=16,
            alignment=TA_CENTER,
            spaceAfter=12
        ))
        
        # استایل زیرعنوان
        self.styles.add(ParagraphStyle(
            name='Subtitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            alignment=TA_CENTER,
            spaceAfter=10
        ))
        
        # استایل هدر جدول
        self.styles.add(ParagraphStyle(
            name='TableHeader',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=TA_CENTER,
            textColor=colors.white,
            backColor=colors.darkblue,
            borderColor=colors.black,
            borderWidth=1
        ))
        
        # استایل پاورقی
        self.styles.add(ParagraphStyle(
            name='Footer',
            parent=self.styles['Normal'],
            fontSize=8,
            alignment=TA_CENTER,
            textColor=colors.gray
        ))
        
        # استایل توضیحات
        self.styles.add(ParagraphStyle(
            name='Note',
            parent=self.styles['Italic'],
            fontSize=9,
            alignment=TA_LEFT,
            textColor=colors.darkgray
        ))
    
    def _create_header_footer(self, canvas, doc) -> None:
        """
        ایجاد سربرگ و پاورقی در هر صفحه
        
        Args:
            canvas: بوم PDF
            doc: سند PDF
        """
        canvas.saveState()
        
        # اضافه کردن سربرگ
        if self.include_header_footer:
            header_text = self.title
            canvas.setFont('Helvetica-Bold', 10)
            canvas.drawString(self.margin, doc.height + self.margin * 2, header_text)
            canvas.line(self.margin, doc.height + self.margin * 1.5, 
                       doc.width + self.margin, doc.height + self.margin * 1.5)
        
        # اضافه کردن پاورقی
        if self.include_header_footer:
            footer_text = f"Generated by {self.author} on {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
            canvas.setFont('Helvetica', 8)
            canvas.drawString(self.margin, self.margin * 0.5, footer_text)
            canvas.line(self.margin, self.margin, 
                       doc.width + self.margin, self.margin)
        
        # اضافه کردن شماره صفحه
        if self.include_page_numbers:
            page_num = canvas.getPageNumber()
            page_text = f"Page {page_num}"
            canvas.drawRightString(doc.width + self.margin, self.margin * 0.5, page_text)
        
        canvas.restoreState()
    
    def _create_table_style(self, num_cols: int) -> TableStyle:
        """
        ایجاد استایل جدول
        
        Args:
            num_cols (int): تعداد ستون‌ها
            
        Returns:
            TableStyle: استایل جدول
        """
        # استایل پایه
        style = [
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (num_cols - 1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (num_cols - 1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            
            # استایل ردیف‌های زوج و فرد (برای خوانایی بهتر)
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            
            # استایل حاشیه خارجی جدول
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            
            # استایل ردیف مجموع در انتها
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('LINEABOVE', (0, -1), (-1, -1), 1, colors.black),
        ]
        
        # اضافه کردن استایل تکرار هدر در هر صفحه
        if self.table_repeat_rows > 0:
            style.append(('REPEATROWS', 0, self.table_repeat_rows - 1))
        
        return TableStyle(style)
    
    def _format_cell_data(self, value: Any) -> str:
        """
        قالب‌بندی داده‌های سلول برای نمایش در PDF
        
        Args:
            value (Any): مقدار سلول
            
        Returns:
            str: متن قالب‌بندی شده
        """
        if pd.isna(value):
            return ""
        
        elif isinstance(value, (int, float)):
            if isinstance(value, int):
                return f"{value:,d}"
            else:
                return f"{value:,.2f}"
        
        elif isinstance(value, (datetime.datetime, datetime.date)):
            return value.strftime('%Y-%m-%d')
        
        else:
            return str(value)
    
    def _create_summary_section(self, data: pd.DataFrame) -> List:
        """
        ایجاد بخش خلاصه در PDF
        
        Args:
            data (pd.DataFrame): داده‌ها
            
        Returns:
            List: لیست عناصر flowable برای اضافه کردن به سند
        """
        elements = []
        
        # ایجاد بخش خلاصه
        elements.append(Paragraph("Summary Information", self.styles['Heading2']))
        elements.append(Spacer(1, 0.2 * cm))
        
        # تعداد رکوردها
        summary_data = [
            ["Total Records:", f"{len(data)}"]
        ]
        
        # اطلاعات اضافی خلاصه
        if 'Price' in data.columns or 'Value' in data.columns or 'sellingPrice' in data.columns:
            price_col = next(col for col in ['Price', 'Value', 'sellingPrice'] if col in data.columns)
            
            summary_data.extend([
                ["Min Price:", f"${data[price_col].min():,.2f}"],
                ["Max Price:", f"${data[price_col].max():,.2f}"],
                ["Average Price:", f"${data[price_col].mean():,.2f}"]
            ])
        
        # ایجاد جدول خلاصه
        summary_table = Table(summary_data, colWidths=[4 * cm, 5 * cm])
        summary_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ]))
        
        elements.append(summary_table)
        elements.append(Spacer(1, 0.5 * cm))
        
        return elements
    
    def _create_data_table(self, data: pd.DataFrame) -> List:
        """
        ایجاد جدول داده‌ها در PDF
        
        Args:
            data (pd.DataFrame): داده‌ها
            
        Returns:
            List: لیست عناصر flowable برای اضافه کردن به سند
        """
        elements = []
        
        # عنوان جدول
        elements.append(Paragraph("Data Table", self.styles['Heading2']))
        elements.append(Spacer(1, 0.2 * cm))
        
        # تبدیل دیتافریم به لیست برای ایجاد جدول
        table_data = [list(data.columns)]  # ردیف هدر
        
        # اضافه کردن داده‌ها
        for idx, row in data.iterrows():
            table_data.append([self._format_cell_data(row[col]) for col in data.columns])
        
        # اضافه کردن ردیف مجموع
        total_row = ["Total"]
        for col in data.columns[1:]:
            if data[col].dtype in [int, float]:
                total_row.append(self._format_cell_data(data[col].sum()))
            else:
                total_row.append("")
        table_data.append(total_row)
        
        # محاسبه عرض ستون‌ها
        col_widths = []
        available_width = self.pagesize[0] - (2 * self.margin)
        
        for col in data.columns:
            # برای ستون‌هایی که متن طولانی دارند، عرض بیشتری اختصاص می‌دهیم
            if data[col].dtype == object and data[col].str.len().max() > 50:
                col_widths.append(available_width * 0.3)  # 30% عرض موجود
            else:
                col_widths.append(None)  # تقسیم متناسب
        
        # ایجاد جدول
        table = Table(table_data, repeatRows=self.table_repeat_rows, colWidths=col_widths)
        table.setStyle(self._create_table_style(len(data.columns)))
        
        elements.append(table)
        elements.append(Spacer(1, 0.5 * cm))
        
        return elements
    
    def export(self, data: Union[pd.DataFrame, List[Dict]], filename: str = None) -> str:
        """
        صدور داده‌ها به یک فایل PDF
        
        Args:
            data (Union[pd.DataFrame, List[Dict]]): داده‌ها برای صدور
            filename (str, optional): نام فایل خروجی
            
        Returns:
            str: مسیر فایل ذخیره شده
        """
        try:
            # تبدیل به دیتافریم اگر لازم باشد
            if not isinstance(data, pd.DataFrame):
                data = pd.DataFrame(data)
            
            # ایجاد نام فایل اگر ارائه نشده باشد
            if filename is None:
                filename = self._get_default_filename("report", "pdf")
            elif not filename.lower().endswith('.pdf'):
                filename += '.pdf'
            
            # اطمینان از وجود مسیر کامل
            if not os.path.isabs(filename):
                filename = os.path.join(self.output_dir, filename)
            
            # ایجاد دایرکتوری اگر وجود نداشته باشد
            os.makedirs(os.path.dirname(os.path.abspath(filename)), exist_ok=True)
            
            # ایجاد سند PDF
            doc = SimpleDocTemplate(
                filename,
                pagesize=self.pagesize,
                leftMargin=self.margin,
                rightMargin=self.margin,
                topMargin=self.margin * 3,  # فضای بیشتر برای سربرگ
                bottomMargin=self.margin * 2  # فضای بیشتر برای پاورقی
            )
            
            # لیست عناصر قابل جاری
            elements = []
            
            # اضافه کردن عنوان اصلی
            elements.append(Paragraph(self.title, self.styles['Title']))
            elements.append(Paragraph(
                f"Generated on {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}",
                self.styles['Italic']
            ))
            elements.append(Spacer(1, 1 * cm))
            
            # اضافه کردن بخش خلاصه
            elements.extend(self._create_summary_section(data))
            
            # اضافه کردن شکست صفحه
            elements.append(PageBreak())
            
            # اضافه کردن جدول داده‌ها
            elements.extend(self._create_data_table(data))
            
            # ایجاد PDF با سربرگ و پاورقی
            doc.build(elements, onFirstPage=self._create_header_footer, onLaterPages=self._create_header_footer)
            
            logger.info(f"PDF report exported to {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Error exporting to PDF: {str(e)}")
            return ""


# تابع کمکی برای استفاده سریع از صادرکننده‌ها
def export_data(data: Union[pd.DataFrame, List[Dict]], format: str = 'excel', 
               filename: str = None, output_dir: str = None, **kwargs) -> str:
    """
    صدور داده‌ها به فرمت مشخص شده
    
    Args:
        data (Union[pd.DataFrame, List[Dict]]): داده‌ها برای صدور
        format (str, optional): فرمت خروجی ('excel', 'pdf')
        filename (str, optional): نام فایل خروجی
        output_dir (str, optional): مسیر دایرکتوری برای ذخیره خروجی‌ها
        **kwargs: پارامترهای اضافی برای صادرکننده
        
    Returns:
        str: مسیر فایل ذخیره شده
    """
    if format.lower() == 'excel':
        exporter = ExcelExporter(output_dir)
    elif format.lower() == 'pdf':
        exporter = PDFExporter(output_dir)
    else:
        logger.error(f"Unknown export format: {format}")
        return ""
    
    # تنظیم متادیتا اگر ارائه شده باشد
    if 'title' in kwargs or 'author' in kwargs or 'subject' in kwargs or 'keywords' in kwargs:
        exporter.set_metadata(
            title=kwargs.get('title'),
            author=kwargs.get('author'),
            subject=kwargs.get('subject'),
            keywords=kwargs.get('keywords')
        )
    
    # اعمال تنظیمات اضافی
    for key, value in kwargs.items():
        if hasattr(exporter, key):
            setattr(exporter, key, value)
    
    # صدور داده‌ها
    return exporter.export(data, filename) 