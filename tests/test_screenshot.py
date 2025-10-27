"""Unit tests for ScreenshotController.

Tests cover:
- Screenshot capture (full screen and regions)
- Image format conversion (numpy arrays, PIL images, bytes)
- File saving in multiple formats (PNG, JPEG, BMP)
- Error handling and validation
- Framebuffer interaction
- Delay functionality
"""

import pytest
import numpy as np
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, call
from io import BytesIO

from vnc_agent_bridge.core.screenshot import ScreenshotController
from vnc_agent_bridge.types.common import ImageFormat, FramebufferConfig
from vnc_agent_bridge.exceptions import VNCInputError


@pytest.fixture
def mock_connection() -> Mock:
    """Create mock VNC connection."""
    conn = Mock()
    conn.read_framebuffer_update = Mock(return_value=[])
    return conn


@pytest.fixture
def mock_framebuffer() -> Mock:
    """Create mock framebuffer manager."""
    fb = Mock()
    fb.width = 1920
    fb.height = 1080
    fb.request_update = Mock()
    fb.process_update = Mock()
    fb.get_buffer = Mock(return_value=_create_test_array(1080, 1920))
    fb.get_region = Mock(return_value=_create_test_array(300, 400))
    return fb


@pytest.fixture
def screenshot_controller(
    mock_connection: Mock, mock_framebuffer: Mock
) -> ScreenshotController:
    """Create screenshot controller with mocks."""
    return ScreenshotController(mock_connection, mock_framebuffer)


def _create_test_array(height: int, width: int) -> np.ndarray:
    """Create test RGBA numpy array."""
    return np.ones((height, width, 4), dtype=np.uint8) * 128


class TestScreenshotCapture:
    """Test screenshot capture methods."""

    def test_capture_basic(
        self, screenshot_controller: ScreenshotController, mock_framebuffer: Mock
    ) -> None:
        """Test basic full-screen capture."""
        result = screenshot_controller.capture()

        assert isinstance(result, np.ndarray)
        assert result.shape == (1080, 1920, 4)
        assert result.dtype == np.uint8
        mock_framebuffer.request_update.assert_called_once_with(incremental=False)
        mock_framebuffer.process_update.assert_called_once()

    def test_capture_incremental(
        self, screenshot_controller: ScreenshotController, mock_framebuffer: Mock
    ) -> None:
        """Test capture with incremental update."""
        screenshot_controller.capture(incremental=True)

        mock_framebuffer.request_update.assert_called_once_with(incremental=True)

    @patch("time.sleep")
    def test_capture_with_delay(
        self,
        mock_sleep: Mock,
        screenshot_controller: ScreenshotController,
        mock_framebuffer: Mock,
    ) -> None:
        """Test capture with delay."""
        screenshot_controller.capture(delay=1.5)

        mock_sleep.assert_called_once_with(1.5)

    @patch("time.sleep")
    def test_capture_no_delay(
        self,
        mock_sleep: Mock,
        screenshot_controller: ScreenshotController,
        mock_framebuffer: Mock,
    ) -> None:
        """Test that no delay means no sleep call."""
        screenshot_controller.capture(delay=0)

        mock_sleep.assert_not_called()


