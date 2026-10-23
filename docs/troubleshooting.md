# Troubleshooting Guide

This document lists common operational issues and their resolutions.

---

## 1. Relay Unavailable / Connection Refused

### Symptom
Streamlit displays:
> `Could not connect to 127.0.0.1:5000: [Errno 111] Connection refused`

### Cause
The TCP relay server ([`server.py`](../server.py)) is not currently running on the specified host/port.

### Solution
1. Open a separate terminal and start the relay:
   ```bash
   ./scripts/run_relay.sh
   # Or: python3 server.py
   ```
2. Verify the relay is listening:
   ```bash
   ss -tulpn | grep 5000
   ```
3. Refresh the Streamlit page.

---

## 2. Decryption Failed (Tamper Detected)

### Symptom
System chat log displays:
> `⚠️ Decryption failed (Tamper detected).`

### Cause
The AES-256-GCM authentication tag did not match the computed GHASH over the ciphertext and nonce. This indicates one of the following:
1. An active adversary or network proxy modified bits in flight.
2. A client connected with mismatched session keys (e.g. handshake was interrupted).
3. The nonce or ciphertext was corrupted in transit.

### Solution
1. Verify that both endpoints completed the hybrid handshake simultaneously.
2. Click **Clear conversation** in the Streamlit sidebar.
3. Restart both client endpoints to negotiate a fresh post-quantum session key.

---

## 3. Bob AI Responder Shows "[Offline]"

### Symptom
Bob replies with:
> `[Bob AI - llama3 (Offline)]: Received '...'. (Local Ollama daemon not reachable: [Errno 111] Connection refused)`

### Cause
The headless Bob endpoint ([`bob_ai.py`](../bob_ai.py)) is running, but the local [Ollama](https://ollama.com/) service is either stopped or the `llama3` model is not pulled.

### Solution
1. Start the Ollama server:
   ```bash
   ollama serve
   ```
2. In another terminal, ensure the model is pulled:
   ```bash
   ollama pull llama3
   ```
3. Once running, subsequent messages will be processed directly by Llama-3 locally.

---

## 4. Port Conflict on Port 8501 or Port 5000

### Symptom
`Address already in use` error when launching Streamlit or the relay server.

### Solution
Find and terminate existing instances:
```bash
# For relay port 5000:
lsof -i :5000
kill -9 <PID>

# For Streamlit port 8501:
lsof -i :8501
kill -9 <PID>
```
Or specify an alternate port via environment variables:
```bash
RELAY_PORT=5500 ./scripts/run_relay.sh
STREAMLIT_PORT=8502 ./scripts/run_alice.sh
```
