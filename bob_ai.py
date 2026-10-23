"""Headless Bob endpoint for the encrypted chat relay."""

import logging
import os
import time

from crypto_client import SecureClient
from langchain_ollama import OllamaLLM

LOGGER = logging.getLogger(__name__)


def generate_response(prompt: str, model: str | None = None) -> str:
    """Generate an AI response using local Ollama if available, with a graceful fallback."""
    selected_model = model or os.environ.get("OLLAMA_MODEL", "llama3")
    try:
        llm = OllamaLLM(model=selected_model)
        return str(llm.invoke(prompt))
    except Exception as exc:
        LOGGER.warning("Local Ollama inference failed or unavailable: %s", exc)
        return (
            f"[Bob AI - {selected_model} (Offline)]: Acknowledged secure message '{prompt}'. "
            f"(Local Ollama daemon not reachable: {exc})"
        )


def main() -> None:
    """Connect Bob, process decrypted user messages, and reply securely."""
    relay_host = os.environ.get("RELAY_HOST", "127.0.0.1")
    relay_port = int(os.environ.get("RELAY_PORT", "5000"))
    message_queue: list[dict[str, str]] = []
    client = SecureClient(message_queue, inbound_role="user")

    print(f"[Bob] Connecting to the encrypted relay on {relay_host}:{relay_port}...", flush=True)
    client.connect(relay_port, role="Bob (Responder)", host=relay_host)
    print("[Bob] Connected and responder handshake completed.", flush=True)

    processed_index = 0
    while True:
        while processed_index < len(message_queue):
            message = message_queue[processed_index]
            processed_index += 1

            if message.get("role") != "user":
                continue

            prompt = message.get("content", "")
            print("[Bob] Message decrypted; invoking local Ollama...", flush=True)
            response = generate_response(prompt)
            client.send_message(response)
            print("[Bob] AI response encrypted and transmitted.", flush=True)

        time.sleep(0.5)


if __name__ == "__main__":
    main()