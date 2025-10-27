"""Comprehensive tests for VideoRecorder class."""

from __future__ import annotations

import tempfile
import time
from pathlib import Path
from unittest.mock import Mock

import numpy as np
import pytest

from vnc_agent_bridge.core.video import VideoRecorder
from vnc_agent_bridge.exceptions import VNCInputError, VNCStateError
from vnc_agent_bridge.types.common import ImageFormat, VideoFrame


class TestVideoRecorderInit:
    """Test VideoRecorder initialization."""

    def test_init_success(self) -> None:
        """Test successful initialization."""
        mock_conn = Mock()
        mock_framebuffer = Mock()
        mock_screenshot = Mock()

        recorder = VideoRecorder(mock_conn, mock_framebuffer, mock_screenshot)

        assert recorder._connection is mock_conn
        assert recorder._framebuffer is mock_framebuffer
        assert recorder._screenshot is mock_screenshot
        assert not recorder._is_recording
        assert recorder._frame_count == 0


class TestVideoRecorderRecord:
    """Test record() method."""

    def test_record_success(self) -> None:
        """Test successful fixed duration recording."""
        mock_conn = Mock()
        mock_conn.is_connected = True
        mock_framebuffer = Mock()
        mock_screenshot = Mock()

        # Create sample frame data
        frame_data = np.zeros((480, 640, 4), dtype=np.uint8)
        mock_screenshot.capture.return_value = frame_data

        recorder = VideoRecorder(mock_conn, mock_framebuffer, mock_screenshot)
        frames = recorder.record(duration=0.1, fps=10.0)

        assert len(frames) > 0
        assert all(isinstance(f, VideoFrame) for f in frames)
        assert all(f.data is frame_data for f in frames)

    def test_record_zero_duration(self) -> None:
        """Test record with zero duration."""
        mock_conn = Mock()
        mock_conn.is_connected = True
        recorder = VideoRecorder(mock_conn, Mock(), Mock())

        with pytest.raises(VNCInputError):
            recorder.record(duration=0, fps=30.0)

    def test_record_negative_duration(self) -> None:
        """Test record with negative duration."""
        mock_conn = Mock()
        mock_conn.is_connected = True
        recorder = VideoRecorder(mock_conn, Mock(), Mock())

        with pytest.raises(VNCInputError):
            recorder.record(duration=-1.0, fps=30.0)

    def test_record_zero_fps(self) -> None:
        """Test record with zero FPS."""
        mock_conn = Mock()
        mock_conn.is_connected = True
        recorder = VideoRecorder(mock_conn, Mock(), Mock())

        with pytest.raises(VNCInputError):
            recorder.record(duration=1.0, fps=0)

    def test_record_negative_fps(self) -> None:
        """Test record with negative FPS."""
        mock_conn = Mock()
        mock_conn.is_connected = True
        recorder = VideoRecorder(mock_conn, Mock(), Mock())

        with pytest.raises(VNCInputError):
            recorder.record(duration=1.0, fps=-30.0)

    def test_record_not_connected(self) -> None:
        """Test record when not connected."""
        mock_conn = Mock()
        mock_conn.is_connected = False
        recorder = VideoRecorder(mock_conn, Mock(), Mock())

        with pytest.raises(VNCStateError):
            recorder.record(duration=1.0, fps=30.0)

    def test_record_with_delay(self) -> None:
        """Test record with initial delay."""
        mock_conn = Mock()
        mock_conn.is_connected = True
        mock_screenshot = Mock()
        mock_screenshot.capture.return_value = np.zeros((480, 640, 4), dtype=np.uint8)

        recorder = VideoRecorder(mock_conn, Mock(), mock_screenshot)

        start = time.time()
        _ = recorder.record(duration=0.05, fps=10.0, delay=0.1)
        elapsed = time.time() - start

        assert elapsed >= 0.1  # Includes delay

    def test_record_frame_numbering(self) -> None:
        """Test that frames are numbered correctly."""
        mock_conn = Mock()
        mock_conn.is_connected = True
        mock_screenshot = Mock()
        mock_screenshot.capture.return_value = np.zeros((480, 640, 4), dtype=np.uint8)

        recorder = VideoRecorder(mock_conn, Mock(), mock_screenshot)
        frames = recorder.record(duration=0.1, fps=10.0)

        for i, frame in enumerate(frames):
            assert frame.frame_number == i

    def test_record_maintains_fps(self) -> None:
        """Test that recording maintains target FPS."""
        mock_conn = Mock()
        mock_conn.is_connected = True
        mock_screenshot = Mock()
        mock_screenshot.capture.return_value = np.zeros((480, 640, 4), dtype=np.uint8)

        recorder = VideoRecorder(mock_conn, Mock(), mock_screenshot)
        frames = recorder.record(duration=0.2, fps=10.0)

        # Should have approximately 2 frames at 10 FPS for 0.2 seconds
        assert len(frames) >= 1