class TestCaptureRegion:
    """Test region capture methods."""

    def test_capture_region_basic(
        self, screenshot_controller: ScreenshotController, mock_framebuffer: Mock
    ) -> None:
        """Test basic region capture."""
        result = screenshot_controller.capture_region(100, 100, 400, 300)

        assert isinstance(result, np.ndarray)
        assert result.shape == (300, 400, 4)
        mock_framebuffer.request_update.assert_called_once_with(
            incremental=False, x=100, y=100, width=400, height=300
        )
        mock_framebuffer.get_region.assert_called_once_with(100, 100, 400, 300)

    def test_capture_region_corner(
        self, screenshot_controller: ScreenshotController, mock_framebuffer: Mock
    ) -> None:
        """Test capture from corner."""
        screenshot_controller.capture_region(0, 0, 100, 100)

        mock_framebuffer.request_update.assert_called_once_with(
            incremental=False, x=0, y=0, width=100, height=100
        )

    def test_capture_region_invalid_x_negative(
        self, screenshot_controller: ScreenshotController
    ) -> None:
        """Test that negative x raises error."""
        with pytest.raises(VNCInputError):
            screenshot_controller.capture_region(-1, 100, 400, 300)

    def test_capture_region_invalid_y_negative(
        self, screenshot_controller: ScreenshotController
    ) -> None:
        """Test that negative y raises error."""
        with pytest.raises(VNCInputError):
            screenshot_controller.capture_region(100, -1, 400, 300)

    def test_capture_region_invalid_width_zero(
        self, screenshot_controller: ScreenshotController
    ) -> None:
        """Test that zero width raises error."""
        with pytest.raises(VNCInputError):
            screenshot_controller.capture_region(100, 100, 0, 300)

    def test_capture_region_invalid_height_zero(
        self, screenshot_controller: ScreenshotController
    ) -> None:
        """Test that zero height raises error."""
        with pytest.raises(VNCInputError):
            screenshot_controller.capture_region(100, 100, 400, 0)

    def test_capture_region_invalid_width_negative(
        self, screenshot_controller: ScreenshotController
    ) -> None:
        """Test that negative width raises error."""
        with pytest.raises(VNCInputError):
            screenshot_controller.capture_region(100, 100, -400, 300)

    def test_capture_region_exceeds_bounds(
        self, screenshot_controller: ScreenshotController
    ) -> None:
        """Test that region exceeding bounds raises error."""
        with pytest.raises(VNCInputError):
            # 1920 + 100 > 1920
            screenshot_controller.capture_region(1920, 100, 100, 300)

    def test_capture_region_exceeds_height(
        self, screenshot_controller: ScreenshotController
    ) -> None:
        """Test that region exceeding height raises error."""
        with pytest.raises(VNCInputError):
            # 1080 + 100 > 1080
            screenshot_controller.capture_region(100, 1080, 400, 100)

    @patch("time.sleep")
    def test_capture_region_with_delay(
        self,
        mock_sleep: Mock,
        screenshot_controller: ScreenshotController,
        mock_framebuffer: Mock,
    ) -> None:
        """Test region capture with delay."""
        screenshot_controller.capture_region(100, 100, 400, 300, delay=2.0)

        mock_sleep.assert_called_once_with(2.0)


class TestSaveScreenshot:
    """Test screenshot file saving."""

    def test_save_png_format(
        self, screenshot_controller: ScreenshotController, mock_framebuffer: Mock
    ) -> None:
        """Test saving screenshot as PNG."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "test.png")
            screenshot_controller.save(filepath, format=ImageFormat.PNG)

            assert os.path.exists(filepath)
            assert os.path.getsize(filepath) > 0

    def test_save_jpeg_format(
        self, screenshot_controller: ScreenshotController, mock_framebuffer: Mock
    ) -> None:
        """Test saving screenshot as JPEG."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "test.jpg")
            screenshot_controller.save(filepath, format=ImageFormat.JPEG)

            assert os.path.exists(filepath)

    def test_save_bmp_format(
        self, screenshot_controller: ScreenshotController, mock_framebuffer: Mock
    ) -> None:
        """Test saving screenshot as BMP."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "test.bmp")
            screenshot_controller.save(filepath, format=ImageFormat.BMP)

            assert os.path.exists(filepath)

    def test_save_default_format_is_png(
        self, screenshot_controller: ScreenshotController, mock_framebuffer: Mock
    ) -> None:
        """Test that default format is PNG."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "test.png")
            screenshot_controller.save(filepath)

            assert os.path.exists(filepath)

    @patch("time.sleep")
    def test_save_with_delay(
        self,
        mock_sleep: Mock,
        screenshot_controller: ScreenshotController,
        mock_framebuffer: Mock,
    ) -> None:
        """Test save with delay."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "test.png")
            screenshot_controller.save(filepath, delay=1.0)

            mock_sleep.assert_called_once_with(1.0)

    @patch("time.sleep")
    def test_save_incremental_update(
        self,
        mock_sleep: Mock,
        screenshot_controller: ScreenshotController,
        mock_framebuffer: Mock,
    ) -> None:
        """Test save with incremental update."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "test.png")
            screenshot_controller.save(filepath, incremental=True)

            mock_framebuffer.request_update.assert_called_once_with(incremental=True)


