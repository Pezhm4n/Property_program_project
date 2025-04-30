"""
کلاس مدیریت کاربران
"""
from .core import ffi, lib

class UserManager:
    """
    کلاس مدیریت کاربران
    """
    
    def __init__(self):
        """
        مقداردهی اولیه کلاس مدیریت کاربران
        """
        pass
    
    def register(self, user_data):
        """
        ثبت نام کاربر جدید

        Parameters:
        ----------
        user_data : dict
            داده‌های کاربر شامل فیلدهای مورد نیاز

        Returns:
        -------
        bool
            True در صورت موفقیت، False در صورت شکست
        """
        if not self._validate_user_data(user_data):
            raise ValueError("داده‌های کاربر نامعتبر است")
        
        # ایجاد ساختار C برای کاربر
        user = self._create_user_struct(user_data)
        
        # فراخوانی تابع ثبت نام کاربر از کتابخانه C
        result = lib.user_register(user)
        
        return result == 1
    
    def login(self, username, password):
        """
        ورود کاربر به سیستم

        Parameters:
        ----------
        username : str
            نام کاربری
        password : str
            کلمه عبور

        Returns:
        -------
        bool
            True در صورت موفقیت، False در صورت شکست
        """
        if not username or not isinstance(username, str):
            raise ValueError("نام کاربری نامعتبر است")
        
        if not password or not isinstance(password, str):
            raise ValueError("کلمه عبور نامعتبر است")
        
        # فراخوانی تابع ورود به سیستم از کتابخانه C
        result = lib.user_login(
            ffi.new("char[]", username.encode('utf-8')),
            ffi.new("char[]", password.encode('utf-8'))
        )
        
        return result == 1
    
    def get_by_username(self, username):
        """
        دریافت اطلاعات کاربر با نام کاربری

        Parameters:
        ----------
        username : str
            نام کاربری

        Returns:
        -------
        dict
            دیکشنری حاوی اطلاعات کاربر یا None در صورت عدم وجود
        """
        if not username or not isinstance(username, str):
            raise ValueError("نام کاربری نامعتبر است")
        
        # فراخوانی تابع دریافت کاربر از کتابخانه C
        user_ptr = lib.user_get_by_username(
            ffi.new("char[]", username.encode('utf-8'))
        )
        
        if user_ptr == ffi.NULL:
            return None
        
        # تبدیل ساختار C به دیکشنری پایتون
        user_dict = self._convert_user_to_dict(user_ptr)
        
        # آزاد کردن حافظه تخصیص داده شده در سمت C
        lib.user_free(user_ptr)
        
        return user_dict
    
    def update_profile(self, user_data):
        """
        به‌روزرسانی پروفایل کاربر

        Parameters:
        ----------
        user_data : dict
            داده‌های جدید کاربر

        Returns:
        -------
        bool
            True در صورت موفقیت، False در صورت شکست
        """
        if not self._validate_user_data(user_data, update=True):
            raise ValueError("داده‌های کاربر نامعتبر است")
        
        # ایجاد ساختار C برای کاربر
        user = self._create_user_struct(user_data)
        
        # فراخوانی تابع به‌روزرسانی پروفایل از کتابخانه C
        result = lib.user_update_profile(user)
        
        return result == 1
    
    def change_password(self, username, old_password, new_password):
        """
        تغییر کلمه عبور کاربر

        Parameters:
        ----------
        username : str
            نام کاربری
        old_password : str
            کلمه عبور قدیمی
        new_password : str
            کلمه عبور جدید

        Returns:
        -------
        bool
            True در صورت موفقیت، False در صورت شکست
        """
        if not username or not isinstance(username, str):
            raise ValueError("نام کاربری نامعتبر است")
        
        if not old_password or not isinstance(old_password, str):
            raise ValueError("کلمه عبور قدیمی نامعتبر است")
        
        if not new_password or not isinstance(new_password, str) or len(new_password) < 6:
            raise ValueError("کلمه عبور جدید باید حداقل 6 کاراکتر باشد")
        
        # فراخوانی تابع تغییر کلمه عبور از کتابخانه C
        result = lib.user_change_password(
            ffi.new("char[]", username.encode('utf-8')),
            ffi.new("char[]", old_password.encode('utf-8')),
            ffi.new("char[]", new_password.encode('utf-8'))
        )
        
        return result == 1
    
    def deactivate(self, username):
        """
        غیرفعال کردن حساب کاربری

        Parameters:
        ----------
        username : str
            نام کاربری

        Returns:
        -------
        bool
            True در صورت موفقیت، False در صورت شکست
        """
        if not username or not isinstance(username, str):
            raise ValueError("نام کاربری نامعتبر است")
        
        # فراخوانی تابع غیرفعال کردن کاربر از کتابخانه C
        result = lib.user_deactivate(
            ffi.new("char[]", username.encode('utf-8'))
        )
        
        return result == 1
    
    def get_all(self):
        """
        دریافت تمام کاربران

        Returns:
        -------
        list
            لیستی از دیکشنری‌های حاوی اطلاعات کاربران
        """
        # تخصیص فضا برای شمارنده
        count_ptr = ffi.new("int*")
        
        # فراخوانی تابع دریافت همه کاربران از کتابخانه C
        result_ptr = lib.user_get_all(count_ptr)
        
        # تبدیل نتایج به لیست پایتون
        count = count_ptr[0]
        return self._convert_users_to_list(result_ptr, count)
    
    def _validate_user_data(self, user_data, update=False):
        """
        بررسی اعتبار داده‌های کاربر

        Parameters:
        ----------
        user_data : dict
            داده‌های کاربر
        update : bool
            آیا برای به‌روزرسانی است؟

        Returns:
        -------
        bool
            True اگر داده‌ها معتبر باشند، False در غیر این صورت
        """
        if not isinstance(user_data, dict):
            return False
        
        # فیلدهای اجباری برای ثبت نام
        required_fields = ['username', 'fullName', 'email', 'phone']
        
        # برای ثبت نام، کلمه عبور نیز اجباری است
        if not update:
            required_fields.append('password')
        
        # بررسی وجود فیلدهای اجباری
        for field in required_fields:
            if field not in user_data or not user_data[field]:
                return False
        
        # بررسی نام کاربری
        if not isinstance(user_data.get('username', ''), str) or len(user_data.get('username', '')) < 3:
            return False
        
        # بررسی ایمیل (بررسی ساده)
        email = user_data.get('email', '')
        if not isinstance(email, str) or '@' not in email or '.' not in email:
            return False
        
        # بررسی شماره تلفن (بررسی ساده)
        phone = user_data.get('phone', '')
        if not isinstance(phone, str) or len(phone) < 10:
            return False
        
        # بررسی کلمه عبور
        if 'password' in user_data and (not isinstance(user_data['password'], str) or len(user_data['password']) < 6):
            return False
        
        return True
    
    def _create_user_struct(self, user_data):
        """
        ایجاد ساختار کاربر برای استفاده در C

        Parameters:
        ----------
        user_data : dict
            داده‌های کاربر

        Returns:
        -------
        User
            ساختار کاربر
        """
        # ایجاد ساختار جدید
        user = ffi.new("User*")
        
        # پر کردن فیلدهای ساختار
        username = user_data.get('username', '')
        ffi.memmove(user.username, username.encode('utf-8'), min(len(username), 99))
        
        if 'password' in user_data:
            password = user_data.get('password', '')
            ffi.memmove(user.passwordHash, password.encode('utf-8'), min(len(password), 99))
        
        full_name = user_data.get('fullName', '')
        ffi.memmove(user.fullName, full_name.encode('utf-8'), min(len(full_name), 199))
        
        email = user_data.get('email', '')
        ffi.memmove(user.email, email.encode('utf-8'), min(len(email), 99))
        
        phone = user_data.get('phone', '')
        ffi.memmove(user.phone, phone.encode('utf-8'), min(len(phone), 49))
        
        role = user_data.get('role', 'user')
        ffi.memmove(user.role, role.encode('utf-8'), min(len(role), 49))
        
        user.isActive = user_data.get('isActive', 1)
        
        reg_date = user_data.get('registrationDate', '')
        ffi.memmove(user.registrationDate, reg_date.encode('utf-8'), min(len(reg_date), 19))
        
        login_date = user_data.get('lastLoginDate', '')
        ffi.memmove(user.lastLoginDate, login_date.encode('utf-8'), min(len(login_date), 19))
        
        return user[0]
    
    def _convert_user_to_dict(self, user_ptr):
        """
        تبدیل ساختار C کاربر به دیکشنری پایتون

        Parameters:
        ----------
        user_ptr : User*
            اشاره‌گر به ساختار کاربر

        Returns:
        -------
        dict
            دیکشنری حاوی اطلاعات کاربر
        """
        if user_ptr == ffi.NULL:
            return None
        
        user = {
            'username': ffi.string(user_ptr.username).decode('utf-8'),
            'fullName': ffi.string(user_ptr.fullName).decode('utf-8'),
            'email': ffi.string(user_ptr.email).decode('utf-8'),
            'phone': ffi.string(user_ptr.phone).decode('utf-8'),
            'role': ffi.string(user_ptr.role).decode('utf-8'),
            'isActive': user_ptr.isActive,
            'registrationDate': ffi.string(user_ptr.registrationDate).decode('utf-8'),
            'lastLoginDate': ffi.string(user_ptr.lastLoginDate).decode('utf-8')
        }
        
        return user
    
    def _convert_users_to_list(self, users_ptr, count):
        """
        تبدیل آرایه‌ای از ساختارهای C کاربر به لیست پایتونی

        Parameters:
        ----------
        users_ptr : User*
            اشاره‌گر به آرایه‌ای از ساختارهای کاربر
        count : int
            تعداد عناصر در آرایه

        Returns:
        -------
        list
            لیستی از دیکشنری‌های پایتون حاوی اطلاعات کاربران
        """
        if users_ptr == ffi.NULL or count <= 0:
            return []
        
        result_list = []
        
        # تبدیل هر ساختار C به دیکشنری پایتون
        for i in range(count):
            user = users_ptr[i]
            
            user_dict = {
                'username': ffi.string(user.username).decode('utf-8'),
                'fullName': ffi.string(user.fullName).decode('utf-8'),
                'email': ffi.string(user.email).decode('utf-8'),
                'phone': ffi.string(user.phone).decode('utf-8'),
                'role': ffi.string(user.role).decode('utf-8'),
                'isActive': user.isActive,
                'registrationDate': ffi.string(user.registrationDate).decode('utf-8'),
                'lastLoginDate': ffi.string(user.lastLoginDate).decode('utf-8')
            }
            
            result_list.append(user_dict)
        
        # آزاد کردن حافظه تخصیص داده شده در سمت C
        lib.user_free_array(users_ptr)
        
        return result_list 