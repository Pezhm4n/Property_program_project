import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.session_manager import SessionManager

def test_session_manager_remember_me(tmp_path):
    sm = SessionManager()
    sm.settings_file = os.path.join(tmp_path, "settings.json")
    
    # Test setting session with RBAC data
    login_data = {
        "token": "dummy-token",
        "username": "admin",
        "user_id": 1,
        "role": "admin",
        "role_id": 1,
        "first_name": "مدیر",
        "last_name": "سیستم",
        "permissions": ["VIEW_PROPERTIES", "CREATE_PROPERTY", "MANAGE_USERS"]
    }
    sm.set_session(login_data, True)
    assert sm.session_token == "dummy-token"
    assert sm.username == "admin"
    assert sm.role == "admin"
    assert sm.has_permission("VIEW_PROPERTIES") is True
    assert sm.has_permission("DELETE_PROPERTY") is False
    assert sm.remember_me is True
    
    # Test clearing session
    sm.clear_session()
    assert sm.session_token is None
    assert sm.username is None
