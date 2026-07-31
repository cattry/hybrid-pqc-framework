"""
quantum/decoder.py

Handles Bob's basis transformation, noisy channel simulation, and measurement.
"""

from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error


def build_noisy_channel(noise_level: float = 0.0) -> NoiseModel:
    """
    Creates a physical depolarizing quantum noise model.
    """
    noise_model = NoiseModel()
    if noise_level > 0.0:
        # Depolarizing error simulates quantum channel decoherence
        error = depolarizing_error(noise_level, 1)
        noise_model.add_all_qubit_quantum_error(error, ["h", "x", "measure"])
    return noise_model


def measure_qubit(qc: QuantumCircuit, bob_basis: str, noise_level: float = 0.08) -> int:
    """
    Applies Bob's basis transformation, executes on AerSimulator with noise,
    and returns Bob's measured bit (0 or 1).
    """
    # Create a copy so we don't mutate Alice's original circuit reference
    meas_circuit = qc.copy()

    # If Bob measures in X-basis, rotate back to Z-basis using Hadamard gate
    if bob_basis.upper() == "X":
        meas_circuit.h(0)

    # Measure qubit into classical bit register
    meas_circuit.measure(0, 0)

    # Configure AerSimulator with Noise Model
    noise_model = build_noisy_channel(noise_level)
    simulator = AerSimulator(noise_model=noise_model)

    # Execute 1 shot
    result = simulator.run(meas_circuit, shots=1).result()
    counts = result.get_counts()

    # Get string key '0' or '1' and convert to integer
    measured_bit = int(list(counts.keys())[0])

    return measured_bit