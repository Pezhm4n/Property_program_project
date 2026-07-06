# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]
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
