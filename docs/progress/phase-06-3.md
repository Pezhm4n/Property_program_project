# Release Note: Phase 6.3 (Search, Filtering & Sorting)
**Progress:** 90%
**Capabilities Added:**
- Universal `SearchState` DTO (Query, Filters, Sorting, Pagination).
- Quick Search UI integrated directly into Property Management.
- Advanced Filter Dialog handling property fields (Category, Area, Price, City, District) entirely statelessly.
- Server-side sorting orchestration via C DLL (`SortingDTO` mapping to header clicks).
- Server-side pagination mapping to UI Toolbar controls (Prev/Next/Size).
- Legacy files `advanced_search.py`, `search_engine.py`, and `filter_models.py` audited and scheduled for deletion in Phase 6.5.
**Key Files Changed:**
- `app/ui/views/property_list_view.py`
- `app/ui/dialogs/filter_dialog.py`
- `bridge/re_bridge/models.py`
- `app/tests/test_ui_search.py`
**Architecture Notes:**
All search states are fully stateless in the UI and sent to the Bridge. No data is filtered directly inside `QAbstractTableModel`.
