from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QPushButton, QFormLayout, QHBoxLayout
from PySide6.QtCore import Qt

class SettingsPage(QWidget):
    def __init__(self, session_manager, main_window, parent=None):
        super().__init__(parent)
        self.session = session_manager
        self.main_window = main_window
        self.setObjectName("SettingsPage")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        # Header
        self.header = QLabel("تنظیمات سیستم")
        self.header.setObjectName("settingsHeader")
        self.header.setStyleSheet("font-size: 22px; font-weight: bold;")
        self.header.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.header)
        
        # Form
        form = QFormLayout()
        form.setSpacing(16)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        
        self.cmb_theme = QComboBox()
        self.cmb_theme.addItems(["تیره", "روشن"])
        self.cmb_theme.setCurrentText("تیره" if self.session.theme == "dark" else "روشن")
        form.addRow("پوسته برنامه:", self.cmb_theme)
        # Password Section
        self.btn_change_password = QPushButton("تغییر رمز عبور")
        self.btn_change_password.setFixedWidth(150)
        self.btn_change_password.clicked.connect(self.show_change_password_dialog)
        form.addRow("امنیت حساب:", self.btn_change_password)
        
        layout.addLayout(form)
        
        # Save Button
        btn_layout = QHBoxLayout()
        self.btn_save = QPushButton("ذخیره تغییرات")
        self.btn_save.setFixedWidth(150)
        self.btn_save.clicked.connect(self.save_settings)
        btn_layout.addWidget(self.btn_save)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        layout.addStretch()
        
    def save_settings(self):
        new_theme = "dark" if self.cmb_theme.currentText() == "تیره" else "light"
        if new_theme != self.session.theme:
            self.session.set_theme(new_theme)
            from PySide6.QtWidgets import QApplication
            from core.theme_manager import ThemeManager
            theme_manager = ThemeManager()
            theme_manager.apply_theme(QApplication.instance(), new_theme)

    def show_change_password_dialog(self):
        from ui.dialogs.change_password_dialog import ChangePasswordDialog
        dlg = ChangePasswordDialog(self.session.username, self)
        dlg.exec()
