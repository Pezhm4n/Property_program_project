/**
 * @file utils.h
 * @brief توابع کمکی مورد نیاز برای برنامه مدیریت املاک
 * 
 * این فایل شامل تعاریف توابع کمکی مانند تاریخ، رمزنگاری، اعتبارسنجی و تولید شناسه است.
 */

#ifndef UTILS_H
#define UTILS_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <ctype.h>
#include <stdbool.h>

#ifdef _WIN32
#include <direct.h>
#define MKDIR(dir) _mkdir(dir)
#define PATH_SEPARATOR '\\'
#else
#include <sys/stat.h>
#include <sys/types.h>
#define MKDIR(dir) mkdir(dir, 0755)
#define PATH_SEPARATOR '/'
#endif

/**
 * @brief حداکثر طول مسیر فایل
 */
#define MAX_PATH_LENGTH 256

/**
 * @brief حداکثر طول رشته برای اسامی و آدرس‌ها
 */
#define MAX_STRING_LENGTH 256

/**
 * @brief حداکثر طول پیام‌های لاگ
 */
#define MAX_LOG_MESSAGE 512

/**
 * @brief حداکثر طول رشته تاریخ
 */
#define MAX_DATE_LENGTH 20

/**
 * @brief حداکثر طول کلمه عبور
 */
#define MAX_PASSWORD_LENGTH 64

/**
 * @brief حداکثر طول شناسه
 */
#define MAX_ID_LENGTH 50

/**
 * @brief حداکثر طول شماره تماس
 */
#define MAX_PHONE_LENGTH 20

/**
 * @brief حداکثر طول ایمیل
 */
#define MAX_EMAIL_LENGTH 100

/**
 * @brief حداکثر طول توضیحات
 */
#define MAX_DESCRIPTION_LENGTH 500

/**
 * @brief ساختار تاریخ
 */
typedef struct {
    int year;   /**< سال */
    int month;  /**< ماه */
    int day;    /**< روز */
} Date;

/**
 * @brief تابع ثبت پیام‌های لاگ
 * 
 * @param format قالب پیام لاگ
 * @param ... متغیرهای مورد استفاده در پیام
 * @return int کد موفقیت یا شکست
 */
int property_log(const char* format, ...);

/**
 * @brief تولید شناسه یکتا برای املاک
 * 
 * @param id_buffer بافر ذخیره شناسه تولید شده
 * @param prefix پیشوند شناسه
 * @return int کد موفقیت یا شکست
 */
int generate_property_id(char* id_buffer, const char* prefix);

/**
 * @brief ایجاد کپی از یک رشته
 * 
 * @param str رشته منبع
 * @return char* رشته کپی شده (باید با free آزاد شود)
 */
char* string_duplicate(const char* str);

/**
 * @brief اعتبارسنجی یک رشته (خالی نبودن و داشتن حداقل طول)
 * 
 * @param str رشته مورد بررسی
 * @param min_length حداقل طول مورد نظر
 * @return bool نتیجه اعتبارسنجی
 */
bool validate_string(const char* str, int min_length);

/**
 * @brief اعتبارسنجی فرمت تاریخ (YYYY-MM-DD)
 * 
 * @param date_str رشته تاریخ
 * @return bool نتیجه اعتبارسنجی
 */
bool validate_date_format(const char* date_str);

/**
 * @brief اعتبارسنجی فرمت شماره تلفن
 * 
 * @param phone رشته شماره تلفن
 * @return bool نتیجه اعتبارسنجی
 */
bool validate_phone_number(const char* phone);

/**
 * @brief اعتبارسنجی فرمت ایمیل
 * 
 * @param email رشته ایمیل
 * @return bool نتیجه اعتبارسنجی
 */
bool validate_email(const char* email);

/**
 * @brief اعتبارسنجی قیمت
 * 
 * @param price مقدار قیمت
 * @return bool نتیجه اعتبارسنجی
 */
bool validate_price(double price);

/**
 * @brief اعتبارسنجی مساحت
 * 
 * @param area مقدار مساحت
 * @return bool نتیجه اعتبارسنجی
 */
