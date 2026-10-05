import time
import random
import threading
import json
import base64
import os
import customtkinter as ctk

from core.adaptive_engine import AdaptiveEngine
from core.network_handler import NetworkHandler
from crypto_modules.quantum_bb84 import simulate_quantum_channel
from crypto_modules.classical import ClassicalCrypto
from crypto_modules.post_quantum import PostQuantumCrypto

# Configure the modern aesthetic
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class QuantumNodeGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Hybrid Quantum-Classical Secure P2P Node")
        self.geometry("1050x650")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Core Backend Instances
        self.engine = AdaptiveEngine()
        self.classical_crypto = ClassicalCrypto()
        self.pq_crypto = PostQuantumCrypto()
        self.net_handler = None
        self.running = False
        
        self.build_setup_screen()

    def build_setup_screen(self):
        """Displays the initial connection configuration screen."""
        self.setup_frame = ctk.CTkFrame(self)
        self.setup_frame.pack(pady=150, padx=200, fill="both", expand=True)
        
        title = ctk.CTkLabel(self.setup_frame, text="NODE INITIALIZATION", font=("Roboto", 24, "bold"))
        title.pack(pady=30)
        
        self.role_var = ctk.StringVar(value="server")
        
        role_frame = ctk.CTkFrame(self.setup_frame, fg_color="transparent")
        role_frame.pack(pady=10)
        ctk.CTkRadioButton(role_frame, text="Run as Alice (Server / Listen)", variable=self.role_var, value="server").pack(side="left", padx=10)
        ctk.CTkRadioButton(role_frame, text="Run as Bob (Client / Connect)", variable=self.role_var, value="client").pack(side="left", padx=10)
        
        self.ip_entry = ctk.CTkEntry(self.setup_frame, placeholder_text="Enter IP (e.g., 127.0.0.1 or leave blank for Server)", width=300)
        self.ip_entry.pack(pady=20)
        
        connect_btn = ctk.CTkButton(self.setup_frame, text="ESTABLISH SECURE LINK", command=self.initialize_connection, height=40)
        connect_btn.pack(pady=20)

    def initialize_connection(self):
        """Initializes the network sockets based on GUI input."""
        is_server = self.role_var.get() == "server"
        host = "0.0.0.0" if is_server else self.ip_entry.get().strip()
        
        if not is_server and not host:
            return  # Prevent empty IP on client
            
        self.setup_frame.destroy()
        self.build_dashboard()
        
        self.net_handler = NetworkHandler(host, 5000, is_server)
        self.running = True
        
        # Start connection in a background thread to prevent freezing the GUI
        threading.Thread(target=self._connect_and_listen, daemon=True).start()

    def _connect_and_listen(self):
        self.log_system("Attempting network connection...")
        try:
            self.net_handler.start_connection()
            self.log_system("Secure socket established. Awaiting data...")
            self.receive_messages()
        except Exception as e:
            self.log_system(f"Connection Error: {e}")

    def build_dashboard(self):
        """Builds the main communication and telemetry dashboard."""
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # --- Left Sidebar: Telemetry & Security ---
        self.sidebar = ctk.CTkFrame(self, width=300, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        logo_label = ctk.CTkLabel(self.sidebar, text="ADAPTIVE ENGINE", font=("Roboto", 20, "bold"))
        logo_label.pack(pady=20)
        
        # Stats
        self.gear_label = ctk.CTkLabel(self.sidebar, text="Current Gear: STANDBY", font=("Roboto", 14))
        self.gear_label.pack(pady=5, anchor="w", padx=20)
        
        self.suite_label = ctk.CTkLabel(self.sidebar, text="Suite: Awaiting Handshake", font=("Roboto", 14))
        self.suite_label.pack(pady=5, anchor="w", padx=20)
        
        self.qber_label = ctk.CTkLabel(self.sidebar, text="Last QBER: 0.00%", font=("Roboto", 14))
        self.qber_label.pack(pady=5, anchor="w", padx=20)
        
        # System Logs
        ctk.CTkLabel(self.sidebar, text="SYSTEM LOGS", font=("Roboto", 12, "bold")).pack(pady=(30, 0), anchor="w", padx=20)
        self.sys_logs = ctk.CTkTextbox(self.sidebar, height=350, fg_color="#1e1e1e", text_color="#00ffcc")
        self.sys_logs.pack(pady=10, padx=20, fill="x")
        self.sys_logs.configure(state="disabled")
        
        # --- Right Main Area: Secure Chat ---
        self.main_area = ctk.CTkFrame(self, fg_color="transparent")
        self.main_area.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.main_area.grid_rowconfigure(0, weight=1)
        self.main_area.grid_columnconfigure(0, weight=1)
        
        self.chat_display = ctk.CTkTextbox(self.main_area, font=("Consolas", 14))
        self.chat_display.grid(row=0, column=0, columnspan=2, sticky="nsew", pady=(0, 10))
        self.chat_display.configure(state="disabled")
        
        self.msg_entry = ctk.CTkEntry(self.main_area, placeholder_text="Type secure message here...", height=40)
        self.msg_entry.grid(row=1, column=0, sticky="ew", padx=(0, 10))
        self.msg_entry.bind("<Return>", lambda event: self.send_message())
        
        self.send_btn = ctk.CTkButton(self.main_area, text="ENCRYPT & SEND", command=self.send_message, height=40, font=("Roboto", 12, "bold"))
        self.send_btn.grid(row=1, column=1)

    def log_system(self, message):
        """Safely updates the system log terminal."""
        self.sys_logs.configure(state="normal")
        self.sys_logs.insert("end", f"> {message}\n")
        self.sys_logs.see("end")
        self.sys_logs.configure(state="disabled")

    def display_chat(self, sender, message, metadata=""):
        """Displays messages in the main chat window."""
        self.chat_display.configure(state="normal")
        if sender == "YOU":
            self.chat_display.insert("end", f"[YOU]: {message}\n", "you")
        else:
            self.chat_display.insert("end", f"\n[PEER]: {message}\n", "peer")
            if metadata:
                self.chat_display.insert("end", f"   └─ {metadata}\n")
        self.chat_display.see("end")
        self.chat_display.configure(state="disabled")

    def update_telemetry(self, gear, suite, qber):
        """Updates the left sidebar labels."""
        self.gear_label.configure(text=f"Current Gear: {gear}")
        self.suite_label.configure(text=f"Suite: {suite}")
        self.qber_label.configure(text=f"Last QBER: {qber * 100:.2f}%")

    def send_message(self):
        """The cryptographic pipeline executed on button press."""
        message = self.msg_entry.get().strip()
        if not message or not self.running: return
        self.msg_entry.delete(0, "end")
        
        # Run encryption in background to keep GUI responsive
        threading.Thread(target=self._encrypt_and_transmit, args=(message,), daemon=True).start()

    def _encrypt_and_transmit(self, message):
        try:
            self.display_chat("YOU", message)
            self.log_system("Initiating Quantum Channel assessment...")
            
            pqc_is_available = self.check_system_readiness()
            current_noise_prob = 0.15 if random.random() > 0.6 else 0.05
            
            qber = 1.0
            qkd_shared_key = []
            
            if pqc_is_available:
                qber, qkd_shared_key = simulate_quantum_channel(num_bits=128, noise_probability=current_noise_prob)
                self.log_system(f"BB84 Sifted Key Length: {len(qkd_shared_key)} bits")
            
            active_gear = self.engine.evaluate_channel(qber, pqc_available=pqc_is_available)
            suite = self.engine.get_active_cipher_suite()
            
            # Update GUI Telemetry
            self.update_telemetry(active_gear, suite, qber)
            self.log_system(f"Engaging {suite}")

            # Cryptographic Operations
            raw_material = self.generate_key_material(active_gear, qber, qkd_shared_key)
            aes_key, salt = self.classical_crypto.derive_aes_key(raw_material)
            ciphertext = self.classical_crypto.aes_encrypt(aes_key, message)
            signature, signer_pub_key = self.pq_crypto.sign_message(ciphertext)

            # Transmit
            payload = {
                "gear": active_gear,
                "suite": suite,
                "salt": base64.b64encode(salt).decode('utf-8'),
                "raw_material": base64.b64encode(raw_material).decode('utf-8'),
                "ciphertext": base64.b64encode(ciphertext).decode('utf-8'),
                "signature": base64.b64encode(signature).decode('utf-8'),
                "signer_pub_key": base64.b64encode(signer_pub_key).decode('utf-8')
            }
            
            self.net_handler.send_data(json.dumps(payload).encode('utf-8'))
            self.log_system("Encrypted payload transmitted successfully.")
            
        except Exception as e:
            self.log_system(f"Transmission Error: {e}")

    def receive_messages(self):
        """Continuously listens and decrypts incoming messages."""
        while self.running:
            try:
                data = self.net_handler.receive_data()
                if not data:
                    self.log_system("Connection closed by peer.")
                    self.running = False
                    break
                
                payload = json.loads(data.decode('utf-8'))
                suite = payload["suite"]
                salt = base64.b64decode(payload["salt"])
                raw_material = base64.b64decode(payload["raw_material"])
                ciphertext = base64.b64decode(payload["ciphertext"])
                signature = base64.b64decode(payload["signature"])
                signer_pub_key = base64.b64decode(payload["signer_pub_key"])
                
                self.log_system(f"Incoming payload detected. Suite: {suite}")
                
                # ML-DSA Authentication
                is_valid = self.pq_crypto.verify_signature(ciphertext, signature, signer_pub_key)
                if not is_valid:
                    self.log_system("[ALERT] ML-DSA verification failed. Dropping packet.")
                    continue
                
                self.log_system("ML-DSA signature verified.")
                
                # AES Decryption
                aes_key, _ = self.classical_crypto.derive_aes_key(raw_material, salt=salt)
                decrypted_message = self.classical_crypto.aes_decrypt(aes_key, ciphertext)
                
                meta = f"[Verified via {suite} | Auth: ML-DSA]"
                self.display_chat("PEER", decrypted_message, metadata=meta)
                
            except Exception as e:
                if self.running:
                    self.log_system(f"Receive Error: {e}")

    # --- Core Backend Methods (Adapted from main_node_4.py) ---
    def check_system_readiness(self):
        if not self.net_handler.check_latency():
            self.log_system("Network latency high. PQC unavailable.")
            return False
        if random.uniform(10, 100) > 95.0:
            self.log_system("CPU constrained. PQC unavailable.")
            return False
        return True

    def generate_key_material(self, active_gear, qber, qkd_shared_key):
        key_material = b""
        if active_gear == 1:
            ec_priv, ec_pub = self.classical_crypto.generate_ecdh_keypair()
            peer_priv, peer_pub = self.classical_crypto.generate_ecdh_keypair()
            key_material = self.classical_crypto.derive_shared_secret(ec_priv, peer_pub)
        elif active_gear == 2:
            kem_pub, kem_priv = self.pq_crypto.generate_kem_keypair()
            kem_cipher, kem_shared = self.pq_crypto.encapsulate_secret(kem_pub)
            key_material = kem_shared
        elif active_gear == 3:
            kem_pub, kem_priv = self.pq_crypto.generate_kem_keypair()
            kem_cipher, kem_shared = self.pq_crypto.encapsulate_secret(kem_pub)
            key_material = kem_shared + bytes(qkd_shared_key)
        return key_material

    def on_closing(self):
        self.running = False
        if self.net_handler:
            try: self.net_handler.close_connection()
            except: pass
        self.destroy()
        os._exit(0)

if __name__ == "__main__":
    app = QuantumNodeGUI()
    app.mainloop()