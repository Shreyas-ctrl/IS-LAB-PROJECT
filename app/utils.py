import os
import base64
from typing import Final

from passlib.context import CryptContext
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from cryptography.hazmat.primitives import serialization

# ----------------------
# Password Hashing Utils (argon2id)
# ----------------------

# Argon2id is memory-hard and recommended by OWASP; no 72-byte limit like bcrypt.
# Requires: pip install "argon2-cffi" "passlib>=1.7.4"
pwd_context: Final = CryptContext(
    schemes=["argon2"],  # passlib's argon2 handler uses argon2id
    deprecated="auto",
    # Optional tuning: adjust once everything runs smoothly
    # argon2__time_cost=3,
    # argon2__memory_cost=19456,  # ~19 MiB
    # argon2__parallelism=1,
)

def hash_password(password: str) -> str:
    # Consider capping absurdly long inputs to avoid DoS: if len(password) > 10000: raise ValueError(...)
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# ----------------------
# Fernet Key Persistence
# ----------------------

FERNET_KEY_FILE: Final = "fernet.key"

def _load_or_create_fernet_key(path: str) -> bytes:
    if os.path.exists(path):
        with open(path, "rb") as f:
            return f.read()
    key = Fernet.generate_key()
    with open(path, "wb") as f:
        f.write(key)
    return key

FERNET_KEY: Final = _load_or_create_fernet_key(FERNET_KEY_FILE)
fernet: Final = Fernet(FERNET_KEY)

def encrypt_note(plaintext: str) -> str:
    return fernet.encrypt(plaintext.encode("utf-8")).decode("utf-8")

def decrypt_note(token: str) -> str:
    return fernet.decrypt(token.encode("utf-8")).decode("utf-8")

# ----------------------
# Ed25519 Key Persistence
# ----------------------

ED25519_KEY_FILE: Final = "ed25519.key"

def _load_or_create_ed25519(path: str) -> Ed25519PrivateKey:
    if os.path.exists(path):
        with open(path, "rb") as f:
            raw = f.read()
            return Ed25519PrivateKey.from_private_bytes(raw)
    sk = Ed25519PrivateKey.generate()
    raw = sk.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption(),
    )
    with open(path, "wb") as f:
        f.write(raw)
    return sk

PRIVATE_KEY: Final[Ed25519PrivateKey] = _load_or_create_ed25519(ED25519_KEY_FILE)
PUBLIC_KEY: Final[Ed25519PublicKey] = PRIVATE_KEY.public_key()

# ----------------------
# Note Signing Utilities
# ----------------------

def sign_note(encrypted_content: str) -> str:
    sig = PRIVATE_KEY.sign(encrypted_content.encode("utf-8"))
    return base64.b64encode(sig).decode("utf-8")

def verify_note_signature(encrypted_content: str, signature: str) -> bool:
    try:
        PUBLIC_KEY.verify(base64.b64decode(signature), encrypted_content.encode("utf-8"))
        return True
    except Exception:
        return False
