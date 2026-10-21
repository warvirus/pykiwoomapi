# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Changed
- Development environment moved from conda/pip to uv (`uv.lock`, `[dependency-groups]`)
- CI and publish workflows now use uv

### Removed
- pandas dependency (not imported anywhere in the package)

## [0.1.0] - 2025-04-26

### Added
- Initial release
- Auth module (OAuth2 authentication)
- KiwoomClient (REST API wrapper)
- WebSocketClient (real-time data streaming)
- 180+ API endpoints covering Korean stock market
- Mock/demo environment support
- Custom exception classes
- Comprehensive test suite
- GitHub Actions CI/CD

### Removed
- pyqt5 dependency (not used in REST API)
- pywin32 dependency (Windows only, not required)