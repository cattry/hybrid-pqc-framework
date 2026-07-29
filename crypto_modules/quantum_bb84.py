import random
from qiskit import QuantumCircuit
from qiskit_aer import Aer

def generate_random_bits(length):
    """Generates a list of random bits."""
    return [random.randint(0, 1) for _ in range(length)]

def encode_message(bits, bases):
    """Alice encodes bits into qubits based on randomly chosen bases."""
    encoded_qubits = []
    for i in range(len(bits)):
        qc = QuantumCircuit(1, 1)
        if bits[i] == 1:
            qc.x(0) # Apply X gate for bit 1
        if bases[i] == 1:
            qc.h(0) # Apply Hadamard gate for diagonal basis
        encoded_qubits.append(qc)
    return encoded_qubits

def measure_message(qubits, bases):
    """Bob measures the qubits based on his randomly chosen bases."""
    simulator = Aer.get_backend('qasm_simulator')
    measurements = []
    for i in range(len(qubits)):
        qc = qubits[i]
        if bases[i] == 1:
            qc.h(0) # Apply Hadamard before measurement for diagonal basis
        qc.measure(0, 0)
        result = simulator.run(qc, shots=1, memory=True).result()
        measured_bit = int(result.get_memory()[0])
        measurements.append(measured_bit)
    return measurements

def calculate_qber(alice_bits, bob_bits, alice_bases, bob_bases):
    """
    Compares Alice and Bob's bases to extract the sifted key and calculates QBER.
    """
    sifted_key_alice = []
    sifted_key_bob = []
    
    for i in range(len(alice_bases)):
        if alice_bases[i] == bob_bases[i]:
            sifted_key_alice.append(alice_bits[i])
            sifted_key_bob.append(bob_bits[i])
            
    # Calculate errors in the sifted keys
    errors = sum(1 for a, b in zip(sifted_key_alice, sifted_key_bob) if a != b)
    
    if len(sifted_key_alice) == 0:
        return 1.0 # 100% error if no matching bases
        
    qber = errors / len(sifted_key_alice)
    return qber, sifted_key_alice

def simulate_quantum_channel(num_bits=100, noise_probability=0.05):
    """Simulates the entire BB84 process over a noisy channel."""
    # Alice's preparation
    alice_bits = generate_random_bits(num_bits)
    alice_bases = generate_random_bits(num_bits)
    qubits = encode_message(alice_bits, alice_bases)
    
    # Introduce artificial noise/eavesdropping
    for qc in qubits:
        if random.random() < noise_probability:
            qc.x(0) # Bit flip error
            
    # Bob's measurement
    bob_bases = generate_random_bits(num_bits)
    bob_bits = measure_message(qubits, bob_bases)
    
    # Calculate QBER
    qber, shared_key = calculate_qber(alice_bits, bob_bits, alice_bases, bob_bases)
    return qber, shared_key