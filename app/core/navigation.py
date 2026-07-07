from ui.login_window import LoginWindow
from ui.main_window import MainWindow
from ui.splash_screen import SplashScreen
from core.session_manager import SessionManager

class NavigationManager:
    def __init__(self):
        self.login_window = None
        self.main_window = None
        self.splash_screen = None
        self.session = SessionManager()

    def show_splash(self):
        if not self.splash_screen:
            self.splash_screen = SplashScreen()
        self.splash_screen.show()

    def show_login(self):
        self.stop_inactivity_filter()
        if self.splash_screen:
            self.splash_screen.close()
            
        # First-run Setup Wizard Check
        from re_bridge.services import AuthService
        from ui.dialogs.wizard_dialog import WizardDialog
        try:
            if not AuthService.has_any_user():
                dlg = WizardDialog()
                if dlg.exec() != WizardDialog.DialogCode.Accepted:
                    import sys
                    sys.exit(0)
        except Exception:
            pass # fallback if DB connection fails
            
        if not self.login_window:
            self.login_window = LoginWindow(self)
        self.login_window.show()
        if self.main_window:
            self.main_window.close()

    def show_main_window(self):
        if not self.main_window:
            self.main_window = MainWindow(self)
        self.main_window.show()
        if self.login_window:
            self.login_window.close()
        self.start_inactivity_filter()

    def handle_timeout_logout(self):
        self.stop_inactivity_filter()
        self.session.clear_session()
        self.show_login()
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.warning(self.login_window, "قطع نشست", "نشست شما به دلیل عدم فعالیت بیش از حد منقضی شد.")

    def start_inactivity_filter(self):
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import QObject, QEvent, QTimer
        
        class InactivityEventFilter(QObject):
            def __init__(self, timeout_minutes, logout_callback, parent=None):
                super().__init__(parent)
                self.timeout_ms = timeout_minutes * 60 * 1000
                self.logout_callback = logout_callback
                self.timer = QTimer(self)
                self.timer.setInterval(self.timeout_ms)
                self.timer.setSingleShot(True)
                self.timer.timeout.connect(self.logout_callback)
                self.timer.start()

            def eventFilter(self, obj, event):
                if event.type() in (QEvent.Type.MouseMove, QEvent.Type.MouseButtonPress,
                                    QEvent.Type.KeyPress, QEvent.Type.Wheel):
                    self.timer.start()
                return super().eventFilter(obj, event)
                
        timeout_mins = self.session.get_session_timeout()
        app = QApplication.instance()
        self.inactivity_filter = InactivityEventFilter(timeout_mins, self.handle_timeout_logout, app)
        app.installEventFilter(self.inactivity_filter)

    def stop_inactivity_filter(self):
        if hasattr(self, 'inactivity_filter') and self.inactivity_filter:
            from PySide6.QtWidgets import QApplication
            QApplication.instance().removeEventFilter(self.inactivity_filter)
            self.inactivity_filter.timer.stop()
            self.inactivity_filter = None
