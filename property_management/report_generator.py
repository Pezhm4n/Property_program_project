#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ماژول تولید گزارش‌های پیشرفته برای سیستم مدیریت املاک

این ماژول شامل کلاس‌ها و توابع مورد نیاز برای تولید انواع مختلف گزارش‌ها، 
نمودارها و خروجی‌های متنوع از داده‌های املاک است.
"""

import os
import csv
import logging
import datetime
from typing import List, Dict, Any, Optional, Tuple, Union

# وابستگی‌های خارجی
import pandas as pd
import matplotlib
matplotlib.use('Qt5Agg')  # تنظیم backend برای استفاده با PyQt
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_pdf import PdfPages
import xlsxwriter
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch, cm

# وارد کردن ماژول‌های داخلی سیستم
from . import residential, commercial, land
from .core import get_property_bridge

# تنظیمات لاگینگ
logger = logging.getLogger(__name__)

class ReportGenerator:
    """
    کلاس اصلی برای تولید انواع گزارش‌ها و خروجی‌ها در سیستم مدیریت املاک
    
    این کلاس متدهایی را برای تولید گزارش‌های متنی، نمودارها، 
    فایل‌های Excel و PDF فراهم می‌کند.
    """
    
    def __init__(self, output_dir: str = None):
        """
        سازنده کلاس ReportGenerator
        
        Args:
            output_dir (str, optional): مسیر دایرکتوری برای ذخیره گزارش‌ها
        """
        # تنظیم مسیر خروجی برای گزارش‌ها
        if output_dir is None:
            # دایرکتوری پیش‌فرض برای گزارش‌ها
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.output_dir = os.path.join(base_dir, 'reports')
        else:
            self.output_dir = output_dir
            
        # اطمینان از وجود دایرکتوری خروجی
        os.makedirs(self.output_dir, exist_ok=True)
        
        # ایجاد یک ساختار Property Bridge به عنوان کلاس کمکی
        self.property_bridge = self._init_property_bridge()
        
        # تنظیم زبان انگلیسی برای گزارش‌ها
        self.language = 'en'
        
        logger.info(f"Report generator initialized with output directory: {self.output_dir}")
    
    def _init_property_bridge(self):
        """ایجاد و مقداردهی پل‌های ارتباطی املاک"""
        class PropertyBridge:
            def __init__(self):
                self.residential_bridge = get_property_bridge('residential')()
                self.commercial_bridge = get_property_bridge('commercial')()
                self.land_bridge = get_property_bridge('land')()
        
        return PropertyBridge()
    
    def set_language(self, language_code: str) -> None:
        """
        تنظیم زبان گزارش‌ها
        
        Args:
            language_code (str): کد زبان ('en' برای انگلیسی، 'fa' برای فارسی)
        """
        self.language = language_code
        logger.info(f"Report language set to: {language_code}")
    
    def _get_residential_properties(self, deal_type: int = None, filters: Dict = None) -> List[Dict]:
        """
        دریافت داده‌های املاک مسکونی با امکان اعمال فیلتر
        
        Args:
            deal_type (int, optional): نوع معامله (1: فروش، 2: اجاره)
            filters (Dict, optional): فیلترهای اضافی
            
        Returns:
            List[Dict]: لیست املاک مسکونی
        """
        try:
            all_properties = []
            
            # اگر deal_type مشخص نشده، هم فروش و هم اجاره را بگیر
            deal_types = [1, 2] if deal_type is None else [deal_type]
            
            for dt in deal_types:
                # گرفتن تمام املاک در مناطق مختلف
                all_districts_resp = self.property_bridge.residential_bridge.find_by_district("*", dt)
                if all_districts_resp.get("success", False):
                    all_properties.extend(all_districts_resp.get("properties", []))
            
            # اعمال فیلترها اگر وجود داشته باشند
            if filters:
                filtered_properties = []
                for prop in all_properties:
                    include = True
                    for key, value in filters.items():
                        if key in prop:
                            if isinstance(value, tuple) and len(value) == 2:  # محدوده
                                min_val, max_val = value
                                if not (min_val <= prop[key] <= max_val):
                                    include = False
                                    break
                            elif prop[key] != value:  # مقدار دقیق
                                include = False
                                break
                    if include:
                        filtered_properties.append(prop)
                return filtered_properties
            
            return all_properties
        except Exception as e:
            logger.error(f"Error getting residential properties: {str(e)}")
            return []
    
    def _get_commercial_properties(self, deal_type: int = None, filters: Dict = None) -> List[Dict]:
        """
        دریافت داده‌های املاک تجاری با امکان اعمال فیلتر
        
        Args:
            deal_type (int, optional): نوع معامله (1: فروش، 2: اجاره)
            filters (Dict, optional): فیلترهای اضافی
            
        Returns:
            List[Dict]: لیست املاک تجاری
        """
        try:
            all_properties = []
            
            # اگر deal_type مشخص نشده، هم فروش و هم اجاره را بگیر
            deal_types = [1, 2] if deal_type is None else [deal_type]
            
            for dt in deal_types:
                # گرفتن تمام املاک در مناطق مختلف
                all_districts_resp = self.property_bridge.commercial_bridge.find_by_district("*", dt)
                if all_districts_resp.get("success", False):
                    all_properties.extend(all_districts_resp.get("properties", []))
            
            # اعمال فیلترها اگر وجود داشته باشند
            if filters:
                filtered_properties = []
                for prop in all_properties:
                    include = True
                    for key, value in filters.items():
                        if key in prop:
                            if isinstance(value, tuple) and len(value) == 2:  # محدوده
                                min_val, max_val = value
                                if not (min_val <= prop[key] <= max_val):
                                    include = False
                                    break
                            elif prop[key] != value:  # مقدار دقیق
                                include = False
                                break
                    if include:
                        filtered_properties.append(prop)
                return filtered_properties
            
            return all_properties
        except Exception as e:
            logger.error(f"Error getting commercial properties: {str(e)}")
            return []
    
    def _get_land_properties(self, deal_type: int = None, filters: Dict = None) -> List[Dict]:
        """
        دریافت داده‌های زمین‌ها با امکان اعمال فیلتر
        
        Args:
            deal_type (int, optional): نوع معامله (1: فروش، 2: اجاره)
            filters (Dict, optional): فیلترهای اضافی
            
        Returns:
            List[Dict]: لیست زمین‌ها
        """
        try:
            all_properties = []
            
            # اگر deal_type مشخص نشده، هم فروش و هم اجاره را بگیر
            deal_types = [1, 2] if deal_type is None else [deal_type]
            
            for dt in deal_types:
                # گرفتن تمام املاک در مناطق مختلف
                all_districts_resp = self.property_bridge.land_bridge.find_by_district("*", dt)
                if all_districts_resp.get("success", False):
                    all_properties.extend(all_districts_resp.get("properties", []))
            
            # اعمال فیلترها اگر وجود داشته باشند
            if filters:
                filtered_properties = []
                for prop in all_properties:
                    include = True
                    for key, value in filters.items():
                        if key in prop:
                            if isinstance(value, tuple) and len(value) == 2:  # محدوده
                                min_val, max_val = value
                                if not (min_val <= prop[key] <= max_val):
                                    include = False
                                    break
                            elif prop[key] != value:  # مقدار دقیق
                                include = False
                                break
                    if include:
                        filtered_properties.append(prop)
                return filtered_properties
            
            return all_properties
        except Exception as e:
            logger.error(f"Error getting land properties: {str(e)}")
            return []
    
    def _get_all_properties(self, deal_type: int = None, filters: Dict = None) -> Dict[str, List[Dict]]:
        """
        دریافت تمام انواع املاک با امکان اعمال فیلتر
        
        Args:
            deal_type (int, optional): نوع معامله (1: فروش، 2: اجاره)
            filters (Dict, optional): فیلترهای اضافی
            
        Returns:
            Dict[str, List[Dict]]: دیکشنری شامل لیست همه انواع املاک
        """
        return {
            'residential': self._get_residential_properties(deal_type, filters),
            'commercial': self._get_commercial_properties(deal_type, filters),
            'land': self._get_land_properties(deal_type, filters)
        }
    
    def generate_property_count_report(self, deal_type: int = None, 
                                      output_format: str = 'text',
                                      output_file: str = None) -> Union[str, pd.DataFrame]:
        """
        تولید گزارش تعداد املاک به تفکیک نوع
        
        Args:
            deal_type (int, optional): نوع معامله (1: فروش، 2: اجاره)
            output_format (str, optional): فرمت خروجی ('text', 'csv', 'dataframe')
            output_file (str, optional): نام فایل خروجی
            
        Returns:
            Union[str, pd.DataFrame]: گزارش به فرمت متنی یا دیتافریم pandas
        """
        property_counts = {}
        
        # گرفتن تعداد هر نوع ملک
        properties = self._get_all_properties(deal_type)
        
        for prop_type, props in properties.items():
            property_counts[prop_type] = len(props)
        
        total_count = sum(property_counts.values())
        
        # ساخت دیتافریم
        deal_type_str = "Sale" if deal_type == 1 else "Rent" if deal_type == 2 else "All"
        df = pd.DataFrame({
            'Property Type': ['Residential', 'Commercial', 'Land', 'Total'],
            'Count': [
                property_counts.get('residential', 0),
                property_counts.get('commercial', 0),
                property_counts.get('land', 0),
                total_count
            ],
            'Percentage': [
                f"{property_counts.get('residential', 0) / total_count * 100:.1f}%" if total_count else "0.0%",
                f"{property_counts.get('commercial', 0) / total_count * 100:.1f}%" if total_count else "0.0%",
                f"{property_counts.get('land', 0) / total_count * 100:.1f}%" if total_count else "0.0%",
                "100.0%"
            ]
        })
        
        # خروجی بر اساس فرمت درخواستی
        if output_format == 'dataframe':
            return df
        
        elif output_format == 'csv':
            if output_file is None:
                output_file = os.path.join(self.output_dir, 
                                         f"property_count_report_{deal_type_str.lower()}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
            df.to_csv(output_file, index=False)
            logger.info(f"Property count report saved to {output_file}")
            return output_file
        
        else:  # text
            report_text = f"Property Count Report - Deal Type: {deal_type_str}\n"
            report_text += "=" * 50 + "\n"
            report_text += f"{'Property Type':<15} {'Count':>10} {'Percentage':>15}\n"
            report_text += "-" * 50 + "\n"
            
            for idx, row in df.iterrows():
                report_text += f"{row['Property Type']:<15} {row['Count']:>10} {row['Percentage']:>15}\n"
            
            report_text += "=" * 50 + "\n"
            report_text += f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            
            if output_file is None:
                output_file = os.path.join(self.output_dir, 
                                         f"property_count_report_{deal_type_str.lower()}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_text)
            
            logger.info(f"Property count report saved to {output_file}")
            return report_text
    
    def generate_property_value_report(self, deal_type: int = 1, 
                                      output_format: str = 'text',
                                      output_file: str = None) -> Union[str, pd.DataFrame]:
        """
        تولید گزارش ارزش کل املاک به تفکیک نوع
        
        Args:
            deal_type (int, optional): نوع معامله (1: فروش، 2: اجاره)
            output_format (str, optional): فرمت خروجی ('text', 'csv', 'dataframe')
            output_file (str, optional): نام فایل خروجی
            
        Returns:
            Union[str, pd.DataFrame]: گزارش به فرمت متنی یا دیتافریم pandas
        """
        # فقط برای املاک فروشی معنا دارد
        if deal_type != 1:
            deal_type = 1
            logger.warning("Property value report is only meaningful for sale properties. Setting deal_type to 1.")
        
        properties = self._get_all_properties(deal_type)
        
        # محاسبه ارزش کل
        residential_value = sum(prop.get('sellingPrice', 0) for prop in properties['residential'])
        commercial_value = sum(prop.get('sellingPrice', 0) for prop in properties['commercial'])
        land_value = sum(prop.get('sellingPrice', 0) for prop in properties['land'])
        total_value = residential_value + commercial_value + land_value
        
        # ساخت دیتافریم
        df = pd.DataFrame({
            'Property Type': ['Residential', 'Commercial', 'Land', 'Total'],
            'Total Value': [
                f"${residential_value:,.2f}",
                f"${commercial_value:,.2f}",
                f"${land_value:,.2f}",
                f"${total_value:,.2f}"
            ],
            'Percentage': [
                f"{residential_value / total_value * 100:.1f}%" if total_value else "0.0%",
                f"{commercial_value / total_value * 100:.1f}%" if total_value else "0.0%",
                f"{land_value / total_value * 100:.1f}%" if total_value else "0.0%",
                "100.0%"
            ]
        })
        
        # برای استفاده در محاسبات، مقادیر عددی خام را هم نگه داریم
        df['Raw Value'] = [residential_value, commercial_value, land_value, total_value]
        
        # خروجی بر اساس فرمت درخواستی
        if output_format == 'dataframe':
            return df
        
        elif output_format == 'csv':
            if output_file is None:
                output_file = os.path.join(self.output_dir, 
                                        f"property_value_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
            # ستون Raw Value را حذف می‌کنیم
            df_out = df.drop(columns=['Raw Value'])
            df_out.to_csv(output_file, index=False)
            logger.info(f"Property value report saved to {output_file}")
            return output_file
        
        else:  # text
            report_text = "Property Value Report - Sale Properties\n"
            report_text += "=" * 60 + "\n"
            report_text += f"{'Property Type':<15} {'Total Value':>20} {'Percentage':>15}\n"
            report_text += "-" * 60 + "\n"
            
            for idx, row in df.iterrows():
                report_text += f"{row['Property Type']:<15} {row['Total Value']:>20} {row['Percentage']:>15}\n"
            
            report_text += "=" * 60 + "\n"
            report_text += f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            
            if output_file is None:
                output_file = os.path.join(self.output_dir, 
                                        f"property_value_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_text)
            
            logger.info(f"Property value report saved to {output_file}")
            return report_text
    
    def generate_district_report(self, property_type: str = 'all', deal_type: int = None,
                                output_format: str = 'text',
                                output_file: str = None) -> Union[str, pd.DataFrame]:
        """
        تولید گزارش تعداد املاک به تفکیک منطقه
        
        Args:
            property_type (str, optional): نوع ملک ('residential', 'commercial', 'land', 'all')
            deal_type (int, optional): نوع معامله (1: فروش، 2: اجاره)
            output_format (str, optional): فرمت خروجی ('text', 'csv', 'dataframe')
            output_file (str, optional): نام فایل خروجی
            
        Returns:
            Union[str, pd.DataFrame]: گزارش به فرمت متنی یا دیتافریم pandas
        """
        properties = self._get_all_properties(deal_type)
        district_counts = {}
        
        # جمع‌آوری املاک بر اساس منطقه
        if property_type == 'all' or property_type == 'residential':
            for prop in properties['residential']:
                district = prop.get('district', 'Unknown')
                if district not in district_counts:
                    district_counts[district] = {'residential': 0, 'commercial': 0, 'land': 0, 'total': 0}
                district_counts[district]['residential'] += 1
                district_counts[district]['total'] += 1
        
        if property_type == 'all' or property_type == 'commercial':
            for prop in properties['commercial']:
                district = prop.get('district', 'Unknown')
                if district not in district_counts:
                    district_counts[district] = {'residential': 0, 'commercial': 0, 'land': 0, 'total': 0}
                district_counts[district]['commercial'] += 1
                district_counts[district]['total'] += 1
        
        if property_type == 'all' or property_type == 'land':
            for prop in properties['land']:
                district = prop.get('district', 'Unknown')
                if district not in district_counts:
                    district_counts[district] = {'residential': 0, 'commercial': 0, 'land': 0, 'total': 0}
                district_counts[district]['land'] += 1
                district_counts[district]['total'] += 1
        
        # تبدیل به دیتافریم
        df_data = []
        for district, counts in district_counts.items():
            df_data.append({
                'District': district,
                'Residential': counts['residential'],
                'Commercial': counts['commercial'],
                'Land': counts['land'],
                'Total': counts['total']
            })
        
        # مرتب‌سازی بر اساس تعداد کل نزولی
        df = pd.DataFrame(df_data).sort_values('Total', ascending=False).reset_index(drop=True)
        
        # اضافه کردن سطر مجموع
        total_row = {
            'District': 'Total',
            'Residential': df['Residential'].sum(),
            'Commercial': df['Commercial'].sum(),
            'Land': df['Land'].sum(),
            'Total': df['Total'].sum()
        }
        df = pd.concat([df, pd.DataFrame([total_row])], ignore_index=True)
        
        # عنوان گزارش
        deal_type_str = "Sale" if deal_type == 1 else "Rent" if deal_type == 2 else "All"
        property_type_str = property_type.capitalize() if property_type != 'all' else 'All'
        report_title = f"District Report - {property_type_str} Properties ({deal_type_str})"
        
        # خروجی بر اساس فرمت درخواستی
        if output_format == 'dataframe':
            return df
        
        elif output_format == 'csv':
            if output_file is None:
                output_file = os.path.join(self.output_dir, 
                                        f"district_report_{property_type}_{deal_type_str.lower()}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
            df.to_csv(output_file, index=False)
            logger.info(f"District report saved to {output_file}")
            return output_file
        
        else:  # text
            report_text = f"{report_title}\n"
            report_text += "=" * 70 + "\n"
            report_text += f"{'District':<15} {'Residential':>12} {'Commercial':>12} {'Land':>12} {'Total':>12}\n"
            report_text += "-" * 70 + "\n"
            
            for idx, row in df.iterrows():
                report_text += f"{row['District']:<15} {row['Residential']:>12} {row['Commercial']:>12} {row['Land']:>12} {row['Total']:>12}\n"
            
            report_text += "=" * 70 + "\n"
            report_text += f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            
            if output_file is None:
                output_file = os.path.join(self.output_dir, 
                                        f"district_report_{property_type}_{deal_type_str.lower()}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_text)
            
            logger.info(f"District report saved to {output_file}")
            return report_text
    
    def generate_price_range_report(self, property_type: str = 'all', bins: int = 5,
                                  min_price: int = None, max_price: int = None, num_bins: int = None,
                                  deal_type: int = 1, output_format: str = 'text',
                                  output_file: str = None) -> Union[str, pd.DataFrame]:
        """
        تولید گزارش توزیع املاک بر اساس محدوده قیمتی
        
        Args:
            property_type (str, optional): نوع ملک ('residential', 'commercial', 'land', 'all')
            bins (int, optional): تعداد بازه‌های قیمتی (استفاده نمی‌شود اگر num_bins مقدار داشته باشد)
            min_price (int, optional): حداقل قیمت
            max_price (int, optional): حداکثر قیمت
            num_bins (int, optional): تعداد بازه‌های قیمتی (جایگزین bins)
            deal_type (int, optional): نوع معامله (1: فروش، 2: اجاره، None: همه)
            output_format (str, optional): فرمت خروجی ('text', 'csv', 'dataframe')
            output_file (str, optional): نام فایل خروجی
            
        Returns:
            Union[str, pd.DataFrame]: گزارش به فرمت متنی یا دیتافریم pandas
        """
        # تبدیل پارامتر deal_type از رشته به عدد اگر نیاز است
        if isinstance(deal_type, str):
            if deal_type.lower() == 'sale':
                deal_type = 1
            elif deal_type.lower() == 'rent':
                deal_type = 2
            else:
                deal_type = None
        
        # فقط برای املاک فروشی معنا دارد
        if deal_type != 1 and deal_type is not None:
            logger.warning("Price range report is primarily for sale properties. Setting deal_type to 1.")
            deal_type = 1
            
        properties = self._get_all_properties(deal_type=deal_type)
        
        # جمع‌آوری قیمت‌ها
        prices = []
        labels = []
        
        if property_type == 'all' or property_type == 'residential':
            for prop in properties['residential']:
                price = prop.get('sellingPrice', 0)
                if price > 0:
                    prices.append(price)
                    labels.append('Residential')
        
        if property_type == 'all' or property_type == 'commercial':
            for prop in properties['commercial']:
                price = prop.get('sellingPrice', 0)
                if price > 0:
                    prices.append(price)
                    labels.append('Commercial')
        
        if property_type == 'all' or property_type == 'land':
            for prop in properties['land']:
                price = prop.get('sellingPrice', 0)
                if price > 0:
                    prices.append(price)
                    labels.append('Land')
        
        # اگر داده‌ای نداریم
        if len(prices) == 0:
            logger.warning(f"No price data available for {property_type} properties")
            if output_format == 'dataframe':
                return pd.DataFrame()
            return "No data available for price range report."
        
        # ایجاد دیتافریم
        df = pd.DataFrame({'Price': prices, 'Type': labels})
        
        # محاسبه بازه‌های قیمتی
        if num_bins is not None:
            bins = num_bins
        
        if min_price is not None and max_price is not None:
            # استفاده از حدود قیمت تعیین شده
            bin_ranges = pd.interval_range(start=min_price, end=max_price, periods=bins)
            price_bins = pd.cut(df['Price'], bins=bin_ranges)
        else:
            # محاسبه خودکار بازه‌ها
            min_price = df['Price'].min()
            max_price = df['Price'].max()
            price_bins = pd.cut(df['Price'], bins=bins, precision=0)
        
        price_counts = df.groupby(['Type', price_bins]).size().reset_index(name='Count')
        
        # تغییر نام ستون برای خوانایی بهتر
        price_counts = price_counts.rename(columns={price_bins.name: 'Price Range'})
        
        # محاسبه درصد
        type_totals = df.groupby('Type').size()
        price_counts['Percentage'] = price_counts.apply(
            lambda x: f"{x['Count'] / type_totals[x['Type']] * 100:.1f}%", axis=1
        )
        
        # ایجاد گزارش توصیفی
        property_type_str = property_type.capitalize() if property_type != 'all' else 'All'
        deal_type_str = "Sale" if deal_type == 1 else "Rent" if deal_type == 2 else "All"
        report_title = f"Price Range Report - {property_type_str} Properties ({deal_type_str})"
        
        # خروجی بر اساس فرمت درخواستی
        if output_format == 'dataframe':
            return price_counts
        
        elif output_format == 'csv':
            if output_file is None:
                output_file = os.path.join(self.output_dir, 
                                         f"price_range_report_{property_type}_{deal_type_str.lower()}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
            price_counts.to_csv(output_file, index=False)
            logger.info(f"Price range report saved to {output_file}")
            return output_file
        
        else:  # text
            report_text = f"{report_title}\n"
            report_text += "=" * 70 + "\n"
            report_text += f"{'Type':<15} {'Price Range':<30} {'Count':>10} {'Percentage':>15}\n"
            report_text += "-" * 70 + "\n"
            
            for idx, row in price_counts.iterrows():
                report_text += f"{row['Type']:<15} {str(row['Price Range']):<30} {row['Count']:>10} {row['Percentage']:>15}\n"
            
            report_text += "\nSummary Statistics:\n"
            report_text += "-" * 70 + "\n"
            summary_stats = df.groupby('Type')['Price'].agg(['min', 'max', 'mean', 'median', 'std']).reset_index()
            for idx, row in summary_stats.iterrows():
                report_text += f"Type: {row['Type']}\n"
                report_text += f"  Min Price: ${row['min']:,.2f}\n"
                report_text += f"  Max Price: ${row['max']:,.2f}\n"
                report_text += f"  Average Price: ${row['mean']:,.2f}\n"
                report_text += f"  Median Price: ${row['median']:,.2f}\n"
                report_text += f"  Standard Deviation: ${row['std']:,.2f}\n\n"
            
            report_text += "=" * 70 + "\n"
            report_text += f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            
            if output_file is None:
                output_file = os.path.join(self.output_dir, 
                                         f"price_range_report_{property_type}_{deal_type_str.lower()}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_text)
            
            logger.info(f"Price range report saved to {output_file}")
            return report_text 