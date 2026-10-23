"""
Home.py - Project Armadillo: Post-Quantum Zero-Knowledge Communications
Framework: Pure Streamlit (Python)
Design: Minimalist, highly technical, cryptographic CSS background, pulsing CTA, tactile cards
"""

import streamlit as st

# Configure wide layout and page metadata
st.set_page_config(
    page_title="Project Armadillo",
    page_icon="🛡️",
    layout="wide",
)

# -----------------------------------------------------------------------------
# CUSTOM CSS INJECTION (ANIMATED CYBER GRID, PULSING BUTTON, INTERACTIVE CARDS)
# -----------------------------------------------------------------------------
st.markdown(
    """
    <style>
    /* 1. Cryptographic CSS Background with Slow-Panning Cyber Grid */
    @keyframes cyberGridPan {
        0% {
            background-position: 0 0;
        }
        100% {
            background-position: 60px 60px;
        }
    }

    [data-testid="stAppViewContainer"] {
        position: relative;
    }

    [data-testid="stAppViewContainer"]::before {
        content: "";
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        pointer-events: none;
        z-index: 0;
        opacity: 0.05;
        background-image: 
            linear-gradient(to right, #00e5ff 1px, transparent 1px),
            linear-gradient(to bottom, #00e5ff 1px, transparent 1px);
        background-size: 60px 60px;
        animation: cyberGridPan 24s linear infinite;
    }

    /* 2. Pulsing Button with High Contrast */
    @keyframes pulse {
        0% {
            transform: scale(1);
            box-shadow: 0 0 0 0 rgba(255, 75, 75, 0.4);
        }
        50% {
            transform: scale(1.02);
            box-shadow: 0 0 16px 4px rgba(255, 75, 75, 0.5);
        }
        100% {
            transform: scale(1);
            box-shadow: 0 0 0 0 rgba(255, 75, 75, 0.4);
        }
    }

    .stButton button,
    div[data-testid="stPageLink-NavLink"] {
        animation: pulse 2.4s infinite ease-in-out !important;
        transition: all 0.3s ease !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }

    .stButton button:hover,
    div[data-testid="stPageLink-NavLink"]:hover {
        color: #FFFFFF !important;
        background-color: #FF3B3B !important;
        border-color: #FF3B3B !important;
        transform: scale(1.02) !important;
    }

    .stButton button:hover *,
    div[data-testid="stPageLink-NavLink"]:hover * {
        color: #FFFFFF !important;
    }

    /* 3. Interactive Architecture Cards (Elevation & Subtle Cyan/Emerald Glow) */
    div[data-testid="stAlert"] {
        transition: transform 0.3s ease, box-shadow 0.3s ease !important;
        border-radius: 8px !important;
    }

    div[data-testid="stAlert"]:hover {
        transform: translateY(-5px) !important;
        box-shadow: 0 12px 28px -4px rgba(6, 182, 212, 0.25), 0 8px 16px -4px rgba(16, 185, 129, 0.25) !important;
    }

    /* 4. Footer Spacing: Ensure Ample Bottom Padding */
    .main .block-container {
        padding-bottom: 90px !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# 1. THE HERO SECTION
# -----------------------------------------------------------------------------
st.title("🛡️ Project Armadillo")
st.subheader("Post-Quantum Zero-Knowledge Communications.")

m1, m2, m3 = st.columns(3)

with m1:
    st.metric(
        label="Cryptographic Hardness",
        value="Post-Quantum",
        delta="ML-KEM-768 + X25519",
    )

with m2:
    st.metric(
        label="Data Sovereignty",
        value="Zero-Knowledge",
        delta="Blind TCP Relay",
        delta_color="off",
    )

with m3:
    st.metric(
        label="Endpoint Intelligence",
        value="Air-Gapped",
        delta="Local AI Inference",
    )

st.page_link(
    "pages/1_Chat_Terminal.py",
    label="Launch Secure Terminal",
    icon="🚀",
)

st.divider()

# -----------------------------------------------------------------------------
# 2. THE THREAT MODEL
# -----------------------------------------------------------------------------
st.warning(
    """
    ⚠️ **The Threat Model: Harvest Now, Decrypt Later (HNDL)**

    Adversaries and hostile intelligence entities are actively capturing, archiving, and indexing 
    encrypted communications traffic today. While currently protected by classical algorithms, these stored 
    data stores will be decrypted retroactively once Cryptographically Relevant Quantum Computers (CRQCs) 
    mature and execute **Shor's Algorithm** to factor discrete logarithms and prime moduli in polynomial time.
    """
)

st.divider()

# -----------------------------------------------------------------------------
# 3. THE ARCHITECTURE PILLARS
# -----------------------------------------------------------------------------
st.subheader("🌐 Zero-Knowledge Topology")
st.info(
    "[ Alice (Encrypts) ] ➔ ➔ [ Untrusted TCP Relay (Blind Routing) ] ➔ ➔ [ Bob (Decrypts + Local AI) ]"
)

st.subheader("🏛️ Architecture Pillars")

col_nav, col_dept = st.columns([1, 2.5], gap="large")

with col_nav:
    selected_pillar = st.radio(
        "Select an architecture pillar",
        options=[
            "🔑 Classical Layer",
            "🛡️ Quantum Layer",
            "🔒 Tunneling",
            "🧠 Sovereign AI",
        ],
    )

with col_dept:
    if selected_pillar == "🔑 Classical Layer":
        st.info(
            """
            ### 🔑 Classical Layer
            **X25519**  
            *Standard ECDH*
            """
        )
        st.markdown(
            """
            * **Curve25519 Montgomery Form:** $y^2 = x^3 + 486662x^2 + x$ over prime field $\\mathbb{F}_{2^{255}-19}$.
            * **Constant-Time Ladder:** Immune to cache-timing attacks via data-independent Montgomery ladders.
            * **128-Bit Classical Security:** Robust protection against classical adversaries with 32-byte public keys.
            """
        )
    elif selected_pillar == "🛡️ Quantum Layer":
        st.success(
            """
            ### 🛡️ Quantum Layer
            **ML-KEM-768**  
            *NIST FIPS 203 Standard*
            """
        )
        st.markdown(
            """
            * **Module Learning With Errors ($M\\text{-LWE}$):** High-dimensional polynomial lattices resistant to quantum period-finding.
            * **NIST Security Category 3:** IND-CCA2 security offering 192-bit quantum hardness (Crystals-Kyber parameterization).
            * **Immunity to Shor's Algorithm:** Lattice shortest vector problems lack periodic Abelian subgroup structures.
            """
        )
    elif selected_pillar == "🔒 Tunneling":
        st.error(
            """
            ### 🔒 Tunneling
            **AES-256-GCM**  
            *Authenticated Encryption*
            """
        )
        st.markdown(
            """
            * **Dual-Secret HKDF Extraction:** Combines classical and quantum shared secrets via $\\text{HKDF-Extract}$ into a 256-bit symmetric key.
            * **Galois Counter Mode:** High-throughput authenticated encryption with GHASH over $\\text{GF}(2^{128})$.
            * **Deterministic 96-Bit Nonces:** Collision-free sequence monotonic nonces with 128-bit integrity tags.
            """
        )
    elif selected_pillar == "🧠 Sovereign AI":
        st.warning(
            """
            ### 🧠 Sovereign AI
            **Local Llama-3**  
            *Air-Gapped, Zero-Telemetry Inference*
            """
        )
        st.markdown(
            """
            * **Strict Loopback Binding:** Bound exclusively to local IPC / `127.0.0.1` with zero external network socket listeners.
            * **Zero Outbound Telemetry:** User prompts, weights, and inference matrices never transit external cloud backbones.
            * **Volatile Memory Scrubbing:** Active zeroization of host RAM/VRAM inference buffers upon response completion.
            """
        )

st.divider()

# -----------------------------------------------------------------------------
# 4. THE ARCHITECT PROFILE (FOOTER)
# -----------------------------------------------------------------------------
st.subheader("👨‍💻 Lead Architect")

st.markdown(
    """
    * **Name:** Ayush Nitin Waghmare
    * **Institution:** Symbiosis Artificial Intelligence Institute
    * **Program:** Computer Science (Minor in Marketing Technology)
    * **Focus:** Zero-knowledge architectures, post-quantum cryptography, and local machine learning integration.
    """
)