"""
error_correction.py

Simplified Cascade-inspired Information Reconciliation

Phase 3 - Part 1
"""
import random
import copy
import hashlib
from typing import List, Tuple, Dict, Any


# ============================================================
# Utility Functions
# ============================================================

def calculate_parity(bits: List[int]) -> int:
    """
    Returns the parity of a list of bits.

    Even number of 1s -> 0
    Odd number of 1s  -> 1
    """
    parity = 0
    for bit in bits:
        parity ^= bit
    return parity


# ============================================================

def split_into_blocks(key: List[int], block_size: int) -> List[List[int]]:
    """
    Split the key into fixed-size blocks.
    """
    blocks = []
    for i in range(0, len(key), block_size):
        blocks.append(key[i:i + block_size])
    return blocks


# ============================================================

def parity_matches(block_a: List[int], block_b: List[int]) -> bool:
    """
    Compare parity of two blocks.
    """
    return calculate_parity(block_a) == calculate_parity(block_b)


# ============================================================

def print_blocks(blocks: List[List[int]]) -> None:
    """
    Debug helper.
    """
    for i, block in enumerate(blocks):
        print(
            f"Block {i+1}:",
            "".join(map(str, block)),
            "Parity =",
            calculate_parity(block)
        )


# ============================================================

def compare_blocks(alice_key: List[int],
                   bob_key: List[int],
                   block_size: int) -> List[int]:
    """
    Compare Alice and Bob block parities.

    Returns the indices of mismatching blocks.
    """
    alice_blocks = split_into_blocks(alice_key, block_size)
    bob_blocks = split_into_blocks(bob_key, block_size)

    mismatches = []

    print("\n========== BLOCK PARITY CHECK ==========\n")

    for i, (a, b) in enumerate(zip(alice_blocks, bob_blocks)):
        alice_parity = calculate_parity(a)
        bob_parity = calculate_parity(b)

        print(f"Block {i+1}")
        print("Alice:", "".join(map(str, a)), "| Parity:", alice_parity)
        print("Bob  :", "".join(map(str, b)), "| Parity:", bob_parity)

        if alice_parity != bob_parity:
            print("Mismatch Found\n")
            mismatches.append(i)
        else:
            print("Match\n")

    return mismatches


# ============================================================

def recursive_binary_search(alice_block: List[int],
                            bob_block: List[int],
                            offset: int = 0) -> int:
    """
    Locate ONE erroneous bit using recursive parity checks.

    Returns the bit index in the ORIGINAL key.
    If no error exists, returns -1.
    """
    if len(alice_block) == 1:
        if alice_block[0] != bob_block[0]:
            return offset
        return -1

    mid = len(alice_block) // 2

    alice_left = alice_block[:mid]
    alice_right = alice_block[mid:]

    bob_left = bob_block[:mid]
    bob_right = bob_block[mid:]

    if calculate_parity(alice_left) != calculate_parity(bob_left):
        return recursive_binary_search(
            alice_left,
            bob_left,
            offset
        )

    return recursive_binary_search(
        alice_right,
        bob_right,
        offset + mid
    )


# ============================================================

def flip_bit(key: List[int], index: int) -> None:
    """
    Flip one bit in-place.

    0 -> 1
    1 -> 0
    """
    key[index] ^= 1


# ============================================================

def calculate_qber(alice_key: List[int], bob_key: List[int]) -> float:
    """
    Calculate Quantum Bit Error Rate.
    """
    if len(alice_key) == 0:
        return 0.0

    errors = sum(a != b for a, b in zip(alice_key, bob_key))
    return errors / len(alice_key)


# ============================================================

def correct_errors(alice_key: List[int],
                   bob_key: List[int],
                   block_size: int = 4) -> Tuple[List[int], int]:
    """
    Correct every block that has an odd number of errors (mismatched parity).
    """
    corrected_key = bob_key.copy()

    mismatches = compare_blocks(
        alice_key,
        corrected_key,
        block_size
    )

    corrections = 0
    alice_blocks = split_into_blocks(alice_key, block_size)
    bob_blocks = split_into_blocks(corrected_key, block_size)
    for block_index in mismatches:

        location = recursive_binary_search(
            alice_blocks[block_index],
            bob_blocks[block_index],
            block_index * block_size
        )

        if location != -1:
            print(f"\nCorrecting bit at index {location}")
            flip_bit(corrected_key, location)
            corrections += 1

    return corrected_key, corrections


