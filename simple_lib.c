#include <stdio.h>
#include <windows.h>

// تعریف ماکرو برای صادر کردن توابع
#define DLL_EXPORT __declspec(dllexport)

// یک تابع ساده برای آزمایش
DLL_EXPORT int test_function() {
    return 42;
}

// نقطه ورود DLL
BOOL WINAPI DllMain(HINSTANCE hinstDLL, DWORD fdwReason, LPVOID lpvReserved) {
    switch (fdwReason) {
        case DLL_PROCESS_ATTACH:
            // کد مقداردهی اولیه
            break;
        case DLL_PROCESS_DETACH:
            // کد پاکسازی
            break;
        case DLL_THREAD_ATTACH:
            // کد مربوط به اتصال thread
            break;
        case DLL_THREAD_DETACH:
            // کد مربوط به جدا شدن thread
            break;
    }
    return TRUE;
} 