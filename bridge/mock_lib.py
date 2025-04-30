# Mock library for C functions
import os
import logging
import random
import sys
import ctypes
from datetime import datetime, timedelta

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
        ("username", ctypes.c_char_p),
        ("district", ctypes.c_char_p),
        ("address", ctypes.c_char_p),
        ("area", ctypes.c_float),
        ("price", ctypes.c_double),
        ("creation_date", ctypes.c_char_p),
        ("is_active", ctypes.c_int),
        ("contact_phone", ctypes.c_char_p),
        ("description", ctypes.c_char_p)
    ]

# ایجاد داده‌های شبیه‌سازی شده
def create_mock_data():
    districts = ["منطقه ۱", "منطقه ۲", "منطقه ۳", "منطقه ۴", "منطقه ۵"]
    mock_data = {
        'residential': {
            'sale': [create_mock_residential_property(DEAL_TYPE_SALE, district) for district in districts for _ in range(3)],
            'rent': [create_mock_residential_property(DEAL_TYPE_RENT, district) for district in districts for _ in range(2)]
        },
        'commercial': {
            'sale': [create_mock_commercial_property(DEAL_TYPE_SALE, district) for district in districts for _ in range(2)],
            'rent': [create_mock_commercial_property(DEAL_TYPE_RENT, district) for district in districts for _ in range(1)]
        },
        'land': {
            'sale': [create_mock_land_property(DEAL_TYPE_SALE, district) for district in districts for _ in range(2)],
            'rent': [create_mock_land_property(DEAL_TYPE_RENT, district) for district in districts for _ in range(1)]
        }
    }
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

# کلاس شبیه‌سازی کتابخانه C
class MockCLib:
    def __getattr__(self, name):
        def mock_function(*args, **kwargs):
            logger.info(f"Mock function call: {name} with args: {args}")
            
            # شبیه‌سازی توابع ثبت
            if name.startswith("residential_register_") or name == "residential_register":
                new_id = generate_id()
                logger.info(f"Registered new residential property with ID: {new_id}")
                return new_id
            
            elif name.startswith("commercial_register_") or name == "commercial_register":
                new_id = generate_id()
                logger.info(f"Registered new commercial property with ID: {new_id}")
                return new_id
                
            elif name.startswith("land_register_") or name == "land_register":
                new_id = generate_id()
                logger.info(f"Registered new land property with ID: {new_id}")
                return new_id
            
            elif name == "user_register":
                new_id = generate_id()
                logger.info(f"Registered new user with ID: {new_id}")
                return new_id
                
            # شبیه‌سازی توابع جستجو
            elif name.startswith("residential_find_"):
                # بررسی نوع معامله
                deal_type = args[2] if len(args) > 2 else DEAL_TYPE_SALE
                deal_type_str = "sale" if deal_type == DEAL_TYPE_SALE or deal_type == "sale" else "rent"
                
                logger.info(f"Residential search with deal type: {deal_type_str}")
                
                # برای هر نوع جستجو
                count_ptr = None
                for arg in args:
                    if hasattr(arg, '_obj') and hasattr(arg._obj, 'value'):
                        count_ptr = arg
                        break
                
                # تنظیم تعداد نتایج
                count = len(mock_data['residential'][deal_type_str])
                if count_ptr:
                    count_ptr._obj.value = count
                
                logger.info(f"{name} returning {count} properties for deal type {deal_type_str}")
                # برگرداندن اشاره‌گر به آرایه
                return MockPropertyStruct * count
                
            elif name.startswith("commercial_find_"):
                # بررسی نوع معامله
                deal_type = args[2] if len(args) > 2 else DEAL_TYPE_SALE
                deal_type_str = "sale" if deal_type == DEAL_TYPE_SALE or deal_type == "sale" else "rent"
                
                logger.info(f"Commercial search with deal type: {deal_type_str}")
                
                # برای هر نوع جستجو
                count_ptr = None
                for arg in args:
                    if hasattr(arg, '_obj') and hasattr(arg._obj, 'value'):
                        count_ptr = arg
                        break
                
                # تنظیم تعداد نتایج
                count = len(mock_data['commercial'][deal_type_str])
                if count_ptr:
                    count_ptr._obj.value = count
                
                logger.info(f"{name} returning {count} properties for deal type {deal_type_str}")
                # برگرداندن اشاره‌گر به آرایه
                return MockPropertyStruct * count
                
            elif name.startswith("land_find_"):
                # بررسی نوع معامله
                deal_type = args[2] if len(args) > 2 else DEAL_TYPE_SALE
                deal_type_str = "sale" if deal_type == DEAL_TYPE_SALE or deal_type == "sale" else "rent"
                
                logger.info(f"Land search with deal type: {deal_type_str}")
                
                # برای هر نوع جستجو
                count_ptr = None
                for arg in args:
                    if hasattr(arg, '_obj') and hasattr(arg._obj, 'value'):
                        count_ptr = arg
                        break
                
                # تنظیم تعداد نتایج
                count = len(mock_data['land'][deal_type_str])
                if count_ptr:
                    count_ptr._obj.value = count
                
                logger.info(f"{name} returning {count} properties for deal type {deal_type_str}")
                # برگرداندن اشاره‌گر به آرایه
                return MockPropertyStruct * count
                
            elif name == "property_calculate_total_value" or name == "commercial_calculate_total_value":
                # محاسبه ارزش کل
                total = random.uniform(1000000, 10000000)
                logger.info(f"Calculated total property value: {total}")
                return total
                
            elif name.endswith("_free_array"):
                # آزادسازی حافظه - در شبیه‌سازی نیازی نیست
                logger.info("Memory free requested")
                return None
                
            else:
                # توابع ناشناخته دیگر
                logger.warning(f"Unknown function: {name}")
                return 0
                
        return mock_function

# نمونه از کلاس MockCLib برای استفاده در کد
c_lib = MockCLib()

if __name__ == "__main__":
    print("Mock C library module initialized successfully.")
    print("This module is for testing and development only.")