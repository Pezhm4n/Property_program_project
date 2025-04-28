/**
 * @file user_example.c
 * @brief مثال استفاده از بخش مدیریت کاربران کتابخانه
 */

#include "../include/property_lib.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main() {
    // تنظیم مسیر ذخیره‌سازی داده‌ها
    property_set_data_path("./data/");
    
    // نمایش نسخه کتابخانه
    printf("Property Management Library Version: %s\n", property_get_version());
    
    // متغیرهای مورد نیاز
    char username[50] = "test_user";
    char password[50] = "Test123456";
    char name[50] = "علی";
    char lastName[50] = "رضایی";
    char nationalCode[20] = "1234567890";
    char phoneNumber[20] = "09123456789";
    char email[50] = "test@example.com";
    User user;
    int result;
    
    // ثبت‌نام کاربر
    result = user_register(username, password, name, lastName, nationalCode, phoneNumber, email);
    printf("User registration result: %s\n", property_error_to_string(result));
    
    if (result == PROPERTY_ERROR_DUPLICATE) {
        printf("User already exists. Proceeding with login.\n");
    } else if (result != PROPERTY_SUCCESS) {
        printf("Failed to register user. Exiting.\n");
        return 1;
    }
    
    // ورود به سیستم
    result = user_login(username, password, &user);
    printf("User login result: %s\n", property_error_to_string(result));
    
    if (result == PROPERTY_SUCCESS) {
        printf("Logged in successfully:\n");
        printf("Username: %s\n", user.username);
        printf("Name: %s %s\n", user.name, user.lastName);
        printf("Email: %s\n", user.email);
        printf("Phone: %s\n", user.phoneNumber);
        printf("Registration date: %s\n", user.registrationDateTime);
    } else {
        printf("Failed to login. Exiting.\n");
        return 1;
    }
    
    // تست تلاش ناموفق ورود
    printf("\nTesting failed login attempts:\n");
    result = user_login(username, "wrong_password", &user);
    printf("Login with wrong password result: %s\n", property_error_to_string(result));
    
    // تست تغییر رمز عبور
    printf("\nTesting password change:\n");
    result = user_change_password(username, password, "NewTest123456");
    printf("Password change result: %s\n", property_error_to_string(result));
    
    if (result == PROPERTY_SUCCESS) {
        printf("Testing login with new password:\n");
        result = user_login(username, "NewTest123456", &user);
        printf("Login with new password result: %s\n", property_error_to_string(result));
        
        // بازگرداندن رمز عبور به حالت اولیه
        user_change_password(username, "NewTest123456", password);
    }
    
    // تست تغییر ایمیل
    printf("\nTesting profile update:\n");
    result = user_update_profile(username, "email", "new_email@example.com");
    printf("Email update result: %s\n", property_error_to_string(result));
    
    if (result == PROPERTY_SUCCESS) {
        // ورود مجدد برای دیدن تغییرات
        user_login(username, password, &user);
        printf("Updated email: %s\n", user.email);
        
        // بازگرداندن ایمیل به حالت اولیه
        user_update_profile(username, "email", email);
    }
    
    printf("\nExample completed successfully!\n");
    return 0;
} 