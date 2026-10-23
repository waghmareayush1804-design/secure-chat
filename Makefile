.PHONY: help install install-dev test lint format run-relay run-alice run-bob clean

PYTHON ?= python3

help:
	@echo "Project Armadillo - Make Targets"
	@echo "  make install        Install direct production dependencies"
	@echo "  make install-dev    Install development and testing dependencies"
	@echo "  make test           Run automated test suite"
	@echo "  make lint           Check code with ruff (if installed) or py_compile"
	@echo "  make format         Format code with ruff / black"
	@echo "  make run-relay      Start the zero-knowledge TCP relay"
	@echo "  make run-alice      Launch Alice's Streamlit frontend"
	@echo "  make run-bob        Launch Bob's AI responder endpoint"
	@echo "  make clean          Remove cache and test artifacts"

install:
	$(PYTHON) -m pip install -r requirements.txt

install-dev:
	$(PYTHON) -m pip install -r requirements-dev.txt

test:
	./scripts/run_tests.sh

lint:
	$(PYTHON) -m py_compile Home.py pages/1_Chat_Terminal.py crypto_client.py server.py bob_agent.py bob_ai.py "stegno code.py"
	@if command -v ruff >/dev/null 2>&1; then ruff check .; else echo "ruff not found, syntax compilation verified."; fi

format:
	@if command -v ruff >/dev/null 2>&1; then ruff format .; elif command -v black >/dev/null 2>&1; then black .; else echo "No formatter installed."; fi

run-relay:
	./scripts/run_relay.sh

run-alice:
	./scripts/run_alice.sh

run-bob:
	./scripts/run_bob.sh

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .coverage htmlcov .ruff_cache
