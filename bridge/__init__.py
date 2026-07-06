#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
پکیج bridge برای ارتباط بین کد پایتون و کتابخانه C
"""

# Use mock_lib instead of real C library
from .lib_handler import get_lib_instance

# Get instance of C library
c_lib = get_lib_instance()

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

from .lib_handler import get_lib_instance, set_use_mock

# Package version
__version__ = '1.0.0'