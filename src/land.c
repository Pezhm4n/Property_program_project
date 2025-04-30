/**
 * @file land.c
 * @brief پیاده‌سازی توابع مدیریت زمین‌ها
 */

#include "../include/land.h"
#include "../include/property_lib.h"
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <time.h>

// مسیرهای فایل برای ذخیره زمین‌ها
#define LAND_SALES_PATH "data/land_sales.csv"
#define LAND_RENTALS_PATH "data/land_rentals.csv"

// متغیر جهانی برای مسیر پایه داده
static char data_path_base[256] = "./";

/**
 * @brief تنظیم مسیر پایه برای فایل‌های داده
 * 
 * @param base_path مسیر پایه
 */
void land_set_data_path(const char* base_path) {
    if (base_path) {
        strncpy(data_path_base, base_path, sizeof(data_path_base) - 1);
        data_path_base[sizeof(data_path_base) - 1] = '\0';
    }
}

/**
 * @brief اعتبارسنجی داده‌های زمین
 * 
 * @param property اطلاعات زمین
 * @return int کد خطا: 0 (معتبر)، 1 (نامعتبر)
 */
static int validate_land_property(LandProperty* property) {
    if (!property) {
        property_log("ERROR", "Invalid land property (NULL)");
        return 1;
    }
    
    if (property->base.municipalityDistrict <= 0) {
        property_log("ERROR", "Invalid municipality district");
        return 1;
    }
    
    if (!property_check_address_format(property->base.address)) {
        property_log("ERROR", "Invalid address format");
        return 1;
    }
    
    if (strlen(property->base.ownerPhoneNumber) < 10) {
        property_log("ERROR", "Invalid owner phone number");
        return 1;
    }
    
    if (property->landArea <= 0) {
        property_log("ERROR", "Invalid land area");
        return 1;
    }
    
    if (property->distanceToMainRoad < 0) {
        property_log("ERROR", "Invalid distance to main road");
        return 1;
    }
    
    if (property->hasWell != 0 && property->hasWell != 1) {
        property_log("ERROR", "Invalid has well flag (should be 0 or 1)");
        return 1;
    }
    
    if (strlen(property->landType) == 0) {
        property_log("ERROR", "Land type cannot be empty");
        return 1;
    }
    
    return 0;
}

int land_register_sale(LandProperty* property, const char* username) {
    char log_message[256];
    FILE* file;
    time_t now = time(NULL);
    
    // اعتبارسنجی ورودی‌ها
    if (!property || !username || strlen(username) == 0) {
        property_log("ERROR", "Invalid parameters for land property registration");
        return 1;
    }
    
    // اعتبارسنجی اطلاعات زمین
    if (validate_land_property(property)) {
        return 1;
    }
    
    // اگر قیمت صفر یا منفی باشد
    if (property->sellingPrice <= 0) {
        property_log("ERROR", "Invalid selling price");
        return 1;
    }
    
    // تنظیم اطلاعات پایه
    property->base.propertyId = property_generate_id();
    property->base.isActive = PROPERTY_STATUS_ACTIVE;
    property->base.dealType = PROPERTY_DEAL_SALE;
    strcpy(property->base.registeredBy, username);
    property->base.deleteDate[0] = '\0';  // تاریخ حذف خالی
    
    // تنظیم تاریخ ثبت
    struct tm* tm_info = localtime(&now);
    strftime(property->base.registrationDate, sizeof(property->base.registrationDate), 
             "%Y-%m-%d", tm_info);
    
    // باز کردن فایل برای افزودن داده
    file = fopen(LAND_SALES_PATH, "a");
    if (!file) {
        property_log("ERROR", "Failed to open land sales file for writing");
        return 2;
    }
    
    // نوشتن داده در فایل CSV
    fprintf(file, "%d,%d,%s,%s,%s,%s,%d,%s,%s,%f,%f,%d,%lf,0.0,0.0,%s,%s,%ld,%s\n",
            property->base.propertyId,
            property->base.municipalityDistrict,
            property->base.address,
            property->base.ownerPhoneNumber,
            property->landType,
            property->base.registrationDate,
            property->base.isActive,
            property->base.deleteDate,
            property->base.registeredBy,
            property->landArea,
            property->distanceToMainRoad,
            property->hasWell,
            property->sellingPrice,
            "SALE",
            (long)now,
            "OK");
    
    fclose(file);
    
    // افزایش شمارنده املاک
    int current_count = property_get_count();
    property_update_count(current_count + 1);
    
    // ثبت گزارش در فایل لاگ
    snprintf(log_message, sizeof(log_message), 
             "Land property registered for sale - ID: %d, by: %s", 
             property->base.propertyId, username);
    property_log("INFO", log_message);
    
    return 0;
}

int land_register_rental(LandProperty* property, const char* username) {
    char log_message[256];
    FILE* file;
    time_t now = time(NULL);
    
    // اعتبارسنجی ورودی‌ها
    if (!property || !username || strlen(username) == 0) {
        property_log("ERROR", "Invalid parameters for land property rental registration");
        return 1;
    }
    
    // اعتبارسنجی اطلاعات زمین
    if (validate_land_property(property)) {
        return 1;
    }
    
    // اگر مبلغ رهن و اجاره هر دو صفر یا منفی باشند
    if (property->mortgageAmount <= 0 && property->monthlyRentAmount <= 0) {
        property_log("ERROR", "Both mortgage and rent amounts cannot be zero or negative");
        return 1;
    }
    
    // تنظیم اطلاعات پایه
    property->base.propertyId = property_generate_id();
    property->base.isActive = PROPERTY_STATUS_ACTIVE;
    property->base.dealType = PROPERTY_DEAL_RENT;
    strcpy(property->base.registeredBy, username);
    property->base.deleteDate[0] = '\0';  // تاریخ حذف خالی
    
    // تنظیم تاریخ ثبت
    struct tm* tm_info = localtime(&now);
    strftime(property->base.registrationDate, sizeof(property->base.registrationDate), 
             "%Y-%m-%d", tm_info);
    
    // باز کردن فایل برای افزودن داده
    file = fopen(LAND_RENTALS_PATH, "a");
    if (!file) {
        property_log("ERROR", "Failed to open land rentals file for writing");
        return 2;
    }
    
    // نوشتن داده در فایل CSV
    fprintf(file, "%d,%d,%s,%s,%s,%s,%d,%s,%s,%f,%f,%d,0.0,%lf,%lf,%s,%s,%ld,%s\n",
            property->base.propertyId,
            property->base.municipalityDistrict,
            property->base.address,
            property->base.ownerPhoneNumber,
            property->landType,
            property->base.registrationDate,
            property->base.isActive,
            property->base.deleteDate,
            property->base.registeredBy,
            property->landArea,
            property->distanceToMainRoad,
            property->hasWell,
            property->mortgageAmount,
            property->monthlyRentAmount,
            "RENT",
            (long)now,
            "OK");
    
    fclose(file);
    
    // افزایش شمارنده املاک
    int current_count = property_get_count();
    property_update_count(current_count + 1);
    
    // ثبت گزارش در فایل لاگ
    snprintf(log_message, sizeof(log_message), 
             "Land property registered for rent - ID: %d, by: %s", 
             property->base.propertyId, username);
    property_log("INFO", log_message);
    
    return 0;
}

