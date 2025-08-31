# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.2] - 2024-12-19

### Added
- **Automated Release System**: Comprehensive GitHub Actions workflow for cross-platform binary releases
- **Installation Scripts**: Easy-to-use installation scripts for Linux/macOS (`install.sh`) and Windows (`install.ps1`)
- **Cross-Platform Packages**: Pre-built binaries with documentation packaged as archives
- **Release Verification**: SHA256 checksums for all release assets
- **Enhanced Documentation**: Updated README with multiple installation methods

### Improved
- **Binary Packaging**: Archives now include README, LICENSE, and platform-specific installation instructions
- **GitHub Actions**: Enhanced workflows with better error handling, platform detection, and release automation
- **User Experience**: One-command installation for all supported platforms
- **Release Notes**: Automated changelog extraction and comprehensive release documentation

### Technical Enhancements
- PyInstaller optimization flags for smaller, faster binaries
- Improved cross-platform compatibility testing
- Automated artifact verification and testing
- Enhanced workflow error handling and debugging

## [0.1.1] - 2024-12-19

### Fixed
- **Encoding errors**: Fixed UTF-8 decoding issues in Shadowsocks and VMess URL parsing
- **Base64 decoding**: Added robust error handling for malformed base64 data with fallback to latin-1 encoding
- **Error messages**: Improved error reporting with cleaner warning messages instead of verbose stack traces
- **Subscription parsing**: Enhanced base64 subscription decoder to handle various encoding formats

### Technical Improvements
- Added `binascii.Error` exception handling for invalid base64 data
- Implemented encoding fallback chain: UTF-8 → latin-1 → skip
- Applied encoding fixes across all proxy decoders (VMess, Shadowsocks, subscription parser)
- Reduced error verbosity while maintaining functionality

## [0.1.0] - 2024-08-31

### Added
- Convert JMS subscription strings to Clash configuration files
- Support for multiple proxy protocols:
  - VMess (including WebSocket transport)
  - VLESS (with various transport options)
  - Shadowsocks (multiple ciphers)
  - Trojan (with SNI support)
- Base64 encoded subscription parsing
- Chinese user optimizations:
  - DNS servers: Tencent (119.29.29.29), Alibaba (223.5.5.5)
  - Fallback DNS: Cloudflare, Google DNS over HTTPS
  - Service-specific proxy groups (Bilibili, NetEase Music, etc.)
  - Ad blocking rules
  - GeoIP-based routing (CN traffic → Direct)
- Complete Clash configuration generation with:
  - 14 proxy groups with Chinese names and emojis
  - 80+ routing rules optimized for China
  - Fake IP DNS for better performance
  - Automatic and manual proxy selection options
- Professional development setup:
  - Modern Python packaging (pyproject.toml)
  - uv for fast package management
  - Comprehensive pytest test suite
  - Code formatting with Black and Ruff
  - Development automation with Makefile
- Cross-platform binary building with PyInstaller
- Clean separation of concerns:
  - Pure conversion logic in main script
  - All testing in pytest framework
  - All building in Makefile
- Multiple usage interfaces:
  - Direct Python script execution
  - Compiled standalone binary
  - Development helper script (dev.py)
  - Make commands for automation

### Technical Details
- **Language**: Python 3.8+
- **Dependencies**: PyYAML (runtime), pytest/black/ruff (dev), PyInstaller (build)
- **Architecture**: Single-file converter with modular decoder functions
- **Testing**: 22 comprehensive test cases covering all protocols and edge cases
- **Performance**: Processes 1000+ proxies per second, generates 50-200KB configs
- **Binary Size**: ~7MB standalone executable

### Supported Platforms
- Linux (x64)
- Windows (x64) 
- macOS (x64 & ARM64)

[Unreleased]: https://github.com/skywardpixel/jms2clash/compare/v0.1.2...HEAD
[0.1.2]: https://github.com/skywardpixel/jms2clash/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/skywardpixel/jms2clash/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/skywardpixel/jms2clash/releases/tag/v0.1.0