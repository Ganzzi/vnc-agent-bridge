"""Video recording functionality for VNC Agent Bridge."""

from __future__ import annotations

import threading
import time
from pathlib import Path
from typing import TYPE_CHECKING, Callable, List, Optional

from vnc_agent_bridge.exceptions import (
    VNCInputError,
    VNCStateError,
)
from vnc_agent_bridge.types.common import (
    ImageFormat,
    VideoFrame,
)

if TYPE_CHECKING:
    from vnc_agent_bridge.core.base_connection import VNCConnectionBase
    from vnc_agent_bridge.core.framebuffer import FramebufferManager
    from vnc_agent_bridge.core.screenshot import ScreenshotController


class VideoRecorder:
    """Records screen sessions as video frames."""

    def __init__(
        self,
        connection: VNCConnectionBase,
        framebuffer: FramebufferManager,
        screenshot: ScreenshotController,
    ) -> None:
        """Initialize video recorder.

        Args:
            connection: VNC connection instance
            framebuffer: Framebuffer manager instance
            screenshot: Screenshot controller instance

        Raises:
            ImportError: If numpy is not available
        """
        self._connection = connection
        self._framebuffer = framebuffer
        self._screenshot = screenshot

        self._frames: List[VideoFrame] = []
        self._is_recording = False
        self._recording_thread: Optional[threading.Thread] = None
        self._should_stop_recording = False
        self._frame_count = 0

    def record(
        self,
        duration: float,
        fps: float = 30.0,
        delay: float = 0,
    ) -> List[VideoFrame]:
        """Record screen for specified duration.

        Args:
            duration: Recording duration in seconds
            fps: Target frames per second (default 30.0)
            delay: Wait time before starting (default 0)

        Returns:
            List of VideoFrame objects

        Raises:
            VNCInputError: If parameters invalid (duration <= 0, fps <= 0)
            VNCStateError: If not connected to VNC server
        """
        if delay > 0:
            time.sleep(delay)

        if duration <= 0:
            raise VNCInputError(f"Duration must be positive: {duration}")
        if fps <= 0:
            raise VNCInputError(f"FPS must be positive: {fps}")

        if not self._connection.is_connected:
            raise VNCStateError("Not connected to VNC server")

        # Record frames for specified duration
        frames: List[VideoFrame] = []
        start_time = time.time()
        frame_num = 0
        interval = 1.0 / fps

        while time.time() - start_time < duration:
            frame_start = time.time()
            timestamp = frame_start - start_time

            try:
                # Capture frame
                frame_data = self._screenshot.capture(incremental=True)

                # Create VideoFrame object
                frame = VideoFrame(
                    timestamp=timestamp,
                    data=frame_data,
                    frame_number=frame_num,
                )
                frames.append(frame)
                frame_num += 1

                # Maintain FPS by sleeping appropriate time
                elapsed = time.time() - frame_start
                sleep_time = max(0, interval - elapsed)
                if sleep_time > 0:
                    time.sleep(sleep_time)

            except Exception:
                # Continue recording on capture error
                continue

        return frames

    def record_until(
        self,
        condition: Callable[[], bool],
        max_duration: float = 60.0,
        fps: float = 30.0,
        delay: float = 0,
    ) -> List[VideoFrame]:
        """Record screen until condition is met.

        Args:
            condition: Callable that returns True to stop recording
            max_duration: Maximum recording duration in seconds (default 60.0)
            fps: Target frames per second (default 30.0)
            delay: Wait time before starting (default 0)

        Returns:
            List of VideoFrame objects

        Raises:
            VNCInputError: If parameters invalid
            VNCStateError: If not connected to VNC server
        """
        if delay > 0:
            time.sleep(delay)

        if max_duration <= 0:
            raise VNCInputError(f"Max duration must be positive: {max_duration}")
        if fps <= 0:
            raise VNCInputError(f"FPS must be positive: {fps}")

        if not self._connection.is_connected:
            raise VNCStateError("Not connected to VNC server")

        frames: List[VideoFrame] = []
        start_time = time.time()
        frame_num = 0
        interval = 1.0 / fps

        while time.time() - start_time < max_duration:
            # Check stop condition
            try:
                if condition():
                    break
            except Exception:
                # Continue on condition error
                pass

            frame_start = time.time()
            timestamp = frame_start - start_time

            try:
                # Capture frame
                frame_data = self._screenshot.capture(incremental=True)

                # Create VideoFrame object
                frame = VideoFrame(
                    timestamp=timestamp,
                    data=frame_data,
                    frame_number=frame_num,
                )
                frames.append(frame)
                frame_num += 1

                # Maintain FPS by sleeping appropriate time
                elapsed = time.time() - frame_start
                sleep_time = max(0, interval - elapsed)
                if sleep_time > 0:
                    time.sleep(sleep_time)

            except Exception:
                # Continue recording on capture error
                continue

        return frames

    def start_recording(
        self,
        fps: float = 30.0,
        delay: float = 0,
    ) -> None:
        """Start recording in background thread.

        Args:
            fps: Target frames per second (default 30.0)
            delay: Wait time before starting (default 0)

        Raises:
            VNCInputError: If parameters invalid
            VNCStateError: If already recording or not connected
        """
        if self._is_recording:
            raise VNCStateError("Already recording")

        if fps <= 0:
            raise VNCInputError(f"FPS must be positive: {fps}")

        if not self._connection.is_connected:
            raise VNCStateError("Not connected to VNC server")

        self._frames = []
        self._frame_count = 0
        self._should_stop_recording = False
        self._is_recording = True

        # Start recording thread
        self._recording_thread = threading.Thread(
            target=self._recording_worker,
            args=(fps, delay),
            daemon=False,
        )
        self._recording_thread.start()

    def stop_recording(self) -> List[VideoFrame]:
        """Stop background recording and return frames.

        Returns:
            List of VideoFrame objects captured

        Raises:
            VNCStateError: If not currently recording
        """
        if not self._is_recording:
            raise VNCStateError("Not currently recording")

        self._should_stop_recording = True

        # Wait for recording thread to finish
        if self._recording_thread is not None:
            self._recording_thread.join(timeout=10.0)

        self._is_recording = False
        return self._frames.copy()

    def is_recording(self) -> bool:
        """Check if currently recording.

        Returns:
            True if recording, False otherwise
        """
        return self._is_recording

    def save_frames(
        self,
        frames: List[VideoFrame],
        directory: str,
        prefix: str = "frame",
        format: ImageFormat = ImageFormat.PNG,
    ) -> None:
        """Save frames as individual images.

        Args:
            frames: List of VideoFrame objects
            directory: Output directory path
            prefix: Filename prefix (default "frame")
            format: Image format (default PNG)

        Raises:
            VNCInputError: If parameters invalid
            OSError: If directory creation or file write fails
        """
        if not frames:
            raise VNCInputError("No frames to save")

        # Create directory if needed
        output_dir = Path(directory)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save each frame
        for frame in frames:
            filename = f"{prefix}_{frame.frame_number:06d}.{format.value}"
            filepath = output_dir / filename

            # Use screenshot's helper to convert and save
            self._screenshot.save(
                str(filepath),
                format=format,
            )

    def get_frame_rate(self, frames: List[VideoFrame]) -> float:
        """Calculate actual frame rate from recorded frames.

        Args:
            frames: List of VideoFrame objects

        Returns:
            Frames per second (float)

        Raises:
            VNCInputError: If frames list empty or invalid
        """
        if not frames:
            raise VNCInputError("Cannot calculate FPS from empty frame list")

        if len(frames) < 2:
            return 0.0

        total_duration = frames[-1].timestamp - frames[0].timestamp
        if total_duration <= 0:
            return 0.0

        frame_count = len(frames)
        return frame_count / total_duration

    def get_duration(self, frames: List[VideoFrame]) -> float:
        """Get total duration of recorded frames in seconds.

        Args:
            frames: List of VideoFrame objects

        Returns:
            Total duration in seconds (float)

        Raises:
            VNCInputError: If frames list empty
        """
        if not frames:
            raise VNCInputError("Cannot calculate duration from empty frame list")

        return frames[-1].timestamp - frames[0].timestamp

    @property
    def frame_count(self) -> int:
        """Get number of frames recorded during background recording.

        Returns:
            Number of frames
        """
        return self._frame_count

    def _recording_worker(self, fps: float, delay: float) -> None:
        """Background thread worker for continuous recording.

        Args:
            fps: Target frames per second
            delay: Initial delay before starting
        """
        try:
            if delay > 0:
                time.sleep(delay)

            interval = 1.0 / fps
            frame_num = 0
            start_time = time.time()

            while not self._should_stop_recording:
                frame_start = time.time()
                timestamp = frame_start - start_time

                try:
                    # Capture frame
                    frame_data = self._screenshot.capture(incremental=True)

                    # Create VideoFrame object
                    frame = VideoFrame(
                        timestamp=timestamp,
                        data=frame_data,
                        frame_number=frame_num,
                    )
                    self._frames.append(frame)
                    self._frame_count += 1
                    frame_num += 1

                except Exception:
                    # Continue recording on capture error
                    pass

                # Maintain FPS by sleeping appropriate time
                elapsed = time.time() - frame_start
                sleep_time = max(0, interval - elapsed)
                if sleep_time > 0:
                    time.sleep(sleep_time)

        except Exception:
            # Silently fail in background thread
            pass
