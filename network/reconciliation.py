"""
network/reconciliation.py

Networked Cascade Reconciliation
"""

from crypto.error_correction import calculate_parity
from network.messages import MessageType
from network.protocol import send_packet, receive_packet


# ==========================================================
# Alice Protocol Initialization
# ==========================================================

def start_reconciliation(sock):

    send_packet(
        sock,
        MessageType.RECON_START,
        {}
    )

    packet = receive_packet(sock)

    if packet["type"] != MessageType.RECON_ACK.value:
        raise ValueError("Expected RECON_ACK")

    print("\nReconciliation Started")


# ==========================================================
# Bob Protocol Initialization
# ==========================================================

def wait_for_reconciliation(sock):

    packet = receive_packet(sock)

    if packet["type"] != MessageType.RECON_START.value:
        raise ValueError("Expected RECON_START")

    print("\nReconciliation Request Received")

    send_packet(
        sock,
        MessageType.RECON_ACK,
        {}
    )


# ==========================================================
# Alice Requests Parity
# ==========================================================

def request_parity(sock, start, end):

    send_packet(
        sock,
        MessageType.PARITY_REQUEST,
        {
            "start": start,
            "end": end
        }
    )

    packet = receive_packet(sock)

    if packet["type"] != MessageType.PARITY_RESPONSE.value:
        raise ValueError("Expected PARITY_RESPONSE")

    return packet["payload"]["parity"]


# ==========================================================
# Bob Handles Parity Request
# ==========================================================

def handle_parity_request(sock, key, packet):

    start = packet["payload"]["start"]
    end = packet["payload"]["end"]

    parity = calculate_parity(key[start:end])

    send_packet(
        sock,
        MessageType.PARITY_RESPONSE,
        {
            "parity": parity
        }
    )


# ==========================================================
# Alice Error Location Requests
# ==========================================================

def request_error_location(sock, start, end):

    send_packet(
        sock,
        MessageType.ERROR_LOCATION_REQUEST,
        {
            "start": start,
            "end": end
        }
    )

    packet = receive_packet(sock)

    if packet["type"] != MessageType.ERROR_LOCATION_RESPONSE.value:
        raise RuntimeError("Expected ERROR_LOCATION_RESPONSE")

    return packet["payload"]["parity"]


# ==========================================================
# Bob Handles Error Location Request
# ==========================================================

def handle_error_location_request(sock, bob_key, packet):

    start = packet["payload"]["start"]
    end = packet["payload"]["end"]

    parity = calculate_parity(bob_key[start:end])

    send_packet(
        sock,
        MessageType.ERROR_LOCATION_RESPONSE,
        {
            "parity": parity
        }
    )


# ==========================================================
# Recursive Binary Search for Error Location
# ==========================================================

def locate_error(sock, alice_key, start, end):

    while end - start > 1:

        mid = (start + end) // 2

        alice_parity = calculate_parity(alice_key[start:mid])

        bob_parity = request_error_location(
            sock,
            start,
            mid
        )

        if alice_parity != bob_parity:
            end = mid
        else:
            start = mid

    return start


# ==========================================================
# Step 2: Alice Sends Bit Correction
# ==========================================================

def send_correction(sock, index):

    send_packet(
        sock,
        MessageType.ERROR_CORRECTION,
        {
            "index": index
        }
    )

    packet = receive_packet(sock)

    if packet["type"] != MessageType.CORRECTION_ACK.value:
        raise RuntimeError("Expected CORRECTION_ACK")


# ==========================================================
# Step 3: Bob Handles Error Correction
# ==========================================================

def handle_error_correction(sock, bob_key, packet):

    index = packet["payload"]["index"]

    # Flip the erroneous bit in Bob's key
    bob_key[index] ^= 1

    print(f"Corrected bit {index}")

    send_packet(
        sock,
        MessageType.CORRECTION_ACK,
        {}
    )