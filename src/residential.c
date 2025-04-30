/**
 * @file residential.c
 * @brief پیاده‌سازی توابع مرتبط با املاک مسکونی
 */

#include "../include/residential.h"
#include "../include/data_manager.h"
#include "../include/utils.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

// مسیر فایل ذخیره‌سازی املاک مسکونی
static char RESIDENTIAL_SALES_PATH[256] = "data/residential_sales.csv";
static char RESIDENTIAL_RENTALS_PATH[256] = "data/residential_rentals.csv";

// تنظیم مسیر فایل‌ها بر اساس مسیر کلی داده‌ها
void residential_set_data_path(const char* base_path) {
    snprintf(RESIDENTIAL_SALES_PATH, sizeof(RESIDENTIAL_SALES_PATH), 
             "%s/residential_sales.csv", base_path);
    snprintf(RESIDENTIAL_RENTALS_PATH, sizeof(RESIDENTIAL_RENTALS_PATH), 
             "%s/residential_rentals.csv", base_path);
}

/**
 * @brief اعتبارسنجی داده‌های ملک مسکونی
 * 
 * @param property اطلاعات ملک مسکونی
 * @return int 0: معتبر، 1: نامعتبر
 */
static int validate_residential_property(ResidentialProperty* property) {
    // بررسی داده‌های پایه
    if (property->base.municipalityDistrict <= 0 || 
        property->base.municipalityDistrict > 22) {
        property_log("ERROR", "منطقه شهرداری نامعتبر است");
        return 1;
    }
    
    if (!property_check_address_format(property->base.address)) {
        property_log("ERROR", "فرمت آدرس نامعتبر است");
        return 1;
    }
    
    if (strlen(property->base.ownerPhoneNumber) < 10) {
        property_log("ERROR", "شماره تماس مالک نامعتبر است");
        return 1;
    }
    
    // بررسی داده‌های اختصاصی
    if (property->areaSize <= 0) {
        property_log("ERROR", "متراژ نامعتبر است");
        return 1;
    }
    
    if (property->buildingAge < 0) {
        property_log("ERROR", "سن ساختمان نامعتبر است");
        return 1;
    }
    
    if (property->bedrooms < 0) {
        property_log("ERROR", "تعداد اتاق خواب نامعتبر است");
        return 1;
    }
    
    if (property->totalFloors < 0) {
        property_log("ERROR", "تعداد کل طبقات نامعتبر است");
        return 1;
    }
    
    // اعتبارسنجی قیمت بر اساس نوع معامله
    if (property->base.dealType == PROPERTY_DEAL_SALE) {
        if (property->sellingPrice <= 0) {
            property_log("ERROR", "قیمت فروش نامعتبر است");
            return 1;
        }
    } else if (property->base.dealType == PROPERTY_DEAL_RENT) {
        if (property->mortgageAmount < 0 || property->monthlyRentAmount <= 0) {
            property_log("ERROR", "مبلغ رهن یا اجاره نامعتبر است");
            return 1;
        }
    }
    
    return 0; // معتبر
}

int residential_register_sale(ResidentialProperty* property, const char* username) {
    char log_message[256];
    
    // بررسی پارامترها
    if (!property || !username || strlen(username) == 0) {
        property_log("ERROR", "پارامترهای ورودی نامعتبر برای ثبت ملک مسکونی فروشی");
        return PROPERTY_ERROR_VALIDATION;
    }
    
    // تنظیم اطلاعات پایه
    property->base.propertyId = property_generate_id();
    property->base.dealType = PROPERTY_DEAL_SALE;
    property->base.isActive = PROPERTY_STATUS_ACTIVE;
    strcpy(property->base.registeredBy, username);
    
    // تنظیم تاریخ ثبت
    time_t now = time(NULL);
    struct tm* tm_info = localtime(&now);
    strftime(property->base.registrationDate, sizeof(property->base.registrationDate), 
             "%Y-%m-%d", tm_info);
    property->base.deleteDate[0] = '\0'; // خالی کردن تاریخ حذف
    
    // اعتبارسنجی داده‌ها
    if (validate_residential_property(property)) {
        snprintf(log_message, sizeof(log_message), 
                 "خطای اعتبارسنجی در ثبت ملک مسکونی فروشی توسط کاربر %s", username);
        property_log("ERROR", log_message);
        return PROPERTY_ERROR_VALIDATION;
    }
    
    // ذخیره‌سازی در فایل
    FILE* file = fopen(RESIDENTIAL_SALES_PATH, "ab");
    if (!file) {
        snprintf(log_message, sizeof(log_message), 
                 "خطای باز کردن فایل برای ثبت ملک مسکونی فروشی توسط کاربر %s", username);
        property_log("ERROR", log_message);
        return PROPERTY_ERROR_FILE;
    }
    
    // نوشتن اطلاعات در فایل
    fprintf(file, "%d,%d,%s,%s,%d,%s,%s,%d,%f,%d,%d,%d,%d,%d,%d,%lf,0,0,%s,%s,%d,%s\n",
            property->base.propertyId,
            property->base.municipalityDistrict,
            property->base.address,
            property->base.ownerPhoneNumber,
            property->buildingAge,
            property->base.registrationDate,
            property->base.deleteDate,
            property->base.isActive,
            property->areaSize,
            property->bedrooms,
            property->floor,
            property->totalFloors,
            property->hasElevator,
            property->hasParking,
            property->hasStorage,
            property->sellingPrice,
            // برای فروش مقادیر رهن و اجاره صفر ثبت می‌شود
            property->base.registeredBy,
            "ACTIVE", // وضعیت برای تغییرات آینده
            (int)time(NULL) // زمان ثبت به صورت timestamp
            );
    
    fclose(file);
    
    // به‌روزرسانی شمارنده املاک
    int count = property_get_count();
    property_update_count(count + 1);
    
    snprintf(log_message, sizeof(log_message), 
             "ملک مسکونی فروشی با شناسه %d توسط کاربر %s ثبت شد", 
             property->base.propertyId, username);
    property_log("INFO", log_message);
    
    return PROPERTY_SUCCESS;
}

int residential_register_rental(ResidentialProperty* property, const char* username) {
    char log_message[256];
    
    // بررسی پارامترها
    if (!property || !username || strlen(username) == 0) {
        property_log("ERROR", "پارامترهای ورودی نامعتبر برای ثبت ملک مسکونی اجاره‌ای");
        return PROPERTY_ERROR_VALIDATION;
    }
    
    // تنظیم اطلاعات پایه
    property->base.propertyId = property_generate_id();
    property->base.dealType = PROPERTY_DEAL_RENT;
    property->base.isActive = PROPERTY_STATUS_ACTIVE;
    strcpy(property->base.registeredBy, username);
    
    // تنظیم تاریخ ثبت
    time_t now = time(NULL);
    struct tm* tm_info = localtime(&now);
    strftime(property->base.registrationDate, sizeof(property->base.registrationDate), 
             "%Y-%m-%d", tm_info);
    property->base.deleteDate[0] = '\0'; // خالی کردن تاریخ حذف
    
    // اعتبارسنجی داده‌ها
    if (validate_residential_property(property)) {
        snprintf(log_message, sizeof(log_message), 
                 "خطای اعتبارسنجی در ثبت ملک مسکونی اجاره‌ای توسط کاربر %s", username);
        property_log("ERROR", log_message);
        return PROPERTY_ERROR_VALIDATION;
    }
    
    // ذخیره‌سازی در فایل
    FILE* file = fopen(RESIDENTIAL_RENTALS_PATH, "ab");
    if (!file) {
        snprintf(log_message, sizeof(log_message), 
                 "خطای باز کردن فایل برای ثبت ملک مسکونی اجاره‌ای توسط کاربر %s", username);
        property_log("ERROR", log_message);
        return PROPERTY_ERROR_FILE;
    }
    
    // نوشتن اطلاعات در فایل
    fprintf(file, "%d,%d,%s,%s,%d,%s,%s,%d,%f,%d,%d,%d,%d,%d,%d,0,%lf,%lf,%s,%s,%d,%s\n",
            property->base.propertyId,
            property->base.municipalityDistrict,
            property->base.address,
            property->base.ownerPhoneNumber,
            property->buildingAge,
            property->base.registrationDate,
            property->base.deleteDate,
            property->base.isActive,
            property->areaSize,
            property->bedrooms,
            property->floor,
            property->totalFloors,
            property->hasElevator,
            property->hasParking,
            property->hasStorage,
            // برای اجاره قیمت فروش صفر ثبت می‌شود
            property->mortgageAmount,
            property->monthlyRentAmount,
            property->base.registeredBy,
            "ACTIVE", // وضعیت برای تغییرات آینده
            (int)time(NULL) // زمان ثبت به صورت timestamp
            );
    
    fclose(file);
    
    // به‌روزرسانی شمارنده املاک
    int count = property_get_count();
    property_update_count(count + 1);
    
    snprintf(log_message, sizeof(log_message), 
             "ملک مسکونی اجاره‌ای با شناسه %d توسط کاربر %s ثبت شد", 
             property->base.propertyId, username);
    property_log("INFO", log_message);
    
    return PROPERTY_SUCCESS;
}

