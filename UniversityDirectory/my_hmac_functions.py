from UniversityDirectory.my_sha256 import Sha256

def hmac_sign_with_sha256(key, message):
    block_size = 64  # 64 nibbles (256 bits) for SHA-256

    # if the key is longer than the block size, hash it and resize it to be 64 bytes long
    if len(key) > block_size:
        key = Sha256(key).digest()

    # if the key is shorter than the block size, we should pad it with zeros until it becomes 64 bytes long
    if len(key) < block_size:
        key = key + b'\x00' * (block_size - len(key))

    # xor the key with the inner and outer padding
    inner_padding = b'\x36' * block_size
    outer_padding = b'\x5c' * block_size
    inner_key = bytes([a ^ b for a, b in zip(key, inner_padding)])
    outer_key = bytes([a ^ b for a, b in zip(key, outer_padding)])

    # Calculate the inner hash
    inner_hash = Sha256(inner_key + message).digest()

    # Calculate the outer hash with the inner hash
    outer_hash = Sha256(outer_key + inner_hash).digest()

    return outer_hash

def verify_hmac(key, message, computed_digest):
    # Compute the expected HMAC using the given secret key and message
    expected_digest = hmac_sign_with_sha256(key, message)

    # Compare the computed HMAC to the expected HMAC
    return str(computed_digest) == str(expected_digest)