"""
کلاس مدیریت زمین
"""
from .core import ffi, lib
from .property import PropertyManager

class LandManager(PropertyManager):
    """
    کلاس مدیریت زمین
    """
    
    def __init__(self):
        """
        مقداردهی اولیه کلاس مدیریت زمین
        """
        super().__init__()
    
    def register_sale(self, username, property_data):
        """
        ثبت زمین برای فروش

        Parameters:
        ----------
        username : str
            نام کاربری ثبت کننده
        property_data : dict
            داده‌های زمین شامل فیلدهای مورد نیاز

        Returns:
        -------
        bool
            True در صورت موفقیت، False در صورت شکست
        """
        if not self._validate_username(username):
            raise ValueError("نام کاربری نامعتبر است")
        
        # بررسی داده‌های زمین
        if not self._validate_property_data(property_data, is_sale=True):
            raise ValueError("داده‌های زمین نامعتبر است")
        
        # ایجاد ساختار C برای زمین
        land_property = self._create_land_property_struct(property_data)
        
        # فراخوانی تابع ثبت فروش از کتابخانه C
        result = lib.land_register_sale(
            ffi.new("char[]", username.encode('utf-8')),
            land_property
        )
        
        return result == 1
    
    def register_rental(self, username, property_data):
        """
        ثبت زمین برای اجاره

        Parameters:
        ----------
        username : str
            نام کاربری ثبت کننده
        property_data : dict
            داده‌های زمین شامل فیلدهای مورد نیاز

        Returns:
        -------
        bool
            True در صورت موفقیت، False در صورت شکست
        """
        if not self._validate_username(username):
            raise ValueError("نام کاربری نامعتبر است")
        
        # بررسی داده‌های زمین
        if not self._validate_property_data(property_data, is_sale=False):
            raise ValueError("داده‌های زمین نامعتبر است")
        
        # ایجاد ساختار C برای زمین
        land_property = self._create_land_property_struct(property_data)
        
        # فراخوانی تابع ثبت اجاره از کتابخانه C
        result = lib.land_register_rental(
            ffi.new("char[]", username.encode('utf-8')),
            land_property
        )
        
        return result == 1
    
    def find_by_district(self, district, deal_type):
        """
        جستجوی زمین بر اساس منطقه

        Parameters:
        ----------
        district : str
            نام منطقه
        deal_type : int
            نوع معامله (فروش یا اجاره)

        Returns:
        -------
        list
            لیستی از زمین‌های یافت شده
        """
        if not self._validate_district(district):
            raise ValueError("منطقه نامعتبر است")
        
        if not self._validate_deal_type(deal_type):
            raise ValueError("نوع معامله نامعتبر است")
        
        # تخصیص فضا برای شمارنده
        count_ptr = ffi.new("int*")
        
        # فراخوانی تابع جستجو
        result_ptr = lib.land_find_by_district(
            ffi.new("char[]", district.encode('utf-8')),
            deal_type,
            count_ptr
        )
        
        # تبدیل نتایج به لیست پایتون
        count = count_ptr[0]
        return self._convert_to_python_list(result_ptr, count)
    
    def find_by_area(self, min_area, max_area, deal_type):
        """
        جستجوی زمین بر اساس مساحت

        Parameters:
        ----------
        min_area : float
            حداقل مساحت
        max_area : float
            حداکثر مساحت
        deal_type : int
            نوع معامله (فروش یا اجاره)

        Returns:
        -------
        list
            لیستی از زمین‌های یافت شده
        """
        if not (isinstance(min_area, (int, float)) and min_area > 0):
            raise ValueError("حداقل مساحت باید یک عدد مثبت باشد")
        
        if not (isinstance(max_area, (int, float)) and max_area >= min_area):
            raise ValueError("حداکثر مساحت باید یک عدد بزرگتر یا مساوی حداقل مساحت باشد")
        
        if not self._validate_deal_type(deal_type):
            raise ValueError("نوع معامله نامعتبر است")
        
        # تخصیص فضا برای شمارنده
        count_ptr = ffi.new("int*")
        
        # فراخوانی تابع جستجو
        result_ptr = lib.land_find_by_area(
            min_area,
            max_area,
            deal_type,
            count_ptr
        )
        
        # تبدیل نتایج به لیست پایتون
        count = count_ptr[0]
        return self._convert_to_python_list(result_ptr, count)
    
    def find_by_type(self, land_type, deal_type):
        """
        جستجوی زمین بر اساس نوع

        Parameters:
        ----------
        land_type : str
            نوع زمین
        deal_type : int
            نوع معامله (فروش یا اجاره)

        Returns:
        -------
        list
            لیستی از زمین‌های یافت شده
        """
        if not isinstance(land_type, str) or not land_type:
            raise ValueError("نوع زمین نامعتبر است")
        
        if not self._validate_deal_type(deal_type):
            raise ValueError("نوع معامله نامعتبر است")
        
        # تخصیص فضا برای شمارنده
        count_ptr = ffi.new("int*")
        
        # فراخوانی تابع جستجو
        result_ptr = lib.land_find_by_type(
            ffi.new("char[]", land_type.encode('utf-8')),
            deal_type,
            count_ptr
        )
        
        # تبدیل نتایج به لیست پایتون
        count = count_ptr[0]
        return self._convert_to_python_list(result_ptr, count)
    
    def find_by_price(self, min_price, max_price, deal_type):
        """
        جستجوی زمین بر اساس قیمت

        Parameters:
        ----------
        min_price : float
            حداقل قیمت
        max_price : float
            حداکثر قیمت
        deal_type : int
            نوع معامله (فروش یا اجاره)

        Returns:
        -------
        list
            لیستی از زمین‌های یافت شده
        """
        if not (isinstance(min_price, (int, float)) and min_price >= 0):
            raise ValueError("حداقل قیمت باید یک عدد مثبت باشد")
        
        if not (isinstance(max_price, (int, float)) and max_price >= min_price):
            raise ValueError("حداکثر قیمت باید یک عدد بزرگتر یا مساوی حداقل قیمت باشد")
        
        if not self._validate_deal_type(deal_type):
            raise ValueError("نوع معامله نامعتبر است")
        
        # تخصیص فضا برای شمارنده
        count_ptr = ffi.new("int*")
        
        # فراخوانی تابع جستجو
        result_ptr = lib.land_find_by_price(
            min_price,
            max_price,
            deal_type,
            count_ptr
        )
        
        # تبدیل نتایج به لیست پایتون
        count = count_ptr[0]
        return self._convert_to_python_list(result_ptr, count)
    
    def find_by_distance(self, max_distance, deal_type):
        """
        جستجوی زمین بر اساس فاصله از جاده اصلی

        Parameters:
        ----------
        max_distance : float
            حداکثر فاصله از جاده اصلی
        deal_type : int
            نوع معامله (فروش یا اجاره)

        Returns:
        -------
        list
            لیستی از زمین‌های یافت شده
        """
        if not (isinstance(max_distance, (int, float)) and max_distance >= 0):
            raise ValueError("حداکثر فاصله باید یک عدد مثبت باشد")
        
        if not self._validate_deal_type(deal_type):
            raise ValueError("نوع معامله نامعتبر است")
        
        # تخصیص فضا برای شمارنده
        count_ptr = ffi.new("int*")
        
        # فراخوانی تابع جستجو
        result_ptr = lib.land_find_by_distance(
            max_distance,
            deal_type,
            count_ptr
        )
        
        # تبدیل نتایج به لیست پایتون
        count = count_ptr[0]
        return self._convert_to_python_list(result_ptr, count)
    
    def find_with_well(self, deal_type):
        """
        جستجوی زمین‌های دارای چاه

        Parameters:
        ----------
        deal_type : int
            نوع معامله (فروش یا اجاره)

        Returns:
        -------
        list
            لیستی از زمین‌های یافت شده
        """
        if not self._validate_deal_type(deal_type):
            raise ValueError("نوع معامله نامعتبر است")
        
        # تخصیص فضا برای شمارنده
        count_ptr = ffi.new("int*")
        
        # فراخوانی تابع جستجو
        result_ptr = lib.land_find_with_well(
            deal_type,
            count_ptr
        )
        
        # تبدیل نتایج به لیست پایتون
        count = count_ptr[0]
        return self._convert_to_python_list(result_ptr, count)
    
    def find_deleted_by_date(self, start_date, end_date, deal_type):
        """
        جستجوی زمین‌های حذف شده بر اساس بازه زمانی

        Parameters:
        ----------
        start_date : str
            تاریخ شروع (YYYY-MM-DD)
        end_date : str
            تاریخ پایان (YYYY-MM-DD)
        deal_type : int
            نوع معامله (فروش یا اجاره)

        Returns:
        -------
        list
            لیستی از زمین‌های یافت شده
        """
        if not self._validate_date_format(start_date):
            raise ValueError("قالب تاریخ شروع نامعتبر است (YYYY-MM-DD)")
        
        if not self._validate_date_format(end_date):
            raise ValueError("قالب تاریخ پایان نامعتبر است (YYYY-MM-DD)")
        
        if not self._validate_deal_type(deal_type):
            raise ValueError("نوع معامله نامعتبر است")
        
        # تخصیص فضا برای شمارنده
        count_ptr = ffi.new("int*")
        
        # فراخوانی تابع جستجو
        result_ptr = lib.land_find_deleted_by_date(
            ffi.new("char[]", start_date.encode('utf-8')),
            ffi.new("char[]", end_date.encode('utf-8')),
            deal_type,
            count_ptr
        )
        
        # تبدیل نتایج به لیست پایتون
        count = count_ptr[0]
        return self._convert_to_python_list(result_ptr, count)
    
    def find_by_user(self, username, deal_type):
        """
        جستجوی زمین‌های ثبت شده توسط یک کاربر

        Parameters:
        ----------
        username : str
            نام کاربری
        deal_type : int
            نوع معامله (فروش یا اجاره)

        Returns:
        -------
        list
            لیستی از زمین‌های یافت شده
        """
        if not self._validate_username(username):
            raise ValueError("نام کاربری نامعتبر است")
        
        if not self._validate_deal_type(deal_type):
            raise ValueError("نوع معامله نامعتبر است")
        
        # تخصیص فضا برای شمارنده
        count_ptr = ffi.new("int*")
        
        # فراخوانی تابع جستجو
        result_ptr = lib.land_find_by_user(
            ffi.new("char[]", username.encode('utf-8')),
            deal_type,
            count_ptr
        )
        
        # تبدیل نتایج به لیست پایتون
        count = count_ptr[0]
        return self._convert_to_python_list(result_ptr, count)
    
    def calculate_total_value(self):
        """
        محاسبه مجموع ارزش زمین‌های فعال برای فروش

        Returns:
        -------
        float
            مجموع ارزش زمین‌ها
        """
        return lib.land_calculate_total_value()
    
    def _validate_property_data(self, property_data, is_sale=True):
        """
        بررسی اعتبار داده‌های زمین

        Parameters:
        ----------
        property_data : dict
            داده‌های زمین
        is_sale : bool
            آیا برای فروش است؟

        Returns:
        -------
        bool
            True اگر داده‌ها معتبر باشند، False در غیر این صورت
        """
        if not isinstance(property_data, dict):
            return False
        
        # بررسی فیلدهای اجباری
        required_fields = [
            'district', 'landType', 'landArea', 'distanceToMainRoad',
            'hasWell', 'ownerName', 'ownerContact', 'description'
        ]
        
        # فیلدهای اضافی بر اساس نوع معامله
        if is_sale:
            required_fields.append('sellingPrice')
        else:
            required_fields.extend(['mortgageAmount', 'monthlyRentAmount'])
        
        for field in required_fields:
            if field not in property_data:
                return False
        
        # بررسی نوع داده‌ها
        if not self._validate_district(property_data.get('district', '')):
            return False
        
        if not isinstance(property_data.get('landType', ''), str) or not property_data.get('landType', ''):
            return False
        
        if not self._validate_area(property_data.get('landArea', 0)):
            return False
        
        if not isinstance(property_data.get('distanceToMainRoad', 0), (int, float)) or property_data.get('distanceToMainRoad', 0) < 0:
            return False
        
        if not isinstance(property_data.get('hasWell', 0), int) or property_data.get('hasWell', 0) not in [0, 1]:
            return False
        
        # بررسی قیمت بر اساس نوع معامله
        if is_sale:
            if not self._validate_price(property_data.get('sellingPrice', 0)):
                return False
        else:
            if not self._validate_price(property_data.get('mortgageAmount', 0)):
                return False
            if not self._validate_price(property_data.get('monthlyRentAmount', 0)):
                return False
        
        return True
    
    def _create_land_property_struct(self, property_data):
        """
        ایجاد ساختار زمین برای استفاده در C

        Parameters:
        ----------
        property_data : dict
            داده‌های زمین

        Returns:
        -------
        LandProperty
            ساختار زمین
        """
        # ایجاد ساختار جدید
        land_property = ffi.new("LandProperty*")
        
        # پر کردن فیلدهای ساختار
        if 'id' in property_data:
            ffi.memmove(land_property.id, property_data['id'].encode('utf-8'), min(len(property_data['id']), 19))
        
        district = property_data.get('district', '')
        ffi.memmove(land_property.district, district.encode('utf-8'), min(len(district), 99))
        
        land_property.isActive = property_data.get('isActive', 1)
        
        land_type = property_data.get('landType', '')
        ffi.memmove(land_property.landType, land_type.encode('utf-8'), min(len(land_type), 99))
        
        land_property.landArea = property_data.get('landArea', 0.0)
        land_property.distanceToMainRoad = property_data.get('distanceToMainRoad', 0.0)
        land_property.hasWell = property_data.get('hasWell', 0)
        land_property.sellingPrice = property_data.get('sellingPrice', 0.0)
        land_property.mortgageAmount = property_data.get('mortgageAmount', 0.0)
        land_property.monthlyRentAmount = property_data.get('monthlyRentAmount', 0.0)
        
        reg_date = property_data.get('registrationDate', '')
        ffi.memmove(land_property.registrationDate, reg_date.encode('utf-8'), min(len(reg_date), 19))
        
        update_date = property_data.get('lastUpdateDate', '')
        ffi.memmove(land_property.lastUpdateDate, update_date.encode('utf-8'), min(len(update_date), 19))
        
        owner_name = property_data.get('ownerName', '')
        ffi.memmove(land_property.ownerName, owner_name.encode('utf-8'), min(len(owner_name), 99))
        
        owner_contact = property_data.get('ownerContact', '')
        ffi.memmove(land_property.ownerContact, owner_contact.encode('utf-8'), min(len(owner_contact), 99))
        
        description = property_data.get('description', '')
        ffi.memmove(land_property.description, description.encode('utf-8'), min(len(description), 499))
        
        reg_by = property_data.get('registeredBy', '')
        ffi.memmove(land_property.registeredBy, reg_by.encode('utf-8'), min(len(reg_by), 99))
        
        return land_property[0]
    
    def _convert_to_python_list(self, result_ptr, count):
        """
        تبدیل آرایه‌ای از ساختارهای C به لیست پایتونی

        Parameters:
        ----------
        result_ptr : LandProperty*
            اشاره‌گر به آرایه‌ای از ساختارهای زمین
        count : int
            تعداد عناصر در آرایه

        Returns:
        -------
        list
            لیستی از دیکشنری‌های پایتون حاوی اطلاعات زمین‌ها
        """
        if result_ptr == ffi.NULL or count <= 0:
            return []
        
        result_list = []
        
        # تبدیل هر ساختار C به دیکشنری پایتون
        for i in range(count):
            prop = result_ptr[i]
            
            property_dict = {
                'id': ffi.string(prop.id).decode('utf-8'),
                'district': ffi.string(prop.district).decode('utf-8'),
                'isActive': prop.isActive,
                'landType': ffi.string(prop.landType).decode('utf-8'),
                'landArea': prop.landArea,
                'distanceToMainRoad': prop.distanceToMainRoad,
                'hasWell': prop.hasWell,
                'sellingPrice': prop.sellingPrice,
                'mortgageAmount': prop.mortgageAmount,
                'monthlyRentAmount': prop.monthlyRentAmount,
                'registrationDate': ffi.string(prop.registrationDate).decode('utf-8'),
                'lastUpdateDate': ffi.string(prop.lastUpdateDate).decode('utf-8'),
                'ownerName': ffi.string(prop.ownerName).decode('utf-8'),
                'ownerContact': ffi.string(prop.ownerContact).decode('utf-8'),
                'description': ffi.string(prop.description).decode('utf-8'),
                'registeredBy': ffi.string(prop.registeredBy).decode('utf-8')
            }
            
            result_list.append(property_dict)
        
        # آزاد کردن حافظه تخصیص داده شده در سمت C
        lib.land_free_array(result_ptr)
        
        return result_list 