class TestSaveRegion:
    """Test region saving."""

    def test_save_region_png(
        self, screenshot_controller: ScreenshotController, mock_framebuffer: Mock
    ) -> None:
        """Test saving region as PNG."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "region.png")
            screenshot_controller.save_region(
                filepath, x=100, y=100, width=400, height=300, format=ImageFormat.PNG
            )

            assert os.path.exists(filepath)

    def test_save_region_jpeg(
        self, screenshot_controller: ScreenshotController, mock_framebuffer: Mock
    ) -> None:
        """Test saving region as JPEG."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "region.jpg")
            screenshot_controller.save_region(
                filepath, x=100, y=100, width=400, height=300, format=ImageFormat.JPEG
            )

            assert os.path.exists(filepath)

    def test_save_region_invalid_coords(
        self, screenshot_controller: ScreenshotController
    ) -> None:
        """Test that invalid region coords raise error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "region.png")
            with pytest.raises(VNCInputError):
                screenshot_controller.save_region(
                    filepath, x=-1, y=100, width=400, height=300
                )

    @patch("time.sleep")
    def test_save_region_with_delay(
        self,
        mock_sleep: Mock,
        screenshot_controller: ScreenshotController,
        mock_framebuffer: Mock,
    ) -> None:
        """Test region save with delay."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "region.png")
            screenshot_controller.save_region(
                filepath, x=100, y=100, width=400, height=300, delay=1.5
            )

            mock_sleep.assert_called_once_with(1.5)


class TestArrayConversion:
    """Test numpy array to PIL Image conversion."""

    def test_to_pil_image_valid_array(
        self, screenshot_controller: ScreenshotController
    ) -> None:
        """Test converting valid numpy array to PIL Image."""
        array = _create_test_array(100, 100)
        pil_image = screenshot_controller.to_pil_image(array)

        assert pil_image is not None
        assert pil_image.size == (100, 100)
        assert pil_image.mode == "RGBA"

    def test_to_pil_image_wrong_shape(
        self, screenshot_controller: ScreenshotController
    ) -> None:
        """Test that wrong shape raises error."""
        array = np.ones((100, 100), dtype=np.uint8)  # Missing channel dimension
        with pytest.raises(ValueError):
            screenshot_controller.to_pil_image(array)

    def test_to_pil_image_wrong_channels(
        self, screenshot_controller: ScreenshotController
    ) -> None:
        """Test that wrong number of channels raises error."""
        array = np.ones((100, 100, 3), dtype=np.uint8)  # RGB instead of RGBA
        with pytest.raises(ValueError):
            screenshot_controller.to_pil_image(array)

    def test_to_pil_image_wrong_dtype(
        self, screenshot_controller: ScreenshotController
    ) -> None:
        """Test that wrong dtype raises error."""
        array = np.ones((100, 100, 4), dtype=np.float32)  # Float instead of uint8
        with pytest.raises(ValueError):
            screenshot_controller.to_pil_image(array)

    def test_to_pil_image_not_array(
        self, screenshot_controller: ScreenshotController
    ) -> None:
        """Test that non-array input raises error."""
        with pytest.raises(ValueError):
            screenshot_controller.to_pil_image([1, 2, 3])  # type: ignore

    def test_to_pil_image_different_sizes(
        self, screenshot_controller: ScreenshotController
    ) -> None:
        """Test converting arrays of different sizes."""
        for height, width in [(10, 10), (100, 100), (1080, 1920)]:
            array = _create_test_array(height, width)
            pil_image = screenshot_controller.to_pil_image(array)

            assert pil_image.size == (width, height)