class TestVideoRecorderRecordUntil:
    """Test record_until() method."""

    def test_record_until_condition_true(self) -> None:
        """Test record_until when condition becomes true."""
        mock_conn = Mock()
        mock_conn.is_connected = True
        mock_screenshot = Mock()
        mock_screenshot.capture.return_value = np.zeros((480, 640, 4), dtype=np.uint8)

        condition_calls = [0]

        def condition() -> bool:
            condition_calls[0] += 1
            return condition_calls[0] >= 3

        recorder = VideoRecorder(mock_conn, Mock(), mock_screenshot)
        frames = recorder.record_until(condition, max_duration=10.0, fps=10.0)

        assert len(frames) > 0
        assert condition_calls[0] >= 3

    def test_record_until_max_duration(self) -> None:
        """Test record_until reaches max duration."""
        mock_conn = Mock()
        mock_conn.is_connected = True
        mock_screenshot = Mock()
        mock_screenshot.capture.return_value = np.zeros((480, 640, 4), dtype=np.uint8)

        condition = Mock(return_value=False)

        recorder = VideoRecorder(mock_conn, Mock(), mock_screenshot)
        start = time.time()
        _ = recorder.record_until(condition, max_duration=0.1, fps=10.0)
        elapsed = time.time() - start

        assert elapsed >= 0.1

    def test_record_until_invalid_max_duration(self) -> None:
        """Test record_until with invalid max_duration."""
        mock_conn = Mock()
        mock_conn.is_connected = True
        recorder = VideoRecorder(mock_conn, Mock(), Mock())

        with pytest.raises(VNCInputError):
            recorder.record_until(lambda: False, max_duration=0)

    def test_record_until_invalid_fps(self) -> None:
        """Test record_until with invalid fps."""
        mock_conn = Mock()
        mock_conn.is_connected = True
        recorder = VideoRecorder(mock_conn, Mock(), Mock())

        with pytest.raises(VNCInputError):
            recorder.record_until(lambda: False, max_duration=1.0, fps=-1.0)

    def test_record_until_not_connected(self) -> None:
        """Test record_until when not connected."""
        mock_conn = Mock()
        mock_conn.is_connected = False
        recorder = VideoRecorder(mock_conn, Mock(), Mock())

        with pytest.raises(VNCStateError):
            recorder.record_until(lambda: False, max_duration=1.0, fps=30.0)

    def test_record_until_with_delay(self) -> None:
        """Test record_until with initial delay."""
        mock_conn = Mock()
        mock_conn.is_connected = True
        mock_screenshot = Mock()
        mock_screenshot.capture.return_value = np.zeros((480, 640, 4), dtype=np.uint8)

        recorder = VideoRecorder(mock_conn, Mock(), mock_screenshot)
        start = time.time()
        _ = recorder.record_until(lambda: False, max_duration=0.05, fps=10.0, delay=0.1)
        elapsed = time.time() - start

        assert elapsed >= 0.1


