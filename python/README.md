# واسط پایتون برای سیستم مدیریت املاک

این بسته پایتون یک لایه میانی برای استفاده راحت‌تر از کتابخانه C سیستم مدیریت املاک فراهم می‌کند.

## نیازمندی‌ها

* پایتون 3.6 یا بالاتر
* کتابخانه CFFI برای ارتباط با کد C
* کتابخانه C سیستم مدیریت املاک (property_lib)

## نصب

برای نصب این بسته، ابتدا باید کتابخانه C را بسازید:

```bash
cd Property_program_project
make
```

سپس بسته پایتون را نصب کنید:

```bash
cd python
pip install -e .
```

## استفاده

این بسته شامل چند کلاس اصلی برای مدیریت انواع مختلف املاک است:

* `UserManager`: مدیریت کاربران
* `ResidentialManager`: مدیریت املاک مسکونی
* `CommercialManager`: مدیریت املاک تجاری
* `LandManager`: مدیریت زمین

### مثال استفاده

```python
from property_management import UserManager, ResidentialManager

# مدیریت کاربران
user_manager = UserManager()

# ثبت نام کاربر جدید
user_manager.register({
    'username': 'user1',
    'password': 'password123',
    'fullName': 'نام کاربر',
    'email': 'user@example.com',
    'phone': '09123456789'
})

# ورود به سیستم
login_result = user_manager.login('user1', 'password123')

# مدیریت املاک مسکونی
residential_manager = ResidentialManager()

# ثبت ملک مسکونی برای فروش
residential_manager.register_sale('user1', {
    'district': 'منطقه ۱',
    'buildingAge': 5,
    'areaSize': 120.0,
    'bedrooms': 2,
    'floor': 3,
    'totalFloors': 5,
    'hasElevator': 1,
    'hasParking': 1,
    'hasStorage': 1,
    'sellingPrice': 1000000000.0,
    'ownerName': 'نام مالک',
    'ownerContact': '09123456789',
    'description': 'توضیحات ملک'
})

# جستجوی املاک مسکونی
properties = residential_manager.find_by_district('منطقه ۱', residential_manager.deal_type_sale)
```

## کلاس‌های اصلی

### UserManager

کلاس مدیریت کاربران که توابع زیر را ارائه می‌دهد:

* `register(user_data)`: ثبت نام کاربر جدید
* `login(username, password)`: ورود به سیستم
* `get_by_username(username)`: دریافت اطلاعات کاربر
* `update_profile(user_data)`: به‌روزرسانی پروفایل کاربر
* `change_password(username, old_password, new_password)`: تغییر رمز عبور
* `deactivate(username)`: غیرفعال کردن حساب کاربری
* `get_all()`: دریافت همه کاربران

### ResidentialManager

کلاس مدیریت املاک مسکونی که توابع زیر را ارائه می‌دهد:

* `register_sale(username, property_data)`: ثبت ملک برای فروش
* `register_rental(username, property_data)`: ثبت ملک برای اجاره
* `find_by_district(district, deal_type)`: جستجو بر اساس منطقه
* `find_by_age(min_age, max_age, deal_type)`: جستجو بر اساس سن ساختمان
* `find_by_area(min_area, max_area, deal_type)`: جستجو بر اساس مساحت
* `find_by_bedrooms(min_bedrooms, max_bedrooms, deal_type)`: جستجو بر اساس تعداد اتاق خواب
* `find_by_price(min_price, max_price, deal_type)`: جستجو بر اساس قیمت
* `find_by_floor(min_floor, max_floor, deal_type)`: جستجو بر اساس طبقه
* `find_with_elevator(deal_type)`: جستجوی املاک دارای آسانسور
* `find_with_parking(deal_type)`: جستجوی املاک دارای پارکینگ
* `find_with_storage(deal_type)`: جستجوی املاک دارای انباری
* `find_deleted_by_date(start_date, end_date, deal_type)`: جستجوی املاک حذف شده
* `find_by_user(username, deal_type)`: جستجوی املاک ثبت شده توسط کاربر
* `calculate_total_value()`: محاسبه ارزش کل املاک

### CommercialManager

کلاس مدیریت املاک تجاری با توابع مشابه `ResidentialManager` و همچنین:

* `find_by_type(commercial_type, deal_type)`: جستجو بر اساس نوع ملک تجاری

### LandManager

کلاس مدیریت زمین با توابع مشابه `ResidentialManager` و همچنین:

* `find_by_type(land_type, deal_type)`: جستجو بر اساس نوع زمین
* `find_by_distance(max_distance, deal_type)`: جستجو بر اساس فاصله از جاده اصلی
* `find_with_well(deal_type)`: جستجوی زمین‌های دارای چاه

## مثال کامل

یک نمونه کامل از استفاده این کتابخانه در فایل `example.py` ارائه شده است.

## کد منبع

برای مشاهده کد منبع به دایرکتوری `property_management` مراجعه کنید.

## توسعه

برای توسعه این بسته، شما می‌توانید کلاس‌های جدید ایجاد کنید یا عملکردهای موجود را گسترش دهید. همچنین، می‌توانید از این بسته به عنوان پایه‌ای برای ایجاد واسط‌های کاربری گرافیکی استفاده کنید. 