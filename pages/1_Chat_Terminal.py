"""Streamlit frontend for Alice's encrypted relay client."""

import hashlib

import os

import streamlit as st

from crypto_client import SecureClient

st.set_page_config(page_title="E2EE Secure Chat", page_icon=":material/lock:")

RELAY_PORT = int(os.environ.get("RELAY_PORT", "5000"))
RELAY_HOST = os.environ.get("RELAY_HOST", "127.0.0.1")
POLL_INTERVAL = "500ms"


def initialize_client() -> None:
    """Create and connect Alice's client once for this browser session."""
    if "client" in st.session_state:
        return

    st.session_state.message_queue = []
    st.session_state.activity_queue = []
    client = SecureClient(
        st.session_state.message_queue,
        st.session_state.activity_queue,
    )

    try:
        client.connect(RELAY_PORT, role="Alice (Initiator)", host=RELAY_HOST, max_retries=1)
    except OSError as error:
        st.session_state.connection_error = str(error)
        return

    st.session_state.client = client
    st.session_state.connection_error = None


def render_system_message(message: dict[str, str]) -> None:
    """Keep protocol status messages available without crowding the chat."""
    with st.expander("System log", expanded=False):
        st.caption(message.get("content", ""))


def render_activity() -> None:
    """Render endpoint telemetry collected by SecureClient."""
    events = st.session_state.activity_queue
    if not events:
        return

    tab1, tab2 = st.tabs(
        ["📤 Outbound (Encryption)", "📥 Inbound (Decryption)"]
    )

    with tab1:
        outbound_events = [
            event
            for event in events
            if event.get("direction") == "outbound"
            and event.get("title")
            in {
                "Plaintext prepared",
                "AES-256-GCM encrypted",
                "Encrypted packet forwarded",
            }
        ]
        if not outbound_events:
            st.caption("No outbound message telemetry yet.")
        for event in outbound_events[-3:]:
            st.markdown(f"**{event['title']}**")
            st.caption(event["detail"])
            data = event.get("data")
            if data:
                st.code("\n".join(f"{key}: {value}" for key, value in data.items()))

    with tab2:
        inbound_events = [
            event
            for event in events
            if event.get("direction") == "inbound"
            and event.get("title")
            in {
                "Encrypted packet received",
                "AES-GCM authentication passed",
            }
        ]
        if not inbound_events:
            st.caption("No inbound response telemetry yet.")
        for event in inbound_events[-2:]:
            title = (
                "AES-256-GCM Decryption"
                if event["title"] == "AES-GCM authentication passed"
                else event["title"]
            )
            if event.get("title") == "AES-GCM authentication passed":
                st.markdown("**AES-256-GCM Decryption**")
                st.caption("Nonce verified and authentication tag accepted.")
            else:
                st.markdown(f"**{title}**")
                st.caption(event["detail"])
            data = event.get("data")
            if data:
                st.code("\n".join(f"{key}: {value}" for key, value in data.items()))

        plaintext_events = [
            event
            for event in inbound_events
            if event.get("title") == "AES-GCM authentication passed"
        ]
        if plaintext_events:
            plaintext = plaintext_events[-1].get("data", {}).get("text", "")
            st.markdown("**Plaintext revealed**")
            st.code(plaintext, language="text")


@st.fragment(run_every=POLL_INTERVAL)
def render_chat() -> None:
    """Render the queue and poll for messages received by the background thread."""
    messages = st.session_state.message_queue
    visible_messages = 0

    for message in messages:
        role = message.get("role")
        if role == "system":
            render_system_message(message)
            continue

        if role not in {"user", "assistant", "ai"}:
            continue

        visible_messages += 1
        display_role = "assistant" if role == "ai" else role
        with st.chat_message(display_role):
            st.markdown(message.get("content", ""))
            crypto = message.get("crypto")
            if crypto:
                with st.expander("🔍 View Cryptographic Details"):
                    st.code(
                        "Nonce (12 bytes):\n"
                        f"{crypto['nonce']}\n\n"
                        "AES-GCM ciphertext (hex):\n"
                        f"{crypto['ciphertext']}",
                        language="text",
                    )

    if visible_messages == 0:
        st.info(
            "Connect Alice and Bob, then send a message over the encrypted relay.",
            icon=":material/lock_open:",
        )

    client = st.session_state.get("client")
    if client is None:
        return

    if prompt := st.chat_input("Type your message..."):
        # The frontend owns the local conversation view; SecureClient encrypts
        # this same plaintext before writing it to the relay socket.
        messages.append({"role": "user", "content": prompt})
        try:
            client.send_message(prompt)
        except OSError as error:
            messages.append(
                {"role": "system", "content": f"Transmission failed: {error}"}
            )
        st.rerun()


initialize_client()

with st.sidebar:
    st.header("Session security")
    client = st.session_state.get("client")
    if client is not None:
        st.badge(
            "Active: FIPS 203 Hybrid (X25519 + ML-KEM-768)",
            color="green",
            icon=":material/verified_user:",
        )
        key_data = hashlib.sha256(client.aes_key).hexdigest()[:32]
        st.caption("Derived hybrid session key fingerprint")
        st.code(key_data, language="text")
        st.caption("The relay forwards ciphertext; this endpoint owns decryption.")
    else:
        st.badge("Relay unavailable", color="red", icon=":material/cloud_off:")
        error = st.session_state.get("connection_error")
        if error:
            st.caption(f"Could not connect to 127.0.0.1:{RELAY_PORT}: {error}")

    if st.button("Clear conversation", icon=":material/delete_sweep:"):
        st.session_state.message_queue.clear()
        st.session_state.activity_queue.clear()
        st.rerun()

st.title("End-to-end encrypted chat")
st.caption("Alice's plaintext is encrypted before it reaches the localhost relay.")

render_chat()
render_activity()
