"""Unit tests for Bob AI responder and automated agent."""

import socket
import threading
import time
import unittest

import bob_agent
import bob_ai
import server


class TestBobAgent(unittest.TestCase):
    """Test Bob agent automation and AI fallback response generator."""

    def test_generate_response_offline_fallback(self):
        """Verify fallback behavior when local Ollama daemon is unreachable."""
        response = bob_ai.generate_response("test prompt", model="nonexistent-test-model")
        self.assertIn("Acknowledged secure message 'test prompt'", response)
        self.assertIn("nonexistent-test-model", response)

    def test_connect_to_router_refused(self):
        """Verify connect_to_router raises ConnectionRefusedError when server is offline."""
        # Find unused port
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
            probe.bind(("127.0.0.1", 0))
            unused_port = probe.getsockname()[1]

        with self.assertRaises(ConnectionRefusedError):
            bob_agent.connect_to_router(host="127.0.0.1", port=unused_port, max_retries=2)

    def test_connect_to_router_success(self):
        """Verify connect_to_router succeeds when relay is online."""
        stop_event = threading.Event()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
            probe.bind(("127.0.0.1", 0))
            port = probe.getsockname()[1]

        server_thread = threading.Thread(
            target=server.run_server,
            kwargs={"host": "127.0.0.1", "port": port, "stop_event": stop_event},
            daemon=True,
        )
        server_thread.start()
        time.sleep(0.15)

        # Connect Alice as initiator in background so handshake completes
        from crypto_client import SecureClient
        alice = SecureClient([])
        alice_thread = threading.Thread(
            target=alice.connect,
            kwargs={"port": port, "role": "Alice (Initiator)", "max_retries": 3},
            daemon=True,
        )
        alice_thread.start()

        # Connect Bob
        bob_client = bob_agent.connect_to_router(host="127.0.0.1", port=port, max_retries=5)
        self.assertIsNotNone(bob_client)
        self.assertIsNotNone(bob_client.aes_key)

        alice_thread.join(timeout=3)
        self.assertEqual(bob_client.aes_key, alice.aes_key)

        alice.close()
        bob_client.close()
        stop_event.set()


if __name__ == "__main__":
    unittest.main()
