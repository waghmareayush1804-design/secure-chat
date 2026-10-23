import socket
import threading
import time
import os
import hashlib
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import mlkem
from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

class SecureClient:
    def __init__(self, message_queue, activity_queue=None, inbound_role="assistant", responder=None):
        self.message_queue = message_queue
        self.activity_queue = activity_queue if activity_queue is not None else []
        self.inbound_role = inbound_role
        self.responder = responder
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.aes_key = None

    def _record_activity(self, title, detail, direction, kind="status", data=None):
        event = {
            "title": title,
            "detail": detail,
            "direction": direction,
            "kind": kind,
        }
        if data is not None:
            event["data"] = data
        self.activity_queue.append(event)
        
    def close(self):
        """Cleanly close the client connection."""
        try:
            self.conn.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        finally:
            self.conn.close()

    def connect(self, port=5000, role="Alice (Initiator)", host="127.0.0.1", max_retries=None, retry_delay=1.0):
        attempts = 0
        while True:
            try:
                self.conn.connect((host, port))
                break
            except ConnectionRefusedError:
                attempts += 1
                if max_retries is not None and attempts >= max_retries:
                    raise ConnectionRefusedError(f"Could not connect to {host}:{port} after {attempts} attempts")
                print(f"[{role}] Server offline. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)

        self.message_queue.append({"role": "system", "content": "🟢 Connected to Zero-Knowledge Server."})
        
        self._perform_handshake(role)
        threading.Thread(target=self._receive_loop, daemon=True).start()

    def _perform_handshake(self, role):
        self.message_queue.append({"role": "system", "content": f"🔄 Initiating Hybrid Key Exchange as {role}..."})
        
        if role == "Alice (Initiator)":
            # 1. Generate Classical + Quantum Keys
            alice_x25519_priv = x25519.X25519PrivateKey.generate()
            alice_x25519_pub = alice_x25519_priv.public_key().public_bytes_raw()
            alice_mlkem_priv = mlkem.MLKEM768PrivateKey.generate()
            alice_mlkem_pub = alice_mlkem_priv.public_key().public_bytes(
                serialization.Encoding.Raw,
                serialization.PublicFormat.Raw,
            )
            
            # 2. Send both public keys to Bob
            self.conn.sendall(alice_x25519_pub + alice_mlkem_pub)
            
            # 3. Wait for Bob's response (Classical PubKey + Quantum Ciphertext)
            response = self.conn.recv(2048)
            bob_x25519_pub_bytes = response[:32]
            mlkem_ciphertext = response[32:]
            
            # 4. Decapsulate / Derive the secrets
            bob_x25519_pub = x25519.X25519PublicKey.from_public_bytes(bob_x25519_pub_bytes)
            classical_secret = alice_x25519_priv.exchange(bob_x25519_pub)
            pq_secret = alice_mlkem_priv.decapsulate(mlkem_ciphertext)
            
        else:
            # 1. Bob waits for Alice's public keys
            data = self.conn.recv(2048)
            alice_x25519_pub_bytes = data[:32]
            alice_mlkem_pub_bytes = data[32:]
            
            # 2. Bob generates his Classical Keys
            bob_x25519_priv = x25519.X25519PrivateKey.generate()
            bob_x25519_pub = bob_x25519_priv.public_key().public_bytes_raw()
            
            # 3. Bob encapsulates a quantum secret using Alice's public key
            alice_mlkem_pub = mlkem.MLKEM768PublicKey.from_public_bytes(alice_mlkem_pub_bytes)
            (pq_secret, mlkem_ciphertext) = alice_mlkem_pub.encapsulate()
            
            # 4. Bob sends his public key and the ciphertext back
            self.conn.sendall(bob_x25519_pub + mlkem_ciphertext)
            
            # 5. Bob derives the classical secret
            alice_x25519_pub = x25519.X25519PublicKey.from_public_bytes(alice_x25519_pub_bytes)
            classical_secret = bob_x25519_priv.exchange(alice_x25519_pub)

        # --- HYBRID KEY DERIVATION ---
        combined_secrets = classical_secret + pq_secret
        self._record_activity(
            "Hybrid key material mixed",
            "X25519 and ML-KEM shared secrets combined locally",
            "local",
            kind="key_mix",
            data={
                "x25519_bytes": len(classical_secret),
                "x25519_fingerprint": hashlib.sha256(classical_secret).hexdigest()[:16],
                "mlkem_bytes": len(pq_secret),
                "mlkem_fingerprint": hashlib.sha256(pq_secret).hexdigest()[:16],
                "combined_bytes": len(combined_secrets),
                "combined_fingerprint": hashlib.sha256(combined_secrets).hexdigest()[:16],
            },
        )
        hkdf = HKDF(algorithm=hashes.SHA256(), length=32, salt=None, info=b"pq-hybrid-v1")
        self.aes_key = hkdf.derive(combined_secrets)
        self._record_activity(
            "HKDF derived session key",
            "A fresh AES-256 key was derived locally",
            "local",
            kind="derived_key",
            data={
                "algorithm": "HKDF-SHA256",
                "info": "pq-hybrid-v1",
                "key_bytes": len(self.aes_key),
                "key_fingerprint": hashlib.sha256(self.aes_key).hexdigest()[:16],
            },
        )
        
        self.message_queue.append({"role": "system", "content": f"✅ Quantum-Safe AES-256-GCM Key Established!"})

    def encrypt_and_send(self, plaintext: str):
        self._record_activity(
            "Plaintext prepared",
            f"{len(plaintext.encode('utf-8'))} bytes visible only to this client",
            "outbound",
            kind="plaintext",
            data={"text": plaintext},
        )
        aesgcm = AESGCM(self.aes_key)
        nonce = os.urandom(12)
        ciphertext = aesgcm.encrypt(nonce, plaintext.encode('utf-8'), associated_data=None)
        packet = nonce + ciphertext
        payload_details = {
            "nonce": nonce.hex(),
            "ciphertext": ciphertext.hex(),
        }
        for message in reversed(self.message_queue):
            if (
                message.get("content") == plaintext
                and message.get("role") in {"user", "assistant"}
                and "crypto" not in message
            ):
                message["crypto"] = payload_details
                break
        self._record_activity(
            "AES-256-GCM encrypted",
            f"{len(packet)} bytes sealed with a fresh 12-byte nonce",
            "outbound",
            kind="encryption",
            data={
                "nonce": nonce.hex(),
                "ciphertext_preview": ciphertext.hex()[:48],
                "ciphertext_bytes": len(ciphertext),
            },
        )
        self.conn.sendall(packet)
        self._record_activity(
            "Encrypted packet forwarded",
            "The router can forward bytes but cannot read this message",
            "outbound",
        )

    def send_message(self, plaintext: str):
        """Compatibility name for sending an encrypted message."""
        self.encrypt_and_send(plaintext)

    def _receive_loop(self):
        while True:
            try:
                data = self.conn.recv(4096)
                if not data:
                    self.message_queue.append({"role": "system", "content": "ℹ️ Relay connection closed."})
                    break
            except OSError:
                self.message_queue.append({"role": "system", "content": "ℹ️ Relay disconnected."})
                break

            try:
                self._record_activity(
                    "Encrypted packet received",
                    f"{len(data)} bytes received from the router",
                    "inbound",
                    data={
                        "nonce": data[:12].hex(),
                        "ciphertext": data[12:-16].hex() if len(data) >= 28 else data[12:].hex(),
                        "authentication_tag": data[-16:].hex() if len(data) >= 28 else "",
                    },
                )
                nonce, ciphertext = data[:12], data[12:]
                aesgcm = AESGCM(self.aes_key)
                plaintext = aesgcm.decrypt(nonce, ciphertext, associated_data=None)
                self._record_activity(
                    "AES-GCM authentication passed",
                    f"{len(plaintext)} plaintext bytes recovered locally",
                    "inbound",
                    kind="decryption",
                    data={
                        "nonce": nonce.hex(),
                        "text": plaintext.decode("utf-8"),
                    },
                )
                received_text = plaintext.decode("utf-8")
                self.message_queue.append(
                    {
                        "role": self.inbound_role,
                        "content": received_text,
                        "crypto": {
                            "nonce": nonce.hex(),
                            "ciphertext": ciphertext.hex(),
                        },
                    }
                )
                if self.responder is not None:
                    response_text = self.responder(received_text)
                    self.message_queue.append({"role": "assistant", "content": response_text})
                    self._record_activity(
                        "Bob AI composed a response",
                        "The responder ran locally after authenticated decryption",
                        "outbound",
                        kind="ai_response",
                        data={"text": response_text},
                    )
                    self.encrypt_and_send(response_text)
            except Exception:
                self.message_queue.append({"role": "system", "content": "⚠️ Decryption failed (Tamper detected)."})
                break