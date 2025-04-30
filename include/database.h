/**
 * @file database.h
 * @brief مدیریت داده‌ها با استفاده از فایل‌های CSV
 * 
 * این فایل شامل تعاریف توابع مدیریت داده‌ها، خواندن و نوشتن در فایل‌های CSV و عملیات CRUD است.
 */

#ifndef DATABASE_H
#define DATABASE_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include "utils.h"

/**
 * @brief شناسه خطاهای پایگاه داده
 */
#define DB_SUCCESS 0
#define DB_ERROR_OPEN_FILE -1
#define DB_ERROR_READ_FILE -2
#define DB_ERROR_WRITE_FILE -3
#define DB_ERROR_INVALID_PARAMETERS -4
#define DB_ERROR_MEMORY_ALLOCATION -5
#define DB_ERROR_FILE_NOT_FOUND -6
#define DB_ERROR_RECORD_NOT_FOUND -7
#define DB_ERROR_DUPLICATE_KEY -8
#define DB_ERROR_CORRUPTED_DATA -9
#define DB_ERROR_INVALID_FORMAT -10

/**
 * @brief مسیرهای پیش‌فرض فایل‌های داده
 */
#define DEFAULT_BASE_PATH "data"
#define USERS_FILE "users.csv"
#define RESIDENTIAL_SALES_FILE "residential_sales.csv"
#define RESIDENTIAL_RENTALS_FILE "residential_rentals.csv"
#define COMMERCIAL_SALES_FILE "commercial_sales.csv"
#define COMMERCIAL_RENTALS_FILE "commercial_rentals.csv"
#define LAND_SALES_FILE "land_sales.csv"
#define LAND_RENTALS_FILE "land_rentals.csv"
#define PROPERTY_COUNTER_FILE "property_counter.txt"
#define LOG_FILE "log.txt"

/**
 * @brief تنظیم مسیر پایه برای ذخیره‌سازی داده‌ها
 * 
 * @param base_path مسیر پایه
 * @return int کد موفقیت یا شکست
 */
int data_manager_set_base_path(const char* base_path);

/**
 * @brief دریافت مسیر کامل یک فایل داده
 * 
 * @param relative_path مسیر نسبی فایل
 * @param full_path بافر برای ذخیره مسیر کامل
 * @return int کد موفقیت یا شکست
 */
int get_full_path(const char* relative_path, char* full_path);

/**
 * @brief آماده‌سازی فضای ذخیره‌سازی
 * 
 * این تابع دایرکتوری‌ها و فایل‌های مورد نیاز را ایجاد می‌کند.
 * 
 * @return int کد موفقیت یا شکست
 */
int data_manager_init_storage(void);

/**
 * @brief خواندن یک رکورد از یک فایل CSV
 * 
 * @param file_path مسیر فایل CSV
 * @param key مقدار کلید برای جستجو
 * @param key_index شماره ستون کلید
 * @param record_buffer بافر برای ذخیره رکورد یافته شده
 * @param buffer_size سایز بافر
 * @return int کد موفقیت یا شکست
 */
int csv_read_record(const char* file_path, const char* key, int key_index, char* record_buffer, size_t buffer_size);

/**
 * @brief نوشتن یک رکورد در یک فایل CSV
 * 
 * @param file_path مسیر فایل CSV
 * @param record_csv رکورد به فرمت CSV
 * @param key مقدار کلید برای بررسی تکراری بودن
 * @param key_index شماره ستون کلید
 * @param update آیا بروزرسانی انجام شود؟
 * @return int کد موفقیت یا شکست
 */
int csv_write_record(const char* file_path, const char* record_csv, const char* key, int key_index, bool update);

/**
 * @brief حذف یک رکورد از یک فایل CSV
 * 
 * @param file_path مسیر فایل CSV
 * @param key مقدار کلید برای جستجو
 * @param key_index شماره ستون کلید
 * @return int کد موفقیت یا شکست
 */
int csv_delete_record(const char* file_path, const char* key, int key_index);

/**
 * @brief حذف منطقی یک رکورد از یک فایل CSV
 * 
 * @param file_path مسیر فایل CSV
 * @param key مقدار کلید برای جستجو
 * @param key_index شماره ستون کلید
 * @param status_index شماره ستون وضعیت
 * @return int کد موفقیت یا شکست
 */
int csv_logical_delete_record(const char* file_path, const char* key, int key_index, int status_index);

