"""
Unit tests for FramebufferManager.

Tests framebuffer initialization, updates, and buffer operations.
"""

from unittest.mock import Mock
import pytest
import numpy as np

from vnc_agent_bridge.core.framebuffer import FramebufferManager
from vnc_agent_bridge.core.connection_tcp import TCPVNCConnection
from vnc_agent_bridge.types.common import FramebufferConfig


class TestFramebufferManagerInitialization:
    """Tests for FramebufferManager initialization."""

    def test_init_basic(self) -> None:
        """Test basic initialization."""
        mock_conn = Mock(spec=TCPVNCConnection)
        config = FramebufferConfig(
            width=800, height=600, pixel_format=b"RGBA", name="test"
        )

        fb = FramebufferManager(mock_conn, config)

        assert fb.connection is mock_conn
        assert fb.config is config
        assert fb._buffer is None
        assert fb._is_dirty is False

    def test_init_with_different_dimensions(self) -> None:
        """Test initialization with various dimensions."""
        mock_conn = Mock(spec=TCPVNCConnection)

        for width, height in [(640, 480), (1024, 768), (1920, 1080), (3840, 2160)]:
            config = FramebufferConfig(
                width=width, height=height, pixel_format=b"RGBA", name="test"
            )
            fb = FramebufferManager(mock_conn, config)
            assert fb.config.width == width
            assert fb.config.height == height


class TestFramebufferBufferInitialization:
    """Tests for buffer initialization."""

    def test_initialize_buffer(self) -> None:
        """Test buffer initialization creates correct RGBA array."""
        mock_conn = Mock(spec=TCPVNCConnection)
        config = FramebufferConfig(
            width=800, height=600, pixel_format=b"RGBA", name="test"
        )
        fb = FramebufferManager(mock_conn, config)

        fb.initialize_buffer()

        assert fb._buffer is not None
        assert isinstance(fb._buffer, np.ndarray)
        assert fb._buffer.shape == (600, 800, 4)  # (height, width, 4 for RGBA)
        assert fb._buffer.dtype == np.uint8
        assert fb._is_dirty is False

    def test_initialize_buffer_zeros(self) -> None:
        """Test that buffer is initialized with zeros (black)."""
        mock_conn = Mock(spec=TCPVNCConnection)
        config = FramebufferConfig(
            width=100, height=100, pixel_format=b"RGBA", name="test"
        )
        fb = FramebufferManager(mock_conn, config)

        fb.initialize_buffer()

        # All pixels should be zero (black, fully transparent)
        assert np.all(fb._buffer == 0)

    def test_initialize_buffer_multiple_times(self) -> None:
        """Test that reinitializing buffer works correctly."""
        mock_conn = Mock(spec=TCPVNCConnection)
        config = FramebufferConfig(
            width=800, height=600, pixel_format=b"RGBA", name="test"
        )
        fb = FramebufferManager(mock_conn, config)

        fb.initialize_buffer()
        first_buffer = fb._buffer

        # Set some data
        fb._buffer[0, 0] = [255, 128, 64, 255]

        # Reinitialize
        fb.initialize_buffer()

        # Should be fresh zeros
        assert np.all(fb._buffer == 0)
        assert fb._buffer is not first_buffer or fb._buffer[0, 0, 0] == 0


class TestFramebufferProperties:
    """Tests for framebuffer properties."""

    def test_width_property(self) -> None:
        """Test width property returns correct value."""
        mock_conn = Mock(spec=TCPVNCConnection)
        config = FramebufferConfig(
            width=1920, height=1080, pixel_format=b"RGBA", name="test"
        )
        fb = FramebufferManager(mock_conn, config)

        assert fb.width == 1920

    def test_height_property(self) -> None:
        """Test height property returns correct value."""
        mock_conn = Mock(spec=TCPVNCConnection)
        config = FramebufferConfig(
            width=1920, height=1080, pixel_format=b"RGBA", name="test"
        )
        fb = FramebufferManager(mock_conn, config)

        assert fb.height == 1080

    def test_is_dirty_property(self) -> None:
        """Test is_dirty property returns correct value."""
        mock_conn = Mock(spec=TCPVNCConnection)
        config = FramebufferConfig(
            width=800, height=600, pixel_format=b"RGBA", name="test"
        )
        fb = FramebufferManager(mock_conn, config)

        assert fb.is_dirty is False

        fb._is_dirty = True
        assert fb.is_dirty is True


