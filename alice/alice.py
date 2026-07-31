"""
alice/alice.py

Alice (BB84 Sender)

Phase 9: Cascade Reconciliation -> Key Verification -> Privacy Amplification -> AES
"""

import os
import sys

# ----------------------------------------------------
# Allow imports from project root
# ----------------------------------------------------

sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            ".."
        )
    )
)

# ----------------------------------------------------
# Imports
# ----------------------------------------------------

from network.client import Client
from network.protocol import send_packet, receive_packet
from network.messages import MessageType

from crypto.bb84 import (
    generate_bits,
    generate_bases,
    sift_key,
    sift_indices
)

from crypto.error_correction import calculate_qber, calculate_parity

from network.reconciliation import (
    start_reconciliation,
    request_parity,
    locate_error,
    send_correction
)

from crypto.key_verification import key_hash

from crypto.privacy import (
    privacy_amplification,
    digest_to_hex
)

from crypto.aes import encrypt_message

# ----------------------------------------------------

HOST = "127.0.0.1"
PORT = 5000
NUM_BITS = 64


# ----------------------------------------------------

def main():

    print("=" * 60)
    print("ALICE")
    print("=" * 60)

    # ------------------------------------------------
    # Generate BB84 Data
    # ------------------------------------------------

    alice_bits = generate_bits(NUM_BITS)
    alice_bases = generate_bases(NUM_BITS)

    print("\nGenerated Bits")
    print(alice_bits)

    print("\nGenerated Bases")
    print(alice_bases)

    # ------------------------------------------------
    # Connect to Bob
    # ------------------------------------------------

    client = Client(HOST, PORT)
    client.connect()

    # ------------------------------------------------
    # Send HELLO
    # ------------------------------------------------

    send_packet(
        client.socket,
        MessageType.HELLO,
        {}
    )

    packet = receive_packet(client.socket)

    if packet["type"] != MessageType.HELLO_ACK.value:
        print("HELLO_ACK not received.")
        client.close()
        return

    print("\nHandshake Complete")

    # ------------------------------------------------
    # Send BB84_INIT
    # ------------------------------------------------

    send_packet(
        client.socket,
        MessageType.BB84_INIT,
        {
            "bits": alice_bits,
            "bases": alice_bases
        }
    )

    print("\nBB84_INIT Sent")

    # ------------------------------------------------
    # Receive Bob's Bases
    # ------------------------------------------------

    packet = receive_packet(client.socket)

    if packet["type"] != MessageType.BB84_BASES.value:
        print("Unexpected packet.")
        client.close()
        return

    payload = packet["payload"]

    bob_bases = payload["bases"]
    bob_measurements = payload["measurements"]

    print("\nReceived Bob Bases")
    print(bob_bases)

    print("\nReceived Bob Measurements")
    print(bob_measurements)

    # ------------------------------------------------
    # Sifting
    # ------------------------------------------------

    indices = sift_indices(
        alice_bases,
        bob_bases
    )

    alice_sifted = sift_key(
        alice_bits,
        alice_bases,
        bob_bases
    )

    bob_sifted = sift_key(
        bob_measurements,
        alice_bases,
        bob_bases
    )

    print("\nMatching Basis Positions")
    print(indices)

    print("\nAlice Sifted Key")
    print(alice_sifted)

    print("\nBob Sifted Key")
    print(bob_sifted)

    # ------------------------------------------------
    # Calculate Initial QBER
    # ------------------------------------------------

    qber = calculate_qber(
        alice_sifted,
        bob_sifted
    )

    print("\n" + "=" * 60)
    print("QBER BEFORE CASCADE")
    print("=" * 60)
    print(f"{qber:.2%}")

    # ------------------------------------------------
    # Inform Bob of QBER
    # ------------------------------------------------

    send_packet(
        client.socket,
        MessageType.QBER_REPORT,
        {
            "qber": qber
        }
    )

    print("\nQBER Report Sent")
    print("\n" + "=" * 60)
    print("STARTING CASCADE (MULTI-PASS)")
    print("=" * 60)

    start_reconciliation(client.socket)

    # ------------------------------------------------
    # Multi-Pass Cascade Execution
    # ------------------------------------------------

    BLOCK_SIZES = [4, 8, 16]

    for block_size in BLOCK_SIZES:

        print(f"\n===== Cascade Pass (Block Size {block_size}) =====")

        for start in range(0, len(alice_sifted), block_size):

            end = min(start + block_size, len(alice_sifted))

            alice_parity = calculate_parity(alice_sifted[start:end])

            bob_parity = request_parity(
                client.socket,
                start,
                end
            )

            print(
                f"Block {start}-{end}: "
                f"Alice={alice_parity} Bob={bob_parity}"
            )

            if alice_parity != bob_parity:

                error_index = locate_error(
                    client.socket,
                    alice_sifted,
                    start,
                    end
                )

                print(f"Error located at bit {error_index}")

                send_correction(
                    client.socket,
                    error_index
                )

    # ------------------------------------------------
    # Complete Reconciliation
    # ------------------------------------------------

    send_packet(
        client.socket,
        MessageType.RECON_COMPLETE,
        {}
    )

    # ------------------------------------------------
    # Step 4: Alice Receives Hash & Verification
    # ------------------------------------------------

    packet = receive_packet(client.socket)

    if packet["type"] != MessageType.KEY_VERIFY.value:
        print("Verification failed.")
        client.close()
        return

    bob_hash = packet["payload"]["hash"]
    alice_hash = key_hash(alice_sifted)

    print("\n" + "=" * 60)
    print("KEY VERIFICATION")
    print("=" * 60)
    print("Alice Hash:")
    print(alice_hash)
    print("\nBob Hash:")
    print(bob_hash)

    # ------------------------------------------------
    # Step 5: Compare Hashes (Abort if mismatch)
    # ------------------------------------------------

    if alice_hash != bob_hash:
        print("\nKeys DO NOT match.")
        print("Aborting communication.")

        send_packet(
            client.socket,
            MessageType.CLOSE,
            {}
        )

        client.close()
        return

    print("\nKeys Verified Successfully")

    # ------------------------------------------------
    # Step 6: Privacy Amplification (Post-Verification)
    # ------------------------------------------------

    final_digest = privacy_amplification(alice_sifted)

    print("\n" + "=" * 60)
    print("PRIVACY AMPLIFICATION")
    print("=" * 60)
    print("Final Secret Key (SHA256)")
    print(digest_to_hex(final_digest))

    # ------------------------------------------------
    # AES Encryption & Transmission
    # ------------------------------------------------

    print("\n" + "=" * 60)
    print("AES ENCRYPTION")
    print("=" * 60)

    message = input("\nEnter message to send to Bob:\n> ")

    nonce, ciphertext = encrypt_message(
        final_digest,
        message
    )

    print("\nOriginal Message")
    print(message)

    print("\nCiphertext")
    print(ciphertext.hex())

    # Send encrypted message packet
    send_packet(
        client.socket,
        MessageType.ENCRYPTED_MESSAGE,
        {
            "nonce": nonce.hex(),
            "ciphertext": ciphertext.hex()
        }
    )

    print("\nCascade Protocol Finished")

    # Close connection gracefully
    send_packet(
        client.socket,
        MessageType.CLOSE,
        {}
    )
    client.close()


# ----------------------------------------------------

if __name__ == "__main__":
    main()