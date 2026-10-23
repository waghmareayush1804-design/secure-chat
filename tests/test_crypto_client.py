import os
import socket
import struct
import threading
import time
import unittest

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import mlkem, x25519
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

from crypto_client import SecureClient
import server


class TestCryptoPrimitives(unittest.TestCase):
    """Test offline cryptographic primitives without network sockets."""

    def test_direct_crypto_primitives(self):
        """Verify underlying X25519, ML-KEM-768, and HKDF-SHA256 operations."""
        # 1. Alice generates keys
        alice_x25519 = x25519.X25519PrivateKey.generate()
        alice_mlkem = mlkem.MLKEM768PrivateKey.generate()
        alice_x25519_pub_bytes = alice_x25519.public_key().public_bytes_raw()
        alice_mlkem_pub_bytes = alice_mlkem.public_key().public_bytes(
            serialization.Encoding.Raw, serialization.PublicFormat.Raw
        )

        self.assertEqual(len(alice_x25519_pub_bytes), 32)
        self.assertEqual(len(alice_mlkem_pub_bytes), 1184)

        # 2. Bob encapsulates ML-KEM and generates X25519
        bob_x25519 = x25519.X25519PrivateKey.generate()
        bob_x25519_pub_bytes = bob_x25519.public_key().public_bytes_raw()

        alice_mlkem_pub = mlkem.MLKEM768PublicKey.from_public_bytes(alice_mlkem_pub_bytes)
        pq_secret_bob, ciphertext = alice_mlkem_pub.encapsulate()
        self.assertEqual(len(ciphertext), 1088)
        self.assertEqual(len(pq_secret_bob), 32)

        # 3. Both exchange classical keys
        classical_bob = bob_x25519.exchange(x25519.X25519PublicKey.from_public_bytes(alice_x25519_pub_bytes))
        classical_alice = alice_x25519.exchange(x25519.X25519PublicKey.from_public_bytes(bob_x25519_pub_bytes))
        self.assertEqual(classical_bob, classical_alice)

        # 4. Alice decapsulates quantum ciphertext
        pq_secret_alice = alice_mlkem.decapsulate(ciphertext)
        self.assertEqual(pq_secret_bob, pq_secret_alice)

        # 5. HKDF derive symmetric key
        hkdf_alice = HKDF(algorithm=hashes.SHA256(), length=32, salt=None, info=b"pq-hybrid-v1")
        key_alice = hkdf_alice.derive(classical_alice + pq_secret_alice)

        hkdf_bob = HKDF(algorithm=hashes.SHA256(), length=32, salt=None, info=b"pq-hybrid-v1")
        key_bob = hkdf_bob.derive(classical_bob + pq_secret_bob)

        self.assertEqual(len(key_alice), 32)
        self.assertEqual(key_alice, key_bob)

    def test_tamper_detection(self):
        """Verify that tampering with ciphertext triggers an integrity alert."""
        alice_queue = []
        alice = SecureClient(alice_queue)
        aes_key = os.urandom(32)
        alice.aes_key = aes_key

        # Valid encryption
        aesgcm = AESGCM(aes_key)
        nonce = os.urandom(12)
        ciphertext = aesgcm.encrypt(nonce, b"Secret document", None)

        # Corrupt one bit in ciphertext
        corrupted_ciphertext = bytearray(ciphertext)
        corrupted_ciphertext[0] ^= 0x01
        corrupted_ciphertext = bytes(corrupted_ciphertext)

        # Decrypting corrupted ciphertext must raise exception
        with self.assertRaises(Exception):
            aesgcm.decrypt(nonce, corrupted_ciphertext, None)

        # Corrupted nonce must raise exception
        corrupted_nonce = bytearray(nonce)
        corrupted_nonce[0] ^= 0x01
        with self.assertRaises(Exception):
            aesgcm.decrypt(bytes(corrupted_nonce), ciphertext, None)

        alice.close()


