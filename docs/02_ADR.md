# Architecture Decision Records (ADR)

این سند شامل تصمیمات کلیدی معماری پروژه و دلایل فنی پشت آن‌هاست.

## ADR-001: Why SQLite
- **Decision:** استفاده از SQLite.
- **Trade-offs:** آفلاین و سریع با تراکنش‌های ACID، اما مقیاس‌پذیری محدود به شبکه محلی.

## ADR-002: Why PySide6
- **Decision:** استفاده از PySide6 برای UI.
- **Trade-offs:** پشتیبانی کامل از RTL و ابزارهای حرفه‌ای، در مقابل افزایش حجم برنامه.

## ADR-003: Why C instead of C++
- **Decision:** حفظ هسته در C.
- **Trade-offs:** حفظ هویت پروژه اولیه و ارائه ABI بسیار پایدار به قیمت مدیریت حافظه دستی.

## ADR-004: Why JSON instead of Struct (For FFI)
- **Decision:** تبادل داده بین C و Python با رشته‌های JSON (DTO).
- **Trade-offs:** جلوگیری قطعی از شکستن ABI هنگام تغییرات دیتابیس، در مقابل سربار جزئی پارس کردن جیسون.

## ADR-005: Why ctypes
- **Decision:** استفاده از `ctypes` پایتون.
- **Trade-offs:** بی‌نیاز از کامپایلر سمت پایتون و اتصال بسیار ساده به توابع cdecl.

## ADR-006: Why DLL (Shared Library)
- **Decision:** تبدیل هسته C به `re_core.dll`.
- **Trade-offs:** جداسازی کامل دغدغه‌ها و امکان آپدیت مستقل UI یا هسته.

## ADR-007: Why SQLite inside C (and not Python)
- **Decision:** پایگاه داده منحصراً توسط هسته C لمس می‌شود.
- **Trade-offs:** UI نمی‌تواند اعتبارسنجی‌ها و قوانین تجاری را دور بزند.

## ADR-008: Why Layered Architecture
- **Decision:** پیاده‌سازی Clean / Layered Architecture.
- **Trade-offs:** زمان توسعه اولیه بالاتر، اما هزینه نگهداری و افزودن فیچر در درازمدت نزدیک به صفر می‌شود.

## ADR-009: Why CMake
- **Decision:** استفاده از CMake به عنوان سیستم Build.
- **Trade-offs:** استانداردسازی پروژه برای اتصال به ابزارهای CI/CD.

## ADR-010: Why Portable Distribution
- **Decision:** استفاده از Portable Distribution به جای سینگل اگزِ.
- **Trade-offs:** امکان استفاده از MSI Installer، پلاگین‌ها، و آپدیت خودکار در آینده.

## ADR-011: Why SQLite WAL Mode
- **Decision:** فعال‌سازی Write-Ahead Logging.
- **Trade-offs:** امکان خواندن و نوشتن همزمان با سرعت بالا را فراهم می‌کند و در مقابل Crash مقاوم‌تر است.

## ADR-012: Why Repository Pattern
- **Decision:** استفاده از الگوی Repository در کد C برای تعامل با دیتابیس.
- **Trade-offs:** تمرکز کدهای SQL در یک لایه مجزا که تست‌پذیری لایه سرویس را به شدت بالا می‌برد.

## ADR-013: Why Error Codes instead of Exceptions
- **Decision:** بازگرداندن کدهای خطای منفی `int` از DLL و مپ کردن آن‌ها به Exception در پایتون.
- **Trade-offs:** ایجاد مرز ارتباطی کاملاً امن و واضح در سطح ABI بدون وابستگی به مکانیزم Exception هندلینگ C++.

## ADR-014: Why UTF-8 Everywhere
- **Decision:** اجبار UTF-8 در دیتابیس، استرینگ‌های C و UI.
- **Trade-offs:** جلوگیری از به هم ریختگی متون فارسی.

## ADR-015: Why Soft Delete
- **Decision:** عدم حذف فیزیکی هیچ‌یک از رکوردها (`is_deleted` یا `archived_at`).
- **Trade-offs:** حفظ یکپارچگی گزارش‌های مالی و دیتای حسابرسی، با هزینه افزایش اندک حجم دیتابیس.

## ADR-016: Why Transaction Per Use Case
- **Decision:** باز و بسته کردن تراکنش (BEGIN...COMMIT) روی هر عملیات معنادار تجاری.
- **Trade-offs:** Data Integrity صد درصدی در صورت کرش وسط عملیات ثبت چندجدولی.

## ADR-017: Why Database Versioning
- **Decision:** استفاده از مایگریشن‌ها و جدول `schema_migrations`.
- **Trade-offs:** آپگرید امن نرم‌افزار روی سیستم کلاینت‌هایی که از نسخه‌های قدیمی استفاده می‌کرده‌اند.

## ADR-018: Why Prepared Statements
- **Decision:** استفاده صددرصدی از `sqlite3_bind_*`.
- **Trade-offs:** مسدود کردن کامل حملات SQL Injection.

## ADR-019: Why DTO (JSON)
- **Decision:** جدا کردن مدل‌های دیتابیس از مدل‌های انتقال داده از طریق DTO.
- **Trade-offs:** امنیت بیشتر با مخفی کردن فیلدهای حساس دیتابیس در زمان ارسال داده به UI.

## ADR-021: Why DTO Validation
- **Decision:** انجام Validation دقیق روی DTOهای JSON ورودی در لایه C، پیش از رسیدن به Business Logic.
- **Trade-offs:** جلوگیری از ورود دیتای مخرب یا ناقص به هسته سیستم که ممکن است به واسطه یک UI ثالث (یا کلاینت‌های آینده) ارسال شود.

## ADR-022: Why Dependency Inversion
- **Decision:** وارونگی وابستگی در لایه C (عدم وابستگی مستقیم Service به 구현 Repository).
- **Trade-offs:** تست‌پذیری ماژولار را به واسطه امکان Mock کردن لایه داده افزایش می‌دهد.
