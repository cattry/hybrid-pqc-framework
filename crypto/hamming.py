"""
crypto/hamming.py

Hamming(7,4) Error Correction
"""

# -------------------------------------------------------
# Convert bytes to bit list
# -------------------------------------------------------

def bytes_to_bits(data: bytes):

    bits = []

    for byte in data:
        for i in range(8):
            bits.append((byte >> (7 - i)) & 1)

    return bits


# -------------------------------------------------------
# Convert bit list back to bytes
# -------------------------------------------------------

def bits_to_bytes(bits):

    while len(bits) % 8 != 0:
        bits.append(0)

    output = bytearray()

    for i in range(0, len(bits), 8):

        value = 0

        for bit in bits[i:i+8]:
            value = (value << 1) | bit

        output.append(value)

    return bytes(output)


# -------------------------------------------------------
# Encode one nibble
# -------------------------------------------------------

def encode_nibble(nibble):

    d1, d2, d3, d4 = nibble

    p1 = d1 ^ d2 ^ d4
    p2 = d1 ^ d3 ^ d4
    p3 = d2 ^ d3 ^ d4

    return [
        p1,
        p2,
        d1,
        p3,
        d2,
        d3,
        d4
    ]


# -------------------------------------------------------
# Decode one codeword
# -------------------------------------------------------

def decode_codeword(code):

    b = code.copy()

    s1 = b[0] ^ b[2] ^ b[4] ^ b[6]
    s2 = b[1] ^ b[2] ^ b[5] ^ b[6]
    s3 = b[3] ^ b[4] ^ b[5] ^ b[6]

    syndrome = s1 + (s2 << 1) + (s3 << 2)

    corrected = False

    if syndrome != 0:

        position = syndrome - 1

        if position < 7:
            b[position] ^= 1
            corrected = True

    data = [
        b[2],
        b[4],
        b[5],
        b[6]
    ]

    return data, corrected


# -------------------------------------------------------
# Encode bytes
# -------------------------------------------------------

def hamming_encode(data: bytes):

    bits = bytes_to_bits(data)

    encoded = []

    while len(bits) % 4 != 0:
        bits.append(0)

    for i in range(0, len(bits), 4):

        encoded.extend(
            encode_nibble(bits[i:i+4])
        )

    return bits_to_bytes(encoded)


# -------------------------------------------------------
# Decode bytes
# -------------------------------------------------------

def hamming_decode(data: bytes):

    bits = bytes_to_bits(data)

    decoded = []

    corrected_errors = 0

    usable = len(bits) // 7

    for i in range(usable):

        code = bits[i*7:(i+1)*7]

        nibble, corrected = decode_codeword(code)

        decoded.extend(nibble)

        if corrected:
            corrected_errors += 1

    return bits_to_bytes(decoded), corrected_errors