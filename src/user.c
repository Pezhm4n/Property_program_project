/**
 * @file user.c
 * @brief پیاده‌سازی توابع مرتبط با مدیریت کاربران
 */

#include "../include/user.h"
#include "../include/utils.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <ctype.h>

// فایل‌های مورد استفاده
static const char* USER_FILE = "data/users.csv";
static const char* FAILED_ATTEMPTS_FILE = "data/failed_attempts.csv";
static const char* LOCKED_ACCOUNTS_FILE = "data/locked_accounts.csv";

// مسیر ذخیره‌سازی داده‌ها
static char data_path[256] = "";

// تنظیم مسیر ذخیره‌سازی
void user_set_data_path(const char* path) {
    if (path && strlen(path) < 230) {
        strcpy(data_path, path);
        // اطمینان از وجود کاراکتر / در انتها
        if (data_path[strlen(data_path) - 1] != '/' && data_path[strlen(data_path) - 1] != '\\') {
            strcat(data_path, "/");
        }
    }
}

// ساخت مسیر کامل فایل
static void get_full_path(char* full_path, const char* file_name) {
    if (strlen(data_path) > 0) {
        strcpy(full_path, data_path);
        strcat(full_path, file_name);
    } else {
        strcpy(full_path, file_name);
    }
}

int user_register(const char* username, const char* password, const char* name, 
                 const char* lastName, const char* nationalCode, 
                 const char* phoneNumber, const char* email) {
    
    // بررسی اعتبار ورودی‌ها
    if (!user_is_valid_username(username)) {
        return PROPERTY_ERROR_VALIDATION;
    }
    
    if (user_is_duplicate_username(username)) {
        return PROPERTY_ERROR_DUPLICATE;
    }
    
    if (!user_is_strong_password(password)) {
        return PROPERTY_ERROR_VALIDATION;
    }
    
    if (!user_is_valid_national_code(nationalCode)) {
        return PROPERTY_ERROR_VALIDATION;
    }
    
    if (!user_is_valid_phone_number(phoneNumber)) {
        return PROPERTY_ERROR_VALIDATION;
    }
    
    if (!user_is_valid_email(email)) {
        return PROPERTY_ERROR_VALIDATION;
    }
    
    // ساخت مسیر کامل فایل
    char full_path[300];
    get_full_path(full_path, USER_FILE);
    
    // باز کردن فایل برای افزودن به انتها
    FILE* file = fopen(full_path, "a");
    if (!file) {
        // اگر فایل وجود ندارد، ایجاد کن و هدر را اضافه کن
        file = fopen(full_path, "w");
        if (!file) {
            return PROPERTY_ERROR_FILE;
        }
        fprintf(file, "username,password,name,lastName,nationalCode,phoneNumber,email,registrationDateTime,lastLoginTime\n");
    }
    
    // هش کردن رمز عبور (در یک پیاده‌سازی واقعی باید از الگوریتم قوی‌تری استفاده شود)
    char hashed_password[100];
    // در این مثال فرضی، رمز را به صورت خام ذخیره می‌کنیم، اما در پروژه واقعی باید هش شود
    strcpy(hashed_password, password);
    
    // ثبت زمان کنونی
    time_t now = time(NULL);
    struct tm* tm_info = localtime(&now);
    char registration_time[50];
    strftime(registration_time, sizeof(registration_time), "%Y-%m-%d %H:%M:%S", tm_info);
    
    // نوشتن رکورد کاربر جدید
    fprintf(file, "%s,%s,%s,%s,%s,%s,%s,%s,%ld\n",
            username, hashed_password, name, lastName, nationalCode, 
            phoneNumber, email, registration_time, now);
    
    fclose(file);
    
    return PROPERTY_SUCCESS;
}

