/**
 * @file land.h
 * @brief تعاریف و توابع مرتبط با زمین‌ها
 */

#ifndef PROPERTY_LIB_LAND_H
#define PROPERTY_LIB_LAND_H

#ifdef __cplusplus
extern "C" {
#endif

#include "property.h"

/**
 * @struct LandProperty
 * @brief ساختار ذخیره‌سازی اطلاعات زمین
 */
typedef struct {
    BaseProperty base;              /**< اطلاعات پایه ملک */
    char landType[20];              /**< نوع زمین (مسکونی، تجاری، کشاورزی و غیره) */
    float landArea;                 /**< مساحت زمین (مترمربع) */
    float distanceToMainRoad;       /**< فاصله تا خیابان اصلی (متر) */
    int hasWell;                    /**< دارای چاه آب (1: بله، 0: خیر) */
    double sellingPrice;            /**< قیمت فروش (تومان) */
    double mortgageAmount;          /**< مبلغ رهن (تومان) */
    double monthlyRentAmount;       /**< مبلغ اجاره ماهیانه (تومان) */
} LandProperty;

/**
 * @brief ثبت زمین جدید برای فروش
 * 
 * @param property اطلاعات زمین
 * @param username نام کاربری ثبت‌کننده
 * @return int کد خطا: 0 (موفق)، 1 (اعتبارسنجی ناموفق)، 2 (خطای فایل)
 */
int land_register_sale(LandProperty* property, const char* username);

/**
 * @brief ثبت زمین جدید برای اجاره
 * 
 * @param property اطلاعات زمین
 * @param username نام کاربری ثبت‌کننده
 * @return int کد خطا: 0 (موفق)، 1 (اعتبارسنجی ناموفق)، 2 (خطای فایل)
 */
int land_register_rental(LandProperty* property, const char* username);

/**
 * @brief استخراج و جستجوی زمین‌ها بر اساس منطقه شهرداری
 * 
 * @param district منطقه شهرداری (0 برای همه مناطق)
 * @param dealType نوع معامله (فروش/اجاره)
 * @param count خروجی: تعداد زمین‌های یافت شده
 * @return LandProperty* آرایه‌ای از زمین‌های یافت شده (باید با land_free_array آزاد شود)
 */
LandProperty* land_find_by_district(int district, PropertyDealType dealType, int* count);

/**
 * @brief استخراج و جستجوی زمین‌ها بر اساس محدوده مساحت
 * 
 * @param minArea حداقل مساحت (0 برای بدون محدودیت)
 * @param maxArea حداکثر مساحت (0 برای بدون محدودیت)
 * @param dealType نوع معامله (فروش/اجاره)
 * @param count خروجی: تعداد زمین‌های یافت شده
 * @return LandProperty* آرایه‌ای از زمین‌های یافت شده (باید با land_free_array آزاد شود)
 */
LandProperty* land_find_by_area(float minArea, float maxArea, PropertyDealType dealType, int* count);

/**
 * @brief استخراج و جستجوی زمین‌ها بر اساس نوع زمین
 * 
 * @param landType نوع زمین ("مسکونی"، "تجاری"، "کشاورزی"، "صنعتی"، "همه" برای همه انواع)
 * @param dealType نوع معامله (فروش/اجاره)
 * @param count خروجی: تعداد زمین‌های یافت شده
 * @return LandProperty* آرایه‌ای از زمین‌های یافت شده (باید با land_free_array آزاد شود)
 */
LandProperty* land_find_by_type(const char* landType, PropertyDealType dealType, int* count);

/**
 * @brief استخراج و جستجوی زمین‌ها بر اساس محدوده قیمت
 * 
 * @param minPrice حداقل قیمت (0 برای بدون محدودیت)
 * @param maxPrice حداکثر قیمت (0 برای بدون محدودیت)
 * @param dealType نوع معامله (فروش/اجاره)
 * @param count خروجی: تعداد زمین‌های یافت شده
 * @return LandProperty* آرایه‌ای از زمین‌های یافت شده (باید با land_free_array آزاد شود)
 */
LandProperty* land_find_by_price(double minPrice, double maxPrice, PropertyDealType dealType, int* count);

/**
 * @brief استخراج و جستجوی زمین‌ها بر اساس محدوده فاصله تا خیابان اصلی
 * 
 * @param maxDistance حداکثر فاصله تا خیابان اصلی (متر)
 * @param dealType نوع معامله (فروش/اجاره)
 * @param count خروجی: تعداد زمین‌های یافت شده
 * @return LandProperty* آرایه‌ای از زمین‌های یافت شده (باید با land_free_array آزاد شود)
 */
LandProperty* land_find_by_distance(float maxDistance, PropertyDealType dealType, int* count);

/**
 * @brief استخراج زمین‌های دارای چاه آب
 * 
 * @param dealType نوع معامله (فروش/اجاره)
 * @param count خروجی: تعداد زمین‌های یافت شده
 * @return LandProperty* آرایه‌ای از زمین‌های یافت شده (باید با land_free_array آزاد شود)
 */
LandProperty* land_find_with_well(PropertyDealType dealType, int* count);

/**
 * @brief استخراج زمین‌های حذف شده در بازه زمانی مشخص
 * 
 * @param startDate تاریخ شروع بازه (فرمت YYYY-MM-DD)
 * @param endDate تاریخ پایان بازه (فرمت YYYY-MM-DD)
 * @param dealType نوع معامله (فروش/اجاره)
 * @param count خروجی: تعداد زمین‌های یافت شده
 * @return LandProperty* آرایه‌ای از زمین‌های یافت شده (باید با land_free_array آزاد شود)
 */
LandProperty* land_find_deleted_by_date(const char* startDate, const char* endDate, 
                                      PropertyDealType dealType, int* count);

/**
 * @brief استخراج زمین‌های ثبت شده توسط کاربر خاص
 * 
 * @param username نام کاربری
 * @param dealType نوع معامله (فروش/اجاره)
 * @param count خروجی: تعداد زمین‌های یافت شده
 * @return LandProperty* آرایه‌ای از زمین‌های یافت شده (باید با land_free_array آزاد شود)
 */
LandProperty* land_find_by_user(const char* username, PropertyDealType dealType, int* count);

/**
 * @brief محاسبه ارزش کل زمین‌های فروشی
 * 
 * @return double ارزش کل (تومان)
 */
double land_calculate_total_value();

/**
 * @brief آزاد کردن حافظه آرایه زمین‌ها
 * 
 * @param array آرایه زمین‌ها
 * @param count تعداد عناصر آرایه
 */
void land_free_array(LandProperty* array, int count);

#ifdef __cplusplus
}  // extern "C"
#endif

#endif  // PROPERTY_LIB_LAND_H 