ResidentialProperty* residential_find_by_district(int district, PropertyDealType dealType, int* count) {
    char filename[256];
    char log_message[256];
    ResidentialProperty* results = NULL;
    *count = 0;
    
    // انتخاب فایل بر اساس نوع معامله
    if (dealType == PROPERTY_DEAL_SALE) {
        strcpy(filename, RESIDENTIAL_SALES_PATH);
    } else if (dealType == PROPERTY_DEAL_RENT) {
        strcpy(filename, RESIDENTIAL_RENTALS_PATH);
    } else {
        property_log("ERROR", "نوع معامله نامعتبر در جستجوی املاک مسکونی بر اساس منطقه");
        return NULL;
    }
    
    // باز کردن فایل
    FILE* file = fopen(filename, "rb");
    if (!file) {
        snprintf(log_message, sizeof(log_message), 
                 "خطای باز کردن فایل برای جستجوی املاک مسکونی منطقه %d", district);
        property_log("ERROR", log_message);
        return NULL;
    }
    
    // شمارش تعداد املاک واجد شرایط
    char line[1024];
    int match_count = 0;
    
    // شمارش تعداد املاک واجد شرایط
    while (fgets(line, sizeof(line), file)) {
        ResidentialProperty temp;
        int id, municipality_district, is_active, building_age, bedrooms, floor;
        int total_floors, has_elevator, has_parking, has_storage, timestamp;
        float area_size;
        double selling_price, mortgage_amount, monthly_rent;
        char address[100], owner_phone[20], reg_date[11], del_date[11], reg_by[50], status[20];
        
        // خواندن داده‌ها از خط فایل
        sscanf(line, "%d,%d,%[^,],%[^,],%d,%[^,],%[^,],%d,%f,%d,%d,%d,%d,%d,%d,%lf,%lf,%lf,%[^,],%[^,],%d,%s",
               &id, &municipality_district, address, owner_phone, &building_age, reg_date, del_date, 
               &is_active, &area_size, &bedrooms, &floor, &total_floors, &has_elevator, 
               &has_parking, &has_storage, &selling_price, &mortgage_amount, &monthly_rent, 
               reg_by, status, &timestamp, status);
        
        // بررسی شرایط جستجو
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
    results = (ResidentialProperty*)malloc(match_count * sizeof(ResidentialProperty));
    if (!results) {
        property_log("ERROR", "خطای تخصیص حافظه در جستجوی املاک مسکونی");
        fclose(file);
        return NULL;
    }
    
    // بازگشت به ابتدای فایل
    rewind(file);
    
    // خواندن و ذخیره املاک واجد شرایط
    int index = 0;
    while (fgets(line, sizeof(line), file) && index < match_count) {
        ResidentialProperty* property = &results[index];
        int id, municipality_district, is_active, building_age, bedrooms, floor;
        int total_floors, has_elevator, has_parking, has_storage, timestamp;
        float area_size;
        double selling_price, mortgage_amount, monthly_rent;
        char address[100], owner_phone[20], reg_date[11], del_date[11], reg_by[50], status[20];
        
        // خواندن داده‌ها از خط فایل
        sscanf(line, "%d,%d,%[^,],%[^,],%d,%[^,],%[^,],%d,%f,%d,%d,%d,%d,%d,%d,%lf,%lf,%lf,%[^,],%[^,],%d,%s",
               &id, &municipality_district, address, owner_phone, &building_age, reg_date, del_date, 
               &is_active, &area_size, &bedrooms, &floor, &total_floors, &has_elevator, 
               &has_parking, &has_storage, &selling_price, &mortgage_amount, &monthly_rent, 
               reg_by, status, &timestamp, status);
        
        // بررسی شرایط جستجو و ذخیره نتایج
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
            property->bedrooms = bedrooms;
            property->floor = floor;
            property->totalFloors = total_floors;
            property->hasElevator = has_elevator;
            property->hasParking = has_parking;
            property->hasStorage = has_storage;
            property->sellingPrice = selling_price;
            property->mortgageAmount = mortgage_amount;
            property->monthlyRentAmount = monthly_rent;
            
            index++;
        }
    }
    
    fclose(file);
    *count = index;
    
    snprintf(log_message, sizeof(log_message), 
             "جستجوی املاک مسکونی منطقه %d: %d مورد یافت شد", district, index);
    property_log("INFO", log_message);
    
    return results;
}

