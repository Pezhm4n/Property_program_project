import os

class ThemeManager:
    def __init__(self):
        self.current_theme = "dark"
        from core.resource_manager import ResourceManager
        self.styles_dir = ResourceManager.resolve_path(os.path.join('app', 'resources', 'styles'))

    def apply_theme(self, app, theme_name="dark"):
        self.current_theme = theme_name
        base_path = os.path.join(self.styles_dir, 'base.qss')
        theme_path = os.path.join(self.styles_dir, f'theme_{theme_name}.qss')
        
        stylesheet = ""
        for path in (base_path, theme_path):
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    stylesheet += f.read() + "\n"
        
        app.setStyleSheet(stylesheet)
