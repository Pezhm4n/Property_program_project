# راهنمای حل مشکل کتابخانه DLL

اگر با خطای زیر مواجه شده‌اید:
```
خطا در بارگیری کتابخانه C: cannot load library 'C:\c-programs\#FINAL\Property_program_project\lib\property_lib.dll': error 0xc1
خطا در اجرای برنامه: [WinError 193] %1 is not a valid Win32 application
```

این خطا نشان می‌دهد که کتابخانه DLL با معماری پایتون شما سازگار نیست یا به درستی کامپایل نشده است. برای حل این مشکل، مراحل زیر را دنبال کنید:

## مرحله ۱: بررسی نسخه پایتون

ابتدا بررسی کنید که آیا از پایتون ۳۲ بیتی یا ۶۴ بیتی استفاده می‌کنید:

۱. ترمینال یا خط فرمان را باز کنید.
۲. دستور زیر را اجرا کنید:
```
python -c "import platform; print(platform.architecture()[0])"
```
۳. اگر نتیجه '64bit' بود، پایتون ۶۴ بیتی دارید، در غیر این صورت ۳۲ بیتی دارید.

## مرحله ۲: کامپایل مجدد کتابخانه

### نصب کامپایلر GCC:

۱. [MSYS2](https://www.msys2.org) را دانلود و نصب کنید.
۲. پس از نصب، MSYS2 را اجرا کنید.
۳. دستور زیر را برای نصب GCC وارد کنید:
```
# برای سیستم 64 بیتی
pacman -S mingw-w64-x86_64-gcc

# برای سیستم 32 بیتی
pacman -S mingw-w64-i686-gcc
```
۴. مسیر bin کامپایلر را به PATH سیستم اضافه کنید:
   - برای 64 بیتی: C:\msys64\mingw64\bin
   - برای 32 بیتی: C:\msys64\mingw32\bin

### کامپایل کتابخانه:

۱. به پوشه پروژه بروید.
۲. با توجه به معماری پایتون، یکی از فایل‌های زیر را اجرا کنید:
   - برای ۶۴ بیتی: فایل `compile_lib_win64.bat` را اجرا کنید.
   - برای ۳۲ بیتی: فایل `compile_lib_win32.bat` را اجرا کنید.

اگر این فایل‌ها وجود ندارند، آن‌ها را با استفاده از محتوای زیر ایجاد کنید:

### فایل compile_lib_win64.bat (برای پایتون ۶۴ بیتی):
```batch
@echo off
echo در حال ساخت کتابخانه property_lib برای ویندوز 64 بیتی...

REM ایجاد دایرکتوری خروجی اگر وجود ندارد
if not exist "lib" mkdir lib

echo در حال کامپایل فایل‌های منبع C...
gcc -c -m64 src/property_lib.c -I include -o property_lib.o
gcc -c -m64 src/commercial.c -I include -o commercial.o
gcc -c -m64 src/residential.c -I include -o residential.o
gcc -c -m64 src/land.c -I include -o land.o
gcc -c -m64 src/report.c -I include -o report.o
gcc -c -m64 src/data_manager.c -I include -o data_manager.o

echo در حال ساخت DLL...
gcc -m64 -shared -o lib/property_lib.dll property_lib.o commercial.o residential.o land.o report.o data_manager.o -Wl,--out-implib,lib/libproperty.a

echo در حال پاکسازی فایل‌های موقتی...
del *.o

echo.
echo ساخت کتابخانه با موفقیت انجام شد.
echo کتابخانه 64 بیتی در مسیر lib/property_lib.dll قرار دارد.
pause
```

### فایل compile_lib_win32.bat (برای پایتون ۳۲ بیتی):
```batch
@echo off
echo در حال ساخت کتابخانه property_lib برای ویندوز 32 بیتی...

REM ایجاد دایرکتوری خروجی اگر وجود ندارد
if not exist "lib" mkdir lib

echo در حال کامپایل فایل‌های منبع C...
gcc -c -m32 src/property_lib.c -I include -o property_lib.o
gcc -c -m32 src/commercial.c -I include -o commercial.o
gcc -c -m32 src/residential.c -I include -o residential.o
gcc -c -m32 src/land.c -I include -o land.o
gcc -c -m32 src/report.c -I include -o report.o
gcc -c -m32 src/data_manager.c -I include -o data_manager.o

echo در حال ساخت DLL...
gcc -m32 -shared -o lib/property_lib.dll property_lib.o commercial.o residential.o land.o report.o data_manager.o -Wl,--out-implib,lib/libproperty.a

echo در حال پاکسازی فایل‌های موقتی...
del *.o

echo.
echo ساخت کتابخانه با موفقیت انجام شد.
echo کتابخانه 32 بیتی در مسیر lib/property_lib.dll قرار دارد.
pause
```

## مرحله ۳: اطمینان از وجود فایل‌های لازم

پس از اجرای فایل‌ها، فایل `property_lib.dll` باید در پوشه `lib` ایجاد شده باشد.

## مرحله ۴: کپی کردن DLL در مسیرهای سیستمی (اختیاری)

اگر همچنان با مشکل مواجه هستید، DLL را در یکی از مسیرهای زیر کپی کنید:

1. در کنار فایل اجرایی پایتون:
   - مسیر پایتون را با اجرای `where python` در خط فرمان پیدا کنید.
   - فایل DLL را در همان پوشه کپی کنید.

2. در مسیر سیستمی ویندوز:
   - برای پایتون ۶۴ بیتی: `C:\Windows\System32\`
   - برای پایتون ۳۲ بیتی: `C:\Windows\SysWOW64\`

## مرحله ۵: حل مشکلات احتمالی دیگر

اگر با وجود انجام همه مراحل بالا، همچنان با مشکل مواجه هستید:

1. اطمینان حاصل کنید که تمام وابستگی‌های پایتون نصب شده‌اند:
   ```
   pip install -r requirements.txt
   ```

2. اطمینان حاصل کنید که پوشه‌های `data` و `logs` در مسیر پروژه وجود دارند:
   ```
   mkdir data
   mkdir logs
   ```

3. فایل‌های لاگ را در پوشه `logs` بررسی کنید تا جزئیات بیشتری از خطا پیدا کنید.

## راه حل جایگزین: حذف پیوند با کد C

اگر تمامی تلاش‌ها برای کامپایل کد C ناموفق بود، می‌توانید برنامه را در حالت شبیه‌سازی اجرا کنید. برای این کار فایل زیر را ایجاد کنید:

فایل جدیدی به نام `Property_program_project/bridge/mock_lib.py` ایجاد کنید:
```python
# این فایل یک شبیه‌ساز برای کتابخانه C است
import os
import logging

log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'mock_lib.log')

logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger('mock_lib')
logger.info("استفاده از کتابخانه شبیه‌سازی شده به جای کتابخانه C")

# یک کلاس dummy برای جایگزینی ctypes.CDLL
class MockCLib:
    def __getattr__(self, name):
        def mock_function(*args, **kwargs):
            logger.info(f"فراخوانی شبیه‌سازی شده تابع: {name} با آرگومان‌های {args}")
            # برای توابعی که مقداری برمی‌گردانند، یک مقدار پیش‌فرض برگردان
            if name.startswith("residential_") or name.startswith("commercial_") or name.startswith("land_"):
                return 1  # برای توابع ثبت، کد موفقیت
            return None
        return mock_function

# یک نمونه از کلاس MockCLib برای استفاده در کد
c_lib = MockCLib()
```

سپس فایل‌های bridge را تغییر دهید تا از این شبیه‌ساز استفاده کنند.

## کمک بیشتر

اگر همچنان با مشکل مواجه هستید، لطفاً با تیم پشتیبانی تماس بگیرید و اطلاعات زیر را ارائه دهید:
1. خطای دقیق
2. فایل‌های لاگ
3. نسخه و معماری پایتون
4. سیستم عامل و نسخه آن 