LandProperty* land_find_by_district(int district, PropertyDealType dealType, int* count) {
    char filename[256];
    char log_message[256];
    LandProperty* results = NULL;
    *count = 0;
    
    // انتخاب فایل بر اساس نوع معامله
    if (dealType == PROPERTY_DEAL_SALE) {
        strcpy(filename, LAND_SALES_PATH);
    } else if (dealType == PROPERTY_DEAL_RENT) {
        strcpy(filename, LAND_RENTALS_PATH);
    } else {
        property_log("ERROR", "Invalid deal type for district-based land property search");
        return NULL;
    }
    
    // باز کردن فایل
    FILE* file = fopen(filename, "r");
    if (!file) {
        snprintf(log_message, sizeof(log_message), 
                 "Error opening file for district-based land property search");
        property_log("ERROR", log_message);
        return NULL;
    }
    
    // شمارش تعداد زمین‌های واجد شرایط
    char line[1024];
    int match_count = 0;
    
    while (fgets(line, sizeof(line), file)) {
        int id, municipality_district, is_active, has_well, timestamp;
        float land_area, distance_to_road;
        double selling_price, mortgage_amount, monthly_rent;
        char address[100], owner_phone[20], land_type[20], reg_date[11], del_date[11], 
             reg_by[50], deal_type[10], status[20];
        
        // خواندن داده‌ها از خط فایل
        sscanf(line, "%d,%d,%[^,],%[^,],%[^,],%[^,],%d,%[^,],%[^,],%f,%f,%d,%lf,%lf,%lf,%[^,],%[^,],%d,%s",
               &id, &municipality_district, address, owner_phone, land_type, reg_date, 
               &is_active, del_date, reg_by, &land_area, &distance_to_road, &has_well,
               &selling_price, &mortgage_amount, &monthly_rent, deal_type, &timestamp, status);
        
        // بررسی فعال بودن زمین و تطابق با منطقه مورد نظر (یا همه مناطق)
        if (is_active == PROPERTY_STATUS_ACTIVE && 
            (district == 0 || municipality_district == district)) {
            match_count++;
        }
    }
    
    // اگر هیچ موردی پیدا نشد
    if (match_count == 0) {
        fclose(file);
        return NULL;
    }
    
    // تخصیص حافظه برای نتایج
    results = (LandProperty*)malloc(match_count * sizeof(LandProperty));
    if (!results) {
        property_log("ERROR", "Memory allocation error in district-based land property search");
        fclose(file);
        return NULL;
    }
    
    // بازگشت به ابتدای فایل
    rewind(file);
    
    // خواندن و ذخیره زمین‌های واجد شرایط
    int index = 0;
    while (fgets(line, sizeof(line), file) && index < match_count) {
        LandProperty* property = &results[index];
        int id, municipality_district, is_active, has_well, timestamp;
        float land_area, distance_to_road;
        double selling_price, mortgage_amount, monthly_rent;
        char address[100], owner_phone[20], land_type[20], reg_date[11], del_date[11], 
             reg_by[50], deal_type[10], status[20];
        
        // خواندن داده‌ها از خط فایل
        sscanf(line, "%d,%d,%[^,],%[^,],%[^,],%[^,],%d,%[^,],%[^,],%f,%f,%d,%lf,%lf,%lf,%[^,],%[^,],%d,%s",
               &id, &municipality_district, address, owner_phone, land_type, reg_date, 
               &is_active, del_date, reg_by, &land_area, &distance_to_road, &has_well,
               &selling_price, &mortgage_amount, &monthly_rent, deal_type, &timestamp, status);
        
        // بررسی فعال بودن زمین و تطابق با منطقه مورد نظر (یا همه مناطق)
        if (is_active == PROPERTY_STATUS_ACTIVE && 
            (district == 0 || municipality_district == district)) {
            property->base.propertyId = id;
            property->base.municipalityDistrict = municipality_district;
            strcpy(property->base.address, address);
            strcpy(property->base.ownerPhoneNumber, owner_phone);
            strcpy(property->landType, land_type);
            strcpy(property->base.registrationDate, reg_date);
            strcpy(property->base.deleteDate, del_date);
            property->base.isActive = is_active;
            strcpy(property->base.registeredBy, reg_by);
            property->base.dealType = dealType;
            
            property->landArea = land_area;
            property->distanceToMainRoad = distance_to_road;
            property->hasWell = has_well;
            property->sellingPrice = selling_price;
            property->mortgageAmount = mortgage_amount;
            property->monthlyRentAmount = monthly_rent;
            
            index++;
        }
    }
    
    fclose(file);
    *count = index;
    
    snprintf(log_message, sizeof(log_message), 
             "Land property search by district %d: found %d properties", district, index);
    property_log("INFO", log_message);
    
    return results;
}

