# Security Policy

## Supported Versions

Only the latest commit on the `master` branch is currently actively supported with security updates.

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |
| < 0.1.0 | :x:                |

## Cryptographic Architecture & Threat Scope

Project Armadillo implements a hybrid post-quantum cryptographic scheme designed to counter **Harvest Now, Decrypt Later (HNDL)** attacks:

1. **Key Encapsulation:** NIST FIPS 203 ML-KEM-768 lattice-based KEM combined with classical X25519 ECDH.
2. **Key Derivation:** HKDF-SHA256 (`info=b"pq-hybrid-v1"`).
3. **Payload Encryption:** AES-256-GCM with fresh 12-byte nonces generated via OS CSPRNG (`os.urandom(12)`).
4. **Relay Trust Model:** The TCP router is an **untrusted, blind relay**. It handles opaque byte streams without session keys or access to plaintext.
5. **AI Inference Isolation:** Bob's AI model runs strictly on localhost (Ollama) with zero external network telemetry.

### Out-of-Scope Security Reports

The following are outside the threat model and will not be considered vulnerabilities:
- Attacks requiring physical access or root access to a compromised endpoint device.
- Denial of Service (DoS) attacks on the local loopback TCP port.
- Side-channel timing attacks on non-constant-time host hardware environments.

## Reporting a Vulnerability

We take the security of cryptographic software seriously. If you identify a security flaw, vulnerability, or potential exploit:

1. **Private GitHub Advisory (Recommended):** Please report the issue via GitHub's private vulnerability reporting feature under **Security > Advisories > Report a vulnerability**.
2. **Direct Contact:** If GitHub Private Reporting is unavailable, contact the project maintainer directly at: `ayush.waghmare.bsc2025@saii.siu.edu.in`.

Please **do not** file public GitHub issues for security vulnerabilities.

### What to Include

Please provide:
- A detailed description of the vulnerability.
- Steps to reproduce or proof-of-concept (PoC) code.
- Cryptographic analysis of the failure mode (e.g. key leakage, ciphertext malleability, replay vulnerability).
- Potential impact on confidentiality or integrity.

## Response Timeline

- **Initial Response:** Within 48 hours of report receipt.
- **Triage & Status Update:** Within 5 business days.
- **Remediation & Advisory Release:** Coordinated with the reporter before public disclosure.
