@echo off
echo در حال ساخت کتابخانه property_lib برای ویندوز 32 بیتی...

REM بررسی وجود کامپایلر
where gcc >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo خطا: کامپایلر GCC یافت نشد!
    echo لطفاً MinGW یا تولچین مشابه دیگری را نصب کنید.
    echo برای نصب MinGW-w64 می‌توانید از msys2 استفاده کنید: https://www.msys2.org
    pause
    exit /b 1
)

REM ایجاد دایرکتوری خروجی اگر وجود ندارد
if not exist "lib" mkdir lib

echo در حال کامپایل فایل‌های منبع C...
REM کامپایل فایل‌های منبع C با تنظیمات 32 بیتی
gcc -c -m32 src/property_lib.c -I include -o property_lib.o
if %ERRORLEVEL% NEQ 0 goto error

gcc -c -m32 src/commercial.c -I include -o commercial.o
if %ERRORLEVEL% NEQ 0 goto error

gcc -c -m32 src/residential.c -I include -o residential.o
if %ERRORLEVEL% NEQ 0 goto error

gcc -c -m32 src/land.c -I include -o land.o
if %ERRORLEVEL% NEQ 0 goto error

gcc -c -m32 src/report.c -I include -o report.o
if %ERRORLEVEL% NEQ 0 goto error

gcc -c -m32 src/data_manager.c -I include -o data_manager.o
if %ERRORLEVEL% NEQ 0 goto error

echo در حال ساخت DLL...
REM ساخت DLL 32 بیتی
gcc -m32 -shared -o lib/property_lib_32.dll property_lib.o commercial.o residential.o land.o report.o data_manager.o -Wl,--out-implib,lib/libproperty_32.a
if %ERRORLEVEL% NEQ 0 goto error

echo در حال پاکسازی فایل‌های موقتی...
REM پاکسازی فایل‌های موقتی
del *.o

echo.
echo ساخت کتابخانه با موفقیت انجام شد.
echo کتابخانه 32 بیتی در مسیر lib/property_lib_32.dll قرار دارد.
goto end

:error
echo خطا در فرآیند کامپایل رخ داد.
exit /b 1

:end
pause 