LandProperty* land_find_by_area(float minArea, float maxArea, PropertyDealType dealType, int* count) {
    char filename[256];
    char log_message[256];
    LandProperty* results = NULL;
    *count = 0;
    
    // بررسی پارامترهای ورودی
    if (minArea < 0 || (maxArea > 0 && maxArea < minArea)) {
        property_log("ERROR", "Invalid area range for land property search");
        return NULL;
    }
    
    // انتخاب فایل بر اساس نوع معامله
    if (dealType == PROPERTY_DEAL_SALE) {
        strcpy(filename, LAND_SALES_PATH);
    } else if (dealType == PROPERTY_DEAL_RENT) {
        strcpy(filename, LAND_RENTALS_PATH);
    } else {
        property_log("ERROR", "Invalid deal type for area-based land property search");
        return NULL;
    }
    
    // باز کردن فایل
    FILE* file = fopen(filename, "r");
    if (!file) {
        snprintf(log_message, sizeof(log_message), 
                 "Error opening file for area-based land property search");
        property_log("ERROR", log_message);
        return NULL;
    }
    
    // شمارش تعداد زمین‌های واجد شرایط
    char line[1024];
    int match_count = 0;
    
    while (fgets(line, sizeof(line), file)) {
        int id, municipality_district, is_active, has_well, timestamp;
        float land_area, distance_to_road;
        double selling_price, mortgage_amount, monthly_rent;
        char address[100], owner_phone[20], land_type[20], reg_date[11], del_date[11], 
             reg_by[50], deal_type[10], status[20];
        
        // خواندن داده‌ها از خط فایل
        sscanf(line, "%d,%d,%[^,],%[^,],%[^,],%[^,],%d,%[^,],%[^,],%f,%f,%d,%lf,%lf,%lf,%[^,],%[^,],%d,%s",
               &id, &municipality_district, address, owner_phone, land_type, reg_date, 
               &is_active, del_date, reg_by, &land_area, &distance_to_road, &has_well,
               &selling_price, &mortgage_amount, &monthly_rent, deal_type, &timestamp, status);
        
        // بررسی فعال بودن زمین و تطابق با محدوده مساحت
        if (is_active == PROPERTY_STATUS_ACTIVE && 
            land_area >= minArea && 
            (maxArea == 0 || land_area <= maxArea)) {
            match_count++;
        }
    }
    
    // اگر هیچ موردی پیدا نشد
    if (match_count == 0) {
        fclose(file);
        return NULL;
    }
    
    // تخصیص حافظه برای نتایج
    results = (LandProperty*)malloc(match_count * sizeof(LandProperty));
    if (!results) {
        property_log("ERROR", "Memory allocation error in area-based land property search");
        fclose(file);
        return NULL;
    }
    
    // بازگشت به ابتدای فایل
    rewind(file);
    
    // خواندن و ذخیره زمین‌های واجد شرایط
    int index = 0;
    while (fgets(line, sizeof(line), file) && index < match_count) {
        LandProperty* property = &results[index];
        int id, municipality_district, is_active, has_well, timestamp;
        float land_area, distance_to_road;
        double selling_price, mortgage_amount, monthly_rent;
        char address[100], owner_phone[20], land_type[20], reg_date[11], del_date[11], 
             reg_by[50], deal_type[10], status[20];
        
        // خواندن داده‌ها از خط فایل
        sscanf(line, "%d,%d,%[^,],%[^,],%[^,],%[^,],%d,%[^,],%[^,],%f,%f,%d,%lf,%lf,%lf,%[^,],%[^,],%d,%s",
               &id, &municipality_district, address, owner_phone, land_type, reg_date, 
               &is_active, del_date, reg_by, &land_area, &distance_to_road, &has_well,
               &selling_price, &mortgage_amount, &monthly_rent, deal_type, &timestamp, status);
        
        // بررسی فعال بودن زمین و تطابق با محدوده مساحت
        if (is_active == PROPERTY_STATUS_ACTIVE && 
            land_area >= minArea && 
            (maxArea == 0 || land_area <= maxArea)) {
            property->base.propertyId = id;
            property->base.municipalityDistrict = municipality_district;
            strcpy(property->base.address, address);
            strcpy(property->base.ownerPhoneNumber, owner_phone);
            strcpy(property->landType, land_type);
            strcpy(property->base.registrationDate, reg_date);
            strcpy(property->base.deleteDate, del_date);
            property->base.isActive = is_active;
            strcpy(property->base.registeredBy, reg_by);
            property->base.dealType = dealType;
            
            property->landArea = land_area;
            property->distanceToMainRoad = distance_to_road;
            property->hasWell = has_well;
            property->sellingPrice = selling_price;
            property->mortgageAmount = mortgage_amount;
            property->monthlyRentAmount = monthly_rent;
            
            index++;
        }
    }
    
    fclose(file);
    *count = index;
    
    snprintf(log_message, sizeof(log_message), 
             "Land property search by area range %.2f-%.2f: found %d properties", 
             minArea, maxArea == 0 ? 999999.99 : maxArea, index);
    property_log("INFO", log_message);
    
    return results;
}

