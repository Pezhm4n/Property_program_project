# JSON SCHEMA (Phase 0.4)

این سند قراردادهای ساختاری رشته‌های JSON (DTOs) که بین پایتون و C مبادله می‌شوند را تعریف می‌کند. 
در صورت عدم رعایت این ساختارها، لایه C خطای `RE_ERR_VALIDATION` را برمی‌گرداند.

## 1. فرمت کلی پاسخ‌ها (Base Output JSON)
تمام خروجی‌های موفقی که نیاز به برگرداندن داده دارند، از فرمت زیر پیروی می‌کنند:
```json
{
  "api_version": "1.0",
  "status": "success",
  "data": { ... } // Payload اصلی اینجا قرار می‌گیرد
}
```

## 2. مشخصات کاربر (User DTO)
**هنگام ثبت نام (`re_register_user`):**
```json
{
  "username": "ali_rez",
  "password": "SecurePass123!", // به صورت خام، در C هش می‌شود
  "first_name": "علی",
  "last_name": "رضایی",
  "national_id": "0123456789",
  "phone": "09120000000",
  "role": "agent" // فقط admin یا agent
}
```

**هنگام دریافت اطلاعات کاربر:** (بدون فیلد password)
```json
{
  "id": 1,
  "username": "ali_rez",
  "first_name": "علی",
  "last_name": "رضایی",
  "role": "agent"
}
```

## 3. نشست فعال (Session DTO)
خروجی پس از موفقیت `re_login`:
```json
{
  "session_token": "abc123xyz-uuid-token",
  "expires_at": "2026-07-06T20:00:00Z",
  "user": {
     "id": 1,
     "username": "admin",
     "role": "admin"
  }
}
```

## 4. فرم ثبت و ویرایش ملک (Property DTO)
این DTO شامل فیلدهای مشترک و فیلدهای اختصاصی هر دسته‌بندی است.

**مسکونی (Residential):**
```json
{
  "category": "residential",
  "listing_type": "sale",
  "municipal_district": 2,
  "address": "سعادت آباد، بلوار ...",
  "owner_phone": "09121112233",
  "sale_price": 50000000000,
  "rent_deposit": null,
  "rent_monthly": null,
  "details": {
    "building_age": 5,
    "floor_area_sqm": 120.5,
    "floor_number": 4,
    "land_area_sqm": null,
    "bedroom_count": 3
  }
}
```

**زمین (Land):**
```json
{
  "category": "land",
  "listing_type": "sale",
  "municipal_district": 22,
  "address": "چیتگر، بلوار ...",
  "owner_phone": "09123334455",
  "sale_price": 10000000000,
  "details": {
    "land_type": "urban",
    "land_area_sqm": 500.0,
    "distance_to_main_road": 50.0,
    "has_well": 0
  }
}
```

## 5. فیلترهای جستجو (Search Filter DTO)
ورودی تابع `re_search_properties`. فیلدها Optional هستند.
```json
{
  "category": "residential", // optional
  "listing_type": "sale", // optional
  "district": 2, // optional
  "min_price": 1000000000, // optional
  "max_price": 50000000000, // optional
  "min_area": 80, // optional
  "sort_by": "created_at", // "created_at", "price", "area"
  "sort_order": "DESC", // "ASC", "DESC"
  "page": 1,
  "page_size": 50
}
```