int user_login(const char* username, const char* password, User* out_user) {
    if (!username || !password || !out_user) {
        return PROPERTY_ERROR_VALIDATION;
    }
    
    // بررسی وضعیت قفل حساب
    long remaining_seconds;
    if (user_is_account_locked(username, &remaining_seconds)) {
        return PROPERTY_ERROR_PERMISSION;
    }
    
    // ساخت مسیر کامل فایل
    char full_path[300];
    get_full_path(full_path, USER_FILE);
    
    FILE* file = fopen(full_path, "r");
    if (!file) {
        return PROPERTY_ERROR_FILE;
    }
    
    char line[500];
    bool found = false;
    
    // خواندن خط اول (هدر)
    if (fgets(line, sizeof(line), file) == NULL) {
        fclose(file);
        return PROPERTY_ERROR_FILE;
    }
    
    // جستجو برای کاربر
    while (fgets(line, sizeof(line), file) != NULL) {
        char username_read[50], password_read[100], name_read[50], lastName_read[50];
        char nationalCode_read[20], phoneNumber_read[20], email_read[50], registrationDateTime_read[50];
        long lastLoginTime_read;
        
        // تجزیه سطر CSV
        int ret = sscanf(line, "%[^,],%[^,],%[^,],%[^,],%[^,],%[^,],%[^,],%[^,],%ld",
               username_read, password_read, name_read, lastName_read, nationalCode_read,
               phoneNumber_read, email_read, registrationDateTime_read, &lastLoginTime_read);
        
        if (ret != 9) {
            continue; // خط نامعتبر، ادامه بده
        }
        
        if (strcmp(username_read, username) == 0) {
            // کاربر پیدا شد، بررسی رمز عبور
            found = true;
            
            // در یک پیاده‌سازی واقعی، باید رمز ورودی هش شود و با رمز هش‌شده مقایسه شود
            if (strcmp(password_read, password) == 0) {
                // رمز عبور صحیح است
                strcpy(out_user->username, username_read);
                strcpy(out_user->password, ""); // برای امنیت، رمز را در ساختار ذخیره نمی‌کنیم
                strcpy(out_user->name, name_read);
                strcpy(out_user->lastName, lastName_read);
                strcpy(out_user->nationalCode, nationalCode_read);
                strcpy(out_user->phoneNumber, phoneNumber_read);
                strcpy(out_user->email, email_read);
                strcpy(out_user->registrationDateTime, registrationDateTime_read);
                out_user->lastLoginTime = lastLoginTime_read;
                out_user->propertyCount = 0; // باید در جای دیگری محاسبه شود
                out_user->next = NULL;
                
                // به‌روزرسانی زمان آخرین ورود
                user_update_last_login(username);
                
                // حذف رکوردهای تلاش ناموفق
                removeUserAttempts(username);
                
                fclose(file);
                return PROPERTY_SUCCESS;
            } else {
                // رمز عبور اشتباه است
                int attempts = user_record_failed_attempt(username);
                
                // بررسی تعداد تلاش‌ها برای قفل کردن حساب
                if (attempts >= 5) { // پس از 5 تلاش ناموفق
                    lockAccount(username, attempts);
                }
                
                fclose(file);
                return PROPERTY_ERROR_VALIDATION;
            }
        }
    }
    
    fclose(file);
    
    if (!found) {
        // کاربر پیدا نشد
        return PROPERTY_ERROR_NOT_FOUND;
    }
    
    return PROPERTY_ERROR_VALIDATION; // هیچ موردی پیدا نشد، اما خطای اعتبارسنجی برمی‌گردانیم
}

bool user_is_valid_username(const char* username) {
    if (!username || strlen(username) < 3 || strlen(username) > 30) {
        return false;
    }
    
    // بررسی کاراکترهای مجاز (حروف، اعداد، زیرخط)
    for (int i = 0; username[i]; i++) {
        if (!isalnum(username[i]) && username[i] != '_') {
            return false;
        }
    }
    
    return true;
}

