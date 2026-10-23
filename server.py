"""Pure TCP relay for an end-to-end encrypted chat application."""

import logging
import os
import socket
import threading


HOST = os.environ.get("RELAY_HOST", "127.0.0.1")
PORT = int(os.environ.get("RELAY_PORT", "5000"))
BUFFER_SIZE = 4096
MAX_PENDING_PAYLOADS = 100

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
LOGGER = logging.getLogger(__name__)


def remove_client(
    client_socket: socket.socket,
    clients: set[socket.socket],
    clients_lock: threading.Lock,
    pending_payloads: list[tuple[socket.socket, bytes]] | None = None,
) -> None:
    """Remove and close a client socket exactly once."""
    with clients_lock:
        was_active = client_socket in clients
        clients.discard(client_socket)
        if pending_payloads is not None:
            pending_payloads[:] = [
                (sender, payload)
                for sender, payload in pending_payloads
                if sender is not client_socket
            ]

    if was_active:
        try:
            address = client_socket.getpeername()
        except OSError:
            address = "unknown peer"
        LOGGER.info("Client %s disconnected", address)

    try:
        client_socket.shutdown(socket.SHUT_RDWR)
    except OSError:
        pass
    finally:
        client_socket.close()


def relay_payload(
    sender: socket.socket,
    payload: bytes,
    clients: set[socket.socket],
    clients_lock: threading.Lock,
    pending_payloads: list[tuple[socket.socket, bytes]] | None = None,
) -> None:
    """Relay opaque bytes to every active client except the sender."""
    with clients_lock:
        recipients = tuple(client for client in clients if client is not sender)
        if not recipients and pending_payloads is not None:
            if len(pending_payloads) < MAX_PENDING_PAYLOADS:
                pending_payloads.append((sender, payload))
                LOGGER.info(
                    "No recipients available; buffered %d bytes for next connected peer",
                    len(payload),
                )
            else:
                LOGGER.warning("Pending payload queue full; dropped %d bytes", len(payload))
            return

    failed_recipients: list[socket.socket] = []
    for recipient in recipients:
        try:
            recipient.sendall(payload)
        except OSError:
            failed_recipients.append(recipient)

    for recipient in failed_recipients:
        remove_client(recipient, clients, clients_lock, pending_payloads)

    LOGGER.info("Relayed payload of %d bytes", len(payload))


def handle_client(
    client_socket: socket.socket,
    address: tuple[str, int],
    clients: set[socket.socket],
    clients_lock: threading.Lock,
    pending_payloads: list[tuple[socket.socket, bytes]],
) -> None:
    """Receive and relay one client's opaque TCP byte stream."""
    try:
        while True:
            payload = client_socket.recv(BUFFER_SIZE)
            if not payload:
                break
            relay_payload(client_socket, payload, clients, clients_lock, pending_payloads)
    except OSError as error:
        LOGGER.info("Socket error for client %s: %s", address, error)
    finally:
        remove_client(client_socket, clients, clients_lock, pending_payloads)


def run_server(
    host: str = HOST,
    port: int = PORT,
    stop_event: threading.Event | None = None,
) -> None:
    """Run the relay server with optional stop event for testing and lifecycle management."""
    clients: set[socket.socket] = set()
    clients_lock = threading.Lock()
    pending_payloads: list[tuple[socket.socket, bytes]] = []

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((host, port))
        server_socket.listen()
        if stop_event is not None:
            server_socket.settimeout(0.5)
        LOGGER.info("Zero-knowledge relay listening on %s:%d", host, port)

        try:
            while stop_event is None or not stop_event.is_set():
                try:
                    client_socket, address = server_socket.accept()
                except socket.timeout:
                    continue

                with clients_lock:
                    clients.add(client_socket)
                    LOGGER.info("Client %s connected", address)

                    to_deliver = [
                        payload
                        for sender, payload in pending_payloads
                        if sender is not client_socket
                    ]
                    pending_payloads[:] = [
                        (sender, payload)
                        for sender, payload in pending_payloads
                        if sender is client_socket
                    ]

                for payload in to_deliver:
                    try:
                        client_socket.sendall(payload)
                        LOGGER.info("Delivered %d buffered bytes to new peer %s", len(payload), address)
                    except OSError:
                        remove_client(client_socket, clients, clients_lock, pending_payloads)
                        break

                threading.Thread(
                    target=handle_client,
                    args=(client_socket, address, clients, clients_lock, pending_payloads),
                    daemon=True,
                ).start()
        except KeyboardInterrupt:
            LOGGER.info("Relay server stopping")
        finally:
            with clients_lock:
                active_clients = tuple(clients)
                clients.clear()
                pending_payloads.clear()
            for client_socket in active_clients:
                try:
                    client_socket.shutdown(socket.SHUT_RDWR)
                except OSError:
                    pass
                client_socket.close()


def main() -> None:
    """Start the relay and accept clients until the process is stopped."""
    run_server(HOST, PORT)


if __name__ == "__main__":
    main()