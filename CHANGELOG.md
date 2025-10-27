# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Placeholder for future releases

### Changed
- N/A

### Deprecated
- N/A

### Removed
- N/A

### Fixed
- N/A

### Security
- N/A

## [0.3.0] - 2025-10-27

### Added
- **WebSocket VNC Support**: Generic WebSocket connections with URL templates
  - New `WebSocketVNCConnection` class for WebSocket-based VNC servers
  - `create_websocket_vnc()` convenience function for easy WebSocket setup
  - URL template system with `${host}`, `${port}`, `${ticket}`, `${password}` placeholders
  - Server-agnostic design supporting Proxmox, noVNC, and custom WebSocket VNC servers
  - SSL/TLS support with certificate verification and custom certificates
  - 45 comprehensive unit tests (95%+ coverage)

- **Connection Strategy Pattern**: Modular connection architecture
  - New `VNCConnectionBase` abstract base class for connection strategies
  - Refactored `TCPVNCConnection` (formerly `VNCConnection`) for TCP connections
  - Clean separation between TCP and WebSocket implementations
  - Backward compatibility maintained with `VNCConnection` alias

- **Enhanced Documentation**: Comprehensive WebSocket guides and examples
  - New `docs/guides/websocket_connections.md` (600+ lines) with usage patterns
  - Updated API documentation for WebSocket connections
  - Working examples in `examples/websocket_usage.py` (400+ lines)
  - Multiple server configuration examples (Proxmox, noVNC, custom)

### Changed
- **Architecture Refactoring**: Connection classes reorganized for modularity
  - `VNCConnection` moved to `connection_tcp.py` as `TCPVNCConnection`
  - New `base_connection.py` with abstract `VNCConnectionBase` class
  - New `connection_websocket.py` with `WebSocketVNCConnection` class
  - Backward compatibility preserved with imports and aliases

- **Code Quality**: Maintained high standards throughout refactoring
  - All 303 tests passing (no regression from v0.2.0)
  - 100% mypy strict compliance maintained
  - Zero flake8 errors
  - 100% black formatting
  - 85%+ test coverage maintained

### Removed
- **Deprecated Code Cleanup**: Removed legacy monolithic connection implementation
  - Deleted `vnc_agent_bridge/core/connection.py` (functionality preserved in modular files)
  - Updated all imports across 7 files (test files, documentation, core modules)
  - Clean codebase with no deprecated code remaining

### Fixed
- **Import Consistency**: All modules now import from correct modular locations
  - Test files updated to use `TCPVNCConnection` from `connection_tcp`
  - Documentation examples updated with correct import paths
  - No remaining references to deprecated `connection.py` module

### Security
- **WebSocket Security**: Enhanced security for WebSocket connections
  - SSL certificate verification enabled by default
  - Support for custom SSL certificates
  - Secure WebSocket (WSS) protocol support
  - Authentication via tickets and passwords (user responsibility for credential security)

## [0.2.0] - 2025-10-27

### Added
- **Screenshot Capture Feature**: Capture screen or specific regions
  - New `ScreenshotController` class with 6 methods
  - `capture()` - Capture full screen as numpy array
  - `capture_region()` - Capture specific screen region
  - `save()` - Save screenshot to file (PNG, JPEG, BMP)
  - `save_region()` - Save region to file
  - `to_pil_image()` - Convert to PIL Image
  - `to_bytes()` - Export as image bytes
  - Full integration with FramebufferManager
  - 52 comprehensive unit tests (95%+ coverage)

- **Video Recording Feature**: Record screen sessions
  - New `VideoRecorder` class with 11 methods
  - `record()` - Record for fixed duration
  - `record_until()` - Record until condition met
  - `start_recording()` / `stop_recording()` - Background recording
  - `save_frames()` - Export frames as PNG/JPEG/BMP
  - Frame statistics: `get_frame_rate()`, `get_duration()`, `frame_count`
  - Configurable FPS (frames per second)
  - 43 comprehensive unit tests (95%+ coverage)

- **Clipboard Management Feature**: Handle remote clipboard
  - New `ClipboardController` class with 5 methods
  - `send_text()` - Send text to remote clipboard
  - `get_text()` - Get text from remote clipboard
  - `clear()` - Clear remote clipboard
  - `has_text()` - Check if clipboard has text
  - `content` property for cached access
  - 24 comprehensive unit tests (100% coverage)

- **Framebuffer Management**: Screen buffer synchronization
  - New `FramebufferManager` class for efficient screen state management
  - `request_update()` - Request incremental or full screen updates
  - `process_update()` - Apply server updates to buffer
  - `get_buffer()` / `get_region()` - Access framebuffer data
  - Support for Raw, CopyRect, RRE, Hextile, ZRLE encodings
  - Dirty tracking for change detection
  - 25 comprehensive unit tests (90%+ coverage)

- **VNCConnection Extensions**: Framebuffer protocol support
  - Added `request_framebuffer_update()` method
  - Added `read_framebuffer_update()` method for parsing updates
  - Added `set_encodings()` method for encoding configuration
  - Added `send_clipboard_text()` and `receive_clipboard_text()` methods
  - Support for FramebufferUpdateRequest message (type 3)
  - Support for SetEncodings message (type 2)
  - Support for ClientCutText message (type 6)

- **VNCAgentBridge Facade Updates**:
  - New `screenshot` property for ScreenshotController
  - New `video` property for VideoRecorder
  - New `clipboard` property for ClipboardController
  - New `enable_framebuffer` parameter (default: True)
  - Graceful degradation when framebuffer disabled
  - Enhanced docstrings with v0.2.0 examples

