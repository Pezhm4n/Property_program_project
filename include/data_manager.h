/**
 * @file data_manager.h
 * @brief مدیریت داده‌های املاک، مدیریت فایل‌ها و پایگاه داده
 */

#ifndef DATA_MANAGER_H
#define DATA_MANAGER_H

#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>

/**
 * @brief مقادیر ثابت مسیرهای ذخیره‌سازی داده‌ها
 */
#define DATA_DIRECTORY "data"
#define USER_DATA_PATH "data/users.csv"
#define PROPERTY_SALES_PATH "data/property_sales.csv"
#define PROPERTY_RENTALS_PATH "data/property_rentals.csv"
#define RESIDENTIAL_SALES_PATH "data/residential_sales.csv"
#define RESIDENTIAL_RENTALS_PATH "data/residential_rentals.csv"
#define COMMERCIAL_SALES_PATH "data/commercial_sales.csv"
#define COMMERCIAL_RENTALS_PATH "data/commercial_rentals.csv"
#define LAND_SALES_PATH "data/land_sales.csv"
#define LAND_RENTALS_PATH "data/land_rentals.csv"
#define LOG_FILE_PATH "data/system_log.txt"

/**
 * @brief ساختار برای تعریف تراکنش‌های پایگاه داده
 */
typedef struct {
    void* data;          /**< اشاره‌گر به داده‌های تراکنش */
    size_t data_size;    /**< اندازه داده‌های تراکنش */
    char file_path[256]; /**< مسیر فایل برای عملیات */
    int operation_type;  /**< نوع عملیات (افزودن، حذف، به‌روزرسانی) */
} DataTransaction;

/**
 * @brief انواع عملیات‌های پایگاه داده
 */
enum DataOperationType {
    OPERATION_INSERT = 1,
    OPERATION_UPDATE = 2,
    OPERATION_DELETE = 3,
    OPERATION_SELECT = 4
};

/**
 * @brief مقدار کد بازگشتی وضعیت عملیات‌ها
 */
enum DataManagerStatus {
    DATA_MANAGER_SUCCESS = 0,
    DATA_MANAGER_FILE_ERROR = -1,
    DATA_MANAGER_MEMORY_ERROR = -2,
    DATA_MANAGER_INVALID_INPUT = -3,
    DATA_MANAGER_NOT_FOUND = -4,
    DATA_MANAGER_DUPLICATE = -5
};

/**
 * @brief تنظیم مسیر پایه برای فایل‌های داده
 * 
 * @param base_path مسیر پایه جدید
 * @return وضعیت عملیات
 */
int data_manager_set_base_path(const char* base_path);

/**
 * @brief بررسی و ایجاد دایرکتوری‌های مورد نیاز در صورت عدم وجود
 * 
 * @return وضعیت عملیات
 */
int data_manager_init_storage();

/**
 * @brief افزودن رکورد جدید به فایل CSV
 * 
 * @param file_path مسیر فایل CSV
 * @param record_data داده‌های رکورد جدید
 * @return وضعیت عملیات
 */
int data_manager_insert_record(const char* file_path, const char* record_data);

/**
 * @brief به‌روزرسانی رکورد در فایل CSV
 * 
 * @param file_path مسیر فایل CSV
 * @param record_id شناسه رکورد
 * @param updated_data داده‌های به‌روز شده
 * @return وضعیت عملیات
 */
int data_manager_update_record(const char* file_path, const char* record_id, const char* updated_data);

/**
 * @brief حذف منطقی رکورد در فایل CSV
 * 
 * @param file_path مسیر فایل CSV
 * @param record_id شناسه رکورد
 * @return وضعیت عملیات
 */
int data_manager_delete_record(const char* file_path, const char* record_id);

/**
 * @brief خواندن کل رکوردهای فایل CSV
 * 
 * @param file_path مسیر فایل CSV
 * @param callback تابع فراخوانی برای هر رکورد
 * @param user_data داده‌های کاربر برای ارسال به callback
 * @return وضعیت عملیات
 */
