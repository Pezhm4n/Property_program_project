# Release Note: Phase 3 (Core Business Logic)
**Progress:** 45%
**Capabilities Added:**
- Core Business Logic Services (Auth, Property, Report)
- Transaction Boundaries & Audit Logging
- C ABI DLL Exports Facade
- DTO Validation & JSON Parsing skeletons
**Key Files Changed:**
- `core/src/api/exports.c`, `auth_service.c`, `re_core.h`, `json_parser.c`
**New ADRs:**
- Decided to use `cJSON` exclusively for parsing to prevent manual string manipulation risks.
**Technical Debt:** Business logic currently relies on skeletons returning `-99`.
**Risks:** JSON parsing requires `cJSON` dependency to be added manually by developer.
**Tests & CI:** CI handles missing cJSON safely with warnings.
