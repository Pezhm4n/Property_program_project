/**
 * @file utils.c
 * @brief پیاده‌سازی توابع کمکی و عمومی مورد نیاز در سیستم مدیریت املاک
 */

#include "../include/utils.h"
#include "../include/property_lib.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <ctype.h>

#ifdef _WIN32
#include <windows.h>
#else
#include <unistd.h>
#include <sys/stat.h>
#endif

void property_log(const char* level, const char* message) {
    if (!level || !message) {
        return;
    }
    
    time_t now = time(NULL);
    struct tm* tm_info = localtime(&now);
    char timestamp[30];
    char log_path[512];
    char full_log_line[1024];
    
    // ایجاد تایم‌استمپ
    strftime(timestamp, sizeof(timestamp), "%Y-%m-%d %H:%M:%S", tm_info);
    
    // ساخت خط کامل لاگ
    snprintf(full_log_line, sizeof(full_log_line), "[%s] [%s] %s\n", 
             timestamp, level, message);
    
    // مسیر فایل لاگ
    time_t day = now / 86400 * 86400; // گرد کردن به ابتدای روز
    struct tm* day_tm = localtime(&day);
    char day_str[20];
    strftime(day_str, sizeof(day_str), "%Y-%m-%d", day_tm);
    
    // استفاده از تابع data_manager برای دریافت مسیر پایه
    extern const char* data_manager_get_base_path();
    const char* base_path = data_manager_get_base_path();
    
    snprintf(log_path, sizeof(log_path), "%sdata/logs/property_log_%s.txt", 
             base_path ? base_path : "./", day_str);
    
    // باز کردن فایل لاگ
    FILE* log_file = fopen(log_path, "a");
    if (!log_file) {
        // در صورت خطا، سعی در ایجاد مسیر
        char dir_path[512];
        snprintf(dir_path, sizeof(dir_path), "%sdata/logs", base_path ? base_path : "./");
        
#ifdef _WIN32
        CreateDirectory(dir_path, NULL);
#else
        mkdir(dir_path, 0755);
#endif
        
        log_file = fopen(log_path, "a");
        if (!log_file) {
            // اگر همچنان نتوانستیم باز کنیم، به خروجی استاندارد میفرستیم
            fprintf(stderr, "%s", full_log_line);
            return;
        }
    }
    
    // نوشتن در فایل
    fprintf(log_file, "%s", full_log_line);
    fclose(log_file);
    
    // نمایش خطاها و هشدارها در خروجی استاندارد
    if (strcmp(level, "ERROR") == 0 || strcmp(level, "WARNING") == 0) {
        fprintf(stderr, "%s", full_log_line);
    }
}

int generate_property_id() {
    char counter_path[512];
    int property_id = 0;
    
    // استفاده از تابع data_manager برای دریافت مسیر پایه
    extern const char* data_manager_get_base_path();
    const char* base_path = data_manager_get_base_path();
    
    snprintf(counter_path, sizeof(counter_path), "%sdata/property_counter.txt", 
             base_path ? base_path : "./");
    
    // خواندن شناسه فعلی
    FILE* counter_file = fopen(counter_path, "r");
    if (counter_file) {
        if (fscanf(counter_file, "%d", &property_id) != 1) {
            property_id = 1000; // مقدار پیش‌فرض
        }
        fclose(counter_file);
    } else {
        property_log("WARNING", "Could not open property counter file. Using default value.");
        property_id = 1000; // مقدار پیش‌فرض
    }
    
    // افزایش شناسه
    property_id++;
    
    // ذخیره شناسه جدید
    counter_file = fopen(counter_path, "w");
    if (counter_file) {
        fprintf(counter_file, "%d", property_id);
        fclose(counter_file);
    } else {
        property_log("ERROR", "Could not update property counter file.");
    }
    
    return property_id;
}

char* string_duplicate(const char* str) {
    if (!str) {
        return NULL;
    }
    
    char* new_str = (char*)malloc(strlen(str) + 1);
    if (!new_str) {
        property_log("ERROR", "Memory allocation failed in string_duplicate");
        return NULL;
    }
    
    strcpy(new_str, str);
    return new_str;
}

void free_string(char* str) {
    if (str) {
        free(str);
    }
}