class TestBytesExport:
    """Test numpy array to bytes export."""

    def test_to_bytes_png(self, screenshot_controller: ScreenshotController) -> None:
        """Test exporting array as PNG bytes."""
        array = _create_test_array(100, 100)
        result = screenshot_controller.to_bytes(array, format=ImageFormat.PNG)

        assert isinstance(result, bytes)
        assert len(result) > 0
        # PNG magic number
        assert result[:8] == b"\x89PNG\r\n\x1a\n"

    def test_to_bytes_jpeg(self, screenshot_controller: ScreenshotController) -> None:
        """Test exporting array as JPEG bytes."""
        array = _create_test_array(100, 100)
        result = screenshot_controller.to_bytes(array, format=ImageFormat.JPEG)

        assert isinstance(result, bytes)
        assert len(result) > 0
        # JPEG magic number
        assert result[:2] == b"\xff\xd8"

    def test_to_bytes_bmp(self, screenshot_controller: ScreenshotController) -> None:
        """Test exporting array as BMP bytes."""
        array = _create_test_array(100, 100)
        result = screenshot_controller.to_bytes(array, format=ImageFormat.BMP)

        assert isinstance(result, bytes)
        assert len(result) > 0
        # BMP magic number
        assert result[:2] == b"BM"

    def test_to_bytes_default_format(
        self, screenshot_controller: ScreenshotController
    ) -> None:
        """Test that default format is PNG."""
        array = _create_test_array(100, 100)
        result = screenshot_controller.to_bytes(array)

        assert result[:8] == b"\x89PNG\r\n\x1a\n"

    def test_to_bytes_invalid_array(
        self, screenshot_controller: ScreenshotController
    ) -> None:
        """Test that invalid array raises error."""
        with pytest.raises(ValueError):
            screenshot_controller.to_bytes(
                np.ones((100, 100), dtype=np.uint8), format=ImageFormat.PNG
            )


class TestFormatHandling:
    """Test image format handling."""

    def test_get_format_string_png(
        self, screenshot_controller: ScreenshotController
    ) -> None:
        """Test getting PIL format string for PNG."""
        result = screenshot_controller._get_format_string(ImageFormat.PNG)
        assert result == "PNG"

    def test_get_format_string_jpeg(
        self, screenshot_controller: ScreenshotController
    ) -> None:
        """Test getting PIL format string for JPEG."""
        result = screenshot_controller._get_format_string(ImageFormat.JPEG)
        assert result == "JPEG"

    def test_get_format_string_bmp(
        self, screenshot_controller: ScreenshotController
    ) -> None:
        """Test getting PIL format string for BMP."""
        result = screenshot_controller._get_format_string(ImageFormat.BMP)
        assert result == "BMP"

    def test_unsupported_format(
        self, screenshot_controller: ScreenshotController
    ) -> None:
        """Test that unsupported format raises error."""
        # Create an invalid format value (not a real ImageFormat)
        with pytest.raises(ValueError):
            screenshot_controller._get_format_string("INVALID")  # type: ignore


class TestFramebufferInteraction:
    """Test interaction with framebuffer manager."""

    def test_framebuffer_request_called(
        self, screenshot_controller: ScreenshotController, mock_framebuffer: Mock
    ) -> None:
        """Test that framebuffer request is called."""
        screenshot_controller.capture()

        mock_framebuffer.request_update.assert_called_once()

    def test_framebuffer_process_called(
        self, screenshot_controller: ScreenshotController, mock_framebuffer: Mock
    ) -> None:
        """Test that framebuffer process is called."""
        screenshot_controller.capture()

        mock_framebuffer.process_update.assert_called_once()

    def test_connection_read_called(
        self, screenshot_controller: ScreenshotController, mock_connection: Mock
    ) -> None:
        """Test that connection read is called."""
        screenshot_controller.capture()

        mock_connection.read_framebuffer_update.assert_called_once()

    def test_framebuffer_properties_used(
        self, screenshot_controller: ScreenshotController, mock_framebuffer: Mock
    ) -> None:
        """Test that framebuffer properties are accessed."""
        screenshot_controller.capture_region(100, 100, 400, 300)

        # Properties should be accessed during validation
        assert mock_framebuffer.width > 0
        assert mock_framebuffer.height > 0