ResidentialProperty* residential_find_by_age(int maxAge, PropertyDealType dealType, int* count) {
    char filename[256];
    char log_message[256];
    ResidentialProperty* results = NULL;
    *count = 0;
    
    // انتخاب فایل بر اساس نوع معامله
    if (dealType == PROPERTY_DEAL_SALE) {
        strcpy(filename, RESIDENTIAL_SALES_PATH);
    } else if (dealType == PROPERTY_DEAL_RENT) {
        strcpy(filename, RESIDENTIAL_RENTALS_PATH);
    } else {
        property_log("ERROR", "نوع معامله نامعتبر در جستجوی املاک مسکونی بر اساس سن ساختمان");
        return NULL;
    }
    
    // باز کردن فایل
    FILE* file = fopen(filename, "rb");
    if (!file) {
        snprintf(log_message, sizeof(log_message), 
                 "خطای باز کردن فایل برای جستجوی املاک مسکونی با سن حداکثر %d سال", maxAge);
        property_log("ERROR", log_message);
        return NULL;
    }
    
    // شمارش تعداد املاک واجد شرایط
    char line[1024];
    int match_count = 0;
    
    while (fgets(line, sizeof(line), file)) {
        ResidentialProperty temp;
        int id, municipality_district, is_active, building_age, bedrooms, floor;
        int total_floors, has_elevator, has_parking, has_storage, timestamp;
        float area_size;
        double selling_price, mortgage_amount, monthly_rent;
        char address[100], owner_phone[20], reg_date[11], del_date[11], reg_by[50], status[20];
        
        // خواندن داده‌ها از خط فایل
        sscanf(line, "%d,%d,%[^,],%[^,],%d,%[^,],%[^,],%d,%f,%d,%d,%d,%d,%d,%d,%lf,%lf,%lf,%[^,],%[^,],%d,%s",
               &id, &municipality_district, address, owner_phone, &building_age, reg_date, del_date, 
               &is_active, &area_size, &bedrooms, &floor, &total_floors, &has_elevator, 
               &has_parking, &has_storage, &selling_price, &mortgage_amount, &monthly_rent, 
               reg_by, status, &timestamp, status);
        
        // بررسی شرایط جستجو
        if (is_active == PROPERTY_STATUS_ACTIVE && building_age <= maxAge) {
            match_count++;
        }
    }
    
    // اگر هیچ موردی پیدا نشد
    if (match_count == 0) {
        fclose(file);
        return NULL;
    }
    
    // تخصیص حافظه برای نتایج
    results = (ResidentialProperty*)malloc(match_count * sizeof(ResidentialProperty));
    if (!results) {
        property_log("ERROR", "خطای تخصیص حافظه در جستجوی املاک مسکونی");
        fclose(file);
        return NULL;
    }
    
    // بازگشت به ابتدای فایل
    rewind(file);
    
    // خواندن و ذخیره املاک واجد شرایط
    int index = 0;
    while (fgets(line, sizeof(line), file) && index < match_count) {
        ResidentialProperty* property = &results[index];
        int id, municipality_district, is_active, building_age, bedrooms, floor;
        int total_floors, has_elevator, has_parking, has_storage, timestamp;
        float area_size;
        double selling_price, mortgage_amount, monthly_rent;
        char address[100], owner_phone[20], reg_date[11], del_date[11], reg_by[50], status[20];
        
        // خواندن داده‌ها از خط فایل
        sscanf(line, "%d,%d,%[^,],%[^,],%d,%[^,],%[^,],%d,%f,%d,%d,%d,%d,%d,%d,%lf,%lf,%lf,%[^,],%[^,],%d,%s",
               &id, &municipality_district, address, owner_phone, &building_age, reg_date, del_date, 
               &is_active, &area_size, &bedrooms, &floor, &total_floors, &has_elevator, 
               &has_parking, &has_storage, &selling_price, &mortgage_amount, &monthly_rent, 
               reg_by, status, &timestamp, status);
        
        // بررسی شرایط جستجو و ذخیره نتایج
        if (is_active == PROPERTY_STATUS_ACTIVE && building_age <= maxAge) {
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
            property->bedrooms = bedrooms;
            property->floor = floor;
            property->totalFloors = total_floors;
            property->hasElevator = has_elevator;
            property->hasParking = has_parking;
            property->hasStorage = has_storage;
            property->sellingPrice = selling_price;
            property->mortgageAmount = mortgage_amount;
            property->monthlyRentAmount = monthly_rent;
            
            index++;
        }
    }
    
    fclose(file);
    *count = index;
    
    snprintf(log_message, sizeof(log_message), 
             "جستجوی املاک مسکونی با سن حداکثر %d سال: %d مورد یافت شد", maxAge, index);
    property_log("INFO", log_message);
    
    return results;
}

