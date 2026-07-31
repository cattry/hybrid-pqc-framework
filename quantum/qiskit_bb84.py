"""
quantum/qiskit_bb84.py

High-level interface function replacing the mock/pure-Python measurement function.
"""

import random
from quantum.encoder import prepare_qubit
from quantum.decoder import measure_qubit


def generate_bits(n: int) -> list[int]:
    """Generate n random bits."""
    return [random.randint(0, 1) for _ in range(n)]


def generate_bases(n: int) -> list[str]:
    """Generate n random bases ('+' or 'x')."""
    return [random.choice(["+", "x"]) for _ in range(n)]


def run_bb84_qubits(alice_bits: list[int],
                    alice_bases: list[str],
                    bob_bases: list[str],
                    noise_level: float = 0.08) -> list[int]:
    """
    Simulates sending n qubits from Alice to Bob over a noisy quantum channel
    using Qiskit Aer.
    """
    bob_measurements = []

    for bit, a_basis, b_basis in zip(alice_bits, alice_bases, bob_bases):
        # 1. Alice encodes bit & basis into a QuantumCircuit
        qc = prepare_qubit(bit, a_basis)

        # 2. Bob measures the qubit on AerSimulator with noisy channel
        measured_bit = measure_qubit(qc, b_basis, noise_level=noise_level)

        bob_measurements.append(measured_bit)

    return bob_measurements