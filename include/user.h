/**
 * @file user.h
 * @brief تعاریف و توابع مرتبط با مدیریت کاربران
 */

#ifndef PROPERTY_LIB_USER_H
#define PROPERTY_LIB_USER_H

#ifdef __cplusplus
extern "C" {
#endif

#include <stdbool.h>
#include <time.h>

/**
 * @struct User
 * @brief ساختار ذخیره‌سازی اطلاعات کاربر
 */
typedef struct User {
    char username[50];          /**< نام کاربری (منحصر به فرد) */
    char password[100];         /**< رمز عبور (هش شده) */
    char name[50];              /**< نام */
    char lastName[50];          /**< نام خانوادگی */
    char nationalCode[20];      /**< کد ملی */
    char phoneNumber[20];       /**< شماره تلفن */
    char email[50];             /**< ایمیل */
    char registrationDateTime[50]; /**< زمان ثبت‌نام */
    time_t lastLoginTime;       /**< آخرین زمان ورود به سیستم */
    int propertyCount;          /**< تعداد املاک ثبت شده توسط کاربر */
    struct User* next;          /**< اشاره‌گر به کاربر بعدی (برای لیست پیوندی) */
} User;

/**
 * @brief ثبت‌نام کاربر جدید
 * 
 * @param username نام کاربری
 * @param password رمز عبور
 * @param name نام
 * @param lastName نام خانوادگی
 * @param nationalCode کد ملی
 * @param phoneNumber شماره تلفن
 * @param email ایمیل
 * @return int کد خطا: 0 (موفق)، 1 (نام کاربری تکراری)، 2 (خطای اعتبارسنجی)، 3 (خطای فایل)
 * 
 * @example
 * int result = user_register("ali123", "StrongPass123!", "علی", "محمدی", "1234567890", "09123456789", "ali@example.com");
 * if (result == 0) {
 *     printf("ثبت‌نام موفق بود\n");
 * } else if (result == 1) {
 *     printf("این نام کاربری قبلاً استفاده شده است\n");
 * }
 */
int user_register(const char* username, const char* password, const char* name, 
                 const char* lastName, const char* nationalCode, 
                 const char* phoneNumber, const char* email);

/**
 * @brief ورود کاربر به سیستم
 * 
 * @param username نام کاربری
 * @param password رمز عبور
 * @param out_user اشاره‌گر به ساختار کاربر برای پر کردن اطلاعات در صورت موفقیت
 * @return int کد خطا: 0 (موفق)، 1 (نام کاربری یا رمز عبور اشتباه)، 2 (حساب قفل شده)، 3 (خطای فایل)
 */
int user_login(const char* username, const char* password, User* out_user);

/**
 * @brief تغییر رمز عبور کاربر
 * 
 * @param username نام کاربری
 * @param currentPassword رمز عبور فعلی
 * @param newPassword رمز عبور جدید
 * @return int کد خطا: 0 (موفق)، 1 (رمز عبور فعلی اشتباه)، 2 (رمز عبور جدید ضعیف)، 3 (خطای فایل)
 */
int user_change_password(const char* username, const char* currentPassword, const char* newPassword);

/**
 * @brief تغییر اطلاعات پروفایل کاربر
 * 
 * @param username نام کاربری
 * @param fieldName نام فیلد ("name", "lastName", "email", "phoneNumber")
 * @param newValue مقدار جدید
 * @return int کد خطا: 0 (موفق)، 1 (فیلد نامعتبر)، 2 (مقدار نامعتبر)، 3 (خطای فایل)
 */
int user_update_profile(const char* username, const char* fieldName, const char* newValue);

/**
 * @brief بررسی اعتبار نام کاربری (بدون کاراکتر خاص و فاصله)
 * 
 * @param username نام کاربری
 * @return bool صحیح اگر معتبر است، غلط در غیر این صورت
 */
bool user_is_valid_username(const char* username);

/**
 * @brief بررسی تکراری بودن نام کاربری
 * 
 * @param username نام کاربری
 * @return bool صحیح اگر تکراری است، غلط در غیر این صورت
 */
bool user_is_duplicate_username(const char* username);

/**
 * @brief بررسی اعتبار رمز عبور (حداقل ۸ کاراکتر، شامل حروف بزرگ، کوچک و عدد)
 * 
 * @param password رمز عبور
 * @return bool صحیح اگر معتبر است، غلط در غیر این صورت
 */
bool user_is_strong_password(const char* password);

/**
 * @brief بررسی اعتبار ایمیل
 * 
 * @param email ایمیل
 * @return bool صحیح اگر معتبر است، غلط در غیر این صورت
 */
bool user_is_valid_email(const char* email);

/**
 * @brief بررسی اعتبار شماره تلفن
 * 
 * @param phoneNumber شماره تلفن
 * @return bool صحیح اگر معتبر است، غلط در غیر این صورت
 */
bool user_is_valid_phone_number(const char* phoneNumber);

/**
 * @brief بررسی اعتبار کد ملی
 * 
 * @param nationalCode کد ملی
 * @return bool صحیح اگر معتبر است، غلط در غیر این صورت
 */
bool user_is_valid_national_code(const char* nationalCode);

/**
 * @brief ثبت تلاش ناموفق ورود
 * 
 * @param username نام کاربری
 * @return int تعداد تلاش‌های ناموفق تا کنون
 */
int user_record_failed_attempt(const char* username);

/**
 * @brief بررسی وضعیت قفل حساب کاربری
 * 
 * @param username نام کاربری
 * @param remainingSeconds خروجی: زمان باقی‌مانده تا رفع قفل (ثانیه)
 * @return bool صحیح اگر حساب قفل است، غلط در غیر این صورت
 */
bool user_is_account_locked(const char* username, long* remainingSeconds);

/**
 * @brief به‌روزرسانی زمان آخرین ورود کاربر
 * 
 * @param username نام کاربری
 * @return int کد خطا: 0 (موفق)، 1 (کاربر یافت نشد)، 2 (خطای فایل)
 */
int user_update_last_login(const char* username);

/**
 * @brief دریافت لیست کاربران بر اساس تعداد املاک ثبت شده
 * 
 * @param users_count خروجی: تعداد کاربران بازگشتی
 * @return User* آرایه‌ای از کاربران (باید با user_free_list آزاد شود)
 */
User* user_get_by_property_count(int* users_count);

/**
 * @brief آزاد کردن حافظه لیست کاربران
 * 
 * @param users لیست کاربران
 * @param count تعداد کاربران
 */
void user_free_list(User* users, int count);

#ifdef __cplusplus
}  // extern "C"
#endif

#endif  // PROPERTY_LIB_USER_H 