int validate_required_string(const char* str, const char* field_name) {
    if (!str || strlen(str) == 0) {
        char error_message[100];
        snprintf(error_message, sizeof(error_message), 
                "Required field '%s' is missing or empty", field_name);
        property_log("ERROR", error_message);
        return 0; // نامعتبر
    }
    return 1; // معتبر
}

int validate_date_format(const char* date) {
    if (!date || strlen(date) != 10) {
        return 0; // نامعتبر
    }
    
    // بررسی فرمت YYYY-MM-DD
    if (date[4] != '-' || date[7] != '-') {
        return 0;
    }
    
    // بررسی ارقام بودن سایر کاراکترها
    for (int i = 0; i < 10; i++) {
        if (i != 4 && i != 7 && !isdigit(date[i])) {
            return 0;
        }
    }
    
    // استخراج سال، ماه و روز
    int year, month, day;
    sscanf(date, "%d-%d-%d", &year, &month, &day);
    
    // بررسی محدوده معتبر
    if (year < 1900 || year > 2100) return 0;
    if (month < 1 || month > 12) return 0;
    
    // بررسی روز بر اساس ماه
    int days_in_month[] = {0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31};
    
    // تنظیم برای سال کبیسه
    if ((year % 4 == 0 && year % 100 != 0) || (year % 400 == 0)) {
        days_in_month[2] = 29;
    }
    
    if (day < 1 || day > days_in_month[month]) {
        return 0;
    }
    
    return 1; // معتبر
}

int validate_positive_number(double value, const char* field_name) {
    if (value < 0) {
        char error_message[100];
        snprintf(error_message, sizeof(error_message), 
                "Field '%s' must be a positive number", field_name);
        property_log("ERROR", error_message);
        return 0; // نامعتبر
    }
    return 1; // معتبر
}

int validate_phone_number(const char* phone) {
    if (!phone) {
        return 0;
    }
    
    size_t len = strlen(phone);
    if (len < 8 || len > 15) {
        return 0;
    }
    
    // شماره تلفن باید فقط شامل اعداد، + (در ابتدا) و - باشد
    for (size_t i = 0; i < len; i++) {
        if (i == 0 && phone[i] == '+') {
            continue;
        }
        
        if (!isdigit(phone[i]) && phone[i] != '-') {
            return 0;
        }
    }
    
    return 1;
}

int validate_email(const char* email) {
    if (!email) {
        return 0;
    }
    
    // بررسی وجود @ در ایمیل
    const char* at_sign = strchr(email, '@');
    if (!at_sign) {
        return 0;
    }
    
    // بررسی وجود حداقل یک کاراکتر قبل از @
    if (at_sign == email) {
        return 0;
    }
    
    // بررسی وجود حداقل یک کاراکتر بعد از @
    if (at_sign[1] == '\0') {
        return 0;
    }
    
    // بررسی وجود . بعد از @
    const char* dot = strchr(at_sign, '.');
    if (!dot || dot == at_sign + 1 || dot[1] == '\0') {
        return 0;
    }
    
    return 1;
}

int parse_csv_line(const char* line, char** fields, int max_fields) {
    if (!line || !fields || max_fields <= 0) {
        return 0;
    }
    
    int field_count = 0;
    const char* p = line;
    int in_quotes = 0;
    const char* start = p;
    
    while (*p && field_count < max_fields) {
        if (*p == '"') {
            in_quotes = !in_quotes;
        } else if (*p == ',' && !in_quotes) {
            // به پایان یک فیلد رسیدیم
            int len = p - start;
            char* field = (char*)malloc(len + 1);
            
            if (!field) {
                // آزادسازی فیلدهای قبلی در صورت خطا
                for (int i = 0; i < field_count; i++) {
                    free(fields[i]);
                    fields[i] = NULL;
                }
                return 0;
            }
            
            // کپی محتوای فیلد
            strncpy(field, start, len);
            field[len] = '\0';
            
            // حذف نقل قول‌ها در صورت وجود
            if (len >= 2 && field[0] == '"' && field[len-1] == '"') {
                memmove(field, field + 1, len - 2);
                field[len - 2] = '\0';
            }
            
            fields[field_count++] = field;
            start = p + 1;
        }
        p++;
    }
    
    // فیلد آخر
    if (*start && field_count < max_fields) {
        int len = strlen(start);
        
        // حذف کاراکتر نیولاین در انتها اگر وجود دارد
        if (len > 0 && (start[len-1] == '\n' || start[len-1] == '\r')) {
            len--;
            if (len > 0 && (start[len-1] == '\r')) {
                len--;
            }
        }
        
        char* field = (char*)malloc(len + 1);
        
        if (!field) {
            // آزادسازی فیلدهای قبلی در صورت خطا
            for (int i = 0; i < field_count; i++) {
                free(fields[i]);
                fields[i] = NULL;
            }
            return 0;
        }
        
        // کپی محتوای فیلد
        strncpy(field, start, len);
        field[len] = '\0';
        
        // حذف نقل قول‌ها در صورت وجود
        if (len >= 2 && field[0] == '"' && field[len-1] == '"') {
            memmove(field, field + 1, len - 2);
            field[len - 2] = '\0';
        }
        
        fields[field_count++] = field;
    }
    
    return field_count;
}

