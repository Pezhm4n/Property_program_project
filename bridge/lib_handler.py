"""
این ماژول مسئول مدیریت بارگذاری کتابخانه‌ها
"""

import os
import sys
import logging
import ctypes
from importlib import import_module
from typing import Any, Optional, Union

# تنظیم لاگر
logger = logging.getLogger(__name__)

# مسیر فعلی
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)

# مسیر کتابخانه
LIB_PATH = os.path.join(PROJECT_ROOT, 'lib', 'property_lib.dll')

# نمونه کتابخانه
_lib_instance = None
_mock_lib_instance = None
_use_mock = False  # آیا از نسخه موک استفاده شود؟

def find_library_path() -> str:
    """یافتن مسیر کتابخانه C"""
    paths = [
        LIB_PATH,
        os.path.join(PROJECT_ROOT, 'property_lib.dll'),
        os.path.join(os.path.dirname(PROJECT_ROOT), 'lib', 'property_lib.dll'),
        os.path.join(os.getcwd(), 'lib', 'property_lib.dll'),
        os.path.join(os.getcwd(), 'property_lib.dll')
    ]
    
    for path in paths:
        if os.path.exists(path):
            logger.info(f"کتابخانه C در مسیر {path} یافت شد.")
            return path
    
    logger.warning("کتابخانه C یافت نشد.")
    return ""

def load_c_library() -> Optional[Any]:
    """بارگذاری کتابخانه C"""
    lib_path = find_library_path()
    if not lib_path:
        logger.error("مسیر کتابخانه C یافت نشد.")
        return None
    
    try:
        # سعی در بارگذاری کتابخانه
        lib = ctypes.CDLL(lib_path)
        logger.info("کتابخانه C با موفقیت بارگذاری شد.")
        return lib
    except OSError as e:
        logger.error(f"خطا در بارگذاری کتابخانه C: {e}")
        return None

def load_mock_library() -> Any:
    """بارگذاری کتابخانه جایگزین (mock)"""
    try:
        # وارد کردن ماژول mock_lib.py از همین دایرکتوری
        mock_lib = import_module('.mock_lib', package='bridge')
        logger.info("کتابخانه Mock با موفقیت بارگذاری شد.")
        return mock_lib.c_lib
    except ImportError as e:
        logger.error(f"خطا در بارگذاری کتابخانه Mock: {e}")
        sys.exit(1)

def set_use_mock(use_mock: bool = True) -> None:
    """تعیین استفاده از کتابخانه موک"""
    global _use_mock
    _use_mock = use_mock
    logger.info(f"وضعیت استفاده از Mock: {_use_mock}")

def get_lib_instance(force_refresh: bool = False) -> Any:
    """
    دریافت نمونه کتابخانه (اصلی یا موک)
    
    Args:
        force_refresh: آیا نمونه جدید ایجاد شود؟
        
    Returns:
        نمونه کتابخانه C یا mock
    """
    global _lib_instance, _mock_lib_instance, _use_mock
    
    # اگر نمونه قبلی باشد و نیاز به بازسازی نباشد
    if not force_refresh:
        if _use_mock and _mock_lib_instance:
            return _mock_lib_instance
        elif not _use_mock and _lib_instance:
            return _lib_instance
    
    # ابتدا سعی در بارگذاری کتابخانه اصلی
    if not _use_mock:
        _lib_instance = load_c_library()
        if _lib_instance:
            return _lib_instance
        else:
            # اگر بارگذاری کتابخانه C با شکست مواجه شد، به mock تغییر وضعیت می‌دهیم
            logger.warning("استفاده از کتابخانه mock به دلیل عدم بارگذاری کتابخانه C")
            _use_mock = False
    
    # اگر استفاده از mock مجاز باشد
    if _use_mock:
        _mock_lib_instance = load_mock_library()
        return _mock_lib_instance
    
    # اگر هر دو روش شکست بخورد
    logger.error("خطا در بارگذاری هر دو نوع کتابخانه (اصلی و mock)")
    sys.exit(1)

# بارگذاری کتابخانه با شروع ماژول
if __name__ != "__main__":
    try:
        # ابتدا تلاش می‌کنیم کتابخانه اصلی را بارگذاری کنیم
        c_lib = load_c_library()
        if c_lib:
            _lib_instance = c_lib
            _use_mock = False
        else:
            # در صورت عدم موفقیت، از mock استفاده می‌کنیم
            _mock_lib_instance = load_mock_library()
            _use_mock = False
    except Exception as e:
        logger.error(f"خطا در راه‌اندازی lib_handler: {e}")
        _mock_lib_instance = load_mock_library()
        _use_mock = False 