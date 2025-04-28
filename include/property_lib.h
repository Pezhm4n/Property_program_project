/**
 * @file property_lib.h
 * @brief فایل هدر اصلی کتابخانه مدیریت املاک
 * 
 * این فایل شامل تمام فایل‌های هدر دیگر است و نقطه ورودی اصلی برای استفاده از کتابخانه می‌باشد.
 * 
 * @version 1.0.0
 * @date 1402/04/15
 */

#ifndef PROPERTY_LIB_H
#define PROPERTY_LIB_H

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief نسخه کتابخانه
 */
#define PROPERTY_LIB_VERSION "1.0.0"

/**
 * @brief کد خطاهای عمومی کتابخانه
 */
typedef enum {
    PROPERTY_SUCCESS = 0,           /**< عملیات موفق */
    PROPERTY_ERROR_VALIDATION = 1,  /**< خطای اعتبارسنجی */
    PROPERTY_ERROR_FILE = 2,        /**< خطای فایل */
    PROPERTY_ERROR_MEMORY = 3,      /**< خطای حافظه */
    PROPERTY_ERROR_NOT_FOUND = 4,   /**< مورد یافت نشد */
    PROPERTY_ERROR_PERMISSION = 5,  /**< عدم دسترسی */
    PROPERTY_ERROR_DUPLICATE = 6    /**< موجودیت تکراری */
} PropertyError;

/**
 * @brief تنظیم مسیر ذخیره‌سازی فایل‌های داده
 * 
 * این تابع را در ابتدای برنامه فراخوانی کنید تا مسیر ذخیره‌سازی فایل‌ها تنظیم شود.
 * 
 * @param path مسیر ذخیره‌سازی
 * @return int کد خطا: 0 (موفق)، 2 (خطای دسترسی به مسیر)
 */
int property_set_data_path(const char* path);

/**
 * @brief دریافت نسخه کتابخانه
 * 
 * @return const char* رشته نسخه کتابخانه
 */
const char* property_get_version();

/**
 * @brief تبدیل کد خطا به پیام خطا
 * 
 * @param error_code کد خطا
 * @return const char* پیام خطا
 */
const char* property_error_to_string(int error_code);

/**
 * @brief نوشتن پیام در فایل لاگ
 * 
 * @param level سطح لاگ ("INFO", "WARNING", "ERROR", "DEBUG")
 * @param message پیام
 * @return int کد خطا: 0 (موفق)، 2 (خطای فایل)
 */
int property_log(const char* level, const char* message);

// شامل کردن فایل‌های هدر ماژول‌ها
#include "user.h"
#include "property.h"
#include "residential.h"
#include "commercial.h"
#include "land.h"
#include "data_manager.h"
#include "report.h"
#include "utils.h"

#ifdef __cplusplus
}  // extern "C"
#endif

#endif  // PROPERTY_LIB_H 