void free_csv_fields(char** fields, int field_count) {
    if (!fields) {
        return;
    }
    
    for (int i = 0; i < field_count; i++) {
        if (fields[i]) {
            free(fields[i]);
            fields[i] = NULL;
        }
    }
}

char* create_csv_line(const char** fields, int field_count) {
    if (!fields || field_count <= 0) {
        return NULL;
    }
    
    // محاسبه طول مورد نیاز برای رشته نهایی
    size_t total_length = 0;
    for (int i = 0; i < field_count; i++) {
        if (fields[i]) {
            // بررسی نیاز به قرار دادن فیلد در نقل قول
            int needs_quotes = 0;
            const char* p = fields[i];
            while (*p) {
                if (*p == ',' || *p == '"' || *p == '\n' || *p == '\r') {
                    needs_quotes = 1;
                    break;
                }
                p++;
            }
            
            total_length += strlen(fields[i]);
            if (needs_quotes) {
                total_length += 2; // برای نقل‌قول‌ها
                
                // شمارش کاراکترهای " که باید escape شوند
                p = fields[i];
                while (*p) {
                    if (*p == '"') {
                        total_length++; // برای هر " یک " اضافی برای escape
                    }
                    p++;
                }
            }
        }
        
        total_length += 1; // برای کاما یا نیولاین
    }
    
    // تخصیص حافظه برای رشته نهایی
    char* csv_line = (char*)malloc(total_length + 1);
    if (!csv_line) {
        property_log("ERROR", "Memory allocation failed in create_csv_line");
        return NULL;
    }
    
    // ساخت رشته CSV
    char* p = csv_line;
    for (int i = 0; i < field_count; i++) {
        if (fields[i]) {
            // بررسی نیاز به قرار دادن فیلد در نقل قول
            int needs_quotes = 0;
            const char* c = fields[i];
            while (*c) {
                if (*c == ',' || *c == '"' || *c == '\n' || *c == '\r') {
                    needs_quotes = 1;
                    break;
                }
                c++;
            }
            
            if (needs_quotes) {
                *p++ = '"';
                
                // کپی محتوا با escape کردن نقل‌قول‌ها
                c = fields[i];
                while (*c) {
                    if (*c == '"') {
                        *p++ = '"'; // یک " اضافی برای escape
                    }
                    *p++ = *c++;
                }
                
                *p++ = '"';
            } else {
                strcpy(p, fields[i]);
                p += strlen(fields[i]);
            }
        }
        
        // کاما بین فیلدها
        if (i < field_count - 1) {
            *p++ = ',';
        }
    }
    
    *p = '\0';
    
    return csv_line;
}

int compare_dates(const char* date1, const char* date2) {
    // تبدیل تاریخ‌ها به ساختار زمان برای مقایسه
    struct tm tm1 = {0}, tm2 = {0};
    int year, month, day;
    
    if (sscanf(date1, "%d-%d-%d", &year, &month, &day) == 3) {
        tm1.tm_year = year - 1900;
        tm1.tm_mon = month - 1;
        tm1.tm_mday = day;
    } else {
        return 0; // خطا در تبدیل تاریخ اول
    }
    
    if (sscanf(date2, "%d-%d-%d", &year, &month, &day) == 3) {
        tm2.tm_year = year - 1900;
        tm2.tm_mon = month - 1;
        tm2.tm_mday = day;
    } else {
        return 0; // خطا در تبدیل تاریخ دوم
    }
    
    // مقایسه تاریخ‌ها
    time_t time1 = mktime(&tm1);
    time_t time2 = mktime(&tm2);
    
    if (time1 < time2) return -1;
    if (time1 > time2) return 1;
    return 0;
}

