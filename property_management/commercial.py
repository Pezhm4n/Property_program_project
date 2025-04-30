"""
کلاس مدیریت املاک تجاری
"""
from .core import ffi, lib
from .property import PropertyManager

class CommercialManager(PropertyManager):
    """
    کلاس مدیریت املاک تجاری
    """
    
    def __init__(self):
        """
        مقداردهی اولیه کلاس مدیریت املاک تجاری
        """
        super().__init__()
    
    def register_sale(self, username, property_data):
        """
        ثبت ملک تجاری برای فروش

        Parameters:
        ----------
        username : str
            نام کاربری ثبت کننده
        property_data : dict
            داده‌های ملک تجاری شامل فیلدهای مورد نیاز

        Returns:
        -------
        bool
            True در صورت موفقیت، False در صورت شکست
        """
        if not self._validate_username(username):
            raise ValueError("نام کاربری نامعتبر است")
        
        # بررسی داده‌های ملک
        if not self._validate_property_data(property_data, is_sale=True):
            raise ValueError("داده‌های ملک تجاری نامعتبر است")
        
        # ایجاد ساختار C برای ملک تجاری
        com_property = self._create_commercial_property_struct(property_data)
        
        # فراخوانی تابع ثبت فروش از کتابخانه C
        result = lib.commercial_register_sale(
            ffi.new("char[]", username.encode('utf-8')),
            com_property
        )
        
        return result == 1
    
    def register_rental(self, username, property_data):
        """
        ثبت ملک تجاری برای اجاره

        Parameters:
        ----------
        username : str
            نام کاربری ثبت کننده
        property_data : dict
            داده‌های ملک تجاری شامل فیلدهای مورد نیاز

        Returns:
        -------
        bool
            True در صورت موفقیت، False در صورت شکست
        """
        if not self._validate_username(username):
            raise ValueError("نام کاربری نامعتبر است")
        
        # بررسی داده‌های ملک
        if not self._validate_property_data(property_data, is_sale=False):
            raise ValueError("داده‌های ملک تجاری نامعتبر است")
        
        # ایجاد ساختار C برای ملک تجاری
        com_property = self._create_commercial_property_struct(property_data)
        
        # فراخوانی تابع ثبت اجاره از کتابخانه C
        result = lib.commercial_register_rental(
            ffi.new("char[]", username.encode('utf-8')),
            com_property
        )
        
        return result == 1
    
    def find_by_district(self, district, deal_type):
        """
        جستجوی املاک تجاری بر اساس منطقه

        Parameters:
        ----------
        district : str
            نام منطقه
        deal_type : int
            نوع معامله (فروش یا اجاره)

        Returns:
        -------
        list
            لیستی از املاک تجاری یافت شده
        """
        if not self._validate_district(district):
            raise ValueError("منطقه نامعتبر است")
        
        if not self._validate_deal_type(deal_type):
            raise ValueError("نوع معامله نامعتبر است")
        
        # تخصیص فضا برای شمارنده
        count_ptr = ffi.new("int*")
        
        # فراخوانی تابع جستجو
        result_ptr = lib.commercial_find_by_district(
            ffi.new("char[]", district.encode('utf-8')),
            deal_type,
            count_ptr
        )
        
        # تبدیل نتایج به لیست پایتون
        count = count_ptr[0]
        return self._convert_to_python_list(result_ptr, count)
    
    def find_by_age(self, min_age, max_age, deal_type):
        """
        جستجوی املاک تجاری بر اساس سن ساختمان

        Parameters:
        ----------
        min_age : int
            حداقل سن ساختمان
        max_age : int
            حداکثر سن ساختمان
        deal_type : int
            نوع معامله (فروش یا اجاره)

        Returns:
        -------
        list
            لیستی از املاک تجاری یافت شده
        """
        if not (isinstance(min_age, int) and min_age >= 0):
            raise ValueError("حداقل سن باید یک عدد صحیح مثبت باشد")
        
        if not (isinstance(max_age, int) and max_age >= min_age):
            raise ValueError("حداکثر سن باید یک عدد صحیح بزرگتر یا مساوی حداقل سن باشد")
        
        if not self._validate_deal_type(deal_type):
            raise ValueError("نوع معامله نامعتبر است")
        
        # تخصیص فضا برای شمارنده
        count_ptr = ffi.new("int*")
        
        # فراخوانی تابع جستجو
        result_ptr = lib.commercial_find_by_age(
            min_age,
            max_age,
            deal_type,
            count_ptr
        )
        
        # تبدیل نتایج به لیست پایتون
        count = count_ptr[0]
        return self._convert_to_python_list(result_ptr, count)
    
    def find_by_area(self, min_area, max_area, deal_type):
        """
        جستجوی املاک تجاری بر اساس مساحت

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
            لیستی از املاک تجاری یافت شده
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
        result_ptr = lib.commercial_find_by_area(
            min_area,
            max_area,
            deal_type,
            count_ptr
        )
        
        # تبدیل نتایج به لیست پایتون
        count = count_ptr[0]
        return self._convert_to_python_list(result_ptr, count)
    
    def find_by_type(self, commercial_type, deal_type):
        """
        جستجوی املاک تجاری بر اساس نوع

        Parameters:
        ----------
        commercial_type : str
            نوع ملک تجاری
        deal_type : int
            نوع معامله (فروش یا اجاره)

        Returns:
        -------
        list
            لیستی از املاک تجاری یافت شده
        """
        if not isinstance(commercial_type, str) or not commercial_type:
            raise ValueError("نوع ملک تجاری نامعتبر است")
        
        if not self._validate_deal_type(deal_type):
            raise ValueError("نوع معامله نامعتبر است")
        
        # تخصیص فضا برای شمارنده
        count_ptr = ffi.new("int*")
        
        # فراخوانی تابع جستجو
        result_ptr = lib.commercial_find_by_type(
            ffi.new("char[]", commercial_type.encode('utf-8')),
            deal_type,
            count_ptr
        )
        
        # تبدیل نتایج به لیست پایتون
        count = count_ptr[0]
        return self._convert_to_python_list(result_ptr, count)
    
    def find_by_price(self, min_price, max_price, deal_type):
        """
        جستجوی املاک تجاری بر اساس قیمت

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
            لیستی از املاک تجاری یافت شده
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
        result_ptr = lib.commercial_find_by_price(
            min_price,
            max_price,
            deal_type,
            count_ptr
        )
        
        # تبدیل نتایج به لیست پایتون
        count = count_ptr[0]
        return self._convert_to_python_list(result_ptr, count)
    
    def find_with_parking(self, deal_type):
        """
        جستجوی املاک تجاری دارای پارکینگ

        Parameters:
        ----------
        deal_type : int
            نوع معامله (فروش یا اجاره)

        Returns:
        -------
        list
            لیستی از املاک تجاری یافت شده
        """
        if not self._validate_deal_type(deal_type):
            raise ValueError("نوع معامله نامعتبر است")
        
        # تخصیص فضا برای شمارنده
        count_ptr = ffi.new("int*")
        
        # فراخوانی تابع جستجو
        result_ptr = lib.commercial_find_with_parking(
            deal_type,
            count_ptr
        )
        
        # تبدیل نتایج به لیست پایتون
        count = count_ptr[0]
        return self._convert_to_python_list(result_ptr, count)
    
    def find_deleted_by_date(self, start_date, end_date, deal_type):
        """
        جستجوی املاک تجاری حذف شده بر اساس بازه زمانی

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
            لیستی از املاک تجاری یافت شده
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
        result_ptr = lib.commercial_find_deleted_by_date(
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
        جستجوی املاک تجاری ثبت شده توسط یک کاربر

        Parameters:
        ----------
        username : str
            نام کاربری
        deal_type : int
            نوع معامله (فروش یا اجاره)

        Returns:
        -------
        list
            لیستی از املاک تجاری یافت شده
        """
        if not self._validate_username(username):
            raise ValueError("نام کاربری نامعتبر است")
        
        if not self._validate_deal_type(deal_type):
            raise ValueError("نوع معامله نامعتبر است")
        
        # تخصیص فضا برای شمارنده
        count_ptr = ffi.new("int*")
        
        # فراخوانی تابع جستجو
        result_ptr = lib.commercial_find_by_user(
            ffi.new("char[]", username.encode('utf-8')),
            deal_type,
            count_ptr
        )
        
        # تبدیل نتایج به لیست پایتون
        count = count_ptr[0]
        return self._convert_to_python_list(result_ptr, count)
    
    def calculate_total_value(self):
        """
        محاسبه مجموع ارزش املاک تجاری فعال برای فروش

        Returns:
        -------
        float
            مجموع ارزش املاک
        """
        return lib.commercial_calculate_total_value()
    
    def _validate_property_data(self, property_data, is_sale=True):
        """
        بررسی اعتبار داده‌های ملک تجاری

        Parameters:
        ----------
        property_data : dict
            داده‌های ملک تجاری
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
            'district', 'buildingAge', 'areaSize', 'hasParking',
            'commercialType', 'ownerName', 'ownerContact', 'description'
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
        
        if not isinstance(property_data.get('buildingAge', 0), int) or property_data.get('buildingAge', 0) < 0:
            return False
        
        if not self._validate_area(property_data.get('areaSize', 0)):
            return False
        
        if not isinstance(property_data.get('hasParking', 0), int) or property_data.get('hasParking', 0) not in [0, 1]:
            return False
        
        if not isinstance(property_data.get('commercialType', ''), str) or not property_data.get('commercialType', ''):
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
    
    def _create_commercial_property_struct(self, property_data):
        """
        ایجاد ساختار ملک تجاری برای استفاده در C

        Parameters:
        ----------
        property_data : dict
            داده‌های ملک تجاری

        Returns:
        -------
        CommercialProperty
            ساختار ملک تجاری
        """
        # ایجاد ساختار جدید
        com_property = ffi.new("CommercialProperty*")
        
        # پر کردن فیلدهای ساختار
        if 'id' in property_data:
            ffi.memmove(com_property.id, property_data['id'].encode('utf-8'), min(len(property_data['id']), 19))
        
        district = property_data.get('district', '')
        ffi.memmove(com_property.district, district.encode('utf-8'), min(len(district), 99))
        
        com_property.isActive = property_data.get('isActive', 1)
        com_property.buildingAge = property_data.get('buildingAge', 0)
        com_property.areaSize = property_data.get('areaSize', 0.0)
        com_property.hasParking = property_data.get('hasParking', 0)
        
        com_type = property_data.get('commercialType', '')
        ffi.memmove(com_property.commercialType, com_type.encode('utf-8'), min(len(com_type), 99))
        
        com_property.sellingPrice = property_data.get('sellingPrice', 0.0)
        com_property.mortgageAmount = property_data.get('mortgageAmount', 0.0)
        com_property.monthlyRentAmount = property_data.get('monthlyRentAmount', 0.0)
        
        reg_date = property_data.get('registrationDate', '')
        ffi.memmove(com_property.registrationDate, reg_date.encode('utf-8'), min(len(reg_date), 19))
        
        update_date = property_data.get('lastUpdateDate', '')
        ffi.memmove(com_property.lastUpdateDate, update_date.encode('utf-8'), min(len(update_date), 19))
        
        owner_name = property_data.get('ownerName', '')
        ffi.memmove(com_property.ownerName, owner_name.encode('utf-8'), min(len(owner_name), 99))
        
        owner_contact = property_data.get('ownerContact', '')
        ffi.memmove(com_property.ownerContact, owner_contact.encode('utf-8'), min(len(owner_contact), 99))
        
        description = property_data.get('description', '')
        ffi.memmove(com_property.description, description.encode('utf-8'), min(len(description), 499))
        
        reg_by = property_data.get('registeredBy', '')
        ffi.memmove(com_property.registeredBy, reg_by.encode('utf-8'), min(len(reg_by), 99))
        
        return com_property[0]
    
    def _convert_to_python_list(self, result_ptr, count):
        """
        تبدیل آرایه‌ای از ساختارهای C به لیست پایتونی

        Parameters:
        ----------
        result_ptr : CommercialProperty*
            اشاره‌گر به آرایه‌ای از ساختارهای ملک تجاری
        count : int
            تعداد عناصر در آرایه

        Returns:
        -------
        list
            لیستی از دیکشنری‌های پایتون حاوی اطلاعات املاک
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
                'buildingAge': prop.buildingAge,
                'areaSize': prop.areaSize,
                'hasParking': prop.hasParking,
                'commercialType': ffi.string(prop.commercialType).decode('utf-8'),
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
        lib.commercial_free_array(result_ptr)
        
        return result_list