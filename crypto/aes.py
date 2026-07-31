from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os


def encrypt_message(key: bytes, plaintext: str):
    """
    Encrypt plaintext using AES-256-GCM.
    Returns nonce and ciphertext.
    """

    aes = AESGCM(key)

    nonce = os.urandom(12)

    ciphertext = aes.encrypt(
        nonce,
        plaintext.encode(),
        None
    )

    return nonce, ciphertext


def decrypt_message(key: bytes, nonce: bytes, ciphertext: bytes):
    """
    Decrypt AES-GCM ciphertext.
    """

    aes = AESGCM(key)

    plaintext = aes.decrypt(
        nonce,
        ciphertext,
        None
    )

    return plaintext.decode()