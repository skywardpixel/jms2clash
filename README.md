# jms2clash

Convert JMS subscription strings to Clash configuration files optimized for Chinese users.

## Features

- **Multi-format support**: VMess, VLESS, Shadowsocks, Trojan
- **Chinese optimization**: DNS, routing rules, and proxy groups for China users
- **Clean architecture**: Focused Python script with proper testing and build tools
- **Comprehensive testing**: Full pytest test suite
- **Modern tooling**: Uses uv for fast package management

## Installation

### 🚀 Quick Install (Recommended)

**Linux/macOS:**
```bash
curl -fsSL https://raw.githubusercontent.com/skywardpixel/jms2clash/main/install.sh | bash
```

**Windows (PowerShell):**
```powershell
iwr https://raw.githubusercontent.com/skywardpixel/jms2clash/main/install.ps1 | iex
```

### 📦 Manual Download

Download pre-built binaries from [GitHub Releases](https://github.com/skywardpixel/jms2clash/releases/latest):

- **Linux x64**: `jms2clash-linux-x64.tar.gz`
- **Windows x64**: `jms2clash-windows-x64.exe.zip`
- **macOS x64**: `jms2clash-macos-x64.tar.gz`
- **macOS ARM64**: `jms2clash-macos-arm64.tar.gz`

Extract and run directly:
```bash
# Linux/macOS
tar -xzf jms2clash-*.tar.gz
chmod +x jms2clash
./jms2clash < subscription.txt > config.yaml

# Windows
# Extract the ZIP file and run jms2clash.exe
```

### 🛠️ Development Setup

For development or building from source:

#### 1. Install uv (Modern Python Package Manager)
```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or via homebrew
brew install uv
```

#### 2. Setup Environment
```bash
# Install dependencies
make deps

# Or manually with uv
uv pip install -e ".[dev,build]"
```

#### 3. Build and Test
```bash
# Run tests
make test

# Build standalone binary
make build

# Use binary
echo "subscription_content" | ./dist/jms2clash > config.yaml
```

## Quick Start

## Supported Formats

### Input Formats
- **VMess**: `vmess://eyJhZGQiOiJleGFtcGxlLmNvbSIsImFpZCI...`
- **VLESS**: `vless://uuid@server:port?type=tcp&security=tls#name`
- **Shadowsocks**: `ss://YWVzLTI1Ni1nY206cGFzc3dvcmQ@server:port#name`
- **Trojan**: `trojan://password@server:port?sni=example.com#name`
- **Base64 encoded** subscription files
- **Mixed format** files with comments (lines starting with # are ignored)

### Example Input
```
# Example subscription file
vmess://eyJhZGQiOiJleGFtcGxlLmNvbSIsImFpZCI6IjAiLCJpZCI6InRlc3QiLCJuZXQiOiJ0Y3AiLCJwb3J0IjoiNDQzIiwicHMiOiJUZXN0Iiwic2N5IjoiYXV0byIsInRscyI6InRscyIsInYiOiIyIn0=
ss://YWVzLTI1Ni1nY206cGFzc3dvcmQ@example.com:8388#Test%20SS
trojan://password@example.com:443?sni=example.com#Test%20Trojan
```

## Generated Configuration

The output Clash config includes:

### Proxy Groups (Chinese Optimized)
- 🚀 **节点选择** - Manual proxy selection
- ♻️ **自动选择** - Automatic fastest proxy
- 🎯 **全球直连** - Direct connection
- 🛑 **广告拦截** - Ad blocking
- 📺 **哔哩哔哩** - Bilibili optimization
- 🎵 **网易云音乐** - Music services
- 📹 **YouTube** - International streaming
- 🎬 **Netflix** - Streaming services
- 📱 **Telegram** - Messaging
- 🔍 **Google** - Google services
- 🍎 **苹果服务** - Apple services
- Ⓜ️ **微软服务** - Microsoft services

### DNS Configuration
- **Primary DNS**: 119.29.29.29 (Tencent), 223.5.5.5 (Alibaba)
- **Fallback DNS**: Cloudflare, Google DNS over HTTPS
- **Fake IP**: Enabled for better performance
- **GeoIP filtering**: China vs international routing

### Routing Rules
- **Local network** → Direct
- **Chinese services** → Direct
- **International services** → Proxy
- **Ad domains** → Block
- **GeoIP CN** → Direct

## Usage Examples

### Basic Conversion
```bash
# With installed binary
curl -s "https://example.com/subscription" | jms2clash > config.yaml

# From file
jms2clash < subscription.txt > clash_config.yaml

# Multiple subscriptions
cat sub1.txt sub2.txt | jms2clash > combined.yaml
```

### Development Usage
```bash
# File to file
uv run python src/jms_to_clash.py < subscription.txt > clash_config.yaml

# Pipe from curl
curl -s "https://example.com/subscription" | uv run python src/jms_to_clash.py > config.yaml

# Using local binary after building
./dist/jms2clash < subscription.txt > config.yaml
```

### Integration Examples
```bash
# Automated daily update
#!/bin/bash
curl -s "$SUBSCRIPTION_URL" | jms2clash > ~/.config/clash/config.yaml
systemctl restart clash

# Validate generated config
jms2clash < input.txt > config.yaml
python3 -c "import yaml; yaml.safe_load(open('config.yaml'))" && echo "Valid YAML"

# Windows PowerShell example
Invoke-WebRequest -Uri $SubscriptionUrl | Select-Object -ExpandProperty Content | jms2clash.exe > config.yaml
```

## Development

### Project Structure
```
jms2clash/
├── src/jms_to_clash.py          # Core conversion logic
├── test_jms_to_clash.py         # Comprehensive pytest test suite
├── pyproject.toml               # Modern Python packaging
├── Makefile                     # Build and test automation
├── dev.py                       # Development helper
├── .python-version              # Python version for uv
└── README.md                    # This file
```

### Available Make Commands
```bash
make help         # Show all available commands
make install-uv   # Install uv package manager
make deps         # Install Python dependencies with uv
make dev          # Setup development environment
make test         # Run all tests (pytest + functionality)
make pytest       # Run pytest only
make build        # Build standalone binary
make install      # Build and install to /usr/local/bin
make clean        # Clean build artifacts
make example      # Show usage examples
make all          # Clean, deps, build, and test
```

### Using uv for Development

#### Quick Start
```bash
# Clone and setup
git clone <repository-url>
cd jms2clash

# Development setup with uv
make dev
source .venv/bin/activate

# Or manually
uv venv
uv pip install -e ".[dev,build]"
```

#### Running with uv
```bash
# Install dependencies
uv pip install -e ".[dev]"          # Development dependencies
uv pip install -e ".[build]"        # Build dependencies  
uv pip install -e ".[dev,build]"    # All dependencies

# Run script
uv run python src/jms_to_clash.py --help

# Run tests
uv run pytest test_jms_to_clash.py -v

# Build binary
uv run pyinstaller --onefile src/jms_to_clash.py
```

### Testing
```bash
# Run comprehensive test suite
make test

# Run only pytest
make pytest

# Test Python script functionality
make test-python

# Run specific tests
uv run pytest test_jms_to_clash.py::TestProxyDecoders::test_decode_vmess -v
```

### Requirements
- **Python 3.8+**
- **uv** (modern Python package manager)
- **PyYAML** (installed via uv)
- **pytest** (for testing, installed via uv)
- **pyinstaller** (for building, installed via uv)

## Troubleshooting

### Common Issues

1. **uv not found**
   - Install uv: `curl -LsSf https://astral.sh/uv/install.sh | sh`
   - Or via homebrew: `brew install uv`
   - Restart terminal after installation

2. **"No input provided"**
   - Ensure data is piped to stdin
   - Use `uv run python src/jms_to_clash.py --help` for usage

3. **"No valid proxies found"**
   - Verify proxy URL formats
   - Check for proper base64 encoding
   - Run `make test` to verify functionality

4. **Build fails**
   - Ensure Python 3.8+ is installed
   - Run `make deps` to install dependencies
   - Check internet connection (downloads packages)

### Debug Mode
```bash
# Run with error output visible
jms2clash < input.txt 2>debug.log > config.yaml

# Validate YAML output
python3 -c "import yaml; yaml.safe_load(open('config.yaml'))"

# Development debug mode
uv run python src/jms_to_clash.py < input.txt 2>debug.log

# Check dependencies (development)
uv pip list
```

### Legacy pip Support
If you prefer pip over uv:
```bash
# Install with pip (not recommended)
python -m venv venv
source venv/bin/activate  
pip install -e ".[dev,build]"
```

## Compatibility

### Clash Clients
- ✅ Clash for Windows (CFW)
- ✅ ClashX (macOS)
- ✅ Clash for Android
- ✅ Clash Premium/Meta

### Operating Systems
- ✅ Windows 10/11 (x64)
- ✅ macOS 10.15+ (x64 & ARM64)
- ✅ Linux (x64, tested on Ubuntu 18.04+, CentOS 7+)

## Performance

- **Speed**: ~1000 proxies per second
- **Binary size**: ~7MB standalone
- **Memory usage**: ~50MB
- **Config size**: 50-200KB typical output

## Security Notes

- All processing is done locally
- No data sent to external servers
- DNS uses secure fallbacks (DoH/DoT)
- Includes `skip-cert-verify: true` for compatibility

## CLI Reference

```
usage: jms2clash [-h] [--version]

Convert JMS subscription strings to Clash configuration files

options:
  -h, --help  show this help message and exit
  --version   show program's version number and exit

Examples:
  jms2clash < subscription.txt > config.yaml
  echo "vmess://..." | jms2clash
  cat subscription.txt | jms2clash > clash_config.yaml
  curl -s "subscription-url" | jms2clash > config.yaml

Supported proxy formats:
  - VMess: vmess://...
  - VLESS: vless://...
  - Shadowsocks: ss://...
  - Trojan: trojan://...
  - Base64 encoded subscriptions
```

## Sample Output Structure

```yaml
port: 7890
socks-port: 7891
allow-lan: false
mode: rule
external-controller: 127.0.0.1:9090

dns:
  enable: true
  enhanced-mode: fake-ip
  nameserver:
    - 119.29.29.29
    - 223.5.5.5
  fallback:
    - https://dns.cloudflare.com/dns-query

proxies:
  - name: "Test Server"
    type: vmess
    server: example.com
    port: 443
    # ... proxy configuration

proxy-groups:
  - name: "🚀 节点选择"
    type: select
    proxies: ["♻️ 自动选择", "🎯 全球直连", "Test Server"]

rules:
  - GEOIP,CN,🎯 全球直连
  - DOMAIN-KEYWORD,google,🚀 节点选择
  - MATCH,🐟 漏网之鱼
```

## License

MIT License - Free to use and modify.

## Repository

This project is hosted at: https://github.com/skywardpixel/jms2clash

### Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Make your changes and test thoroughly
4. Commit your changes: `git commit -am 'Add new feature'`
5. Push to the branch: `git push origin feature/new-feature`
6. Submit a pull request

### Issues

Report bugs and request features at: https://github.com/skywardpixel/jms2clash/issues

---

## ✅ **Modern Python Project Summary**

This project uses **modern Python tooling** with clean separation of concerns:

### 📁 **Final Project Structure**
```
jms2clash/
├── src/jms_to_clash.py          # Pure conversion logic (275 lines)
├── test_jms_to_clash.py         # Comprehensive pytest tests (364 lines)  
├── pyproject.toml              # Modern Python packaging (118 lines)
├── Makefile                    # Build automation with uv (78 lines)
├── dev.py                      # Development helper script (139 lines)
├── .python-version             # Python version for uv (3.12)
└── README.md                   # This documentation
```

### 🚀 **Key Features**
- **Pure Python logic**: No testing/building code in main script
- **Professional testing**: 22 comprehensive pytest test cases
- **Modern packaging**: pyproject.toml standard
- **Fast tooling**: uv package manager (10-100x faster than pip)
- **Multiple interfaces**: Makefile, dev.py helper, direct uv commands

**Quick Commands Summary:**
```bash
# Setup and development
python3 dev.py setup                                         # One-time setup
make dev                                                     # Alternative setup
make test                                                    # Run all tests
make build                                                   # Build binary

# Daily usage  
uv run python src/jms_to_clash.py < input.txt > output.yaml # Convert with Python
cat input.txt | ./dist/jms2clash > output.yaml             # Convert with binary

# Development workflow
python3 dev.py demo                                          # Quick demo
uv run pytest -v                                           # Run tests
uv pip install -e ".[dev,build]"                           # Install all dependencies
```
