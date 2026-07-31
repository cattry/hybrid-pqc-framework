import hashlib


def key_hash(key_bits):
    """
    Convert bit list into SHA256 hash.
    """

    bit_string = "".join(map(str, key_bits))

    return hashlib.sha256(
        bit_string.encode()
    ).hexdigest()