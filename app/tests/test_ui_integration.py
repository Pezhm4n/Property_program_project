import pytest
import sys
import os
import sqlite3

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'bridge')))
from re_bridge.services import PropertyService, DashboardService, BackupService, calculate_financials
from re_bridge.models import PropertyDTO, SearchState

def test_commission_and_tax_calculation():
    # 1. Residential Sale (BR-001: 0.25% + 9% VAT)
    p1 = PropertyDTO(
        id=1, is_archived=False, category="مسکونی", listing_type="فروش",
        city="Tehran", municipal_district=1, address="T1", owner_phone="0912",
        area_sqm=100, sale_price=1000000, rent_deposit=0, rent_monthly=0, date_registered="1405/01/01"
    )
    fin1 = calculate_financials(p1)
    assert fin1["commission"] == 2500  # 1,000,000 * 0.0025
    assert fin1["tax"] == 225         # 2500 * 0.09
    
    # 2. Commercial Sale (BR-001: 0.5% + 9% VAT)
    p2 = PropertyDTO(
        id=2, is_archived=False, category="تجاری", listing_type="فروش",
        city="Tehran", municipal_district=2, address="T2", owner_phone="0912",
        area_sqm=80, sale_price=1000000, rent_deposit=0, rent_monthly=0, date_registered="1405/01/01"
    )
    fin2 = calculate_financials(p2)
    assert fin2["commission"] == 5000  # 1,000,000 * 0.005
    assert fin2["tax"] == 450         # 5000 * 0.09

def test_backup_and_restore():
    token = "test_token"
    backup_file = "test_backup.db"
    
    # Create some dummy property first to ensure database is not empty
    p = PropertyDTO(
        id=0, is_archived=False, category="مسکونی", listing_type="فروش",
        city="Tehran", municipal_district=1, address="Address", owner_phone="0912",
        area_sqm=100, sale_price=1000, rent_deposit=0, rent_monthly=0, date_registered="1405/01/01"
    )
    res = PropertyService.create_property(token, p)
    assert res["id"] > 0
    
    # Backup
    BackupService.create_backup(token, backup_file)
    assert os.path.exists(backup_file)
    
    # Delete original db to prove restore works
    if os.path.exists("real_estate.db"):
        os.remove("real_estate.db")
        
    # Restore
    BackupService.restore_backup(token, backup_file)
    assert os.path.exists("real_estate.db")
    
    # Clean up backup file
    if os.path.exists(backup_file):
        os.remove(backup_file)

def test_dashboard_real_data():
    token = "test_token"
    # Ensure there is data
    p = PropertyDTO(
        id=0, is_archived=False, category="مسکونی", listing_type="فروش",
        city="Tehran", municipal_district=1, address="Address", owner_phone="0912",
        area_sqm=100, sale_price=1000, rent_deposit=0, rent_monthly=0, date_registered="1405/01/01"
    )
    PropertyService.create_property(token, p)
    
    data = DashboardService.get_dashboard_data(token)
    assert data["total_properties"] > 0
    assert data["active_properties"] > 0
    assert len(data["recent_activities"]) > 0
