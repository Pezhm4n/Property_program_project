# FOLDER STRUCTURE

ساختار دقیق پوشه‌ها و فایل‌های پروژه مطابق معماری تایید شده، به همراه تفکیک کامل لایه‌های درونی C.

```text
real-estate-suite/
├── .github/
│   └── workflows/
│       └── ci.yml                  # تنظیمات GitHub Actions
├── core/                           # هسته منطق C و مدیریت دیتابیس
│   ├── CMakeLists.txt
│   ├── include/
│   │   └── re_core.h               # هدر پابلیک (تنها فایل مورد نیاز برای Bridge)
│   ├── src/
│   │   ├── api/                    # لایه واسط DLL Export
│   │   │   └── exports.c           # پیاده‌سازی متدهای پابلیک (پیشوند re_)
│   │   ├── services/               # لایه Business Logic (مستقل از جزئیات دیتابیس)
│   │   │   ├── auth_service.c
│   │   │   ├── property_service.c
│   │   │   └── report_service.c
│   │   ├── repository/             # لایه Data Access (وابسته به SQLite)
│   │   │   ├── db_connection.c     # مدیریت کانکشن و WAL
│   │   │   ├── user_repo.c         # کوئری‌های جدول کاربران
│   │   │   ├── property_repo.c     # کوئری‌های ثبت ملک و جزئیات
│   │   │   ├── audit_repo.c        # کوئری‌های جدول آدیت‌لاگ
│   │   │   └── migrations.c        # اجرای اتوماتیک فایل‌های SQL نسخه
│   │   ├── models/                 # ساختارهای داده داخلی C (Domain Models)
│   │   │   ├── user_model.h
│   │   │   └── property_model.h
│   │   ├── dto/                    # مپرهای JSON به Model (DTO Validation)
│   │   │   ├── json_parser.c
│   │   │   └── dto_validators.c
│   │   └── errors/                 # مدیریت یکپارچه خطاها
│   │       └── error_handler.c
│   ├── third_party/
│   │   ├── sqlite3/
│   │   ├── cJSON/
│   │   └── argon2/
│   ├── migrations/
│   │   ├── 0001_initial.sql
│   │   └── 0002_report_views.sql
│   └── tests/
│       ├── test_services/          # تست‌های منطق تجاری (با دیتابیس ماک شده در آینده)
│       └── test_repositories/      # تست‌های ادغام پایگاه داده
├── bridge/                         # لایه پایتون برای اتصال به DLL
│   ├── setup.py
│   ├── re_bridge/
│   │   ├── __init__.py
│   │   ├── loader.py
│   │   ├── exceptions.py
│   │   ├── services/               # Python Service Wrappers
│   │   └── models/                 # Python Data Classes (Pydantic/Dataclasses)
│   └── tests/
├── app/                            # رابط کاربری PySide6
│   ├── main.py
│   ├── resources/
│   ├── ui/
│   └── tests/
├── scripts/
│   ├── build_core.bat
│   └── build_exe.bat
├── docs/                           # مستندات معماری و پایگاه داده
│   ├── 01_PROJECT_VISION.md
│   ├── 02_ADR.md
│   ├── 03_ROADMAP.md
│   ├── 04_ARCHITECTURE.md
│   ├── 05_FOLDER_STRUCTURE.md
│   ├── 06_DATABASE_DESIGN.md       # طراحی کامل جداول دیتابیس
│   └── original_project/
└── README.md
```
