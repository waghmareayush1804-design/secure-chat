import socket
import time
from pathlib import Path
import sys

from bob_ai import generate_response
from crypto_client import SecureClient


def connect_to_router():
    for _ in range(40):
        client = SecureClient(
            [],
            inbound_role="user",
            responder=generate_response,
        )
        try:
            client.connect(port=9999, role="Bob (Responder)")
            return client
        except ConnectionRefusedError:
            client.conn.close()
            time.sleep(0.15)
    raise ConnectionRefusedError("Bob could not connect to the local router")


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent))
    bob_client = connect_to_router()
    while True:
        time.sleep(60)