bool user_is_duplicate_username(const char* username) {
    if (!username) {
        return false;
    }
    
    // ساخت مسیر کامل فایل
    char full_path[300];
    get_full_path(full_path, USER_FILE);
    
    FILE* file = fopen(full_path, "r");
    if (!file) {
        return false; // فایل وجود ندارد، پس کاربری ثبت نشده
    }
    
    char line[500];
    bool duplicate = false;
    
    // خواندن خط اول (هدر)
    if (fgets(line, sizeof(line), file) == NULL) {
        fclose(file);
        return false;
    }
    
    // جستجو برای نام کاربری تکراری
    while (fgets(line, sizeof(line), file) != NULL) {
        char username_read[50];
        sscanf(line, "%[^,]", username_read);
        
        if (strcmp(username_read, username) == 0) {
            duplicate = true;
            break;
        }
    }
    
    fclose(file);
    return duplicate;
}

bool user_is_strong_password(const char* password) {
    if (!password || strlen(password) < 8) {
        return false;
    }
    
    bool has_upper = false;
    bool has_lower = false;
    bool has_digit = false;
    
    for (int i = 0; password[i]; i++) {
        if (isupper(password[i])) has_upper = true;
        else if (islower(password[i])) has_lower = true;
        else if (isdigit(password[i])) has_digit = true;
    }
    
    return has_upper && has_lower && has_digit;
}

bool user_is_valid_email(const char* email) {
    if (!email || strlen(email) < 5) {
        return false;
    }
    
    // بررسی ساده ایمیل (باید @ و . داشته باشد)
    const char* at = strchr(email, '@');
    if (!at) return false;
    
    const char* dot = strchr(at, '.');
    if (!dot || dot == at + 1) return false;
    
    return true;
}

bool user_is_valid_phone_number(const char* phoneNumber) {
    if (!phoneNumber) return false;
    
    int len = strlen(phoneNumber);
    
    // شماره موبایل ایران باید 11 رقم باشد و با 09 شروع شود
    if (len != 11 || phoneNumber[0] != '0' || phoneNumber[1] != '9') {
        return false;
    }
    
    // بررسی اینکه فقط شامل اعداد باشد
    for (int i = 0; i < len; i++) {
        if (!isdigit(phoneNumber[i])) {
            return false;
        }
    }
    
    return true;
}

bool user_is_valid_national_code(const char* nationalCode) {
    if (!nationalCode) return false;
    
    int len = strlen(nationalCode);
    
    // کد ملی ایران باید 10 رقم باشد
    if (len != 10) {
        return false;
    }
    
    // بررسی اینکه فقط شامل اعداد باشد
    for (int i = 0; i < len; i++) {
        if (!isdigit(nationalCode[i])) {
            return false;
        }
    }
    
    // در یک پیاده‌سازی کامل، الگوریتم اعتبارسنجی کد ملی ایران پیاده‌سازی می‌شود
    
    return true;
}

int user_record_failed_attempt(const char* username) {
    if (!username) return 0;
    
    // ساخت مسیر کامل فایل
    char full_path[300];
    get_full_path(full_path, FAILED_ATTEMPTS_FILE);
    
    // خواندن تلاش‌های قبلی
    FILE* read_file = fopen(full_path, "r");
    int attempts = 0;
    bool found = false;
    char line[500];
    char tempFileName[300];
    sprintf(tempFileName, "%sfailed_attempts_temp.csv", data_path);
    FILE* temp_file = fopen(tempFileName, "w");
    
    if (!temp_file) {
        if (read_file) fclose(read_file);
        return 0;
    }
    
    // اگر فایل وجود دارد، آن را پردازش کن
    if (read_file) {
        // خواندن هدر
        if (fgets(line, sizeof(line), read_file) != NULL) {
            fprintf(temp_file, "%s", line);
        } else {
            fprintf(temp_file, "username,attempts,last_attempt_time\n");
        }
        
        // خواندن رکوردها
        while (fgets(line, sizeof(line), read_file) != NULL) {
            char username_read[50];
            int attempts_read;
            time_t last_attempt_time;
            
            sscanf(line, "%[^,],%d,%ld", username_read, &attempts_read, &last_attempt_time);
            
            if (strcmp(username_read, username) == 0) {
                // به‌روزرسانی رکورد موجود
                attempts = attempts_read + 1;
                found = true;
                fprintf(temp_file, "%s,%d,%ld\n", username, attempts, time(NULL));
            } else {
                // کپی رکورد موجود
                fprintf(temp_file, "%s", line);
            }
        }
        
        fclose(read_file);
    } else {
        // ایجاد فایل جدید
        fprintf(temp_file, "username,attempts,last_attempt_time\n");
    }
    
    // اگر کاربر قبلاً ثبت نشده، اضافه کن
    if (!found) {
        attempts = 1;
        fprintf(temp_file, "%s,%d,%ld\n", username, attempts, time(NULL));
    }
    
    fclose(temp_file);
    
    // جایگزینی فایل اصلی با فایل موقت
    remove(full_path);
    rename(tempFileName, full_path);
    
    return attempts;
}

