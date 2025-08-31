#!/bin/bash

# JMS to Clash Converter - Installation Script
# This script downloads and installs the latest release of jms2clash

set -e

# Configuration
REPO="skywardpixel/jms2clash"
INSTALL_DIR="${INSTALL_DIR:-/usr/local/bin}"
BINARY_NAME="jms2clash"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

success() {
    echo -e "${GREEN}✅${NC} $1"
}

warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

error() {
    echo -e "${RED}❌${NC} $1"
    exit 1
}

# Detect platform
detect_platform() {
    local os=$(uname -s)
    local arch=$(uname -m)

    case "$os" in
        Linux*)
            case "$arch" in
                x86_64) echo "linux-x64" ;;
                *) error "Unsupported Linux architecture: $arch" ;;
            esac
            ;;
        Darwin*)
            case "$arch" in
                x86_64) echo "macos-x64" ;;
                arm64) echo "macos-arm64" ;;
                *) error "Unsupported macOS architecture: $arch" ;;
            esac
            ;;
        CYGWIN*|MINGW*|MSYS*)
            echo "windows-x64"
            ;;
        *)
            error "Unsupported operating system: $os"
            ;;
    esac
}

# Get latest release info
get_latest_release() {
    info "Fetching latest release information..."

    if command -v curl >/dev/null 2>&1; then
        curl -s "https://api.github.com/repos/$REPO/releases/latest"
    elif command -v wget >/dev/null 2>&1; then
        wget -qO- "https://api.github.com/repos/$REPO/releases/latest"
    else
        error "Neither curl nor wget is available. Please install one of them."
    fi
}

# Download and install
install_binary() {
    local platform=$(detect_platform)
    local temp_dir=$(mktemp -d)

    info "Detected platform: $platform"
    info "Installing to: $INSTALL_DIR"

    # Get release information
    local release_info=$(get_latest_release)
    local tag_name=$(echo "$release_info" | grep '"tag_name":' | sed -E 's/.*"tag_name": "([^"]+)".*/\1/')

    if [ -z "$tag_name" ]; then
        error "Failed to get latest release information"
    fi

    success "Found latest release: $tag_name"

    # Determine download URL and file extension
    local file_ext
    local extract_cmd

    if [[ "$platform" == "windows-x64" ]]; then
        file_ext="zip"
        extract_cmd="unzip -q"
    else
        file_ext="tar.gz"
        extract_cmd="tar -xzf"
    fi

    local download_url="https://github.com/$REPO/releases/download/$tag_name/jms2clash-$platform.$file_ext"
    local archive_file="$temp_dir/jms2clash-$platform.$file_ext"

    info "Downloading from: $download_url"

    # Download the archive
    if command -v curl >/dev/null 2>&1; then
        curl -L "$download_url" -o "$archive_file" --progress-bar
    elif command -v wget >/dev/null 2>&1; then
        wget --progress=bar:force "$download_url" -O "$archive_file"
    else
        error "Neither curl nor wget is available"
    fi

    if [ ! -f "$archive_file" ]; then
        error "Download failed"
    fi

    success "Download completed"

    # Extract the archive
    info "Extracting archive..."
    cd "$temp_dir"
    $extract_cmd "$archive_file"

    # Find the binary
    local binary_path
    if [[ "$platform" == "windows-x64" ]]; then
        binary_path=$(find . -name "jms2clash.exe" | head -1)
    else
        binary_path=$(find . -name "jms2clash" -type f | head -1)
    fi

    if [ -z "$binary_path" ]; then
        error "Binary not found in archive"
    fi

    # Create install directory if it doesn't exist
    if [ ! -d "$INSTALL_DIR" ]; then
        info "Creating install directory: $INSTALL_DIR"
        sudo mkdir -p "$INSTALL_DIR" 2>/dev/null || mkdir -p "$INSTALL_DIR"
    fi

    # Install the binary
    local install_path="$INSTALL_DIR/$BINARY_NAME"
    if [[ "$platform" == "windows-x64" ]]; then
        install_path="$INSTALL_DIR/$BINARY_NAME.exe"
    fi

    info "Installing binary to: $install_path"

    if [ -w "$INSTALL_DIR" ]; then
        cp "$binary_path" "$install_path"
        chmod +x "$install_path" 2>/dev/null || true
    else
        sudo cp "$binary_path" "$install_path"
        sudo chmod +x "$install_path"
    fi

    # Cleanup
    rm -rf "$temp_dir"

    success "Installation completed!"

    # Verify installation
    if command -v "$BINARY_NAME" >/dev/null 2>&1; then
        local version=$("$BINARY_NAME" --version 2>&1 | head -1)
        success "Installed version: $version"
    else
        warn "Binary installed but not in PATH. You may need to add $INSTALL_DIR to your PATH."
        echo "  export PATH=\"$INSTALL_DIR:\$PATH\""
    fi
}

# Uninstall function
uninstall_binary() {
    local install_path="$INSTALL_DIR/$BINARY_NAME"

    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
        install_path="$INSTALL_DIR/$BINARY_NAME.exe"
    fi

    if [ -f "$install_path" ]; then
        info "Removing $install_path"
        if [ -w "$INSTALL_DIR" ]; then
            rm "$install_path"
        else
            sudo rm "$install_path"
        fi
        success "Uninstalled successfully"
    else
        warn "Binary not found at $install_path"
    fi
}

# Show usage
usage() {
    echo "JMS to Clash Converter - Installation Script"
    echo
    echo "Usage: $0 [OPTIONS]"
    echo
    echo "Options:"
    echo "  install      Install or update jms2clash (default)"
    echo "  uninstall    Remove jms2clash"
    echo "  --dir DIR    Set installation directory (default: /usr/local/bin)"
    echo "  --help       Show this help message"
    echo
    echo "Environment variables:"
    echo "  INSTALL_DIR  Installation directory (default: /usr/local/bin)"
    echo
    echo "Examples:"
    echo "  $0                           # Install to /usr/local/bin"
    echo "  $0 --dir ~/.local/bin        # Install to ~/.local/bin"
    echo "  INSTALL_DIR=~/bin $0         # Install using environment variable"
    echo "  $0 uninstall                 # Remove jms2clash"
}

# Main execution
main() {
    local action="install"

    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            install)
                action="install"
                shift
                ;;
            uninstall)
                action="uninstall"
                shift
                ;;
            --dir)
                INSTALL_DIR="$2"
                shift 2
                ;;
            --help|-h)
                usage
                exit 0
                ;;
            *)
                error "Unknown option: $1. Use --help for usage information."
                ;;
        esac
    done

    # Check for required tools
    if ! command -v curl >/dev/null 2>&1 && ! command -v wget >/dev/null 2>&1; then
        error "Either curl or wget is required for installation"
    fi

    if [[ "$action" == "install" ]]; then
        if ! command -v tar >/dev/null 2>&1 && [[ "$(detect_platform)" != "windows-x64" ]]; then
            error "tar is required for installation on Unix systems"
        fi
        if ! command -v unzip >/dev/null 2>&1 && [[ "$(detect_platform)" == "windows-x64" ]]; then
            error "unzip is required for installation on Windows systems"
        fi
    fi

    # Execute action
    case $action in
        install)
            install_binary
            echo
            info "Quick start:"
            echo "  curl -s \"https://your-subscription-url\" | $BINARY_NAME > config.yaml"
            echo "  $BINARY_NAME < subscription.txt > config.yaml"
            echo
            info "For more information, visit: https://github.com/$REPO"
            ;;
        uninstall)
            uninstall_binary
            ;;
        *)
            error "Unknown action: $action"
            ;;
    esac
}

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
