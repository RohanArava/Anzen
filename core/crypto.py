from cryptography.fernet import Fernet
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend

def derive_user_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100_000,
        backend=default_backend(),
    )
    key = kdf.derive(password.encode())
    return base64.urlsafe_b64encode(key)

def encrypt_secret(secret_base32: str, key: bytes) -> bytes:
    f = Fernet(key)
    return f.encrypt(secret_base32.encode())

def decrypt_secret(encrypted: bytes, key: bytes) -> str:
    f = Fernet(key)
    return f.decrypt(encrypted).decode()
