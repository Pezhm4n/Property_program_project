"""
exceptions.py
Real Estate Management System
"""

class REException(Exception):
    """Base exception for all RE Bridge errors"""
    def __init__(self, message: str, code: int = -99, details: str = ""):
        self.message = message
        self.code = code
        self.details = details
        super().__init__(f"[{code}] {message} - {details}" if details else f"[{code}] {message}")

class ValidationError(REException): pass
class NotFoundError(REException): pass
class DuplicateError(REException): pass
class AuthenticationError(REException): pass
class LockedError(REException): pass
class ForbiddenError(REException): pass
class DatabaseError(REException): pass
class SessionExpiredError(REException): pass
class BusyError(REException): pass
class CorruptError(REException): pass
class LastAdminError(REException): pass
class MemoryError(REException): pass
class InternalError(REException): pass
class NotImplementedError(REException): pass

def check_error(code: int, details: str = "") -> None:
    if code == 0:
        return
    elif code == -1:
        raise ValidationError("Invalid input data.", code, details)
    elif code == -2:
        raise NotFoundError("Record not found.", code, details)
    elif code == -3:
        raise DuplicateError("Duplicate record exists.", code, details)
    elif code == -4:
        raise AuthenticationError("Authentication failed.", code, details)
    elif code == -5:
        raise LockedError("Account is locked.", code, details)
    elif code == -6:
        raise ForbiddenError("Access forbidden.", code, details)
    elif code == -7:
        raise DatabaseError("Database error occurred.", code, details)
    elif code == -8:
        raise SessionExpiredError("Session has expired.", code, details)
    elif code == -10:
        raise BusyError("Database is busy.", code, details)
    elif code == -11:
        raise CorruptError("Database is corrupt.", code, details)
    elif code == -12:
        raise LastAdminError("Cannot modify the last admin account.", code, details)
    elif code == -98:
        raise MemoryError("Out of memory in DLL.", code, details)
    elif code == -100:
        raise NotImplementedError("This API endpoint is not yet implemented in the core DLL.", code, details)
    else:
        raise InternalError("Internal error occurred.", code, details)
