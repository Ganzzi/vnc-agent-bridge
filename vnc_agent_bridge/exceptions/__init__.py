# Exception classes for VNC Agent Bridge


class VNCException(Exception):
    """Base exception for all VNC errors."""

    pass


class VNCConnectionError(VNCException):
    """Raised when connection fails."""

    pass


class VNCTimeoutError(VNCException):
    """Raised when operation times out."""

    pass


class VNCInputError(VNCException):
    """Raised when invalid input provided."""

    pass


class VNCStateError(VNCException):
    """Raised when operation in invalid state."""

    pass


class VNCProtocolError(VNCException):
    """Raised on VNC protocol violation."""

    pass


__all__ = [
    "VNCException",
    "VNCConnectionError",
    "VNCTimeoutError",
    "VNCInputError",
    "VNCStateError",
    "VNCProtocolError",
]
