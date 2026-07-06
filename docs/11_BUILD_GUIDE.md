# BUILD GUIDE (Phase 0.5)

این سند مراحل کامل Build، کامپایل و پیکربندی سیستم مدیریت املاک را برای محیط توسعه و تولید شرح می‌دهد.

## 1. سیاست نسخه‌گذاری (SemVer Policy)
نسخه‌گذاری نرم‌افزار دقیقاً از قالب Semantic Versioning (`MAJOR.MINOR.PATCH`) پیروی می‌کند:
- **MAJOR (نسخه اصلی):** تغییرات بزرگ که ABI را می‌شکنند (Breaking Changes در DLL یا ساختار دیتابیس).
- **MINOR (نسخه فرعی):** اضافه شدن ویژگی‌های جدید با حفظ سازگاری رو به عقب (Backwards Compatible).
- **PATCH (نسخه اصلاحی):** رفع باگ‌ها و بهبودهای جزئی بدون تغییر در API.

## 2. حداقل نیازمندی‌ها (Compiler Matrix)
سیستم باید قابلیت کامپایل موفق و بدون Warning با کامپایلرهای زیر را داشته باشد:
- **MSVC 2022** (محیط اصلی ویندوز)
- **GCC 13+** (جهت CI روی لینوکس)
- **Clang 17+**
- **استاندارد C:** `C17`
- **نسخه پایتون:** `Python 3.11+`

## 3. راهنمای بیلد مرحله به مرحله (Step-by-Step Build)

### 3.1. نصب ابزارها
نصب `CMake` (نسخه 3.20 به بالا)، کامپایلر MSVC (از طریق Visual Studio Build Tools) و `Python 3.11+`.

### 3.2. پیکربندی با CMake
پروژه از CMake برای مدیریت ساخت DLL و وابستگی‌ها (شامل کامپایل `sqlite3.c` و `cJSON`) استفاده می‌کند.
```bash
cd core
mkdir build && cd build
cmake -G "Visual Studio 17 2022" ..
```

### 3.3. ساخت لایه C (کامپایل DLL)
**Build Debug:** برای محیط توسعه (همراه با نمادهای دیباگ).
```bash
cmake --build . --config Debug
```
**Build Release:** برای خروجی نهایی (بهینه‌سازی حداکثری و حجم کمتر).
```bash
cmake --build . --config Release
```
خروجی این مرحله فایل `re_core.dll` در پوشه خروجی خواهد بود.

### 3.4. اجرای تست‌های لایه C
پس از ساخت، تست‌های C (توسط فریم‌ورک Criterion یا Unity) با ابزار `ctest` اجرا می‌شوند.
```bash
ctest -C Debug --output-on-failure
```

### 3.5. آماده‌سازی و اجرای Python
نصب وابستگی‌های پایتون در یک محیط مجازی:
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
# اجرای تست‌های پایتون
pytest bridge/tests/ app/tests/
# اجرای برنامه در حالت توسعه
python app/main.py
```

### 3.6. بسته‌بندی نهایی (Executable Build)
پس از پایان توسعه، برنامه توسط `PyInstaller` (یا Nuitka) باندل می‌شود:
```bash
pyinstaller --noconfirm --windowed --add-binary "../core/build/Release/re_core.dll;." --name "RealEstateManager" app/main.py
```

### 3.7. ساخت Installer
خروجی پوشه `dist` به همراه وابستگی‌ها با ابزار **Inno Setup** به یک فایل `.exe` نصاب (Installer) تبدیل می‌شود. اسکریپت `installer.iss` در پوشه `scripts/` تنظیمات ایجاد میان‌بر منوی استارت و مسیر نصب را مشخص می‌کند.
