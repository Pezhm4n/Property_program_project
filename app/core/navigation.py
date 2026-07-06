from ui.login_window import LoginWindow
from ui.main_window import MainWindow

class NavigationManager:
    def __init__(self):
        self.login_window = None
        self.main_window = None

    def show_login(self):
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