/**
 * @brief جستجو در یک فایل CSV بر اساس معیارهای مختلف
 * 
 * @param file_path مسیر فایل CSV
 * @param criteria تابع معیار جستجو
 * @param criteria_param پارامتر برای تابع معیار
 * @param result_callback تابع فراخوانی برای هر نتیجه
 * @param callback_param پارامتر برای تابع فراخوانی
 * @param count تعداد نتایج یافت شده (خروجی)
 * @return int کد موفقیت یا شکست
 */
int csv_search_records(
    const char* file_path, 
    bool (*criteria)(const char*, void*), 
    void* criteria_param,
    int (*result_callback)(const char*, void*),
    void* callback_param,
    int* count
);

/**
 * @brief خواندن تمام رکوردهای یک فایل CSV
 * 
 * @param file_path مسیر فایل CSV
 * @param result_callback تابع فراخوانی برای هر رکورد
 * @param callback_param پارامتر برای تابع فراخوانی
 * @param count تعداد رکوردهای خوانده شده (خروجی)
 * @return int کد موفقیت یا شکست
 */
int csv_read_all_records(
    const char* file_path,
    int (*result_callback)(const char*, void*),
    void* callback_param,
    int* count
);

/**
 * @brief شمارش تعداد رکوردهای یک فایل CSV
 * 
 * @param file_path مسیر فایل CSV
 * @param count تعداد رکوردها (خروجی)
 * @return int کد موفقیت یا شکست
 */
int csv_count_records(const char* file_path, int* count);

/**
 * @brief تجزیه یک رکورد CSV به فیلدها
 * 
 * @param csv_line خط CSV
 * @param fields آرایه برای ذخیره فیلدها
 * @param max_fields حداکثر تعداد فیلدها
 * @return int تعداد فیلدهای استخراج شده یا کد خطا
 */
int csv_parse_line(const char* csv_line, char** fields, int max_fields);

/**
 * @brief ترکیب فیلدها برای ایجاد یک خط CSV
 * 
 * @param fields آرایه فیلدها
 * @param field_count تعداد فیلدها
 * @param buffer بافر برای ذخیره خط CSV
 * @param buffer_size سایز بافر
 * @return int کد موفقیت یا شکست
 */
int csv_compose_line(const char** fields, int field_count, char* buffer, size_t buffer_size);

/**
 * @brief دریافت شناسه جدید برای یک رکورد جدید
 * 
 * @param prefix پیشوند شناسه (مثلا "USER", "PROP")
 * @param id_buffer بافر برای ذخیره شناسه
 * @param buffer_size سایز بافر
 * @return int کد موفقیت یا شکست
 */
int db_get_next_id(const char* prefix, char* id_buffer, size_t buffer_size);

/**
 * @brief تهیه نسخه پشتیبان از یک فایل داده
 * 
 * @param file_path مسیر فایل داده
 * @return int کد موفقیت یا شکست
 */
int db_backup_file(const char* file_path);

/**
 * @brief بازیابی یک فایل داده از نسخه پشتیبان
 * 
 * @param file_path مسیر فایل داده
 * @return int کد موفقیت یا شکست
 */
int db_restore_file(const char* file_path);

/**
 * @brief تراکنش پایگاه داده
 */
typedef struct {
    char file_path[MAX_PATH_LENGTH];  /**< مسیر فایل */
    FILE* file;                        /**< اشاره‌گر فایل */
    bool is_open;                     /**< آیا تراکنش فعال است؟ */
} DBTransaction;

/**
 * @brief شروع یک تراکنش برای نوشتن در پایگاه داده
 * 
 * @param transaction ساختار تراکنش
 * @param file_path مسیر فایل
 * @return int کد موفقیت یا شکست
 */
int db_transaction_begin(DBTransaction* transaction, const char* file_path);

/**
 * @brief افزودن یک رکورد به تراکنش
 * 
 * @param transaction ساختار تراکنش
 * @param record_csv رکورد به فرمت CSV
 * @return int کد موفقیت یا شکست
 */
int db_transaction_add_record(DBTransaction* transaction, const char* record_csv);

/**
 * @brief پایان تراکنش و ذخیره تغییرات
 * 
 * @param transaction ساختار تراکنش
 * @return int کد موفقیت یا شکست
 */
int db_transaction_commit(DBTransaction* transaction);

/**
 * @brief لغو تراکنش و بازگشت به حالت قبل
 * 
 * @param transaction ساختار تراکنش
 * @return int کد موفقیت یا شکست
 */
int db_transaction_rollback(DBTransaction* transaction);

#endif /* DATABASE_H */ 