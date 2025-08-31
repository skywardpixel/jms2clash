# Contributing to jms2clash

Thank you for your interest in contributing to jms2clash! This guide will help you get started with contributing to the project.

## Code of Conduct

By participating in this project, you are expected to uphold our Code of Conduct. Please report unacceptable behavior to the project maintainers.

## How to Contribute

### Reporting Bugs

Before creating bug reports, please check the issue list as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

- Use a clear and descriptive title
- Describe the exact steps which reproduce the problem
- Provide specific examples to demonstrate the steps
- Describe the behavior you observed after following the steps
- Explain which behavior you expected to see instead and why
- Include details about your configuration and environment

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

- Use a clear and descriptive title
- Provide a step-by-step description of the suggested enhancement
- Provide specific examples to demonstrate the steps
- Describe the current behavior and explain which behavior you expected to see instead
- Explain why this enhancement would be useful

### Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/YOUR-USERNAME/jms2clash.git
   cd jms2clash
   ```

2. **Set up development environment**
   ```bash
   # Install uv if you haven't already
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Setup development environment
   python3 dev.py setup
   # or
   make dev
   ```

3. **Activate virtual environment**
   ```bash
   source .venv/bin/activate
   ```

4. **Verify setup**
   ```bash
   python3 dev.py demo
   make test
   ```

### Development Workflow

1. **Create a branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following our coding standards:
   - Write clear, readable code
   - Add docstrings for functions and classes
   - Follow existing code style and patterns
   - Keep functions focused and modular

3. **Add tests** for new functionality:
   ```bash
   # Add tests to test_jms_to_clash.py
   # Run tests to ensure they pass
   make test
   ```

4. **Format and lint your code**:
   ```bash
   uv run black src/ test_jms_to_clash.py
   uv run ruff check src/ test_jms_to_clash.py
   ```

5. **Test thoroughly**:
   ```bash
   # Run full test suite
   make test
   
   # Test functionality
   python3 dev.py demo
   
   # Test binary build
   make build
   ```

6. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat: add support for new proxy protocol
   
   - Add decoder function for new protocol
   - Add comprehensive test cases
   - Update documentation"
   ```

7. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

8. **Create a Pull Request**

### Pull Request Process

1. **Before submitting**:
   - Ensure all tests pass
   - Update documentation if needed
   - Add entry to CHANGELOG.md if applicable
   - Ensure your code follows the project's coding standards

2. **Pull Request checklist**:
   - [ ] Tests pass locally
   - [ ] Code is properly formatted
   - [ ] Documentation is updated
   - [ ] CHANGELOG.md is updated (if applicable)
   - [ ] Commit messages are clear and descriptive

3. **Pull Request template**:
   ```
   ## Description
   Brief description of what this PR does.
   
   ## Type of Change
   - [ ] Bug fix (non-breaking change which fixes an issue)
   - [ ] New feature (non-breaking change which adds functionality)
   - [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
   - [ ] Documentation update
   
   ## Testing
   - [ ] I have added tests that prove my fix is effective or that my feature works
   - [ ] New and existing unit tests pass locally with my changes
   
   ## Checklist
   - [ ] My code follows the style guidelines of this project
   - [ ] I have performed a self-review of my own code
   - [ ] I have commented my code, particularly in hard-to-understand areas
   - [ ] I have made corresponding changes to the documentation
   - [ ] My changes generate no new warnings
   ```

### Coding Standards

#### Python Style
- Follow PEP 8 style guide
- Use Black for code formatting
- Use Ruff for linting
- Maximum line length: 88 characters
- Use type hints where appropriate

#### Code Organization
- **src/jms_to_clash.py**: Pure conversion logic only
- **test_jms_to_clash.py**: All tests using pytest
- **Makefile**: All build automation
- **dev.py**: Development helper commands

#### Function Guidelines
- Keep functions focused and small
- Use descriptive names
- Add docstrings for all public functions
- Handle errors gracefully
- Return None for invalid input rather than raising exceptions

#### Testing
- Write tests for all new functionality
- Use descriptive test names
- Test both valid and invalid inputs
- Aim for high test coverage
- Group related tests in classes

### Adding New Proxy Protocols

To add support for a new proxy protocol:

1. **Add decoder function**:
   ```python
   def decode_new_protocol(url: str) -> Optional[Dict[str, Any]]:
       """Decode new protocol URL to proxy config"""
       try:
           # Parse URL and extract configuration
           # Return standardized proxy config dictionary
           return {
               'name': 'Server Name',
               'type': 'new_protocol',
               'server': 'hostname',
               'port': 12345,
               # ... other protocol-specific fields
           }
       except Exception as e:
           print(f"Error decoding new protocol: {e}", file=sys.stderr)
           return None
   ```

2. **Update parse_subscription function**:
   ```python
   elif line.startswith('new_protocol://'):
       proxy = decode_new_protocol(line)
   ```

3. **Add comprehensive tests**:
   ```python
   def test_decode_new_protocol(self):
       """Test new protocol URL decoding"""
       url = "new_protocol://config_here"
       result = decode_new_protocol(url)
       
       assert result is not None
       assert result['type'] == 'new_protocol'
       # ... more assertions
   ```

4. **Update documentation**:
   - Add to README.md supported formats
   - Update examples
   - Add to CHANGELOG.md

### Project Structure

```
jms2clash/
├── .github/workflows/     # GitHub Actions CI/CD
├── src/jms_to_clash.py   # Core conversion logic
├── test_jms_to_clash.py  # Comprehensive test suite
├── dev.py                # Development helper script
├── pyproject.toml        # Modern Python packaging
├── Makefile              # Build automation
├── README.md             # Project documentation
├── CONTRIBUTING.md       # This file
├── CHANGELOG.md          # Release notes
├── LICENSE               # MIT License
└── .python-version       # Python version for uv
```

### Release Process

Releases are automated via GitHub Actions when tags are pushed:

1. **Prepare release**:
   - Update version in `pyproject.toml` and `src/jms_to_clash.py`
   - Update `CHANGELOG.md` with new version
   - Commit changes

2. **Create and push tag**:
   ```bash
   git tag v0.2.0
   git push origin v0.2.0
   ```

3. **Automated process**:
   - GitHub Actions will run tests
   - Build binaries for all platforms
   - Create GitHub release
   - Publish to PyPI (if configured)

### Getting Help

- Check existing issues and discussions
- Join project discussions
- Ask questions in pull requests
- Contact maintainers via GitHub

### Recognition

Contributors will be recognized in:
- CHANGELOG.md for significant contributions
- GitHub contributors list
- Release notes for major features

Thank you for contributing to jms2clash! 🎉