# Mock library for C functions
import os
import logging
import random
import sys
import ctypes
from datetime import datetime, timedelta
import string
from enum import Enum
from typing import Dict, List, Any, Optional
import pandas as pd

# Setup logging
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'mock_lib.log')

logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger('mock_lib')
logger.info("Using mock library instead of C library")

# ثابت‌های نوع معامله
DEAL_TYPE_SALE = 1
DEAL_TYPE_RENT = 2

# ساختار داده برای شبیه‌سازی ساختارهای املاک
class MockPropertyStruct(ctypes.Structure):
    _fields_ = [
        ("id", ctypes.c_int),
        ("username", ctypes.c_char * 50),
        ("district", ctypes.c_int),
        ("address", ctypes.c_char * 200),
        ("area", ctypes.c_float),
        ("price", ctypes.c_double),
        ("creation_date", ctypes.c_char * 20),
        ("is_active", ctypes.c_int),
        ("contact_phone", ctypes.c_char * 20),
        ("description", ctypes.c_char * 500)
    ]

# کلاس مجازی برای ساختار کاربر
class MockUserStruct(ctypes.Structure):
    _fields_ = [
        ("id", ctypes.c_int),
        ("username", ctypes.c_char * 50),
        ("password_hash", ctypes.c_char * 100),
        ("email", ctypes.c_char * 100),
        ("role", ctypes.c_int),
        ("is_active", ctypes.c_int),
        ("registration_date", ctypes.c_char * 20)
    ]

# کلاس برای Mock Array با تعداد متغیر
def create_mock_property_struct_array(count):
    class MockPropertyStructArray(ctypes.Structure):
        _fields_ = [("properties", MockPropertyStruct * count)]
        
        def __init__(self):
            super().__init__()
            self.properties = self._create_mock_properties(count)
        
        def _create_mock_properties(self, count):
            mock_props = []
            districts = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
            
            for i in range(count):
                prop = MockPropertyStruct()
                prop.id = generate_id()
                prop.username = f"user{i}".encode('utf-8')
                prop.district = random.choice(districts)
                prop.address = f"خیابان {random.randint(1, 100)}, پلاک {random.randint(1, 999)}".encode('utf-8')
                prop.area = random.uniform(50, 500)
                prop.price = random.uniform(1000000, 10000000)
                
                # تاریخ تصادفی در ۳۶۵ روز گذشته
                days_ago = random.randint(0, 365)
                date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
                prop.creation_date = date.encode('utf-8')
                
                prop.is_active = 1
                prop.contact_phone = f"09{random.randint(10000000, 99999999)}".encode('utf-8')
                prop.description = f"توضیحات ملک شماره {i+1}".encode('utf-8')
                
                mock_props.append(prop)
            
            return (MockPropertyStruct * count)(*mock_props)
        
        def __getitem__(self, index):
            if 0 <= index < count:
                return self.properties[index]
            raise IndexError(f"Index {index} out of range")
        
        def __len__(self):
            return count
    
    return MockPropertyStructArray