class TestFramebufferGetBuffer:
    """Tests for get_buffer method."""

    def test_get_buffer_before_init(self) -> None:
        """Test get_buffer before initialization raises error."""
        mock_conn = Mock(spec=TCPVNCConnection)
        config = FramebufferConfig(
            width=800, height=600, pixel_format=b"RGBA", name="test"
        )
        fb = FramebufferManager(mock_conn, config)

        with pytest.raises(RuntimeError):
            fb.get_buffer()

    def test_get_buffer_after_init(self) -> None:
        """Test get_buffer after initialization returns array."""
        mock_conn = Mock(spec=TCPVNCConnection)
        config = FramebufferConfig(
            width=800, height=600, pixel_format=b"RGBA", name="test"
        )
        fb = FramebufferManager(mock_conn, config)
        fb.initialize_buffer()

        result = fb.get_buffer()

        assert result is not None
        assert isinstance(result, np.ndarray)
        assert result.shape == (600, 800, 4)

    def test_get_buffer_returns_same_object(self) -> None:
        """Test get_buffer returns copy on multiple calls."""
        mock_conn = Mock(spec=TCPVNCConnection)
        config = FramebufferConfig(
            width=800, height=600, pixel_format=b"RGBA", name="test"
        )
        fb = FramebufferManager(mock_conn, config)
        fb.initialize_buffer()

        buffer1 = fb.get_buffer()
        buffer2 = fb.get_buffer()

        # Should be different objects (copies)
        assert buffer1 is not buffer2
        # But with same data
        assert np.array_equal(buffer1, buffer2)


class TestFramebufferGetRegion:
    """Tests for get_region method."""

    def test_get_region_full_screen(self) -> None:
        """Test getting full screen region."""
        mock_conn = Mock(spec=TCPVNCConnection)
        config = FramebufferConfig(
            width=800, height=600, pixel_format=b"RGBA", name="test"
        )
        fb = FramebufferManager(mock_conn, config)
        fb.initialize_buffer()

        region = fb.get_region(0, 0, 800, 600)

        assert isinstance(region, np.ndarray)
        assert region.shape == (600, 800, 4)

    def test_get_region_partial(self) -> None:
        """Test getting partial screen region."""
        mock_conn = Mock(spec=TCPVNCConnection)
        config = FramebufferConfig(
            width=800, height=600, pixel_format=b"RGBA", name="test"
        )
        fb = FramebufferManager(mock_conn, config)
        fb.initialize_buffer()

        # Get top-left 100x100 region
        region = fb.get_region(0, 0, 100, 100)

        assert region.shape == (100, 100, 4)

    def test_get_region_with_offset(self) -> None:
        """Test getting region with offset."""
        mock_conn = Mock(spec=TCPVNCConnection)
        config = FramebufferConfig(
            width=800, height=600, pixel_format=b"RGBA", name="test"
        )
        fb = FramebufferManager(mock_conn, config)
        fb.initialize_buffer()

        # Set a pixel to non-zero to verify correct region
        fb._buffer[100, 100] = [255, 128, 64, 255]

        # Get region containing that pixel
        region = fb.get_region(50, 50, 100, 100)

        # The pixel should be at (50, 50) in the region
        assert region.shape == (100, 100, 4)
        assert np.any(region != 0)  # Should have non-zero data

    def test_get_region_edge_cases(self) -> None:
        """Test get_region with edge case dimensions."""
        mock_conn = Mock(spec=TCPVNCConnection)
        config = FramebufferConfig(
            width=800, height=600, pixel_format=b"RGBA", name="test"
        )
        fb = FramebufferManager(mock_conn, config)
        fb.initialize_buffer()

        # Single pixel
        region = fb.get_region(0, 0, 1, 1)
        assert region.shape == (1, 1, 4)

        # Single row
        region = fb.get_region(0, 0, 800, 1)
        assert region.shape == (1, 800, 4)

        # Single column
        region = fb.get_region(0, 0, 1, 600)
        assert region.shape == (600, 1, 4)


class TestFramebufferUpdateRectangle:
    """Tests for update_rectangle method."""

    def test_update_rectangle_basic(self) -> None:
        """Test updating a rectangle in framebuffer."""
        mock_conn = Mock(spec=TCPVNCConnection)
        config = FramebufferConfig(
            width=800, height=600, pixel_format=b"RGBA", name="test"
        )
        fb = FramebufferManager(mock_conn, config)
        fb.initialize_buffer()

        # Create pixel data for 10x10 region
        pixel_data = np.ones((10, 10, 4), dtype=np.uint8) * 255
        pixel_bytes = pixel_data.tobytes()

        fb.update_rectangle(0, 0, 10, 10, pixel_bytes)

        # Verify region was updated
        region = fb.get_region(0, 0, 10, 10)
        assert np.all(region == 255)

    def test_update_rectangle_sets_dirty(self) -> None:
        """Test that process_update sets dirty flag."""
        mock_conn = Mock(spec=TCPVNCConnection)
        config = FramebufferConfig(
            width=800, height=600, pixel_format=b"RGBA", name="test"
        )
        fb = FramebufferManager(mock_conn, config)
        fb.initialize_buffer()

        pixel_data = np.ones((10, 10, 4), dtype=np.uint8) * 128
        pixel_bytes = pixel_data.tobytes()

        # process_update sets dirty flag, not update_rectangle
        fb.process_update([(0, 0, 10, 10, pixel_bytes)])

        assert fb.is_dirty is True

    def test_update_rectangle_multiple_regions(self) -> None:
        """Test updating multiple rectangles."""
        mock_conn = Mock(spec=TCPVNCConnection)
        config = FramebufferConfig(
            width=800, height=600, pixel_format=b"RGBA", name="test"
        )
        fb = FramebufferManager(mock_conn, config)
        fb.initialize_buffer()

        # Update top-left corner
        pixel_data1 = np.ones((50, 50, 4), dtype=np.uint8) * 100
        fb.update_rectangle(0, 0, 50, 50, pixel_data1.tobytes())

        # Update bottom-right corner
        pixel_data2 = np.ones((50, 50, 4), dtype=np.uint8) * 200
        fb.update_rectangle(750, 550, 50, 50, pixel_data2.tobytes())

        # Verify both regions
        region1 = fb.get_region(0, 0, 50, 50)
        region2 = fb.get_region(750, 550, 50, 50)

        assert np.all(region1 == 100)
        assert np.all(region2 == 200)