class TestPilImportError:
    """Test handling of missing Pillow dependency."""

    def test_to_pil_image_no_pillow(
        self, screenshot_controller: ScreenshotController
    ) -> None:
        """Test that ImportError is raised when Pillow missing."""
        array = _create_test_array(100, 100)

        # Temporarily hide PIL
        with patch("vnc_agent_bridge.core.screenshot.Image", None):
            with pytest.raises(ImportError):
                screenshot_controller.to_pil_image(array)

    def test_to_bytes_no_pillow(
        self, screenshot_controller: ScreenshotController
    ) -> None:
        """Test that ImportError is raised when Pillow missing."""
        array = _create_test_array(100, 100)

        # Temporarily hide PIL
        with patch("vnc_agent_bridge.core.screenshot.Image", None):
            with pytest.raises(ImportError):
                screenshot_controller.to_bytes(array)


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_capture_region_full_screen(
        self, screenshot_controller: ScreenshotController, mock_framebuffer: Mock
    ) -> None:
        """Test capturing entire screen as region."""
        # Mock returns the requested region
        expected_array = _create_test_array(1080, 1920)
        mock_framebuffer.get_region.return_value = expected_array

        result = screenshot_controller.capture_region(0, 0, 1920, 1080)

        assert result.shape == (1080, 1920, 4)
        mock_framebuffer.get_region.assert_called_once_with(0, 0, 1920, 1080)

    def test_capture_region_single_pixel(
        self, screenshot_controller: ScreenshotController, mock_framebuffer: Mock
    ) -> None:
        """Test capturing single pixel region."""
        screenshot_controller.capture_region(100, 100, 1, 1)

        mock_framebuffer.get_region.assert_called_once_with(100, 100, 1, 1)

    def test_capture_region_max_bounds(
        self, screenshot_controller: ScreenshotController, mock_framebuffer: Mock
    ) -> None:
        """Test capturing region at maximum bounds."""
        screenshot_controller.capture_region(0, 0, 1920, 1080)

        mock_framebuffer.get_region.assert_called_once_with(0, 0, 1920, 1080)

    def test_large_array_conversion(
        self, screenshot_controller: ScreenshotController
    ) -> None:
        """Test converting large arrays."""
        array = _create_test_array(2160, 3840)  # 4K
        pil_image = screenshot_controller.to_pil_image(array)

        assert pil_image.size == (3840, 2160)

    def test_small_array_conversion(
        self, screenshot_controller: ScreenshotController
    ) -> None:
        """Test converting very small arrays."""
        array = _create_test_array(1, 1)
        pil_image = screenshot_controller.to_pil_image(array)

        assert pil_image.size == (1, 1)


class TestSaveArrayHelper:
    """Test _save_array helper method."""

    def test_save_array_creates_file(
        self, screenshot_controller: ScreenshotController
    ) -> None:
        """Test that save_array creates file."""
        array = _create_test_array(100, 100)

        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "test.png")
            screenshot_controller._save_array(array, filepath, ImageFormat.PNG)

            assert os.path.exists(filepath)
            assert os.path.getsize(filepath) > 0

    def test_save_array_multiple_formats(
        self, screenshot_controller: ScreenshotController
    ) -> None:
        """Test saving array in multiple formats."""
        array = _create_test_array(100, 100)

        with tempfile.TemporaryDirectory() as tmpdir:
            for format_type in [ImageFormat.PNG, ImageFormat.JPEG, ImageFormat.BMP]:
                filepath = os.path.join(tmpdir, f"test.{format_type.value}")
                screenshot_controller._save_array(array, filepath, format_type)

                assert os.path.exists(filepath)
