# VNC Agent Bridge
# Open-source Python package for AI agents to interact with VNC servers

__version__ = "0.1.0"

# Import main classes and exceptions
from .core.bridge import VNCAgentBridge
from .exceptions import (
    VNCException,
    VNCConnectionError,
    VNCTimeoutError,
    VNCInputError,
    VNCStateError,
    VNCProtocolError,
)

__all__ = [
    "VNCAgentBridge",
    "VNCException",
    "VNCConnectionError",
    "VNCTimeoutError",
    "VNCInputError",
    "VNCStateError",
    "VNCProtocolError",
]
