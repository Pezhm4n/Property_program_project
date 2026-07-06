"""
تست ساده کتابخانه moc برای نمودارها
"""

from mock_lib import c_lib
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_district_data():
    """تست داده‌های منطقه"""
    print("=== تست داده‌های منطقه ===")
    district_data = c_lib.get_district_data_for_chart('all', 'all')
    print(f"نوع داده‌ها: {type(district_data)}")
    if hasattr(district_data, 'head'):
        print("نمونه داده‌ها:")
        print(district_data.head(3))
        print(f"ستون‌ها: {district_data.columns.tolist()}")
    else:
        print("داده‌ها دیتافریم نیستند")

def test_price_data():
    """تست داده‌های قیمت"""
    print("\n=== تست داده‌های قیمت ===")
    price_data = c_lib.get_price_data_for_chart('all', 'all')
    print(f"نوع داده‌ها: {type(price_data)}")
    if hasattr(price_data, 'head'):
        print("نمونه داده‌ها:")
        print(price_data.head())
        print(f"ستون‌ها: {price_data.columns.tolist()}")
    else:
        print("داده‌ها دیتافریم نیستند")

def test_property_counts():
    """تست شمارش املاک"""
    print("\n=== تست شمارش املاک ===")
    
    prop_types = ['residential', 'commercial', 'land']
    for prop_type in prop_types:
        try:
            count_func = getattr(c_lib, f"{prop_type}_get_count")
            all_count = count_func('all')
            print(f"{prop_type}: {all_count} واحد")
        except Exception as e:
            print(f"خطا در {prop_type}: {e}")

if __name__ == "__main__":
    print("شروع تست کتابخانه mock...")
    
    try:
        test_district_data()
    except Exception as e:
        print(f"خطا در تست داده‌های منطقه: {e}")
    
    try:
        test_price_data()
    except Exception as e:
        print(f"خطا در تست داده‌های قیمت: {e}")
    
    try:
        test_property_counts()
    except Exception as e:
        print(f"خطا در تست شمارش املاک: {e}")
    
    print("\nتست‌ها به پایان رسید.") 