"""AES-256 encryption/decryption using Fernet with PBKDF2 key derivation."""

import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend


def derive_key(password, salt):
    """
    Derive a key from password using PBKDF2.
    
    Args:
        password: Password string
        salt: Random salt bytes
        
    Returns:
        bytes: 32-byte key
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode('utf-8')))


def encrypt_message(plaintext, password):
    """
    Encrypt plaintext using AES-256-GCM via Fernet.
    
    Args:
        plaintext: Bytes to encrypt
        password: Encryption password
        
    Returns:
        bytes: Salt + ciphertext (Fernet token)
    """
    # Generate random salt
    salt = os.urandom(16)
    
    # Derive key
    key = derive_key(password, salt)
    
    # Encrypt
    f = Fernet(key)
    ciphertext = f.encrypt(plaintext)
    
    # Return salt + ciphertext
    return salt + ciphertext


def decrypt_message(ciphertext_with_salt, password):
    """
    Decrypt ciphertext using AES-256-GCM via Fernet.
    
    Args:
        ciphertext_with_salt: Bytes containing salt + ciphertext
        password: Decryption password
        
    Returns:
        bytes: Decrypted plaintext
    """
    if len(ciphertext_with_salt) < 16:
        raise ValueError("Invalid ciphertext")
    
    # Extract salt (first 16 bytes)
    salt = ciphertext_with_salt[:16]
    ciphertext = ciphertext_with_salt[16:]
    
    # Derive key
    key = derive_key(password, salt)
    
    # Decrypt
    f = Fernet(key)
    return f.decrypt(ciphertext)