int data_manager_read_all_records(const char* file_path, void (*callback)(const char*, void*), void* user_data);

/**
 * @brief جستجوی رکورد با مقدار خاص در یک ستون
 * 
 * @param file_path مسیر فایل CSV
 * @param column_index شماره ستون برای جستجو
 * @param search_value مقدار جستجو
 * @param callback تابع فراخوانی برای هر رکورد یافت شده
 * @param user_data داده‌های کاربر برای ارسال به callback
 * @return وضعیت عملیات
 */
int data_manager_find_records(const char* file_path, int column_index, const char* search_value, 
                            void (*callback)(const char*, void*), void* user_data);

/**
 * @brief شمارش تعداد رکوردها در فایل CSV
 * 
 * @param file_path مسیر فایل CSV
 * @return تعداد رکوردها یا کد خطا
 */
int data_manager_count_records(const char* file_path);

/**
 * @brief بررسی وجود رکورد با مقدار خاص در یک ستون
 * 
 * @param file_path مسیر فایل CSV
 * @param column_index شماره ستون برای بررسی
 * @param search_value مقدار جستجو
 * @return true اگر رکورد وجود داشته باشد، false در غیر این صورت
 */
bool data_manager_record_exists(const char* file_path, int column_index, const char* search_value);

/**
 * @brief پشتیبان‌گیری از یک فایل داده
 * 
 * @param file_path مسیر فایل اصلی
 * @param backup_path مسیر فایل پشتیبان
 * @return وضعیت عملیات
 */
int data_manager_backup_file(const char* file_path, const char* backup_path);

/**
 * @brief بازیابی فایل از نسخه پشتیبان
 * 
 * @param backup_path مسیر فایل پشتیبان
 * @param file_path مسیر فایل اصلی
 * @return وضعیت عملیات
 */
int data_manager_restore_from_backup(const char* backup_path, const char* file_path);

/**
 * @brief خواندن یک فایل و بازگرداندن محتوای آن به صورت رشته
 * 
 * @param file_path مسیر فایل
 * @return اشاره‌گر به رشته حاوی محتوای فایل (نیاز به آزادسازی با free)
 */
char* data_manager_read_file_content(const char* file_path);

/**
 * @brief نوشتن محتوا در یک فایل
 * 
 * @param file_path مسیر فایل
 * @param content محتوای مورد نظر
 * @param append اگر true باشد، محتوا به انتهای فایل اضافه می‌شود
 * @return وضعیت عملیات
 */
int data_manager_write_file_content(const char* file_path, const char* content, bool append);

/**
 * @brief تبدیل فایل CSV به JSON
 * 
 * @param csv_file_path مسیر فایل CSV
 * @param json_file_path مسیر فایل JSON
 * @return وضعیت عملیات
 */
int data_manager_convert_csv_to_json(const char* csv_file_path, const char* json_file_path);

/**
 * @brief اجرای یک تراکنش پایگاه داده
 * 
 * @param transaction اشاره‌گر به ساختار تراکنش
 * @return وضعیت عملیات
 */
int data_manager_execute_transaction(DataTransaction* transaction);

/**
 * @brief شروع یک تراکنش چندگانه (برای عملیات‌های اتمیک)
 * 
 * @return اشاره‌گر به ساختار کنترل‌کننده تراکنش
 */
void* data_manager_begin_transaction();

/**
 * @brief تایید و اجرای تراکنش چندگانه
 * 
 * @param transaction_controller اشاره‌گر به ساختار کنترل‌کننده تراکنش
 * @return وضعیت عملیات
 */
int data_manager_commit_transaction(void* transaction_controller);

/**
 * @brief لغو تراکنش چندگانه
 * 
 * @param transaction_controller اشاره‌گر به ساختار کنترل‌کننده تراکنش
 * @return وضعیت عملیات
 */
int data_manager_rollback_transaction(void* transaction_controller);

#endif /* DATA_MANAGER_H */ 