char* get_current_date() {
    time_t now = time(NULL);
    struct tm* tm_info = localtime(&now);
    
    char* date = (char*)malloc(11);
    if (!date) {
        property_log("ERROR", "Memory allocation failed in get_current_date");
        return NULL;
    }
    
    sprintf(date, "%04d-%02d-%02d", 
            tm_info->tm_year + 1900, tm_info->tm_mon + 1, tm_info->tm_mday);
    
    return date;
}

int case_insensitive_compare(const char* str1, const char* str2) {
    if (!str1 || !str2) {
        return str1 == str2 ? 0 : (str1 ? 1 : -1);
    }
    
#ifdef _WIN32
    return _stricmp(str1, str2);
#else
    return strcasecmp(str1, str2);
#endif
}

int partial_string_match(const char* str, const char* pattern) {
    if (!str || !pattern) {
        return 0;
    }
    
    // تبدیل هر دو رشته به حروف کوچک برای مقایسه بدون حساسیت به بزرگی و کوچکی
    size_t str_len = strlen(str);
    size_t pattern_len = strlen(pattern);
    
    char* str_lower = (char*)malloc(str_len + 1);
    char* pattern_lower = (char*)malloc(pattern_len + 1);
    
    if (!str_lower || !pattern_lower) {
        if (str_lower) free(str_lower);
        if (pattern_lower) free(pattern_lower);
        property_log("ERROR", "Memory allocation failed in partial_string_match");
        return 0;
    }
    
    for (size_t i = 0; i < str_len; i++) {
        str_lower[i] = tolower(str[i]);
    }
    str_lower[str_len] = '\0';
    
    for (size_t i = 0; i < pattern_len; i++) {
        pattern_lower[i] = tolower(pattern[i]);
    }
    pattern_lower[pattern_len] = '\0';
    
    // بررسی وجود الگو در رشته
    int result = strstr(str_lower, pattern_lower) != NULL;
    
    free(str_lower);
    free(pattern_lower);
    
    return result;
}

int export_to_json(const char* csv_path, const char* json_path, 
                   const char** headers, int header_count) {
    if (!csv_path || !json_path || !headers || header_count <= 0) {
        property_log("ERROR", "Invalid parameters for export_to_json");
        return PROPERTY_ERROR_INVALID_PARAMETER;
    }
    
    FILE* csv_file = fopen(csv_path, "r");
    if (!csv_file) {
        char error_message[256];
        snprintf(error_message, sizeof(error_message), 
                "Failed to open CSV file for JSON export: %s", csv_path);
        property_log("ERROR", error_message);
        return PROPERTY_ERROR_FILE_OPEN;
    }
    
    FILE* json_file = fopen(json_path, "w");
    if (!json_file) {
        char error_message[256];
        snprintf(error_message, sizeof(error_message), 
                "Failed to create JSON file: %s", json_path);
        property_log("ERROR", error_message);
        fclose(csv_file);
        return PROPERTY_ERROR_FILE_OPEN;
    }
    
    char line[2048];
    char* fields[50];
    int line_count = 0;
    
    // آغاز آرایه JSON
    fprintf(json_file, "[\n");
    
    // خواندن خط به خط فایل CSV
    while (fgets(line, sizeof(line), csv_file)) {
        // تجزیه خط CSV
        int field_count = parse_csv_line(line, fields, 50);
        
        if (field_count < header_count) {
            // تعداد فیلدها کمتر از هدرها است، نامعتبر
            free_csv_fields(fields, field_count);
            continue;
        }
        
        // اضافه کردن کاما بین آیتم‌ها بجز اولین آیتم
        if (line_count > 0) {
            fprintf(json_file, ",\n");
        }
        
        // آغاز شیء JSON
        fprintf(json_file, "  {\n");
        
        // نوشتن فیلدها
        for (int i = 0; i < header_count; i++) {
            // escape کردن کاراکترهای خاص در مقادیر
            char* escaped_value = NULL;
            size_t value_len = strlen(fields[i]);
            size_t escaped_len = 0;
            
            // محاسبه طول مورد نیاز برای رشته escape شده
            for (size_t j = 0; j < value_len; j++) {
                if (fields[i][j] == '"' || fields[i][j] == '\\' || fields[i][j] == '\n' || 
                    fields[i][j] == '\r' || fields[i][j] == '\t') {
                    escaped_len += 2;
                } else {
                    escaped_len++;
                }
            }
            
            escaped_value = (char*)malloc(escaped_len + 1);
            if (!escaped_value) {
                property_log("ERROR", "Memory allocation failed in export_to_json");
                free_csv_fields(fields, field_count);
                fclose(csv_file);
                fclose(json_file);
                return PROPERTY_ERROR_MEMORY;
            }
            
            // ایجاد رشته escape شده
            size_t k = 0;
            for (size_t j = 0; j < value_len; j++) {
                if (fields[i][j] == '"' || fields[i][j] == '\\') {
                    escaped_value[k++] = '\\';
                    escaped_value[k++] = fields[i][j];
                } else if (fields[i][j] == '\n') {
                    escaped_value[k++] = '\\';
                    escaped_value[k++] = 'n';
                } else if (fields[i][j] == '\r') {
                    escaped_value[k++] = '\\';
                    escaped_value[k++] = 'r';
                } else if (fields[i][j] == '\t') {
                    escaped_value[k++] = '\\';
                    escaped_value[k++] = 't';
                } else {
                    escaped_value[k++] = fields[i][j];
                }
            }
            escaped_value[k] = '\0';
            
            // نوشتن فیلد در فایل JSON
            fprintf(json_file, "    \"%s\": \"%s\"%s\n", 
                    headers[i], escaped_value, (i < header_count - 1) ? "," : "");
            
            free(escaped_value);
        }
        
        // پایان شیء JSON
        fprintf(json_file, "  }");
        
        // آزادسازی فیلدهای تجزیه شده
        free_csv_fields(fields, field_count);
        
        line_count++;
    }
    
    // پایان آرایه JSON
    fprintf(json_file, "\n]\n");
    
    fclose(csv_file);
    fclose(json_file);
    
    char log_message[256];
    snprintf(log_message, sizeof(log_message), 
            "Exported %d records from CSV to JSON: %s -> %s", 
            line_count, csv_path, json_path);
    property_log("INFO", log_message);
    
    return PROPERTY_SUCCESS;
}

