import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes

class ClassicalCrypto:
    def __init__(self):
        pass

    def generate_ecdh_keypair(self):
        """Generates an Elliptic Curve keypair for ECDH."""
        private_key = ec.generate_private_key(ec.SECP384R1())
        public_key = private_key.public_key()
        return private_key, public_key

    def derive_shared_secret(self, private_key, peer_public_key):
        """Derives a shared secret using ECDH."""
        shared_key = private_key.exchange(ec.ECDH(), peer_public_key)
        return shared_key

    def derive_aes_key(self, input_key_material, salt=None):
        """Derives a secure AES-256 key using HKDF."""
        if salt is None:
            salt = os.urandom(16)
            
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=32, # 256 bits for AES-256
            salt=salt,
            info=b"hybrid-crypto-key-expansion",
        )
        return hkdf.derive(input_key_material), salt

    def aes_encrypt(self, key, plaintext):
        """Encrypts data using AES-256-GCM."""
        aesgcm = AESGCM(key)
        nonce = os.urandom(12)
        ciphertext = aesgcm.encrypt(nonce, plaintext.encode('utf-8'), None)
        return nonce + ciphertext # Prepend nonce for decryption

    def aes_decrypt(self, key, encrypted_data):
        """Decrypts data using AES-256-GCM."""
        aesgcm = AESGCM(key)
        nonce = encrypted_data[:12]
        ciphertext = encrypted_data[12:]
        plaintext = aesgcm.decrypt(nonce, ciphertext, None)
        return plaintext.decode('utf-8')