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
        self._load_preferences()

    def set_session(self, token: str, username: str, remember: bool):
        self.session_token = token
        self.username = username
        self.remember_me = remember
        self._save_preferences()

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

    def start_timeout_timer(self):
        # @todo Skeleton for session timeout handling
        pass
