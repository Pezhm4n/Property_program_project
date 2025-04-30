#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ماژول مدیریت کاربران
این ماژول کلاس‌های مربوط به مدیریت کاربران، احراز هویت و دسترسی‌ها را فراهم می‌کند.
"""

import os
import json
import logging
import hashlib
import datetime
from typing import Dict, List, Any, Optional, Tuple, Set

class User:
    """کلاس نگهداری اطلاعات کاربر"""
    
    def __init__(self, username: str, password_hash: str = None, 
                 is_admin: bool = False, full_name: str = "", 
                 email: str = "", phone: str = "", roles: List[str] = None):
        self.username = username
        self.password_hash = password_hash
        self.is_admin = is_admin
        self.full_name = full_name
        self.email = email
        self.phone = phone
        self.roles = roles or []
        self.last_login = None
        self.created_at = datetime.datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """تبدیل کاربر به دیکشنری"""
        return {
            "username": self.username,
            "password": self.password_hash,
            "is_admin": self.is_admin,
            "full_name": self.full_name,
            "email": self.email,
            "phone": self.phone,
            "roles": self.roles,
            "last_login": self.last_login,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """ایجاد شیء کاربر از دیکشنری"""
        user = cls(
            username=data.get("username", ""),
            password_hash=data.get("password", ""),
            is_admin=data.get("is_admin", False),
            full_name=data.get("full_name", ""),
            email=data.get("email", ""),
            phone=data.get("phone", ""),
            roles=data.get("roles", [])
        )
        user.last_login = data.get("last_login")
        user.created_at = data.get("created_at", datetime.datetime.now().isoformat())
        return user
    
    def has_role(self, role: str) -> bool:
        """بررسی آیا کاربر نقش مشخص شده را دارد"""
        return role in self.roles or self.is_admin


class UserManager:
    """کلاس مدیریت کاربران سیستم"""
    
    def __init__(self, users_file: str = None):
        self.logger = logging.getLogger(__name__)
        self.users_file = users_file or os.path.expanduser("~/property_management_users.json")
        self.users: Dict[str, User] = {}
        self.load_users()
    
    def load_users(self) -> bool:
        """بارگذاری کاربران از فایل"""
        if not os.path.exists(self.users_file):
            self.logger.warning(f"فایل کاربران یافت نشد: {self.users_file}")
            return False
        
        try:
            with open(self.users_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            self.users = {
                username: User.from_dict(user_data)
                for username, user_data in data.items()
            }
            
            self.logger.info(f"{len(self.users)} کاربر بارگذاری شد")
            return True
        except (json.JSONDecodeError, FileNotFoundError) as e:
            self.logger.error(f"خطا در بارگذاری فایل کاربران: {str(e)}")
            return False
    
    def save_users(self) -> bool:
        """ذخیره کاربران در فایل"""
        try:
            # اطمینان از وجود دایرکتوری
            os.makedirs(os.path.dirname(self.users_file), exist_ok=True)
            
            data = {
                username: user.to_dict()
                for username, user in self.users.items()
            }
            
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            
            self.logger.info(f"{len(self.users)} کاربر ذخیره شد")
            return True
        except Exception as e:
            self.logger.error(f"خطا در ذخیره فایل کاربران: {str(e)}")
            return False
    
    def hash_password(self, password: str) -> str:
        """تبدیل کلمه عبور به هش"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def authenticate(self, username: str, password: str) -> Optional[User]:
        """احراز هویت کاربر"""
        if username not in self.users:
            self.logger.warning(f"تلاش ورود ناموفق: کاربر '{username}' یافت نشد")
            return None
        
        user = self.users[username]
        hashed_password = self.hash_password(password)
        
        if user.password_hash != hashed_password:
            self.logger.warning(f"تلاش ورود ناموفق: کلمه عبور نادرست برای کاربر '{username}'")
            return None
        
        # بروزرسانی زمان آخرین ورود
        user.last_login = datetime.datetime.now().isoformat()
        self.save_users()
        
        self.logger.info(f"کاربر '{username}' با موفقیت وارد سیستم شد")
        return user
    
    def add_user(self, username: str, password: str, is_admin: bool = False, 
                 full_name: str = "", email: str = "", phone: str = "", 
                 roles: List[str] = None) -> Optional[User]:
        """افزودن کاربر جدید"""
        if username in self.users:
            self.logger.warning(f"نام کاربری '{username}' قبلا ثبت شده است")
            return None
        
        hashed_password = self.hash_password(password)
        user = User(
            username=username,
            password_hash=hashed_password,
            is_admin=is_admin,
            full_name=full_name,
            email=email,
            phone=phone,
            roles=roles or []
        )
        
        self.users[username] = user
        self.save_users()
        
        self.logger.info(f"کاربر جدید '{username}' اضافه شد")
        return user
    
    def update_user(self, username: str, **kwargs) -> Optional[User]:
        """بروزرسانی اطلاعات کاربر"""
        if username not in self.users:
            self.logger.warning(f"کاربر '{username}' برای بروزرسانی یافت نشد")
            return None
        
        user = self.users[username]
        
        # بروزرسانی فیلدهای ارسال شده
        if 'password' in kwargs:
            user.password_hash = self.hash_password(kwargs.pop('password'))
        
        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)
        
        self.save_users()
        self.logger.info(f"اطلاعات کاربر '{username}' بروزرسانی شد")
        return user
    
    def delete_user(self, username: str) -> bool:
        """حذف کاربر"""
        if username not in self.users:
            self.logger.warning(f"کاربر '{username}' برای حذف یافت نشد")
            return False
        
        del self.users[username]
        self.save_users()
        
        self.logger.info(f"کاربر '{username}' حذف شد")
        return True
    
    def get_user(self, username: str) -> Optional[User]:
        """دریافت اطلاعات کاربر"""
        return self.users.get(username)
    
    def get_all_users(self) -> List[User]:
        """دریافت لیست تمام کاربران"""
        return list(self.users.values())
    
    def has_admin(self) -> bool:
        """بررسی آیا حداقل یک کاربر مدیر وجود دارد"""
        return any(user.is_admin for user in self.users.values())
    
    def add_role_to_user(self, username: str, role: str) -> bool:
        """افزودن نقش به کاربر"""
        if username not in self.users:
            self.logger.warning(f"کاربر '{username}' برای افزودن نقش یافت نشد")
            return False
        
        user = self.users[username]
        if role not in user.roles:
            user.roles.append(role)
            self.save_users()
            self.logger.info(f"نقش '{role}' به کاربر '{username}' اضافه شد")
        
        return True
    
    def remove_role_from_user(self, username: str, role: str) -> bool:
        """حذف نقش از کاربر"""
        if username not in self.users:
            self.logger.warning(f"کاربر '{username}' برای حذف نقش یافت نشد")
            return False
        
        user = self.users[username]
        if role in user.roles:
            user.roles.remove(role)
            self.save_users()
            self.logger.info(f"نقش '{role}' از کاربر '{username}' حذف شد")
        
        return True


