import random

def generate_bits(n):
    return [random.randint(0, 1) for _ in range(n)]

def generate_bases(n):
    return [random.choice(["+", "x"]) for _ in range(n)]

# Step 11: Updated measure function to include configurable noise
def measure(alice_bits, alice_bases, bob_bases, noise=0.0):
    bob_bits = []

    for bit, a_basis, b_basis in zip(alice_bits, alice_bases, bob_bases):
        # 1. Base measurement
        if a_basis == b_basis:
            measured = bit
        else:
            measured = random.randint(0, 1)

        # 2. Channel Noise flip (bitwise XOR flips 0->1 or 1->0)
        if random.random() < noise:
            measured ^= 1

        bob_bits.append(measured)

    return bob_bits

# Step 12: Eavesdropper simulation (Intercept-Resend)
def eve_intercept(bits, bases):
    eve_bases = generate_bases(len(bits))
    eve_bits = measure(bits, bases, eve_bases)
    return eve_bits, eve_bases

def sift_key(bits, alice_bases, bob_bases):
    """
    Keep only the bits where Alice and Bob
    used the same basis.
    """

    key = []

    for bit, a_basis, b_basis in zip(bits,
                                     alice_bases,
                                     bob_bases):

        if a_basis == b_basis:
            key.append(bit)

    return key


def sift_indices(alice_bases, bob_bases):
    """
    Return matching basis positions.
    """

    indices = []

    for i, (a, b) in enumerate(zip(alice_bases,
                                   bob_bases)):

        if a == b:
            indices.append(i)

    return indices

def calculate_qber(alice_key, bob_key):
    if not alice_key:
        return 0.0
    errors = sum(a != b for a, b in zip(alice_key, bob_key))
    return errors / len(alice_key)

def measure_qubits(alice_bits, alice_bases, bob_bases, noise=0.0):
    """
    Wrapper used by the networking layer.
    """
    return measure(
        alice_bits,
        alice_bases,
        bob_bases,
        noise
    )

if __name__ == "__main__":
    # Increased N to 10,000 so statistical QBER averages out accurately
    N = 10000

    alice_bits = generate_bits(N)
    alice_bases = generate_bases(N)

    # --- Step 11 Test: Channel Noise (10%) without Eve ---
    bob_bases_noise = generate_bases(N)
    bob_bits_noise = measure(alice_bits, alice_bases, bob_bases_noise, noise=0.10)

    a_key_noise = sift_key(alice_bits, alice_bases, bob_bases_noise)
    b_key_noise = sift_key(bob_bits_noise, alice_bases, bob_bases_noise)
    qber_noise = calculate_qber(a_key_noise, b_key_noise)

    print(f"--- Step 11: Noise (10%) ---")
    print(f"QBER = {qber_noise:.4f} (Expected ≈ 0.10)")

    # --- Step 12 Test: Eve Intercept-Resend (no noise) ---
    eve_bits, eve_bases = eve_intercept(alice_bits, alice_bases)

    bob_bases_eve = generate_bases(N)
    bob_bits_eve = measure(eve_bits, eve_bases, bob_bases_eve, noise=0.0)

    a_key_eve = sift_key(alice_bits, alice_bases, bob_bases_eve)
    b_key_eve = sift_key(bob_bits_eve, alice_bases, bob_bases_eve)
    qber_eve = calculate_qber(a_key_eve, b_key_eve)

    print(f"\n--- Step 12: Eve Intercept-Resend ---")
    print(f"QBER = {qber_eve:.4f} (Expected ≈ 0.25)")