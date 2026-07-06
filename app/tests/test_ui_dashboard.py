import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'bridge')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from PySide6.QtWidgets import QApplication
from app.ui.widgets.statistics_card import StatisticsCard
from app.ui.widgets.recent_activity import RecentActivityWidget
from app.ui.widgets.empty_state import EmptyStateWidget
from re_bridge.models import SearchState

# Re-use QApplication if already initialized by pytest-qt or create a test fixture
@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance()
    if not app:
        app = QApplication([])
    return app

def test_statistics_card_initialization(qapp):
    card = StatisticsCard("Test Title", "10", "⭐", "Test Description")
    assert card.lbl_title.text() == "Test Title"
    assert card.lbl_value.text() == "10"
    assert card.lbl_icon.text() == "⭐"
    assert card.lbl_desc.text() == "Test Description"

def test_statistics_card_update(qapp):
    card = StatisticsCard("Test Title", "10", "⭐", "Test Description")
    card.update_value("20")
    assert card.lbl_value.text() == "20"

def test_recent_activity_widget_empty(qapp):
    widget = RecentActivityWidget()
    widget.update_activities([])
    assert widget.list_widget.count() == 1
    assert "هیچ فعالیتی ثبت نشده است." in widget.list_widget.item(0).text()

def test_recent_activity_widget_populated(qapp):
    widget = RecentActivityWidget()
    widget.update_activities([
        {"timestamp": "12:00", "user": "admin", "action": "تست", "details": "جزئیات"}
    ])
    assert widget.list_widget.count() == 1
    assert "admin: تست (جزئیات)" in widget.list_widget.item(0).text()

def test_empty_state_widget(qapp):
    widget = EmptyStateWidget("پیام تستی", "راهنما تستی")
    assert widget.lbl_message.text() == "پیام تستی"
    assert widget.lbl_hint.text() == "راهنما تستی"
