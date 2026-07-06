import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.session_manager import SessionManager

def test_session_manager_remember_me(tmp_path):
    sm = SessionManager()
    sm.settings_file = os.path.join(tmp_path, "settings.json")
    
    # Test setting session
    sm.set_session("dummy-token", "admin", True)
    assert sm.session_token == "dummy-token"
    assert sm.username == "admin"
    assert sm.remember_me is True
    
    # Test clearing session
    sm.clear_session()
    assert sm.session_token is None
    assert sm.username is None