char* utils_generate_unique_id() {
    time_t current_time = time(NULL);
    char* id = (char*)malloc(21 * sizeof(char)); // 20 کاراکتر + \0
    if (id == NULL) {
        return NULL;
    }
    
    struct tm* time_info = localtime(&current_time);
    long random_part = rand() % 10000;
    
    sprintf(id, "%04d%02d%02d%02d%02d%02d%04ld", 
            time_info->tm_year + 1900,
            time_info->tm_mon + 1, 
            time_info->tm_mday,
            time_info->tm_hour, 
            time_info->tm_min, 
            time_info->tm_sec,
            random_part);
            
    return id;
}

void utils_format_date(time_t time_value, char* buffer) {
    struct tm* time_info = localtime(&time_value);
    sprintf(buffer, "%04d-%02d-%02d", 
            time_info->tm_year + 1900,
            time_info->tm_mon + 1, 
            time_info->tm_mday);
}

time_t utils_parse_date(const char* date_string) {
    if (!utils_validate_date(date_string)) {
        return (time_t)-1;
    }
    
    struct tm time_info = {0};
    int year, month, day;
    
    if (sscanf(date_string, "%d-%d-%d", &year, &month, &day) != 3) {
        return (time_t)-1;
    }
    
    time_info.tm_year = year - 1900;
    time_info.tm_mon = month - 1;
    time_info.tm_mday = day;
    
    return mktime(&time_info);
}

bool utils_validate_date(const char* date_string) {
    if (date_string == NULL) {
        return false;
    }
    
    int year, month, day;
    if (sscanf(date_string, "%d-%d-%d", &year, &month, &day) != 3) {
        return false;
    }
    
    // بررسی محدوده مقادیر
    if (year < 1900 || year > 2100 || month < 1 || month > 12 || day < 1 || day > 31) {
        return false;
    }
    
    // بررسی روزهای ماه‌های مختلف
    int days_in_month[] = {0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31};
    
    // سال کبیسه
    if ((year % 4 == 0 && year % 100 != 0) || (year % 400 == 0)) {
        days_in_month[2] = 29;
    }
    
    return day <= days_in_month[month];
}

bool utils_validate_number_range(double value, double min_value, double max_value) {
    return value >= min_value && value <= max_value;
}