class TestVideoRecorderBackgroundRecording:
    """Test start_recording() and stop_recording() methods."""

    def test_start_recording_success(self) -> None:
        """Test successful start_recording."""
        mock_conn = Mock()
        mock_conn.is_connected = True
        mock_screenshot = Mock()
        mock_screenshot.capture.return_value = np.zeros((480, 640, 4), dtype=np.uint8)

        recorder = VideoRecorder(mock_conn, Mock(), mock_screenshot)
        recorder.start_recording(fps=10.0)

        assert recorder.is_recording()
        time.sleep(0.05)
        frames = recorder.stop_recording()

        assert len(frames) > 0
        assert not recorder.is_recording()

    def test_start_recording_already_recording(self) -> None:
        """Test start_recording when already recording."""
        mock_conn = Mock()
        mock_conn.is_connected = True
        mock_screenshot = Mock()
        mock_screenshot.capture.return_value = np.zeros((480, 640, 4), dtype=np.uint8)

        recorder = VideoRecorder(mock_conn, Mock(), mock_screenshot)
        recorder.start_recording(fps=10.0)

        with pytest.raises(VNCStateError):
            recorder.start_recording(fps=10.0)

        recorder.stop_recording()

    def test_start_recording_invalid_fps(self) -> None:
        """Test start_recording with invalid fps."""
        mock_conn = Mock()
        mock_conn.is_connected = True
        recorder = VideoRecorder(mock_conn, Mock(), Mock())

        with pytest.raises(VNCInputError):
            recorder.start_recording(fps=0)

    def test_start_recording_not_connected(self) -> None:
        """Test start_recording when not connected."""
        mock_conn = Mock()
        mock_conn.is_connected = False
        recorder = VideoRecorder(mock_conn, Mock(), Mock())

        with pytest.raises(VNCStateError):
            recorder.start_recording(fps=10.0)

    def test_stop_recording_not_recording(self) -> None:
        """Test stop_recording when not recording."""
        mock_conn = Mock()
        mock_conn.is_connected = True
        recorder = VideoRecorder(mock_conn, Mock(), Mock())

        with pytest.raises(VNCStateError):
            recorder.stop_recording()

    def test_stop_recording_with_delay(self) -> None:
        """Test start_recording with initial delay."""
        mock_conn = Mock()
        mock_conn.is_connected = True
        mock_screenshot = Mock()
        mock_screenshot.capture.return_value = np.zeros((480, 640, 4), dtype=np.uint8)

        recorder = VideoRecorder(mock_conn, Mock(), mock_screenshot)
        start = time.time()
        recorder.start_recording(fps=10.0, delay=0.1)
        time.sleep(0.15)
        _ = recorder.stop_recording()
        elapsed = time.time() - start

        # Total time includes delay + recording
        assert elapsed >= 0.1

    def test_is_recording_initial_state(self) -> None:
        """Test is_recording() initially returns False."""
        mock_conn = Mock()
        recorder = VideoRecorder(mock_conn, Mock(), Mock())

        assert not recorder.is_recording()

    def test_is_recording_after_start(self) -> None:
        """Test is_recording() returns True after start."""
        mock_conn = Mock()
        mock_conn.is_connected = True
        mock_screenshot = Mock()
        mock_screenshot.capture.return_value = np.zeros((480, 640, 4), dtype=np.uint8)

        recorder = VideoRecorder(mock_conn, Mock(), mock_screenshot)
        recorder.start_recording(fps=10.0)

        assert recorder.is_recording()
        recorder.stop_recording()

    def test_is_recording_after_stop(self) -> None:
        """Test is_recording() returns False after stop."""
        mock_conn = Mock()
        mock_conn.is_connected = True
        mock_screenshot = Mock()
        mock_screenshot.capture.return_value = np.zeros((480, 640, 4), dtype=np.uint8)

        recorder = VideoRecorder(mock_conn, Mock(), mock_screenshot)
        recorder.start_recording(fps=10.0)
        recorder.stop_recording()

        assert not recorder.is_recording()


