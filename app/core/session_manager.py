import json
import os

class SessionManager:
    def __init__(self):
        self.session_token = None
        self.username = None
        self.remember_me = False
        self.settings_file = os.path.join(os.path.dirname(__file__), '..', '..', 'settings.json')
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
        try:
            prefs = {"username": self.username if self.remember_me else ""}
            with open(self.settings_file, 'w') as f:
                json.dump(prefs, f)
        except Exception:
            pass

    def _load_preferences(self):
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    prefs = json.load(f)
                    self.username = prefs.get("username", "")
                    if self.username:
                        self.remember_me = True
        except Exception:
            pass

    def start_timeout_timer(self):
        # @todo Skeleton for session timeout handling
        pass