class TestCryptoClientNetwork(unittest.TestCase):
    """Test SecureClient network protocol and message relaying."""

    def setUp(self):
        self.stop_event = threading.Event()
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
            probe.bind(("127.0.0.1", 0))
            self.port = probe.getsockname()[1]

        self.server_thread = threading.Thread(
            target=server.run_server,
            kwargs={"host": "127.0.0.1", "port": self.port, "stop_event": self.stop_event},
            daemon=True,
        )
        self.server_thread.start()
        time.sleep(0.15)

    def tearDown(self):
        self.stop_event.set()
        time.sleep(0.1)

    def test_hybrid_handshake_and_secure_messaging(self):
        """Test full network handshake and bidirectional encrypted messaging."""
        alice_queue = []
        bob_queue = []
        alice_activity = []
        bob_activity = []

        alice = SecureClient(alice_queue, activity_queue=alice_activity)
        bob = SecureClient(
            bob_queue,
            activity_queue=bob_activity,
            inbound_role="user",
            responder=lambda text: f"Processed: {text.upper()}",
        )

        t_alice = threading.Thread(
            target=alice.connect,
            kwargs={"port": self.port, "role": "Alice (Initiator)", "max_retries": 3},
            daemon=True,
        )
        t_bob = threading.Thread(
            target=bob.connect,
            kwargs={"port": self.port, "role": "Bob (Responder)", "max_retries": 3},
            daemon=True,
        )

        t_alice.start()
        time.sleep(0.05)
        t_bob.start()

        t_alice.join(timeout=4)
        t_bob.join(timeout=4)

        self.assertIsNotNone(alice.aes_key)
        self.assertIsNotNone(bob.aes_key)
        self.assertEqual(alice.aes_key, bob.aes_key)

        # Send message from Alice
        alice.send_message("quantum-safe secret payload")
        time.sleep(0.4)

        # Verify Bob received and decrypted the message
        received_by_bob = [m for m in bob_queue if m.get("role") == "user"]
        self.assertTrue(len(received_by_bob) >= 1)
        self.assertEqual(received_by_bob[0]["content"], "quantum-safe secret payload")

        # Verify Alice received Bob's automated response
        received_by_alice = [m for m in alice_queue if m.get("role") == "assistant"]
        self.assertTrue(len(received_by_alice) >= 1)
        self.assertEqual(received_by_alice[0]["content"], "Processed: QUANTUM-SAFE SECRET PAYLOAD")

        # Verify activity tracking logged key derivation events
        alice_titles = [e.get("title") for e in alice_activity]
        self.assertIn("Hybrid key material mixed", alice_titles)
        self.assertIn("HKDF derived session key", alice_titles)
        self.assertIn("AES-256-GCM encrypted", alice_titles)

        alice.close()
        bob.close()

    def test_rapid_successive_messages(self):
        """Verify multiple messages sent without pauses are preserved and decrypted."""
        alice_queue, bob_queue = [], []
        alice = SecureClient(alice_queue)
        bob = SecureClient(bob_queue, inbound_role="user")

        t_alice = threading.Thread(
            target=alice.connect,
            kwargs={"port": self.port, "role": "Alice (Initiator)", "max_retries": 3},
            daemon=True,
        )
        t_bob = threading.Thread(
            target=bob.connect,
            kwargs={"port": self.port, "role": "Bob (Responder)", "max_retries": 3},
            daemon=True,
        )
        t_alice.start()
        time.sleep(0.05)
        t_bob.start()
        t_alice.join(timeout=4)
        t_bob.join(timeout=4)

        # Send 5 messages in immediate succession
        for i in range(5):
            alice.send_message(f"Rapid Packet #{i}")

        time.sleep(0.4)

        user_messages = [m["content"] for m in bob_queue if m.get("role") == "user"]
        self.assertEqual(len(user_messages), 5)
        for i in range(5):
            self.assertEqual(user_messages[i], f"Rapid Packet #{i}")

        # Ensure no tamper alarms were falsely triggered
        tamper_alarms = [m for m in bob_queue if "Tamper detected" in m.get("content", "")]
        self.assertEqual(len(tamper_alarms), 0)

        alice.close()
        bob.close()

    def test_large_message_payload(self):
        """Verify messages larger than socket buffer size (64KB) are reassembled accurately."""
        alice_queue, bob_queue = [], []
        alice = SecureClient(alice_queue)
        bob = SecureClient(bob_queue, inbound_role="user")

        t_alice = threading.Thread(
            target=alice.connect,
            kwargs={"port": self.port, "role": "Alice (Initiator)", "max_retries": 3},
            daemon=True,
        )
        t_bob = threading.Thread(
            target=bob.connect,
            kwargs={"port": self.port, "role": "Bob (Responder)", "max_retries": 3},
            daemon=True,
        )
        t_alice.start()
        time.sleep(0.05)
        t_bob.start()
        t_alice.join(timeout=4)
        t_bob.join(timeout=4)

        large_text = "ARMADILLO-SECURE-PAYLOAD-" * 2500  # ~62.5 KB
        alice.send_message(large_text)
        time.sleep(0.5)

        user_messages = [m["content"] for m in bob_queue if m.get("role") == "user"]
        self.assertEqual(len(user_messages), 1)
        self.assertEqual(user_messages[0], large_text)

        alice.close()
        bob.close()

    def test_network_tamper_resilience(self):
        """Verify corrupted network packets alert without permanently destroying connection."""
        alice_queue, bob_queue = [], []
        bob_activity = []
        alice = SecureClient(alice_queue)
        bob = SecureClient(bob_queue, activity_queue=bob_activity, inbound_role="user")

        t_alice = threading.Thread(
            target=alice.connect,
            kwargs={"port": self.port, "role": "Alice (Initiator)", "max_retries": 3},
            daemon=True,
        )
        t_bob = threading.Thread(
            target=bob.connect,
            kwargs={"port": self.port, "role": "Bob (Responder)", "max_retries": 3},
            daemon=True,
        )
        t_alice.start()
        time.sleep(0.05)
        t_bob.start()
        t_alice.join(timeout=4)
        t_bob.join(timeout=4)

        # 1. Send valid message
        alice.send_message("Pre-tamper message")
        time.sleep(0.2)

        # 2. Inject corrupted framed packet directly through Alice's connection
        corrupted_payload = os.urandom(48)
        framed_bad = struct.pack(">I", len(corrupted_payload)) + corrupted_payload
        alice.conn.sendall(framed_bad)
        time.sleep(0.2)

        # 3. Send valid message after corruption
        alice.send_message("Post-tamper message")
        time.sleep(0.3)

        # Confirm both valid messages were decoded
        user_messages = [m["content"] for m in bob_queue if m.get("role") == "user"]
        self.assertEqual(user_messages, ["Pre-tamper message", "Post-tamper message"])

        # Confirm tamper event was logged in queue and telemetry
        system_warnings = [m["content"] for m in bob_queue if "Tamper detected" in m.get("content", "")]
        self.assertTrue(len(system_warnings) >= 1)

        tamper_events = [e for e in bob_activity if e.get("kind") == "tamper_alert"]
        self.assertTrue(len(tamper_events) >= 1)

        alice.close()
        bob.close()


if __name__ == "__main__":
    unittest.main()
