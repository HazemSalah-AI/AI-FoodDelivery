from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError

hasher = PasswordHasher()


def hash_password(password: str):
    return hasher.hash(password)


def verify_password(encoded: str, password: str):
    try:
        return hasher.verify(encoded, password)
    except (VerificationError, InvalidHashError):
        return False
