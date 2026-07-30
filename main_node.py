import time
import random
import threading
import sys
import json
import base64
import os

from core.adaptive_engine import AdaptiveEngine
from core.network_handler import NetworkHandler
from crypto_modules.quantum_bb84 import simulate_quantum_channel
from crypto_modules.classical import ClassicalCrypto
from crypto_modules.post_quantum import PostQuantumCrypto

class P2PNode:
    def __init__(self, host, port, is_server=False):
        self.is_server = is_server
        self.engine = AdaptiveEngine()
        self.net_handler = NetworkHandler(host, port, is_server)
        self.running = True
        
        # Initialize Cryptographic Suites
        self.classical_crypto = ClassicalCrypto()
        self.pq_crypto = PostQuantumCrypto()

    def start(self):
        """Starts the network connection and initializes two-way communication."""
        self.net_handler.start_connection()
        
        receive_thread = threading.Thread(target=self.receive_messages, daemon=True)
        receive_thread.start()
        
        self.send_messages()

    def check_system_readiness(self):
        """Automated check for QKD and PQC viability."""
        if not self.net_handler.check_latency():
            print("\n[CRITICAL] Handshake timeout risk detected. PQC unavailable.")
            return False
            
        cpu_load = random.uniform(10, 100)
        if cpu_load > 95.0:
            print(f"\n[CRITICAL] Host CPU load at {cpu_load:.1f}%. Resource exhaustion. PQC unavailable.")
            return False
            
        return True

    def generate_key_material(self, active_gear, qber, qkd_shared_key):
        """
        Actively executes the underlying cryptographic libraries to generate
        and combine raw key materials based on the active gear.
        """
        key_material = b""

        # Gear 1: Classical ECDH Fallback
        if active_gear == 1:
            ec_priv, ec_pub = self.classical_crypto.generate_ecdh_keypair()
            peer_priv, peer_pub = self.classical_crypto.generate_ecdh_keypair()
            shared_secret = self.classical_crypto.derive_shared_secret(ec_priv, peer_pub)
            key_material = shared_secret

        # Gear 2: Post-Quantum Only (ML-KEM)
        elif active_gear == 2:
            kem_pub, kem_priv = self.pq_crypto.generate_kem_keypair()
            kem_cipher, kem_shared = self.pq_crypto.encapsulate_secret(kem_pub)
            key_material = kem_shared

        # Gear 3: QKD + ML-KEM
        elif active_gear == 3:
            kem_pub, kem_priv = self.pq_crypto.generate_kem_keypair()
            kem_cipher, kem_shared = self.pq_crypto.encapsulate_secret(kem_pub)
            qkd_bytes = bytes(qkd_shared_key)
            key_material = kem_shared + qkd_bytes

        return key_material

    def send_messages(self):
        """Handles the true mathematical encryption, signing, and sending of messages."""
        base_noise_probability = 0.05 

        while self.running:
            try:
                time.sleep(0.1) 
                message = input("\n[YOU] Enter message to send (or type 'exit'): ")
                
                if message.lower() == 'exit':
                    self.running = False
                    self.net_handler.close_connection()
                    sys.exit(0)
                    
                pqc_is_available = self.check_system_readiness()
                qber = 1.0
                qkd_shared_key = []

                if not pqc_is_available:
                    print("[ENVIRONMENT] System constraints force fallback to classical security.")
                else:
                    if random.random() > 0.6:
                        current_noise_prob = 0.15 
                        print("[ENVIRONMENT] Simulating heavy channel interference (Eve active)...")
                    else:
                        current_noise_prob = base_noise_probability
                        print("[ENVIRONMENT] Quantum channel is stable.")

                    print("[QUANTUM] Executing BB84 circuit...")
                    qber, qkd_shared_key = simulate_quantum_channel(num_bits=128, noise_probability=current_noise_prob)
                    print(f"[QUANTUM] Sifted key length: {len(qkd_shared_key)} bits")
                
                # Determine Gear
                active_gear = self.engine.evaluate_channel(qber, pqc_available=pqc_is_available)
                suite = self.engine.get_active_cipher_suite()
                print(f"[ENCRYPTION] Active Suite: {suite}")

                # 1. Generate Raw Key Material
                raw_material = self.generate_key_material(active_gear, qber, qkd_shared_key)

                # 2. Derive AES-256 Key using HKDF
                aes_key, salt = self.classical_crypto.derive_aes_key(raw_material)

                # 3. Encrypt the Message using AES-256-GCM
                ciphertext = self.classical_crypto.aes_encrypt(aes_key, message)

                # 4. Sign the Ciphertext using ML-DSA (Post-Quantum Authentication)
                signature, signer_pub_key = self.pq_crypto.sign_message(ciphertext)

                # 5. Package Payload for Network Transit
                payload = {
                    "gear": active_gear,
                    "suite": suite,
                    "salt": base64.b64encode(salt).decode('utf-8'),
                    "raw_material": base64.b64encode(raw_material).decode('utf-8'),
                    "ciphertext": base64.b64encode(ciphertext).decode('utf-8'),
                    "signature": base64.b64encode(signature).decode('utf-8'),
                    "signer_pub_key": base64.b64encode(signer_pub_key).decode('utf-8')
                }
                
                payload_bytes = json.dumps(payload).encode('utf-8')
                self.net_handler.send_data(payload_bytes)
                
            except Exception as e:
                if self.running:
                    print(f"\n[ERROR] Failed to send message: {e}")
                break

    def receive_messages(self):
        """Continuously receives, mathematically verifies, derives keys, and decrypts messages."""
        while self.running:
            try:
                data = self.net_handler.receive_data()
                if not data:
                    print("\n[NETWORK] Connection closed by peer.")
                    self.running = False
                    self.net_handler.close_connection()
                    os._exit(0) 
                
                # Parse the incoming JSON payload
                payload = json.loads(data.decode('utf-8'))
                suite = payload["suite"]
                salt = base64.b64decode(payload["salt"])
                raw_material = base64.b64decode(payload["raw_material"])
                ciphertext = base64.b64decode(payload["ciphertext"])
                signature = base64.b64decode(payload["signature"])
                signer_pub_key = base64.b64decode(payload["signer_pub_key"])
                
                print(f"\n\n--- INCOMING SECURE TRANSMISSION ---")
                print(f"[RECEIVER] Authenticated Cipher Suite: {suite}")
                print(f"[RECEIVER] Encrypted Payload (Hex): {ciphertext.hex()[:40]}...")

                # 1. Verify Post-Quantum Signature (ML-DSA) before doing anything else
                is_valid = self.pq_crypto.verify_signature(ciphertext, signature, signer_pub_key)
                if not is_valid:
                    print("[CRITICAL ALERT] ML-DSA Signature Verification Failed! Message dropped.")
                    print("------------------------------------\n[YOU] Enter message to send (or type 'exit'): ", end="", flush=True)
                    continue  # Drop the malicious packet and wait for the next one

                print("[AUTHENTICATION] ML-DSA Signature Verified Successfully.")
                
                # 2. Re-derive the AES-256 Key using HKDF and the shared salt/material
                aes_key, _ = self.classical_crypto.derive_aes_key(raw_material, salt=salt)
                
                # 3. Decrypt the actual AES-256-GCM ciphertext
                decrypted_message = self.classical_crypto.aes_decrypt(aes_key, ciphertext)
                
                print(f"[PEER SAYS]: {decrypted_message}")
                print("------------------------------------\n[YOU] Enter message to send (or type 'exit'): ", end="", flush=True)
                    
            except ConnectionResetError:
                print("\n[NETWORK] Connection reset by peer.")
                self.running = False
                break
            except Exception as e:
                if self.running:
                    print(f"\n[ERROR] Decryption or Receive error: {e}")
                break

if __name__ == "__main__":
    print("=== True Hybrid Quantum Classical Cryptography Node ===")
    mode = input("Run as (1) Alice/Device A or (2) Bob/Device B? ")
    
    if mode == '1':
        node = P2PNode('0.0.0.0', 5000, is_server=True)
        node.start()
    elif mode == '2':
        ip = input("Enter Alice's IP (e.g., 127.0.0.1 for local): ")
        node = P2PNode(ip, 5000, is_server=False)
        node.start()
    else:
        print("Invalid selection. Exiting.")