import json
import os
from abc import ABC, abstractmethod

class StorageInterface(ABC):
    @abstractmethod
    def save(self, key: str, value: str):
        pass

    @abstractmethod
    def load(self, key: str) -> str:
        pass

class JsonStorage(StorageInterface):
    def __init__(self, filepath: str):
        self.filepath = filepath

    def save(self, key: str, value: str):
        prefs = {}
        try:
            if os.path.exists(self.filepath):
                with open(self.filepath, 'r') as f:
                    prefs = json.load(f)
        except Exception:
            pass
            
        prefs[key] = value
        try:
            with open(self.filepath, 'w') as f:
                json.dump(prefs, f)
        except Exception:
            pass

    def load(self, key: str) -> str:
        try:
            if os.path.exists(self.filepath):
                with open(self.filepath, 'r') as f:
                    prefs = json.load(f)
                    return prefs.get(key, "")
        except Exception:
            pass
        return ""

class SessionManager:
    def __init__(self, storage: StorageInterface = None):
        if storage is None:
            settings_path = os.path.join(os.path.dirname(__file__), '..', '..', 'settings.json')
            storage = JsonStorage(settings_path)
        self.storage = storage
        self.session_token = None
        self.username = None
        self.remember_me = False
        self.theme = self.storage.load("theme") or "dark"
        self._load_preferences()

    def set_session(self, token: str, username: str, remember: bool):
        self.session_token = token
        self.username = username
        self.remember_me = remember
        self._save_preferences()

    def set_theme(self, theme: str):
        self.theme = theme
        self.storage.save("theme", theme)

    def clear_session(self):
        self.session_token = None
        self.username = None
        self.remember_me = False
        self._save_preferences()

    def _save_preferences(self):
        if self.remember_me and self.username:
            self.storage.save("username", self.username)
        else:
            self.storage.save("username", "")

    def _load_preferences(self):
        saved_user = self.storage.load("username")
        if saved_user:
            self.username = saved_user
            self.remember_me = True

    def get_db_path(self) -> str:
        env_path = os.getenv("DB_PATH")
        if env_path:
            return env_path
        saved_path = self.storage.load("db_path")
        if saved_path:
            return saved_path
        return "real_estate.db"

    def get_session_timeout(self) -> int:
        val = self.storage.load("session_timeout_minutes")
        try:
            return int(val) if val else 15
        except Exception:
            return 15

    def get_window_size(self) -> tuple[int, int]:
        w = self.storage.load("window_width")
        h = self.storage.load("window_height")
        try:
            return (int(w) if w else 1100, int(h) if h else 700)
        except Exception:
            return (1100, 700)

    def get_backup_directory(self) -> str:
        saved_dir = self.storage.load("backup_dir")
        return saved_dir if saved_dir else "backups"

    def get_page_size(self) -> int:
        val = self.storage.load("page_size")
        try:
            return int(val) if val else 20
        except Exception:
            return 20

    def get_default_sorting(self) -> tuple[str, bool]:
        col = self.storage.load("sort_column") or "date_registered"
        asc = self.storage.load("sort_ascending")
        is_asc = (str(asc).lower() == "true") if asc else False
        return col, is_asc
