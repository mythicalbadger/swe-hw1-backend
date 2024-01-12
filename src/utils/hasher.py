import bcrypt


def hash(password: str) -> bytes:
    """
    Hashes a password.
    :param password: The password to hash.
    :return: The hashed password.
    """
    return bcrypt.hashpw(password.encode("utf-8"), salt=bcrypt.gensalt())


def verify(password: str, hashed_password: bytes) -> bool:
    """
    Checks a password against a hashed password.
    :param password: The plaintext password.
    :param hashed_password: The hashed password.
    :return: True if passwords match, False otherwise.
    """
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password)
