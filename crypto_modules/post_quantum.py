import oqs

class PostQuantumCrypto:
    def __init__(self, kem_alg="Kyber512", sig_alg="Dilithium2"):
        self.kem_alg = kem_alg
        self.sig_alg = sig_alg

    def generate_kem_keypair(self):
        """Generates a public/private keypair using ML-KEM."""
        with oqs.KeyEncapsulation(self.kem_alg) as client:
            public_key = client.generate_keypair()
            secret_key = client.export_secret_key()
            return public_key, secret_key

    def encapsulate_secret(self, public_key):
        """Server encapsulates a shared secret using Client's public key."""
        with oqs.KeyEncapsulation(self.kem_alg) as server:
            ciphertext, shared_secret = server.encap_secret(public_key)
            return ciphertext, shared_secret

    def decapsulate_secret(self, ciphertext, secret_key):
        """Client decapsulates the shared secret using their private key."""
        with oqs.KeyEncapsulation(self.kem_alg) as client:
            client.secret_key = secret_key
            shared_secret = client.decap_secret(ciphertext)
            return shared_secret

    def sign_message(self, message):
        """Signs a message using ML-DSA."""
        with oqs.Signature(self.sig_alg) as signer:
            signer_pub_key = signer.generate_keypair()
            signature = signer.sign(message)
            return signature, signer_pub_key

    def verify_signature(self, message, signature, public_key):
        """Verifies an ML-DSA signature."""
        with oqs.Signature(self.sig_alg) as verifier:
            is_valid = verifier.verify(message, signature, public_key)
            return is_valid