# کلاس شی‌گرا برای نگهداری اطلاعات املاک
class PropertyObject:
    def __init__(self, property_dict):
        self._data = property_dict  # ذخیره داده اصلی
        for key, value in property_dict.items():
            setattr(self, key, value)
    
    def __getattr__(self, name):
        """
        متد جادویی برای دسترسی به صفاتی که موجود نیستند.
        برای سازگاری با کد موجود، برخی از صفات را به صورت تنبل (lazy) محاسبه می‌کند.
        """
        # سازگاری با رشته‌های باینری
        if name.endswith('_decoded'):
            original_name = name[:-8]  # حذف _decoded از انتها
            original_value = getattr(self, original_name, None)
            if isinstance(original_value, str):
                return original_value  # رشته عادی نیازی به رمزگشایی ندارد
            return None
        
        # صفات نوع ملک
        if name == 'property_type':
            return 'commercial_type' if hasattr(self, 'commercial_type') else ('land_type' if hasattr(self, 'land_type') else 'residential')
        
        # صفات قیمت
        if name == 'price' and not hasattr(self, 'price'):
            if hasattr(self, 'selling_price'):
                return self.selling_price
            if hasattr(self, 'monthly_rent_amount'):
                return self.monthly_rent_amount
        
        # صفات دیگر
        if name == 'age' and hasattr(self, 'buildingAge'):
            return self.buildingAge
            
        if name == 'rooms' and hasattr(self, 'bedrooms'):
            return self.bedrooms
            
        if name == 'deposit' and hasattr(self, 'mortgageAmount'):
            return self.mortgageAmount
            
        if name == 'rent' and hasattr(self, 'monthlyRentAmount'):
            return self.monthlyRentAmount
        
        # اگر صفت موجود نباشد، مقدار پیش‌فرض مناسب برگردان
        if name in ['is_active', 'has_elevator', 'has_parking', 'has_storage']:
            return True  # مقدار پیش‌فرض برای صفات بولی
            
        return None  # برای سایر صفات
        
    def decode(self, encoding='utf-8'):
        """
        متدی برای سازگاری با رشته‌های باینری
        """
        return self
        
    def __len__(self):
        """
        طول این شی، همیشه 1 خواهد بود چون یک ملک را نمایش می‌دهد
        """
        return 1
        
    def __iter__(self):
        """
        امکان استفاده از این شی در حلقه‌ها
        """
        yield self  # این شی را به عنوان یک آیتم برمی‌گرداند
        
    def __getitem__(self, key):
        """
        امکان دسترسی به صفات با روش دیکشنری
        """
        if key in self._data:
            return self._data[key]
        if hasattr(self, key):
            return getattr(self, key)
        return None

# ایجاد داده‌های شبیه‌سازی شده
def create_mock_data(): 
    """تولید داده‌های مصنوعی برای املاک"""
    # ساختاری برای نگهداری املاک مختلف
    mock_data = {
        'residential': {
            'sale': [],
            'rent': []
        },
        'commercial': {
            'sale': [],
            'rent': []
        },
        'land': {
            'sale': [],
            'rent': []
        }
    }
    
    # تولید داده‌های مصنوعی برای انواع املاک
    # اطلاعات مسکونی
    for i in range(10):
        # ملک‌های فروشی
        district = random.randint(1, 8)
        mock_data['residential']['sale'].append(
            create_mock_residential_property('sale', district)
        )
        
        # ملک‌های اجاره‌ای
        district = random.randint(1, 8)
        mock_data['residential']['rent'].append(
            create_mock_residential_property('rent', district)
        )
    
    # اطلاعات تجاری
    for i in range(5):
        # ملک‌های فروشی
        district = random.randint(1, 8)
        mock_data['commercial']['sale'].append(
            create_mock_commercial_property('sale', district)
        )
        
        # ملک‌های اجاره‌ای
        district = random.randint(1, 8)
        mock_data['commercial']['rent'].append(
            create_mock_commercial_property('rent', district)
        )
    
    # اطلاعات زمین
    for i in range(3):
        # زمین‌های فروشی
        district = random.randint(1, 8)
        mock_data['land']['sale'].append(
            create_mock_land_property('sale', district)
        )
        
        # زمین‌های اجاره‌ای (نادر)
        if random.random() > 0.7:  # 30% احتمال
            district = random.randint(1, 8)
            mock_data['land']['rent'].append(
                create_mock_land_property('rent', district)
            )
    
    return mock_data

# ایجاد یک ملک مسکونی شبیه‌سازی شده
def create_mock_residential_property(deal_type, district):
    creation_date = (datetime.now() - timedelta(days=random.randint(1, 365))).strftime("%Y-%m-%d")
    area = random.uniform(50, 200)
    
    # قیمت فروش یا اجاره
    price = 0
    if deal_type == DEAL_TYPE_SALE:
        price = area * random.uniform(20, 50) * 1000000
    else:  # اجاره
        price = area * random.uniform(0.5, 2) * 1000000
    
    property_data = {
        "id": generate_id(),
        "username": "admin",
        "district": district,
        "address": f"خیابان نمونه، پلاک {random.randint(1, 100)}",
        "area": area,
        "price": price,
        "bedrooms": random.randint(1, 4),
        "floor": random.randint(0, 10),
        "has_elevator": random.choice([0, 1]),
        "has_parking": random.choice([0, 1]),
        "creation_date": creation_date,
        "is_active": 1,
        "contact_phone": f"0912{random.randint(1000000, 9999999)}",
        "description": "توضیحات نمونه برای ملک مسکونی"
    }
    return property_data

