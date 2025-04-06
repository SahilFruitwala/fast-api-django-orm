import bcrypt


def get_hashed_password(password: str) -> bytes:
    # Generate salt and hash password
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed


def is_correct_password(plain_password: str, hashed_password: bytes) -> bool:
    """
    Given a previously-stored salt and hash, and a password provided by a user
    trying to log in, check whether the password is correct.
    """
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password)
