import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'bridge')))
from re_bridge.models import SearchState, PaginationDTO, SortingDTO

def test_search_state_initialization():
    state = SearchState()
    assert state.query == ""
    assert state.filters == {}
    assert state.pagination.page_number == 1
    assert state.pagination.page_size == 20
    assert state.sorting.column == "date_registered"
    assert state.sorting.ascending is False

def test_search_state_to_dict():
    state = SearchState(
        query="test query",
        filters={"category": "مسکونی"},
        pagination=PaginationDTO(page_number=2, page_size=50),
        sorting=SortingDTO(column="sale_price", ascending=True)
    )
    
    d = state.to_dict()
    assert d["query"] == "test query"
    assert d["filters"]["category"] == "مسکونی"
    assert d["pagination"]["page_number"] == 2
    assert d["pagination"]["page_size"] == 50
    assert d["sorting"]["column"] == "sale_price"
    assert d["sorting"]["ascending"] is True
