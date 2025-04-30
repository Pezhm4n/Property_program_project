#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ماژول property_management

بسته اصلی برنامه مدیریت املاک که تمام ماژول‌های سیستم را در بر می‌گیرد.
"""

__version__ = '1.0.0'

# وارد کردن پل ارتباطی با کتابخانه C به طوری که به راحتی قابل استفاده باشد
from .bridge import get_library_instance

# تعریف نسخه به صورت عمومی برای استفاده در برنامه
VERSION = __version__

from .property import PropertyManager
from .residential import ResidentialManager
from .commercial import CommercialManager
from .land import LandManager
from .user import UserManager 