ResidentialProperty* residential_find_by_area(float minArea, float maxArea, PropertyDealType dealType, int* count) {
    char filename[256];
    char log_message[256];
    ResidentialProperty* results = NULL;
    *count = 0;
    
    // انتخاب فایل بر اساس نوع معامله
    if (dealType == PROPERTY_DEAL_SALE) {
        strcpy(filename, RESIDENTIAL_SALES_PATH);
    } else if (dealType == PROPERTY_DEAL_RENT) {
        strcpy(filename, RESIDENTIAL_RENTALS_PATH);
    } else {
        property_log("ERROR", "نوع معامله نامعتبر در جستجوی املاک مسکونی بر اساس مساحت");
        return NULL;
    }
    
    // باز کردن فایل
    FILE* file = fopen(filename, "rb");
    if (!file) {
        snprintf(log_message, sizeof(log_message), 
                 "خطای باز کردن فایل برای جستجوی املاک مسکونی با مساحت بین %f و %f متر", minArea, maxArea);
        property_log("ERROR", log_message);
        return NULL;
    }
    
    // شمارش تعداد املاک واجد شرایط
    char line[1024];
    int match_count = 0;
    
    while (fgets(line, sizeof(line), file)) {
        int id, municipality_district, is_active, building_age, bedrooms, floor;
        int total_floors, has_elevator, has_parking, has_storage, timestamp;
        float area_size;
        double selling_price, mortgage_amount, monthly_rent;
        char address[100], owner_phone[20], reg_date[11], del_date[11], reg_by[50], status[20];
        
        // خواندن داده‌ها از خط فایل
        sscanf(line, "%d,%d,%[^,],%[^,],%d,%[^,],%[^,],%d,%f,%d,%d,%d,%d,%d,%d,%lf,%lf,%lf,%[^,],%[^,],%d,%s",
               &id, &municipality_district, address, owner_phone, &building_age, reg_date, del_date, 
               &is_active, &area_size, &bedrooms, &floor, &total_floors, &has_elevator, 
               &has_parking, &has_storage, &selling_price, &mortgage_amount, &monthly_rent, 
               reg_by, status, &timestamp, status);
        
        // بررسی شرایط جستجو
        if (is_active == PROPERTY_STATUS_ACTIVE && 
            (minArea == 0 || area_size >= minArea) && 
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
    results = (ResidentialProperty*)malloc(match_count * sizeof(ResidentialProperty));
    if (!results) {
        property_log("ERROR", "خطای تخصیص حافظه در جستجوی املاک مسکونی");
        fclose(file);
        return NULL;
    }
    
    // بازگشت به ابتدای فایل
    rewind(file);
    
    // خواندن و ذخیره املاک واجد شرایط
    int index = 0;
    while (fgets(line, sizeof(line), file) && index < match_count) {
        ResidentialProperty* property = &results[index];
        int id, municipality_district, is_active, building_age, bedrooms, floor;
        int total_floors, has_elevator, has_parking, has_storage, timestamp;
        float area_size;
        double selling_price, mortgage_amount, monthly_rent;
        char address[100], owner_phone[20], reg_date[11], del_date[11], reg_by[50], status[20];
        
        // خواندن داده‌ها از خط فایل
        sscanf(line, "%d,%d,%[^,],%[^,],%d,%[^,],%[^,],%d,%f,%d,%d,%d,%d,%d,%d,%lf,%lf,%lf,%[^,],%[^,],%d,%s",
               &id, &municipality_district, address, owner_phone, &building_age, reg_date, del_date, 
               &is_active, &area_size, &bedrooms, &floor, &total_floors, &has_elevator, 
               &has_parking, &has_storage, &selling_price, &mortgage_amount, &monthly_rent, 
               reg_by, status, &timestamp, status);
        
        // بررسی شرایط جستجو و ذخیره نتایج
        if (is_active == PROPERTY_STATUS_ACTIVE && 
            (minArea == 0 || area_size >= minArea) && 
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
            property->bedrooms = bedrooms;
            property->floor = floor;
            property->totalFloors = total_floors;
            property->hasElevator = has_elevator;
            property->hasParking = has_parking;
            property->hasStorage = has_storage;
            property->sellingPrice = selling_price;
            property->mortgageAmount = mortgage_amount;
            property->monthlyRentAmount = monthly_rent;
            
            index++;
        }
    }
    
    fclose(file);
    *count = index;
    
    snprintf(log_message, sizeof(log_message), 
             "جستجوی املاک مسکونی با مساحت بین %f و %f متر: %d مورد یافت شد", 
             minArea, maxArea, index);
    property_log("INFO", log_message);
    
    return results;
}

ResidentialProperty* residential_find_by_bedrooms(int minBedrooms, int maxBedrooms, PropertyDealType dealType, int* count) {
    char filename[256];
    char log_message[256];
    ResidentialProperty* results = NULL;
    *count = 0;
    
    // انتخاب فایل بر اساس نوع معامله
    if (dealType == PROPERTY_DEAL_SALE) {
        strcpy(filename, RESIDENTIAL_SALES_PATH);
    } else if (dealType == PROPERTY_DEAL_RENT) {
        strcpy(filename, RESIDENTIAL_RENTALS_PATH);
    } else {
        property_log("ERROR", "نوع معامله نامعتبر در جستجوی املاک مسکونی بر اساس تعداد اتاق خواب");
        return NULL;
    }
    
    // باز کردن فایل
    FILE* file = fopen(filename, "rb");
    if (!file) {
        snprintf(log_message, sizeof(log_message), 
                 "خطای باز کردن فایل برای جستجوی املاک مسکونی با تعداد اتاق خواب بین %d و %d", 
                 minBedrooms, maxBedrooms);
        property_log("ERROR", log_message);
        return NULL;
    }
    
    // شمارش تعداد املاک واجد شرایط
    char line[1024];
    int match_count = 0;
    
    while (fgets(line, sizeof(line), file)) {
        int id, municipality_district, is_active, building_age, bedrooms, floor;
        int total_floors, has_elevator, has_parking, has_storage, timestamp;
        float area_size;
        double selling_price, mortgage_amount, monthly_rent;
        char address[100], owner_phone[20], reg_date[11], del_date[11], reg_by[50], status[20];
        
        // خواندن داده‌ها از خط فایل
        sscanf(line, "%d,%d,%[^,],%[^,],%d,%[^,],%[^,],%d,%f,%d,%d,%d,%d,%d,%d,%lf,%lf,%lf,%[^,],%[^,],%d,%s",
               &id, &municipality_district, address, owner_phone, &building_age, reg_date, del_date, 
               &is_active, &area_size, &bedrooms, &floor, &total_floors, &has_elevator, 
               &has_parking, &has_storage, &selling_price, &mortgage_amount, &monthly_rent, 
               reg_by, status, &timestamp, status);
        
        // بررسی شرایط جستجو
        if (is_active == PROPERTY_STATUS_ACTIVE && 
            (minBedrooms == 0 || bedrooms >= minBedrooms) && 
            (maxBedrooms == 0 || bedrooms <= maxBedrooms)) {
            match_count++;
        }
    }
    
    // اگر هیچ موردی پیدا نشد
    if (match_count == 0) {
        fclose(file);
        return NULL;
    }
    
    // تخصیص حافظه برای نتایج
    results = (ResidentialProperty*)malloc(match_count * sizeof(ResidentialProperty));
    if (!results) {
        property_log("ERROR", "خطای تخصیص حافظه در جستجوی املاک مسکونی");
        fclose(file);
        return NULL;
    }
    
    // بازگشت به ابتدای فایل
    rewind(file);
    
    // خواندن و ذخیره املاک واجد شرایط
    int index = 0;
    while (fgets(line, sizeof(line), file) && index < match_count) {
        ResidentialProperty* property = &results[index];
        int id, municipality_district, is_active, building_age, bedrooms, floor;
        int total_floors, has_elevator, has_parking, has_storage, timestamp;
        float area_size;
        double selling_price, mortgage_amount, monthly_rent;
        char address[100], owner_phone[20], reg_date[11], del_date[11], reg_by[50], status[20];
        
        // خواندن داده‌ها از خط فایل
        sscanf(line, "%d,%d,%[^,],%[^,],%d,%[^,],%[^,],%d,%f,%d,%d,%d,%d,%d,%d,%lf,%lf,%lf,%[^,],%[^,],%d,%s",
               &id, &municipality_district, address, owner_phone, &building_age, reg_date, del_date, 
               &is_active, &area_size, &bedrooms, &floor, &total_floors, &has_elevator, 
               &has_parking, &has_storage, &selling_price, &mortgage_amount, &monthly_rent, 
               reg_by, status, &timestamp, status);
        
        // بررسی شرایط جستجو و ذخیره نتایج
        if (is_active == PROPERTY_STATUS_ACTIVE && 
            (minBedrooms == 0 || bedrooms >= minBedrooms) && 
            (maxBedrooms == 0 || bedrooms <= maxBedrooms)) {
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
            property->bedrooms = bedrooms;
            property->floor = floor;
            property->totalFloors = total_floors;
            property->hasElevator = has_elevator;
            property->hasParking = has_parking;
            property->hasStorage = has_storage;
            property->sellingPrice = selling_price;
            property->mortgageAmount = mortgage_amount;
            property->monthlyRentAmount = monthly_rent;
            
            index++;
        }
    }
    
    fclose(file);
    *count = index;
    
    snprintf(log_message, sizeof(log_message), 
             "جستجوی املاک مسکونی با تعداد اتاق خواب بین %d و %d: %d مورد یافت شد", 
             minBedrooms, maxBedrooms, index);
    property_log("INFO", log_message);
    
    return results;
}

ResidentialProperty* residential_find_by_price(double minPrice, double maxPrice, PropertyDealType dealType, int* count) {
    char filename[256];
    char log_message[256];
    ResidentialProperty* results = NULL;
    *count = 0;
    
    // انتخاب فایل بر اساس نوع معامله
    if (dealType == PROPERTY_DEAL_SALE) {
        strcpy(filename, RESIDENTIAL_SALES_PATH);
    } else if (dealType == PROPERTY_DEAL_RENT) {
        strcpy(filename, RESIDENTIAL_RENTALS_PATH);
    } else {
        property_log("ERROR", "نوع معامله نامعتبر در جستجوی املاک مسکونی بر اساس قیمت");
        return NULL;
    }
    
    // باز کردن فایل
    FILE* file = fopen(filename, "rb");
    if (!file) {
        snprintf(log_message, sizeof(log_message), 
                 "خطای باز کردن فایل برای جستجوی املاک مسکونی با قیمت بین %f و %f تومان", 
                 minPrice, maxPrice);
        property_log("ERROR", log_message);
        return NULL;
    }
    
    // شمارش تعداد املاک واجد شرایط
    char line[1024];
    int match_count = 0;
    
    while (fgets(line, sizeof(line), file)) {
        int id, municipality_district, is_active, building_age, bedrooms, floor;
        int total_floors, has_elevator, has_parking, has_storage, timestamp;
        float area_size;
        double selling_price, mortgage_amount, monthly_rent;
        char address[100], owner_phone[20], reg_date[11], del_date[11], reg_by[50], status[20];
        
        // خواندن داده‌ها از خط فایل
        sscanf(line, "%d,%d,%[^,],%[^,],%d,%[^,],%[^,],%d,%f,%d,%d,%d,%d,%d,%d,%lf,%lf,%lf,%[^,],%[^,],%d,%s",
               &id, &municipality_district, address, owner_phone, &building_age, reg_date, del_date, 
               &is_active, &area_size, &bedrooms, &floor, &total_floors, &has_elevator, 
               &has_parking, &has_storage, &selling_price, &mortgage_amount, &monthly_rent, 
               reg_by, status, &timestamp, status);
        
        // بررسی شرایط جستجو برای فروش یا اجاره
        if (is_active == PROPERTY_STATUS_ACTIVE) {
            if (dealType == PROPERTY_DEAL_SALE) {
                if ((minPrice == 0 || selling_price >= minPrice) && 
                    (maxPrice == 0 || selling_price <= maxPrice)) {
                    match_count++;
                }
            } else { // PROPERTY_DEAL_RENT
                // برای اجاره: کل ارزش ملک = رهن + (اجاره × 12)
                double total_value = mortgage_amount + (monthly_rent * 12);
                if ((minPrice == 0 || total_value >= minPrice) && 
                    (maxPrice == 0 || total_value <= maxPrice)) {
                    match_count++;
                }
            }
        }
    }
    
    // اگر هیچ موردی پیدا نشد
    if (match_count == 0) {
        fclose(file);
        return NULL;
    }
    
    // تخصیص حافظه برای نتایج
    results = (ResidentialProperty*)malloc(match_count * sizeof(ResidentialProperty));
    if (!results) {
        property_log("ERROR", "خطای تخصیص حافظه در جستجوی املاک مسکونی");
        fclose(file);
        return NULL;
    }
    
    // بازگشت به ابتدای فایل
    rewind(file);
    
    // خواندن و ذخیره املاک واجد شرایط
    int index = 0;
    while (fgets(line, sizeof(line), file) && index < match_count) {
        ResidentialProperty* property = &results[index];
        int id, municipality_district, is_active, building_age, bedrooms, floor;
        int total_floors, has_elevator, has_parking, has_storage, timestamp;
        float area_size;
        double selling_price, mortgage_amount, monthly_rent;
        char address[100], owner_phone[20], reg_date[11], del_date[11], reg_by[50], status[20];
        
        // خواندن داده‌ها از خط فایل
        sscanf(line, "%d,%d,%[^,],%[^,],%d,%[^,],%[^,],%d,%f,%d,%d,%d,%d,%d,%d,%lf,%lf,%lf,%[^,],%[^,],%d,%s",
               &id, &municipality_district, address, owner_phone, &building_age, reg_date, del_date, 
               &is_active, &area_size, &bedrooms, &floor, &total_floors, &has_elevator, 
               &has_parking, &has_storage, &selling_price, &mortgage_amount, &monthly_rent, 
               reg_by, status, &timestamp, status);
        
        // بررسی شرایط جستجو و ذخیره نتایج
        if (is_active == PROPERTY_STATUS_ACTIVE) {
            int match = 0;
            
            if (dealType == PROPERTY_DEAL_SALE) {
                if ((minPrice == 0 || selling_price >= minPrice) && 
                    (maxPrice == 0 || selling_price <= maxPrice)) {
                    match = 1;
                }
            } else { // PROPERTY_DEAL_RENT
                double total_value = mortgage_amount + (monthly_rent * 12);
                if ((minPrice == 0 || total_value >= minPrice) && 
                    (maxPrice == 0 || total_value <= maxPrice)) {
                    match = 1;
                }
            }
            
            if (match) {
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
                property->bedrooms = bedrooms;
                property->floor = floor;
                property->totalFloors = total_floors;
                property->hasElevator = has_elevator;
                property->hasParking = has_parking;
                property->hasStorage = has_storage;
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
             "جستجوی املاک مسکونی با قیمت بین %f و %f تومان: %d مورد یافت شد", 
             minPrice, maxPrice, index);
    property_log("INFO", log_message);
    
    return results;
}

ResidentialProperty* residential_find_by_floor(int minFloor, int maxFloor, PropertyDealType dealType, int* count) {
    char filename[256];
    char log_message[256];
    ResidentialProperty* results = NULL;
    *count = 0;
    
    // انتخاب فایل بر اساس نوع معامله
    if (dealType == PROPERTY_DEAL_SALE) {
        strcpy(filename, RESIDENTIAL_SALES_PATH);
    } else if (dealType == PROPERTY_DEAL_RENT) {
        strcpy(filename, RESIDENTIAL_RENTALS_PATH);
    } else {
        property_log("ERROR", "نوع معامله نامعتبر در جستجوی املاک مسکونی بر اساس طبقه");
        return NULL;
    }
    
    // باز کردن فایل
    FILE* file = fopen(filename, "rb");
    if (!file) {
        snprintf(log_message, sizeof(log_message), 
                 "خطای باز کردن فایل برای جستجوی املاک مسکونی با طبقه بین %d و %d", 
                 minFloor, maxFloor);
        property_log("ERROR", log_message);
        return NULL;
    }
    
    // شمارش تعداد املاک واجد شرایط
    char line[1024];
    int match_count = 0;
    
    while (fgets(line, sizeof(line), file)) {
        int id, municipality_district, is_active, building_age, bedrooms, floor;
        int total_floors, has_elevator, has_parking, has_storage, timestamp;
        float area_size;
        double selling_price, mortgage_amount, monthly_rent;
        char address[100], owner_phone[20], reg_date[11], del_date[11], reg_by[50], status[20];
        
        // خواندن داده‌ها از خط فایل
        sscanf(line, "%d,%d,%[^,],%[^,],%d,%[^,],%[^,],%d,%f,%d,%d,%d,%d,%d,%d,%lf,%lf,%lf,%[^,],%[^,],%d,%s",
               &id, &municipality_district, address, owner_phone, &building_age, reg_date, del_date, 
               &is_active, &area_size, &bedrooms, &floor, &total_floors, &has_elevator, 
               &has_parking, &has_storage, &selling_price, &mortgage_amount, &monthly_rent, 
               reg_by, status, &timestamp, status);
        
        // بررسی شرایط جستجو
        if (is_active == PROPERTY_STATUS_ACTIVE && 
            (minFloor == 0 || floor >= minFloor) && 
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
    results = (ResidentialProperty*)malloc(match_count * sizeof(ResidentialProperty));
    if (!results) {
        property_log("ERROR", "خطای تخصیص حافظه در جستجوی املاک مسکونی");
        fclose(file);
        return NULL;
    }
    
    // بازگشت به ابتدای فایل
    rewind(file);
    
    // خواندن و ذخیره املاک واجد شرایط
    int index = 0;
    while (fgets(line, sizeof(line), file) && index < match_count) {
        ResidentialProperty* property = &results[index];
        int id, municipality_district, is_active, building_age, bedrooms, floor;
        int total_floors, has_elevator, has_parking, has_storage, timestamp;
        float area_size;
        double selling_price, mortgage_amount, monthly_rent;
        char address[100], owner_phone[20], reg_date[11], del_date[11], reg_by[50], status[20];
        
        // خواندن داده‌ها از خط فایل
        sscanf(line, "%d,%d,%[^,],%[^,],%d,%[^,],%[^,],%d,%f,%d,%d,%d,%d,%d,%d,%lf,%lf,%lf,%[^,],%[^,],%d,%s",
               &id, &municipality_district, address, owner_phone, &building_age, reg_date, del_date, 
               &is_active, &area_size, &bedrooms, &floor, &total_floors, &has_elevator, 
               &has_parking, &has_storage, &selling_price, &mortgage_amount, &monthly_rent, 
               reg_by, status, &timestamp, status);
        
        // بررسی شرایط جستجو و ذخیره نتایج
        if (is_active == PROPERTY_STATUS_ACTIVE && 
            (minFloor == 0 || floor >= minFloor) && 
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
            property->bedrooms = bedrooms;
            property->floor = floor;
            property->totalFloors = total_floors;
            property->hasElevator = has_elevator;
            property->hasParking = has_parking;
            property->hasStorage = has_storage;
            property->sellingPrice = selling_price;
            property->mortgageAmount = mortgage_amount;
            property->monthlyRentAmount = monthly_rent;
            
            index++;
        }
    }
    
    fclose(file);
    *count = index;
    
    snprintf(log_message, sizeof(log_message), 
             "جستجوی املاک مسکونی با طبقه بین %d و %d: %d مورد یافت شد", 
             minFloor, maxFloor, index);
    property_log("INFO", log_message);
    
    return results;
}

ResidentialProperty* residential_find_with_elevator(PropertyDealType dealType, int* count) {
    char filename[256];
    char log_message[256];
    ResidentialProperty* results = NULL;
    *count = 0;
    
    // انتخاب فایل بر اساس نوع معامله
    if (dealType == PROPERTY_DEAL_SALE) {
        strcpy(filename, RESIDENTIAL_SALES_PATH);
    } else if (dealType == PROPERTY_DEAL_RENT) {
        strcpy(filename, RESIDENTIAL_RENTALS_PATH);
    } else {
        property_log("ERROR", "نوع معامله نامعتبر در جستجوی املاک مسکونی دارای آسانسور");
        return NULL;
    }
    
    // باز کردن فایل
    FILE* file = fopen(filename, "rb");
    if (!file) {
        property_log("ERROR", "خطای باز کردن فایل برای جستجوی املاک مسکونی دارای آسانسور");
        return NULL;
    }
    
    // شمارش تعداد املاک واجد شرایط
    char line[1024];
    int match_count = 0;
    
    while (fgets(line, sizeof(line), file)) {
        int id, municipality_district, is_active, building_age, bedrooms, floor;
        int total_floors, has_elevator, has_parking, has_storage, timestamp;
        float area_size;
        double selling_price, mortgage_amount, monthly_rent;
        char address[100], owner_phone[20], reg_date[11], del_date[11], reg_by[50], status[20];
        
        // خواندن داده‌ها از خط فایل
        sscanf(line, "%d,%d,%[^,],%[^,],%d,%[^,],%[^,],%d,%f,%d,%d,%d,%d,%d,%d,%lf,%lf,%lf,%[^,],%[^,],%d,%s",
               &id, &municipality_district, address, owner_phone, &building_age, reg_date, del_date, 
               &is_active, &area_size, &bedrooms, &floor, &total_floors, &has_elevator, 
               &has_parking, &has_storage, &selling_price, &mortgage_amount, &monthly_rent, 
               reg_by, status, &timestamp, status);
        
        // بررسی شرایط جستجو
        if (is_active == PROPERTY_STATUS_ACTIVE && has_elevator == 1) {
            match_count++;
        }
    }
    
    // اگر هیچ موردی پیدا نشد
    if (match_count == 0) {
        fclose(file);
        return NULL;
    }
    
    // تخصیص حافظه برای نتایج
    results = (ResidentialProperty*)malloc(match_count * sizeof(ResidentialProperty));
    if (!results) {
        property_log("ERROR", "خطای تخصیص حافظه در جستجوی املاک مسکونی");
        fclose(file);
        return NULL;
    }
    
    // بازگشت به ابتدای فایل
    rewind(file);
    
    // خواندن و ذخیره املاک واجد شرایط
    int index = 0;
    while (fgets(line, sizeof(line), file) && index < match_count) {
        ResidentialProperty* property = &results[index];
        int id, municipality_district, is_active, building_age, bedrooms, floor;
        int total_floors, has_elevator, has_parking, has_storage, timestamp;
        float area_size;
        double selling_price, mortgage_amount, monthly_rent;
        char address[100], owner_phone[20], reg_date[11], del_date[11], reg_by[50], status[20];
        
        // خواندن داده‌ها از خط فایل
        sscanf(line, "%d,%d,%[^,],%[^,],%d,%[^,],%[^,],%d,%f,%d,%d,%d,%d,%d,%d,%lf,%lf,%lf,%[^,],%[^,],%d,%s",
               &id, &municipality_district, address, owner_phone, &building_age, reg_date, del_date, 
               &is_active, &area_size, &bedrooms, &floor, &total_floors, &has_elevator, 
               &has_parking, &has_storage, &selling_price, &mortgage_amount, &monthly_rent, 
               reg_by, status, &timestamp, status);
        
        // بررسی شرایط جستجو و ذخیره نتایج
        if (is_active == PROPERTY_STATUS_ACTIVE && has_elevator == 1) {
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
            property->bedrooms = bedrooms;
            property->floor = floor;
            property->totalFloors = total_floors;
            property->hasElevator = has_elevator;
            property->hasParking = has_parking;
            property->hasStorage = has_storage;
            property->sellingPrice = selling_price;
            property->mortgageAmount = mortgage_amount;
            property->monthlyRentAmount = monthly_rent;
            
            index++;
        }
    }
    
    fclose(file);
    *count = index;
    
    snprintf(log_message, sizeof(log_message), 
             "جستجوی املاک مسکونی دارای آسانسور: %d مورد یافت شد", index);
    property_log("INFO", log_message);
    
    return results;
}

ResidentialProperty* residential_find_with_parking(PropertyDealType dealType, int* count) {
    char filename[256];
    char log_message[256];
    ResidentialProperty* results = NULL;
    *count = 0;
    
    // انتخاب فایل بر اساس نوع معامله
    if (dealType == PROPERTY_DEAL_SALE) {
        strcpy(filename, RESIDENTIAL_SALES_PATH);
    } else if (dealType == PROPERTY_DEAL_RENT) {
        strcpy(filename, RESIDENTIAL_RENTALS_PATH);
    } else {
        property_log("ERROR", "نوع معامله نامعتبر در جستجوی املاک مسکونی دارای پارکینگ");
        return NULL;
    }
    
    // باز کردن فایل
    FILE* file = fopen(filename, "rb");
    if (!file) {
        property_log("ERROR", "خطای باز کردن فایل برای جستجوی املاک مسکونی دارای پارکینگ");
        return NULL;
    }
    
    // شمارش تعداد املاک واجد شرایط
    char line[1024];
    int match_count = 0;
    
    while (fgets(line, sizeof(line), file)) {
        int id, municipality_district, is_active, building_age, bedrooms, floor;
        int total_floors, has_elevator, has_parking, has_storage, timestamp;
        float area_size;
        double selling_price, mortgage_amount, monthly_rent;
        char address[100], owner_phone[20], reg_date[11], del_date[11], reg_by[50], status[20];
        
        // خواندن داده‌ها از خط فایل
        sscanf(line, "%d,%d,%[^,],%[^,],%d,%[^,],%[^,],%d,%f,%d,%d,%d,%d,%d,%d,%lf,%lf,%lf,%[^,],%[^,],%d,%s",
               &id, &municipality_district, address, owner_phone, &building_age, reg_date, del_date, 
               &is_active, &area_size, &bedrooms, &floor, &total_floors, &has_elevator, 
               &has_parking, &has_storage, &selling_price, &mortgage_amount, &monthly_rent, 
               reg_by, status, &timestamp, status);
        
        // بررسی شرایط جستجو
        if (is_active == PROPERTY_STATUS_ACTIVE && has_parking == 1) {
            match_count++;
        }
    }
    
    // اگر هیچ موردی پیدا نشد
    if (match_count == 0) {
        fclose(file);
        return NULL;
    }
    
    // تخصیص حافظه برای نتایج
    results = (ResidentialProperty*)malloc(match_count * sizeof(ResidentialProperty));
    if (!results) {
        property_log("ERROR", "خطای تخصیص حافظه در جستجوی املاک مسکونی");
        fclose(file);
        return NULL;
    }
    
    // بازگشت به ابتدای فایل
    rewind(file);
    
    // خواندن و ذخیره املاک واجد شرایط
    int index = 0;
    while (fgets(line, sizeof(line), file) && index < match_count) {
        ResidentialProperty* property = &results[index];
        int id, municipality_district, is_active, building_age, bedrooms, floor;
        int total_floors, has_elevator, has_parking, has_storage, timestamp;
        float area_size;
        double selling_price, mortgage_amount, monthly_rent;
        char address[100], owner_phone[20], reg_date[11], del_date[11], reg_by[50], status[20];
        
        // خواندن داده‌ها از خط فایل
        sscanf(line, "%d,%d,%[^,],%[^,],%d,%[^,],%[^,],%d,%f,%d,%d,%d,%d,%d,%d,%lf,%lf,%lf,%[^,],%[^,],%d,%s",
               &id, &municipality_district, address, owner_phone, &building_age, reg_date, del_date, 
               &is_active, &area_size, &bedrooms, &floor, &total_floors, &has_elevator, 
               &has_parking, &has_storage, &selling_price, &mortgage_amount, &monthly_rent, 
               reg_by, status, &timestamp, status);
        
        // بررسی شرایط جستجو و ذخیره نتایج
        if (is_active == PROPERTY_STATUS_ACTIVE && has_parking == 1) {
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
            property->bedrooms = bedrooms;
            property->floor = floor;
            property->totalFloors = total_floors;
            property->hasElevator = has_elevator;
            property->hasParking = has_parking;
            property->hasStorage = has_storage;
            property->sellingPrice = selling_price;
            property->mortgageAmount = mortgage_amount;
            property->monthlyRentAmount = monthly_rent;
            
            index++;
        }
    }
    
    fclose(file);
    *count = index;
    
    snprintf(log_message, sizeof(log_message), 
             "جستجوی املاک مسکونی دارای پارکینگ: %d مورد یافت شد", index);
    property_log("INFO", log_message);
    
    return results;
}

ResidentialProperty* residential_find_with_storage(PropertyDealType dealType, int* count) {
    char filename[256];
    char log_message[256];
    ResidentialProperty* results = NULL;
    *count = 0;
    
    // انتخاب فایل بر اساس نوع معامله
    if (dealType == PROPERTY_DEAL_SALE) {
        strcpy(filename, RESIDENTIAL_SALES_PATH);
    } else if (dealType == PROPERTY_DEAL_RENT) {
        strcpy(filename, RESIDENTIAL_RENTALS_PATH);
    } else {
        property_log("ERROR", "نوع معامله نامعتبر در جستجوی املاک مسکونی دارای انباری");
        return NULL;
    }
    
    // باز کردن فایل
    FILE* file = fopen(filename, "rb");
    if (!file) {
        property_log("ERROR", "خطای باز کردن فایل برای جستجوی املاک مسکونی دارای انباری");
        return NULL;
    }
    
    // شمارش تعداد املاک واجد شرایط
    char line[1024];
    int match_count = 0;
    
    while (fgets(line, sizeof(line), file)) {
        int id, municipality_district, is_active, building_age, bedrooms, floor;
        int total_floors, has_elevator, has_parking, has_storage, timestamp;
        float area_size;
        double selling_price, mortgage_amount, monthly_rent;
        char address[100], owner_phone[20], reg_date[11], del_date[11], reg_by[50], status[20];
        
        // خواندن داده‌ها از خط فایل
        sscanf(line, "%d,%d,%[^,],%[^,],%d,%[^,],%[^,],%d,%f,%d,%d,%d,%d,%d,%d,%lf,%lf,%lf,%[^,],%[^,],%d,%s",
               &id, &municipality_district, address, owner_phone, &building_age, reg_date, del_date, 
               &is_active, &area_size, &bedrooms, &floor, &total_floors, &has_elevator, 
               &has_parking, &has_storage, &selling_price, &mortgage_amount, &monthly_rent, 
               reg_by, status, &timestamp, status);
        
        // بررسی شرایط جستجو
        if (is_active == PROPERTY_STATUS_ACTIVE && has_storage == 1) {
            match_count++;
        }
    }
    
    // اگر هیچ موردی پیدا نشد
    if (match_count == 0) {
        fclose(file);
        return NULL;
    }
    
    // تخصیص حافظه برای نتایج
    results = (ResidentialProperty*)malloc(match_count * sizeof(ResidentialProperty));
    if (!results) {
        property_log("ERROR", "خطای تخصیص حافظه در جستجوی املاک مسکونی");
        fclose(file);
        return NULL;
    }
    
    // بازگشت به ابتدای فایل
    rewind(file);
    
    // خواندن و ذخیره املاک واجد شرایط
    int index = 0;
    while (fgets(line, sizeof(line), file) && index < match_count) {
        ResidentialProperty* property = &results[index];
        int id, municipality_district, is_active, building_age, bedrooms, floor;
        int total_floors, has_elevator, has_parking, has_storage, timestamp;
        float area_size;
        double selling_price, mortgage_amount, monthly_rent;
        char address[100], owner_phone[20], reg_date[11], del_date[11], reg_by[50], status[20];
        
        // خواندن داده‌ها از خط فایل
        sscanf(line, "%d,%d,%[^,],%[^,],%d,%[^,],%[^,],%d,%f,%d,%d,%d,%d,%d,%d,%lf,%lf,%lf,%[^,],%[^,],%d,%s",
               &id, &municipality_district, address, owner_phone, &building_age, reg_date, del_date, 
               &is_active, &area_size, &bedrooms, &floor, &total_floors, &has_elevator, 
               &has_parking, &has_storage, &selling_price, &mortgage_amount, &monthly_rent, 
               reg_by, status, &timestamp, status);
        
        // بررسی شرایط جستجو و ذخیره نتایج
        if (is_active == PROPERTY_STATUS_ACTIVE && has_storage == 1) {
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
            property->bedrooms = bedrooms;
            property->floor = floor;
            property->totalFloors = total_floors;
            property->hasElevator = has_elevator;
            property->hasParking = has_parking;
            property->hasStorage = has_storage;
            property->sellingPrice = selling_price;
            property->mortgageAmount = mortgage_amount;
            property->monthlyRentAmount = monthly_rent;
            
            index++;
        }
    }
    
    fclose(file);
    *count = index;
    
    snprintf(log_message, sizeof(log_message), 
             "جستجوی املاک مسکونی دارای انباری: %d مورد یافت شد", index);
    property_log("INFO", log_message);
    
    return results;
}

// ... existing code ...
ResidentialProperty* residential_find_deleted_by_date(const char* startDate, const char* endDate, 
                                                 PropertyDealType dealType, int* count) {
    char filename[256];
    char log_message[256];
    ResidentialProperty* results = NULL;
    *count = 0;
    
    // بررسی پارامترهای ورودی
    if (!startDate || !endDate) {
        property_log("ERROR", "Invalid input dates for deleted residential property search");
        return NULL;
    }
    
    // انتخاب فایل بر اساس نوع معامله
    if (dealType == PROPERTY_DEAL_SALE) {
        strcpy(filename, RESIDENTIAL_SALES_PATH);
    } else if (dealType == PROPERTY_DEAL_RENT) {
        strcpy(filename, RESIDENTIAL_RENTALS_PATH);
    } else {
        property_log("ERROR", "Invalid deal type for deleted residential property search");
        return NULL;
    }
    
    // باز کردن فایل
    FILE* file = fopen(filename, "rb");
    if (!file) {
        snprintf(log_message, sizeof(log_message), 
                 "Error opening file for deleted residential properties between %s and %s", 
                 startDate, endDate);
        property_log("ERROR", log_message);
        return NULL;
    }
    
    // شمارش تعداد املاک واجد شرایط
    char line[1024];
    int match_count = 0;
    
    while (fgets(line, sizeof(line), file)) {
        int id, municipality_district, is_active, building_age, bedrooms, floor;
        int total_floors, has_elevator, has_parking, has_storage, timestamp;
        float area_size;
        double selling_price, mortgage_amount, monthly_rent;
        char address[100], owner_phone[20], reg_date[11], del_date[11], reg_by[50], status[20];
        
        // خواندن داده‌ها از خط فایل
        sscanf(line, "%d,%d,%[^,],%[^,],%d,%[^,],%[^,],%d,%f,%d,%d,%d,%d,%d,%d,%lf,%lf,%lf,%[^,],%[^,],%d,%s",
               &id, &municipality_district, address, owner_phone, &building_age, reg_date, del_date, 
               &is_active, &area_size, &bedrooms, &floor, &total_floors, &has_elevator, 
               &has_parking, &has_storage, &selling_price, &mortgage_amount, &monthly_rent, 
               reg_by, status, &timestamp, status);
        
        // اگر ملک حذف شده است و تاریخ آن در محدوده مورد نظر است
        if (strlen(del_date) > 0 && is_active == PROPERTY_STATUS_INACTIVE) {
            if (utils_compare_dates(del_date, startDate) >= 0 && 
                utils_compare_dates(del_date, endDate) <= 0) {
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
    results = (ResidentialProperty*)malloc(match_count * sizeof(ResidentialProperty));
    if (!results) {
        property_log("ERROR", "Memory allocation error in deleted residential property search");
        fclose(file);
        return NULL;
    }
    
    // بازگشت به ابتدای فایل
    rewind(file);
    
    // خواندن و ذخیره املاک واجد شرایط
    int index = 0;
    while (fgets(line, sizeof(line), file) && index < match_count) {
        ResidentialProperty* property = &results[index];
        int id, municipality_district, is_active, building_age, bedrooms, floor;
        int total_floors, has_elevator, has_parking, has_storage, timestamp;
        float area_size;
        double selling_price, mortgage_amount, monthly_rent;
        char address[100], owner_phone[20], reg_date[11], del_date[11], reg_by[50], status[20];
        
        // خواندن داده‌ها از خط فایل
        sscanf(line, "%d,%d,%[^,],%[^,],%d,%[^,],%[^,],%d,%f,%d,%d,%d,%d,%d,%d,%lf,%lf,%lf,%[^,],%[^,],%d,%s",
               &id, &municipality_district, address, owner_phone, &building_age, reg_date, del_date, 
               &is_active, &area_size, &bedrooms, &floor, &total_floors, &has_elevator, 
               &has_parking, &has_storage, &selling_price, &mortgage_amount, &monthly_rent, 
               reg_by, status, &timestamp, status);
        
        // بررسی شرایط جستجو و ذخیره نتایج
        if (strlen(del_date) > 0 && is_active == PROPERTY_STATUS_INACTIVE) {
            if (utils_compare_dates(del_date, startDate) >= 0 && 
                utils_compare_dates(del_date, endDate) <= 0) {
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
                property->bedrooms = bedrooms;
                property->floor = floor;
                property->totalFloors = total_floors;
                property->hasElevator = has_elevator;
                property->hasParking = has_parking;
                property->hasStorage = has_storage;
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
             "Search for deleted residential properties between %s and %s: found %d properties", 
             startDate, endDate, index);
    property_log("INFO", log_message);
    
    return results;
}

ResidentialProperty* residential_find_by_user(const char* username, PropertyDealType dealType, int* count) {
    char filename[256];
    char log_message[256];
    ResidentialProperty* results = NULL;
    *count = 0;
    
    // بررسی پارامترهای ورودی
    if (!username || strlen(username) == 0) {
        property_log("ERROR", "Invalid username for residential property search");
        return NULL;
    }
    
    // انتخاب فایل بر اساس نوع معامله
    if (dealType == PROPERTY_DEAL_SALE) {
        strcpy(filename, RESIDENTIAL_SALES_PATH);
    } else if (dealType == PROPERTY_DEAL_RENT) {
        strcpy(filename, RESIDENTIAL_RENTALS_PATH);
    } else {
        property_log("ERROR", "Invalid deal type for user's residential property search");
        return NULL;
    }
    
    // باز کردن فایل
    FILE* file = fopen(filename, "rb");
    if (!file) {
        snprintf(log_message, sizeof(log_message), 
                 "Error opening file for user %s residential properties search", username);
        property_log("ERROR", log_message);
        return NULL;
    }
    
    // شمارش تعداد املاک واجد شرایط
    char line[1024];
    int match_count = 0;
    
    while (fgets(line, sizeof(line), file)) {
        int id, municipality_district, is_active, building_age, bedrooms, floor;
        int total_floors, has_elevator, has_parking, has_storage, timestamp;
        float area_size;
        double selling_price, mortgage_amount, monthly_rent;
        char address[100], owner_phone[20], reg_date[11], del_date[11], reg_by[50], status[20];
        
        // خواندن داده‌ها از خط فایل
        sscanf(line, "%d,%d,%[^,],%[^,],%d,%[^,],%[^,],%d,%f,%d,%d,%d,%d,%d,%d,%lf,%lf,%lf,%[^,],%[^,],%d,%s",
               &id, &municipality_district, address, owner_phone, &building_age, reg_date, del_date, 
               &is_active, &area_size, &bedrooms, &floor, &total_floors, &has_elevator, 
               &has_parking, &has_storage, &selling_price, &mortgage_amount, &monthly_rent, 
               reg_by, status, &timestamp, status);
        
        // بررسی نام کاربری ثبت‌کننده
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
    results = (ResidentialProperty*)malloc(match_count * sizeof(ResidentialProperty));
    if (!results) {
        property_log("ERROR", "Memory allocation error in user's residential property search");
        fclose(file);
        return NULL;
    }
    
    // بازگشت به ابتدای فایل
    rewind(file);
    
    // خواندن و ذخیره املاک واجد شرایط
    int index = 0;
    while (fgets(line, sizeof(line), file) && index < match_count) {
        ResidentialProperty* property = &results[index];
        int id, municipality_district, is_active, building_age, bedrooms, floor;
        int total_floors, has_elevator, has_parking, has_storage, timestamp;
        float area_size;
        double selling_price, mortgage_amount, monthly_rent;
        char address[100], owner_phone[20], reg_date[11], del_date[11], reg_by[50], status[20];
        
        // خواندن داده‌ها از خط فایل
        sscanf(line, "%d,%d,%[^,],%[^,],%d,%[^,],%[^,],%d,%f,%d,%d,%d,%d,%d,%d,%lf,%lf,%lf,%[^,],%[^,],%d,%s",
               &id, &municipality_district, address, owner_phone, &building_age, reg_date, del_date, 
               &is_active, &area_size, &bedrooms, &floor, &total_floors, &has_elevator, 
               &has_parking, &has_storage, &selling_price, &mortgage_amount, &monthly_rent, 
               reg_by, status, &timestamp, status);
        
        // بررسی نام کاربری و ذخیره نتایج
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
            property->bedrooms = bedrooms;
            property->floor = floor;
            property->totalFloors = total_floors;
            property->hasElevator = has_elevator;
            property->hasParking = has_parking;
            property->hasStorage = has_storage;
            property->sellingPrice = selling_price;
            property->mortgageAmount = mortgage_amount;
            property->monthlyRentAmount = monthly_rent;
            
            index++;
        }
    }
    
    fclose(file);
    *count = index;
    
    snprintf(log_message, sizeof(log_message), 
             "Search for user %s residential properties: found %d properties", username, index);
    property_log("INFO", log_message);
    
    return results;
}

double residential_calculate_total_value() {
    char log_message[256];
    double total_value = 0.0;
    
    // باز کردن فایل فروش
    FILE* file = fopen(RESIDENTIAL_SALES_PATH, "rb");
    if (!file) {
        property_log("ERROR", "Error opening file for calculating total residential properties value");
        return 0.0;
    }
    
    // محاسبه مجموع قیمت‌های فروش
    char line[1024];
    while (fgets(line, sizeof(line), file)) {
        int id, municipality_district, is_active, building_age, bedrooms, floor;
        int total_floors, has_elevator, has_parking, has_storage, timestamp;
        float area_size;
        double selling_price, mortgage_amount, monthly_rent;
        char address[100], owner_phone[20], reg_date[11], del_date[11], reg_by[50], status[20];
        
        // خواندن داده‌ها از خط فایل
        sscanf(line, "%d,%d,%[^,],%[^,],%d,%[^,],%[^,],%d,%f,%d,%d,%d,%d,%d,%d,%lf,%lf,%lf,%[^,],%[^,],%d,%s",
               &id, &municipality_district, address, owner_phone, &building_age, reg_date, del_date, 
               &is_active, &area_size, &bedrooms, &floor, &total_floors, &has_elevator, 
               &has_parking, &has_storage, &selling_price, &mortgage_amount, &monthly_rent, 
               reg_by, status, &timestamp, status);
        
        // فقط املاک فعال محاسبه می‌شوند
        if (is_active == PROPERTY_STATUS_ACTIVE) {
            total_value += selling_price;
        }
    }
    
    fclose(file);
    
    snprintf(log_message, sizeof(log_message), 
             "محاسبه ارزش کل املاک مسکونی فروشی: %f تومان", total_value);
    property_log("INFO", log_message);
    
    return total_value;
}

void residential_free_array(ResidentialProperty* array, int count) {
    if (array) {
        free(array);
    }
}