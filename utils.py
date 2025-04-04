from hashlib import pbkdf2_hmac
from hmac import compare_digest
from os import urandom


def get_hashed_password(password: str) -> tuple[bytes, bytes]:
    """
    Hash the provided password with a randomly-generated salt and return the
    salt and hash to store in the database.
    """
    salt = urandom(16)
    pw_hash = pbkdf2_hmac('sha256', password.encode(), salt, 100000)
    return salt, pw_hash


def is_correct_password(salt: bytes, pw_hash: bytes, password: str) -> bool:
    """
    Given a previously-stored salt and hash, and a password provided by a user
    trying to log in, check whether the password is correct.
    """
    return compare_digest(pw_hash, pbkdf2_hmac('sha256', password.encode(), salt, 100000))
