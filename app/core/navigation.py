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
        if self.splash_screen:
            self.splash_screen.close()
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
