.PHONY: build test clean help install deps

PYTHON := python3
SCRIPT := src/jms_to_clash.py
BINARY := dist/jms2clash
TEST_FILE := test_jms_to_clash.py

help: ## Show available commands
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

install-uv: ## Install uv package manager
	@command -v uv >/dev/null 2>&1 || { \
		echo "Installing uv..."; \
		curl -LsSf https://astral.sh/uv/install.sh | sh; \
	}

deps: install-uv ## Install Python dependencies
	uv pip install -e ".[dev,build]"

build: deps ## Build standalone binary
	@echo "Building standalone binary..."
	uv run pyinstaller --onefile \
		--name jms2clash \
		--distpath dist \
		--workpath build \
		--specpath . \
		--console \
		$(SCRIPT)
	@if [ -f $(BINARY) ]; then \
		echo "✅ Binary built successfully: $(BINARY)"; \
		echo "📦 Binary size: $$(du -h $(BINARY) | cut -f1)"; \
	else \
		echo "❌ Build failed"; \
		exit 1; \
	fi

test: deps ## Run all tests
	@echo "Running pytest test suite..."
	uv run pytest $(TEST_FILE) -v
	@echo ""
	@echo "Testing binary functionality..."
	@if [ -f $(BINARY) ]; then \
		echo "vmess://eyJhZGQiOiJleGFtcGxlLmNvbSIsImFpZCI6IjAiLCJpZCI6InRlc3QiLCJuZXQiOiJ0Y3AiLCJwb3J0IjoiNDQzIiwicHMiOiJUZXN0Iiwic2N5IjoiYXV0byIsInRscyI6InRscyIsInYiOiIyIn0=" | $(BINARY) > /dev/null && echo "✅ Binary test passed" || echo "❌ Binary test failed"; \
	else \
		echo "⚠️  Binary not found, run 'make build' first"; \
	fi

test-python: deps ## Run tests with Python script
	@echo "Testing Python script functionality..."
	@echo "vmess://eyJhZGQiOiJleGFtcGxlLmNvbSIsImFpZCI6IjAiLCJpZCI6InRlc3QiLCJuZXQiOiJ0Y3AiLCJwb3J0IjoiNDQzIiwicHMiOiJUZXN0Iiwic2N5IjoiYXV0byIsInRscyI6InRscyIsInYiOiIyIn0=" | uv run python $(SCRIPT) > /dev/null && echo "✅ Python script test passed" || echo "❌ Python script test failed"

pytest: deps ## Run pytest only
	uv run pytest $(TEST_FILE) -v

install: build ## Build and install to /usr/local/bin
	sudo cp $(BINARY) /usr/local/bin/jms2clash
	@echo "✅ Installed to /usr/local/bin/jms2clash"

clean: ## Clean build artifacts
	rm -rf dist build *.spec
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete
	rm -rf .pytest_cache

example: ## Show example usage
	@echo "Examples:"
	@echo "  uv run python $(SCRIPT) < subscription.txt > config.yaml"
	@echo "  cat subscription.txt | uv run python $(SCRIPT) > config.yaml"
	@echo "  echo 'vmess://...' | uv run python $(SCRIPT)"
	@echo "  echo 'vmess://...' | ./$(BINARY)  # After building"

all: clean deps build test ## Clean, install deps, build, and test
	@echo "🎉 All tasks completed successfully!"

dev: install-uv ## Setup development environment
	uv venv
	uv pip install -e ".[dev,build]"
	@echo "✅ Development environment ready"
	@echo "💡 Activate with: source .venv/bin/activate"