void removeUserAttempts(char* username) {
    if (!username) return;
    
    // ساخت مسیر کامل فایل
    char full_path[300];
    get_full_path(full_path, FAILED_ATTEMPTS_FILE);
    
    FILE* read_file = fopen(full_path, "r");
    if (!read_file) return;
    
    char line[500];
    char tempFileName[300];
    sprintf(tempFileName, "%sfailed_attempts_temp.csv", data_path);
    FILE* temp_file = fopen(tempFileName, "w");
    
    if (!temp_file) {
        fclose(read_file);
        return;
    }
    
    // کپی هدر
    if (fgets(line, sizeof(line), read_file) != NULL) {
        fprintf(temp_file, "%s", line);
    }
    
    // کپی همه رکوردها به جز رکورد کاربر مورد نظر
    while (fgets(line, sizeof(line), read_file) != NULL) {
        char username_read[50];
        sscanf(line, "%[^,]", username_read);
        
        if (strcmp(username_read, username) != 0) {
            fprintf(temp_file, "%s", line);
        }
    }
    
    fclose(read_file);
    fclose(temp_file);
    
    // جایگزینی فایل اصلی با فایل موقت
    remove(full_path);
    rename(tempFileName, full_path);
    
    // همچنین رکورد قفل حساب را هم حذف کن
    get_full_path(full_path, LOCKED_ACCOUNTS_FILE);
    read_file = fopen(full_path, "r");
    
    if (read_file) {
        sprintf(tempFileName, "%slocked_accounts_temp.csv", data_path);
        temp_file = fopen(tempFileName, "w");
        
        if (temp_file) {
            // کپی هدر
            if (fgets(line, sizeof(line), read_file) != NULL) {
                fprintf(temp_file, "%s", line);
            }
            
            // کپی همه رکوردها به جز رکورد کاربر مورد نظر
            while (fgets(line, sizeof(line), read_file) != NULL) {
                char username_read[50];
                sscanf(line, "%[^,]", username_read);
                
                if (strcmp(username_read, username) != 0) {
                    fprintf(temp_file, "%s", line);
                }
            }
            
            fclose(temp_file);
            
            // جایگزینی فایل اصلی با فایل موقت
            remove(full_path);
            rename(tempFileName, full_path);
        }
        
        fclose(read_file);
    }
}

void lockAccount(const char* username, int count) {
    if (!username) return;
    
    // ساخت مسیر کامل فایل
    char full_path[300];
    get_full_path(full_path, LOCKED_ACCOUNTS_FILE);
    
    FILE* file = fopen(full_path, "a");
    if (!file) {
        // ایجاد فایل جدید
        file = fopen(full_path, "w");
        if (!file) return;
        
        fprintf(file, "username,lock_time,lock_duration\n");
    }
    
    // محاسبه مدت زمان قفل بر اساس تعداد تلاش‌ها
    int lock_duration = 300; // 5 دقیقه پیش‌فرض
    
    if (count >= 10) {
        lock_duration = 3600; // 1 ساعت
    } else if (count >= 7) {
        lock_duration = 1800; // 30 دقیقه
    } else if (count >= 5) {
        lock_duration = 600; // 10 دقیقه
    }
    
    time_t now = time(NULL);
    fprintf(file, "%s,%ld,%d\n", username, now, lock_duration);
    
    fclose(file);
}

