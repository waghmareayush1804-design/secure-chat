"""Headless Bob endpoint for the encrypted chat relay."""

import time

from crypto_client import SecureClient
from langchain_ollama import OllamaLLM


def main() -> None:
    """Connect Bob, process decrypted user messages, and reply securely."""
    message_queue: list[dict[str, str]] = []
    client = SecureClient(message_queue, inbound_role="user")
    llm = OllamaLLM(model="llama3")

    print("[Bob] Connecting to the encrypted relay on 127.0.0.1:5000...", flush=True)
    client.connect(5000, role="Bob (Responder)")
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
            response = str(llm.invoke(prompt))
            client.send_message(response)
            print("[Bob] AI response encrypted and transmitted.", flush=True)

        time.sleep(0.5)


if __name__ == "__main__":
    main()