#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ماژول تولید نمودارهای آماری برای سیستم مدیریت املاک

این ماژول شامل کلاس‌های مختلف برای تولید انواع نمودارهای آماری
مانند نمودار میله‌ای، دایره‌ای و خطی است.
"""

import os
import logging
import matplotlib
matplotlib.use('Qt5Agg')  # تنظیم backend برای استفاده با PyQt
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple, Union, Callable
from datetime import datetime, timedelta
import seaborn as sns

# برای پشتیبانی از زبان فارسی در نمودارها
plt.rcParams['font.family'] = 'DejaVu Sans'

# تنظیمات لاگینگ
logger = logging.getLogger(__name__)

class BaseChart:
    """
    کلاس پایه برای تمام نمودارها
    """
    
    def __init__(self, title: str = '', figsize: Tuple[int, int] = (10, 6), dpi: int = 100):
        """
        مقداردهی اولیه کلاس BaseChart
        
        Args:
            title (str, optional): عنوان نمودار
            figsize (Tuple[int, int], optional): اندازه نمودار (عرض، ارتفاع) به اینچ
            dpi (int, optional): وضوح نمودار (نقطه در اینچ)
        """
        self.title = title
        self.figsize = figsize
        self.dpi = dpi
        self.fig = None
        self.ax = None
        
        # ایجاد Figure و Axes
        self.create_figure()
        
        # تنظیم سبک
        self._set_style()
    
    def create_figure(self) -> None:
        """
        ایجاد Figure و Axes جدید
        """
        self.fig, self.ax = plt.subplots(figsize=self.figsize, dpi=self.dpi)
        self.fig.tight_layout(pad=3.0)
        self.ax.set_title(self.title, fontsize=14, pad=20)
    
    def _set_style(self) -> None:
        """
        تنظیم سبک پیش‌فرض نمودار
        """
        # تنظیم سبک seaborn برای ظاهر زیباتر
        sns.set_style("whitegrid")
        
        # تنظیم فونت‌ها
        plt.rcParams['font.size'] = 11
        plt.rcParams['axes.titlesize'] = 14
        plt.rcParams['axes.labelsize'] = 12
        plt.rcParams['xtick.labelsize'] = 10
        plt.rcParams['ytick.labelsize'] = 10
        plt.rcParams['legend.fontsize'] = 10
    
    def save(self, output_path: str, format: str = 'png') -> str:
        """
        ذخیره نمودار در یک فایل
        
        Args:
            output_path (str): مسیر فایل خروجی
            format (str, optional): فرمت فایل ('png', 'pdf', 'svg', 'jpg')
            
        Returns:
            str: مسیر فایل ذخیره شده
        """
        try:
            # اطمینان از وجود دایرکتوری
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            
            # تنظیم اندازه نهایی
            self.fig.tight_layout()
            
            # ذخیره فایل
            self.fig.savefig(output_path, format=format, bbox_inches='tight', dpi=self.dpi)
            logger.info(f"Chart saved to {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error saving chart: {str(e)}")
            return ""
    
    def get_figure(self) -> Figure:
        """
        دریافت شیء Figure
        
        Returns:
            Figure: شیء Figure برای استفاده در matplotlib
        """
        return self.fig
    
    def get_canvas(self) -> FigureCanvas:
        """
        دریافت Canvas برای استفاده در PyQt
        
        Returns:
            FigureCanvas: شیء FigureCanvas برای استفاده در PyQt
        """
        return FigureCanvas(self.fig)
    
    def get_toolbar(self, parent: Any) -> NavigationToolbar:
        """
        دریافت Toolbar برای استفاده در PyQt
        
        Args:
            parent: ویجت والد برای toolbar
            
        Returns:
            NavigationToolbar: شیء NavigationToolbar برای استفاده در PyQt
        """
        return NavigationToolbar(self.get_canvas(), parent)
    
    def close(self) -> None:
        """
        بستن نمودار و آزادسازی منابع
        """
        plt.close(self.fig)


class BarChart(BaseChart):
    """
    کلاس نمودار میله‌ای
    """
    
    def __init__(self, title: str = '', figsize: Tuple[int, int] = (10, 6), dpi: int = 100,
                is_horizontal: bool = False, stacked: bool = False):
        """
        مقداردهی اولیه کلاس BarChart
        
        Args:
            title (str, optional): عنوان نمودار
            figsize (Tuple[int, int], optional): اندازه نمودار (عرض، ارتفاع) به اینچ
            dpi (int, optional): وضوح نمودار (نقطه در اینچ)
            is_horizontal (bool, optional): آیا نمودار افقی باشد؟
            stacked (bool, optional): آیا نمودار انباشته باشد؟
        """
        super().__init__(title, figsize, dpi)
        self.is_horizontal = is_horizontal
        self.stacked = stacked
    
    def plot(self, data: Union[pd.DataFrame, Dict], x_column: str = None, y_column: str = None,
            color_column: str = None, color_map: str = 'viridis',
            xlabel: str = '', ylabel: str = '', show_values: bool = True,
            rotation: int = 0, grid: bool = True, legend: bool = True) -> 'BarChart':
        """
        رسم نمودار میله‌ای
        
        Args:
            data (Union[pd.DataFrame, Dict]): داده‌ها برای رسم
            x_column (str, optional): نام ستون برای محور x (اگر data دیتافریم باشد)
            y_column (str, optional): نام ستون برای محور y (اگر data دیتافریم باشد)
            color_column (str, optional): نام ستون برای گروه‌بندی رنگ‌ها
            color_map (str, optional): نام نقشه رنگی
            xlabel (str, optional): برچسب محور x
            ylabel (str, optional): برچسب محور y
            show_values (bool, optional): آیا مقادیر روی نمودار نمایش داده شوند؟
            rotation (int, optional): چرخش برچسب‌های محور x
            grid (bool, optional): آیا خطوط شبکه نمایش داده شوند؟
            legend (bool, optional): آیا راهنما نمایش داده شود؟
            
        Returns:
            BarChart: خود شیء برای زنجیره‌سازی فراخوانی‌ها
        """
        try:
            # تبدیل دیکشنری به دیتافریم اگر لازم باشد
            if isinstance(data, dict):
                df = pd.DataFrame(list(data.items()), columns=['Category', 'Value'])
                x_column = 'Category'
                y_column = 'Value'
            else:
                df = data
            
            # اگر color_column تعیین شده، از آن برای گروه‌بندی استفاده می‌کنیم
            if color_column:
                grouped = df.groupby([x_column, color_column])[y_column].sum().unstack()
                
                if self.is_horizontal:
                    grouped.plot(kind='barh', stacked=self.stacked, ax=self.ax, colormap=color_map)
                else:
                    grouped.plot(kind='bar', stacked=self.stacked, ax=self.ax, colormap=color_map)
            else:
                if self.is_horizontal:
                    df.plot(kind='barh', x=x_column, y=y_column, ax=self.ax, color=plt.cm.get_cmap(color_map)(0.5))
                else:
                    df.plot(kind='bar', x=x_column, y=y_column, ax=self.ax, color=plt.cm.get_cmap(color_map)(0.5))
            
            # تنظیم برچسب‌ها
            self.ax.set_xlabel(xlabel)
            self.ax.set_ylabel(ylabel)
            
            # نمایش مقادیر روی نمودار
            if show_values:
                if color_column and self.stacked:
                    # حالت خاص: نمودار انباشته با گروه‌بندی رنگی
                    for i, container in enumerate(self.ax.containers):
                        for j, bar in enumerate(container):
                            if self.is_horizontal:
                                width = bar.get_width()
                                if width > 0:
                                    self.ax.text(bar.get_x() + width/2, bar.get_y() + bar.get_height()/2, 
                                               f'{width:,.0f}', ha='center', va='center', 
                                               color='white', fontweight='bold')
                            else:
                                height = bar.get_height()
                                if height > 0:
                                    self.ax.text(bar.get_x() + bar.get_width()/2, bar.get_y() + height/2, 
                                               f'{height:,.0f}', ha='center', va='center', 
                                               color='white', fontweight='bold')
                else:
                    # حالت عادی
                    for i, p in enumerate(self.ax.patches):
                        if self.is_horizontal:
                            width = p.get_width()
                            self.ax.text(width + (width * 0.01), p.get_y() + p.get_height()/2, 
                                       f'{width:,.0f}', ha='left', va='center')
                        else:
                            height = p.get_height()
                            self.ax.text(p.get_x() + p.get_width()/2, height + (height * 0.01), 
                                       f'{height:,.0f}', ha='center', va='bottom')
            
            # تنظیم چرخش برچسب‌های محور x
            plt.xticks(rotation=rotation)
            
            # تنظیم خطوط شبکه
            self.ax.grid(grid, axis='y' if self.is_horizontal else 'x', linestyle='--', alpha=0.7)
            
            # نمایش راهنما
            if legend and color_column:
                self.ax.legend(title=color_column, loc='best')
            
            # به‌روزرسانی چیدمان
            self.fig.tight_layout()
            
            return self
        except Exception as e:
            logger.error(f"Error creating bar chart: {str(e)}")
            return self


class PieChart(BaseChart):
    """
    کلاس نمودار دایره‌ای
    """
    
    def __init__(self, title: str = '', figsize: Tuple[int, int] = (8, 8), dpi: int = 100,
                donut: bool = False):
        """
        مقداردهی اولیه کلاس PieChart
        
        Args:
            title (str, optional): عنوان نمودار
            figsize (Tuple[int, int], optional): اندازه نمودار (عرض، ارتفاع) به اینچ
            dpi (int, optional): وضوح نمودار (نقطه در اینچ)
            donut (bool, optional): آیا نمودار دونات باشد؟
        """
        super().__init__(title, figsize, dpi)
        self.donut = donut
    
    def plot(self, data: Union[pd.DataFrame, Dict], labels_column: str = None, values_column: str = None,
            colors: Union[str, List] = 'viridis', explode: List[float] = None, 
            shadow: bool = False, startangle: int = 90,
            autopct: str = '%1.1f%%', pctdistance: float = 0.85,
            labeldistance: float = 1.1, show_values: bool = True,
            show_percent: bool = True) -> 'PieChart':
        """
        رسم نمودار دایره‌ای
        
        Args:
            data (Union[pd.DataFrame, Dict]): داده‌ها برای رسم
            labels_column (str, optional): نام ستون برای برچسب‌ها (اگر data دیتافریم باشد)
            values_column (str, optional): نام ستون برای مقادیر (اگر data دیتافریم باشد)
            colors (Union[str, List], optional): رنگ‌ها یا نام نقشه رنگی
            explode (List[float], optional): مقادیر جدایی برای هر قطعه از نمودار
            shadow (bool, optional): آیا سایه نمایش داده شود؟
            startangle (int, optional): زاویه شروع نمودار
            autopct (str, optional): فرمت نمایش درصدها
            pctdistance (float, optional): فاصله نمایش درصدها از مرکز
            labeldistance (float, optional): فاصله نمایش برچسب‌ها از مرکز
            show_values (bool, optional): آیا مقادیر روی نمودار نمایش داده شوند؟
            show_percent (bool, optional): آیا درصدها روی نمودار نمایش داده شوند؟
            
        Returns:
            PieChart: خود شیء برای زنجیره‌سازی فراخوانی‌ها
        """
        try:
            # تبدیل دیکشنری به دیتافریم اگر لازم باشد
            if isinstance(data, dict):
                labels = list(data.keys())
                values = list(data.values())
            else:
                # بررسی خالی بودن دیتافریم
                if data.empty:
                    logger.warning("داده‌ها برای رسم نمودار دایره‌ای خالی هستند")
                    self.ax.text(0.5, 0.5, 'داده‌ای برای نمایش وجود ندارد',
                             horizontalalignment='center',
                             verticalalignment='center',
                             transform=self.ax.transAxes,
                             fontsize=12)
                    return self
                
                # بررسی وجود ستون‌های مورد نیاز
                if labels_column not in data.columns or values_column not in data.columns:
                    missing = []
                    if labels_column not in data.columns:
                        missing.append(f"ستون برچسب '{labels_column}'")
                    if values_column not in data.columns:
                        missing.append(f"ستون مقادیر '{values_column}'")
                    
                    error_msg = f"ستون‌های مورد نیاز یافت نشدند: {', '.join(missing)}"
                    logger.error(error_msg)
                    
                    self.ax.text(0.5, 0.5, error_msg,
                             horizontalalignment='center',
                             verticalalignment='center',
                             transform=self.ax.transAxes,
                             fontsize=10, wrap=True)
                    return self
                
                df = data
                labels = df[labels_column].tolist()
                values = df[values_column].tolist()
            
            # بررسی خالی بودن لیست مقادیر یا برچسب‌ها
            if not labels or not values:
                logger.warning("لیست برچسب‌ها یا مقادیر خالی است")
                self.ax.text(0.5, 0.5, 'داده‌ای برای نمایش وجود ندارد',
                         horizontalalignment='center',
                         verticalalignment='center',
                         transform=self.ax.transAxes,
                         fontsize=12)
                return self
            
            # بررسی صفر بودن تمام مقادیر
            if sum(values) == 0:
                logger.warning("مجموع مقادیر صفر است و نمی‌توان نمودار دایره‌ای رسم کرد")
                self.ax.text(0.5, 0.5, 'مجموع مقادیر صفر است',
                         horizontalalignment='center',
                         verticalalignment='center',
                         transform=self.ax.transAxes,
                         fontsize=12)
                return self
            
            # بررسی آیا نیاز به explode است
            if explode is None:
                explode = [0] * len(labels)
            
            # تعیین رنگ‌ها
            if isinstance(colors, str):
                cmap = plt.cm.get_cmap(colors, len(labels))
                colors = [cmap(i) for i in range(len(labels))]
            
            # تنظیم نمایش درصدها و مقادیر
            if show_values and show_percent:
                # نمایش هم درصد و هم مقدار
                def make_autopct(values):
                    def my_autopct(pct):
                        total = sum(values)
                        val = int(round(pct*total/100.0))
                        return f'{pct:.1f}%\n({val:,})'
                    return my_autopct
                autopct = make_autopct(values)
            elif show_values and not show_percent:
                # فقط نمایش مقدار (بدون درصد)
                def make_autopct(values):
                    def my_autopct(pct):
                        total = sum(values)
                        val = int(round(pct*total/100.0))
                        return f'({val:,})'
                    return my_autopct
                autopct = make_autopct(values)
            elif show_percent and not show_values:
                # فقط نمایش درصد (بدون مقدار)
                autopct = '%1.1f%%'
            else:
                # هیچ کدام نمایش داده نشود
                autopct = None
            
            # رسم نمودار دایره‌ای
            logger.debug(f"رسم نمودار دایره‌ای با داده‌های: برچسب‌ها={labels}, مقادیر={values}")
            wedges, texts, autotexts = self.ax.pie(
                values,
                explode=explode,
                labels=labels,
                colors=colors,
                autopct=autopct,
                shadow=shadow,
                startangle=startangle,
                pctdistance=pctdistance,
                labeldistance=labeldistance
            )
            
            # تنظیم فونت و رنگ متن‌ها
            for text in texts:
                text.set_fontsize(10)
            
            if autopct is not None:
                for autotext in autotexts:
                    autotext.set_fontsize(9)
                    autotext.set_fontweight('bold')
            
            # اگر نمودار دونات باشد، یک دایره سفید در وسط اضافه می‌کنیم
            if self.donut:
                center_circle = plt.Circle((0, 0), 0.5, fc='white')
                self.ax.add_artist(center_circle)
                
                # اضافه کردن مجموع به وسط نمودار دونات
                total = sum(values)
                self.ax.text(0, 0, f'Total\n{total:,}', 
                          horizontalalignment='center',
                          verticalalignment='center', 
                          fontsize=12, fontweight='bold')
            
            # تنظیم نسبت ابعاد برابر
            self.ax.axis('equal')
            
            # به‌روزرسانی چیدمان
            self.fig.tight_layout()
            
            return self
        except Exception as e:
            logger.error(f"Error creating pie chart: {str(e)}")
            return self


class LineChart(BaseChart):
    """
    کلاس نمودار خطی
    """
    
    def __init__(self, title: str = '', figsize: Tuple[int, int] = (10, 6), dpi: int = 100,
                marker: str = 'o', linestyle: str = '-'):
        """
        مقداردهی اولیه کلاس LineChart
        
        Args:
            title (str, optional): عنوان نمودار
            figsize (Tuple[int, int], optional): اندازه نمودار (عرض، ارتفاع) به اینچ
            dpi (int, optional): وضوح نمودار (نقطه در اینچ)
            marker (str, optional): نشانگر نقاط داده
            linestyle (str, optional): سبک خط ('solid', 'dashed', 'dotted', 'dashdot')
        """
        super().__init__(title, figsize, dpi)
        self.marker = marker
        self.linestyle = linestyle
    
    def plot(self, data: Union[pd.DataFrame, Dict], x_column: str = None, y_column: str = None,
            color_column: str = None, color_map: str = 'viridis',
            xlabel: str = '', ylabel: str = '', show_points: bool = True,
            show_grid: bool = True, legend: bool = True, 
            date_format: str = None) -> 'LineChart':
        """
        رسم نمودار خطی
        
        Args:
            data (Union[pd.DataFrame, Dict]): داده‌ها برای رسم
            x_column (str, optional): نام ستون برای محور x (اگر data دیتافریم باشد)
            y_column (str, optional): نام ستون برای محور y (اگر data دیتافریم باشد)
            color_column (str, optional): نام ستون برای گروه‌بندی رنگ‌ها
            color_map (str, optional): نام نقشه رنگی
            xlabel (str, optional): برچسب محور x
            ylabel (str, optional): برچسب محور y
            show_points (bool, optional): آیا نقاط داده نمایش داده شوند؟
            show_grid (bool, optional): آیا خطوط شبکه نمایش داده شوند؟
            legend (bool, optional): آیا راهنما نمایش داده شود؟
            date_format (str, optional): فرمت نمایش تاریخ‌ها در محور x
            
        Returns:
            LineChart: خود شیء برای زنجیره‌سازی فراخوانی‌ها
        """
        try:
            # تبدیل دیکشنری به دیتافریم اگر لازم باشد
            if isinstance(data, dict):
                df = pd.DataFrame(list(data.items()), columns=['X', 'Y'])
                x_column = 'X'
                y_column = 'Y'
            else:
                df = data
            
            # تنظیم نشانگر نقاط
            marker = self.marker if show_points else None
            
            # اگر color_column تعیین شده، از آن برای گروه‌بندی استفاده می‌کنیم
            if color_column:
                grouped = df.groupby(color_column)
                for name, group in grouped:
                    self.ax.plot(group[x_column], group[y_column], 
                               marker=marker, linestyle=self.linestyle,
                               label=name)
            else:
                self.ax.plot(df[x_column], df[y_column], 
                          marker=marker, linestyle=self.linestyle,
                          color=plt.cm.get_cmap(color_map)(0.5))
            
            # تنظیم فرمت تاریخ اگر محور x تاریخ باشد
            if date_format and pd.api.types.is_datetime64_any_dtype(df[x_column]):
                date_formatter = mdates.DateFormatter(date_format)
                self.ax.xaxis.set_major_formatter(date_formatter)
                # چرخش برچسب‌های محور x برای خوانایی بهتر
                plt.xticks(rotation=45)
            
            # تنظیم برچسب‌ها
            self.ax.set_xlabel(xlabel)
            self.ax.set_ylabel(ylabel)
            
            # تنظیم خطوط شبکه
            self.ax.grid(show_grid, linestyle='--', alpha=0.7)
            
            # نمایش راهنما
            if legend and color_column:
                self.ax.legend(title=color_column, loc='best')
            
            # به‌روزرسانی چیدمان
            self.fig.tight_layout()
            
            return self
        except Exception as e:
            logger.error(f"Error creating line chart: {str(e)}")
            return self


# تابع کمکی برای استفاده سریع از نمودارها
def create_chart(chart_type: str, data: Union[pd.DataFrame, Dict], **kwargs) -> BaseChart:
    """
    ایجاد یک نمودار با نوع مشخص شده
    
    Args:
        chart_type (str): نوع نمودار ('bar', 'pie', 'line')
        data (Union[pd.DataFrame, Dict]): داده‌ها برای رسم
        **kwargs: پارامترهای اضافی مربوط به نوع نمودار
        
    Returns:
        BaseChart: شیء نمودار ایجاد شده
    """
    chart_types = {
        'bar': BarChart,
        'pie': PieChart,
        'line': LineChart
    }
    
    chart_class = chart_types.get(chart_type.lower())
    if not chart_class:
        logger.error(f"Unknown chart type: {chart_type}")
        return None
    
    # استخراج پارامترهای مقداردهی اولیه
    init_params = {}
    for param in ['title', 'figsize', 'dpi']:
        if param in kwargs:
            init_params[param] = kwargs.pop(param)
    
    # اضافه کردن پارامترهای خاص هر نوع نمودار
    if chart_type.lower() == 'bar':
        for param in ['is_horizontal', 'stacked']:
            if param in kwargs:
                init_params[param] = kwargs.pop(param)
    elif chart_type.lower() == 'pie':
        if 'donut' in kwargs:
            init_params['donut'] = kwargs.pop('donut')
    elif chart_type.lower() == 'line':
        for param in ['marker', 'linestyle']:
            if param in kwargs:
                init_params[param] = kwargs.pop(param)
    
    # ایجاد نمودار و رسم آن
    chart = chart_class(**init_params)
    chart.plot(data, **kwargs)
    
    return chart 