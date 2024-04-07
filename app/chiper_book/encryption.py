import hashlib
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import os


# 使用AES加密算法加密明文
def encrypt(key_hash, plaintext):
    cipher = AES.new(key_hash, AES.MODE_ECB)
    return cipher.encrypt(pad(plaintext.encode(), AES.block_size))


# 使用AES加密算法解密密文
def decrypt(key_hash, ciphertext):
    cipher = AES.new(key_hash, AES.MODE_ECB)
    return unpad(cipher.decrypt(ciphertext), AES.block_size).decode()


# 使用SHA256哈希算法对密钥进行哈希
def hash_key(key):
    return hashlib.sha256(key.encode()).digest()


def salt_hash_key(key, salt=None):
    if salt is None:
        salt = os.urandom(16)
    key_salt_hash = hashlib.pbkdf2_hmac('sha256', key.encode(), salt, 100000)
    return key_salt_hash, salt