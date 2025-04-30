"""
کلاس مدیریت املاک مسکونی
"""
from .core import ffi, lib
from .property import PropertyManager

class ResidentialManager(PropertyManager):
    """
    کلاس مدیریت املاک مسکونی
    """
    
    def __init__(self):
        """
        مقداردهی اولیه کلاس مدیریت املاک مسکونی
        """
        super().__init__()
    
    def register_sale(self, username, property_data):
        """
        ثبت ملک مسکونی برای فروش

        Parameters:
        ----------
        username : str
            نام کاربری ثبت کننده
        property_data : dict
            داده‌های ملک مسکونی شامل فیلدهای مورد نیاز

        Returns:
        -------
        bool
            True در صورت موفقیت، False در صورت شکست
        """
        if not self._validate_username(username):
            raise ValueError("نام کاربری نامعتبر است")
        
        # بررسی داده‌های ملک
        if not self._validate_property_data(property_data, is_sale=True):
            raise ValueError("داده‌های ملک مسکونی نامعتبر است")
        
        # ایجاد ساختار C برای ملک مسکونی
        res_property = self._create_residential_property_struct(property_data)
        
        # فراخوانی تابع ثبت فروش از کتابخانه C
        result = lib.residential_register_sale(
            ffi.new("char[]", username.encode('utf-8')),
            res_property
        )
        
        return result == 1
    
    def register_rental(self, username, property_data):
        """
        ثبت ملک مسکونی برای اجاره

        Parameters:
        ----------
        username : str
            نام کاربری ثبت کننده
        property_data : dict
            داده‌های ملک مسکونی شامل فیلدهای مورد نیاز

        Returns:
        -------
        bool
            True در صورت موفقیت، False در صورت شکست
        """
        if not self._validate_username(username):
            raise ValueError("نام کاربری نامعتبر است")
        
        # بررسی داده‌های ملک
        if not self._validate_property_data(property_data, is_sale=False):
            raise ValueError("داده‌های ملک مسکونی نامعتبر است")
        
        # ایجاد ساختار C برای ملک مسکونی
        res_property = self._create_residential_property_struct(property_data)
        
        # فراخوانی تابع ثبت اجاره از کتابخانه C
        result = lib.residential_register_rental(
            ffi.new("char[]", username.encode('utf-8')),
            res_property
        )
        
        return result == 1
    
    def find_by_district(self, district, deal_type):
        """
        جستجوی املاک مسکونی بر اساس منطقه

        Parameters:
        ----------
        district : str
            نام منطقه
        deal_type : int
            نوع معامله (فروش یا اجاره)

        Returns:
        -------
        list
            لیستی از املاک مسکونی یافت شده
        """
        if not self._validate_district(district):
            raise ValueError("منطقه نامعتبر است")
        
        if not self._validate_deal_type(deal_type):
            raise ValueError("نوع معامله نامعتبر است")
        
        # تخصیص فضا برای شمارنده
        count_ptr = ffi.new("int*")
        
        # فراخوانی تابع جستجو
        result_ptr = lib.residential_find_by_district(
            ffi.new("char[]", district.encode('utf-8')),
            deal_type,
            count_ptr
        )
        
        # تبدیل نتایج به لیست پایتون
        count = count_ptr[0]
        return self._convert_to_python_list(result_ptr, count)
    
    def find_by_age(self, min_age, max_age, deal_type):
        """
        جستجوی املاک مسکونی بر اساس سن ساختمان

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
            لیستی از املاک مسکونی یافت شده
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
        result_ptr = lib.residential_find_by_age(
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
        جستجوی املاک مسکونی بر اساس مساحت

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
            لیستی از املاک مسکونی یافت شده
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
        result_ptr = lib.residential_find_by_area(
            min_area,
            max_area,
            deal_type,
            count_ptr
        )
        
        # تبدیل نتایج به لیست پایتون
        count = count_ptr[0]
        return self._convert_to_python_list(result_ptr, count)
    
    def find_by_bedrooms(self, min_bedrooms, max_bedrooms, deal_type):
        """
        جستجوی املاک مسکونی بر اساس تعداد اتاق خواب

        Parameters:
        ----------
        min_bedrooms : int
            حداقل تعداد اتاق خواب
        max_bedrooms : int
            حداکثر تعداد اتاق خواب
        deal_type : int
            نوع معامله (فروش یا اجاره)

        Returns:
        -------
        list
            لیستی از املاک مسکونی یافت شده
        """
        if not (isinstance(min_bedrooms, int) and min_bedrooms >= 0):
            raise ValueError("حداقل تعداد اتاق خواب باید یک عدد صحیح مثبت باشد")
        
        if not (isinstance(max_bedrooms, int) and max_bedrooms >= min_bedrooms):
            raise ValueError("حداکثر تعداد اتاق خواب باید یک عدد صحیح بزرگتر یا مساوی حداقل تعداد اتاق خواب باشد")
        
        if not self._validate_deal_type(deal_type):
            raise ValueError("نوع معامله نامعتبر است")
        
        # تخصیص فضا برای شمارنده
        count_ptr = ffi.new("int*")
        
        # فراخوانی تابع جستجو
        result_ptr = lib.residential_find_by_bedrooms(
            min_bedrooms,
            max_bedrooms,
            deal_type,
            count_ptr
        )
        
        # تبدیل نتایج به لیست پایتون
        count = count_ptr[0]
        return self._convert_to_python_list(result_ptr, count)
    
    def find_by_price(self, min_price, max_price, deal_type):
        """
        جستجوی املاک مسکونی بر اساس قیمت

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
            لیستی از املاک مسکونی یافت شده
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
        result_ptr = lib.residential_find_by_price(
            min_price,
            max_price,
            deal_type,
            count_ptr
        )
        
        # تبدیل نتایج به لیست پایتون
        count = count_ptr[0]
        return self._convert_to_python_list(result_ptr, count)
    
    def find_by_floor(self, min_floor, max_floor, deal_type):
        """
        جستجوی املاک مسکونی بر اساس طبقه

        Parameters:
        ----------
        min_floor : int
            حداقل طبقه
        max_floor : int
            حداکثر طبقه
        deal_type : int
            نوع معامله (فروش یا اجاره)

        Returns:
        -------
        list
            لیستی از املاک مسکونی یافت شده
        """
        if not (isinstance(min_floor, int)):
            raise ValueError("حداقل طبقه باید یک عدد صحیح باشد")
        
        if not (isinstance(max_floor, int) and max_floor >= min_floor):
            raise ValueError("حداکثر طبقه باید یک عدد صحیح بزرگتر یا مساوی حداقل طبقه باشد")
        
        if not self._validate_deal_type(deal_type):
            raise ValueError("نوع معامله نامعتبر است")
        
        # تخصیص فضا برای شمارنده
        count_ptr = ffi.new("int*")
        
        # فراخوانی تابع جستجو
        result_ptr = lib.residential_find_by_floor(
            min_floor,
            max_floor,
            deal_type,
            count_ptr
        )
        
        # تبدیل نتایج به لیست پایتون
        count = count_ptr[0]
        return self._convert_to_python_list(result_ptr, count)
    
    def find_with_elevator(self, deal_type):
        """
        جستجوی املاک مسکونی دارای آسانسور

        Parameters:
        ----------
        deal_type : int
            نوع معامله (فروش یا اجاره)

        Returns:
        -------
        list
            لیستی از املاک مسکونی یافت شده
        """
        if not self._validate_deal_type(deal_type):
            raise ValueError("نوع معامله نامعتبر است")
        
        # تخصیص فضا برای شمارنده
        count_ptr = ffi.new("int*")
        
        # فراخوانی تابع جستجو
        result_ptr = lib.residential_find_with_elevator(
            deal_type,
            count_ptr
        )
        
        # تبدیل نتایج به لیست پایتون
        count = count_ptr[0]
        return self._convert_to_python_list(result_ptr, count)
    
    def find_with_parking(self, deal_type):
        """
        جستجوی املاک مسکونی دارای پارکینگ

        Parameters:
        ----------
        deal_type : int
            نوع معامله (فروش یا اجاره)

        Returns:
        -------
        list
            لیستی از املاک مسکونی یافت شده
        """
        if not self._validate_deal_type(deal_type):
            raise ValueError("نوع معامله نامعتبر است")
        
        # تخصیص فضا برای شمارنده
        count_ptr = ffi.new("int*")
        
        # فراخوانی تابع جستجو
        result_ptr = lib.residential_find_with_parking(
            deal_type,
            count_ptr
        )
        
        # تبدیل نتایج به لیست پایتون
        count = count_ptr[0]
        return self._convert_to_python_list(result_ptr, count)
    
    def find_with_storage(self, deal_type):
        """
        جستجوی املاک مسکونی دارای انباری

        Parameters:
        ----------
        deal_type : int
            نوع معامله (فروش یا اجاره)

        Returns:
        -------
        list
            لیستی از املاک مسکونی یافت شده
        """
        if not self._validate_deal_type(deal_type):
            raise ValueError("نوع معامله نامعتبر است")
        
        # تخصیص فضا برای شمارنده
        count_ptr = ffi.new("int*")
        
        # فراخوانی تابع جستجو
        result_ptr = lib.residential_find_with_storage(
            deal_type,
            count_ptr
        )
        
        # تبدیل نتایج به لیست پایتون
        count = count_ptr[0]
        return self._convert_to_python_list(result_ptr, count)
    
    def find_deleted_by_date(self, start_date, end_date, deal_type):
        """
        جستجوی املاک مسکونی حذف شده بر اساس بازه زمانی

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
            لیستی از املاک مسکونی یافت شده
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
        result_ptr = lib.residential_find_deleted_by_date(
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
        جستجوی املاک مسکونی ثبت شده توسط یک کاربر

        Parameters:
        ----------
        username : str
            نام کاربری
        deal_type : int
            نوع معامله (فروش یا اجاره)

        Returns:
        -------
        list
            لیستی از املاک مسکونی یافت شده
        """
        if not self._validate_username(username):
            raise ValueError("نام کاربری نامعتبر است")
        
        if not self._validate_deal_type(deal_type):
            raise ValueError("نوع معامله نامعتبر است")
        
        # تخصیص فضا برای شمارنده
        count_ptr = ffi.new("int*")
        
        # فراخوانی تابع جستجو
        result_ptr = lib.residential_find_by_user(
            ffi.new("char[]", username.encode('utf-8')),
            deal_type,
            count_ptr
        )
        
        # تبدیل نتایج به لیست پایتون
        count = count_ptr[0]
        return self._convert_to_python_list(result_ptr, count)
    
    def calculate_total_value(self):
        """
        محاسبه مجموع ارزش املاک مسکونی فعال برای فروش

        Returns:
        -------
        float
            مجموع ارزش املاک
        """
        return lib.residential_calculate_total_value()
    
    def _validate_property_data(self, property_data, is_sale=True):
        """
        بررسی اعتبار داده‌های ملک مسکونی

        Parameters:
        ----------
        property_data : dict
            داده‌های ملک مسکونی
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
            'district', 'buildingAge', 'areaSize', 'bedrooms', 'floor',
            'totalFloors', 'hasElevator', 'hasParking', 'hasStorage',
            'ownerName', 'ownerContact', 'description'
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
        
        if not isinstance(property_data.get('bedrooms', 0), int) or property_data.get('bedrooms', 0) < 0:
            return False
        
        if not isinstance(property_data.get('floor', 0), int):
            return False
        
        if not isinstance(property_data.get('totalFloors', 0), int) or property_data.get('totalFloors', 0) < 1:
            return False
        
        if not isinstance(property_data.get('hasElevator', 0), int) or property_data.get('hasElevator', 0) not in [0, 1]:
            return False
        
        if not isinstance(property_data.get('hasParking', 0), int) or property_data.get('hasParking', 0) not in [0, 1]:
            return False
        
        if not isinstance(property_data.get('hasStorage', 0), int) or property_data.get('hasStorage', 0) not in [0, 1]:
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
    
    def _create_residential_property_struct(self, property_data):
        """
        ایجاد ساختار ملک مسکونی برای استفاده در C

        Parameters:
        ----------
        property_data : dict
            داده‌های ملک مسکونی

        Returns:
        -------
        ResidentialProperty
            ساختار ملک مسکونی
        """
        # ایجاد ساختار جدید
        res_property = ffi.new("ResidentialProperty*")
        
        # پر کردن فیلدهای ساختار
        if 'id' in property_data:
            ffi.memmove(res_property.id, property_data['id'].encode('utf-8'), min(len(property_data['id']), 19))
        
        district = property_data.get('district', '')
        ffi.memmove(res_property.district, district.encode('utf-8'), min(len(district), 99))
        
        res_property.isActive = property_data.get('isActive', 1)
        res_property.buildingAge = property_data.get('buildingAge', 0)
        res_property.areaSize = property_data.get('areaSize', 0.0)
        res_property.bedrooms = property_data.get('bedrooms', 0)
        res_property.floor = property_data.get('floor', 0)
        res_property.totalFloors = property_data.get('totalFloors', 1)
        res_property.hasElevator = property_data.get('hasElevator', 0)
        res_property.hasParking = property_data.get('hasParking', 0)
        res_property.hasStorage = property_data.get('hasStorage', 0)
        res_property.sellingPrice = property_data.get('sellingPrice', 0.0)
        res_property.mortgageAmount = property_data.get('mortgageAmount', 0.0)
        res_property.monthlyRentAmount = property_data.get('monthlyRentAmount', 0.0)
        
        reg_date = property_data.get('registrationDate', '')
        ffi.memmove(res_property.registrationDate, reg_date.encode('utf-8'), min(len(reg_date), 19))
        
        update_date = property_data.get('lastUpdateDate', '')
        ffi.memmove(res_property.lastUpdateDate, update_date.encode('utf-8'), min(len(update_date), 19))
        
        owner_name = property_data.get('ownerName', '')
        ffi.memmove(res_property.ownerName, owner_name.encode('utf-8'), min(len(owner_name), 99))
        
        owner_contact = property_data.get('ownerContact', '')
        ffi.memmove(res_property.ownerContact, owner_contact.encode('utf-8'), min(len(owner_contact), 99))
        
        description = property_data.get('description', '')
        ffi.memmove(res_property.description, description.encode('utf-8'), min(len(description), 499))
        
        reg_by = property_data.get('registeredBy', '')
        ffi.memmove(res_property.registeredBy, reg_by.encode('utf-8'), min(len(reg_by), 99))
        
        return res_property[0]
    
    def _convert_to_python_list(self, result_ptr, count):
        """
        تبدیل آرایه‌ای از ساختارهای C به لیست پایتونی

        Parameters:
        ----------
        result_ptr : ResidentialProperty*
            اشاره‌گر به آرایه‌ای از ساختارهای ملک مسکونی
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
                'bedrooms': prop.bedrooms,
                'floor': prop.floor,
                'totalFloors': prop.totalFloors,
                'hasElevator': prop.hasElevator,
                'hasParking': prop.hasParking,
                'hasStorage': prop.hasStorage,
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
        lib.residential_free_array(result_ptr)
        
        return result_list 