"""
ماژول هسته برای ارتباط با کتابخانه C مدیریت املاک از طریق CFFI
"""

import os
import platform
from cffi import FFI

ffi = FFI()

# تعریف هدرهای مورد نیاز برای استفاده در CFFI
ffi.cdef("""
    // توابع مدیریت داده
    void data_manager_set_base_path(const char* path);
    int data_manager_init_storage();
    
    // ساختارهای داده و توابع مرتبط با املاک مسکونی
    typedef struct {
        char id[20];
        char district[100];
        int isActive;
        int buildingAge;
        double areaSize;
        int bedrooms;
        int floor;
        int totalFloors;
        int hasElevator;
        int hasParking;
        int hasStorage;
        double sellingPrice;
        double mortgageAmount;
        double monthlyRentAmount;
        char registrationDate[20];
        char lastUpdateDate[20];
        char ownerName[100];
        char ownerContact[100];
        char description[500];
        char registeredBy[100];
    } ResidentialProperty;
    
    // توابع مدیریت املاک مسکونی
    int residential_register_sale(const char* username, ResidentialProperty property);
    int residential_register_rental(const char* username, ResidentialProperty property);
    ResidentialProperty* residential_find_by_district(const char* district, int dealType, int* count);
    ResidentialProperty* residential_find_by_age(int minAge, int maxAge, int dealType, int* count);
    ResidentialProperty* residential_find_by_area(double minArea, double maxArea, int dealType, int* count);
    ResidentialProperty* residential_find_by_bedrooms(int minBedrooms, int maxBedrooms, int dealType, int* count);
    ResidentialProperty* residential_find_by_price(double minPrice, double maxPrice, int dealType, int* count);
    ResidentialProperty* residential_find_by_floor(int minFloor, int maxFloor, int dealType, int* count);
    ResidentialProperty* residential_find_with_elevator(int dealType, int* count);
    ResidentialProperty* residential_find_with_parking(int dealType, int* count);
    ResidentialProperty* residential_find_with_storage(int dealType, int* count);
    ResidentialProperty* residential_find_deleted_by_date(const char* startDate, const char* endDate, int dealType, int* count);
    ResidentialProperty* residential_find_by_user(const char* username, int dealType, int* count);
    double residential_calculate_total_value();
    void residential_free_array(ResidentialProperty* properties);
    
    // ساختارهای داده و توابع مرتبط با املاک تجاری
    typedef struct {
        char id[20];
        char district[100];
        int isActive;
        int buildingAge;
        double areaSize;
        int hasParking;
        char commercialType[100];
        double sellingPrice;
        double mortgageAmount;
        double monthlyRentAmount;
        char registrationDate[20];
        char lastUpdateDate[20];
        char ownerName[100];
        char ownerContact[100];
        char description[500];
        char registeredBy[100];
    } CommercialProperty;
    
    // توابع مدیریت املاک تجاری
    int commercial_register_sale(const char* username, CommercialProperty property);
    int commercial_register_rental(const char* username, CommercialProperty property);
    CommercialProperty* commercial_find_by_district(const char* district, int dealType, int* count);
    CommercialProperty* commercial_find_by_age(int minAge, int maxAge, int dealType, int* count);
    CommercialProperty* commercial_find_by_area(double minArea, double maxArea, int dealType, int* count);
    CommercialProperty* commercial_find_by_type(const char* type, int dealType, int* count);
    CommercialProperty* commercial_find_by_price(double minPrice, double maxPrice, int dealType, int* count);
    CommercialProperty* commercial_find_with_parking(int dealType, int* count);
    CommercialProperty* commercial_find_deleted_by_date(const char* startDate, const char* endDate, int dealType, int* count);
    CommercialProperty* commercial_find_by_user(const char* username, int dealType, int* count);
    double commercial_calculate_total_value();
    void commercial_free_array(CommercialProperty* properties);
    
    // ساختارهای داده و توابع مرتبط با زمین
    typedef struct {
        char id[20];
        char district[100];
        int isActive;
        char landType[100];
        double landArea;
        double distanceToMainRoad;
        int hasWell;
        double sellingPrice;
        double mortgageAmount;
        double monthlyRentAmount;
        char registrationDate[20];
        char lastUpdateDate[20];
        char ownerName[100];
        char ownerContact[100];
        char description[500];
        char registeredBy[100];
    } LandProperty;
    
    // توابع مدیریت زمین
    int land_register_sale(const char* username, LandProperty property);
    int land_register_rental(const char* username, LandProperty property);
    LandProperty* land_find_by_district(const char* district, int dealType, int* count);
    LandProperty* land_find_by_area(double minArea, double maxArea, int dealType, int* count);
    LandProperty* land_find_by_type(const char* type, int dealType, int* count);
    LandProperty* land_find_by_price(double minPrice, double maxPrice, int dealType, int* count);
    LandProperty* land_find_by_distance(double maxDistance, int dealType, int* count);
    LandProperty* land_find_with_well(int dealType, int* count);
    LandProperty* land_find_deleted_by_date(const char* startDate, const char* endDate, int dealType, int* count);
    LandProperty* land_find_by_user(const char* username, int dealType, int* count);
    double land_calculate_total_value();
    void land_free_array(LandProperty* properties);
    
    // ساختارهای داده و توابع مرتبط با کاربران
    typedef struct {
        char username[100];
        char passwordHash[100];
        char fullName[200];
        char email[100];
        char phone[50];
        char role[50];
        int isActive;
        char registrationDate[20];
        char lastLoginDate[20];
    } User;
    
    // توابع مدیریت کاربران
    int user_register(User user);
    int user_login(const char* username, const char* password);
    User* user_get_by_username(const char* username);
    int user_update_profile(User user);
    int user_change_password(const char* username, const char* oldPassword, const char* newPassword);
    int user_deactivate(const char* username);
    User* user_get_all(int* count);
    void user_free(User* user);
    void user_free_array(User* users);
    
    // توابع مربوط به لاگ و خطایابی
    void property_log(const char* message);
    char* get_last_error();
""")