# ============================================================

def shuffle_key(key: List[int]) -> Tuple[List[int], List[int]]:
    """
    Randomly shuffle a key.
    """
    permutation = list(range(len(key)))
    random.shuffle(permutation)
    shuffled = [key[i] for i in permutation]
    return shuffled, permutation


# ============================================================

def unshuffle_key(shuffled_key: List[int], permutation: List[int]) -> List[int]:
    """
    Restore shuffled key to original order.
    """
    original = [0] * len(shuffled_key)
    for shuffled_index, original_index in enumerate(permutation):
        original[original_index] = shuffled_key[shuffled_index]
    return original


# ============================================================

def cascade_reconciliation(alice_key: List[int],
                           bob_key: List[int],
                           passes: int = 4,
                           initial_block_size: int = 4) -> Tuple[List[int], List[Dict[str, Any]]]:
    """
    Simplified Cascade Information Reconciliation.
    """
    corrected = bob_key.copy()
    history = []
    block_size = initial_block_size

    for current_pass in range(1, passes + 1):
        print("\n" + "=" * 60)
        print(f"PASS {current_pass}")
        print("=" * 60)

        shuffled_alice, permutation = shuffle_key(alice_key)
        shuffled_bob = [corrected[i] for i in permutation]

        before = calculate_qber(shuffled_alice, shuffled_bob)

        shuffled_bob, corrections = correct_errors(
            shuffled_alice,
            shuffled_bob,
            block_size
        )

        after = calculate_qber(shuffled_alice, shuffled_bob)

        corrected = unshuffle_key(shuffled_bob, permutation)

        history.append({
            "pass": current_pass,
            "block_size": block_size,
            "before_qber": before,
            "after_qber": after,
            "corrections": corrections
        })

        block_size *= 2

    return corrected, history


# ============================================================

def bits_to_bytes(bits: List[int]) -> bytes:
    """
    Convert a list of bits into bytes.
    """
    bit_string = "".join(map(str, bits))

    while len(bit_string) % 8 != 0:
        bit_string += "0"

    return int(bit_string, 2).to_bytes(
        len(bit_string) // 8,
        byteorder="big"
    )


# ============================================================

def privacy_amplification(corrected_key: List[int]) -> Dict[str, Any]:
    """
    Apply SHA-256 for privacy amplification.
    """
    key_bytes = bits_to_bytes(corrected_key)
    digest = hashlib.sha256(key_bytes).digest()

    return {
        "session_key": digest,
        "hex_key": digest.hex().upper(),
        "length": len(digest)
    }


# ============================================================

def hex_key(key: bytes) -> str:
    """
    Convert bytes to an uppercase hex string.
    """
    return key.hex().upper()


# ============================================================
# Main Execution
# ============================================================

if __name__ == "__main__":

    random.seed(10)

    KEY_SIZE = 64

    alice_key = [random.randint(0, 1) for _ in range(KEY_SIZE)]
    bob_key = copy.deepcopy(alice_key)

    # Inject errors
    error_positions = [7, 18, 29, 47]
    for position in error_positions:
        bob_key[position] ^= 1

    print("=" * 70)
    print("INITIAL")
    print("=" * 70)

    initial_qber = calculate_qber(alice_key, bob_key)
    print("Initial QBER:", f"{initial_qber:.2%}")

    corrected_key, history = cascade_reconciliation(
        alice_key,
        bob_key,
        passes=4,
        initial_block_size=4
    )

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    final_qber = calculate_qber(alice_key, corrected_key)

    for record in history:
        print()
        print(f"Pass {record['pass']}")
        print("Block Size :", record["block_size"])
        print("Corrections:", record["corrections"])
        print("QBER Before:", f"{record['before_qber']:.2%}")
        print("QBER After :", f"{record['after_qber']:.2%}")

    print()
    print("Final QBER:", f"{final_qber:.2%}")

    print("\n" + "=" * 70)
    print("PRIVACY AMPLIFICATION")
    print("=" * 70)

    session = privacy_amplification(corrected_key)

    # Print the hex representation from dictionary
    print("Session Key (Hex):", session["hex_key"])
    print("Key Length       :", session["length"], "bytes")
    print("Format           : AES-256 Session Key")