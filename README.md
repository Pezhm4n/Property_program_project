# Real Estate Management System

## Project Overview
A professional, secure, and offline desktop application for managing real estate agencies. 
It replaces the legacy text-based C coursework with a modern architecture while preserving the core C logic.

## Architecture Summary
- **Core Layer (C17):** Shared library (`re_core.dll`) managing all business rules, auth, and database interactions securely.
- **Database (SQLite):** WAL mode, JSON-based DTO exchange.
- **Bridge Layer (Python ctypes):** Connects the UI securely to the C Core with structured error handling.
- **App Layer (PySide6):** Modern desktop UI.

## Repository Structure
- `app/`: PySide6 Desktop Application
- `bridge/`: Python ctypes wrapper
- `core/`: Business Logic and Database Layer (C DLL)
- `docs/`: Architecture Decision Records and Specifications
- `scripts/`: Build and utility scripts

## Build Prerequisites
- MSVC 2022 / GCC 13+ / Clang 17+
- CMake 3.20+
- Python 3.11+

## Quick Start
1. Create a virtual environment: `python -m venv venv`
2. Install requirements: `pip install -r requirements.txt`
3. Build the core DLL: `cd core && mkdir build && cd build && cmake .. && cmake --build . --config Release`
4. Run the app: `python app/main.py`

## License
[Placeholder License]