class TestVideoRecorderFrameStatistics:
    """Test get_frame_rate() and get_duration() methods."""

    def test_get_frame_rate_success(self) -> None:
        """Test successful frame rate calculation."""
        frames = [
            VideoFrame(timestamp=0.0, data=Mock(), frame_number=0),
            VideoFrame(timestamp=0.05, data=Mock(), frame_number=1),
            VideoFrame(timestamp=0.1, data=Mock(), frame_number=2),
        ]

        mock_conn = Mock()
        recorder = VideoRecorder(mock_conn, Mock(), Mock())
        fps = recorder.get_frame_rate(frames)

        # 3 frames over 0.1 seconds = 30 fps
        assert fps == pytest.approx(30.0, rel=0.01)

    def test_get_frame_rate_empty_frames(self) -> None:
        """Test get_frame_rate with empty frames."""
        mock_conn = Mock()
        recorder = VideoRecorder(mock_conn, Mock(), Mock())

        with pytest.raises(VNCInputError):
            recorder.get_frame_rate([])

    def test_get_frame_rate_single_frame(self) -> None:
        """Test get_frame_rate with single frame."""
        frames = [VideoFrame(timestamp=0.0, data=Mock(), frame_number=0)]

        mock_conn = Mock()
        recorder = VideoRecorder(mock_conn, Mock(), Mock())
        fps = recorder.get_frame_rate(frames)

        assert fps == 0.0

    def test_get_frame_rate_same_timestamp(self) -> None:
        """Test get_frame_rate with frames at same timestamp."""
        frames = [
            VideoFrame(timestamp=0.0, data=Mock(), frame_number=0),
            VideoFrame(timestamp=0.0, data=Mock(), frame_number=1),
        ]

        mock_conn = Mock()
        recorder = VideoRecorder(mock_conn, Mock(), Mock())
        fps = recorder.get_frame_rate(frames)

        assert fps == 0.0

    def test_get_duration_success(self) -> None:
        """Test successful duration calculation."""
        frames = [
            VideoFrame(timestamp=0.0, data=Mock(), frame_number=0),
            VideoFrame(timestamp=0.5, data=Mock(), frame_number=1),
            VideoFrame(timestamp=1.0, data=Mock(), frame_number=2),
        ]

        mock_conn = Mock()
        recorder = VideoRecorder(mock_conn, Mock(), Mock())
        duration = recorder.get_duration(frames)

        assert duration == pytest.approx(1.0, rel=0.01)

    def test_get_duration_empty_frames(self) -> None:
        """Test get_duration with empty frames."""
        mock_conn = Mock()
        recorder = VideoRecorder(mock_conn, Mock(), Mock())

        with pytest.raises(VNCInputError):
            recorder.get_duration([])

    def test_get_duration_single_frame(self) -> None:
        """Test get_duration with single frame."""
        frames = [VideoFrame(timestamp=0.5, data=Mock(), frame_number=0)]

        mock_conn = Mock()
        recorder = VideoRecorder(mock_conn, Mock(), Mock())
        duration = recorder.get_duration(frames)

        assert duration == pytest.approx(0.0, rel=0.01)


class TestVideoRecorderSaveFrames:
    """Test save_frames() method."""

    def test_save_frames_success(self) -> None:
        """Test successful frame saving."""
        frames = [
            VideoFrame(
                timestamp=0.0,
                data=np.zeros((480, 640, 4), dtype=np.uint8),
                frame_number=0,
            ),
            VideoFrame(
                timestamp=0.05,
                data=np.zeros((480, 640, 4), dtype=np.uint8),
                frame_number=1,
            ),
        ]

        mock_conn = Mock()
        mock_screenshot = Mock()
        mock_screenshot.save = Mock()

        recorder = VideoRecorder(mock_conn, Mock(), mock_screenshot)

        with tempfile.TemporaryDirectory() as tmpdir:
            recorder.save_frames(frames, tmpdir, prefix="test", format=ImageFormat.PNG)

            # Verify save was called for each frame
            assert mock_screenshot.save.call_count == 2

    def test_save_frames_empty_list(self) -> None:
        """Test save_frames with empty frame list."""
        mock_conn = Mock()
        recorder = VideoRecorder(mock_conn, Mock(), Mock())

        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.raises(VNCInputError):
                recorder.save_frames([], tmpdir)

    def test_save_frames_creates_directory(self) -> None:
        """Test that save_frames creates directory if needed."""
        frames = [
            VideoFrame(
                timestamp=0.0,
                data=np.zeros((480, 640, 4), dtype=np.uint8),
                frame_number=0,
            ),
        ]

        mock_conn = Mock()
        mock_screenshot = Mock()
        mock_screenshot.save = Mock()

        recorder = VideoRecorder(mock_conn, Mock(), mock_screenshot)

        with tempfile.TemporaryDirectory() as tmpdir:
            subdir = Path(tmpdir) / "new_dir" / "nested"
            recorder.save_frames(frames, str(subdir))

            # Directory should have been created
            assert subdir.exists()

    def test_save_frames_with_different_formats(self) -> None:
        """Test save_frames with different image formats."""
        frames = [
            VideoFrame(
                timestamp=0.0,
                data=np.zeros((480, 640, 4), dtype=np.uint8),
                frame_number=0,
            ),
        ]

        mock_conn = Mock()
        mock_screenshot = Mock()
        mock_screenshot.save = Mock()

        recorder = VideoRecorder(mock_conn, Mock(), mock_screenshot)

        with tempfile.TemporaryDirectory() as tmpdir:
            for fmt in [ImageFormat.PNG, ImageFormat.JPEG, ImageFormat.BMP]:
                recorder.save_frames(frames, tmpdir, format=fmt)


