# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial implementation of JMS to Clash converter
- Support for VMess, VLESS, Shadowsocks, and Trojan protocols
- Chinese-optimized DNS and routing rules
- Comprehensive test suite with 22 test cases
- Modern Python packaging with pyproject.toml
- Fast package management with uv
- Cross-platform binary building
- Development helper script (dev.py)
- GitHub Actions for CI/CD and automated releases

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

[Unreleased]: https://github.com/skywardpixel/jms2clash/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/skywardpixel/jms2clash/releases/tag/v0.1.0