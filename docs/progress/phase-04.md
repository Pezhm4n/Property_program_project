# Release Note: Phase 4 (Python Bridge ctypes)
**Progress:** 60%
**Capabilities Added:**
- ctypes DLL Loader with Lazy Loading
- API Version checking and strict Signature Binding
- Safe Memory Release (re_free_string) in try-finally blocks
- Python Data Models (dataclasses) and Service Facades
- Python Exception Mapping from C error codes
**Key Files Changed:**
- `bridge/re_bridge/exceptions.py`, `loader.py`, `models.py`, `services.py`
**New ADRs:**
- Decided to map all DLL interactions purely through JSON for flexibility, avoiding complex nested C-Structs in ctypes.
- `CHANGELOG.md` integrated for historical tracking.
**Technical Debt:** Legacy UI/Bridge folders from semester 1 still exist in root, blocking pure pytest execution at root level.
**Risks:** DLL loading relies on specific directory structures (`core/build/...`).
**Tests & CI:** Unit tests created. Pytest functional when run directly on test files.
