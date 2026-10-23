# Changelog

All notable changes to **Project Armadillo** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-10-23

### Added
- **Hybrid Post-Quantum Key Exchange:** Combining classical X25519 (ECDH) and quantum-resistant ML-KEM-768 (NIST FIPS 203).
- **Dual-Secret HKDF Extraction:** HKDF-SHA256 derivation of 256-bit AES-GCM session keys (`pq-hybrid-v1`).
- **Authenticated Encryption:** AES-256-GCM authenticated cipher with 12-byte CSPRNG nonces and 128-bit authentication tags.
- **Untrusted Blind Relay Server:** Pure TCP socket server routing encrypted opaque byte streams between endpoints.
- **Unrouted Handshake Buffering:** Automatic queueing and delivery of initial handshake payloads when peers join asynchronously.
- **Streamlit Interactive UI:** Full cryptographic visualization dashboard, real-time message telemetry, and chat interface in `Home.py` and `pages/1_Chat_Terminal.py`.
- **Sovereign Local AI:** Local Ollama Llama-3 inference endpoint (`bob_ai.py` / `bob_agent.py`) with zero outbound telemetry and graceful offline fallback.
- **LSB Image Steganography Module:** In-memory bit-level steganography tool (`stegno code.py`).
- **Comprehensive Automated Test Suite:** 13 unit tests covering cryptography, relay networking, Bob AI responder, and steganography.
- **Production DevOps Tooling:** GitHub Actions CI, Dependabot, Makefile, pre-commit config, and complete architectural documentation.

### Fixed
- Fixed unhandled handshake race condition in `server.py` where initial public keys were dropped if Alice connected before Bob.
- Fixed `ImportError` in `bob_agent.py` caused by missing `generate_response` function in `bob_ai.py`.
- Fixed port mismatch in `bob_agent.py` (changed from hardcoded 9999 to 5000 / configurable `RELAY_PORT`).
- Fixed infinite connection retry hang in `crypto_client.py` and added configurable `max_retries` and `close()` method.
- Fixed Streamlit `st.set_page_config` execution order in `pages/1_Chat_Terminal.py`.
- Added programmatic `encode_image` and `decode_image` functions in `stegno code.py` for automated testability.
- Fixed TCP packet coalescing and fragmentation failure by implementing 4-byte big-endian length-prefixed framing and exact TCP stream reassembly (`_recv_exact`) in `crypto_client.py`.
- Fixed false tamper triggers and socket death on multi-message rapid transmissions and messages exceeding 4KB.
- Fixed fatal socket termination on network tamper detection; invalid ciphertext now triggers an alert while maintaining session connection.
- Removed unused imports (`socket` in `bob_agent.py`, `hashlib` in `tests/test_crypto_client.py`) to ensure CI linter (`ruff check .`) passes cleanly.
- Resolved Pillow 12+ `DeprecationWarning` in `stegno code.py` by introducing `_get_pixel_data()` compatibility shim.
- Expanded automated test suite from 13 to 16 tests with multi-packet rapid streaming, 64KB payload reassembly, and network tamper resilience tests.
