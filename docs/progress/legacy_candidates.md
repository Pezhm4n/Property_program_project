# Legacy Candidates Report (Phase 6.2)

بر اساس دستورالعمل توسعه و قبل از حذف فایل‌های ترم ۱ در Phase 6.5، کاندیداهای زیر جهت استخراج **دانش دامنه (Domain Knowledge)** و انتقال به هسته جدید رزرو شده‌اند:

### 1. Property Management & Domain Logic
- `property_management/property_manager.py` (دارای منطق جستجو و فیلترینگ قدیمی)
- `property_management/advanced_search.py` (پنجره‌های فیلتر و جستجوی پیشرفته ترم ۱)
- `property_management/search_engine.py` (موتور جستجوی قدیمی متکی بر SQLite پایتونی)
- `property_management/filter_models.py` (کلاس‌های DTO قدیمی فیلترینگ)
- `property_management/commercial.py` / `land.py` / `residential.py` (جهت استخراج فرمول‌های محاسبه کمیسیون و مالیات)
- `src/commercial.c` / `src/land.c` / `src/residential.c` (بررسی محدودیت‌ها و Business Ruleهای اصلی)

### 2. Validation & Algorithms
- `property_management/utils.py` (آیا حاوی اعتبارسنجی کد ملی یا فرمت تلفن است؟)
- `include/utils.h` (توابع هش یا تبدیل تاریخ)

### 3. Reports & Charts
- `property_management/charts.py` و `test_charts.py` (جهت درک نیازهای آماری برای Dashboard)
- `property_management/report_generator.py` (فرمت‌های Export مانند CSV)

> **توجه:** هیچ یک از این فایل‌ها تا Phase 6.5 حذف نخواهند شد و در زمان ممیزی، سطر به سطر بازبینی می‌گردند.