bool utils_validate_string_length(const char* str, size_t min_length, size_t max_length) {
    if (str == NULL) {
        return min_length == 0;
    }
    
    size_t length = strlen(str);
    return length >= min_length && length <= max_length;
}

char* utils_encrypt_string(const char* input) {
    if (input == NULL) {
        return NULL;
    }
    
    size_t len = strlen(input);
    char* result = (char*)malloc((len + 1) * sizeof(char));
    
    if (result == NULL) {
        return NULL;
    }
    
    // یک رمزنگاری ساده با تغییر کد اسکی هر کاراکتر
    for (size_t i = 0; i < len; i++) {
        result[i] = input[i] + 3; // شیفت سزار با کلید 3
    }
    
    result[len] = '\0';
    return result;
}

void utils_string_to_lower(char* str) {
    if (str == NULL) {
        return;
    }
    
    for (size_t i = 0; str[i]; i++) {
        str[i] = tolower((unsigned char)str[i]);
    }
}

void utils_string_to_upper(char* str) {
    if (str == NULL) {
        return;
    }
    
    for (size_t i = 0; str[i]; i++) {
        str[i] = toupper((unsigned char)str[i]);
    }
}

char* utils_string_trim(char* str) {
    if (str == NULL) {
        return NULL;
    }
    
    if (str[0] == '\0') {
        return str;
    }
    
    // حذف فضاهای خالی از ابتدا
    char* start = str;
    while (isspace((unsigned char)*start)) {
        start++;
    }
    
    if (*start == '\0') { // همه کاراکترها فضای خالی بودند
        str[0] = '\0';
        return str;
    }
    
    // حذف فضاهای خالی از انتها
    char* end = str + strlen(str) - 1;
    while (end > start && isspace((unsigned char)*end)) {
        end--;
    }
    
    // افزودن کاراکتر پایان رشته
    *(end + 1) = '\0';
    
    // انتقال رشته به ابتدا اگر لازم باشد
    if (start != str) {
        memmove(str, start, (end - start + 2) * sizeof(char));
    }
    
    return str;
}

bool utils_string_match_pattern(const char* str, const char* pattern, bool case_sensitive) {
    if (str == NULL || pattern == NULL) {
        return false;
    }
    
    char* str_copy = utils_string_duplicate(str);
    char* pattern_copy = utils_string_duplicate(pattern);
    
    if (str_copy == NULL || pattern_copy == NULL) {
        free(str_copy);
        free(pattern_copy);
        return false;
    }
    
    if (!case_sensitive) {
        utils_string_to_lower(str_copy);
        utils_string_to_lower(pattern_copy);
    }
    
    bool result = strstr(str_copy, pattern_copy) != NULL;
    
    free(str_copy);
    free(pattern_copy);
    
    return result;
}

char* utils_format_number(long value, char* buffer, size_t buffer_size) {
    if (buffer == NULL || buffer_size == 0) {
        return NULL;
    }
    
    snprintf(buffer, buffer_size, "%ld", value);
    
    size_t len = strlen(buffer);
    if (len <= 3) {
        return buffer;
    }
    
    // فرمت‌بندی با جداکننده هزارگان
    char temp[256];
    size_t pos = 0;
    size_t remainder = len % 3;
    
    if (remainder == 0) {
        remainder = 3;
    }
    
    for (size_t i = 0; i < len; i++) {
        temp[pos++] = buffer[i];
        
        if (i == len - 1) {
            continue;
        }
        
        if ((i + 1) % 3 == remainder) {
            temp[pos++] = ',';
        }
    }
    
    temp[pos] = '\0';
    
    if (pos < buffer_size) {
        strcpy(buffer, temp);
    } else {
        strncpy(buffer, temp, buffer_size - 1);
        buffer[buffer_size - 1] = '\0';
    }
    
    return buffer;
}

