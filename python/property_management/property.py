"""
کلاس پایه برای مدیریت املاک
"""
from .core import ffi, lib, DEAL_TYPE_SALE, DEAL_TYPE_RENT

class PropertyManager:
    """
    کلاس پایه برای مدیریت املاک که توابع مشترک را فراهم می‌کند.
    """
    
    def __init__(self):
        """
        مقداردهی اولیه کلاس مدیریت املاک
        """
        self._deal_type_sale = DEAL_TYPE_SALE
        self._deal_type_rent = DEAL_TYPE_RENT
    
    @property
    def deal_type_sale(self):
        """
        ثابت برای نوع معامله فروش
        """
        return self._deal_type_sale
    
    @property
    def deal_type_rent(self):
        """
        ثابت برای نوع معامله اجاره
        """
        return self._deal_type_rent
    
    @staticmethod
    def log(message):
        """
        ثبت یک پیام در سیستم لاگ

        Parameters:
        ----------
        message : str
            پیام برای ثبت در لاگ
        """
        lib.property_log(ffi.new("char[]", message.encode('utf-8')))
    
    @staticmethod
    def get_last_error():
        """
        دریافت آخرین خطای رخ داده در سیستم

        Returns:
        -------
        str
            پیام خطای آخرین عملیات ناموفق
        """
        error_ptr = lib.get_last_error()
        if error_ptr == ffi.NULL:
            return None
        return ffi.string(error_ptr).decode('utf-8')
    
    def _validate_date_format(self, date_str):
        """
        بررسی اعتبار قالب تاریخ (YYYY-MM-DD)

        Parameters:
        ----------
        date_str : str
            رشته تاریخ برای بررسی

        Returns:
        -------
        bool
            True اگر تاریخ معتبر باشد، False در غیر این صورت
        """
        if not date_str:
            return False
        
        # قالب ساده برای بررسی YYYY-MM-DD
        parts = date_str.split('-')
        if len(parts) != 3:
            return False
        
        try:
            year, month, day = map(int, parts)
            # بررسی سال، ماه و روز در محدوده معقول
            return (1900 <= year <= 2100 and 1 <= month <= 12 and 1 <= day <= 31)
        except ValueError:
            return False
    
    def _validate_price(self, price):
        """
        بررسی اعتبار قیمت

        Parameters:
        ----------
        price : float
            قیمت برای بررسی

        Returns:
        -------
        bool
            True اگر قیمت معتبر باشد، False در غیر این صورت
        """
        return isinstance(price, (int, float)) and price >= 0
    
    def _validate_area(self, area):
        """
        بررسی اعتبار مساحت

        Parameters:
        ----------
        area : float
            مساحت برای بررسی

        Returns:
        -------
        bool
            True اگر مساحت معتبر باشد، False در غیر این صورت
        """
        return isinstance(area, (int, float)) and area > 0
    
    def _validate_district(self, district):
        """
        بررسی اعتبار منطقه

        Parameters:
        ----------
        district : str
            نام منطقه برای بررسی

        Returns:
        -------
        bool
            True اگر منطقه معتبر باشد، False در غیر این صورت
        """
        return isinstance(district, str) and len(district) > 0
    
    def _validate_username(self, username):
        """
        بررسی اعتبار نام کاربری

        Parameters:
        ----------
        username : str
            نام کاربری برای بررسی

        Returns:
        -------
        bool
            True اگر نام کاربری معتبر باشد، False در غیر این صورت
        """
        return isinstance(username, str) and len(username) > 0
    
    def _validate_deal_type(self, deal_type):
        """
        بررسی اعتبار نوع معامله

        Parameters:
        ----------
        deal_type : int
            نوع معامله برای بررسی

        Returns:
        -------
        bool
            True اگر نوع معامله معتبر باشد، False در غیر این صورت
        """
        return deal_type in [self._deal_type_sale, self._deal_type_rent] 