/**
 * @file commercial.c
 * @brief پیاده‌سازی توابع مدیریت املاک تجاری
 */

#include "../include/commercial.h"
#include "../include/property_lib.h"
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <time.h>

// مسیرهای فایل برای ذخیره املاک تجاری
#define COMMERCIAL_SALES_PATH "data/commercial_sales.csv"
#define COMMERCIAL_RENTALS_PATH "data/commercial_rentals.csv"

// متغیر جهانی برای مسیر پایه داده
static char data_path_base[256] = "./";

/**
 * @brief تنظیم مسیر پایه برای فایل‌های داده
 * 
 * @param base_path مسیر پایه
 */
void commercial_set_data_path(const char* base_path) {
    if (base_path) {
        strncpy(data_path_base, base_path, sizeof(data_path_base) - 1);
        data_path_base[sizeof(data_path_base) - 1] = '\0';
    }
}

/**
 * @brief اعتبارسنجی داده‌های ملک تجاری
 * 
 * @param property اطلاعات ملک تجاری
 * @return int کد خطا: 0 (معتبر)، 1 (نامعتبر)
 */
static int validate_commercial_property(CommercialProperty* property) {
    if (!property) {
        property_log("ERROR", "Invalid commercial property (NULL)");
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
    
    if (property->areaSize <= 0) {
        property_log("ERROR", "Invalid area size");
        return 1;
    }
    
    if (property->landArea < 0) {
        property_log("ERROR", "Invalid land area");
        return 1;
    }
    
    if (property->officeRooms < 0) {
        property_log("ERROR", "Invalid number of office rooms");
        return 1;
    }
    
    if (property->buildingAge < 0) {
        property_log("ERROR", "Invalid building age");
        return 1;
    }
    
    return 0;
}

int commercial_register_sale(CommercialProperty* property, const char* username) {
    char log_message[256];
    FILE* file;
    time_t now = time(NULL);
    
    // اعتبارسنجی ورودی‌ها
    if (!property || !username || strlen(username) == 0) {
        property_log("ERROR", "Invalid parameters for commercial property registration");
        return 1;
    }
    
    // اعتبارسنجی اطلاعات ملک
    if (validate_commercial_property(property)) {
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
    file = fopen(COMMERCIAL_SALES_PATH, "a");
    if (!file) {
        property_log("ERROR", "Failed to open commercial sales file for writing");
        return 2;
    }
    
    // نوشتن داده در فایل CSV
    fprintf(file, "%d,%d,%s,%s,%d,%s,%s,%d,%f,%d,%f,%d,%s,%lf,0.0,0.0,%s,%s,%ld,%s\n",
            property->base.propertyId,
            property->base.municipalityDistrict,
            property->base.address,
            property->base.ownerPhoneNumber,
            property->buildingAge,
            property->base.registrationDate,
            property->base.deleteDate,
            property->base.isActive,
            property->areaSize,
            property->floor,
            property->landArea,
            property->officeRooms,
            property->propertyType,
            property->sellingPrice,
            property->base.registeredBy,
            "SALE",
            (long)now,
            "OK");
    
    fclose(file);
    
    // افزایش شمارنده املاک
    int current_count = property_get_count();
    property_update_count(current_count + 1);
    
    // ثبت گزارش در فایل لاگ
    snprintf(log_message, sizeof(log_message), 
             "Commercial property registered for sale - ID: %d, by: %s", 
             property->base.propertyId, username);
    property_log("INFO", log_message);
    
    return 0;
}

int commercial_register_rental(CommercialProperty* property, const char* username) {
    char log_message[256];
    FILE* file;
    time_t now = time(NULL);
    
    // اعتبارسنجی ورودی‌ها
    if (!property || !username || strlen(username) == 0) {
        property_log("ERROR", "Invalid parameters for commercial property rental registration");
        return 1;
    }
    
    // اعتبارسنجی اطلاعات ملک
    if (validate_commercial_property(property)) {
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
    file = fopen(COMMERCIAL_RENTALS_PATH, "a");
    if (!file) {
        property_log("ERROR", "Failed to open commercial rentals file for writing");
        return 2;
    }
    
    // نوشتن داده در فایل CSV
    fprintf(file, "%d,%d,%s,%s,%d,%s,%s,%d,%f,%d,%f,%d,%s,0.0,%lf,%lf,%s,%s,%ld,%s\n",
            property->base.propertyId,
            property->base.municipalityDistrict,
            property->base.address,
            property->base.ownerPhoneNumber,
            property->buildingAge,
            property->base.registrationDate,
            property->base.deleteDate,
            property->base.isActive,
            property->areaSize,
            property->floor,
            property->landArea,
            property->officeRooms,
            property->propertyType,
            property->mortgageAmount,
            property->monthlyRentAmount,
            property->base.registeredBy,
            "RENT",
            (long)now,
            "OK");
    
    fclose(file);
    
    // افزایش شمارنده املاک
    int current_count = property_get_count();
    property_update_count(current_count + 1);
    
    // ثبت گزارش در فایل لاگ
    snprintf(log_message, sizeof(log_message), 
             "Commercial property registered for rent - ID: %d, by: %s", 
             property->base.propertyId, username);
    property_log("INFO", log_message);
    
    return 0;
}

CommercialProperty* commercial_find_by_district(int district, PropertyDealType dealType, int* count) {
    char filename[256];
    char log_message[256];
    CommercialProperty* results = NULL;
    *count = 0;
    
    // انتخاب فایل بر اساس نوع معامله
    if (dealType == PROPERTY_DEAL_SALE) {
        strcpy(filename, COMMERCIAL_SALES_PATH);
    } else if (dealType == PROPERTY_DEAL_RENT) {
        strcpy(filename, COMMERCIAL_RENTALS_PATH);
    } else {
        property_log("ERROR", "Invalid deal type for district-based commercial property search");
        return NULL;
    }
    
    // باز کردن فایل
    FILE* file = fopen(filename, "r");
    if (!file) {
        snprintf(log_message, sizeof(log_message), 
                 "Error opening file for district-based commercial property search");
        property_log("ERROR", log_message);
        return NULL;
    }
    
    // شمارش تعداد املاک واجد شرایط
    char line[1024];
    int match_count = 0;
    
    while (fgets(line, sizeof(line), file)) {
        int id, municipality_district, is_active, building_age, floor, office_rooms, timestamp;
        float area_size, land_area;
        double selling_price, mortgage_amount, monthly_rent;
        char address[100], owner_phone[20], reg_date[11], del_date[11], property_type[20], 
             reg_by[50], deal_type[10], status[20];
        
        // خواندن داده‌ها از خط فایل
        sscanf(line, "%d,%d,%[^,],%[^,],%d,%[^,],%[^,],%d,%f,%d,%f,%d,%[^,],%lf,%lf,%lf,%[^,],%[^,],%d,%s",
               &id, &municipality_district, address, owner_phone, &building_age, reg_date, del_date, 
               &is_active, &area_size, &floor, &land_area, &office_rooms, property_type,
               &selling_price, &mortgage_amount, &monthly_rent, reg_by, deal_type, &timestamp, status);
        
        // بررسی فعال بودن ملک و تطابق با منطقه مورد نظر (یا همه مناطق)
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
    results = (CommercialProperty*)malloc(match_count * sizeof(CommercialProperty));
    if (!results) {
        property_log("ERROR", "Memory allocation error in district-based commercial property search");
        fclose(file);
        return NULL;
    }
    
    // بازگشت به ابتدای فایل
    rewind(file);
    
    // خواندن و ذخیره املاک واجد شرایط
    int index = 0;
    while (fgets(line, sizeof(line), file) && index < match_count) {
        CommercialProperty* property = &results[index];
        int id, municipality_district, is_active, building_age, floor, office_rooms, timestamp;
        float area_size, land_area;
        double selling_price, mortgage_amount, monthly_rent;
        char address[100], owner_phone[20], reg_date[11], del_date[11], property_type[20], 
             reg_by[50], deal_type[10], status[20];
        
        // خواندن داده‌ها از خط فایل
        sscanf(line, "%d,%d,%[^,],%[^,],%d,%[^,],%[^,],%d,%f,%d,%f,%d,%[^,],%lf,%lf,%lf,%[^,],%[^,],%d,%s",
               &id, &municipality_district, address, owner_phone, &building_age, reg_date, del_date, 
               &is_active, &area_size, &floor, &land_area, &office_rooms, property_type,
               &selling_price, &mortgage_amount, &monthly_rent, reg_by, deal_type, &timestamp, status);
        
        // بررسی فعال بودن ملک و تطابق با منطقه مورد نظر (یا همه مناطق)
        if (is_active == PROPERTY_STATUS_ACTIVE && 
            (district == 0 || municipality_district == district)) {
            property->base.propertyId = id;
            property->base.municipalityDistrict = municipality_district;
            strcpy(property->base.address, address);
            strcpy(property->base.ownerPhoneNumber, owner_phone);
            strcpy(property->base.registrationDate, reg_date);
            strcpy(property->base.deleteDate, del_date);
            property->base.isActive = is_active;
            strcpy(property->base.registeredBy, reg_by);
            property->base.dealType = dealType;
            
            property->buildingAge = building_age;
            property->areaSize = area_size;
            property->floor = floor;
            property->landArea = land_area;
            property->officeRooms = office_rooms;
            strcpy(property->propertyType, property_type);
            property->sellingPrice = selling_price;
            property->mortgageAmount = mortgage_amount;
            property->monthlyRentAmount = monthly_rent;
            
            index++;
        }
    }
    
    fclose(file);
    *count = index;
    
    snprintf(log_message, sizeof(log_message), 
             "Commercial property search by district %d: found %d properties", district, index);
    property_log("INFO", log_message);
    
    return results;
}

CommercialProperty* commercial_find_by_age(int minAge, int maxAge, PropertyDealType dealType, int* count) {
    char filename[256];
    char log_message[256];
    CommercialProperty* results = NULL;
    *count = 0;
    
    // بررسی پارامترهای ورودی
    if (minAge < 0 || (maxAge > 0 && maxAge < minAge)) {
        property_log("ERROR", "Invalid age range for commercial property search");
        return NULL;
    }
    
    // انتخاب فایل بر اساس نوع معامله
    if (dealType == PROPERTY_DEAL_SALE) {
        strcpy(filename, COMMERCIAL_SALES_PATH);
    } else if (dealType == PROPERTY_DEAL_RENT) {
        strcpy(filename, COMMERCIAL_RENTALS_PATH);
    } else {
        property_log("ERROR", "Invalid deal type for age-based commercial property search");
        return NULL;
    }
    
    // باز کردن فایل
    FILE* file = fopen(filename, "r");
    if (!file) {
        snprintf(log_message, sizeof(log_message), 
                 "Error opening file for age-based commercial property search");
        property_log("ERROR", log_message);
        return NULL;
    }
    
    // شمارش تعداد املاک واجد شرایط
    char line[1024];
    int match_count = 0;
    
    while (fgets(line, sizeof(line), file)) {
        int id, municipality_district, is_active, building_age, floor, office_rooms, timestamp;
        float area_size, land_area;
        double selling_price, mortgage_amount, monthly_rent;
        char address[100], owner_phone[20], reg_date[11], del_date[11], property_type[20], 
             reg_by[50], deal_type[10], status[20];
        
        // خواندن داده‌ها از خط فایل
        sscanf(line, "%d,%d,%[^,],%[^,],%d,%[^,],%[^,],%d,%f,%d,%f,%d,%[^,],%lf,%lf,%lf,%[^,],%[^,],%d,%s",
               &id, &municipality_district, address, owner_phone, &building_age, reg_date, del_date, 
               &is_active, &area_size, &floor, &land_area, &office_rooms, property_type,
               &selling_price, &mortgage_amount, &monthly_rent, reg_by, deal_type, &timestamp, status);
        
        // بررسی فعال بودن ملک و تطابق با محدوده سنی
        if (is_active == PROPERTY_STATUS_ACTIVE && 
            building_age >= minAge && 
            (maxAge == 0 || building_age <= maxAge)) {
            match_count++;
        }
    }
    
    // اگر هیچ موردی پیدا نشد
    if (match_count == 0) {
        fclose(file);
        return NULL;
    }
    
    // تخصیص حافظه برای نتایج
    results = (CommercialProperty*)malloc(match_count * sizeof(CommercialProperty));
    if (!results) {
        property_log("ERROR", "Memory allocation error in age-based commercial property search");
        fclose(file);
        return NULL;
    }
    
    // بازگشت به ابتدای فایل
    rewind(file);
    
    // خواندن و ذخیره املاک واجد شرایط
    int index = 0;
    while (fgets(line, sizeof(line), file) && index < match_count) {
        CommercialProperty* property = &results[index];
        int id, municipality_district, is_active, building_age, floor, office_rooms, timestamp;
        float area_size, land_area;
        double selling_price, mortgage_amount, monthly_rent;
        char address[100], owner_phone[20], reg_date[11], del_date[11], property_type[20], 
             reg_by[50], deal_type[10], status[20];
        
        // خواندن داده‌ها از خط فایل
        sscanf(line, "%d,%d,%[^,],%[^,],%d,%[^,],%[^,],%d,%f,%d,%f,%d,%[^,],%lf,%lf,%lf,%[^,],%[^,],%d,%s",
               &id, &municipality_district, address, owner_phone, &building_age, reg_date, del_date, 
               &is_active, &area_size, &floor, &land_area, &office_rooms, property_type,
               &selling_price, &mortgage_amount, &monthly_rent, reg_by, deal_type, &timestamp, status);
        
        // بررسی فعال بودن ملک و تطابق با محدوده سنی
        if (is_active == PROPERTY_STATUS_ACTIVE && 
            building_age >= minAge && 
            (maxAge == 0 || building_age <= maxAge)) {
            property->base.propertyId = id;
            property->base.municipalityDistrict = municipality_district;
            strcpy(property->base.address, address);
            strcpy(property->base.ownerPhoneNumber, owner_phone);
            strcpy(property->base.registrationDate, reg_date);
            strcpy(property->base.deleteDate, del_date);
            property->base.isActive = is_active;
            strcpy(property->base.registeredBy, reg_by);
            property->base.dealType = dealType;
            
            property->buildingAge = building_age;
            property->areaSize = area_size;
            property->floor = floor;
            property->landArea = land_area;
            property->officeRooms = office_rooms;
            strcpy(property->propertyType, property_type);
            property->sellingPrice = selling_price;
            property->mortgageAmount = mortgage_amount;
            property->monthlyRentAmount = monthly_rent;
            
            index++;
        }
    }
    
    fclose(file);
    *count = index;
    
    snprintf(log_message, sizeof(log_message), 
             "Commercial property search by age range %d-%s: found %d properties", 
             minAge, maxAge == 0 ? "any" : "max",  index);
    property_log("INFO", log_message);
    
    return results;
}

CommercialProperty* commercial_find_by_area(float minArea, float maxArea, PropertyDealType dealType, int* count) {
    char filename[256];
    char log_message[256];
    CommercialProperty* results = NULL;
    *count = 0;
    
    // بررسی پارامترهای ورودی
    if (minArea < 0 || (maxArea > 0 && maxArea < minArea)) {
        property_log("ERROR", "Invalid area range for commercial property search");
        return NULL;
    }
    
    // انتخاب فایل بر اساس نوع معامله
    if (dealType == PROPERTY_DEAL_SALE) {
        strcpy(filename, COMMERCIAL_SALES_PATH);
    } else if (dealType == PROPERTY_DEAL_RENT) {
        strcpy(filename, COMMERCIAL_RENTALS_PATH);
    } else {
        property_log("ERROR", "Invalid deal type for area-based commercial property search");
        return NULL;
    }
    
    // باز کردن فایل
    FILE* file = fopen(filename, "r");
    if (!file) {
        snprintf(log_message, sizeof(log_message), 
                 "Error opening file for area-based commercial property search");
        property_log("ERROR", log_message);
        return NULL;
    }
    
    // شمارش تعداد املاک واجد شرایط
    char line[1024];
    int match_count = 0;
    
    while (fgets(line, sizeof(line), file)) {
        int id, municipality_district, is_active, building_age, floor, office_rooms, timestamp;
        float area_size, land_area;
        double selling_price, mortgage_amount, monthly_rent;
        char address[100], owner_phone[20], reg_date[11], del_date[11], property_type[20], 
             reg_by[50], deal_type[10], status[20];
        
        // خواندن داده‌ها از خط فایل
        sscanf(line, "%d,%d,%[^,],%[^,],%d,%[^,],%[^,],%d,%f,%d,%f,%d,%[^,],%lf,%lf,%lf,%[^,],%[^,],%d,%s",
               &id, &municipality_district, address, owner_phone, &building_age, reg_date, del_date, 
               &is_active, &area_size, &floor, &land_area, &office_rooms, property_type,
               &selling_price, &mortgage_amount, &monthly_rent, reg_by, deal_type, &timestamp, status);
        
        // بررسی فعال بودن ملک و تطابق با محدوده مساحت
        if (is_active == PROPERTY_STATUS_ACTIVE && 
            area_size >= minArea && 
            (maxArea == 0 || area_size <= maxArea)) {
            match_count++;
        }
    }
    
    // اگر هیچ موردی پیدا نشد
    if (match_count == 0) {
        fclose(file);
        return NULL;
    }
    
    // تخصیص حافظه برای نتایج
    results = (CommercialProperty*)malloc(match_count * sizeof(CommercialProperty));
    if (!results) {
        property_log("ERROR", "Memory allocation error in area-based commercial property search");
        fclose(file);
        return NULL;
    }
    
    // بازگشت به ابتدای فایل
    rewind(file);
    
    // خواندن و ذخیره املاک واجد شرایط
    int index = 0;
    while (fgets(line, sizeof(line), file) && index < match_count) {
        CommercialProperty* property = &results[index];
        int id, municipality_district, is_active, building_age, floor, office_rooms, timestamp;
        float area_size, land_area;
        double selling_price, mortgage_amount, monthly_rent;
        char address[100], owner_phone[20], reg_date[11], del_date[11], property_type[20], 
             reg_by[50], deal_type[10], status[20];
        
        // خواندن داده‌ها از خط فایل
        sscanf(line, "%d,%d,%[^,],%[^,],%d,%[^,],%[^,],%d,%f,%d,%f,%d,%[^,],%lf,%lf,%lf,%[^,],%[^,],%d,%s",
               &id, &municipality_district, address, owner_phone, &building_age, reg_date, del_date, 
               &is_active, &area_size, &floor, &land_area, &office_rooms, property_type,
               &selling_price, &mortgage_amount, &monthly_rent, reg_by, deal_type, &timestamp, status);
        
        // بررسی فعال بودن ملک و تطابق با محدوده مساحت
        if (is_active == PROPERTY_STATUS_ACTIVE && 
            area_size >= minArea && 
            (maxArea == 0 || area_size <= maxArea)) {
            property->base.propertyId = id;
            property->base.municipalityDistrict = municipality_district;
            strcpy(property->base.address, address);
            strcpy(property->base.ownerPhoneNumber, owner_phone);
            strcpy(property->base.registrationDate, reg_date);
            strcpy(property->base.deleteDate, del_date);
            property->base.isActive = is_active;
            strcpy(property->base.registeredBy, reg_by);
            property->base.dealType = dealType;
            
            property->buildingAge = building_age;
            property->areaSize = area_size;
            property->floor = floor;
            property->landArea = land_area;
            property->officeRooms = office_rooms;
            strcpy(property->propertyType, property_type);
            property->sellingPrice = selling_price;
            property->mortgageAmount = mortgage_amount;
            property->monthlyRentAmount = monthly_rent;
            
            index++;
        }
    }
    
    fclose(file);
    *count = index;
    
    snprintf(log_message, sizeof(log_message), 
             "Commercial property search by area range %.2f-%.2f: found %d properties", 
             minArea, maxArea == 0 ? 999999.99 : maxArea, index);
    property_log("INFO", log_message);
    
    return results;
}

CommercialProperty* commercial_find_by_type(const char* type, PropertyDealType dealType, int* count) {
    char filename[256];
    char log_message[256];
    CommercialProperty* results = NULL;
    *count = 0;
    
    // بررسی معتبر بودن نوع ملک
    if (type == NULL || strlen(type) == 0) {
        property_log("ERROR", "Invalid property type for commercial property search");
        return NULL;
    }
    
    // انتخاب فایل بر اساس نوع معامله
    if (dealType == PROPERTY_DEAL_SALE) {
        strcpy(filename, COMMERCIAL_SALES_PATH);
    } else if (dealType == PROPERTY_DEAL_RENT) {
        strcpy(filename, COMMERCIAL_RENTALS_PATH);
    } else {
        property_log("ERROR", "Invalid deal type for type-based commercial property search");
        return NULL;
    }
    
    // باز کردن فایل
    FILE* file = fopen(filename, "r");
    if (!file) {
        snprintf(log_message, sizeof(log_message), 
                 "Error opening file for type-based commercial property search");
        property_log("ERROR", log_message);
        return NULL;
    }
    
    // شمارش تعداد املاک واجد شرایط
    char line[1024];
    int match_count = 0;
    
    while (fgets(line, sizeof(line), file)) {
        int id, municipality_district, is_active, building_age, floor, office_rooms, timestamp;
        float area_size, land_area;
        double selling_price, mortgage_amount, monthly_rent;
        char address[100], owner_phone[20], reg_date[11], del_date[11], property_type[20], 
             reg_by[50], deal_type[10], status[20];
        
        // خواندن داده‌ها از خط فایل
        sscanf(line, "%d,%d,%[^,],%[^,],%d,%[^,],%[^,],%d,%f,%d,%f,%d,%[^,],%lf,%lf,%lf,%[^,],%[^,],%d,%s",
               &id, &municipality_district, address, owner_phone, &building_age, reg_date, del_date, 
               &is_active, &area_size, &floor, &land_area, &office_rooms, property_type,
               &selling_price, &mortgage_amount, &monthly_rent, reg_by, deal_type, &timestamp, status);
        
        // بررسی فعال بودن ملک و تطابق با نوع ملک (بدون توجه به بزرگی و کوچکی حروف)
        if (is_active == PROPERTY_STATUS_ACTIVE && 
            strcasecmp(property_type, type) == 0) {
            match_count++;
        }
    }
    
    // اگر هیچ موردی پیدا نشد
    if (match_count == 0) {
        fclose(file);
        return NULL;
    }
    
    // تخصیص حافظه برای نتایج
    results = (CommercialProperty*)malloc(match_count * sizeof(CommercialProperty));
    if (!results) {
        property_log("ERROR", "Memory allocation error in type-based commercial property search");
        fclose(file);
        return NULL;
    }
    
    // بازگشت به ابتدای فایل
    rewind(file);
    
    // خواندن و ذخیره املاک واجد شرایط
    int index = 0;
    while (fgets(line, sizeof(line), file) && index < match_count) {
        CommercialProperty* property = &results[index];
        int id, municipality_district, is_active, building_age, floor, office_rooms, timestamp;
        float area_size, land_area;
        double selling_price, mortgage_amount, monthly_rent;
        char address[100], owner_phone[20], reg_date[11], del_date[11], property_type[20], 
             reg_by[50], deal_type[10], status[20];
        
        // خواندن داده‌ها از خط فایل
        sscanf(line, "%d,%d,%[^,],%[^,],%d,%[^,],%[^,],%d,%f,%d,%f,%d,%[^,],%lf,%lf,%lf,%[^,],%[^,],%d,%s",
               &id, &municipality_district, address, owner_phone, &building_age, reg_date, del_date, 
               &is_active, &area_size, &floor, &land_area, &office_rooms, property_type,
               &selling_price, &mortgage_amount, &monthly_rent, reg_by, deal_type, &timestamp, status);
        
        // بررسی فعال بودن ملک و تطابق با نوع ملک
        if (is_active == PROPERTY_STATUS_ACTIVE && 
            strcasecmp(property_type, type) == 0) {
            property->base.propertyId = id;
            property->base.municipalityDistrict = municipality_district;
            strcpy(property->base.address, address);
            strcpy(property->base.ownerPhoneNumber, owner_phone);
            strcpy(property->base.registrationDate, reg_date);
            strcpy(property->base.deleteDate, del_date);
            property->base.isActive = is_active;
            strcpy(property->base.registeredBy, reg_by);
            property->base.dealType = dealType;
            
            property->buildingAge = building_age;
            property->areaSize = area_size;
            property->floor = floor;
            property->landArea = land_area;
            property->officeRooms = office_rooms;
            strcpy(property->propertyType, property_type);
            property->sellingPrice = selling_price;
            property->mortgageAmount = mortgage_amount;
            property->monthlyRentAmount = monthly_rent;
            
            index++;
        }
    }
    
    fclose(file);
    *count = index;
    
    snprintf(log_message, sizeof(log_message), 
             "Commercial property search by type '%s': found %d properties", type, index);
    property_log("INFO", log_message);
    
    return results;
}

CommercialProperty* commercial_find_by_price(double minPrice, double maxPrice, PropertyDealType dealType, int* count) {
    char filename[256];
    char log_message[256];
    CommercialProperty* results = NULL;
    *count = 0;
    
    // بررسی پارامترهای ورودی
    if (minPrice < 0 || (maxPrice > 0 && maxPrice < minPrice)) {
        property_log("ERROR", "Invalid price range for commercial property search");
        return NULL;
    }
    
    // انتخاب فایل و فیلد قیمت بر اساس نوع معامله
    if (dealType == PROPERTY_DEAL_SALE) {
        strcpy(filename, COMMERCIAL_SALES_PATH);
    } else if (dealType == PROPERTY_DEAL_RENT) {
        strcpy(filename, COMMERCIAL_RENTALS_PATH);
    } else {
        property_log("ERROR", "Invalid deal type for price-based commercial property search");
        return NULL;
    }
    
    // باز کردن فایل
    FILE* file = fopen(filename, "r");
    if (!file) {
        snprintf(log_message, sizeof(log_message), 
                 "Error opening file for price-based commercial property search");
        property_log("ERROR", log_message);
        return NULL;
    }
    
    // شمارش تعداد املاک واجد شرایط
    char line[1024];
    int match_count = 0;
    
    while (fgets(line, sizeof(line), file)) {
        int id, municipality_district, is_active, building_age, floor, office_rooms, timestamp;
        float area_size, land_area;
        double selling_price, mortgage_amount, monthly_rent;
        char address[100], owner_phone[20], reg_date[11], del_date[11], property_type[20], 
             reg_by[50], deal_type[10], status[20];
        
        // خواندن داده‌ها از خط فایل
        sscanf(line, "%d,%d,%[^,],%[^,],%d,%[^,],%[^,],%d,%f,%d,%f,%d,%[^,],%lf,%lf,%lf,%[^,],%[^,],%d,%s",
               &id, &municipality_district, address, owner_phone, &building_age, reg_date, del_date, 
               &is_active, &area_size, &floor, &land_area, &office_rooms, property_type,
               &selling_price, &mortgage_amount, &monthly_rent, reg_by, deal_type, &timestamp, status);
        
        // بررسی فعال بودن ملک و تطابق با محدوده قیمت بر اساس نوع معامله
        if (is_active == PROPERTY_STATUS_ACTIVE) {
            double price_to_check = 0;
            
            if (dealType == PROPERTY_DEAL_SALE) {
                price_to_check = selling_price;
            } else if (dealType == PROPERTY_DEAL_RENT) {
                // برای اجاره، مجموع رهن و اجاره ۱۲ ماه را در نظر می‌گیریم
                price_to_check = mortgage_amount + (monthly_rent * 12);
            }
            
            if (price_to_check >= minPrice && (maxPrice == 0 || price_to_check <= maxPrice)) {
                match_count++;
            }
        }
    }
    
    // اگر هیچ موردی پیدا نشد
    if (match_count == 0) {
        fclose(file);
        return NULL;
    }
    
    // تخصیص حافظه برای نتایج
    results = (CommercialProperty*)malloc(match_count * sizeof(CommercialProperty));
    if (!results) {
        property_log("ERROR", "Memory allocation error in price-based commercial property search");
        fclose(file);
        return NULL;
    }
    
    // بازگشت به ابتدای فایل
    rewind(file);
    
    // خواندن و ذخیره املاک واجد شرایط
    int index = 0;
    while (fgets(line, sizeof(line), file) && index < match_count) {
        CommercialProperty* property = &results[index];
        int id, municipality_district, is_active, building_age, floor, office_rooms, timestamp;
        float area_size, land_area;
        double selling_price, mortgage_amount, monthly_rent;
        char address[100], owner_phone[20], reg_date[11], del_date[11], property_type[20], 
             reg_by[50], deal_type[10], status[20];
        
        // خواندن داده‌ها از خط فایل
        sscanf(line, "%d,%d,%[^,],%[^,],%d,%[^,],%[^,],%d,%f,%d,%f,%d,%[^,],%lf,%lf,%lf,%[^,],%[^,],%d,%s",
               &id, &municipality_district, address, owner_phone, &building_age, reg_date, del_date, 
               &is_active, &area_size, &floor, &land_area, &office_rooms, property_type,
               &selling_price, &mortgage_amount, &monthly_rent, reg_by, deal_type, &timestamp, status);
        
        // بررسی مجدد شرایط همانند حلقه قبلی
        if (is_active == PROPERTY_STATUS_ACTIVE) {
            double price_to_check = 0;
            
            if (dealType == PROPERTY_DEAL_SALE) {
                price_to_check = selling_price;
            } else if (dealType == PROPERTY_DEAL_RENT) {
                price_to_check = mortgage_amount + (monthly_rent * 12);
            }
            
            if (price_to_check >= minPrice && (maxPrice == 0 || price_to_check <= maxPrice)) {
                property->base.propertyId = id;
                property->base.municipalityDistrict = municipality_district;
                strcpy(property->base.address, address);
                strcpy(property->base.ownerPhoneNumber, owner_phone);
                strcpy(property->base.registrationDate, reg_date);
                strcpy(property->base.deleteDate, del_date);
                property->base.isActive = is_active;
                strcpy(property->base.registeredBy, reg_by);
                property->base.dealType = dealType;
                
                property->buildingAge = building_age;
                property->areaSize = area_size;
                property->floor = floor;
                property->landArea = land_area;
                property->officeRooms = office_rooms;
                strcpy(property->propertyType, property_type);
                property->sellingPrice = selling_price;
                property->mortgageAmount = mortgage_amount;
                property->monthlyRentAmount = monthly_rent;
                
                index++;
            }
        }
    }
    
    fclose(file);
    *count = index;
    
    snprintf(log_message, sizeof(log_message), 
             "Commercial property search by price range %.2f-%.2f: found %d properties", 
             minPrice, maxPrice == 0 ? 999999999.99 : maxPrice, index);
    property_log("INFO", log_message);
    
    return results;
}

CommercialProperty* commercial_find_by_rooms(int minRooms, int maxRooms, PropertyDealType dealType, int* count) {
    char filename[256];
    char log_message[256];
    CommercialProperty* results = NULL;
    *count = 0;
    
    // بررسی پارامترهای ورودی
    if (minRooms < 0 || (maxRooms > 0 && maxRooms < minRooms)) {
        property_log("ERROR", "Invalid room range for commercial property search");
        return NULL;
    }
    
    // انتخاب فایل بر اساس نوع معامله
    if (dealType == PROPERTY_DEAL_SALE) {
        strcpy(filename, COMMERCIAL_SALES_PATH);
    } else if (dealType == PROPERTY_DEAL_RENT) {
        strcpy(filename, COMMERCIAL_RENTALS_PATH);
    } else {
        property_log("ERROR", "Invalid deal type for room-based commercial property search");
        return NULL;
    }
    
    // باز کردن فایل
    FILE* file = fopen(filename, "r");
    if (!file) {
        snprintf(log_message, sizeof(log_message), 
                 "Error opening file for room-based commercial property search");
        property_log("ERROR", log_message);
        return NULL;
    }
    
    // شمارش تعداد املاک واجد شرایط
    char line[1024];
    int match_count = 0;
    
    while (fgets(line, sizeof(line), file)) {
        int id, municipality_district, is_active, building_age, floor, office_rooms, timestamp;
        float area_size, land_area;
        double selling_price, mortgage_amount, monthly_rent;
        char address[100], owner_phone[20], reg_date[11], del_date[11], property_type[20], 
             reg_by[50], deal_type[10], status[20];
        
        // خواندن داده‌ها از خط فایل
        sscanf(line, "%d,%d,%[^,],%[^,],%d,%[^,],%[^,],%d,%f,%d,%f,%d,%[^,],%lf,%lf,%lf,%[^,],%[^,],%d,%s",
               &id, &municipality_district, address, owner_phone, &building_age, reg_date, del_date, 
               &is_active, &area_size, &floor, &land_area, &office_rooms, property_type,
               &selling_price, &mortgage_amount, &monthly_rent, reg_by, deal_type, &timestamp, status);
        
        // بررسی فعال بودن ملک و تطابق با محدوده تعداد اتاق
        if (is_active == PROPERTY_STATUS_ACTIVE && 
            office_rooms >= minRooms && 
            (maxRooms == 0 || office_rooms <= maxRooms)) {
            match_count++;
        }
    }
    
    // اگر هیچ موردی پیدا نشد
    if (match_count == 0) {
        fclose(file);
        return NULL;
    }
    
    // تخصیص حافظه برای نتایج
    results = (CommercialProperty*)malloc(match_count * sizeof(CommercialProperty));
    if (!results) {
        property_log("ERROR", "Memory allocation error in room-based commercial property search");
        fclose(file);
        return NULL;
    }
    
    // بازگشت به ابتدای فایل
    rewind(file);
    
    // خواندن و ذخیره املاک واجد شرایط
    int index = 0;
    while (fgets(line, sizeof(line), file) && index < match_count) {
        CommercialProperty* property = &results[index];
        int id, municipality_district, is_active, building_age, floor, office_rooms, timestamp;
        float area_size, land_area;
        double selling_price, mortgage_amount, monthly_rent;
        char address[100], owner_phone[20], reg_date[11], del_date[11], property_type[20], 
             reg_by[50], deal_type[10], status[20];
        
        // خواندن داده‌ها از خط فایل
        sscanf(line, "%d,%d,%[^,],%[^,],%d,%[^,],%[^,],%d,%f,%d,%f,%d,%[^,],%lf,%lf,%lf,%[^,],%[^,],%d,%s",
               &id, &municipality_district, address, owner_phone, &building_age, reg_date, del_date, 
               &is_active, &area_size, &floor, &land_area, &office_rooms, property_type,
               &selling_price, &mortgage_amount, &monthly_rent, reg_by, deal_type, &timestamp, status);
        
        // بررسی فعال بودن ملک و تطابق با محدوده تعداد اتاق
        if (is_active == PROPERTY_STATUS_ACTIVE && 
            office_rooms >= minRooms && 
            (maxRooms == 0 || office_rooms <= maxRooms)) {
            property->base.propertyId = id;
            property->base.municipalityDistrict = municipality_district;
            strcpy(property->base.address, address);
            strcpy(property->base.ownerPhoneNumber, owner_phone);
            strcpy(property->base.registrationDate, reg_date);
            strcpy(property->base.deleteDate, del_date);
            property->base.isActive = is_active;
            strcpy(property->base.registeredBy, reg_by);
            property->base.dealType = dealType;
            
            property->buildingAge = building_age;
            property->areaSize = area_size;
            property->floor = floor;
            property->landArea = land_area;
            property->officeRooms = office_rooms;
            strcpy(property->propertyType, property_type);
            property->sellingPrice = selling_price;
            property->mortgageAmount = mortgage_amount;
            property->monthlyRentAmount = monthly_rent;
            
            index++;
        }
    }
    
    fclose(file);
    *count = index;
    
    snprintf(log_message, sizeof(log_message), 
             "Commercial property search by room range %d-%d: found %d properties", 
             minRooms, maxRooms == 0 ? 999 : maxRooms, index);
    property_log("INFO", log_message);
    
    return results;
}

CommercialProperty* commercial_find_by_floor(int minFloor, int maxFloor, PropertyDealType dealType, int* count) {
    char filename[256];
    char log_message[256];
    CommercialProperty* results = NULL;
    *count = 0;
    
    // بررسی پارامترهای ورودی
    if ((maxFloor > 0 && maxFloor < minFloor)) {
        property_log("ERROR", "Invalid floor range for commercial property search");
        return NULL;
    }
    
    // انتخاب فایل بر اساس نوع معامله
    if (dealType == PROPERTY_DEAL_SALE) {
        strcpy(filename, COMMERCIAL_SALES_PATH);
    } else if (dealType == PROPERTY_DEAL_RENT) {
        strcpy(filename, COMMERCIAL_RENTALS_PATH);
    } else {
        property_log("ERROR", "Invalid deal type for floor-based commercial property search");
        return NULL;
    }
    
    // باز کردن فایل
    FILE* file = fopen(filename, "r");
    if (!file) {
        snprintf(log_message, sizeof(log_message), 
                 "Error opening file for floor-based commercial property search");
        property_log("ERROR", log_message);
        return NULL;
    }
    
    // شمارش تعداد املاک واجد شرایط
    char line[1024];
    int match_count = 0;
    
    while (fgets(line, sizeof(line), file)) {
        int id, municipality_district, is_active, building_age, floor, office_rooms, timestamp;
        float area_size, land_area;
        double selling_price, mortgage_amount, monthly_rent;
        char address[100], owner_phone[20], reg_date[11], del_date[11], property_type[20], 
             reg_by[50], deal_type[10], status[20];
        
        // خواندن داده‌ها از خط فایل
        sscanf(line, "%d,%d,%[^,],%[^,],%d,%[^,],%[^,],%d,%f,%d,%f,%d,%[^,],%lf,%lf,%lf,%[^,],%[^,],%d,%s",
               &id, &municipality_district, address, owner_phone, &building_age, reg_date, del_date, 
               &is_active, &area_size, &floor, &land_area, &office_rooms, property_type,
               &selling_price, &mortgage_amount, &monthly_rent, reg_by, deal_type, &timestamp, status);
        
        // بررسی فعال بودن ملک و تطابق با محدوده طبقه
        if (is_active == PROPERTY_STATUS_ACTIVE && 
            floor >= minFloor && 
            (maxFloor == 0 || floor <= maxFloor)) {
            match_count++;
        }
    }
    
    // اگر هیچ موردی پیدا نشد
    if (match_count == 0) {
        fclose(file);
        return NULL;
    }
    
    // تخصیص حافظه برای نتایج
    results = (CommercialProperty*)malloc(match_count * sizeof(CommercialProperty));
    if (!results) {
        property_log("ERROR", "Memory allocation error in floor-based commercial property search");
        fclose(file);
        return NULL;
    }
    
    // بازگشت به ابتدای فایل
    rewind(file);
    
    // خواندن و ذخیره املاک واجد شرایط
    int index = 0;
    while (fgets(line, sizeof(line), file) && index < match_count) {
        CommercialProperty* property = &results[index];
        int id, municipality_district, is_active, building_age, floor, office_rooms, timestamp;
        float area_size, land_area;
        double selling_price, mortgage_amount, monthly_rent;
        char address[100], owner_phone[20], reg_date[11], del_date[11], property_type[20], 
             reg_by[50], deal_type[10], status[20];
        
        // خواندن داده‌ها از خط فایل
        sscanf(line, "%d,%d,%[^,],%[^,],%d,%[^,],%[^,],%d,%f,%d,%f,%d,%[^,],%lf,%lf,%lf,%[^,],%[^,],%d,%s",
               &id, &municipality_district, address, owner_phone, &building_age, reg_date, del_date, 
               &is_active, &area_size, &floor, &land_area, &office_rooms, property_type,
               &selling_price, &mortgage_amount, &monthly_rent, reg_by, deal_type, &timestamp, status);
        
        // بررسی فعال بودن ملک و تطابق با محدوده طبقه
        if (is_active == PROPERTY_STATUS_ACTIVE && 
            floor >= minFloor && 
            (maxFloor == 0 || floor <= maxFloor)) {
            property->base.propertyId = id;
            property->base.municipalityDistrict = municipality_district;
            strcpy(property->base.address, address);
            strcpy(property->base.ownerPhoneNumber, owner_phone);
            strcpy(property->base.registrationDate, reg_date);
            strcpy(property->base.deleteDate, del_date);
            property->base.isActive = is_active;
            strcpy(property->base.registeredBy, reg_by);
            property->base.dealType = dealType;
            
            property->buildingAge = building_age;
            property->areaSize = area_size;
            property->floor = floor;
            property->landArea = land_area;
            property->officeRooms = office_rooms;
            strcpy(property->propertyType, property_type);
            property->sellingPrice = selling_price;
            property->mortgageAmount = mortgage_amount;
            property->monthlyRentAmount = monthly_rent;
            
            index++;
        }
    }
    
    fclose(file);
    *count = index;
    
    snprintf(log_message, sizeof(log_message), 
             "Commercial property search by floor range %d-%d: found %d properties", 
             minFloor, maxFloor == 0 ? 999 : maxFloor, index);
    property_log("INFO", log_message);
    
    return results;
}

CommercialProperty* commercial_find_deleted_by_date(const char* startDate, const char* endDate, 
                                                  PropertyDealType dealType, int* count) {
    char filename[256];
    char log_message[256];
    CommercialProperty* results = NULL;
    *count = 0;
    
    // بررسی معتبر بودن تاریخ‌ها
    if (!startDate || !endDate || strlen(startDate) != 10 || strlen(endDate) != 10) {
        property_log("ERROR", "Invalid date format for deleted commercial property search");
        return NULL;
    }
    
    // انتخاب فایل بر اساس نوع معامله
    if (dealType == PROPERTY_DEAL_SALE) {
        strcpy(filename, COMMERCIAL_SALES_PATH);
    } else if (dealType == PROPERTY_DEAL_RENT) {
        strcpy(filename, COMMERCIAL_RENTALS_PATH);
    } else {
        property_log("ERROR", "Invalid deal type for deleted commercial property search");
        return NULL;
    }
    
    // باز کردن فایل
    FILE* file = fopen(filename, "r");
    if (!file) {
        snprintf(log_message, sizeof(log_message), 
                 "Error opening file for deleted commercial property search");
        property_log("ERROR", log_message);
        return NULL;
    }
    
    // شمارش تعداد املاک واجد شرایط
    char line[1024];
    int match_count = 0;
    
    while (fgets(line, sizeof(line), file)) {
        int id, municipality_district, is_active, building_age, floor, office_rooms, timestamp;
        float area_size, land_area;
        double selling_price, mortgage_amount, monthly_rent;
        char address[100], owner_phone[20], reg_date[11], del_date[11], property_type[20], 
             reg_by[50], deal_type[10], status[20];
        
        // خواندن داده‌ها از خط فایل
        sscanf(line, "%d,%d,%[^,],%[^,],%d,%[^,],%[^,],%d,%f,%d,%f,%d,%[^,],%lf,%lf,%lf,%[^,],%[^,],%d,%s",
               &id, &municipality_district, address, owner_phone, &building_age, reg_date, del_date, 
               &is_active, &area_size, &floor, &land_area, &office_rooms, property_type,
               &selling_price, &mortgage_amount, &monthly_rent, reg_by, deal_type, &timestamp, status);
        
        // بررسی ملک‌های حذف شده در محدوده تاریخ مشخص شده
        if (is_active == PROPERTY_STATUS_INACTIVE && 
            strlen(del_date) == 10 &&  // فرمت تاریخ حذف باید معتبر باشد
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
    results = (CommercialProperty*)malloc(match_count * sizeof(CommercialProperty));
    if (!results) {
        property_log("ERROR", "Memory allocation error in deleted commercial property search");
        fclose(file);
        return NULL;
    }
    
    // بازگشت به ابتدای فایل
    rewind(file);
    
    // خواندن و ذخیره املاک واجد شرایط
    int index = 0;
    while (fgets(line, sizeof(line), file) && index < match_count) {
        CommercialProperty* property = &results[index];
        int id, municipality_district, is_active, building_age, floor, office_rooms, timestamp;
        float area_size, land_area;
        double selling_price, mortgage_amount, monthly_rent;
        char address[100], owner_phone[20], reg_date[11], del_date[11], property_type[20], 
             reg_by[50], deal_type[10], status[20];
        
        // خواندن داده‌ها از خط فایل
        sscanf(line, "%d,%d,%[^,],%[^,],%d,%[^,],%[^,],%d,%f,%d,%f,%d,%[^,],%lf,%lf,%lf,%[^,],%[^,],%d,%s",
               &id, &municipality_district, address, owner_phone, &building_age, reg_date, del_date, 
               &is_active, &area_size, &floor, &land_area, &office_rooms, property_type,
               &selling_price, &mortgage_amount, &monthly_rent, reg_by, deal_type, &timestamp, status);
        
        // بررسی ملک‌های حذف شده در محدوده تاریخ مشخص شده
        if (is_active == PROPERTY_STATUS_INACTIVE && 
            strlen(del_date) == 10 &&  // فرمت تاریخ حذف باید معتبر باشد
            strcmp(del_date, startDate) >= 0 && 
            strcmp(del_date, endDate) <= 0) {
            property->base.propertyId = id;
            property->base.municipalityDistrict = municipality_district;
            strcpy(property->base.address, address);
            strcpy(property->base.ownerPhoneNumber, owner_phone);
            strcpy(property->base.registrationDate, reg_date);
            strcpy(property->base.deleteDate, del_date);
            property->base.isActive = is_active;
            strcpy(property->base.registeredBy, reg_by);
            property->base.dealType = dealType;
            
            property->buildingAge = building_age;
            property->areaSize = area_size;
            property->floor = floor;
            property->landArea = land_area;
            property->officeRooms = office_rooms;
            strcpy(property->propertyType, property_type);
            property->sellingPrice = selling_price;
            property->mortgageAmount = mortgage_amount;
            property->monthlyRentAmount = monthly_rent;
            
            index++;
        }
    }
    
    fclose(file);
    *count = index;
    
    snprintf(log_message, sizeof(log_message), 
             "Commercial property search for deleted properties between %s and %s: found %d properties", 
             startDate, endDate, index);
    property_log("INFO", log_message);
    
    return results;
}

CommercialProperty* commercial_find_by_user(const char* username, PropertyDealType dealType, int* count) {
    char filename[256];
    char log_message[256];
    CommercialProperty* results = NULL;
    *count = 0;
    
    // بررسی معتبر بودن نام کاربری
    if (!username || strlen(username) == 0) {
        property_log("ERROR", "Invalid username for commercial property search");
        return NULL;
    }
    
    // انتخاب فایل بر اساس نوع معامله
    if (dealType == PROPERTY_DEAL_SALE) {
        strcpy(filename, COMMERCIAL_SALES_PATH);
    } else if (dealType == PROPERTY_DEAL_RENT) {
        strcpy(filename, COMMERCIAL_RENTALS_PATH);
    } else {
        property_log("ERROR", "Invalid deal type for user-based commercial property search");
        return NULL;
    }
    
    // باز کردن فایل
    FILE* file = fopen(filename, "r");
    if (!file) {
        snprintf(log_message, sizeof(log_message), 
                 "Error opening file for user-based commercial property search");
        property_log("ERROR", log_message);
        return NULL;
    }
    
    // شمارش تعداد املاک واجد شرایط
    char line[1024];
    int match_count = 0;
    
    while (fgets(line, sizeof(line), file)) {
        int id, municipality_district, is_active, building_age, floor, office_rooms, timestamp;
        float area_size, land_area;
        double selling_price, mortgage_amount, monthly_rent;
        char address[100], owner_phone[20], reg_date[11], del_date[11], property_type[20], 
             reg_by[50], deal_type[10], status[20];
        
        // خواندن داده‌ها از خط فایل
        sscanf(line, "%d,%d,%[^,],%[^,],%d,%[^,],%[^,],%d,%f,%d,%f,%d,%[^,],%lf,%lf,%lf,%[^,],%[^,],%d,%s",
               &id, &municipality_district, address, owner_phone, &building_age, reg_date, del_date, 
               &is_active, &area_size, &floor, &land_area, &office_rooms, property_type,
               &selling_price, &mortgage_amount, &monthly_rent, reg_by, deal_type, &timestamp, status);
        
        // بررسی تطابق نام کاربری
        if (strcmp(reg_by, username) == 0) {
            match_count++;
        }
    }
    
    // اگر هیچ موردی پیدا نشد
    if (match_count == 0) {
        fclose(file);
        return NULL;
    }
    
    // تخصیص حافظه برای نتایج
    results = (CommercialProperty*)malloc(match_count * sizeof(CommercialProperty));
    if (!results) {
        property_log("ERROR", "Memory allocation error in user-based commercial property search");
        fclose(file);
        return NULL;
    }
    
    // بازگشت به ابتدای فایل
    rewind(file);
    
    // خواندن و ذخیره املاک واجد شرایط
    int index = 0;
    while (fgets(line, sizeof(line), file) && index < match_count) {
        CommercialProperty* property = &results[index];
        int id, municipality_district, is_active, building_age, floor, office_rooms, timestamp;
        float area_size, land_area;
        double selling_price, mortgage_amount, monthly_rent;
        char address[100], owner_phone[20], reg_date[11], del_date[11], property_type[20], 
             reg_by[50], deal_type[10], status[20];
        
        // خواندن داده‌ها از خط فایل
        sscanf(line, "%d,%d,%[^,],%[^,],%d,%[^,],%[^,],%d,%f,%d,%f,%d,%[^,],%lf,%lf,%lf,%[^,],%[^,],%d,%s",
               &id, &municipality_district, address, owner_phone, &building_age, reg_date, del_date, 
               &is_active, &area_size, &floor, &land_area, &office_rooms, property_type,
               &selling_price, &mortgage_amount, &monthly_rent, reg_by, deal_type, &timestamp, status);
        
        // بررسی تطابق نام کاربری
        if (strcmp(reg_by, username) == 0) {
            property->base.propertyId = id;
            property->base.municipalityDistrict = municipality_district;
            strcpy(property->base.address, address);
            strcpy(property->base.ownerPhoneNumber, owner_phone);
            strcpy(property->base.registrationDate, reg_date);
            strcpy(property->base.deleteDate, del_date);
            property->base.isActive = is_active;
            strcpy(property->base.registeredBy, reg_by);
            property->base.dealType = dealType;
            
            property->buildingAge = building_age;
            property->areaSize = area_size;
            property->floor = floor;
            property->landArea = land_area;
            property->officeRooms = office_rooms;
            strcpy(property->propertyType, property_type);
            property->sellingPrice = selling_price;
            property->mortgageAmount = mortgage_amount;
            property->monthlyRentAmount = monthly_rent;
            
            index++;
        }
    }
    
    fclose(file);
    *count = index;
    
    snprintf(log_message, sizeof(log_message), 
             "Commercial property search for user '%s': found %d properties", 
             username, index);
    property_log("INFO", log_message);
    
    return results;
}

double commercial_calculate_total_value() {
    char log_message[256];
    FILE* file = fopen(COMMERCIAL_SALES_PATH, "r");
    double total_value = 0.0;
    
    if (!file) {
        property_log("ERROR", "Failed to open commercial sales file for total value calculation");
        return 0.0;
    }
    
    char line[1024];
    
    // خواندن هر خط از فایل فروش تجاری و جمع کردن قیمت‌ها
    while (fgets(line, sizeof(line), file)) {
        int id, municipality_district, is_active, building_age, floor, office_rooms, timestamp;
        float area_size, land_area;
        double selling_price, mortgage_amount, monthly_rent;
        char address[100], owner_phone[20], reg_date[11], del_date[11], property_type[20], 
             reg_by[50], deal_type[10], status[20];
        
        // خواندن داده‌ها از خط فایل
        sscanf(line, "%d,%d,%[^,],%[^,],%d,%[^,],%[^,],%d,%f,%d,%f,%d,%[^,],%lf,%lf,%lf,%[^,],%[^,],%d,%s",
               &id, &municipality_district, address, owner_phone, &building_age, reg_date, del_date, 
               &is_active, &area_size, &floor, &land_area, &office_rooms, property_type,
               &selling_price, &mortgage_amount, &monthly_rent, reg_by, deal_type, &timestamp, status);
        
        // فقط املاک فعال در محاسبه لحاظ می‌شوند
        if (is_active == PROPERTY_STATUS_ACTIVE) {
            total_value += selling_price;
        }
    }
    
    fclose(file);
    
    snprintf(log_message, sizeof(log_message), 
             "Total value of commercial properties for sale calculated: %.2f", 
             total_value);
    property_log("INFO", log_message);
    
    return total_value;
}

void commercial_free_array(CommercialProperty* array, int count) {
    if (array != NULL) {
        free(array);
        char log_message[100];
        snprintf(log_message, sizeof(log_message), 
                 "Freed memory for %d commercial properties", count);
        property_log("DEBUG", log_message);
    }
} 