class AuthorizationError(Exception):
    """خطای عدم دسترسی کاربر"""
    pass


class Permission:
    """کلاس نگهداری اطلاعات دسترسی"""
    
    # لیست دسترسی‌های تعریف شده
    VIEW_PROPERTIES = "view_properties"
    ADD_PROPERTY = "add_property"
    EDIT_PROPERTY = "edit_property"
    DELETE_PROPERTY = "delete_property"
    GENERATE_REPORTS = "generate_reports"
    MANAGE_USERS = "manage_users"
    
    # گروه‌بندی دسترسی‌ها
    ROLE_ADMIN = [VIEW_PROPERTIES, ADD_PROPERTY, EDIT_PROPERTY, DELETE_PROPERTY, 
                  GENERATE_REPORTS, MANAGE_USERS]
    ROLE_MANAGER = [VIEW_PROPERTIES, ADD_PROPERTY, EDIT_PROPERTY, GENERATE_REPORTS]
    ROLE_AGENT = [VIEW_PROPERTIES, ADD_PROPERTY]
    ROLE_VIEWER = [VIEW_PROPERTIES]


class PermissionManager:
    """کلاس مدیریت دسترسی‌های سیستم"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # دیکشنری نگاشت نقش‌ها به مجموعه‌ای از دسترسی‌ها
        self.role_permissions: Dict[str, Set[str]] = {
            "admin": set(Permission.ROLE_ADMIN),
            "manager": set(Permission.ROLE_MANAGER),
            "agent": set(Permission.ROLE_AGENT),
            "viewer": set(Permission.ROLE_VIEWER)
        }
    
    def check_permission(self, user: User, permission: str) -> bool:
        """بررسی آیا کاربر دسترسی مورد نظر را دارد"""
        # مدیر همه دسترسی‌ها را دارد
        if user.is_admin:
            return True
        
        # بررسی دسترسی‌های هر نقش کاربر
        for role in user.roles:
            if role in self.role_permissions and permission in self.role_permissions[role]:
                return True
        
        return False
    
    def require_permission(self, user: User, permission: str):
        """اعمال دسترسی - در صورت عدم دسترسی خطا می‌دهد"""
        if not self.check_permission(user, permission):
            self.logger.warning(f"دسترسی غیرمجاز: کاربر '{user.username}' دسترسی '{permission}' را ندارد")
            raise AuthorizationError(f"شما دسترسی لازم برای انجام این عملیات را ندارید")
    
    def get_user_permissions(self, user: User) -> Set[str]:
        """دریافت تمام دسترسی‌های کاربر"""
        if user.is_admin:
            # مدیر همه دسترسی‌ها را دارد
            return set().union(*self.role_permissions.values())
        
        # ترکیب دسترسی‌های تمام نقش‌های کاربر
        permissions = set()
        for role in user.roles:
            if role in self.role_permissions:
                permissions.update(self.role_permissions[role])
        
        return permissions
    
    def add_role_permission(self, role: str, permission: str) -> bool:
        """افزودن دسترسی به نقش"""
        if role not in self.role_permissions:
            self.role_permissions[role] = set()
        
        self.role_permissions[role].add(permission)
        self.logger.info(f"دسترسی '{permission}' به نقش '{role}' اضافه شد")
        return True
    
    def remove_role_permission(self, role: str, permission: str) -> bool:
        """حذف دسترسی از نقش"""
        if role in self.role_permissions and permission in self.role_permissions[role]:
            self.role_permissions[role].remove(permission)
            self.logger.info(f"دسترسی '{permission}' از نقش '{role}' حذف شد")
            return True
        
        return False


# نمونه استفاده:
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # ایجاد مدیر کاربران
    user_manager = UserManager()
    
    # بررسی وجود حساب مدیر
    if not user_manager.has_admin():
        # ایجاد حساب مدیر پیش‌فرض
        user_manager.add_user(
            username="admin",
            password="admin123",
            is_admin=True,
            full_name="مدیر سیستم",
            email="admin@example.com"
        )
    
    # ایجاد کاربر با نقش مدیر
    user_manager.add_user(
        username="manager1",
        password="manager123",
        full_name="مدیر فروش",
        email="manager@example.com",
        roles=["manager"]
    )
    
    # احراز هویت کاربر
    user = user_manager.authenticate("admin", "admin123")
    
    if user:
        # ایجاد مدیر دسترسی
        perm_manager = PermissionManager()
        
        # بررسی دسترسی
        try:
            perm_manager.require_permission(user, Permission.MANAGE_USERS)
            print("کاربر دسترسی مدیریت کاربران را دارد.")
        except AuthorizationError as e:
            print(f"خطای دسترسی: {e}") 