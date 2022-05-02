#%%
import base64
import hashlib
import hmac
#print(base64.b64decode('1BF87E47C784E9833974A2ED9B5ABE73DA5D0A8F1E6D86B492F4A3B312B8D2FC')

def is_correct_password(salt: bytes, pw_hash: bytes, password: str) -> bool:
    """
    Given a previously-stored salt and hash, and a password provided by a user
    trying to log in, check whether the password is correct.
    """
    return hmac.compare_digest(
        pw_hash,
        hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
    )
salt = '8d471dab-7e02-41e3-8185-a5712cba2155'
password = 'Dry19700302&'
pw_hash = '32875BADA1AE17DF22E57AF60377AA4F8CD71AB0BADFB4AD18D56C49E222370E'

print(is_correct_password(salt=salt.encode, password=password, pw_hash=pw_hash.encode))
# %%
from typing import Tuple
import os
import hashlib
import hmac

def hash_new_password(password: str) -> Tuple[bytes, bytes]:
    """
    Hash the provided password with a randomly-generated salt and return the
    salt and hash to store in the database.
    """
    #salt = os.urandom(16)
    salt = '53bc38bc-5ae8-40b7-b22a-1b4785f8fc81'
    pw_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
    return salt, pw_hash

def is_correct_password(salt: bytes, pw_hash: bytes, password: str) -> bool:
    """
    Given a previously-stored salt and hash, and a password provided by a user
    trying to log in, check whether the password is correct.
    """
    return hmac.compare_digest(
        pw_hash,
        hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
    )

# Example usage:
salt, pw_hash = hash_new_password('Dry19700302&')
assert is_correct_password(salt, pw_hash, 'Dry19700302&')
assert not is_correct_password(salt, pw_hash, 'Tr0ub4dor&3')
assert not is_correct_password(salt, pw_hash, 'rosebud')

# %%
