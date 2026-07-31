"""
network/messages.py

Protocol message definitions for the
Hybrid PQC-QKD Secure Communication System.
"""

from enum import Enum


class MessageType(Enum):
    """
    Message types exchanged between Alice and Bob.
    """

    # =====================================================
    # Connection Management
    # =====================================================

    HELLO = "HELLO"
    HELLO_ACK = "HELLO_ACK"
    CLOSE = "CLOSE"
    ERROR = "ERROR"

    # =====================================================
    # Phase 5 - BB84
    # =====================================================

    BB84_INIT = "BB84_INIT"
    BB84_BASES = "BB84_BASES"
    BB84_SIFT = "BB84_SIFT"
    QBER_REPORT = "QBER_REPORT"

    # =====================================================
    # Phase 5.3 - Cascade Error Correction
    # =====================================================

    # =====================================================
    # Phase 5.3 - Cascade Error Correction
    # =====================================================

    RECON_START = "RECON_START"
    RECON_ACK = "RECON_ACK"

    PARITY_REQUEST = "PARITY_REQUEST"
    PARITY_RESPONSE = "PARITY_RESPONSE"

    ERROR_LOCATION_REQUEST = "ERROR_LOCATION_REQUEST"
    ERROR_LOCATION_RESPONSE = "ERROR_LOCATION_RESPONSE"

    BIT_CORRECTION = "BIT_CORRECTION"

    RECON_COMPLETE = "RECON_COMPLETE"
    # =====================================================
    # Phase 5.4 - Privacy Amplification
    # =====================================================

    PRIVACY_START = "PRIVACY_START"

    PRIVACY_KEY = "PRIVACY_KEY"

    PRIVACY_ACK = "PRIVACY_ACK"

    # =====================================================
    # Phase 6 - ML-KEM
    # =====================================================

    MLKEM_PUBLIC_KEY = "MLKEM_PUBLIC_KEY"

    MLKEM_CIPHERTEXT = "MLKEM_CIPHERTEXT"

    MLKEM_SHARED_SECRET = "MLKEM_SHARED_SECRET"

    # =====================================================
    # Phase 6 - ML-DSA
    # =====================================================

    MLDSA_PUBLIC_KEY = "MLDSA_PUBLIC_KEY"

    MLDSA_SIGNATURE = "MLDSA_SIGNATURE"

    MLDSA_VERIFY = "MLDSA_VERIFY"

    # =====================================================
    # Phase 7 - Adaptive Gear Negotiation
    # =====================================================

    GEAR_NEGOTIATION = "GEAR_NEGOTIATION"

    GEAR_RESPONSE = "GEAR_RESPONSE"

    # =====================================================
    # Phase 8 - Secure Messaging
    # =====================================================

    AES_MESSAGE = "AES_MESSAGE"

    AES_ACK = "AES_ACK"

    ERROR_CORRECTION = "ERROR_CORRECTION"
    CORRECTION_ACK = "CORRECTION_ACK"
    UPDATED_KEY = "UPDATED_KEY"
    ENCRYPTED_MESSAGE = "ENCRYPTED_MESSAGE"

    KEY_VERIFY = "KEY_VERIFY"
    KEY_VERIFY_ACK = "KEY_VERIFY_ACK"
    