# Changelog

All notable changes to this project will be documented in this file.
## [Unreleased]
### Added (Phase 12 - Quality Audit & Hardening)
- Implemented C Core input string bounds checking to mitigate buffer overflow risks on login, registration, and listing fields.
- Implemented C Core password memory scrubbing using `memset` immediately after authentication.
- Created secondary database index migration (`0003_add_search_indices.sql`) to optimize search queries and eliminate full table scans.
- Added validation and sanitization checks for all loaded preferences (page size, theme, session timeout) in `SessionManager`.
- Added pre-restore validation running SQLite `PRAGMA integrity_check` on backup files to prevent corruption propagation.
- Verified index usage using SQLite `EXPLAIN QUERY PLAN`.
- Added unit tests for backup corruption handling.

### Added (Phase 11 - Technical Debt Cleanup & Production Hardening)
- Refactored DB path resolution to follow prioritization chain: environment variable -> settings.json -> fallback.
- Removed chart mock data and added dynamic localized empty states.
- Implemented user setup wizard check (`re_has_any_user` & `re_create_initial_admin`) to prevent default admin hardcoding.
- Implemented password update validation (`re_change_password`) and settings page integration.
- Implemented global inactivity event filter on QApplication initiating automated logout session timeouts.

### Added (Phase 10 - UI/UX Polish & User Experience)
- Implemented responsive QSS design tokens for custom fonts, borders (8px/12px/16px), scrollbars, and focus rings.
- Redesigned Login Page as a sleek centered card layout with inline validation alerts and form focus glows.
- Enhanced MainWindow sidebar styling and dynamic toolbar action visibility mapped per tab.
- Integrated runtime dark/light theme switching with persistence in settings.json.
- Redesigned QPainter dashboard charts to draw smooth cubic Bezier splines and translucent gradient fills.
- Updated Property list table to support context menu operations (Edit, Archive/Restore) and double-click row triggers.
- Enforced Right-to-Left (RTL) layout direction across all modal dialogs and alert boxes.

### Added (Phase 8 - Architecture Validation & Core Completion)
- Completed stateless C DLL database prepare statements and services mapping.
- Integrated Argon2 security hashing lockout times and failed login attempts.
- Added dynamic admin seeding checks in C core to check if admin user exists before seeding.
- Moved automated gate review verification suite to scripts/ folder with execution timers and file validation.

### Added (Phase 7 - Business Rules, Reports, Export & Polish)
- Implemented real-time dynamic Dashboard aggregating metrics directly from database.
- Integrated PDF (reportlab) and Excel (xlsxwriter) exports inside ReportsPage.
- Implemented database Backup and Restore services.
- Migrated legacy BR-001 commission calculations (residential and commercial) to service layer.
- Added full integration test suite verifying backup, restore, and commission logic.

### Added (Phase 6.5 - Legacy Audit & Migration)
- Detailed audit and mapping (`docs/legacy_audit.md`) covering all 32 legacy files.
- Documented core business rules, validation criteria, and key algorithms.
- Prioritized migration plan for C and Python business modules.

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
