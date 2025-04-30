#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
این ماژول پکیج ارتباطی بین هسته برنامه C و رابط کاربری پایتون را تعریف می‌کند.
"""

from .property_bridge import (
    register_property, 
    search_properties, 
    calculate_total_value,
    PROPERTY_TYPE_RESIDENTIAL,
    PROPERTY_TYPE_COMMERCIAL,
    PROPERTY_TYPE_LAND,
    DEAL_TYPE_SALE,
    DEAL_TYPE_RENT
)

# نسخه پکیج
__version__ = '1.0.0' 