# ایجاد یک ملک تجاری شبیه‌سازی شده
def create_mock_commercial_property(deal_type, district):
    creation_date = (datetime.now() - timedelta(days=random.randint(1, 365))).strftime("%Y-%m-%d")
    area = random.uniform(30, 300)
    
    # قیمت فروش یا اجاره
    price = 0
    if deal_type == DEAL_TYPE_SALE:
        price = area * random.uniform(30, 80) * 1000000
    else:  # اجاره
        price = area * random.uniform(1, 3) * 1000000
    
    property_data = {
        "id": generate_id(),
        "username": "admin",
        "district": district,
        "address": f"خیابان تجاری، پلاک {random.randint(1, 100)}",
        "area": area,
        "price": price,
        "commercial_type": random.choice(["مغازه", "دفتر", "انبار"]),
        "floor": random.randint(0, 5),
        "has_showcase": random.choice([0, 1]),
        "creation_date": creation_date,
        "is_active": 1,
        "contact_phone": f"0912{random.randint(1000000, 9999999)}",
        "description": "توضیحات نمونه برای ملک تجاری"
    }
    return property_data

# ایجاد یک زمین شبیه‌سازی شده
def create_mock_land_property(deal_type, district):
    creation_date = (datetime.now() - timedelta(days=random.randint(1, 365))).strftime("%Y-%m-%d")
    area = random.uniform(100, 1000)
    
    # قیمت فروش یا اجاره
    price = 0
    if deal_type == DEAL_TYPE_SALE:
        price = area * random.uniform(10, 30) * 1000000
    else:  # اجاره
        price = area * random.uniform(0.2, 1) * 1000000
    
    property_data = {
        "id": generate_id(),
        "username": "admin",
        "district": district,
        "address": f"بلوار زمین، قطعه {random.randint(1, 100)}",
        "area": area,
        "price": price,
        "land_type": random.choice(["مسکونی", "تجاری", "کشاورزی"]),
        "has_well": random.choice([0, 1]),
        "creation_date": creation_date,
        "is_active": 1,
        "contact_phone": f"0912{random.randint(1000000, 9999999)}",
        "description": "توضیحات نمونه برای زمین"
    }
    return property_data

# تولید شناسه جدید
def generate_id():
    return random.randint(1000, 9999)

# ایجاد داده‌های مورد نیاز
mock_data = create_mock_data()

# تبدیل دیکشنری‌های موجود به اشیاء
property_objects = {
    'residential': {
        'sale': [PropertyObject(prop) for prop in mock_data['residential']['sale']],
        'rent': [PropertyObject(prop) for prop in mock_data['residential']['rent']]
    },
    'commercial': {
        'sale': [PropertyObject(prop) for prop in mock_data['commercial']['sale']],
        'rent': [PropertyObject(prop) for prop in mock_data['commercial']['rent']]
    },
    'land': {
        'sale': [PropertyObject(prop) for prop in mock_data['land']['sale']],
        'rent': [PropertyObject(prop) for prop in mock_data['land']['rent']]
    }
}

