"""
pytest fixtures for VNC Agent Bridge testing.

Provides mock connections and pre-configured controller instances
for use across all test modules.
"""

from unittest.mock import Mock
import pytest

from vnc_agent_bridge.core.connection import VNCConnection
from vnc_agent_bridge.core.mouse import MouseController
from vnc_agent_bridge.core.keyboard import KeyboardController
from vnc_agent_bridge.core.scroll import ScrollController
from vnc_agent_bridge.core.bridge import VNCAgentBridge


@pytest.fixture
def mock_vnc_connection() -> Mock:
    """
    Mock VNCConnection for testing controllers.

    Returns:
        Mock: Configured mock connection object with common attributes/methods.
    """
    connection = Mock(spec=VNCConnection)
    connection.is_connected = True
    connection.send_pointer_event = Mock()
    connection.send_key_event = Mock()
    connection.connect = Mock()
    connection.disconnect = Mock()
    return connection


@pytest.fixture
def mouse_controller(mock_vnc_connection: Mock) -> MouseController:
    """
    MouseController instance with mock connection.

    Args:
        mock_vnc_connection: Mock VNCConnection fixture.

    Returns:
        MouseController: Initialized controller for testing.
    """
    return MouseController(mock_vnc_connection)


@pytest.fixture
def keyboard_controller(mock_vnc_connection: Mock) -> KeyboardController:
    """
    KeyboardController instance with mock connection.

    Args:
        mock_vnc_connection: Mock VNCConnection fixture.

    Returns:
        KeyboardController: Initialized controller for testing.
    """
    return KeyboardController(mock_vnc_connection)


@pytest.fixture
def scroll_controller(mock_vnc_connection: Mock) -> ScrollController:
    """
    ScrollController instance with mock connection.

    Args:
        mock_vnc_connection: Mock VNCConnection fixture.

    Returns:
        ScrollController: Initialized controller for testing.
    """
    return ScrollController(mock_vnc_connection)


@pytest.fixture
def vnc_bridge_connected(mock_vnc_connection: Mock) -> VNCAgentBridge:
    """
    VNCAgentBridge instance with mock connection already connected.

    Args:
        mock_vnc_connection: Mock VNCConnection fixture.

    Returns:
        VNCAgentBridge: Initialized and "connected" bridge for testing.
    """
    # Create bridge with mock connection
    bridge = VNCAgentBridge("localhost", port=5900)
    bridge._connection = mock_vnc_connection
    mock_vnc_connection.is_connected = True
    return bridge


@pytest.fixture
def vnc_bridge_disconnected() -> VNCAgentBridge:
    """
    VNCAgentBridge instance with mock connection (not connected).

    Returns:
        VNCAgentBridge: Initialized but "disconnected" bridge for testing.
    """
    bridge = VNCAgentBridge("localhost", port=5900)
    bridge._connection = Mock(spec=VNCConnection)
    bridge._connection.is_connected = False
    return bridge
