"""Unit tests for the zero-knowledge TCP relay server."""

import socket
import threading
import time
import unittest

import server


class TestRelayServer(unittest.TestCase):
    """Test TCP relay routing, connection lifecycle, and buffering."""

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

    def test_bidirectional_relay(self):
        """Verify that payload from one client is routed only to other connected peers."""
        s1 = socket.socket()
        s2 = socket.socket()
        s1.connect(("127.0.0.1", self.port))
        s2.connect(("127.0.0.1", self.port))
        s1.settimeout(1.0)
        s2.settimeout(1.0)
        time.sleep(0.1)

        # Send from s1 -> should arrive at s2
        s1.sendall(b"Hello Peer 2")
        received_by_s2 = s2.recv(1024)
        self.assertEqual(received_by_s2, b"Hello Peer 2")

        # Send from s2 -> should arrive at s1
        s2.sendall(b"Hello Peer 1")
        received_by_s1 = s1.recv(1024)
        self.assertEqual(received_by_s1, b"Hello Peer 1")

        s1.close()
        s2.close()

    def test_buffering_for_subsequent_peer(self):
        """Verify that payloads sent when no recipients exist are buffered and delivered upon join."""
        s1 = socket.socket()
        s1.connect(("127.0.0.1", self.port))
        time.sleep(0.1)

        # s1 sends payload when alone in the room
        s1.sendall(b"Pre-arrival message")
        time.sleep(0.2)

        # s2 now connects
        s2 = socket.socket()
        s2.connect(("127.0.0.1", self.port))
        s2.settimeout(1.5)

        buffered_data = s2.recv(1024)
        self.assertEqual(buffered_data, b"Pre-arrival message")

        s1.close()
        s2.close()

    def test_client_disconnect_resilience(self):
        """Verify relay does not crash when a peer suddenly disconnects."""
        s1 = socket.socket()
        s2 = socket.socket()
        s1.connect(("127.0.0.1", self.port))
        s2.connect(("127.0.0.1", self.port))
        time.sleep(0.1)

        # Abruptly close s1
        s1.close()
        time.sleep(0.2)

        # s2 sends data - should not crash server
        s2.sendall(b"Still alive")
        time.sleep(0.1)
        s2.close()


if __name__ == "__main__":
    unittest.main()
