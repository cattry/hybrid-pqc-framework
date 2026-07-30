import oqs

class PostQuantumCrypto:
    def __init__(self):
        # Dynamically detect the available KEM (Kyber) mechanism
        supported_kems = oqs.get_supported_kem_mechanisms()
        if "Kyber512" in supported_kems:
            self.kem_alg = "Kyber512"
        elif "ML-KEM-512" in supported_kems:
            self.kem_alg = "ML-KEM-512"
        else:
            self.kem_alg = supported_kems[0] # Safe fallback

        # Dynamically detect the available Signature (Dilithium) mechanism
        supported_sigs = oqs.get_supported_sig_mechanisms()
        if "Dilithium2" in supported_sigs:
            self.sig_alg = "Dilithium2"
        elif "ML-DSA-44" in supported_sigs:
            self.sig_alg = "ML-DSA-44"
        elif "dilithium2" in supported_sigs:
            self.sig_alg = "dilithium2"
        else:
            self.sig_alg = supported_sigs[0] # Safe fallback

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
        """Signs a message using ML-DSA/Dilithium."""
        with oqs.Signature(self.sig_alg) as signer:
            signer_pub_key = signer.generate_keypair()
            signature = signer.sign(message)
            return signature, signer_pub_key

    def verify_signature(self, message, signature, public_key):
        """Verifies an ML-DSA/Dilithium signature."""
        with oqs.Signature(self.sig_alg) as verifier:
            is_valid = verifier.verify(message, signature, public_key)
            return is_valid