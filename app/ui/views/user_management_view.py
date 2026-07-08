from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
                                 QTableWidgetItem, QPushButton, QHeaderView, QLabel,
                                 QDialog, QFormLayout, QLineEdit, QComboBox, QDialogButtonBox,
                                 QMessageBox)
from PySide6.QtCore import Qt
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'bridge')))
from re_bridge.services import UserManagementService
from ui.dialogs import show_error_dialog


class CreateUserDialog(QDialog):
    def __init__(self, parent=None, token=None):
        super().__init__(parent)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setWindowTitle("ایجاد کاربر جدید")
        self.resize(400, 360)
        self.token = token

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        form = QFormLayout()
        form.setSpacing(10)

        self.txt_username = QLineEdit()
        self.txt_username.setPlaceholderText("حداقل ۳ کاراکتر")
        form.addRow("نام کاربری:", self.txt_username)

        self.txt_password = QLineEdit()
        self.txt_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_password.setPlaceholderText("حداقل ۶ کاراکتر")
        form.addRow("رمز عبور:", self.txt_password)

        self.txt_first_name = QLineEdit()
        form.addRow("نام:", self.txt_first_name)

        self.txt_last_name = QLineEdit()
        form.addRow("نام خانوادگی:", self.txt_last_name)

        self.txt_national_id = QLineEdit()
        self.txt_national_id.setPlaceholderText("۱۰ رقم")
        form.addRow("کد ملی:", self.txt_national_id)

        self.txt_phone = QLineEdit()
        self.txt_phone.setPlaceholderText("09xxxxxxxxx")
        form.addRow("تلفن:", self.txt_phone)

        self.cmb_role = QComboBox()
        self.cmb_role.addItem("کاربر عادی (مشاور)", 2)
        self.cmb_role.addItem("مدیر (ادمین)", 1)
        form.addRow("نقش:", self.cmb_role)

        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def validate_fields(self) -> list:
        default_style = ""
        error_style = "border: 1.5px solid #ef4444; background-color: #fef2f2;"
        
        self.txt_username.setStyleSheet(default_style)
        self.txt_password.setStyleSheet(default_style)
        self.txt_first_name.setStyleSheet(default_style)
        self.txt_last_name.setStyleSheet(default_style)
        self.txt_national_id.setStyleSheet(default_style)
        self.txt_phone.setStyleSheet(default_style)
        
        username = self.txt_username.text().strip()
        password = self.txt_password.text().strip()
        first_name = self.txt_first_name.text().strip()
        last_name = self.txt_last_name.text().strip()
        national_id = self.txt_national_id.text().strip()
        phone = self.txt_phone.text().strip()
        
        errors = []
        if len(username) < 3:
            self.txt_username.setStyleSheet(error_style)
            errors.append("نام کاربری باید حداقل ۳ کاراکتر باشد.")
            
        if len(password) < 6:
            self.txt_password.setStyleSheet(error_style)
            errors.append("رمز عبور باید حداقل ۶ کاراکتر باشد.")
            
        if not first_name:
            self.txt_first_name.setStyleSheet(error_style)
            errors.append("نام نمی‌تواند خالی باشد.")
            
        if not last_name:
            self.txt_last_name.setStyleSheet(error_style)
            errors.append("نام خانوادگی نمی‌تواند خالی باشد.")
            
        if len(national_id) != 10 or not national_id.isdigit():
            self.txt_national_id.setStyleSheet(error_style)
            errors.append("کد ملی باید دقیقاً ۱۰ رقم عددی باشد.")
            
        if len(phone) != 11 or not phone.startswith("09") or not phone.isdigit():
            self.txt_phone.setStyleSheet(error_style)
            errors.append("شماره تلفن همراه باید ۱۱ رقم بوده و با ۰۹ شروع شود.")
            
        return errors

    def accept(self):
        errors = self.validate_fields()
        if errors:
            QMessageBox.warning(self, "خطای اعتبارسنجی", "\n".join(errors))
            return
            
        if self.token:
            from ui.dialogs import show_error_dialog
            user_data = self.get_user_data()
            try:
                UserManagementService.create_user(self.token, user_data)
            except Exception as e:
                # If there's a validation (-1) or duplicate (-3) error, highlight
                if hasattr(e, 'code') and e.code in (-1, -3):
                    error_style = "border: 1.5px solid #ef4444; background-color: #fef2f2;"
                    self.txt_username.setStyleSheet(error_style)
                    self.txt_national_id.setStyleSheet(error_style)
                    self.txt_phone.setStyleSheet(error_style)
                show_error_dialog(self, e)
                return
                
        super().accept()

    def get_user_data(self) -> dict:
        return {
            "username": self.txt_username.text().strip(),
            "password": self.txt_password.text().strip(),
            "first_name": self.txt_first_name.text().strip(),
            "last_name": self.txt_last_name.text().strip(),
            "national_id": self.txt_national_id.text().strip(),
            "phone": self.txt_phone.text().strip(),
            "role_id": self.cmb_role.currentData()
        }


