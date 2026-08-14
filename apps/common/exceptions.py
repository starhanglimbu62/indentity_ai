class InvalidStateTransition(Exception):
    """Raised when a domain state transition is invalid."""
    pass


class OwnershipError(Exception):
    """Raised when an operation is attempted on an object the user does not own."""
    pass


class SensitiveDataAccessError(Exception):
    """Raised when an accessor attempts to retrieve sensitive data without permission."""
    pass
