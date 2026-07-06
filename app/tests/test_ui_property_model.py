import pytest
from PySide6.QtCore import Qt
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'bridge')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from re_bridge.models import PropertyDTO
from app.ui.models.property_table_model import PropertyTableModel

def test_property_table_model_row_count():
    model = PropertyTableModel([])
    assert model.rowCount() == 0

    props = [
        PropertyDTO(
            id=1, is_archived=False, category="مسکونی", listing_type="فروش",
            city="Tehran", municipal_district=1, address="Address", owner_phone="0912",
            area_sqm=100, sale_price=1000, rent_deposit=0, rent_monthly=0, date_registered="1405/01/01"
        ),
        PropertyDTO(
            id=2, is_archived=True, category="تجاری", listing_type="رهن",
            city="Tehran", municipal_district=2, address="Address 2", owner_phone="0913",
            area_sqm=80, sale_price=0, rent_deposit=100, rent_monthly=10, date_registered="1405/01/02"
        )
    ]
    model.update_data(props)
    assert model.rowCount() == 2

def test_property_table_model_data():
    prop = PropertyDTO(
        id=1, is_archived=True, category="مسکونی", listing_type="فروش",
        city="Tehran", municipal_district=1, address="Address", owner_phone="0912",
        area_sqm=100, sale_price=1000, rent_deposit=0, rent_monthly=0, date_registered="1405/01/01"
    )
    model = PropertyTableModel([prop])
    
    idx = model.index(0, 0) # ID
    assert model.data(idx, Qt.ItemDataRole.DisplayRole) == "1"
    
    idx_status = model.index(0, 1) # Status
    assert model.data(idx_status, Qt.ItemDataRole.DisplayRole) == "آرشیو شده"
