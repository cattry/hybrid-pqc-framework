import time
import random
import threading
import sys
from core.adaptive_engine import AdaptiveEngine
from core.network_handler import NetworkHandler
from crypto_modules.quantum_bb84 import simulate_quantum_channel

class P2PNode:
    def __init__(self, host, port, is_server=False):
        self.is_server = is_server
        self.engine = AdaptiveEngine()
        self.net_handler = NetworkHandler(host, port, is_server)
        self.running = True

    def start(self):
        """Starts the network connection and initializes two-way communication."""
        self.net_handler.start_connection()
        
        # Start a background thread to constantly listen for incoming messages
        receive_thread = threading.Thread(target=self.receive_messages, daemon=True)
        receive_thread.start()
        
        # Run the sending loop on the main thread
        self.send_messages()

    def check_system_readiness(self):
        """
        Automated production check for QKD and PQC viability.
        Returns True if PQC/QKD is feasible, False if fallback to Gear 1 is required.
        """
        # 1. Check Network Latency
        network_stable = self.net_handler.check_latency()
        if not network_stable:
            print("\n[CRITICAL] Handshake timeout risk detected. PQC unavailable.")
            return False
            
        # 2. Simulate CPU/Memory Resource Exhaustion check
        cpu_load = random.uniform(10, 100)
        if cpu_load > 95.0:
            print(f"\n[CRITICAL] Host CPU load at {cpu_load:.1f}%. Resource exhaustion. PQC unavailable.")
            return False
            
        return True

    def send_messages(self):
        """Handles the sending of messages while evaluating channel security."""
        base_noise_probability = 0.05 

        while self.running:
            try:
                # Add a slight delay so incoming messages don't completely bury the prompt
                time.sleep(0.1) 
                message = input("\n[YOU] Enter message to send (or type 'exit'): ")
                
                if message.lower() == 'exit':
                    self.running = False
                    self.net_handler.close_connection()
                    sys.exit(0)
                    
                # Automated Production Health Check
                pqc_is_available = self.check_system_readiness()

                if not pqc_is_available:
                    print("[ENVIRONMENT] System constraints force fallback to classical security.")
                    qber = 1.0  
                else:
                    # Simulate dynamic physical quantum channel environment
                    if random.random() > 0.6:
                        current_noise_prob = 0.15 
                        print("[ENVIRONMENT] Simulating heavy channel interference (Eve active)...")
                    else:
                        current_noise_prob = base_noise_probability
                        print("[ENVIRONMENT] Quantum channel is stable.")

                    print("[QUANTUM] Preparing qubits and executing BB84 circuit...")
                    qber, shared_key = simulate_quantum_channel(num_bits=128, noise_probability=current_noise_prob)
                    print(f"[QUANTUM] Sifted key length: {len(shared_key)} bits")
                
                # The Engine automatically handles the Gear transition
                active_gear = self.engine.evaluate_channel(qber, pqc_available=pqc_is_available)
                suite = self.engine.get_active_cipher_suite()
                
                print(f"[ENCRYPTION] Encrypting using {suite}...")
                
                if pqc_is_available:
                    encrypted_payload = f"ENCRYPTED[{message}]_VIA_{suite}_(QBER:{qber*100:.2f}%)"
                else:
                    encrypted_payload = f"ENCRYPTED[{message}]_VIA_{suite}_(NO_QUANTUM_CHANNEL)"
                
                self.net_handler.send_data(encrypted_payload.encode('utf-8'))
                
            except Exception as e:
                if self.running:
                    print(f"\n[ERROR] Failed to send message: {e}")
                break

    def receive_messages(self):
        """Runs in a background thread to continuously receive messages."""
        while self.running:
            try:
                data = self.net_handler.receive_data()
                if not data:
                    print("\n[NETWORK] Connection closed by peer.")
                    self.running = False
                    self.net_handler.close_connection()
                    # Exit the program aggressively if the other side disconnects
                    os._exit(0) 
                
                decoded_data = data.decode('utf-8')
                print(f"\n\n--- INCOMING MESSAGE ---")
                print(f"[RECEIVER] Payload: {decoded_data}")
                print("[DECRYPTION] Decrypting message...")
                
                if "ENCRYPTED[" in decoded_data and "]_VIA_" in decoded_data:
                    decrypted = decoded_data.split('[')[1].split(']')[0]
                    print(f"[PEER SAYS]: {decrypted}")
                    print("------------------------\n[YOU] Enter message to send (or type 'exit'): ", end="", flush=True)
                else:
                    print(f"[RECEIVER] Unrecognized Payload Format: {decoded_data}\n")
                    
            except ConnectionResetError:
                print("\n[NETWORK] Connection reset by peer.")
                self.running = False
                break
            except Exception as e:
                if self.running:
                    print(f"\n[ERROR] Receive error: {e}")
                break

if __name__ == "__main__":
    import os
    print("=== Hybrid Quantum Classical Cryptography P2P Node ===")
    mode = input("Run as (1) Alice/Device A or (2) Bob/Device B? ")
    
    # We no longer strictly distinguish "Server" vs "Client" behavior after connection
    # It purely determines who binds to the port and who connects to it.
    if mode == '1':
        node = P2PNode('0.0.0.0', 5000, is_server=True)
        node.start()
    elif mode == '2':
        ip = input("Enter Alice's IP (e.g., 127.0.0.1 for local): ")
        node = P2PNode(ip, 5000, is_server=False)
        node.start()
    else:
        print("Invalid selection. Exiting.")