LandProperty* land_find_by_price(double minPrice, double maxPrice, PropertyDealType dealType, int* count) {
    char filename[256];
    char log_message[256];
    LandProperty* results = NULL;
    *count = 0;
    
    // بررسی پارامترهای ورودی
    if (minPrice < 0 || (maxPrice > 0 && maxPrice < minPrice)) {
        property_log("ERROR", "Invalid price range for land property search");
        return NULL;
    }
    
    // انتخاب فایل بر اساس نوع معامله
    if (dealType == PROPERTY_DEAL_SALE) {
        strcpy(filename, LAND_SALES_PATH);
    } else if (dealType == PROPERTY_DEAL_RENT) {
        strcpy(filename, LAND_RENTALS_PATH);
    } else {
        property_log("ERROR", "Invalid deal type for price-based land property search");
        return NULL;
    }
    
    // باز کردن فایل
    FILE* file = fopen(filename, "r");
    if (!file) {
        snprintf(log_message, sizeof(log_message), "Error opening file for price-based land property search");
        property_log("ERROR", log_message);
        return NULL;
    }
    
    // شمارش تعداد زمین‌های واجد شرایط
    char line[1024];
    int match_count = 0;
    
    while (fgets(line, sizeof(line), file)) {
        int id, municipality_district, is_active, has_well, timestamp;
        float land_area, distance_to_road;
        double selling_price, mortgage_amount, monthly_rent;
        char address[100], owner_phone[20], land_type[20], reg_date[11], del_date[11], 
             reg_by[50], deal_type[10], status[20];
        
        // خواندن داده‌ها از خط فایل
        sscanf(line, "%d,%d,%[^,],%[^,],%[^,],%[^,],%d,%[^,],%[^,],%f,%f,%d,%lf,%lf,%lf,%[^,],%[^,],%d,%s",
               &id, &municipality_district, address, owner_phone, land_type, reg_date, 
               &is_active, del_date, reg_by, &land_area, &distance_to_road, &has_well,
               &selling_price, &mortgage_amount, &monthly_rent, deal_type, &timestamp, status);
        
        // متغیری برای ذخیره قیمت مورد بررسی
        double price_to_check;
        
        // تعیین قیمت مورد بررسی بر اساس نوع معامله
        if (dealType == PROPERTY_DEAL_SALE) {
            price_to_check = selling_price;
        } else {
            // برای اجاره، مجموع ودیعه و 12 ماه اجاره را در نظر می‌گیریم
            price_to_check = mortgage_amount + (monthly_rent * 12);
        }
        
        // بررسی فعال بودن زمین و تطابق با محدوده قیمت
        if (is_active == PROPERTY_STATUS_ACTIVE && 
            price_to_check >= minPrice && 
            (maxPrice == 0 || price_to_check <= maxPrice)) {
            match_count++;
        }
    }
    
    // اگر هیچ موردی پیدا نشد
    if (match_count == 0) {
        fclose(file);
        return NULL;
    }
    
    // تخصیص حافظه برای نتایج
    results = (LandProperty*)malloc(match_count * sizeof(LandProperty));
    if (!results) {
        property_log("ERROR", "Memory allocation error in price-based land property search");
        fclose(file);
        return NULL;
    }
    
    // بازگشت به ابتدای فایل
    rewind(file);
    
    // خواندن و ذخیره زمین‌های واجد شرایط
    int index = 0;
    while (fgets(line, sizeof(line), file) && index < match_count) {
        LandProperty* property = &results[index];
        int id, municipality_district, is_active, has_well, timestamp;
        float land_area, distance_to_road;
        double selling_price, mortgage_amount, monthly_rent;
        char address[100], owner_phone[20], land_type[20], reg_date[11], del_date[11], 
             reg_by[50], deal_type[10], status[20];
        
        // خواندن داده‌ها از خط فایل
        sscanf(line, "%d,%d,%[^,],%[^,],%[^,],%[^,],%d,%[^,],%[^,],%f,%f,%d,%lf,%lf,%lf,%[^,],%[^,],%d,%s",
               &id, &municipality_district, address, owner_phone, land_type, reg_date, 
               &is_active, del_date, reg_by, &land_area, &distance_to_road, &has_well,
               &selling_price, &mortgage_amount, &monthly_rent, deal_type, &timestamp, status);
        
        // متغیری برای ذخیره قیمت مورد بررسی
        double price_to_check;
        
        // تعیین قیمت مورد بررسی بر اساس نوع معامله
        if (dealType == PROPERTY_DEAL_SALE) {
            price_to_check = selling_price;
        } else {
            // برای اجاره، مجموع ودیعه و 12 ماه اجاره را در نظر می‌گیریم
            price_to_check = mortgage_amount + (monthly_rent * 12);
        }
        
        // بررسی فعال بودن زمین و تطابق با محدوده قیمت
        if (is_active == PROPERTY_STATUS_ACTIVE && 
            price_to_check >= minPrice && 
            (maxPrice == 0 || price_to_check <= maxPrice)) {
            property->base.propertyId = id;
            property->base.municipalityDistrict = municipality_district;
            strcpy(property->base.address, address);
            strcpy(property->base.ownerPhoneNumber, owner_phone);
            strcpy(property->landType, land_type);
            strcpy(property->base.registrationDate, reg_date);
            strcpy(property->base.deleteDate, del_date);
            property->base.isActive = is_active;
            strcpy(property->base.registeredBy, reg_by);
            property->base.dealType = dealType;
            
            property->landArea = land_area;
            property->distanceToMainRoad = distance_to_road;
            property->hasWell = has_well;
            property->sellingPrice = selling_price;
            property->mortgageAmount = mortgage_amount;
            property->monthlyRentAmount = monthly_rent;
            
            index++;
        }
    }
    
    fclose(file);
    *count = index;
    
    snprintf(log_message, sizeof(log_message), 
             "Land property search by price range %.2f-%.2f: found %d properties", 
             minPrice, maxPrice == 0 ? 999999999.99 : maxPrice, index);
    property_log("INFO", log_message);
    
    return results;
}

