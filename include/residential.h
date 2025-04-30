/**
 * @file residential.h
 * @brief تعاریف و توابع مرتبط با املاک مسکونی
 */

#ifndef PROPERTY_LIB_RESIDENTIAL_H
#define PROPERTY_LIB_RESIDENTIAL_H

#ifdef __cplusplus
extern "C" {
#endif

#include "property.h"

/**
 * @struct ResidentialProperty
 * @brief ساختار ذخیره‌سازی اطلاعات املاک مسکونی
 */
typedef struct {
    BaseProperty base;              /**< اطلاعات پایه ملک */
    int buildingAge;                /**< سن ساختمان (سال) */
    float areaSize;                 /**< مساحت (مترمربع) */
    int bedrooms;                   /**< تعداد اتاق خواب */
    int floor;                      /**< طبقه */
    int totalFloors;                /**< تعداد کل طبقات ساختمان */
    int hasElevator;                /**< دارای آسانسور (1: بله، 0: خیر) */
    int hasParking;                 /**< دارای پارکینگ (1: بله، 0: خیر) */
    int hasStorage;                 /**< دارای انباری (1: بله، 0: خیر) */
    double sellingPrice;            /**< قیمت فروش (تومان) */
    double mortgageAmount;          /**< مبلغ رهن (تومان) */
    double monthlyRentAmount;       /**< مبلغ اجاره ماهیانه (تومان) */
} ResidentialProperty;

/**
 * @brief ثبت ملک مسکونی جدید برای فروش
 * 
 * @param property اطلاعات ملک مسکونی
 * @param username نام کاربری ثبت‌کننده
 * @return int کد خطا: 0 (موفق)، 1 (اعتبارسنجی ناموفق)، 2 (خطای فایل)
 */
int residential_register_sale(ResidentialProperty* property, const char* username);

/**
 * @brief ثبت ملک مسکونی جدید برای اجاره
 * 
 * @param property اطلاعات ملک مسکونی
 * @param username نام کاربری ثبت‌کننده
 * @return int کد خطا: 0 (موفق)، 1 (اعتبارسنجی ناموفق)، 2 (خطای فایل)
 */
int residential_register_rental(ResidentialProperty* property, const char* username);

/**
 * @brief استخراج و جستجوی املاک مسکونی بر اساس منطقه شهرداری
 * 
 * @param district منطقه شهرداری (0 برای همه مناطق)
 * @param dealType نوع معامله (فروش/اجاره)
 * @param count خروجی: تعداد املاک یافت شده
 * @return ResidentialProperty* آرایه‌ای از املاک یافت شده (باید با residential_free_array آزاد شود)
 */
ResidentialProperty* residential_find_by_district(int district, PropertyDealType dealType, int* count);

/**
 * @brief استخراج و جستجوی املاک مسکونی بر اساس سن ساختمان
 * 
 * @param maxAge حداکثر سن ساختمان (سال)
 * @param dealType نوع معامله (فروش/اجاره)
 * @param count خروجی: تعداد املاک یافت شده
 * @return ResidentialProperty* آرایه‌ای از املاک یافت شده (باید با residential_free_array آزاد شود)
 */
ResidentialProperty* residential_find_by_age(int maxAge, PropertyDealType dealType, int* count);

/**
 * @brief استخراج و جستجوی املاک مسکونی بر اساس محدوده مساحت
 * 
 * @param minArea حداقل مساحت (0 برای بدون محدودیت)
 * @param maxArea حداکثر مساحت (0 برای بدون محدودیت)
 * @param dealType نوع معامله (فروش/اجاره)
 * @param count خروجی: تعداد املاک یافت شده
 * @return ResidentialProperty* آرایه‌ای از املاک یافت شده (باید با residential_free_array آزاد شود)
 */
ResidentialProperty* residential_find_by_area(float minArea, float maxArea, PropertyDealType dealType, int* count);

/**
 * @brief استخراج و جستجوی املاک مسکونی بر اساس تعداد اتاق خواب
 * 
 * @param minBedrooms حداقل تعداد اتاق خواب (0 برای بدون محدودیت)
 * @param maxBedrooms حداکثر تعداد اتاق خواب (0 برای بدون محدودیت)
 * @param dealType نوع معامله (فروش/اجاره)
 * @param count خروجی: تعداد املاک یافت شده
 * @return ResidentialProperty* آرایه‌ای از املاک یافت شده (باید با residential_free_array آزاد شود)
 */
ResidentialProperty* residential_find_by_bedrooms(int minBedrooms, int maxBedrooms, PropertyDealType dealType, int* count);

/**
 * @brief استخراج و جستجوی املاک مسکونی بر اساس محدوده قیمت
 * 
 * @param minPrice حداقل قیمت (0 برای بدون محدودیت)
 * @param maxPrice حداکثر قیمت (0 برای بدون محدودیت)
 * @param dealType نوع معامله (فروش/اجاره)
 * @param count خروجی: تعداد املاک یافت شده
 * @return ResidentialProperty* آرایه‌ای از املاک یافت شده (باید با residential_free_array آزاد شود)
 */
ResidentialProperty* residential_find_by_price(double minPrice, double maxPrice, PropertyDealType dealType, int* count);

/**
 * @brief استخراج و جستجوی املاک مسکونی بر اساس طبقه
 * 
 * @param minFloor حداقل طبقه (0 برای بدون محدودیت)
 * @param maxFloor حداکثر طبقه (0 برای بدون محدودیت)
 * @param dealType نوع معامله (فروش/اجاره)
 * @param count خروجی: تعداد املاک یافت شده
 * @return ResidentialProperty* آرایه‌ای از املاک یافت شده (باید با residential_free_array آزاد شود)
 */
ResidentialProperty* residential_find_by_floor(int minFloor, int maxFloor, PropertyDealType dealType, int* count);

/**
 * @brief استخراج املاک مسکونی دارای آسانسور
 * 
 * @param dealType نوع معامله (فروش/اجاره)
 * @param count خروجی: تعداد املاک یافت شده
 * @return ResidentialProperty* آرایه‌ای از املاک یافت شده (باید با residential_free_array آزاد شود)
 */
ResidentialProperty* residential_find_with_elevator(PropertyDealType dealType, int* count);

/**
 * @brief استخراج املاک مسکونی دارای پارکینگ
 * 
 * @param dealType نوع معامله (فروش/اجاره)
 * @param count خروجی: تعداد املاک یافت شده
 * @return ResidentialProperty* آرایه‌ای از املاک یافت شده (باید با residential_free_array آزاد شود)
 */
ResidentialProperty* residential_find_with_parking(PropertyDealType dealType, int* count);

/**
 * @brief استخراج املاک مسکونی دارای انباری
 * 
 * @param dealType نوع معامله (فروش/اجاره)
 * @param count خروجی: تعداد املاک یافت شده
 * @return ResidentialProperty* آرایه‌ای از املاک یافت شده (باید با residential_free_array آزاد شود)
 */
ResidentialProperty* residential_find_with_storage(PropertyDealType dealType, int* count);

/**
 * @brief استخراج املاک مسکونی حذف شده در بازه زمانی مشخص
 * 
 * @param startDate تاریخ شروع بازه (فرمت YYYY-MM-DD)
 * @param endDate تاریخ پایان بازه (فرمت YYYY-MM-DD)
 * @param dealType نوع معامله (فروش/اجاره)
 * @param count خروجی: تعداد املاک یافت شده
 * @return ResidentialProperty* آرایه‌ای از املاک یافت شده (باید با residential_free_array آزاد شود)
 */
ResidentialProperty* residential_find_deleted_by_date(const char* startDate, const char* endDate, 
                                                  PropertyDealType dealType, int* count);

/**
 * @brief استخراج املاک مسکونی ثبت شده توسط کاربر خاص
 * 
 * @param username نام کاربری
 * @param dealType نوع معامله (فروش/اجاره)
 * @param count خروجی: تعداد املاک یافت شده
 * @return ResidentialProperty* آرایه‌ای از املاک یافت شده (باید با residential_free_array آزاد شود)
 */
ResidentialProperty* residential_find_by_user(const char* username, PropertyDealType dealType, int* count);

/**
 * @brief محاسبه ارزش کل املاک مسکونی فروشی
 * 
 * @return double ارزش کل (تومان)
 */
double residential_calculate_total_value();

/**
 * @brief آزاد کردن حافظه آرایه املاک مسکونی
 * 
 * @param array آرایه املاک مسکونی
 * @param count تعداد عناصر آرایه
 */
void residential_free_array(ResidentialProperty* array, int count);

#ifdef __cplusplus
}  // extern "C"
#endif

#endif  // PROPERTY_LIB_RESIDENTIAL_H 