class TestFramebufferReset:
    """Tests for reset method."""

    def test_reset_clears_dirty_flag(self) -> None:
        """Test that reset clears dirty flag."""
        mock_conn = Mock(spec=TCPVNCConnection)
        config = FramebufferConfig(
            width=800, height=600, pixel_format=b"RGBA", name="test"
        )
        fb = FramebufferManager(mock_conn, config)
        fb.initialize_buffer()
        fb._is_dirty = True

        fb.reset()

        assert fb.is_dirty is False

    def test_reset_preserves_buffer(self) -> None:
        """Test that reset clears buffer."""
        mock_conn = Mock(spec=TCPVNCConnection)
        config = FramebufferConfig(
            width=800, height=600, pixel_format=b"RGBA", name="test"
        )
        fb = FramebufferManager(mock_conn, config)
        fb.initialize_buffer()

        # Set some data
        fb._buffer[0, 0] = [255, 128, 64, 255]

        fb.reset()

        # Buffer should be None after reset
        assert fb._buffer is None


class TestFramebufferRequestUpdate:
    """Tests for request_update method."""

    def test_request_update_default_params(self) -> None:
        """Test request_update with default parameters."""
        mock_conn = Mock(spec=TCPVNCConnection)
        mock_conn.request_framebuffer_update = Mock()

        config = FramebufferConfig(
            width=800, height=600, pixel_format=b"RGBA", name="test"
        )
        fb = FramebufferManager(mock_conn, config)

        fb.request_update()

        mock_conn.request_framebuffer_update.assert_called()

    def test_request_update_with_params(self) -> None:
        """Test request_update with specific parameters."""
        mock_conn = Mock(spec=TCPVNCConnection)
        mock_conn.request_framebuffer_update = Mock()

        config = FramebufferConfig(
            width=800, height=600, pixel_format=b"RGBA", name="test"
        )
        fb = FramebufferManager(mock_conn, config)

        fb.request_update(incremental=False, x=100, y=100, width=200, height=200)

        mock_conn.request_framebuffer_update.assert_called_once_with(
            incremental=False, x=100, y=100, width=200, height=200
        )


class TestFramebufferProcessUpdate:
    """Tests for process_update method."""

    def test_process_update_empty_list(self) -> None:
        """Test processing empty update list."""
        mock_conn = Mock(spec=TCPVNCConnection)
        config = FramebufferConfig(
            width=800, height=600, pixel_format=b"RGBA", name="test"
        )
        fb = FramebufferManager(mock_conn, config)
        fb.initialize_buffer()

        fb.process_update([])

        # Should complete without error
        assert fb._buffer is not None

    def test_process_update_single_rectangle(self) -> None:
        """Test processing single rectangle update."""
        mock_conn = Mock(spec=TCPVNCConnection)
        config = FramebufferConfig(
            width=800, height=600, pixel_format=b"RGBA", name="test"
        )
        fb = FramebufferManager(mock_conn, config)
        fb.initialize_buffer()

        # Create rectangle data
        pixel_data = np.ones((100, 100, 4), dtype=np.uint8) * 200
        rectangles = [(0, 0, 100, 100, pixel_data.tobytes())]

        fb.process_update(rectangles)

        # Verify update was applied
        region = fb.get_region(0, 0, 100, 100)
        assert np.all(region == 200)

    def test_process_update_multiple_rectangles(self) -> None:
        """Test processing multiple rectangles."""
        mock_conn = Mock(spec=TCPVNCConnection)
        config = FramebufferConfig(
            width=800, height=600, pixel_format=b"RGBA", name="test"
        )
        fb = FramebufferManager(mock_conn, config)
        fb.initialize_buffer()

        # Create multiple rectangles
        pixel_data1 = np.ones((50, 50, 4), dtype=np.uint8) * 100
        pixel_data2 = np.ones((50, 50, 4), dtype=np.uint8) * 150
        pixel_data3 = np.ones((50, 50, 4), dtype=np.uint8) * 200

        rectangles = [
            (0, 0, 50, 50, pixel_data1.tobytes()),
            (100, 100, 50, 50, pixel_data2.tobytes()),
            (200, 200, 50, 50, pixel_data3.tobytes()),
        ]

        fb.process_update(rectangles)

        # Verify all updates were applied
        assert np.all(fb.get_region(0, 0, 50, 50) == 100)
        assert np.all(fb.get_region(100, 100, 50, 50) == 150)
        assert np.all(fb.get_region(200, 200, 50, 50) == 200)
