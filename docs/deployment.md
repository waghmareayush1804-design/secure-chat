# Deployment and Operations Guide

This guide covers operational deployments of the Project Armadillo architecture.

## 1. Local Production Deployment

To run all three nodes on a Linux server:

### 1.1 Blind Relay Daemon
Run the relay in the background or configure as a systemd service:

```bash
RELAY_HOST=0.0.0.0 RELAY_PORT=5000 python3 server.py
```

#### systemd Unit File (`/etc/systemd/system/armadillo-relay.service`)
```ini
[Unit]
Description=Project Armadillo Zero-Knowledge Relay
After=network.target

[Service]
Type=simple
User=armadillo
WorkingDirectory=/opt/armadillo
ExecStart=/opt/armadillo/.venv/bin/python3 server.py
Restart=always
RestartSec=3
Environment=RELAY_HOST=0.0.0.0
Environment=RELAY_PORT=5000

[Install]
WantedBy=multi-user.target
```

---

### 1.2 Bob Sovereign AI Endpoint
Ensure [Ollama](https://ollama.com/) is installed and running:

```bash
# Start Ollama daemon and pull Llama 3
ollama serve &
ollama pull llama3

# Start Bob AI Endpoint
RELAY_HOST=127.0.0.1 RELAY_PORT=5000 python3 bob_ai.py
```

---

### 1.3 Alice Operator Terminal (Streamlit)
Run Streamlit behind a reverse proxy (e.g. Nginx or Caddy) with TLS termination:

```bash
streamlit run Home.py --server.port 8501 --server.address 127.0.0.1 --server.headless true
```

---

## 2. Docker Deployment

### Dockerfile
```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000 8501
CMD ["./scripts/run_relay.sh"]
```

---

## 3. Network Hardening

1. **Firewall Rules:**
   - The blind relay port (`5000`) should be firewalled so only authorized client endpoints can connect.
   - If running across the public internet, tunnel relay traffic through WireGuard, IPsec, or mutual TLS (mTLS).
2. **Localhost Isolation:**
   - The Bob AI endpoint and Ollama instance should bind strictly to `127.0.0.1` to prevent unauthorized network access to inference buffers.
