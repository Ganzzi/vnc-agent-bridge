# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **v0.2.0 Phase 1 Foundation Complete**: Extended VNCConnection for framebuffer support
  - Added `request_framebuffer_update()` method for screen update requests
  - Added `read_framebuffer_update()` method for parsing server responses
  - Added `set_encodings()` method to configure supported VNC encodings
  - Added `send_clipboard_text()` and `receive_clipboard_text()` methods
  - Created FramebufferManager class with numpy-based pixel storage
  - Added rectangle update processing and dirty tracking
  - Extended type system with ImageFormat, FrameData, VideoFrame, FramebufferConfig
  - All code passes mypy strict and flake8 quality checks
- Initial project structure and setup
- Type definitions and exception hierarchy
- Configuration files (pyproject.toml, setup.py, etc.)
- CI/CD workflow with GitHub Actions
- Comprehensive documentation and planning

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