- **Optional Dependencies**: Conditional feature installation
  - `pip install vnc-agent-bridge[capture]` - For screenshot support
  - `pip install vnc-agent-bridge[video]` - For video recording
  - `pip install vnc-agent-bridge[full]` - For all features
  - Core package remains zero-dependency
  - Requires: numpy>=1.20.0, Pillow>=9.0.0

- **Documentation**: Comprehensive v0.2.0 documentation
  - API Reference: `docs/api/framebuffer.md`, `docs/api/screenshot.md`, `docs/api/clipboard.md`
  - Usage Guides: `docs/guides/screenshot_capture.md`, `docs/guides/video_recording.md`, `docs/guides/clipboard_management.md`, `docs/guides/advanced_v02.md`
  - Example Scripts: 5 new examples demonstrating all features
  - Advanced Patterns: Conditional capture, combined workflows, error recovery
  - 2000+ lines of new documentation

- **Extended Type System**:
  - New types: `ImageFormat`, `FrameData`, `VideoFrame`, `FramebufferConfig`
  - 9 exception types (added 3 new: VNCFramebufferError, VNCClipboardError, VNCEncodingError)
  - Full type safety with 100% mypy strict compliance

- **Quality Assurance**:
  - 282 total tests (v0.1.0 + v0.2.0)
  - 87.54% code coverage (exceeds 85% target)
  - 100% mypy strict compliance
  - 0 flake8 linting errors
  - 100% black formatting compliance
  - Comprehensive integration tests

### Changed
- Updated VNCAgentBridge facade with new controller properties
- Enhanced pyproject.toml with optional dependency groups
- Improved README with v0.2.0 features and examples
- Extended documentation framework for new features

### Deprecated
- N/A (all v0.1.0 APIs maintained)

### Removed
- N/A

### Fixed
- Enhanced error handling for missing optional dependencies
- Improved connection state validation in framebuffer operations

### Security
- No external dependencies required for core functionality
- Optional dependencies (numpy, Pillow) are well-established libraries
- Clipboard operations respect VNC server security restrictions

## [0.1.0] - 2025-10-27

### Added
- Complete VNCConnection class with RFB protocol support
- MouseController with 6 methods (click, move, drag, position)
- KeyboardController with 5 methods (type, press, hotkey, keydown/keyup)
- ScrollController with 3 methods (scroll up/down/to)
- VNCAgentBridge facade with context manager support
- Full type annotations (100% mypy strict compliance)
- Comprehensive test suite (132 tests, 85%+ coverage)

## [0.1.0] - 2025-10-27

### Added
- Complete VNCConnection class with RFB protocol support
- MouseController with 6 methods (click, move, drag, position)
- KeyboardController with 5 methods (type, press, hotkey, keydown/keyup)
- ScrollController with 3 methods (scroll up/down/to)
- VNCAgentBridge facade with context manager support
- Full type annotations (100% mypy strict compliance)
- Comprehensive test suite (132 tests, 85%+ coverage)
- Complete API documentation (4 reference files)
- Usage guides and examples (5 comprehensive guides)
- Example workflows for common use cases
- Detailed module documentation with docstrings

### Changed
- N/A (initial release)

### Deprecated
- N/A

### Removed
- N/A

### Fixed
- N/A

### Security
- No external dependencies - uses only Python standard library
- Input validation on all public methods
- Type-safe parameter handling

## [0.2.0] - 2025-11-XX (Planned)

### Added
- Screenshot capture and image saving capabilities
- Video recording with configurable FPS and formats
- Clipboard text operations (get/set/clear)
- FramebufferManager for screen buffer management
- Extended VNCConnection with framebuffer update support
- Optional dependencies: numpy>=1.20.0, Pillow>=9.0.0
- Enhanced error handling with 9 exception types
- Comprehensive documentation for new features

### Changed
- Improved timing controls and delay mechanisms
- Enhanced keyboard mapping for international layouts
- Extended VNCAgentBridge facade with new controllers

## [1.0.0] - 2026-XX-XX (Future)

### Added
- Async/await support for non-blocking operations
- Connection pooling for multiple VNC servers
- Video encoding with H.264, WebM export formats
- Audio capture and screen+audio recording
- OCR integration for text recognition
- Object detection and AI-powered interaction
- WebSocket and RTMP streaming support
- Multi-display support for dual/triple monitors

### Changed
- API stabilization with backward compatibility guarantees
- Enhanced cross-platform compatibility
- Production-ready stability with comprehensive integration tests

---

## Version History

- **0.1.0**: Core functionality with mouse, keyboard, scroll control
- **0.2.0**: Enhanced features with screenshot, video, and clipboard support
- **1.0.0**: Advanced automation with async support, encoding, and AI features

## Contributing to Changelog

When contributing to this project, please:
1. Add changes to the "Unreleased" section above
2. Categorize changes as Added, Changed, Deprecated, Removed, Fixed, or Security
3. Use present tense for changes ("Add feature" not "Added feature")
4. Reference issue/PR numbers when applicable
5. Update version numbers and dates when releasing

## Release Process

1. Update version in `pyproject.toml` and `vnc_agent_bridge/__init__.py`
2. Move changes from "Unreleased" to new version section
3. Update release date
4. Create git tag: `git tag -a v1.2.3 -m "Release v1.2.3"`
5. Push tag: `git push origin --tags`
6. Publish to PyPI: `python -m build && twine upload dist/*`