bool user_is_account_locked(const char* username, long* remainingSeconds) {
    if (!username) return false;
    
    // ساخت مسیر کامل فایل
    char full_path[300];
    get_full_path(full_path, LOCKED_ACCOUNTS_FILE);
    
    FILE* file = fopen(full_path, "r");
    if (!file) return false;
    
    char line[500];
    bool is_locked = false;
    
    // خواندن هدر
    if (fgets(line, sizeof(line), file) == NULL) {
        fclose(file);
        return false;
    }
    
    // جستجو برای رکورد قفل حساب کاربر
    while (fgets(line, sizeof(line), file) != NULL) {
        char username_read[50];
        time_t lock_time;
        int lock_duration;
        
        sscanf(line, "%[^,],%ld,%d", username_read, &lock_time, &lock_duration);
        
        if (strcmp(username_read, username) == 0) {
            // محاسبه زمان باقی‌مانده
            time_t now = time(NULL);
            time_t unlock_time = lock_time + lock_duration;
            
            if (now < unlock_time) {
                // حساب هنوز قفل است
                is_locked = true;
                if (remainingSeconds) {
                    *remainingSeconds = unlock_time - now;
                }
            }
            
            break;
        }
    }
    
    fclose(file);
    return is_locked;
}

int user_update_last_login(const char* username) {
    if (!username) return PROPERTY_ERROR_VALIDATION;
    
    // ساخت مسیر کامل فایل
    char full_path[300];
    get_full_path(full_path, USER_FILE);
    
    FILE* read_file = fopen(full_path, "r");
    if (!read_file) return PROPERTY_ERROR_FILE;
    
    char line[500];
    char tempFileName[300];
    sprintf(tempFileName, "%susers_temp.csv", data_path);
    FILE* temp_file = fopen(tempFileName, "w");
    
    if (!temp_file) {
        fclose(read_file);
        return PROPERTY_ERROR_FILE;
    }
    
    bool user_found = false;
    
    // کپی هدر
    if (fgets(line, sizeof(line), read_file) != NULL) {
        fprintf(temp_file, "%s", line);
    }
    
    // به‌روزرسانی زمان آخرین ورود کاربر
    while (fgets(line, sizeof(line), read_file) != NULL) {
        char username_read[50], password_read[100], name_read[50], lastName_read[50];
        char nationalCode_read[20], phoneNumber_read[20], email_read[50], registrationDateTime_read[50];
        long lastLoginTime_read;
        
        // کپی سطر با فرمت CSV
        char lineCopy[500];
        strcpy(lineCopy, line);
        
        // تجزیه سطر CSV
        int ret = sscanf(line, "%[^,],%[^,],%[^,],%[^,],%[^,],%[^,],%[^,],%[^,],%ld",
               username_read, password_read, name_read, lastName_read, nationalCode_read,
               phoneNumber_read, email_read, registrationDateTime_read, &lastLoginTime_read);
        
        if (ret != 9) {
            // خط نامعتبر، کپی بدون تغییر
            fprintf(temp_file, "%s", lineCopy);
            continue;
        }
        
        if (strcmp(username_read, username) == 0) {
            // کاربر پیدا شد، به‌روزرسانی زمان آخرین ورود
            user_found = true;
            time_t now = time(NULL);
            fprintf(temp_file, "%s,%s,%s,%s,%s,%s,%s,%s,%ld\n",
                   username_read, password_read, name_read, lastName_read, nationalCode_read,
                   phoneNumber_read, email_read, registrationDateTime_read, now);
        } else {
            // کاربر دیگر، کپی بدون تغییر
            fprintf(temp_file, "%s", lineCopy);
        }
    }
    
    fclose(read_file);
    fclose(temp_file);
    
    if (!user_found) {
        remove(tempFileName);
        return PROPERTY_ERROR_NOT_FOUND;
    }
    
    // جایگزینی فایل اصلی با فایل موقت
    remove(full_path);
    rename(tempFileName, full_path);
    
    return PROPERTY_SUCCESS;
} 