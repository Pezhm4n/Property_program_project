"""
loader.py
Real Estate Management System
"""
import ctypes
import os
import sys
from typing import Tuple
from .exceptions import InternalError

# Expected API version matching re_core.h
EXPECTED_API_VERSION = 200

def _get_dll_path() -> str:
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if sys.platform == 'win32':
        return os.path.join(base_dir, 'core', 'build', 're_core.dll')
    elif sys.platform == 'darwin':
        return os.path.join(base_dir, 'core', 'build', 'libre_core.dylib')
    else:
        return os.path.join(base_dir, 'core', 'build', 'libre_core.so')

def load_dll() -> ctypes.CDLL:
    dll_path = _get_dll_path()
    if not os.path.exists(dll_path):
        raise InternalError(f"DLL not found at {dll_path}. Please build the core project first.")
    
    if sys.platform == 'win32' and hasattr(os, 'add_dll_directory'):
        dll_dir = os.path.dirname(dll_path)
        if os.path.exists(dll_dir):
            try:
                os.add_dll_directory(dll_dir)
            except Exception:
                pass
                
        # Add MSYS2 bin for dependencies during development (skip in packaged builds)
        if not getattr(sys, 'frozen', False):
            mingw_bin = "C:\\msys64\\mingw64\\bin"
            if os.path.exists(mingw_bin):
                try:
                    os.add_dll_directory(mingw_bin)
                except Exception:
                    pass
                
    try:
        dll = ctypes.CDLL(dll_path)
    except Exception as e:
        raise InternalError(f"Failed to load DLL: {e}")
        
    # Bind strictly typed signatures
    dll.re_get_api_version.argtypes = []
    dll.re_get_api_version.restype = ctypes.c_int
    
    dll.re_get_dll_version.argtypes = []
    dll.re_get_dll_version.restype = ctypes.c_int
    
    dll.re_get_last_error.argtypes = []
    dll.re_get_last_error.restype = ctypes.c_int
    
    dll.re_free_string.argtypes = [ctypes.c_void_p]
    dll.re_free_string.restype = None

    dll.re_initialize.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
    dll.re_initialize.restype = ctypes.c_int

    dll.re_shutdown.argtypes = []
    dll.re_shutdown.restype = None
    # Core Data & Auth Endpoints
    endpoints = [
        're_login', 're_logout', 're_validate_session',
        're_create_property', 're_update_property', 're_get_properties', 
        're_get_property', 're_archive_property', 're_restore_property',
        're_get_report', 're_get_statistics', 're_get_dashboard', 're_ping',
        're_has_any_user', 're_create_initial_admin', 're_change_password',
        # User Management (RBAC)
        're_get_users', 're_create_user', 're_change_user_role',
        're_reset_user_password', 're_toggle_user_status',
        # Hardening
        're_log_audit'
    ]

    for ep in endpoints:
        func = getattr(dll, ep)
        func.argtypes = [ctypes.c_char_p, ctypes.POINTER(ctypes.c_char_p)]
        func.restype = ctypes.c_int

    # Enforce Version Checking safely
    try:
        api_version = dll.re_get_api_version()
    except Exception as e:
        raise InternalError("Could not retrieve API version from DLL.", -99, str(e))
        
    if api_version != EXPECTED_API_VERSION:
        raise InternalError(
            f"The core DLL version ({api_version}) is incompatible with this Python Application ({EXPECTED_API_VERSION}). "
            f"Please update your software or rebuild the core project."
        )

    return dll

_dll_instance = None

def get_dll() -> ctypes.CDLL:
    global _dll_instance
    if _dll_instance is None:
        _dll_instance = load_dll()
    return _dll_instance

def call_dll_endpoint(endpoint_name: str, request_json: str) -> Tuple[int, str]:
    dll = get_dll()
    func = getattr(dll, endpoint_name)
    
    req_bytes = request_json.encode('utf-8')
    res_ptr = ctypes.c_char_p()
    
    # Execute DLL endpoint
    rc = func(req_bytes, ctypes.byref(res_ptr))
    
    res_str = ""
    if res_ptr.value:
        try:
            res_str = res_ptr.value.decode('utf-8')
        finally:
            # IMPORTANT: Release memory owned by DLL unconditionally
            dll.re_free_string(res_ptr)
            
    return rc, res_str
