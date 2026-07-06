# API SPECIFICATION (Phase 0.4)

این سند توابع پابلیک DLL، فرمت پارامترها، قوانین مدیریت حافظه و ABI لایه C را برای مصرف توسط لایه Bridge (پایتون) تعریف می‌کند.

## 1. قوانین کلی (ABI Stability Rules)
1. **Calling Convention:** تمامی توابع اکسپورت شده از استاندارد `cdecl` استفاده می‌کنند (`__cdecl`).
2. **Export Prefix:** نام تمامی توابع با `re_` شروع می‌شود (Real Estate).
3. **Return Type:** تمامی توابع بیزینسی، یک مقدار `int` (اعداد صحیح بر اساس جدول Error Codes) برمی‌گردانند.
4. **Data Passing:** هرگونه داده پیچیده (Object) فقط و فقط از طریق یک رشته متنی با فرمت JSON ارسال و دریافت می‌شود.
5. **Memory Ownership:** در صورتی که تابعی رشته‌ای را برگرداند (از طریق خروجی اشاره‌گر مضاعف `char** out_json`)، پایتون موظف است پس از استفاده از رشته، تابع `re_free_string` را فراخوانی کند.

## 2. توابع سیستمی (System Methods)

```c
// راه‌اندازی سیستم، اتصال به دیتابیس و اعمال مایگریشن‌ها
int re_init(const char* db_path);

// خاموش کردن امن دیتابیس و پاکسازی حافظه
int re_shutdown();

// آزاد کردن حافظه استرینگ‌های اختصاص یافته در C توسط پایتون
void re_free_string(char* ptr);

// دریافت نسخه فعلی DLL و API
int re_get_version(char** out_version_json);
```

## 3. توابع احراز هویت (Auth & Session Methods)

```c
// ورود کاربر (بررسی نام کاربری، پسورد هش شده، لاگ‌اوت اکانت، و ثبت لاگ)
// خروجی در صورت موفقیت: JSON حاوی session_token و user_info
int re_login(const char* username, const char* password, char** out_session_json);

// خروج کاربر (باطل کردن توکن سشن)
int re_logout(const char* session_token);

// ثبت کاربر جدید (فقط توسط مدیر)
int re_register_user(const char* session_token, const char* user_json);

// قفل کردن اکانت یک کاربر (فقط توسط مدیر)
int re_disable_user(const char* session_token, int target_user_id);
```

## 4. توابع مدیریت املاک (Property Methods)

```c
// ثبت ملک جدید (اعتبارسنجی DTO، ثبت در پایگاه داده، درج در جداول Detail و ثبت در Audit Log)
int re_add_property(const char* session_token, const char* property_json, int* out_new_property_id);

// ویرایش مشخصات ملک
int re_update_property(const char* session_token, int property_id, const char* property_json);

// بایگانی کردن ملک (Soft Delete) به دلیل فروش یا اجاره رفتن
int re_archive_property(const char* session_token, int property_id);

// بازیابی ملک از حالت بایگانی (بازگشت به لیست فروش)
int re_restore_property(const char* session_token, int property_id);
```

## 5. توابع جستجو و گزارش (Search & Report Methods)

```c
// جستجوی پیشرفته املاک بر اساس فیلترهای JSON (با بازگشت آرایه JSON)
int re_search_properties(const char* session_token, const char* search_filter_json, char** out_properties_json);

// دریافت اطلاعات کامل یک ملک با شناسه
int re_get_property_by_id(const char* session_token, int property_id, char** out_property_json);

// اجرای گزارشات استاندارد از پیش تعریف شده (نام گزارش در json پاس داده می‌شود)
int re_run_report(const char* session_token, const char* report_request_json, char** out_report_result_json);
```
