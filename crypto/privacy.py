import hashlib


def bits_to_bytes(bits):
    """
    Convert list of bits to bytes.
    """

    bit_string = "".join(str(b) for b in bits)

    padding = (8 - len(bit_string) % 8) % 8
    bit_string += "0" * padding

    data = bytearray()

    for i in range(0, len(bit_string), 8):
        data.append(int(bit_string[i:i+8], 2))

    return bytes(data)


def privacy_amplification(bits):

    data = bits_to_bytes(bits)

    digest = hashlib.sha256(data).digest()

    return digest


def digest_to_hex(digest):
    return digest.hex()


def digest_to_bits(digest):

    result = []

    for byte in digest:
        result.extend(
            [int(x) for x in format(byte, "08b")]
        )

    return result