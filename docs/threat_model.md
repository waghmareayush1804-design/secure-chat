# Threat Model & Cryptographic Hardness Analysis

## 1. The Threat: Harvest Now, Decrypt Later (HNDL)

Global intelligence agencies and well-resourced adversaries routinely intercept and store high volumes of encrypted network traffic. Although classical encryption schemes (such as RSA-2048, ECDH Curve25519, and Diffie-Hellman) are currently resilient to classical computational power, they are fundamentally vulnerable to quantum computation.

When a **Cryptographically Relevant Quantum Computer (CRQC)** is developed, an adversary will be able to run **Shor's Algorithm** to compute discrete logarithms and factor prime products in polynomial time $\mathcal{O}((\log N)^3)$. All archived classical sessions will instantly be compromised retroactively.

---

## 2. Dual-Layer Defense: Hybrid Key Exchange

Project Armadillo employs a hybrid cryptographic model:
$$\text{Shared Secret} = \text{HKDF-Extract}(\text{Secret}_{\text{X25519}} \mathbin{\Vert} \text{Secret}_{\text{ML-KEM-768}})$$

### Defense-in-Depth Guarantee
1. **If ML-KEM-768 is theoretically broken by an unforeseen classical lattice reduction:** The classical X25519 Diffie-Hellman secret guarantees that classical adversaries cannot read the traffic.
2. **If X25519 is broken by Shor's algorithm on a quantum computer:** The post-quantum ML-KEM-768 secret guarantees that the quantum adversary cannot derive the symmetric session key.
3. **To break the session key, an adversary must simultaneously break both Curve25519 and Module-LWE.**

---

## 3. Cryptographic Primitives

### 1. ML-KEM-768 (NIST FIPS 203)
- **Mathematical Hardness:** Module Learning With Errors ($M\text{-LWE}$) problem over high-dimensional polynomial rings $\mathbb{Z}_q[X]/(X^{256} + 1)$.
- **Security Strength:** NIST Security Category 3 (equivalent to AES-192 in classical brute-force hardness and $\ge 128$-bit quantum security).
- **Public Key Size:** 1,184 bytes.
- **Ciphertext Size:** 1,088 bytes.
- **Shared Secret Size:** 32 bytes (256 bits).
- **Resistance to Shor's Algorithm:** Lattice Shortest Vector Problems (SVP) lack the periodic Abelian hidden subgroup structure that Shor's algorithm exploits.

### 2. X25519 (RFC 7748)
- **Curve:** Montgomery curve $y^2 = x^3 + 486662x^2 + x$ over prime field $\mathbb{F}_{2^{255}-19}$.
- **Security:** 128-bit classical security against known attacks.
- **Side-Channel Immunity:** Uses data-independent constant-time Montgomery ladder computation, eliminating cache-timing and branch-prediction vulnerabilities.

### 3. AES-256-GCM (NIST SP 800-38D)
- **Cipher Key Length:** 256 bits.
- **Grover's Algorithm Hardness:** Grover's algorithm provides a quadratic speedup against symmetric key searches ($\mathcal{O}(\sqrt{N})$). AES-256 retains $\ge 128$ bits of effective security against quantum search algorithms, meeting all post-quantum security requirements.
- **Authentication:** 128-bit GHASH authentication tag over Galois Field $\text{GF}(2^{128})$ verifies ciphertext integrity and protects against bit-flipping attacks.

---

## 4. Trust Boundaries & Attack Vectors

```
[ Alice (Untrusted WAN/LAN) ]
              │
              ▼
[ Blind TCP Relay Server ]  <-- Untrusted Host / Compromised Router
              │
              ▼
[ Bob Endpoint (Local Air-Gapped AI) ]
```

| Attack Vector | Adversary Capability | Armadillo Defense Mechanism |
|---|---|---|
| **Eavesdropping on Relay** | Adversary captures all bytes passing through `server.py`. | **Immune:** Only opaque ciphertext with random nonces is routed; key exchange is encrypted/encapsulated. |
| **Tampering / Packet Modification** | Router modifies bytes in flight or injects data. | **Detected:** AES-GCM 128-bit tag fails authentication; client rejects corrupt payload, logs tamper alert, and preserves socket loop. |
| **Harvest Now, Decrypt Later** | Adversary records session for 20 years to decrypt with CRQC. | **Protected:** ML-KEM-768 lattice secret protects the derived AES key from Shor's algorithm. |
| **Cloud Prompt Leakage** | Corporate AI model transmits chat logs to cloud providers. | **Eliminated:** Local Ollama model runs strictly on `127.0.0.1` with no WAN network telemetry. |
