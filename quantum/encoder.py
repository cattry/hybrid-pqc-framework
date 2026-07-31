"""
quantum/encoder.py

Encodes Alice's bit and basis into a 1-qubit Qiskit QuantumCircuit.
"""

from qiskit import QuantumCircuit


def prepare_qubit(bit: int, basis: str) -> QuantumCircuit:
    """
    Encodes a single bit into a qubit according to the BB84 protocol.

    BB84 Encoding:
      - Bit 0, Basis Z ('+') -> |0> (No gates)
      - Bit 1, Basis Z ('+') -> |1> (X gate)
      - Bit 0, Basis X ('x') -> |+> (H gate)
      - Bit 1, Basis X ('x') -> |-> (X gate then H gate)
    """
    qc = QuantumCircuit(1, 1)

    # Apply Pauli-X gate if bit is 1
    if bit == 1:
        qc.x(0)

    # Apply Hadamard gate if basis is Diagonal ('x' or 'X')
    if basis.upper() == "X":
        qc.h(0)

    return qc