"""
bob/bob.py

Bob (BB84 Receiver)

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

from network.server import Server
from network.protocol import send_packet, receive_packet
from network.messages import MessageType


from quantum.qiskit_bb84 import (
    generate_bases,
    run_bb84_qubits
)
from crypto.bb84 import sift_key  # Classical sifting utility

from network.reconciliation import (
    wait_for_reconciliation,
    handle_parity_request,
    handle_error_location_request,
    handle_error_correction
)

from crypto.key_verification import key_hash

from crypto.privacy import (
    privacy_amplification,
    digest_to_hex
)

from crypto.aes import decrypt_message

# ----------------------------------------------------

HOST = "127.0.0.1"
PORT = 5000

NOISE = 0.08      # Simulated channel noise

# ----------------------------------------------------


def main():

    print("=" * 60)
    print("BOB")
    print("=" * 60)

    # ------------------------------------------------
    # Start Server
    # ------------------------------------------------

    server = Server(HOST, PORT)
    server.start()

    conn = server.connection

    # ------------------------------------------------
    # Receive HELLO
    # ------------------------------------------------

    packet = receive_packet(conn)

    if packet["type"] != MessageType.HELLO.value:
        print("HELLO not received.")
        server.close()
        return

    print("\nHandshake Started")

    send_packet(
        conn,
        MessageType.HELLO_ACK,
        {}
    )

    print("HELLO_ACK Sent")

    # ------------------------------------------------
    # Receive BB84_INIT
    # ------------------------------------------------

    packet = receive_packet(conn)

    if packet["type"] != MessageType.BB84_INIT.value:
        print("Expected BB84_INIT")
        server.close()
        return

    payload = packet["payload"]

    alice_bits = payload["bits"]
    alice_bases = payload["bases"]

    print("\nReceived Alice Bits")
    print(alice_bits)

    print("\nReceived Alice Bases")
    print(alice_bases)

    # ------------------------------------------------
    # Generate Bob Bases
    # ------------------------------------------------

    bob_bases = generate_bases(
        len(alice_bits)
    )

    print("\nBob Bases")
    print(bob_bases)

    # ------------------------------------------------
    # Measure Qubits
    # ------------------------------------------------

    # Replace your old measure_qubits call with run_bb84_qubits
    bob_measurements = run_bb84_qubits(
        alice_bits,
        alice_bases,
        bob_bases,
        noise_level=NOISE
    )

    print("\nBob Measurements")
    print(bob_measurements)

    # ------------------------------------------------
    # Sift Bob Key
    # ------------------------------------------------

    bob_sifted = sift_key(
        bob_measurements,
        alice_bases,
        bob_bases
    )

    # ------------------------------------------------
    # Send Bob Bases + Measurements
    # ------------------------------------------------

    send_packet(
        conn,
        MessageType.BB84_BASES,
        {
            "bases": bob_bases,
            "measurements": bob_measurements,
            "bob_sifted": bob_sifted
        }
    )

    print("\nSent Bob Bases")

    # ------------------------------------------------
    # Receive QBER
    # ------------------------------------------------

    packet = receive_packet(conn)

    if packet["type"] == MessageType.QBER_REPORT.value:

        qber = packet["payload"]["qber"]

        print("\n" + "=" * 60)
        print("QBER")
        print("=" * 60)
        print(f"{qber:.2%}")

        print("\n" + "=" * 60)
        print("WAITING FOR CASCADE")
        print("=" * 60)

        wait_for_reconciliation(conn)

        print("\nHandling reconciliation requests...\n")

        final_digest = None

        # Event-driven loop handling requests, corrections, verification & AES messages
        while True:

            packet = receive_packet(conn)

            if packet["type"] == MessageType.PARITY_REQUEST.value:

                handle_parity_request(
                    conn,
                    bob_sifted,
                    packet
                )

            elif packet["type"] == MessageType.ERROR_LOCATION_REQUEST.value:

                handle_error_location_request(
                    conn,
                    bob_sifted,
                    packet
                )

            elif packet["type"] == MessageType.ERROR_CORRECTION.value:

                handle_error_correction(
                    conn,
                    bob_sifted,
                    packet
                )

            elif packet["type"] == MessageType.RECON_COMPLETE.value:

                print("\nCascade Complete")

                # ------------------------------------------------
                # Step 3: Send Verification Hash
                # ------------------------------------------------

                send_packet(
                    conn,
                    MessageType.KEY_VERIFY,
                    {
                        "hash": key_hash(bob_sifted)
                    }
                )

                # Privacy Amplification executes locally on Bob's side
                final_digest = privacy_amplification(bob_sifted)

                print("\n" + "=" * 60)
                print("PRIVACY AMPLIFICATION")
                print("=" * 60)
                print("Final Secret Key (SHA256)")
                print(digest_to_hex(final_digest))

            elif packet["type"] == MessageType.ENCRYPTED_MESSAGE.value:

                payload = packet["payload"]

                nonce = bytes.fromhex(payload["nonce"])
                ciphertext = bytes.fromhex(payload["ciphertext"])

                message = decrypt_message(
                    final_digest,
                    nonce,
                    ciphertext
                )

                print("\n" + "=" * 60)
                print("AES DECRYPTION")
                print("=" * 60)

                print("\nReceived Ciphertext")
                print(ciphertext.hex())

                print("\nRecovered Plaintext")
                print(message)

            elif packet["type"] == MessageType.CLOSE.value:

                print("\nConnection Closed by Alice")
                break

        print("\nAll tasks handled successfully.")

        if qber < 0.11:
            print("\nBB84 Successful")
        else:
            print("\nWARNING: High QBER")
            print("Possible Eve or excessive channel noise.")

    server.close()


# ----------------------------------------------------

if __name__ == "__main__":
    main()