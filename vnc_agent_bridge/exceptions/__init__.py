"""Exception classes for VNC Agent Bridge.

This module defines the exception hierarchy used throughout the VNC Agent
Bridge library. All exceptions inherit from VNCException, allowing users to
catch all VNC-related errors with a single exception handler.

Exception Hierarchy:
    VNCException (base)
    ├── VNCConnectionError: Connection-related failures
    ├── VNCTimeoutError: Operation timeouts
    ├── VNCInputError: Invalid input validation
    ├── VNCStateError: Invalid operation state
    └── VNCProtocolError: VNC protocol violations

Usage Examples:
    Catch all VNC errors:
        try:
            vnc.connect()
        except VNCException as e:
            print(f"VNC error: {e}")

    Catch specific error types:
        try:
            vnc.mouse.left_click(-1, 100)
        except VNCInputError as e:
            print(f"Invalid input: {e}")

    Handle connection errors specifically:
        try:
            vnc.connect()
        except VNCConnectionError as e:
            print(f"Connection failed: {e}")
        except VNCTimeoutError as e:
            print(f"Connection timed out: {e}")
"""


class VNCException(Exception):
    """Base exception for all VNC errors.

    All VNC Agent Bridge exceptions inherit from this class, allowing
    consumers to catch all VNC-related errors with a single handler.
    """

    pass


class VNCConnectionError(VNCException):
    """Raised when connection to VNC server fails.

    This exception indicates that the bridge failed to establish or
    maintain a connection to the VNC server. Common causes include:
        - Invalid host or port
        - Network unreachable
        - Connection refused
        - Authentication failure
    """

    pass


class VNCAuthenticationError(VNCConnectionError):
    """Raised when VNC authentication fails.

    This exception indicates that the authentication attempt to the VNC
    server failed. Common causes include:
        - Invalid or missing password
        - Unsupported authentication method
        - Authentication timeout
    """

    pass


class VNCTimeoutError(VNCException):
    """Raised when an operation times out.

    This exception indicates that an operation did not complete within
    the specified timeout period. Common causes include:
        - Network latency
        - Server unresponsive
        - Long-running operation
    """

    pass


class VNCInputError(VNCException):
    """Raised when invalid input is provided.

    This exception indicates that the input validation failed. Common causes:
        - Negative or out-of-bounds coordinates
        - Unknown key name
        - Invalid scroll amount
        - Unsupported characters for typing
    """

    pass


class VNCStateError(VNCException):
    """Raised when operation attempted in invalid state.

    This exception indicates that the operation cannot be performed in the
    current state. Common causes:
        - Operation attempted before connecting
        - Multiple connect attempts
        - Operation attempted after disconnect
    """

    pass


class VNCProtocolError(VNCException):
    """Raised on VNC protocol violation.

    This exception indicates that the VNC server sent an unexpected or
    invalid protocol message. This typically indicates a protocol
    incompatibility or server bug.
    """

    pass


__all__ = [
    "VNCException",
    "VNCConnectionError",
    "VNCAuthenticationError",
    "VNCTimeoutError",
    "VNCInputError",
    "VNCStateError",
    "VNCProtocolError",
]
