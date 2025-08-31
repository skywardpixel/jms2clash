#!/usr/bin/env python3
"""
Development helper script for jms2clash
Provides easy commands for development tasks using uv
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    """Run a command and print status"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(e.stderr)
        sys.exit(1)

def setup():
    """Setup development environment"""
    print("Setting up development environment with uv...")

    # Check if uv is installed
    try:
        subprocess.run(["uv", "--version"], check=True, capture_output=True)
        print("✅ uv is available")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ uv not found. Installing...")
        run_command("curl -LsSf https://astral.sh/uv/install.sh | sh", "Installing uv")
        print("💡 Please restart your terminal and run this script again")
        sys.exit(0)

    # Create virtual environment
    run_command("uv venv", "Creating virtual environment")

    # Install dependencies
    run_command("uv pip install -e '.[dev,build]'", "Installing dependencies from pyproject.toml")

    print("\n🎉 Development environment ready!")
    print("💡 Activate with: source .venv/bin/activate")

def test():
    """Run tests"""
    run_command("uv run pytest test_jms_to_clash.py -v", "Running tests")

def build():
    """Build binary"""
    run_command("uv run pyinstaller --onefile --name jms2clash --console src/jms_to_clash.py", "Building binary")

def format_code():
    """Format code with black"""
    run_command("uv run black src/ test_jms_to_clash.py", "Formatting code")

def lint():
    """Lint code with ruff"""
    run_command("uv run ruff check src/ test_jms_to_clash.py", "Linting code")

def demo():
    """Run demo conversion"""
    print("🚀 Running demo conversion...")
    test_data = "vmess://eyJhZGQiOiJleGFtcGxlLmNvbSIsImFpZCI6IjAiLCJpZCI6InRlc3QiLCJuZXQiOiJ0Y3AiLCJwb3J0IjoiNDQzIiwicHMiOiJUZXN0Iiwic2N5IjoiYXV0byIsInRscyI6InRscyIsInYiOiIyIn0="

    cmd = f'echo "{test_data}" | uv run python src/jms_to_clash.py | head -20'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if result.returncode == 0:
        print("✅ Demo conversion successful!")
        print("\nSample output:")
        print("-" * 40)
        print(result.stdout)
    else:
        print("❌ Demo conversion failed:")
        print(result.stderr)
        sys.exit(1)

def clean():
    """Clean build artifacts"""
    artifacts = ["dist", "build", "*.spec", ".pytest_cache", "__pycache__"]
    for artifact in artifacts:
        if Path(artifact).exists():
            run_command(f"rm -rf {artifact}", f"Removing {artifact}")
    print("✅ Cleaned build artifacts")

def show_help():
    """Show help"""
    print("""
jms2clash - Development Helper

Usage: python dev.py <command>

Commands:
  setup     Setup development environment with uv
  test      Run pytest test suite
  build     Build standalone binary
  format    Format code with black
  lint      Lint code with ruff
  demo      Run demo conversion
  clean     Clean build artifacts
  help      Show this help

Examples:
  python dev.py setup     # First time setup
  python dev.py test      # Run tests
  python dev.py demo      # See it work
  python dev.py build     # Create binary
""")

def main():
    if len(sys.argv) != 2:
        show_help()
        sys.exit(1)

    command = sys.argv[1].lower()

    commands = {
        "setup": setup,
        "test": test,
        "build": build,
        "format": format_code,
        "lint": lint,
        "demo": demo,
        "clean": clean,
        "help": show_help,
    }

    if command not in commands:
        print(f"❌ Unknown command: {command}")
        show_help()
        sys.exit(1)

    commands[command]()

if __name__ == "__main__":
    main()
