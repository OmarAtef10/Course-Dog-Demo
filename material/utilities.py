import hashlib


def calculate_file_hash(target_file):
    BLOCK_SIZE = 65536
    hasher = hashlib.sha256()
    for chunk in iter(lambda: target_file.read(BLOCK_SIZE), b''):
        hasher.update(chunk)
    return hasher.hexdigest()