# تشخیص مسیر کتابخانه بر اساس سیستم عامل
def get_library_path():
    # پوشه اصلی پروژه
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../python', '..'))
    
    if platform.system() == 'Windows':
        return os.path.join(base_dir, 'lib', 'property_lib.dll')
    else:
        return os.path.join(base_dir, 'lib', 'libproperty.so')

# بارگیری کتابخانه
try:
    lib_path = get_library_path()
    lib = ffi.dlopen(lib_path)
    
    # تنظیم مسیر پایه برای ذخیره داده
    base_data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../python', '..', 'data'))
    lib.data_manager_set_base_path(ffi.new("char[]", base_data_path.encode('utf-8')))
    
    # مقدار دهی اولیه فضای ذخیره سازی
    init_result = lib.data_manager_init_storage()
    if init_result != 1:
        print(f"هشدار: مقداردهی اولیه فضای ذخیره سازی با مشکل مواجه شد (کد خطا: {init_result})")
    
except Exception as e:
    print(f"خطا در بارگیری کتابخانه C: {e}")
    # در صورت خطا، یک کتابخانه dummy ایجاد می‌کنیم تا برنامه بتواند بدون crash ادامه دهد
    class DummyLib:
        def __getattr__(self, name):
            def dummy_func(*args, **kwargs):
                print(f"تابع {name} در دسترس نیست. کتابخانه C بارگیری نشده است.")
                return None
            return dummy_func
    
    lib = DummyLib()

# مقادیر ثابت برای نوع معامله
DEAL_TYPE_SALE = 1
DEAL_TYPE_RENT = 2

# تابع برای دریافت پل ارتباطی مناسب بر اساس نوع ملک
def get_property_bridge(property_type):
    """
    بر اساس نوع ملک، پل ارتباطی مناسب را برمی‌گرداند
    
    Args:
        property_type (str): نوع ملک (residential, commercial, land)
        
    Returns:
        object: کلاس پل ارتباطی مناسب
    """
    if property_type == 'residential':
        from bridge.residential_bridge import ResidentialBridge
        return ResidentialBridge
    elif property_type == 'commercial':
        from bridge.commercial_bridge import CommercialBridge
        return CommercialBridge
    elif property_type == 'land':
        from bridge.land_bridge import LandBridge
        return LandBridge
    else:
        raise ValueError(f"نوع ملک نامعتبر: {property_type}") 