class ResetPasswordDialog(QDialog):
    def __init__(self, username, parent=None, token=None, user_id=None):
        super().__init__(parent)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self.setWindowTitle(f"ریست رمز عبور: {username}")
        self.resize(350, 150)
        self.token = token
        self.user_id = user_id

        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.txt_new_password = QLineEdit()
        self.txt_new_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_new_password.setPlaceholderText("حداقل ۶ کاراکتر")
        form.addRow("رمز عبور جدید:", self.txt_new_password)
        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_password(self) -> str:
        return self.txt_new_password.text().strip()

    def accept(self):
        new_pw = self.get_password()
        if len(new_pw) < 6:
            self.txt_new_password.setStyleSheet("border: 1.5px solid #ef4444; background-color: #fef2f2;")
            QMessageBox.warning(self, "خطا", "رمز عبور باید حداقل ۶ کاراکتر باشد.")
            return
            
        if self.token and self.user_id:
            from ui.dialogs import show_error_dialog
            try:
                UserManagementService.reset_password(self.token, self.user_id, new_pw)
                QMessageBox.information(self, "موفق", "رمز عبور با موفقیت تغییر کرد.")
            except Exception as e:
                show_error_dialog(self, e)
                return
                
        super().accept()


class UserManagementView(QWidget):
    def __init__(self, session_manager):
        super().__init__()
        self.session = session_manager
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Header
        header_layout = QHBoxLayout()
        title = QLabel("👥 مدیریت کاربران")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        header_layout.addWidget(title)
        header_layout.addStretch()

        btn_create = QPushButton("➕ کاربر جدید")
        btn_create.setObjectName("btnCreateUser")
        btn_create.clicked.connect(self.create_user)
        header_layout.addWidget(btn_create)
        layout.addLayout(header_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "نام کاربری", "نقش", "وضعیت", "آخرین ورود", "تاریخ ایجاد", "تلفن", "عملیات"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(6, 240)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.table)

        self.refresh_data()

    def refresh_data(self):
        try:
            users = UserManagementService.get_all_users(self.session.session_token)
            self.table.setRowCount(len(users))
            
            for row, user in enumerate(users):
                self.table.setItem(row, 0, QTableWidgetItem(user.get("username", "")))
                
                role_name = user.get("role", "")
                role_display = "مدیر" if role_name == "admin" else "مشاور"
                self.table.setItem(row, 1, QTableWidgetItem(role_display))
                
                is_disabled = user.get("is_disabled", False)
                status = "غیرفعال" if is_disabled else "فعال"
                status_item = QTableWidgetItem(status)
                if is_disabled:
                    status_item.setForeground(Qt.GlobalColor.red)
                else:
                    status_item.setForeground(Qt.GlobalColor.green)
                self.table.setItem(row, 2, status_item)
                
                self.table.setItem(row, 3, QTableWidgetItem(user.get("last_login_at", "—")))
                self.table.setItem(row, 4, QTableWidgetItem(user.get("created_at", "")))
                self.table.setItem(row, 5, QTableWidgetItem(user.get("phone", "")))
                
                # Action buttons
                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(4, 2, 4, 2)
                actions_layout.setSpacing(4)

                user_id = user.get("id", 0)
                username = user.get("username", "")

                btn_toggle = QPushButton("غیرفعال" if not is_disabled else "فعال")
                btn_toggle.setFixedWidth(70)
                btn_toggle.clicked.connect(lambda checked, uid=user_id, en=is_disabled: self.toggle_user(uid, en))
                actions_layout.addWidget(btn_toggle)

                btn_reset = QPushButton("ریست رمز")
                btn_reset.setFixedWidth(70)
                btn_reset.clicked.connect(lambda checked, uid=user_id, uname=username: self.reset_password(uid, uname))
                actions_layout.addWidget(btn_reset)

                btn_role = QPushButton("تغییر نقش")
                btn_role.setFixedWidth(70)
                btn_role.clicked.connect(lambda checked, uid=user_id, rid=user.get("role_id", 2): self.change_role(uid, rid))
                actions_layout.addWidget(btn_role)

                self.table.setCellWidget(row, 6, actions_widget)

        except Exception as e:
            show_error_dialog(self, e)

    def create_user(self):
        dialog = CreateUserDialog(self, token=self.session.session_token)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh_data()

    def toggle_user(self, user_id, currently_disabled):
        try:
            UserManagementService.toggle_status(self.session.session_token, user_id, currently_disabled)
            self.refresh_data()
        except Exception as e:
            show_error_dialog(self, e)

    def reset_password(self, user_id, username):
        dialog = ResetPasswordDialog(username, self, token=self.session.session_token, user_id=user_id)
        dialog.exec()

    def change_role(self, user_id, current_role_id):
        new_role_id = 1 if current_role_id == 2 else 2
        role_name = "مدیر" if new_role_id == 1 else "مشاور"
        
        reply = QMessageBox.question(
            self, "تغییر نقش",
            f"آیا از تغییر نقش به «{role_name}» اطمینان دارید؟",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                UserManagementService.change_role(self.session.session_token, user_id, new_role_id)
                self.refresh_data()
            except Exception as e:
                show_error_dialog(self, e)
