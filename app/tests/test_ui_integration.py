import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'bridge')))
from re_bridge.services import PropertyService, DashboardService, BackupService, re_init, re_close
from re_bridge.models import PropertyDTO
@pytest.fixture(autouse=True)
def setup_test_db():
    re_init("real_estate_test.db", "core/migrations")
    from re_bridge.services import AuthService
    # Seed initial user so property registration foreign key succeeds
    AuthService.create_initial_admin("admin", "password123")
    yield
    re_close()
    if os.path.exists("real_estate_test.db"):
        try:
            os.remove("real_estate_test.db")
        except Exception:
            pass
def get_auth_token():
    from re_bridge.services import AuthService
    from re_bridge.models import LoginRequest
    res = AuthService.login(LoginRequest(username="admin", password="password123"))
    return res["token"]

def test_commission_and_tax_calculation():
    token = get_auth_token()
    
    # 1. Residential Sale (BR-001: 0.25% + 9% VAT)
    p1 = PropertyDTO(
        id=0, is_archived=False, category="مسکونی", listing_type="فروش",
        city="Tehran", municipal_district=1, address="T1", owner_phone="09123456789",
        area_sqm=100, sale_price=1000000, rent_deposit=0, rent_monthly=0, date_registered="1405/01/01"
    )
    PropertyService.create_property(token, p1)
    
    # 2. Commercial Sale (BR-001: 0.5% + 9% VAT)
    p2 = PropertyDTO(
        id=0, is_archived=False, category="تجاری", listing_type="فروش",
        city="Tehran", municipal_district=2, address="T2", owner_phone="09123456789",
        area_sqm=80, sale_price=1000000, rent_deposit=0, rent_monthly=0, date_registered="1405/01/01"
    )
    PropertyService.create_property(token, p2)
    
    data = DashboardService.get_dashboard_data(token)
    financials = data["charts"]["financials"]
    assert financials["commission"] == 7500
    assert financials["tax"] == 675

def test_backup_and_restore():
    token = get_auth_token()
    backup_file = "test_backup.db"
    
    p = PropertyDTO(
        id=0, is_archived=False, category="مسکونی", listing_type="فروش",
        city="Tehran", municipal_district=1, address="Address", owner_phone="09123456789",
        area_sqm=100, sale_price=1000, rent_deposit=0, rent_monthly=0, date_registered="1405/01/01"
    )
    res = PropertyService.create_property(token, p)
    assert res["id"] > 0
    
    # Backup
    BackupService.create_backup(token, backup_file)
    assert os.path.exists(backup_file)
    
    # Delete original db to prove restore works
    re_close()
    if os.path.exists("real_estate_test.db"):
        try:
            os.remove("real_estate_test.db")
        except Exception:
            pass
        
    # Restore
    BackupService.restore_backup(token, backup_file)
    assert os.path.exists("real_estate_test.db")
    
    # Clean up backup file
    if os.path.exists(backup_file):
        os.remove(backup_file)

def test_dashboard_real_data():
    token = get_auth_token()
    p = PropertyDTO(
        id=0, is_archived=False, category="مسکونی", listing_type="فروش",
        city="Tehran", municipal_district=1, address="Address", owner_phone="09123456789",
        area_sqm=100, sale_price=1000, rent_deposit=0, rent_monthly=0, date_registered="1405/01/01"
    )
    PropertyService.create_property(token, p)
    
    data = DashboardService.get_dashboard_data(token)
    assert data["total_properties"] > 0
    assert data["active_properties"] > 0
    assert len(data["recent_activities"]) > 0
