/**
 * @file data_manager.c
 * @brief پیاده‌سازی توابع مدیریت داده برای برنامه مدیریت املاک
 */

#include "../include/data_manager.h"
#include "../include/logger.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <time.h>
#include <sys/stat.h>
#include <errno.h>

#ifdef _WIN32
#include <direct.h>
#define MKDIR(dir) _mkdir(dir)
#else
#define MKDIR(dir) mkdir(dir, 0755)
#endif

// مسیر پایه برای ذخیره داده‌ها
static char base_path[256] = "";

// وضعیت تراکنش‌های فعلی
static bool transaction_active = false;
static DataTransaction* transactions = NULL;
static int transaction_count = 0;
static int transaction_capacity = 0;

/**
 * @brief تنظیم مسیر پایه برای ذخیره داده‌ها
 * @param path مسیر پایه
 * @return وضعیت عملیات
 */
DataManagerStatus data_manager_set_base_path(const char* path) {
    if (path == NULL || strlen(path) == 0 || strlen(path) > 255) {
        log_error("مسیر پایه نامعتبر است: %s", path == NULL ? "NULL" : path);
        return DATA_MANAGER_INVALID_PATH;
    }
    
    strcpy(base_path, path);
    log_info("مسیر پایه برای ذخیره داده‌ها تنظیم شد: %s", base_path);
    return DATA_MANAGER_SUCCESS;
}

/**
 * @brief ترکیب مسیر پایه با مسیر نسبی
 * @param relative_path مسیر نسبی
 * @param full_path خروجی: مسیر کامل
 * @param full_path_size اندازه آرایه مسیر کامل
 * @return وضعیت عملیات
 */
static DataManagerStatus get_full_path(const char* relative_path, char* full_path, size_t full_path_size) {
    if (relative_path == NULL || full_path == NULL) {
        log_error("مسیر نامعتبر است");
        return DATA_MANAGER_INVALID_PATH;
    }
    
    if (strlen(base_path) == 0) {
        // اگر مسیر پایه تنظیم نشده است، مسیر نسبی را برگردان
        if (strlen(relative_path) >= full_path_size) {
            log_error("اندازه مسیر بیش از حد مجاز است");
            return DATA_MANAGER_INVALID_PATH;
        }
        strcpy(full_path, relative_path);
    } else {
        // ترکیب مسیر پایه با مسیر نسبی
        if (strlen(base_path) + strlen(relative_path) + 1 >= full_path_size) {
            log_error("اندازه مسیر ترکیبی بیش از حد مجاز است");
            return DATA_MANAGER_INVALID_PATH;
        }
        
        strcpy(full_path, base_path);
        
        // اطمینان از وجود '/' بین مسیر پایه و مسیر نسبی
        if (base_path[strlen(base_path) - 1] != '/' && relative_path[0] != '/') {
            strcat(full_path, "/");
        }
        
        strcat(full_path, relative_path);
    }
    
    return DATA_MANAGER_SUCCESS;
}

/**
 * @brief ایجاد دایرکتوری‌های مورد نیاز برای فایل
 * @param path مسیر فایل
 * @return وضعیت عملیات
 */
