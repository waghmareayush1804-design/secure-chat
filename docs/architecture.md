# Project Armadillo: Architectural Specification

## 1. Executive Overview

**Project Armadillo** is an end-to-end encrypted, zero-knowledge communications architecture engineered to defend against **Harvest Now, Decrypt Later (HNDL)** adversary operations. By establishing a dual-secret hybrid key exchange combining classical elliptic curves (**X25519**) and lattice-based post-quantum cryptography (**ML-KEM-768 / FIPS 203**), Armadillo ensures that intercepted ciphertexts remain computationally infeasible to decrypt by both classical computers and future Cryptographically Relevant Quantum Computers (CRQCs).

---

## 2. Zero-Knowledge Topology

```mermaid
graph LR
    subgraph ClientEndpointA["Endpoint A: Alice (Initiator)"]
        A_UI["Streamlit UI (Port 8501)"]
        A_KEM["Hybrid KEM Engine\n(X25519 + ML-KEM-768)"]
        A_CIPHER["AES-256-GCM\nAuthenticated Engine"]
        A_UI --> A_CIPHER
        A_KEM --> A_CIPHER
    end

    subgraph Relay["Untrusted Transport Plane"]
        ROUTER["Zero-Knowledge TCP Relay\n(server.py : Port 5000)\n- Blind Byte Routing\n- Unrouted Handshake Queue\n- Zero Access to Keys/Plaintext"]
    end

    subgraph ClientEndpointB["Endpoint B: Bob (Responder)"]
        B_CIPHER["AES-256-GCM\nAuthenticated Engine"]
        B_KEM["Hybrid KEM Engine\n(X25519 + ML-KEM-768)"]
        B_AI["Sovereign Local AI\n(Ollama Llama-3 @ 127.0.0.1)\n- Air-gapped / No External WAN\n- Volatile memory zeroization"]
        B_CIPHER --> B_AI
        B_KEM --> B_CIPHER
    end

    A_CIPHER <== "Opaque TLS/TCP Bytes" ==> ROUTER
    ROUTER <== "Opaque TLS/TCP Bytes" ==> B_CIPHER
```

---

## 3. Cryptographic Key Exchange Sequence

```mermaid
sequenceDiagram
    autonumber
    participant Alice as Alice (Initiator)
    participant Relay as Blind TCP Relay
    participant Bob as Bob (Responder)

    Note over Alice: Generate X25519 priv/pub (32B)<br/>Generate ML-KEM-768 priv/pub (1184B)
    Alice->>Relay: alice_x25519_pub (32B) + alice_mlkem_pub (1184B) = 1216 Bytes
    Note over Relay: If Bob offline, buffer 1216B.<br/>When Bob connects, deliver immediately.
    Relay->>Bob: Deliver Alice's Public Keys (1216 Bytes)

    Note over Bob: Generate Bob X25519 priv/pub (32B)<br/>Encapsulate ML-KEM secret using Alice's pubkey<br/>Outputs: pq_secret (32B) + mlkem_ciphertext (1088B)<br/>Derive classical_secret via X25519 exchange (32B)
    Bob->>Relay: bob_x25519_pub (32B) + mlkem_ciphertext (1088B) = 1120 Bytes
    Relay->>Alice: Forward Bob's Response (1120 Bytes)

    Note over Alice: Decapsulate pq_secret from mlkem_ciphertext<br/>Derive classical_secret via X25519 exchange

    rect rgb(230, 245, 255)
        Note over Alice,Bob: Symmetric Key Derivation (HKDF-SHA256)
        Note over Alice: combined_secrets = classical_secret (32B) + pq_secret (32B) = 64B<br/>aes_key = HKDF-SHA256(secret=combined_secrets, info="pq-hybrid-v1", len=32)
        Note over Bob: combined_secrets = classical_secret (32B) + pq_secret (32B) = 64B<br/>aes_key = HKDF-SHA256(secret=combined_secrets, info="pq-hybrid-v1", len=32)
    end
```

---

## 4. Packet Framing and Authenticated Encryption

Every application payload transmitted across the relay is framed with a 4-byte big-endian length prefix and sealed with **AES-256-GCM** (Galois/Counter Mode).

### Packet Wire Format
```
+--------------------+-------------------+-------------------------------+---------------------+
| Length (4B BigEnd) |  Nonce (12 Bytes) |  Ciphertext (Variable Length)  | Auth Tag (16 Bytes) |
+--------------------+-------------------+-------------------------------+---------------------+
```

1. **Length-Prefixed Framing (`>I`):** Guarantees deterministic TCP byte-stream reassembly across high-latency WAN links, preventing packet coalescing and fragmentation desynchronization.
2. **Nonce Generation:** A fresh, cryptographically secure random 96-bit (12-byte) initialization vector is generated for every transmission using the operating system CSPRNG (`os.urandom(12)`).
3. **GHASH Integrity Tag:** The 128-bit authentication tag guarantees confidentiality and authenticity. Any modification in transit triggers immediate client-side rejection and a tamper alert without killing the client socket loop.
4. **Replay & Malleability Resistance:** Because nonces are unique and tags are strictly verified prior to plaintext decoding, ciphertext manipulation is detected with overwhelming probability ($1 - 2^{-128}$).

---

## 5. Component Responsibilities

| Component | File | Responsibilities |
|---|---|---|
| **Streamlit UI** | [`Home.py`](file:///home/ayushwaghmare/secure-chat/Home.py), [`pages/1_Chat_Terminal.py`](file:///home/ayushwaghmare/secure-chat/pages/1_Chat_Terminal.py) | Human operator interface, cryptographic session telemetry display, real-time message exchange, connection state indicator. |
| **Crypto Client** | [`crypto_client.py`](file:///home/ayushwaghmare/secure-chat/crypto_client.py) | Key pair generation, encapsulation/decapsulation, HKDF extraction, AES-GCM encryption/decryption, background socket receive thread. |
| **Blind TCP Relay** | [`server.py`](file:///home/ayushwaghmare/secure-chat/server.py) | Stateless/opaque packet routing, connection isolation, unrouted handshake queueing for asynchronous peer arrival. |
| **Headless AI Responder** | [`bob_ai.py`](file:///home/ayushwaghmare/secure-chat/bob_ai.py), [`bob_agent.py`](file:///home/ayushwaghmare/secure-chat/bob_agent.py) | Automated autonomous endpoint with local Ollama Llama-3 integration and graceful offline fallback. |
| **LSB Steganography** | [`stegno code.py`](file:///home/ayushwaghmare/secure-chat/stegno%20code.py) | In-memory and file-based LSB image encoding and decoding for covert data storage. |
