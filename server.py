"""Pure TCP relay for an end-to-end encrypted chat application."""

import logging
import socket
import threading


HOST = "127.0.0.1"
PORT = 5000
BUFFER_SIZE = 4096

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
LOGGER = logging.getLogger(__name__)


def remove_client(
    client_socket: socket.socket,
    clients: set[socket.socket],
    clients_lock: threading.Lock,
) -> None:
    """Remove and close a client socket exactly once."""
    with clients_lock:
        was_active = client_socket in clients
        clients.discard(client_socket)

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
) -> None:
    """Relay opaque bytes to every active client except the sender."""
    with clients_lock:
        recipients = tuple(client for client in clients if client is not sender)

    failed_recipients: list[socket.socket] = []
    for recipient in recipients:
        try:
            recipient.sendall(payload)
        except OSError:
            failed_recipients.append(recipient)

    for recipient in failed_recipients:
        remove_client(recipient, clients, clients_lock)

    LOGGER.info("Relayed payload of %d bytes", len(payload))


def handle_client(
    client_socket: socket.socket,
    address: tuple[str, int],
    clients: set[socket.socket],
    clients_lock: threading.Lock,
) -> None:
    """Receive and relay one client's opaque TCP byte stream."""
    try:
        while True:
            payload = client_socket.recv(BUFFER_SIZE)
            if not payload:
                break
            relay_payload(client_socket, payload, clients, clients_lock)
    except OSError as error:
        LOGGER.info("Socket error for client %s: %s", address, error)
    finally:
        remove_client(client_socket, clients, clients_lock)


def main() -> None:
    """Start the relay and accept clients until the process is stopped."""
    clients: set[socket.socket] = set()
    clients_lock = threading.Lock()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        LOGGER.info("Zero-knowledge relay listening on %s:%d", HOST, PORT)

        try:
            while True:
                client_socket, address = server_socket.accept()
                with clients_lock:
                    clients.add(client_socket)
                LOGGER.info("Client %s connected", address)

                threading.Thread(
                    target=handle_client,
                    args=(client_socket, address, clients, clients_lock),
                    daemon=True,
                ).start()
        except KeyboardInterrupt:
            LOGGER.info("Relay server stopping")
        finally:
            with clients_lock:
                active_clients = tuple(clients)
                clients.clear()
            for client_socket in active_clients:
                try:
                    client_socket.shutdown(socket.SHUT_RDWR)
                except OSError:
                    pass
                client_socket.close()


if __name__ == "__main__":
    main()