import hashlib

def get_hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def check_hash(password: str, hash: str) -> bool:
    return get_hash(password) == hash