#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Bridge module between C core and Python UI.
"""

# Use mock_lib instead of real C library
from .mock_lib import c_lib

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

# Package version
__version__ = '1.0.0'