import os
import sys
import time
from pathlib import Path

from bob_ai import generate_response
from crypto_client import SecureClient


def connect_to_router(host: str = "127.0.0.1", port: int = 5000, max_retries: int = 40):
    """Connect Bob's automated responder agent to the encrypted relay."""
    for _ in range(max_retries):
        client = SecureClient(
            [],
            inbound_role="user",
            responder=generate_response,
        )
        try:
            client.connect(port=port, role="Bob (Responder)", host=host, max_retries=1)
            return client
        except (ConnectionRefusedError, OSError):
            client.close()
            time.sleep(0.2)
    raise ConnectionRefusedError(f"Bob could not connect to the local router at {host}:{port}")


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent))
    target_host = os.environ.get("RELAY_HOST", "127.0.0.1")
    target_port = int(os.environ.get("RELAY_PORT", "5000"))
    bob_client = connect_to_router(host=target_host, port=target_port)
    while True:
        time.sleep(60)