LandProperty* land_find_by_type(const char* landType, PropertyDealType dealType, int* count) {
    char filename[256];
    char log_message[256];
    LandProperty* results = NULL;
    *count = 0;
    
    // بررسی پارامترهای ورودی
    if (!landType || strlen(landType) == 0) {
        property_log("ERROR", "Invalid land type for land property search");
        return NULL;
    }
    
    // انتخاب فایل بر اساس نوع معامله
    if (dealType == PROPERTY_DEAL_SALE) {
        strcpy(filename, LAND_SALES_PATH);
    } else if (dealType == PROPERTY_DEAL_RENT) {
        strcpy(filename, LAND_RENTALS_PATH);
    } else {
        property_log("ERROR", "Invalid deal type for type-based land property search");
        return NULL;
    }
    
    // باز کردن فایل
    FILE* file = fopen(filename, "r");
    if (!file) {
        snprintf(log_message, sizeof(log_message), 
                 "Error opening file for type-based land property search");
        property_log("ERROR", log_message);
        return NULL;
    }
    
    // شمارش تعداد زمین‌های واجد شرایط
    char line[1024];
    int match_count = 0;
    
    while (fgets(line, sizeof(line), file)) {
        int id, municipality_district, is_active, has_well, timestamp;
        float land_area, distance_to_road;
        double selling_price, mortgage_amount, monthly_rent;
        char address[100], owner_phone[20], land_type[20], reg_date[11], del_date[11], 
             reg_by[50], deal_type[10], status[20];
        
        // خواندن داده‌ها از خط فایل
        sscanf(line, "%d,%d,%[^,],%[^,],%[^,],%[^,],%d,%[^,],%[^,],%f,%f,%d,%lf,%lf,%lf,%[^,],%[^,],%d,%s",
               &id, &municipality_district, address, owner_phone, land_type, reg_date, 
               &is_active, del_date, reg_by, &land_area, &distance_to_road, &has_well,
               &selling_price, &mortgage_amount, &monthly_rent, deal_type, &timestamp, status);
        
        // بررسی فعال بودن زمین و تطابق با نوع زمین (بدون توجه به حروف بزرگ و کوچک)
        if (is_active == PROPERTY_STATUS_ACTIVE && 
            strcasecmp(land_type, landType) == 0) {
            match_count++;
        }
    }
    
    // اگر هیچ موردی پیدا نشد
    if (match_count == 0) {
        fclose(file);
        return NULL;
    }
    
    // تخصیص حافظه برای نتایج
    results = (LandProperty*)malloc(match_count * sizeof(LandProperty));
    if (!results) {
        property_log("ERROR", "Memory allocation error in type-based land property search");
        fclose(file);
        return NULL;
    }
    
    // بازگشت به ابتدای فایل
    rewind(file);
    
    // خواندن و ذخیره زمین‌های واجد شرایط
    int index = 0;
    while (fgets(line, sizeof(line), file) && index < match_count) {
        LandProperty* property = &results[index];
        int id, municipality_district, is_active, has_well, timestamp;
        float land_area, distance_to_road;
        double selling_price, mortgage_amount, monthly_rent;
        char address[100], owner_phone[20], land_type[20], reg_date[11], del_date[11], 
             reg_by[50], deal_type[10], status[20];
        
        // خواندن داده‌ها از خط فایل
        sscanf(line, "%d,%d,%[^,],%[^,],%[^,],%[^,],%d,%[^,],%[^,],%f,%f,%d,%lf,%lf,%lf,%[^,],%[^,],%d,%s",
               &id, &municipality_district, address, owner_phone, land_type, reg_date, 
               &is_active, del_date, reg_by, &land_area, &distance_to_road, &has_well,
               &selling_price, &mortgage_amount, &monthly_rent, deal_type, &timestamp, status);
        
        // بررسی فعال بودن زمین و تطابق با نوع زمین (بدون توجه به حروف بزرگ و کوچک)
        if (is_active == PROPERTY_STATUS_ACTIVE && 
            strcasecmp(land_type, landType) == 0) {
            property->base.propertyId = id;
            property->base.municipalityDistrict = municipality_district;
            strcpy(property->base.address, address);
            strcpy(property->base.ownerPhoneNumber, owner_phone);
            strcpy(property->landType, land_type);
            strcpy(property->base.registrationDate, reg_date);
            strcpy(property->base.deleteDate, del_date);
            property->base.isActive = is_active;
            strcpy(property->base.registeredBy, reg_by);
            property->base.dealType = dealType;
            
            property->landArea = land_area;
            property->distanceToMainRoad = distance_to_road;
            property->hasWell = has_well;
            property->sellingPrice = selling_price;
            property->mortgageAmount = mortgage_amount;
            property->monthlyRentAmount = monthly_rent;
            
            index++;
        }
    }
    
    fclose(file);
    *count = index;
    
    snprintf(log_message, sizeof(log_message), 
             "Land property search by type '%s': found %d properties", landType, index);
    property_log("INFO", log_message);
    
    return results;
}

LandProperty* land_find_by_distance(float maxDistance, PropertyDealType dealType, int* count) {
    char filename[256];
    char log_message[256];
    LandProperty* results = NULL;
    *count = 0;
    
    // بررسی پارامترهای ورودی
    if (maxDistance < 0) {
        property_log("ERROR", "Invalid max distance for land property search");
        return NULL;
    }
    
    // انتخاب فایل بر اساس نوع معامله
    if (dealType == PROPERTY_DEAL_SALE) {
        strcpy(filename, LAND_SALES_PATH);
    } else if (dealType == PROPERTY_DEAL_RENT) {
        strcpy(filename, LAND_RENTALS_PATH);
    } else {
        property_log("ERROR", "Invalid deal type for distance-based land property search");
        return NULL;
    }
    
    // باز کردن فایل
    FILE* file = fopen(filename, "r");
    if (!file) {
        snprintf(log_message, sizeof(log_message), 
                 "Error opening file for distance-based land property search");
        property_log("ERROR", log_message);
        return NULL;
    }
    
    // شمارش تعداد زمین‌های واجد شرایط
    char line[1024];
    int match_count = 0;
    
    while (fgets(line, sizeof(line), file)) {
        int id, municipality_district, is_active, has_well, timestamp;
        float land_area, distance_to_road;
        double selling_price, mortgage_amount, monthly_rent;
        char address[100], owner_phone[20], land_type[20], reg_date[11], del_date[11], 
             reg_by[50], deal_type[10], status[20];
        
        // خواندن داده‌ها از خط فایل
        sscanf(line, "%d,%d,%[^,],%[^,],%[^,],%[^,],%d,%[^,],%[^,],%f,%f,%d,%lf,%lf,%lf,%[^,],%[^,],%d,%s",
               &id, &municipality_district, address, owner_phone, land_type, reg_date, 
               &is_active, del_date, reg_by, &land_area, &distance_to_road, &has_well,
               &selling_price, &mortgage_amount, &monthly_rent, deal_type, &timestamp, status);
        
        // بررسی فعال بودن زمین و فاصله تا جاده اصلی
        if (is_active == PROPERTY_STATUS_ACTIVE && 
            distance_to_road <= maxDistance) {
            match_count++;
        }
    }
    
    // اگر هیچ موردی پیدا نشد
    if (match_count == 0) {
        fclose(file);
        return NULL;
    }
    
    // تخصیص حافظه برای نتایج
    results = (LandProperty*)malloc(match_count * sizeof(LandProperty));
    if (!results) {
        property_log("ERROR", "Memory allocation error in distance-based land property search");
        fclose(file);
        return NULL;
    }
    
    // بازگشت به ابتدای فایل
    rewind(file);
    
    // خواندن و ذخیره زمین‌های واجد شرایط
    int index = 0;
    while (fgets(line, sizeof(line), file) && index < match_count) {
        LandProperty* property = &results[index];
        int id, municipality_district, is_active, has_well, timestamp;
        float land_area, distance_to_road;
        double selling_price, mortgage_amount, monthly_rent;
        char address[100], owner_phone[20], land_type[20], reg_date[11], del_date[11], 
             reg_by[50], deal_type[10], status[20];
        
        // خواندن داده‌ها از خط فایل
        sscanf(line, "%d,%d,%[^,],%[^,],%[^,],%[^,],%d,%[^,],%[^,],%f,%f,%d,%lf,%lf,%lf,%[^,],%[^,],%d,%s",
               &id, &municipality_district, address, owner_phone, land_type, reg_date, 
               &is_active, del_date, reg_by, &land_area, &distance_to_road, &has_well,
               &selling_price, &mortgage_amount, &monthly_rent, deal_type, &timestamp, status);
        
        // بررسی فعال بودن زمین و فاصله تا جاده اصلی
        if (is_active == PROPERTY_STATUS_ACTIVE && 
            distance_to_road <= maxDistance) {
            property->base.propertyId = id;
            property->base.municipalityDistrict = municipality_district;
            strcpy(property->base.address, address);
            strcpy(property->base.ownerPhoneNumber, owner_phone);
            strcpy(property->landType, land_type);
            strcpy(property->base.registrationDate, reg_date);
            strcpy(property->base.deleteDate, del_date);
            property->base.isActive = is_active;
            strcpy(property->base.registeredBy, reg_by);
            property->base.dealType = dealType;
            
            property->landArea = land_area;
            property->distanceToMainRoad = distance_to_road;
            property->hasWell = has_well;
            property->sellingPrice = selling_price;
            property->mortgageAmount = mortgage_amount;
            property->monthlyRentAmount = monthly_rent;
            
            index++;
        }
    }
    
    fclose(file);
    *count = index;
    
    snprintf(log_message, sizeof(log_message), 
             "Land property search by max distance %.2f: found %d properties", 
             maxDistance, index);
    property_log("INFO", log_message);
    
    return results;
}

