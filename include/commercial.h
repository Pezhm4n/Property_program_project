/**
 * @file commercial.h
 * @brief تعاریف و توابع مرتبط با املاک تجاری
 */

#ifndef PROPERTY_LIB_COMMERCIAL_H
#define PROPERTY_LIB_COMMERCIAL_H

#ifdef __cplusplus
extern "C" {
#endif

#include "property.h"

/**
 * @struct CommercialProperty
 * @brief ساختار ذخیره‌سازی اطلاعات ملک تجاری
 */
typedef struct {
    BaseProperty base;         /**< اطلاعات پایه ملک */
    char propertyType[20];     /**< نوع ملک تجاری (مغازه، دفتر، انبار و غیره) */
    int buildingAge;           /**< سن ساختمان (سال) */
    float areaSize;            /**< متراژ (مترمربع) */
    int floor;                 /**< طبقه */
    float landArea;            /**< متراژ زمین (برای املاک مستقل) */
    int officeRooms;           /**< تعداد اتاق‌های اداری */
    double sellingPrice;       /**< قیمت فروش (تومان) */
    double mortgageAmount;     /**< مبلغ رهن (تومان) */
    double monthlyRentAmount;  /**< مبلغ اجاره ماهیانه (تومان) */
} CommercialProperty;

/**
 * @brief ثبت ملک تجاری جدید برای فروش
 * 
 * @param property اطلاعات ملک تجاری
 * @param username نام کاربری ثبت‌کننده
 * @return int کد خطا: 0 (موفق)، 1 (اعتبارسنجی ناموفق)، 2 (خطای فایل)
 */
int commercial_register_sale(CommercialProperty* property, const char* username);

/**
 * @brief ثبت ملک تجاری جدید برای اجاره
 * 
 * @param property اطلاعات ملک تجاری
 * @param username نام کاربری ثبت‌کننده
 * @return int کد خطا: 0 (موفق)، 1 (اعتبارسنجی ناموفق)، 2 (خطای فایل)
 */
int commercial_register_rental(CommercialProperty* property, const char* username);

/**
 * @brief استخراج و جستجوی املاک تجاری بر اساس منطقه شهرداری
 * 
 * @param district منطقه شهرداری (0 برای همه مناطق)
 * @param dealType نوع معامله (فروش/اجاره)
 * @param count خروجی: تعداد املاک یافت شده
 * @return CommercialProperty* آرایه‌ای از املاک تجاری یافت شده (باید با commercial_free_array آزاد شود)
 */
CommercialProperty* commercial_find_by_district(int district, PropertyDealType dealType, int* count);

/**
 * @brief استخراج و جستجوی املاک تجاری بر اساس محدوده سن ساختمان
 * 
 * @param minAge حداقل سن (0 برای بدون محدودیت)
 * @param maxAge حداکثر سن (0 برای بدون محدودیت)
 * @param dealType نوع معامله (فروش/اجاره)
 * @param count خروجی: تعداد املاک یافت شده
 * @return CommercialProperty* آرایه‌ای از املاک تجاری یافت شده (باید با commercial_free_array آزاد شود)
 */
CommercialProperty* commercial_find_by_age(int minAge, int maxAge, PropertyDealType dealType, int* count);

/**
 * @brief استخراج و جستجوی املاک تجاری بر اساس محدوده متراژ
 * 
 * @param minArea حداقل متراژ (0 برای بدون محدودیت)
 * @param maxArea حداکثر متراژ (0 برای بدون محدودیت)
 * @param dealType نوع معامله (فروش/اجاره)
 * @param count خروجی: تعداد املاک یافت شده
 * @return CommercialProperty* آرایه‌ای از املاک تجاری یافت شده (باید با commercial_free_array آزاد شود)
 */
CommercialProperty* commercial_find_by_area(float minArea, float maxArea, PropertyDealType dealType, int* count);

/**
 * @brief استخراج و جستجوی املاک تجاری بر اساس تعداد اتاق‌های اداری
 * 
 * @param rooms تعداد اتاق‌های مورد نظر (0 برای همه)
 * @param dealType نوع معامله (فروش/اجاره)
 * @param count خروجی: تعداد املاک یافت شده
 * @return CommercialProperty* آرایه‌ای از املاک تجاری یافت شده (باید با commercial_free_array آزاد شود)
 */
CommercialProperty* commercial_find_by_rooms(int rooms, PropertyDealType dealType, int* count);

/**
 * @brief استخراج و جستجوی املاک تجاری بر اساس محدوده قیمت
 * 
 * @param minPrice حداقل قیمت (0 برای بدون محدودیت)
 * @param maxPrice حداکثر قیمت (0 برای بدون محدودیت)
 * @param dealType نوع معامله (فروش/اجاره)
 * @param count خروجی: تعداد املاک یافت شده
 * @return CommercialProperty* آرایه‌ای از املاک تجاری یافت شده (باید با commercial_free_array آزاد شود)
 */
CommercialProperty* commercial_find_by_price(double minPrice, double maxPrice, PropertyDealType dealType, int* count);

/**
 * @brief استخراج و جستجوی املاک تجاری بر اساس طبقه
 * 
 * @param minFloor حداقل طبقه (0 برای همکف، منفی برای زیرزمین)
 * @param maxFloor حداکثر طبقه
 * @param dealType نوع معامله (فروش/اجاره)
 * @param count خروجی: تعداد املاک یافت شده
 * @return CommercialProperty* آرایه‌ای از املاک تجاری یافت شده (باید با commercial_free_array آزاد شود)
 */
CommercialProperty* commercial_find_by_floor(int minFloor, int maxFloor, PropertyDealType dealType, int* count);

/**
 * @brief استخراج املاک تجاری حذف شده در بازه زمانی مشخص
 * 
 * @param startDate تاریخ شروع بازه (فرمت YYYY-MM-DD)
 * @param endDate تاریخ پایان بازه (فرمت YYYY-MM-DD)
 * @param dealType نوع معامله (فروش/اجاره)
 * @param count خروجی: تعداد املاک یافت شده
 * @return CommercialProperty* آرایه‌ای از املاک تجاری یافت شده (باید با commercial_free_array آزاد شود)
 */
CommercialProperty* commercial_find_deleted_by_date(const char* startDate, const char* endDate, 
                                                   PropertyDealType dealType, int* count);

/**
 * @brief استخراج املاک تجاری ثبت شده توسط کاربر خاص
 * 
 * @param username نام کاربری
 * @param dealType نوع معامله (فروش/اجاره)
 * @param count خروجی: تعداد املاک یافت شده
 * @return CommercialProperty* آرایه‌ای از املاک تجاری یافت شده (باید با commercial_free_array آزاد شود)
 */
CommercialProperty* commercial_find_by_user(const char* username, PropertyDealType dealType, int* count);

/**
 * @brief محاسبه ارزش کل املاک تجاری فروشی
 * 
 * @return double ارزش کل (تومان)
 */
double commercial_calculate_total_value();

/**
 * @brief آزاد کردن حافظه آرایه املاک تجاری
 * 
 * @param array آرایه املاک تجاری
 * @param count تعداد عناصر آرایه
 */
void commercial_free_array(CommercialProperty* array, int count);

#ifdef __cplusplus
}  // extern "C"
#endif

#endif  // PROPERTY_LIB_COMMERCIAL_H 