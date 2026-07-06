"""
exceptions.py
Real Estate Management System
"""

class REException(Exception):
    """Base exception for all RE Bridge errors"""
    pass

class ValidationError(REException): pass
class NotFoundError(REException): pass
class DuplicateError(REException): pass
class AuthenticationError(REException): pass
class LockedError(REException): pass
class ForbiddenError(REException): pass
class DatabaseError(REException): pass
class BusyError(REException): pass
class CorruptError(REException): pass
class MemoryError(REException): pass
class InternalError(REException): pass

def check_error(code: int) -> None:
    if code == 0:
        return
    elif code == -1:
        raise ValidationError("Invalid input data.")
    elif code == -2:
        raise NotFoundError("Record not found.")
    elif code == -3:
        raise DuplicateError("Duplicate record exists.")
    elif code == -4:
        raise AuthenticationError("Authentication failed.")
    elif code == -5:
        raise LockedError("Account is locked.")
    elif code == -6:
        raise ForbiddenError("Access forbidden.")
    elif code == -7:
        raise DatabaseError("Database error occurred.")
    elif code == -10:
        raise BusyError("Database is busy.")
    elif code == -11:
        raise CorruptError("Database is corrupt.")
    elif code == -98:
        raise MemoryError("Out of memory in DLL.")
    else:
        raise InternalError(f"Internal error occurred: {code}")