bool validate_area(float area);

/**
 * @brief تبدیل تاریخ به رشته
 * 
 * @param date ساختار تاریخ
 * @param date_str بافر رشته تاریخ
 * @return int کد موفقیت یا شکست
 */
int date_to_string(const Date* date, char* date_str);

/**
 * @brief تبدیل رشته به تاریخ
 * 
 * @param date_str رشته تاریخ
 * @param date ساختار تاریخ
 * @return int کد موفقیت یا شکست
 */
int string_to_date(const char* date_str, Date* date);

/**
 * @brief دریافت تاریخ فعلی
 * 
 * @param date ساختار تاریخ
 * @return int کد موفقیت یا شکست
 */
int get_current_date(Date* date);

/**
 * @brief دریافت تاریخ فعلی به صورت رشته
 * 
 * @param date_str بافر رشته تاریخ
 * @return int کد موفقیت یا شکست
 */
int get_current_date_string(char* date_str);

/**
 * @brief مقایسه دو تاریخ
 * 
 * @param date1 تاریخ اول
 * @param date2 تاریخ دوم
 * @return int نتیجه مقایسه (-1: کوچکتر، 0: برابر، 1: بزرگتر)
 */
int compare_dates(const Date* date1, const Date* date2);

/**
 * @brief مقایسه دو تاریخ به صورت رشته
 * 
 * @param date1_str رشته تاریخ اول
 * @param date2_str رشته تاریخ دوم
 * @return int نتیجه مقایسه (-1: کوچکتر، 0: برابر، 1: بزرگتر)
 */
int compare_date_strings(const char* date1_str, const char* date2_str);

/**
 * @brief رمزنگاری ساده رشته کلمه عبور
 * 
 * @param password کلمه عبور اصلی
 * @param hashed_password بافر کلمه عبور رمزنگاری شده
 * @return int کد موفقیت یا شکست
 */
int hash_password(const char* password, char* hashed_password);

/**
 * @brief مقایسه کلمه عبور با نسخه رمزنگاری شده
 * 
 * @param password کلمه عبور
 * @param hashed_password کلمه عبور رمزنگاری شده
 * @return bool نتیجه مقایسه
 */
bool verify_password(const char* password, const char* hashed_password);

/**
 * @brief تبدیل حروف به حروف کوچک
 * 
 * @param str رشته ورودی/خروجی
 */
void string_to_lower(char* str);

/**
 * @brief حذف فاصله‌های اضافی از ابتدا و انتهای رشته
 * 
 * @param str رشته ورودی/خروجی
 */
void trim_string(char* str);

/**
 * @brief ترکیب دو مسیر فایل
 * 
 * @param base_path مسیر پایه
 * @param relative_path مسیر نسبی
 * @param result_path بافر مسیر نتیجه
 * @return int کد موفقیت یا شکست
 */
int combine_paths(const char* base_path, const char* relative_path, char* result_path);

/**
 * @brief ایجاد دایرکتوری‌ها برای یک مسیر فایل
 * 
 * @param file_path مسیر فایل
 * @return int کد موفقیت یا شکست
 */
int create_directories_for_file(const char* file_path);

/**
 * @brief بررسی وجود فایل
 * 
 * @param file_path مسیر فایل
 * @return bool نتیجه بررسی
 */
bool file_exists(const char* file_path);

/**
 * @brief اسکیپ کردن کاراکترهای خاص برای استفاده در CSV
 * 
 * @param src رشته منبع
 * @param dest بافر رشته مقصد
 * @param dest_size سایز بافر مقصد
 * @return int کد موفقیت یا شکست
 */
int escape_csv_field(const char* src, char* dest, size_t dest_size);

/**
 * @brief برگرداندن اسکیپ کاراکترهای خاص در CSV
 * 
 * @param src رشته منبع
 * @param dest بافر رشته مقصد
 * @param dest_size سایز بافر مقصد
 * @return int کد موفقیت یا شکست
 */
int unescape_csv_field(const char* src, char* dest, size_t dest_size);

#endif /* UTILS_H */ 