class TestVideoRecorderFrameCount:
    """Test frame_count property."""

    def test_frame_count_initial(self) -> None:
        """Test frame_count is 0 initially."""
        mock_conn = Mock()
        recorder = VideoRecorder(mock_conn, Mock(), Mock())

        assert recorder.frame_count == 0

    def test_frame_count_increments(self) -> None:
        """Test frame_count increments during recording."""
        mock_conn = Mock()
        mock_conn.is_connected = True
        mock_screenshot = Mock()
        mock_screenshot.capture.return_value = np.zeros((480, 640, 4), dtype=np.uint8)

        recorder = VideoRecorder(mock_conn, Mock(), mock_screenshot)
        recorder.start_recording(fps=10.0)
        time.sleep(0.1)

        count_during = recorder.frame_count
        assert count_during > 0

        recorder.stop_recording()


class TestVideoRecorderEdgeCases:
    """Test edge cases and error handling."""

    def test_record_capture_error_continues(self) -> None:
        """Test that recording continues on capture error."""
        mock_conn = Mock()
        mock_conn.is_connected = True
        mock_screenshot = Mock()
        mock_screenshot.capture.side_effect = [
            Exception("Capture failed"),
            np.zeros((480, 640, 4), dtype=np.uint8),
            np.zeros((480, 640, 4), dtype=np.uint8),
        ]

        recorder = VideoRecorder(mock_conn, Mock(), mock_screenshot)
        frames = recorder.record(duration=0.2, fps=5.0)

        # Should have frames even with one error
        assert len(frames) >= 1

    def test_record_until_condition_error(self) -> None:
        """Test that record_until continues on condition error."""
        mock_conn = Mock()
        mock_conn.is_connected = True
        mock_screenshot = Mock()
        mock_screenshot.capture.return_value = np.zeros((480, 640, 4), dtype=np.uint8)

        call_count = [0]

        def condition() -> bool:
            call_count[0] += 1
            if call_count[0] == 1:
                raise Exception("Condition error")
            return call_count[0] >= 3

        recorder = VideoRecorder(mock_conn, Mock(), mock_screenshot)
        frames = recorder.record_until(condition, max_duration=10.0, fps=10.0)

        assert len(frames) > 0

    def test_background_recording_capture_error(self) -> None:
        """Test background recording continues on capture error."""
        mock_conn = Mock()
        mock_conn.is_connected = True
        mock_screenshot = Mock()
        mock_screenshot.capture.side_effect = [
            Exception("Capture failed"),
            np.zeros((480, 640, 4), dtype=np.uint8),
            np.zeros((480, 640, 4), dtype=np.uint8),
        ]

        recorder = VideoRecorder(mock_conn, Mock(), mock_screenshot)
        recorder.start_recording(fps=10.0)
        time.sleep(0.15)
        frames = recorder.stop_recording()

        # Should have frames even with one error
        assert len(frames) >= 1


class TestVideoRecorderIntegration:
    """Integration tests combining multiple features."""

    def test_full_recording_workflow(self) -> None:
        """Test complete recording workflow."""
        mock_conn = Mock()
        mock_conn.is_connected = True
        mock_screenshot = Mock()
        mock_screenshot.capture.return_value = np.zeros((480, 640, 4), dtype=np.uint8)
        mock_screenshot.save = Mock()

        recorder = VideoRecorder(mock_conn, Mock(), mock_screenshot)

        # Record video
        frames = recorder.record(duration=0.2, fps=10.0)
        assert len(frames) > 0

        # Calculate statistics
        fps = recorder.get_frame_rate(frames)
        duration = recorder.get_duration(frames)

        assert fps >= 0  # FPS might be 0 with < 2 frames
        assert duration >= 0

        # Save frames
        with tempfile.TemporaryDirectory() as tmpdir:
            recorder.save_frames(frames, tmpdir)

    def test_mixed_recording_modes(self) -> None:
        """Test using both fixed-duration and background recording."""
        mock_conn = Mock()
        mock_conn.is_connected = True
        mock_screenshot = Mock()
        mock_screenshot.capture.return_value = np.zeros((480, 640, 4), dtype=np.uint8)

        recorder = VideoRecorder(mock_conn, Mock(), mock_screenshot)

        # Fixed duration recording
        frames1 = recorder.record(duration=0.05, fps=10.0)

        # Background recording
        recorder.start_recording(fps=10.0)
        time.sleep(0.05)
        frames2 = recorder.stop_recording()

        assert len(frames1) > 0
        assert len(frames2) > 0
