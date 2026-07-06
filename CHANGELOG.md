# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]
### Added (Phase 6.4 - Dashboard & Reporting UI)
- Fully functional `DashboardPage` and `ReportsPage` connected statelessly to Bridge.
- StatisticsCard, RecentActivity, and QPainter-based Chart skeleton widgets.
- EmptyStateWidget to display clean placeholder messages for empty table views.
- Serializing and restoring capability (`from_dict` / `to_dict`) on `SearchState`.

### Added (Phase 6.3 - Search, Filtering & Sorting)
- `SearchState` DTO representing Query, Filters, Sorting, and Pagination.
- Stateless Search Toolbar and Advanced Filter Dialog.
- Server-side sorting triggers via `QTableView` header clicks.

### Added (Phase 6.2 - Property Management UI)
- API Freeze in C core defining complete v1.0 bindings with `RE_ERR_NOT_IMPLEMENTED`.
- `PropertyTableModel` leveraging Qt Model/View paradigm.
- Property CRUD Interface connecting Python `PropertyDTO` to Bridge (without direct UI validation).
- Interface-driven `SessionManager` storage abstractions.

### Added (Phase 6.1 - Authentication UI)
- Fully functional Login UI connected via Bridge to `AuthService`.
- Checkboxes for Remember Me (JSON Storage) and Show/Hide Password.
### Added (Phase 5 - UI Foundation)
- PySide6 Application bootstrap with dynamic QSS theming (Light/Dark).
- Standardized MessageBox for translating Bridge Exceptions cleanly to the user.
- Base UI managers for Font, Navigation, and Themes.

### Added (Phase 4 - Python Bridge)
- `ctypes` bindings establishing Python to C integration.
- `loader.py` implementing robust memory deallocation (`re_free_string`) via try-finally blocks.
- Unified Exception mapping (`exceptions.py`) converting C errors to Python domain errors.
- Service wrappers for passing pure JSON configurations to the DLL.
- Strict API version matching (`re_get_api_version()`) preventing incompatible loads.

### Added (Phase 3 - Core Business Logic)
- C ABI Facade in `exports.c` preventing raw DB logic exposure.
- Skeleton implementation for Service layers (`auth_service`, `property_service`).
- Architecture prepared for `cJSON` parsing.
- Audit Log enforcement across all write actions.
- Transaction control boundaries inside C domain services.

### Added (Phase 2 - Database Layer)
- Atomic SQLite Migrations engine relying on `migration_manifest.h`.
- Database connection lifecycle management and repository interfaces enforcing Prepared Statements.
- CMake configured to compile without SQLite if omitted, relying on standard Warning fallbacks for Offline Mode.

### Added (Phase 1 - Initialization)
- Complete directory structure based on Architecture Phase.
- Base CI pipeline on GitHub Actions spanning Ubuntu & Windows.
- `CMakeLists.txt` configured with strict compiler flags (`C17`, `-Werror`).
