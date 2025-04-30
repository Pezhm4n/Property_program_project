@echo off
echo در حال ساخت کتابخانه property_lib برای ویندوز...

REM ایجاد دایرکتوری خروجی اگر وجود ندارد
if not exist "lib" mkdir lib

REM کامپایل فایل‌های منبع C
gcc -c src/property_lib.c src/commercial.c src/residential.c src/land.c src/report.c src/data_manager.c -I include

REM ساخت DLL
gcc -shared -o lib/property_lib.dll property_lib.o commercial.o residential.o land.o report.o data_manager.o -Wl,--out-implib,lib/libproperty.a

REM پاکسازی فایل‌های موقتی
del *.o

echo ساخت کتابخانه با موفقیت انجام شد.
echo کتابخانه در مسیر lib/property_lib.dll قرار دارد. 