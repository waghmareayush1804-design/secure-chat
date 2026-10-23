# Developer Guide

Welcome to the development guide for **Project Armadillo**.

## 1. Environment Setup

### Prerequisites
- Python 3.11+
- Git

### Virtual Environment Configuration
```bash
git clone https://github.com/waghmareayush1804-design/secure-chat.git
cd secure-chat

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

---

## 2. Running Automated Tests

The test suite runs with either standard library `unittest` or `pytest`:

```bash
# Run using the Makefile:
make test

# Or run using the wrapper script:
./scripts/run_tests.sh

# Or directly with Python unittest:
python3 -m unittest discover -s tests -p "test_*.py" -v

# Or with pytest (if installed):
pytest -v tests/
```

### Test Organization
- [`tests/test_crypto_client.py`](file:///home/ayushwaghmare/secure-chat/tests/test_crypto_client.py): Verifies X25519, ML-KEM-768, HKDF derivation, AES-GCM encryption/decryption, and tamper detection.
- [`tests/test_server.py`](file:///home/ayushwaghmare/secure-chat/tests/test_server.py): Tests TCP relay routing, asynchronous client buffering, and socket disconnect resiliency.
- [`tests/test_bob_agent.py`](file:///home/ayushwaghmare/secure-chat/tests/test_bob_agent.py): Tests headless AI responder, fallback behavior when Ollama is offline, and retry handling.
- [`tests/test_steganography.py`](file:///home/ayushwaghmare/secure-chat/tests/test_steganography.py): Tests bit-level LSB steganography roundtrips and input validation.

---

## 3. Code Formatting and Linting

We enforce strict Python syntax and style:

```bash
# Compile and lint:
make lint

# Automatically format:
make format
```

---

## 4. Architecture Conventions

1. **Deterministic Wire Sizing:**
   - Alice Public Handshake: `32 bytes (X25519) + 1184 bytes (ML-KEM-768) = 1216 bytes`.
   - Bob Public Handshake: `32 bytes (X25519) + 1088 bytes (ML-KEM-768 Ciphertext) = 1120 bytes`.
   - Data Packets: `12 bytes (Nonce) + N bytes (Ciphertext) + 16 bytes (Auth Tag)`.
2. **Zero-Knowledge Principle:**
   - Never inspect or parse plaintext inside [`server.py`](file:///home/ayushwaghmare/secure-chat/server.py). The relay must remain an opaque byte transport.
3. **Telemetry & Secrets:**
   - Truncated SHA-256 fingerprints may be exposed in UI telemetry (for key verification), but private keys and unhashed session keys must never be logged.
