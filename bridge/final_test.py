"""
تست نهایی برای بررسی داده‌های نمودار
"""

# وارد کردن کتابخانه
import sys
import time
from mock_lib import c_lib

def main():
    """تست نهایی"""
    print("=== تست نهایی ===")
    
    # ایجاد تأخیر برای جلوگیری از تداخل لاگ‌ها
    time.sleep(1)
    
    print("\n1. تست داده‌های منطقه:")
    district_data = c_lib.get_district_data_for_chart('all', 'all')
    print(f"نوع داده: {type(district_data)}")
    
    if hasattr(district_data, 'shape'):
        print(f"ابعاد: {district_data.shape}")
        print("پنج سطر اول:")
        print(district_data.head(5))
    else:
        print("داده‌ها دیتافریم نیستند")
    
    # ایجاد تأخیر مجدد
    time.sleep(1)
    
    print("\n2. تست داده‌های قیمت:")
    price_data = c_lib.get_price_data_for_chart('all', 'all')
    print(f"نوع داده: {type(price_data)}")
    
    if hasattr(price_data, 'shape'):
        print(f"ابعاد: {price_data.shape}")
        print("تمام سطرها:")
        print(price_data)
    else:
        print("داده‌ها دیتافریم نیستند")
    
    # ایجاد تأخیر مجدد
    time.sleep(1)
    
    print("\nتست با موفقیت به پایان رسید.")

if __name__ == "__main__":
    print("شروع تست نهایی...")
    main()
    print("تست نهایی به پایان رسید.") 