LandProperty* land_find_with_well(PropertyDealType dealType, int* count) {
    char filename[256];
    char log_message[256];
    LandProperty* results = NULL;
    *count = 0;
    
    // انتخاب فایل بر اساس نوع معامله
    if (dealType == PROPERTY_DEAL_SALE) {
        strcpy(filename, LAND_SALES_PATH);
    } else if (dealType == PROPERTY_DEAL_RENT) {
        strcpy(filename, LAND_RENTALS_PATH);
    } else {
        property_log("ERROR", "Invalid deal type for well-based land property search");
        return NULL;
    }
    
    // باز کردن فایل
    FILE* file = fopen(filename, "r");
    if (!file) {
        snprintf(log_message, sizeof(log_message), 
                 "Error opening file for well-based land property search");
        property_log("ERROR", log_message);
        return NULL;
    }
    
    // شمارش تعداد زمین‌های واجد شرایط
    char line[1024];
    int match_count = 0;
    
    while (fgets(line, sizeof(line), file)) {
        int id, municipality_district, is_active, has_well, timestamp;
        float land_area, distance_to_road;
        double selling_price, mortgage_amount, monthly_rent;
        char address[100], owner_phone[20], land_type[20], reg_date[11], del_date[11], 
             reg_by[50], deal_type[10], status[20];
        
        // خواندن داده‌ها از خط فایل
        sscanf(line, "%d,%d,%[^,],%[^,],%[^,],%[^,],%d,%[^,],%[^,],%f,%f,%d,%lf,%lf,%lf,%[^,],%[^,],%d,%s",
               &id, &municipality_district, address, owner_phone, land_type, reg_date, 
               &is_active, del_date, reg_by, &land_area, &distance_to_road, &has_well,
               &selling_price, &mortgage_amount, &monthly_rent, deal_type, &timestamp, status);
        
        // بررسی فعال بودن زمین و داشتن چاه
        if (is_active == PROPERTY_STATUS_ACTIVE && has_well == 1) {
            match_count++;
        }
    }
    
    // اگر هیچ موردی پیدا نشد
    if (match_count == 0) {
        fclose(file);
        return NULL;
    }
    
    // تخصیص حافظه برای نتایج
    results = (LandProperty*)malloc(match_count * sizeof(LandProperty));
    if (!results) {
        property_log("ERROR", "Memory allocation error in well-based land property search");
        fclose(file);
        return NULL;
    }
    
    // بازگشت به ابتدای فایل
    rewind(file);
    
    // خواندن و ذخیره زمین‌های واجد شرایط
    int index = 0;
    while (fgets(line, sizeof(line), file) && index < match_count) {
        LandProperty* property = &results[index];
        int id, municipality_district, is_active, has_well, timestamp;
        float land_area, distance_to_road;
        double selling_price, mortgage_amount, monthly_rent;
        char address[100], owner_phone[20], land_type[20], reg_date[11], del_date[11], 
             reg_by[50], deal_type[10], status[20];
        
        // خواندن داده‌ها از خط فایل
        sscanf(line, "%d,%d,%[^,],%[^,],%[^,],%[^,],%d,%[^,],%[^,],%f,%f,%d,%lf,%lf,%lf,%[^,],%[^,],%d,%s",
               &id, &municipality_district, address, owner_phone, land_type, reg_date, 
               &is_active, del_date, reg_by, &land_area, &distance_to_road, &has_well,
               &selling_price, &mortgage_amount, &monthly_rent, deal_type, &timestamp, status);
        
        // بررسی فعال بودن زمین و داشتن چاه
        if (is_active == PROPERTY_STATUS_ACTIVE && has_well == 1) {
            property->base.propertyId = id;
            property->base.municipalityDistrict = municipality_district;
            strcpy(property->base.address, address);
            strcpy(property->base.ownerPhoneNumber, owner_phone);
            strcpy(property->landType, land_type);
            strcpy(property->base.registrationDate, reg_date);
            strcpy(property->base.deleteDate, del_date);
            property->base.isActive = is_active;
            strcpy(property->base.registeredBy, reg_by);
            property->base.dealType = dealType;
            
            property->landArea = land_area;
            property->distanceToMainRoad = distance_to_road;
            property->hasWell = has_well;
            property->sellingPrice = selling_price;
            property->mortgageAmount = mortgage_amount;
            property->monthlyRentAmount = monthly_rent;
            
            index++;
        }
    }
    
    fclose(file);
    *count = index;
    
    snprintf(log_message, sizeof(log_message), 
             "Land property search with well: found %d properties", index);
    property_log("INFO", log_message);
    
    return results;
}