char** utils_split_string(const char* str, char delim, int* count) {
    if (str == NULL || count == NULL) {
        return NULL;
    }
    
    // تعداد جداکننده‌ها را شمارش می‌کنیم
    int num_tokens = 1; // حداقل یک قطعه وجود دارد
    for (size_t i = 0; str[i]; i++) {
        if (str[i] == delim) {
            num_tokens++;
        }
    }
    
    // تخصیص حافظه برای آرایه نتیجه
    char** result = (char**)malloc(num_tokens * sizeof(char*));
    if (result == NULL) {
        *count = 0;
        return NULL;
    }
    
    // کپی کردن رشته اصلی برای تغییر
    char* str_copy = utils_string_duplicate(str);
    if (str_copy == NULL) {
        free(result);
        *count = 0;
        return NULL;
    }
    
    // جداسازی رشته
    int i = 0;
    char* token = strtok(str_copy, &delim);
    
    while (token != NULL && i < num_tokens) {
        result[i] = utils_string_duplicate(token);
        
        if (result[i] == NULL) {
            // در صورت خطا، حافظه آزاد می‌شود
            for (int j = 0; j < i; j++) {
                free(result[j]);
            }
            free(result);
            free(str_copy);
            *count = 0;
            return NULL;
        }
        
        i++;
        token = strtok(NULL, &delim);
    }
    
    *count = i;
    free(str_copy);
    
    return result;
}

void utils_free_string_array(char** array, int count) {
    if (array == NULL || count <= 0) {
        return;
    }
    
    for (int i = 0; i < count; i++) {
        free(array[i]);
    }
    
    free(array);
}

char* utils_string_duplicate(const char* str) {
    if (str == NULL) {
        return NULL;
    }
    
    size_t len = strlen(str);
    char* result = (char*)malloc((len + 1) * sizeof(char));
    
    if (result == NULL) {
        return NULL;
    }
    
    strcpy(result, str);
    return result;
}

bool utils_validate_email(const char* email) {
    if (email == NULL) {
        return false;
    }
    
    // بررسی حداقل طول و وجود @ و .
    size_t len = strlen(email);
    if (len < 5) { // a@b.c حداقل طول ممکن
        return false;
    }
    
    const char* at = strchr(email, '@');
    if (at == NULL || at == email) { // @ باید باشد و نباید در ابتدای رشته باشد
        return false;
    }
    
    const char* dot = strchr(at, '.');
    if (dot == NULL || dot == at + 1 || dot[1] == '\0') {
        // . باید بعد از @ باشد و نباید بلافاصله بعد از @ یا در انتهای رشته باشد
        return false;
    }
    
    // بررسی کاراکترهای مجاز
    for (size_t i = 0; i < len; i++) {
        char c = email[i];
        if (!isalnum(c) && c != '@' && c != '.' && c != '_' && c != '-') {
            return false;
        }
    }
    
    return true;
}

bool utils_validate_phone(const char* phone) {
    if (phone == NULL) {
        return false;
    }
    
    size_t len = strlen(phone);
    
    // بررسی طول (برای شماره‌های ایران معمولاً 11 رقم است)
    if (len != 11) {
        return false;
    }
    
    // بررسی شروع با 09
    if (phone[0] != '0' || phone[1] != '9') {
        return false;
    }
    
    // بررسی اینکه همه کاراکترها عدد باشند
    for (size_t i = 0; i < len; i++) {
        if (!isdigit(phone[i])) {
            return false;
        }
    }
    
    return true;
}

bool utils_validate_national_code(const char* national_code) {
    if (national_code == NULL) {
        return false;
    }
    
    size_t len = strlen(national_code);
    
    // کد ملی باید 10 رقم باشد
    if (len != 10) {
        return false;
    }
    
    // همه کاراکترها باید عدد باشند
    for (size_t i = 0; i < len; i++) {
        if (!isdigit(national_code[i])) {
            return false;
        }
    }
    
    // الگوریتم اعتبارسنجی کد ملی ایران
    int check = national_code[9] - '0';
    int sum = 0;
    
    for (int i = 0; i < 9; i++) {
        sum += (national_code[i] - '0') * (10 - i);
    }
    
    int remainder = sum % 11;
    int valid_check;
    
    if (remainder < 2) {
        valid_check = remainder;
    } else {
        valid_check = 11 - remainder;
    }
    
    return check == valid_check;
}

bool utils_validate_postal_code(const char* postal_code) {
    if (postal_code == NULL) {
        return false;
    }
    
    size_t len = strlen(postal_code);
    
    // کد پستی ایران 10 رقم است
    if (len != 10) {
        return false;
    }
    
    // همه کاراکترها باید عدد باشند
    for (size_t i = 0; i < len; i++) {
        if (!isdigit(postal_code[i])) {
            return false;
        }
    }
    
    return true;
} 