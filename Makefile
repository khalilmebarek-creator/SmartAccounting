# Accounting Platform - Development Commands
# ===========================================
# Usage: make <command>

.PHONY: install install-dev test test-cov lint format typecheck run clean help

PYTHON = python
PIP = pip
VENV = .venv
VENV_PYTHON = $(VENV)/Scripts/python.exe
VENV_PIP = $(VENV)/Scripts/pip.exe

help: ## Show this help
	@echo "Accounting Platform - Available Commands:"
	@echo "=========================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install production dependencies
	$(VENV_PIP) install -r requirements.txt

install-dev: ## Install all dependencies (production + dev)
	$(VENV_PIP) install -r requirements-dev.txt

test: ## Run all tests
	$(VENV_PYTHON) -m pytest tests/ -v

test-cov: ## Run tests with coverage report
	$(VENV_PYTHON) -m pytest tests/ -v --cov=modules --cov=database --cov=ui --cov=utils --cov-report=html

lint: ## Run linter (ruff)
	$(VENV_PYTHON) -m ruff check .

format: ## Auto-format code
	$(VENV_PYTHON) -m ruff format .

typecheck: ## Run type checker
	$(VENV_PYTHON) -m mypy .

run: ## Run the GUI application
	$(VENV_PYTHON) ui/run_ui.py

cli: ## Run the CLI version
	$(VENV_PYTHON) main.py

clean: ## Clean build artifacts
	-rmdir /s /q build dist *.egg-info 2>nul
	-del /q *.pyc 2>nul
	-rmdir /s /q __pycache__ 2>nul
	-rmdir /s /q .pytest_cache 2>nul
	-rmdir /s /q htmlcov 2>nul
	-rmdir /s /q .mypy_cache 2>nul
	@echo "Cleaned!"