static DataManagerStatus create_directories_for_file(const char* path) {
    char dir_path[512];
    strcpy(dir_path, path);
    
    // یافتن آخرین '/' در مسیر
    char* last_slash = strrchr(dir_path, '/');
    if (last_slash == NULL) {
        // فایل در دایرکتوری فعلی است، نیازی به ایجاد دایرکتوری نیست
        return DATA_MANAGER_SUCCESS;
    }
    
    // قطع رشته در محل آخرین '/' برای گرفتن مسیر دایرکتوری
    *last_slash = '\0';
    
    // ایجاد دایرکتوری مورد نیاز
#ifdef _WIN32
    // در ویندوز، از mkdir بدون پارامتر دوم استفاده می‌شود
    if (mkdir(dir_path) != 0 && errno != EEXIST) {
#else
    // در سیستم‌های شبیه به یونیکس، از mkdir با پارامتر دوم استفاده می‌شود
    if (mkdir(dir_path, 0755) != 0 && errno != EEXIST) {
#endif
        log_error("خطا در ایجاد دایرکتوری: %s (خطا: %d)", dir_path, errno);
        return DATA_MANAGER_IO_ERROR;
    }
    
    return DATA_MANAGER_SUCCESS;
}

/**
 * @brief آماده‌سازی فضای ذخیره‌سازی
 * @return وضعیت عملیات
 */
DataManagerStatus data_manager_init_storage(void) {
    // ایجاد دایرکتوری "data" اگر وجود ندارد
    char data_dir[512];
    if (strlen(base_path) == 0) {
        strcpy(data_dir, "data");
    } else {
        sprintf(data_dir, "%s/data", base_path);
    }
    
#ifdef _WIN32
    // در ویندوز، از mkdir بدون پارامتر دوم استفاده می‌شود
    if (mkdir(data_dir) != 0 && errno != EEXIST) {
#else
    // در سیستم‌های شبیه به یونیکس، از mkdir با پارامتر دوم استفاده می‌شود
    if (mkdir(data_dir, 0755) != 0 && errno != EEXIST) {
#endif
        log_error("خطا در ایجاد دایرکتوری داده: %s (خطا: %d)", data_dir, errno);
        return DATA_MANAGER_IO_ERROR;
    }
    
    // ایجاد فایل‌های مورد نیاز اگر وجود ندارند
    const char* required_files[] = {
        USER_DATA_PATH,
        PROPERTY_SALES_PATH,
        PROPERTY_RENTALS_PATH,
        RESIDENTIAL_SALES_PATH,
        RESIDENTIAL_RENTALS_PATH,
        COMMERCIAL_SALES_PATH,
        COMMERCIAL_RENTALS_PATH,
        LAND_SALES_PATH,
        LAND_RENTALS_PATH
    };
    
    for (int i = 0; i < sizeof(required_files) / sizeof(required_files[0]); i++) {
        char full_path[512];
        if (get_full_path(required_files[i], full_path, sizeof(full_path)) != DATA_MANAGER_SUCCESS) {
            continue;
        }
        
        // ایجاد دایرکتوری‌های مورد نیاز
        if (create_directories_for_file(full_path) != DATA_MANAGER_SUCCESS) {
            continue;
        }
        
        // بررسی وجود فایل
        FILE* file = fopen(full_path, "r");
        if (file == NULL) {
            // فایل وجود ندارد، ایجاد آن
            file = fopen(full_path, "w");
            if (file == NULL) {
                log_error("خطا در ایجاد فایل: %s", full_path);
                continue;
            }
            // اضافه کردن سربرگ CSV بر اساس نوع فایل
            if (strstr(required_files[i], "users.csv") != NULL) {
                fprintf(file, "username,password,fullname,email,phone,role,active,created_date\n");
            } else if (strstr(required_files[i], "sales.csv") != NULL) {
                fprintf(file, "id,username,district,address,property_type,price,registration_date,active,deleted_date\n");
            } else if (strstr(required_files[i], "rentals.csv") != NULL) {
                fprintf(file, "id,username,district,address,property_type,mortgage,rent,registration_date,active,deleted_date\n");
            }
            log_info("فایل ایجاد شد: %s", full_path);
        }
        fclose(file);
    }
    
    log_info("فضای ذخیره‌سازی با موفقیت آماده‌سازی شد");
    return DATA_MANAGER_SUCCESS;
}

int data_manager_initialize() {
    char full_path[512];
    char log_message[256];
    
    // ایجاد پوشه اصلی داده‌ها
    snprintf(full_path, sizeof(full_path), "%sdata", base_path);
    
    if (MKDIR(full_path) != 0) {
        // اگر پوشه وجود دارد، خطا نیست
        if (errno != EEXIST) {
            snprintf(log_message, sizeof(log_message), 
                    "Failed to create data directory: %s", full_path);
            log_error(log_message);
            return DATA_MANAGER_ERROR_DIRECTORY;
        }
    }
    
    // ایجاد زیرپوشه‌های مورد نیاز
    const char* subdirs[] = {"logs", "users", "backups"};
    
    for (int i = 0; i < 3; i++) {
        snprintf(full_path, sizeof(full_path), "%sdata/%s", base_path, subdirs[i]);
        
        if (MKDIR(full_path) != 0) {
            if (errno != EEXIST) {
                snprintf(log_message, sizeof(log_message), 
                        "Failed to create subdirectory: %s", full_path);
                log_error(log_message);
                return DATA_MANAGER_ERROR_DIRECTORY;
            }
        }
    }
    
    // ایجاد فایل‌های اولیه مورد نیاز
    const char* files[] = {
        "data/property_counter.txt",
        "data/users.csv",
        "data/residential_sales.csv",
        "data/residential_rentals.csv",
        "data/commercial_sales.csv",
        "data/commercial_rentals.csv",
        "data/land_sales.csv",
        "data/land_rentals.csv"
    };
    
    for (int i = 0; i < 8; i++) {
        snprintf(full_path, sizeof(full_path), "%s%s", base_path, files[i]);
        
        FILE* file = fopen(full_path, "a");
        if (!file) {
            snprintf(log_message, sizeof(log_message), 
                    "Failed to create/open file: %s", full_path);
            log_error(log_message);
            return DATA_MANAGER_ERROR_FILE;
        }
        
        fclose(file);
    }
    
    // مقداردهی اولیه شمارنده املاک اگر خالی است
    snprintf(full_path, sizeof(full_path), "%sdata/property_counter.txt", base_path);
    FILE* counter_file = fopen(full_path, "r");
    
    if (counter_file) {
        char buffer[20] = {0};
        if (fgets(buffer, sizeof(buffer), counter_file) == NULL || strlen(buffer) == 0) {
            fclose(counter_file);
            
            // فایل خالی است، مقدار اولیه را ثبت می‌کنیم
            counter_file = fopen(full_path, "w");
            if (counter_file) {
                fprintf(counter_file, "1000"); // مقدار اولیه برای شمارنده
                fclose(counter_file);
            }
        } else {
            fclose(counter_file);
        }
    }
    
    log_info("Data manager initialized successfully");
    return DATA_MANAGER_SUCCESS;
}

const char* data_manager_get_base_path() {
    return base_path;
}

int data_manager_get_file_path(char* out_path, size_t path_size, const char* filename) {
    if (!out_path || !filename || path_size == 0) {
        log_error("Invalid parameters for data_manager_get_file_path");
        return DATA_MANAGER_ERROR_INVALID_PARAMETER;
    }
    
    snprintf(out_path, path_size, "%s%s", base_path, filename);
    return DATA_MANAGER_SUCCESS;
}

int data_manager_backup_database() {
    char backup_dir[512];
    char backup_file[512];
    char src_file[512];
    char log_message[256];
    time_t now = time(NULL);
    struct tm* tm_info = localtime(&now);
    char timestamp[32];
    
    // ایجاد تایم‌استمپ برای نام فایل پشتیبان
    strftime(timestamp, sizeof(timestamp), "%Y%m%d_%H%M%S", tm_info);
    
    // مسیر پوشه پشتیبان
    snprintf(backup_dir, sizeof(backup_dir), "%sdata/backups", base_path);
    
    // لیست فایل‌های مورد نیاز برای پشتیبان‌گیری
    const char* files[] = {
        "data/property_counter.txt",
        "data/users.csv",
        "data/residential_sales.csv",
        "data/residential_rentals.csv",
        "data/commercial_sales.csv",
        "data/commercial_rentals.csv",
        "data/land_sales.csv",
        "data/land_rentals.csv"
    };
    
    for (int i = 0; i < 8; i++) {
        // مسیر فایل اصلی
        snprintf(src_file, sizeof(src_file), "%s%s", base_path, files[i]);
        
        // نام فایل بدون مسیر
        const char* filename = strrchr(files[i], '/');
        if (!filename) {
            filename = files[i];
        } else {
            filename++; // رد کردن کاراکتر '/'
        }
        
        // مسیر فایل پشتیبان
        snprintf(backup_file, sizeof(backup_file), "%s/%s_%s", backup_dir, filename, timestamp);
        
        // کپی فایل
        FILE* src = fopen(src_file, "rb");
        if (!src) {
            snprintf(log_message, sizeof(log_message), 
                    "Failed to open source file for backup: %s", src_file);
            log_warning(log_message);
            continue;
        }
        
        FILE* dest = fopen(backup_file, "wb");
        if (!dest) {
            snprintf(log_message, sizeof(log_message), 
                    "Failed to create backup file: %s", backup_file);
            log_error(log_message);
            fclose(src);
            return DATA_MANAGER_ERROR_FILE;
        }
        
        // کپی محتوا
        char buffer[4096];
        size_t bytes;
        
        while ((bytes = fread(buffer, 1, sizeof(buffer), src)) > 0) {
            fwrite(buffer, 1, bytes, dest);
        }
        
        fclose(src);
        fclose(dest);
        
        snprintf(log_message, sizeof(log_message), 
                "Backup created: %s", backup_file);
        log_info(log_message);
    }
    
    return DATA_MANAGER_SUCCESS;
}

int data_manager_export_csv(const char* source_file, const char* export_path) {
    char src_path[512];
    char log_message[256];
    
    if (!source_file || !export_path) {
        log_error("Invalid parameters for data_manager_export_csv");
        return DATA_MANAGER_ERROR_INVALID_PARAMETER;
    }
    
    // مسیر کامل فایل منبع
    snprintf(src_path, sizeof(src_path), "%s%s", base_path, source_file);
    
    // کپی فایل به مقصد
    FILE* src = fopen(src_path, "rb");
    if (!src) {
        snprintf(log_message, sizeof(log_message), 
                "Failed to open source file for export: %s", src_path);
        log_error(log_message);
        return DATA_MANAGER_ERROR_FILE;
    }
    
    FILE* dest = fopen(export_path, "wb");
    if (!dest) {
        snprintf(log_message, sizeof(log_message), 
                "Failed to create export file: %s", export_path);
        log_error(log_message);
        fclose(src);
        return DATA_MANAGER_ERROR_FILE;
    }
    
    // کپی محتوا
    char buffer[4096];
    size_t bytes;
    
    while ((bytes = fread(buffer, 1, sizeof(buffer), src)) > 0) {
        fwrite(buffer, 1, bytes, dest);
    }
    
    fclose(src);
    fclose(dest);
    
    snprintf(log_message, sizeof(log_message), 
            "CSV exported: %s -> %s", source_file, export_path);
    log_info(log_message);
    
    return DATA_MANAGER_SUCCESS;
}

int data_manager_import_csv(const char* import_path, const char* target_file) {
    char dest_path[512];
    char backup_path[512];
    char log_message[256];
    time_t now = time(NULL);
    struct tm* tm_info = localtime(&now);
    char timestamp[32];
    
    if (!import_path || !target_file) {
        log_error("Invalid parameters for data_manager_import_csv");
        return DATA_MANAGER_ERROR_INVALID_PARAMETER;
    }
    
    // ایجاد تایم‌استمپ برای نام فایل پشتیبان
    strftime(timestamp, sizeof(timestamp), "%Y%m%d_%H%M%S", tm_info);
    
    // مسیر کامل فایل هدف
    snprintf(dest_path, sizeof(dest_path), "%s%s", base_path, target_file);
    
    // ایجاد پشتیبان از فایل هدف قبل از وارد کردن
    const char* filename = strrchr(target_file, '/');
    if (!filename) {
        filename = target_file;
    } else {
        filename++; // رد کردن کاراکتر '/'
    }
    
    snprintf(backup_path, sizeof(backup_path), "%sdata/backups/%s_before_import_%s",
            base_path, filename, timestamp);
    
    // کپی فایل هدف به عنوان پشتیبان
    FILE* src = fopen(dest_path, "rb");
    if (src) {
        FILE* backup = fopen(backup_path, "wb");
        if (backup) {
            char buffer[4096];
            size_t bytes;
            
            while ((bytes = fread(buffer, 1, sizeof(buffer), src)) > 0) {
                fwrite(buffer, 1, bytes, backup);
            }
            
            fclose(backup);
            snprintf(log_message, sizeof(log_message), 
                    "Backup created before import: %s", backup_path);
            log_info(log_message);
        }
        fclose(src);
    }
    
    // وارد کردن فایل جدید
    FILE* import_file = fopen(import_path, "rb");
    if (!import_file) {
        snprintf(log_message, sizeof(log_message), 
                "Failed to open import file: %s", import_path);
        log_error(log_message);
        return DATA_MANAGER_ERROR_FILE;
    }
    
    FILE* dest = fopen(dest_path, "wb");
    if (!dest) {
        snprintf(log_message, sizeof(log_message), 
                "Failed to create target file: %s", dest_path);
        log_error(log_message);
        fclose(import_file);
        return DATA_MANAGER_ERROR_FILE;
    }
    
    // کپی محتوا
    char buffer[4096];
    size_t bytes;
    
    while ((bytes = fread(buffer, 1, sizeof(buffer), import_file)) > 0) {
        fwrite(buffer, 1, bytes, dest);
    }
    
    fclose(import_file);
    fclose(dest);
    
    snprintf(log_message, sizeof(log_message), 
            "CSV imported: %s -> %s", import_path, target_file);
    log_info(log_message);
    
    return DATA_MANAGER_SUCCESS;
}

int data_manager_restore_backup(const char* backup_name) {
    char backup_path[512];
    char target_path[512];
    char log_message[256];
    
    if (!backup_name) {
        log_error("Invalid backup name for data_manager_restore_backup");
        return DATA_MANAGER_ERROR_INVALID_PARAMETER;
    }
    
    // تشخیص نوع فایل پشتیبان و مقصد آن
    const char* files[] = {
        "property_counter.txt",
        "users.csv",
        "residential_sales.csv",
        "residential_rentals.csv",
        "commercial_sales.csv",
        "commercial_rentals.csv",
        "land_sales.csv",
        "land_rentals.csv"
    };
    
    const char* target = NULL;
    for (int i = 0; i < 8; i++) {
        if (strstr(backup_name, files[i]) != NULL) {
            target = files[i];
            break;
        }
    }
    
    if (!target) {
        snprintf(log_message, sizeof(log_message), 
                "Unknown backup type: %s", backup_name);
        log_error(log_message);
        return DATA_MANAGER_ERROR_INVALID_PARAMETER;
    }
    
    // مسیر کامل فایل پشتیبان
    snprintf(backup_path, sizeof(backup_path), "%sdata/backups/%s", base_path, backup_name);
    
    // مسیر کامل فایل هدف
    snprintf(target_path, sizeof(target_path), "%sdata/%s", base_path, target);
    
    // بازیابی پشتیبان
    FILE* backup = fopen(backup_path, "rb");
    if (!backup) {
        snprintf(log_message, sizeof(log_message), 
                "Failed to open backup file: %s", backup_path);
        log_error(log_message);
        return DATA_MANAGER_ERROR_FILE;
    }
    
    FILE* dest = fopen(target_path, "wb");
    if (!dest) {
        snprintf(log_message, sizeof(log_message), 
                "Failed to create target file: %s", target_path);
        log_error(log_message);
        fclose(backup);
        return DATA_MANAGER_ERROR_FILE;
    }
    
    // کپی محتوا
    char buffer[4096];
    size_t bytes;
    
    while ((bytes = fread(buffer, 1, sizeof(buffer), backup)) > 0) {
        fwrite(buffer, 1, bytes, dest);
    }
    
    fclose(backup);
    fclose(dest);
    
    snprintf(log_message, sizeof(log_message), 
            "Backup restored: %s -> %s", backup_name, target);
    property_log("INFO", log_message);
    
    return DATA_MANAGER_SUCCESS;
}

char** data_manager_list_backups(int* count) {
    char backup_dir[512];
    char log_message[256];
    
    if (!count) {
        property_log("ERROR", "Invalid parameter for data_manager_list_backups");
        return NULL;
    }
    
    *count = 0;
    
    // مسیر پوشه پشتیبان
    snprintf(backup_dir, sizeof(backup_dir), "%sdata/backups", data_base_path);
    
    // باز کردن پوشه
#ifdef _WIN32
    struct _finddata_t file_info;
    intptr_t handle;
    char search_pattern[512];
    
    snprintf(search_pattern, sizeof(search_pattern), "%s/*.*", backup_dir);
    
    handle = _findfirst(search_pattern, &file_info);
    if (handle == -1) {
        snprintf(log_message, sizeof(log_message), 
                "Failed to open backup directory: %s", backup_dir);
        property_log("ERROR", log_message);
        return NULL;
    }
    
    // شمارش تعداد فایل‌ها
    int file_count = 0;
    do {
        if (!(file_info.attrib & _A_SUBDIR)) { // فقط فایل‌ها، نه پوشه‌ها
            file_count++;
        }
    } while (_findnext(handle, &file_info) == 0);
    
    _findclose(handle);
    
    if (file_count == 0) {
        return NULL;
    }
    
    // تخصیص حافظه برای آرایه نتایج
    char** backup_list = (char**)malloc(file_count * sizeof(char*));
    if (!backup_list) {
        property_log("ERROR", "Memory allocation error in data_manager_list_backups");
        return NULL;
    }
    
    // مرور مجدد فایل‌ها و ذخیره نام آن‌ها
    handle = _findfirst(search_pattern, &file_info);
    int index = 0;
    
    do {
        if (!(file_info.attrib & _A_SUBDIR)) { // فقط فایل‌ها، نه پوشه‌ها
            backup_list[index] = (char*)malloc(strlen(file_info.name) + 1);
            if (backup_list[index]) {
                strcpy(backup_list[index], file_info.name);
                index++;
            }
        }
    } while (_findnext(handle, &file_info) == 0);
    
    _findclose(handle);
    
    *count = index;
#else
    DIR* dir = opendir(backup_dir);
    if (!dir) {
        snprintf(log_message, sizeof(log_message), 
                "Failed to open backup directory: %s", backup_dir);
        property_log("ERROR", log_message);
        return NULL;
    }
    
    // شمارش تعداد فایل‌ها
    int file_count = 0;
    struct dirent* entry;
    
    while ((entry = readdir(dir)) != NULL) {
        if (entry->d_type == DT_REG) { // فقط فایل‌های معمولی
            file_count++;
        }
    }
    
    rewinddir(dir);
    
    if (file_count == 0) {
        closedir(dir);
        return NULL;
    }
    
    // تخصیص حافظه برای آرایه نتایج
    char** backup_list = (char**)malloc(file_count * sizeof(char*));
    if (!backup_list) {
        property_log("ERROR", "Memory allocation error in data_manager_list_backups");
        closedir(dir);
        return NULL;
    }
    
    // مرور مجدد فایل‌ها و ذخیره نام آن‌ها
    int index = 0;
    
    while ((entry = readdir(dir)) != NULL) {
        if (entry->d_type == DT_REG) { // فقط فایل‌های معمولی
            backup_list[index] = (char*)malloc(strlen(entry->d_name) + 1);
            if (backup_list[index]) {
                strcpy(backup_list[index], entry->d_name);
                index++;
            }
        }
    }
    
    closedir(dir);
    
    *count = index;
#endif
    
    return backup_list;
}

void data_manager_free_backup_list(char** backup_list, int count) {
    if (!backup_list) {
        return;
    }
    
    for (int i = 0; i < count; i++) {
        if (backup_list[i]) {
            free(backup_list[i]);
        }
    }
    
    free(backup_list);
}

/**
 * @brief شروع یک تراکنش جدید
 * @return وضعیت عملیات
 */
DataManagerStatus data_manager_begin_transaction(void) {
    if (transaction_active) {
        log_warning("یک تراکنش از قبل فعال است");
        return DATA_MANAGER_TRANSACTION_ALREADY_ACTIVE;
    }
    
    if (transactions == NULL) {
        // اختصاص حافظه اولیه برای تراکنش‌ها
        transaction_capacity = 10;
        transactions = (DataTransaction*)malloc(transaction_capacity * sizeof(DataTransaction));
        if (transactions == NULL) {
            log_error("خطا در تخصیص حافظه برای تراکنش‌ها");
            return DATA_MANAGER_MEMORY_ERROR;
        }
    }
    
    transaction_count = 0;
    transaction_active = true;
    log_info("تراکنش جدید آغاز شد");
    return DATA_MANAGER_SUCCESS;
}

/**
 * @brief افزودن یک تراکنش جدید
 * @param transaction_type نوع تراکنش
 * @param file_path مسیر فایل
 * @param data داده‌های مربوط به تراکنش
 * @return وضعیت عملیات
 */
DataManagerStatus data_manager_add_transaction(TransactionType transaction_type, const char* file_path, const char* data) {
    if (!transaction_active) {
        log_error("هیچ تراکنش فعالی وجود ندارد");
        return DATA_MANAGER_NO_ACTIVE_TRANSACTION;
    }
    
    if (file_path == NULL || data == NULL) {
        log_error("مسیر فایل یا داده نامعتبر است");
        return DATA_MANAGER_INVALID_PARAMS;
    }
    
    // بررسی نیاز به افزایش فضای تراکنش‌ها
    if (transaction_count >= transaction_capacity) {
        transaction_capacity *= 2;
        DataTransaction* new_transactions = (DataTransaction*)realloc(transactions, 
                                                                   transaction_capacity * sizeof(DataTransaction));
        if (new_transactions == NULL) {
            log_error("خطا در افزایش حافظه برای تراکنش‌ها");
            return DATA_MANAGER_MEMORY_ERROR;
        }
        transactions = new_transactions;
    }
    
    // اضافه کردن تراکنش جدید
    transactions[transaction_count].type = transaction_type;
    strncpy(transactions[transaction_count].file_path, file_path, sizeof(transactions[transaction_count].file_path) - 1);
    transactions[transaction_count].file_path[sizeof(transactions[transaction_count].file_path) - 1] = '\0';
    
    // اختصاص حافظه برای داده
    transactions[transaction_count].data = strdup(data);
    if (transactions[transaction_count].data == NULL) {
        log_error("خطا در تخصیص حافظه برای داده تراکنش");
        return DATA_MANAGER_MEMORY_ERROR;
    }
    
    transaction_count++;
    log_debug("تراکنش جدید اضافه شد: نوع=%d، فایل=%s", transaction_type, file_path);
    return DATA_MANAGER_SUCCESS;
}

/**
 * @brief تأیید و اعمال تراکنش‌های فعال
 * @return وضعیت عملیات
 */
DataManagerStatus data_manager_commit_transaction(void) {
    if (!transaction_active) {
        log_error("هیچ تراکنش فعالی برای تأیید وجود ندارد");
        return DATA_MANAGER_NO_ACTIVE_TRANSACTION;
    }
    
    DataManagerStatus status = DATA_MANAGER_SUCCESS;
    
    // اعمال تراکنش‌های ثبت شده
    for (int i = 0; i < transaction_count; i++) {
        char full_path[512];
        if (get_full_path(transactions[i].file_path, full_path, sizeof(full_path)) != DATA_MANAGER_SUCCESS) {
            log_error("خطا در محاسبه مسیر کامل برای فایل: %s", transactions[i].file_path);
            status = DATA_MANAGER_INVALID_PATH;
            continue;
        }
        
        // ایجاد دایرکتوری‌های مورد نیاز
        if (create_directories_for_file(full_path) != DATA_MANAGER_SUCCESS) {
            status = DATA_MANAGER_IO_ERROR;
            continue;
        }
        
        FILE* file;
        if (transactions[i].type == TRANSACTION_APPEND) {
            // افزودن به انتهای فایل
            file = fopen(full_path, "a");
            if (file == NULL) {
                log_error("خطا در باز کردن فایل برای افزودن: %s", full_path);
                status = DATA_MANAGER_IO_ERROR;
                continue;
            }
            
            fprintf(file, "%s\n", transactions[i].data);
            fclose(file);
            log_debug("داده به فایل اضافه شد: %s", full_path);
        } else if (transactions[i].type == TRANSACTION_UPDATE) {
            // بروزرسانی فایل با جایگزینی محتوا
            // ایجاد نام فایل موقت
            char temp_path[520];
            sprintf(temp_path, "%s.tmp", full_path);
            
            // خواندن فایل اصلی و ایجاد فایل جدید
            FILE* original_file = fopen(full_path, "r");
            if (original_file == NULL) {
                log_error("خطا در باز کردن فایل اصلی برای بروزرسانی: %s", full_path);
                status = DATA_MANAGER_IO_ERROR;
                continue;
            }
            
            file = fopen(temp_path, "w");
            if (file == NULL) {
                log_error("خطا در ایجاد فایل موقت: %s", temp_path);
                fclose(original_file);
                status = DATA_MANAGER_IO_ERROR;
                continue;
            }
            
            // کپی خط‌های فایل و جایگزینی با داده جدید در صورت نیاز
            char line[1024];
            char id_to_update[64];
            bool updated = false;
            
            // استخراج ID مورد نظر برای بروزرسانی
            sscanf(transactions[i].data, "%[^,]", id_to_update);
            
            // کپی سربرگ CSV
            if (fgets(line, sizeof(line), original_file) != NULL) {
                fprintf(file, "%s", line);
            }
            
            // بررسی و بروزرسانی خط‌های دیگر
            while (fgets(line, sizeof(line), original_file) != NULL) {
                char current_id[64];
                sscanf(line, "%[^,]", current_id);
                
                if (strcmp(current_id, id_to_update) == 0) {
                    // جایگزینی این خط با داده جدید
                    fprintf(file, "%s\n", transactions[i].data);
                    updated = true;
                } else {
                    // کپی خط اصلی
                    fprintf(file, "%s", line);
                }
            }
            
            // اگر رکورد یافت نشد، آن را اضافه کنید
            if (!updated) {
                fprintf(file, "%s\n", transactions[i].data);
            }
            
            // بستن فایل‌ها
            fclose(original_file);
            fclose(file);
            
            // جایگزینی فایل اصلی با فایل موقت
            remove(full_path);
            rename(temp_path, full_path);
            log_debug("فایل با موفقیت بروزرسانی شد: %s", full_path);
        } else if (transactions[i].type == TRANSACTION_DELETE) {
            // حذف منطقی یا فیزیکی یک رکورد
            // (فعلاً فقط حذف منطقی پیاده‌سازی شده است)
            // در اینجا عملیات مشابه بروزرسانی است
            char temp_path[520];
            sprintf(temp_path, "%s.tmp", full_path);
            
            FILE* original_file = fopen(full_path, "r");
            if (original_file == NULL) {
                log_error("خطا در باز کردن فایل اصلی برای حذف: %s", full_path);
                status = DATA_MANAGER_IO_ERROR;
                continue;
            }
            
            file = fopen(temp_path, "w");
            if (file == NULL) {
                log_error("خطا در ایجاد فایل موقت: %s", temp_path);
                fclose(original_file);
                status = DATA_MANAGER_IO_ERROR;
                continue;
            }
            
            // کپی خط‌های فایل و جایگزینی با داده جدید در صورت نیاز
            char line[1024];
            char id_to_delete[64];
            bool deleted = false;
            
            // استخراج ID مورد نظر برای حذف
            sscanf(transactions[i].data, "%[^,]", id_to_delete);
            
            // کپی سربرگ CSV
            if (fgets(line, sizeof(line), original_file) != NULL) {
                fprintf(file, "%s", line);
            }
            
            // بررسی و بروزرسانی خط‌های دیگر
            while (fgets(line, sizeof(line), original_file) != NULL) {
                char current_id[64];
                sscanf(line, "%[^,]", current_id);
                
                if (strcmp(current_id, id_to_delete) == 0) {
                    // جایگزینی این خط با داده بروزرسانی شده (غیرفعال)
                    fprintf(file, "%s\n", transactions[i].data);
                    deleted = true;
                } else {
                    // کپی خط اصلی
                    fprintf(file, "%s", line);
                }
            }
            
            // بستن فایل‌ها
            fclose(original_file);
            fclose(file);
            
            if (deleted) {
                // جایگزینی فایل اصلی با فایل موقت
                remove(full_path);
                rename(temp_path, full_path);
                log_debug("رکورد با موفقیت حذف شد: %s در فایل %s", id_to_delete, full_path);
            } else {
                remove(temp_path);
                log_warning("رکورد برای حذف یافت نشد: %s در فایل %s", id_to_delete, full_path);
            }
        } else {
            log_error("نوع تراکنش نامعتبر است: %d", transactions[i].type);
            status = DATA_MANAGER_INVALID_PARAMS;
        }
    }
    
    // آزادسازی منابع تراکنش
    for (int i = 0; i < transaction_count; i++) {
        free(transactions[i].data);
    }
    transaction_count = 0;
    transaction_active = false;
    
    log_info("تراکنش با موفقیت تأیید شد");
    return status;
}

/**
 * @brief لغو تراکنش‌های فعال
 * @return وضعیت عملیات
 */
DataManagerStatus data_manager_rollback_transaction(void) {
    if (!transaction_active) {
        log_error("هیچ تراکنش فعالی برای لغو وجود ندارد");
        return DATA_MANAGER_NO_ACTIVE_TRANSACTION;
    }
    
    // آزادسازی منابع تراکنش
    for (int i = 0; i < transaction_count; i++) {
        free(transactions[i].data);
    }
    transaction_count = 0;
    transaction_active = false;
    
    log_info("تراکنش لغو شد");
    return DATA_MANAGER_SUCCESS;
}

/**
 * @brief آزادسازی منابع مدیریت داده
 */
void data_manager_cleanup(void) {
    // لغو هر تراکنش فعال
    if (transaction_active) {
        data_manager_rollback_transaction();
    }
    
    // آزادسازی حافظه تراکنش‌ها
    if (transactions != NULL) {
        free(transactions);
        transactions = NULL;
    }
    transaction_capacity = 0;
    
    log_info("منابع مدیریت داده آزاد شدند");
} 