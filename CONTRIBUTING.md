# Contributing to Project Armadillo

Thank you for your interest in contributing to **Project Armadillo: Post-Quantum Zero-Knowledge Communications**!

## Development Setup

### 1. Prerequisites
- Python 3.11, 3.12, 3.13, or 3.14
- Git 2.30+
- (Optional) [Ollama](https://ollama.com/) with `llama3` pulled (`ollama pull llama3`) for local AI responder testing.

### 2. Clone and Initialize Virtual Environment
```bash
git clone https://github.com/waghmareayush1804-design/secure-chat.git
cd secure-chat
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

### 3. Verify Local Installation
```bash
make test
make lint
```

## Running the Application Locally

1. **Terminal 1 - Relay Router:**
   ```bash
   ./scripts/run_relay.sh
   # Or: python3 server.py
   ```

2. **Terminal 2 - Bob AI Endpoint:**
   ```bash
   ./scripts/run_bob.sh
   # Or: python3 bob_ai.py
   ```

3. **Terminal 3 - Alice UI (Streamlit):**
   ```bash
   ./scripts/run_alice.sh
   # Or: streamlit run Home.py
   ```

## Development Standards

### Code Style
- Follow PEP 8 and use LF line endings.
- Run `make lint` before opening a pull request.
- Ensure all public functions have clear, accurate docstrings.

### Cryptographic Guidelines
- Never modify or bypass cryptographic primitives without explicit review and RFC/FIPS citations.
- Nonces for AES-256-GCM must never be reused; use `os.urandom(12)`.
- Never log private keys, raw shared secrets, or plaintext messages in server logs or terminal traces.

### Automated Testing
- All new features and bug fixes must include unit tests under `tests/`.
- Run the full test suite with:
  ```bash
  make test
  ```

## Git Commit Conventions

We follow Conventional Commits:
- `feat: add post-quantum signature verification`
- `fix: resolve handshake race condition in blind relay`
- `docs: update cryptographic architecture specification`
- `test: add unit tests for corrupted tag detection`
- `refactor: modularize steganography encoding`

## Pull Request Process

1. Create a feature branch: `git checkout -b feat/your-feature-name`.
2. Commit your changes following commit message conventions.
3. Ensure all tests and lint checks pass (`make test && make lint`).
4. Submit your pull request using the provided PR template.
