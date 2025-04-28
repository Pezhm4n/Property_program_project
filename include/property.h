/**
 * @file property.h
 * @brief تعاریف و توابع پایه مرتبط با مدیریت املاک
 */

#ifndef PROPERTY_LIB_PROPERTY_H
#define PROPERTY_LIB_PROPERTY_H

#ifdef __cplusplus
extern "C" {
#endif

#include <stdbool.h>

/**
 * @enum PropertyType
 * @brief انواع ملک
 */
typedef enum {
    PROPERTY_TYPE_RESIDENTIAL = 1,  /**< ملک مسکونی */
    PROPERTY_TYPE_COMMERCIAL = 2,   /**< ملک تجاری */
    PROPERTY_TYPE_LAND = 3          /**< زمین */
} PropertyType;

/**
 * @enum PropertyStatus
 * @brief وضعیت ملک
 */
typedef enum {
    PROPERTY_STATUS_ACTIVE = 1,     /**< فعال */
    PROPERTY_STATUS_INACTIVE = 0    /**< غیرفعال */
} PropertyStatus;

/**
 * @enum PropertyDealType
 * @brief نوع معامله
 */
typedef enum {
    PROPERTY_DEAL_SALE = 1,         /**< فروش */
    PROPERTY_DEAL_RENT = 2          /**< اجاره */
} PropertyDealType;

/**
 * @struct BaseProperty
 * @brief ساختار پایه برای همه انواع املاک
 */
typedef struct {
    int propertyId;                /**< شناسه یکتای ملک */
    int municipalityDistrict;      /**< منطقه شهرداری */
    char address[100];             /**< آدرس کامل */
    char ownerPhoneNumber[20];     /**< شماره تلفن مالک */
    char registrationDate[11];     /**< تاریخ ثبت به فرمت YYYY-MM-DD */
    char deleteDate[11];           /**< تاریخ حذف (در صورت حذف) */
    PropertyStatus isActive;       /**< وضعیت فعال یا غیرفعال */
    char registeredBy[50];         /**< نام کاربری ثبت‌کننده */
    PropertyDealType dealType;     /**< نوع معامله (فروش یا اجاره) */
} BaseProperty;

/**
 * @struct PropertyNode
 * @brief گره لیست پیوندی برای املاک
 */
typedef struct PropertyNode {
    void* property;                /**< اشاره‌گر به ملک (باید به نوع مناسب تبدیل شود) */
    PropertyType type;             /**< نوع ملک ذخیره شده */
    struct PropertyNode* next;     /**< اشاره‌گر به گره بعدی */
} PropertyNode;

/**
 * @brief ایجاد یک گره جدید برای لیست پیوندی املاک
 * 
 * @param property اشاره‌گر به ملک
 * @param type نوع ملک
 * @return PropertyNode* گره ایجاد شده یا NULL در صورت خطا
 */
PropertyNode* property_create_node(void* property, PropertyType type);

/**
 * @brief افزودن یک ملک به لیست پیوندی
 * 
 * @param head اشاره‌گر به اشاره‌گر سر لیست
 * @param property اشاره‌گر به ملک
 * @param type نوع ملک
 * @return int کد خطا: 0 (موفق)، 1 (خطای حافظه)
 */
int property_insert_node(PropertyNode** head, void* property, PropertyType type);

/**
 * @brief آزاد کردن حافظه لیست پیوندی املاک
 * 
 * @param head اشاره‌گر به سر لیست
 */
void property_free_list(PropertyNode* head);

/**
 * @brief دریافت تعداد کل املاک ثبت شده
 * 
 * @return int تعداد کل املاک
 */
int property_get_count();

/**
 * @brief به‌روزرسانی شمارنده املاک
 * 
 * @param newCount مقدار جدید
 * @return int کد خطا: 0 (موفق)، 1 (خطای فایل)
 */
int property_update_count(int newCount);

/**
 * @brief بررسی فرمت آدرس
 * 
 * @param address رشته آدرس
 * @return bool صحیح اگر فرمت معتبر است، غلط در غیر این صورت
 */
bool property_check_address_format(const char* address);

/**
 * @brief گرفتن شناسه جدید برای ملک
 * 
 * @return int شناسه جدید
 */
int property_generate_id();

/**
 * @brief جستجوی ملک بر اساس شناسه
 * 
 * @param propertyId شناسه ملک
 * @param dealType نوع معامله (فروش یا اجاره)
 * @param propertyType خروجی: نوع ملک یافت شده
 * @return void* اشاره‌گر به ملک یافت شده یا NULL
 */
void* property_find_by_id(int propertyId, PropertyDealType dealType, PropertyType* propertyType);

/**
 * @brief حذف ملک بر اساس شناسه
 * 
 * @param propertyId شناسه ملک
 * @param dealType نوع معامله (فروش یا اجاره)
 * @param propertyType نوع ملک
 * @param username نام کاربری کاربر درخواست‌کننده
 * @return int کد خطا: 0 (موفق)، 1 (ملک یافت نشد)، 2 (عدم دسترسی)، 3 (خطای فایل)
 */
int property_delete(int propertyId, PropertyDealType dealType, PropertyType propertyType, const char* username);

/**
 * @brief بارگذاری املاک از فایل
 * 
 * @param filename نام فایل
 * @param propertyList خروجی: اشاره‌گر به لیست پیوندی املاک
 * @param dealType نوع معامله (فروش یا اجاره)
 * @param propertyType نوع ملک
 * @return int کد خطا: 0 (موفق)، 1 (خطای فایل)، 2 (خطای حافظه)
 */
int property_load_from_file(const char* filename, PropertyNode** propertyList, 
                            PropertyDealType dealType, PropertyType propertyType);

#ifdef __cplusplus
}  // extern "C"
#endif

#endif  // PROPERTY_LIB_PROPERTY_H 