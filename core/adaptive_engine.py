class AdaptiveEngine:
    def __init__(self):
        # The cryptographically justified BB84 bound threshold
        self.qber_threshold = 0.11 
        self.current_gear = 3
        
    def evaluate_channel(self, qber_value, pqc_available=True):
        """
        Evaluates the QBER and determines the appropriate security gear.
        """
        print(f"[ENGINE] Current QBER measured at: {qber_value * 100:.2f}%")
        
        if qber_value <= self.qber_threshold and pqc_available:
            self.transition_to_gear(3)
        elif qber_value > self.qber_threshold and pqc_available:
            print("[WARNING] QBER threshold exceeded. Potential eavesdropping or high noise detected.")
            self.transition_to_gear(2)
        else:
            print("[CRITICAL] Quantum and Post-Quantum channels unavailable.")
            self.transition_to_gear(1)
            
        return self.current_gear

    def transition_to_gear(self, gear_level):
        if self.current_gear != gear_level:
            print(f"[TRANSITION] Switching from Gear {self.current_gear} to Gear {gear_level}")
            self.current_gear = gear_level
        else:
            print(f"[STATUS] Maintaining Gear {self.current_gear}")

    def get_active_cipher_suite(self):
        if self.current_gear == 3:
            return "QKD + ML-KEM + AES"
        elif self.current_gear == 2:
            return "ML-KEM + ML-DSA + AES"
        elif self.current_gear == 1:
            return "ECDH + AES"