LandProperty* land_find_deleted_by_date(const char* startDate, 
                                       const char* endDate, 
                                       PropertyDealType dealType, 
                                       int* count) {
    char filename[256];
    char log_message[256];
    LandProperty* results = NULL;
    *count = 0;
    
    // بررسی پارامترهای ورودی
    if (!startDate || !endDate || strlen(startDate) != 10 || strlen(endDate) != 10) {
        property_log("ERROR", "Invalid date format for deleted land property search");
        return NULL;
    }
    
    // انتخاب فایل بر اساس نوع معامله
    if (dealType == PROPERTY_DEAL_SALE) {
        strcpy(filename, LAND_SALES_PATH);
    } else if (dealType == PROPERTY_DEAL_RENT) {
        strcpy(filename, LAND_RENTALS_PATH);
    } else {
        property_log("ERROR", "Invalid deal type for deleted land property search");
        return NULL;
    }
    
    // باز کردن فایل
    FILE* file = fopen(filename, "r");
    if (!file) {
        snprintf(log_message, sizeof(log_message), 
                 "Error opening file for deleted land property search");
        property_log("ERROR", log_message);
        return NULL;
    }
    
    // شمارش تعداد زمین‌های واجد شرایط
    char line[1024];
    int match_count = 0;
    
    while (fgets(line, sizeof(line), file)) {
        int id, municipality_district, is_active, has_well, timestamp;
        float land_area, distance_to_road;
        double selling_price, mortgage_amount, monthly_rent;
        char address[100], owner_phone[20], land_type[20], reg_date[11], del_date[11], 
             reg_by[50], deal_type[10], status[20];
        
        // خواندن داده‌ها از خط فایل
        sscanf(line, "%d,%d,%[^,],%[^,],%[^,],%[^,],%d,%[^,],%[^,],%f,%f,%d,%lf,%lf,%lf,%[^,],%[^,],%d,%s",
               &id, &municipality_district, address, owner_phone, land_type, reg_date, 
               &is_active, del_date, reg_by, &land_area, &distance_to_road, &has_well,
               &selling_price, &mortgage_amount, &monthly_rent, deal_type, &timestamp, status);
        
        // بررسی غیرفعال بودن زمین و تطابق تاریخ حذف با محدوده
        if (is_active == PROPERTY_STATUS_DELETED && 
            strlen(del_date) == 10 &&
            strcmp(del_date, startDate) >= 0 && 
            strcmp(del_date, endDate) <= 0) {
            match_count++;
        }
    }
    
    // اگر هیچ موردی پیدا نشد
    if (match_count == 0) {
        fclose(file);
        return NULL;
    }
    
    // تخصیص حافظه برای نتایج
    results = (LandProperty*)malloc(match_count * sizeof(LandProperty));
    if (!results) {
        property_log("ERROR", "Memory allocation error in deleted land property search");
        fclose(file);
        return NULL;
    }
    
    // بازگشت به ابتدای فایل
    rewind(file);
    
    // خواندن و ذخیره زمین‌های واجد شرایط
    int index = 0;
    while (fgets(line, sizeof(line), file) && index < match_count) {
        LandProperty* property = &results[index];
        int id, municipality_district, is_active, has_well, timestamp;
        float land_area, distance_to_road;
        double selling_price, mortgage_amount, monthly_rent;
        char address[100], owner_phone[20], land_type[20], reg_date[11], del_date[11], 
             reg_by[50], deal_type[10], status[20];
        
        // خواندن داده‌ها از خط فایل
        sscanf(line, "%d,%d,%[^,],%[^,],%[^,],%[^,],%d,%[^,],%[^,],%f,%f,%d,%lf,%lf,%lf,%[^,],%[^,],%d,%s",
               &id, &municipality_district, address, owner_phone, land_type, reg_date, 
               &is_active, del_date, reg_by, &land_area, &distance_to_road, &has_well,
               &selling_price, &mortgage_amount, &monthly_rent, deal_type, &timestamp, status);
        
        // بررسی غیرفعال بودن زمین و تطابق تاریخ حذف با محدوده
        if (is_active == PROPERTY_STATUS_DELETED && 
            strlen(del_date) == 10 &&
            strcmp(del_date, startDate) >= 0 && 
            strcmp(del_date, endDate) <= 0) {
            property->base.propertyId = id;
            property->base.municipalityDistrict = municipality_district;
            strcpy(property->base.address, address);
            strcpy(property->base.ownerPhoneNumber, owner_phone);
            strcpy(property->landType, land_type);
            strcpy(property->base.registrationDate, reg_date);
            strcpy(property->base.deleteDate, del_date);
            property->base.isActive = is_active;
            strcpy(property->base.registeredBy, reg_by);
            property->base.dealType = dealType;
            
            property->landArea = land_area;
            property->distanceToMainRoad = distance_to_road;
            property->hasWell = has_well;
            property->sellingPrice = selling_price;
            property->mortgageAmount = mortgage_amount;
            property->monthlyRentAmount = monthly_rent;
            
            index++;
        }
    }
    
    fclose(file);
    *count = index;
    
    snprintf(log_message, sizeof(log_message), 
             "Deleted land property search between %s and %s: found %d properties", 
             startDate, endDate, index);
    property_log("INFO", log_message);
    
    return results;
}

