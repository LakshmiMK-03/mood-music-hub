class AppError(Exception):
    """Base class for all application errors."""
    def __init__(self, message, status_code=500, payload=None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['error'] = self.message
        rv['success'] = False
        return rv

class ValidationError(AppError):
    """Raised when user input is invalid."""
    def __init__(self, message, payload=None):
        super().__init__(message, status_code=400, payload=payload)

class AuthError(AppError):
    """Raised during authentication failures."""
    def __init__(self, message, payload=None):
        super().__init__(message, status_code=401, payload=payload)

class DatabaseError(AppError):
    """Raised for database operation failures."""
    def __init__(self, message, payload=None):
        super().__init__(message, status_code=500, payload=payload)

class ExternalAPIError(AppError):
    """Raised when an external service (YouTube, HF, etc.) fails."""
    def __init__(self, service_name, message, payload=None):
        msg = f"{service_name} error: {message}"
        super().__init__(msg, status_code=502, payload=payload)
