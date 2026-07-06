import pytest
import os
import sys

# Modify path to allow imports from bridge package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from re_bridge.exceptions import check_error, ValidationError, NotFoundError, InternalError
from re_bridge.loader import load_dll

def test_error_mapping():
    with pytest.raises(ValidationError):
        check_error(-1)
    
    with pytest.raises(NotFoundError):
        check_error(-2)
        
    # Check OK
    check_error(0) # Should not raise

def test_missing_dll_raises_internal_error():
    # If the DLL doesn't exist, it should raise InternalError smoothly, not crash
    try:
        load_dll()
    except InternalError as e:
        assert "DLL not found" in str(e) or "Failed to load" in str(e)
