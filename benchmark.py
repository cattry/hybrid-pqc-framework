import time
import json
import base64
from crypto_modules.classical import ClassicalCrypto
from crypto_modules.post_quantum import PostQuantumCrypto
from crypto_modules.quantum_bb84 import simulate_quantum_channel

def run_benchmarks(iterations=50):
    print(f"--- Running Cryptographic Benchmarks ({iterations} iterations) ---")
    
    classical = ClassicalCrypto()
    pq = PostQuantumCrypto()
    message = "This is a standard test message for payload benchmarking."
    
    # 1. Benchmark Gear 1: Classical ECDH
    start = time.perf_counter()
    for _ in range(iterations):
        priv, pub = classical.generate_ecdh_keypair()
        peer_priv, peer_pub = classical.generate_ecdh_keypair()
        secret = classical.derive_shared_secret(priv, peer_pub)
    ecdh_time = ((time.perf_counter() - start) / iterations) * 1000
    print(f"Gear 1 (ECDH) Key Exchange Avg Time: {ecdh_time:.3f} ms")
    
    # 2. Benchmark Gear 2: Post-Quantum ML-KEM
    start = time.perf_counter()
    for _ in range(iterations):
        kem_pub, kem_priv = pq.generate_kem_keypair()
        cipher, shared = pq.encapsulate_secret(kem_pub)
        decap_shared = pq.decapsulate_secret(cipher, kem_priv)
    kem_time = ((time.perf_counter() - start) / iterations) * 1000
    print(f"Gear 2 (ML-KEM) Key Exchange Avg Time: {kem_time:.3f} ms")
    
    # 3. Benchmark Gear 3: QKD (BB84 Simulation)
    start = time.perf_counter()
    for _ in range(iterations):
        simulate_quantum_channel(num_bits=128, noise_probability=0.05)
    bb84_time = ((time.perf_counter() - start) / iterations) * 1000
    print(f"Gear 3 (BB84 QKD 128-bit) Avg Time:   {bb84_time:.3f} ms")

    # 4. Benchmark ML-DSA Authentication
    start = time.perf_counter()
    for _ in range(iterations):
        sig, sig_pub = pq.sign_message(message.encode('utf-8'))
        pq.verify_signature(message.encode('utf-8'), sig, sig_pub)
    dsa_time = ((time.perf_counter() - start) / iterations) * 1000
    print(f"ML-DSA Sign & Verify Avg Time:        {dsa_time:.3f} ms")

    # 5. Payload Size Comparison
    _, ec_pub = classical.generate_ecdh_keypair()
    kem_pub, _ = pq.generate_kem_keypair()
    print("\n--- Payload Size Overhead ---")
    print(f"Classical ECDH Public Key Size: {len(ec_pub.public_bytes(encoding=getattr(__import__('cryptography.hazmat.primitives.serialization', fromlist=['Encoding']), 'Encoding').X962, format=getattr(__import__('cryptography.hazmat.primitives.serialization', fromlist=['PublicFormat']), 'PublicFormat').UncompressedPoint))} bytes")
    print(f"Post-Quantum ML-KEM Public Key Size: {len(kem_pub)} bytes")
    print(f"Post-Quantum ML-DSA Signature Size: {len(sig)} bytes")

if __name__ == "__main__":
    run_benchmarks()