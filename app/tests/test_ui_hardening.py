import pytest
import os
import sys
from unittest.mock import MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'bridge')))
from re_bridge.services import AuthService, re_init, re_close
from re_bridge.exceptions import ValidationError, ForbiddenError, AuthenticationError
from core.session_manager import SessionManager, JsonStorage

@pytest.fixture(autouse=True)
def setup_test_db():
    db_name = "real_estate_hardening_test.db"
    re_init(db_name, "core/migrations")
    yield db_name
    re_close()
    if os.path.exists(db_name):
        try:
            os.remove(db_name)
        except Exception:
            pass

def test_configuration_chain(monkeypatch, tmp_path):
    # Test Env override
    monkeypatch.setenv("DB_PATH", "env_database.db")
    storage = JsonStorage(str(tmp_path / "settings_test.json"))
    manager = SessionManager(storage)
    assert manager.get_db_path() == "env_database.db"
    
    # Test settings.json override
    monkeypatch.delenv("DB_PATH", raising=False)
    storage.save("db_path", "json_database.db")
    manager = SessionManager(storage)
    assert manager.get_db_path() == "json_database.db"
    
    # Test Default fallback
    storage.save("db_path", "")
    manager = SessionManager(storage)
    assert manager.get_db_path() == "real_estate.db"

def test_initial_admin_setup_wizard_protection():
    # Since DB is empty, has_any_user should be False
    assert AuthService.has_any_user() is False
    
    # Create initial admin
    success = AuthService.create_initial_admin("wizard_admin", "password123")
    assert success is True
    
    # Now has_any_user should be True
    assert AuthService.has_any_user() is True
    
    # Attempting to seed initial admin again should fail with RE_ERR_FORBIDDEN (-6)
    with pytest.raises(ForbiddenError) as excinfo:
        AuthService.create_initial_admin("hacker_admin", "password123")
    assert excinfo.value.code == -6 # RE_ERR_FORBIDDEN

def test_change_password_flow():
    # Setup initial admin
    AuthService.create_initial_admin("admin_user", "password123")
    
    # Attempt change password with wrong current password -> AuthError (-4)
    with pytest.raises(AuthenticationError) as excinfo:
        AuthService.change_password("admin_user", "wrong_current", "new_password123")
    assert excinfo.value.code == -4 # RE_ERR_AUTH
    
    # Attempt change password with too short new password -> ValidationError (-1)
    with pytest.raises(ValidationError) as excinfo:
        AuthService.change_password("admin_user", "password123", "123")
    assert excinfo.value.code == -1 # RE_ERR_VALIDATION

    # Correct change password
    success = AuthService.change_password("admin_user", "password123", "new_password123")
    assert success is True

def test_backup_restore_integrity_check(tmp_path):
    # Create a corrupted mock backup file (plain text instead of SQLite database)
    bad_backup_path = tmp_path / "corrupted_backup.db"
    bad_backup_path.write_text("THIS IS NOT A SQLITE DATABASE FILE")

    # Restoring from this file should raise a ValueError
    from re_bridge.services import BackupService
    with pytest.raises(ValueError) as excinfo:
        BackupService.restore_backup("test_token", str(bad_backup_path))
    assert "اعتبارسنجی بکاپ با خطا مواجه شد" in str(excinfo.value)

def test_property_archive_restore_search_filtering():
    # 1. Create a dynamic test admin
    AuthService.create_initial_admin("test_user_filtering", "password123")
    
    # 2. Login to get token
    from re_bridge.models import LoginRequest
    resp = AuthService.login(LoginRequest(username="test_user_filtering", password="password123"))
    token = resp.token
    
    # 3. Create properties DTO
    from re_bridge.models import PropertyDTO, SearchState
    from re_bridge.services import PropertyService
    
    prop_dto = PropertyDTO(
        id=0,
        is_archived=False,
        category="مسکونی",
        listing_type="فروش",
        city="تهران",
        municipal_district=5,
        address="خیابان کاشانی",
        owner_phone="09121111111",
        area_sqm=85,
        sale_price=5000000,
        rent_deposit=0,
        rent_monthly=0,
        date_registered=""
    )
    

    
    # Create the property
    success = PropertyService.create_property(token, prop_dto)
    assert success.get("id") == 1
    # Search properties (default: active only)
    search_state = SearchState()
    properties = PropertyService.get_properties(token, search_state)
    assert len(properties) == 1
    assert properties[0].is_archived is False
    
    # Archive the property
    prop_id = properties[0].id
    PropertyService.archive_property(token, prop_id)
    
    # Search properties (default: active only) should return 0 items!
    properties = PropertyService.get_properties(token, search_state)
    assert len(properties) == 0
    
    # Search properties with is_archived = True filter
    search_state.filters = {"is_archived": True}
    properties = PropertyService.get_properties(token, search_state)
    assert len(properties) == 1
    assert properties[0].id == prop_id
    assert properties[0].is_archived is True
    
    # Search properties with is_archived = None or omitted (status "All")
    search_state.filters = {}
    properties = PropertyService.get_properties(token, search_state)
    assert len(properties) == 1
    
    # Restore the property
    PropertyService.restore_property(token, prop_id)
    
    # Search properties (default: active only) should return 1 item again!
    search_state.filters = {"is_archived": False}
    properties = PropertyService.get_properties(token, search_state)
    assert len(properties) == 1
    assert properties[0].is_archived is False
