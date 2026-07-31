"""
network/protocol.py

Protocol helper functions for sending and receiving
messages between Alice and Bob.

Packet Format
-------------

{
    "type": "BB84_INIT",
    "payload": {
        ...
    }
}

Packets are transmitted as:

[4-byte packet length][JSON packet]

This guarantees complete packet delivery over TCP.
"""

import json
import struct

from network.messages import MessageType


# ==========================================================
# Internal Helper
# ==========================================================

def _recv_exact(sock, size):
    """
    Receive exactly 'size' bytes from the socket.
    """

    data = b""

    while len(data) < size:

        packet = sock.recv(size - len(data))

        if not packet:
            raise ConnectionError("Connection closed.")

        data += packet

    return data


# ==========================================================
# Packet Creation
# ==========================================================

def create_packet(message_type, payload=None):
    """
    Create a packet dictionary.

    Parameters
    ----------
    message_type : MessageType or str

    payload : dict
    """

    if payload is None:
        payload = {}

    if isinstance(message_type, MessageType):
        message_type = message_type.value

    return {
        "type": message_type,
        "payload": payload
    }


# ==========================================================
# Packet Validation
# ==========================================================

def validate_packet(packet):
    """
    Validate received packet.
    """

    if not isinstance(packet, dict):
        return False

    if "type" not in packet:
        return False

    if "payload" not in packet:
        return False

    if not isinstance(packet["payload"], dict):
        return False

    return True


# ==========================================================
# Send Packet
# ==========================================================

def send_packet(sock, message_type, payload=None):
    """
    Send one packet over TCP.
    """

    packet = create_packet(message_type, payload)

    encoded = json.dumps(packet).encode("utf-8")

    length = struct.pack(">I", len(encoded))

    sock.sendall(length + encoded)


# ==========================================================
# Receive Packet
# ==========================================================

def receive_packet(sock):
    """
    Receive one complete packet.
    """

    header = _recv_exact(sock, 4)

    length = struct.unpack(">I", header)[0]

    data = _recv_exact(sock, length)

    packet = json.loads(data.decode("utf-8"))

    if not validate_packet(packet):
        raise ValueError("Invalid packet received.")

    return packet


# ==========================================================
# Pretty Print Packet
# ==========================================================

def print_packet(packet):
    """
    Print a packet in a readable format.
    """

    print("\n" + "=" * 60)

    print("MESSAGE TYPE")
    print(packet["type"])

    print("\nPAYLOAD")

    print(
        json.dumps(
            packet["payload"],
            indent=4
        )
    )

    print("=" * 60)


# ==========================================================
# Convenience Functions
# ==========================================================

def send_hello(sock):
    send_packet(
        sock,
        MessageType.HELLO
    )


def send_close(sock):
    send_packet(
        sock,
        MessageType.CLOSE
    )


def send_error(sock, message):
    send_packet(
        sock,
        MessageType.ERROR,
        {
            "message": message
        }
    )


# ==========================================================
# Generic Receive
# ==========================================================

def receive(sock):
    """
    Alias for receive_packet().
    """

    return receive_packet(sock)


# ==========================================================
# Type Checking
# ==========================================================

def is_type(packet, message_type):
    """
    Check whether a received packet is
    of the expected type.
    """

    if isinstance(message_type, MessageType):
        message_type = message_type.value

    return packet["type"] == message_type