LandProperty* land_find_by_user(const char* username, PropertyDealType dealType, int* count) {
    char filename[256];
    char log_message[256];
    LandProperty* results = NULL;
    *count = 0;
    
    // بررسی پارامترهای ورودی
    if (!username || strlen(username) == 0) {
        property_log("ERROR", "Invalid username for land property search");
        return NULL;
    }
    
    // انتخاب فایل بر اساس نوع معامله
    if (dealType == PROPERTY_DEAL_SALE) {
        strcpy(filename, LAND_SALES_PATH);
    } else if (dealType == PROPERTY_DEAL_RENT) {
        strcpy(filename, LAND_RENTALS_PATH);
    } else {
        property_log("ERROR", "Invalid deal type for user-based land property search");
        return NULL;
    }
    
    // باز کردن فایل
    FILE* file = fopen(filename, "r");
    if (!file) {
        snprintf(log_message, sizeof(log_message), 
                 "Error opening file for user-based land property search");
        property_log("ERROR", log_message);
        return NULL;
    }
    
    // شمارش تعداد زمین‌های واجد شرایط
    char line[1024];
    int match_count = 0;
    
    while (fgets(line, sizeof(line), file)) {
        int id, municipality_district, is_active, has_well, timestamp;
        float land_area, distance_to_road;
        double selling_price, mortgage_amount, monthly_rent;
        char address[100], owner_phone[20], land_type[20], reg_date[11], del_date[11], 
             reg_by[50], deal_type[10], status[20];
        
        // خواندن داده‌ها از خط فایل
        sscanf(line, "%d,%d,%[^,],%[^,],%[^,],%[^,],%d,%[^,],%[^,],%f,%f,%d,%lf,%lf,%lf,%[^,],%[^,],%d,%s",
               &id, &municipality_district, address, owner_phone, land_type, reg_date, 
               &is_active, del_date, reg_by, &land_area, &distance_to_road, &has_well,
               &selling_price, &mortgage_amount, &monthly_rent, deal_type, &timestamp, status);
        
        // بررسی ثبت کننده زمین (بدون توجه به حروف بزرگ و کوچک)
        if (strcasecmp(reg_by, username) == 0) {
            match_count++;
        }
    }
    
    // اگر هیچ موردی پیدا نشد
    if (match_count == 0) {
        fclose(file);
        return NULL;
    }
    
    // تخصیص حافظه برای نتایج
    results = (LandProperty*)malloc(match_count * sizeof(LandProperty));
    if (!results) {
        property_log("ERROR", "Memory allocation error in user-based land property search");
        fclose(file);
        return NULL;
    }
    
    // بازگشت به ابتدای فایل
    rewind(file);
    
    // خواندن و ذخیره زمین‌های واجد شرایط
    int index = 0;
    while (fgets(line, sizeof(line), file) && index < match_count) {
        LandProperty* property = &results[index];
        int id, municipality_district, is_active, has_well, timestamp;
        float land_area, distance_to_road;
        double selling_price, mortgage_amount, monthly_rent;
        char address[100], owner_phone[20], land_type[20], reg_date[11], del_date[11], 
             reg_by[50], deal_type[10], status[20];
        
        // خواندن داده‌ها از خط فایل
        sscanf(line, "%d,%d,%[^,],%[^,],%[^,],%[^,],%d,%[^,],%[^,],%f,%f,%d,%lf,%lf,%lf,%[^,],%[^,],%d,%s",
               &id, &municipality_district, address, owner_phone, land_type, reg_date, 
               &is_active, del_date, reg_by, &land_area, &distance_to_road, &has_well,
               &selling_price, &mortgage_amount, &monthly_rent, deal_type, &timestamp, status);
        
        // بررسی ثبت کننده زمین (بدون توجه به حروف بزرگ و کوچک)
        if (strcasecmp(reg_by, username) == 0) {
            property->base.propertyId = id;
            property->base.municipalityDistrict = municipality_district;
            strcpy(property->base.address, address);
            strcpy(property->base.ownerPhoneNumber, owner_phone);
            strcpy(property->landType, land_type);
            strcpy(property->base.registrationDate, reg_date);
            strcpy(property->base.deleteDate, del_date);
            property->base.isActive = is_active;
            strcpy(property->base.registeredBy, reg_by);
            property->base.dealType = dealType;
            
            property->landArea = land_area;
            property->distanceToMainRoad = distance_to_road;
            property->hasWell = has_well;
            property->sellingPrice = selling_price;
            property->mortgageAmount = mortgage_amount;
            property->monthlyRentAmount = monthly_rent;
            
            index++;
        }
    }
    
    fclose(file);
    *count = index;
    
    snprintf(log_message, sizeof(log_message), 
             "Land property search by user '%s': found %d properties", username, index);
    property_log("INFO", log_message);
    
    return results;
}

double land_calculate_total_value(void) {
    FILE* file;
    char log_message[256];
    double total_value = 0.0;
    
    // باز کردن فایل فروش زمین
    file = fopen(LAND_SALES_PATH, "r");
    if (!file) {
        property_log("ERROR", "Failed to open land sales file for total value calculation");
        return 0.0;
    }
    
    // خواندن خطوط فایل و محاسبه ارزش کل
    char line[1024];
    
    while (fgets(line, sizeof(line), file)) {
        int id, municipality_district, is_active, has_well, timestamp;
        float land_area, distance_to_road;
        double selling_price, mortgage_amount, monthly_rent;
        char address[100], owner_phone[20], land_type[20], reg_date[11], del_date[11], 
             reg_by[50], deal_type[10], status[20];
        
        // خواندن داده‌ها از خط فایل
        sscanf(line, "%d,%d,%[^,],%[^,],%[^,],%[^,],%d,%[^,],%[^,],%f,%f,%d,%lf,%lf,%lf,%[^,],%[^,],%d,%s",
               &id, &municipality_district, address, owner_phone, land_type, reg_date, 
               &is_active, del_date, reg_by, &land_area, &distance_to_road, &has_well,
               &selling_price, &mortgage_amount, &monthly_rent, deal_type, &timestamp, status);
        
        // فقط برای زمین‌های فعال، قیمت فروش را به مجموع اضافه می‌کنیم
        if (is_active == PROPERTY_STATUS_ACTIVE) {
            total_value += selling_price;
        }
    }
    
    fclose(file);
    
    // ثبت گزارش در فایل لاگ
    snprintf(log_message, sizeof(log_message), 
             "Total value of active land properties for sale: %.2f", total_value);
    property_log("INFO", log_message);
    
    return total_value;
}

void land_free_array(LandProperty* array) {
    if (array) {
        free(array);
        property_log("INFO", "Land property array memory freed");
    }
} 