# کتابخانه مجازی C
class MockCLib:
    """کلاس تقلیدی C-Library برای آزمایش و توسعه"""
    
    def __init__(self):
        global mock_data
        # دریافت داده‌های آماده
        if not mock_data:
            mock_data = create_mock_data()
        logger.info("کتابخانه مجازی (mock) برای آزمایش و توسعه آماده‌سازی شد")
    
    def generate_id(self):
        """تولید یک شناسه تصادفی"""
        return random.randint(1000, 9999)
        
    def get_properties(self, property_type, deal_type):
        """دریافت تمام املاک بر اساس نوع ملک و نوع معامله"""
        # تبدیل نوع معامله به رشته
        deal_type_str = "sale" if deal_type == 1 or deal_type == "sale" else "rent"
        
        # برگرداندن داده‌های آماده از mock
        count = len(mock_data.get(property_type, {}).get(deal_type_str, []))
        logger.info(f"درخواست دریافت همه املاک {property_type} برای {deal_type_str}: {count} ملک یافت شد")
        
        # ایجاد یک نمونه از کلاس آرایه ساختار و برگرداندن آن
        array_class = create_mock_property_struct_array(count)
        array_instance = array_class()  # ایجاد نمونه از کلاس
        return array_instance  # برگرداندن نمونه به جای کلاس
    
    def get_property_by_id(self, property_id, property_type=None):
        """دریافت ملک با شناسه مشخص"""
        logging.info(f"درخواست ملک با شناسه {property_id} و نوع {property_type}")
        
        # ایجاد یک ساختار تقلیدی برای ملک
        property_struct_class = create_mock_property_struct()
        property_instance = property_struct_class()
        return property_instance
    
    def user_register(self, username, password, email, phone, role):
        """ثبت کاربر جدید"""
        user_id = self.generate_id()
        logger.info(f"ثبت کاربر جدید با شناسه: {user_id}")
        return user_id
    
    def land_calculate_total_value(self):
        """محاسبه مجموع ارزش زمین‌ها"""
        total_value = random.randint(1000000000, 5000000000)
        logger.info(f"محاسبه مجموع ارزش زمین‌ها: {total_value}")
        return total_value
    
    def residential_calculate_total_value(self):
        """محاسبه مجموع ارزش املاک مسکونی"""
        total_value = random.randint(5000000000, 15000000000)
        logger.info(f"محاسبه مجموع ارزش املاک مسکونی: {total_value}")
        return total_value
        
    def commercial_calculate_total_value(self):
        """محاسبه مجموع ارزش املاک تجاری"""
        total_value = random.randint(3000000000, 10000000000)
        logger.info(f"محاسبه مجموع ارزش املاک تجاری: {total_value}")
        return total_value
    
    def __getattr__(self, name):
        """برای فراخوانی‌های پویا به توابع تعریف نشده"""
        def mock_method(*args, **kwargs):
            logger.info(f"فراخوانی تابع mock: {name} با آرگومان‌های {args} و {kwargs}")
            
            # تولید یک شناسه تصادفی برای ثبت ملک
            if name.startswith('residential_register') or name.startswith('commercial_register') or name.startswith('land_register'):
                property_id = self.generate_id()
                logger.info(f"شناسه ملک جدید تولید شد: {property_id}")
                return property_id
                
            # ثبت کاربر جدید
            elif name == "user_register":
                user_id = self.generate_id()
                logger.info(f"ثبت کاربر جدید با شناسه: {user_id}")
                return user_id
                
            # جستجوی املاک
            elif name.startswith('residential_find_') or name.startswith('commercial_find_') or name.startswith('land_find_'):
                count_arg = None
                for arg in args:
                    if isinstance(arg, ctypes._Pointer):
                        count_arg = arg
                        break
                
                # تعیین نوع ملک
                property_type = None
                if name.startswith('residential_'):
                    property_type = 'residential'
                elif name.startswith('commercial_'):
                    property_type = 'commercial'
                elif name.startswith('land_'):
                    property_type = 'land'
                
                # تعیین نوع معامله
                deal_type_arg = None
                deal_type_index = -1
                
                if name.endswith('_by_district'):
                    deal_type_index = 1
                elif name.endswith('_by_age') or name.endswith('_by_area') or name.endswith('_by_price'):
                    deal_type_index = 2
                elif name.endswith('_by_bedrooms') or name.endswith('_by_floor'):
                    deal_type_index = 2
                elif name.endswith('_with_elevator') or name.endswith('_with_parking') or name.endswith('_with_storage'):
                    deal_type_index = 0
                elif name.endswith('_by_user'):
                    deal_type_index = 1
                
                if 0 <= deal_type_index < len(args):
                    deal_type_arg = args[deal_type_index]
                
                # برگرداندن نتایج mock
                deal_type_str = "sale" if deal_type_arg == 1 or deal_type_arg == "sale" else "rent"
                result_count = random.randint(0, 5)
                
                if count_arg:
                    count_arg._obj.value = result_count
                
                # ایجاد نمونه از کلاس آرایه و برگرداندن آن
                array_class = create_mock_property_struct_array(result_count)
                array_instance = array_class()  # ایجاد نمونه از کلاس
                return array_instance  # برگرداندن نمونه به جای کلاس
                
            # محاسبات ارزش کل
            elif name == 'land_calculate_total_value':
                value = random.randint(1000000000, 9000000000)
                logger.info(f"محاسبه ارزش کل زمین‌ها: {value:,} ریال")
                return value
            elif name == 'residential_calculate_total_value':
                value = random.randint(5000000000, 15000000000)
                logger.info(f"محاسبه ارزش کل املاک مسکونی: {value:,} ریال")
                return value
            elif name == 'commercial_calculate_total_value':
                value = random.randint(3000000000, 10000000000)
                logger.info(f"محاسبه ارزش کل املاک تجاری: {value:,} ریال")
                return value
            
            # داده‌های نمودار قیمت
            elif name == 'get_price_data_for_chart':
                # به جای برگرداندن تابع، مستقیماً دیتافریم را برمی‌گردانیم
                logger.info(f"دریافت داده‌های قیمت برای نمودار: نوع ملک {args[0] if args else 'all'}، نوع معامله {args[1] if len(args) > 1 else 'all'}")
                property_type = args[0] if args else 'all'
                deal_type = args[1] if len(args) > 1 else 'all'
                
                # تولید داده‌های مصنوعی برای نمودار قیمت
                import pandas as pd
                price_ranges = [
                    "زیر ۵۰۰ میلیون", 
                    "۵۰۰ تا ۱ میلیارد", 
                    "۱ تا ۲ میلیارد", 
                    "۲ تا ۵ میلیارد", 
                    "بالای ۵ میلیارد"
                ]
                
                counts = [random.randint(5, 30) for _ in range(len(price_ranges))]
                total = sum(counts)
                percentages = [round((count / total) * 100, 1) for count in counts]
                
                # ساخت دیتافریم
                df = pd.DataFrame({
                    'PriceRange': price_ranges,
                    'Count': counts,
                    'Percentage': percentages
                })
                
                return df
            
            # داده‌های نمودار منطقه
            elif name == 'get_district_data_for_chart':
                # به جای برگرداندن تابع، مستقیماً دیتافریم را برمی‌گردانیم
                logger.info(f"دریافت داده‌های منطقه برای نمودار: نوع ملک {args[0] if args else 'all'}، نوع معامله {args[1] if len(args) > 1 else 'all'}")
                property_type = args[0] if args else 'all'
                deal_type = args[1] if len(args) > 1 else 'all'
                
                # تولید داده‌های مصنوعی برای نمودار منطقه
                import pandas as pd
                districts = [
                    "منطقه ۱", "منطقه ۲", "منطقه ۳", "منطقه ۴", "منطقه ۵", 
                    "منطقه ۶", "منطقه ۷", "منطقه ۸"
                ]
                
                # ستون‌های مورد نیاز برای نمودار
                property_types = ["مسکونی", "تجاری", "زمین"]
                data = {}
                
                # ستون منطقه
                data["District"] = districts.copy()
                
                # تولید داده برای هر نوع ملک
                for p_type in property_types:
                    data[p_type] = [random.randint(0, 15) for _ in range(len(districts))]
                
                # ستون مجموع
                data["Total"] = [sum(data[p_type][i] for p_type in property_types) for i in range(len(districts))]
                
                # اضافه کردن جمع کل به انتهای دیتافریم
                data["District"].append("Total")
                for col in property_types + ["Total"]:
                    data[col].append(sum(data[col][:-1] if col == "Total" else data[col]))
                
                # ساخت دیتافریم
                df = pd.DataFrame(data)
                
                return df
            
            # توابع شمارش املاک
            elif name.endswith('_get_count'):
                property_type = name.split('_')[0]  # استخراج نوع ملک از نام تابع
                deal_type = args[0] if args else 'all'
                
                if deal_type is None or deal_type == 'all':
                    count = random.randint(10, 50)
                else:
                    count = random.randint(5, 30)
                    
                logger.info(f"شمارش املاک نوع {property_type} برای معامله {deal_type}: {count}")
                return count
            
            # حالت پیش‌فرض - برگرداندن 0 به عنوان نشانه موفقیت
            return 0
        
        return mock_method

# نمونه از کلاس MockCLib برای استفاده در کد
c_lib = MockCLib()

if __name__ == "__main__":
    print("Mock C library module initialized successfully.")
    print("This module is for testing and development only.")