import os
from Crypto.Util.Padding import pad, unpad
from Crypto.Cipher import AES
import base64
from read_config import read_aes_config

KEYSIZE = 16
BLOCKSIZE = 16
plaintext1 = "Hello! Welcome to The Security Buddy!!"

def encrypt(plaintext):
    config=read_aes_config()
    key=config["password"]
    iv=config["iv"]
    key=key.encode("ascii")
    iv=iv.encode("ascii")

    cipher1 = AES.new(key, AES.MODE_CBC, iv)
    ciphertext = cipher1.encrypt(pad(plaintext.encode(), BLOCKSIZE))

    ciphertext=(base64.b64encode(ciphertext)).decode("ascii")
    return ciphertext

def decrypt(ciphertext):
    config=read_aes_config()
    key=config["password"]
    iv=config["iv"]
    key=key.encode("ascii")
    iv=iv.encode("ascii")

    ciphertext=ciphertext.encode("ascii")
    ciphertext=base64.b64decode(ciphertext)

    cipher2 = AES.new(key, AES.MODE_CBC, iv)
    plaintext2 = unpad(cipher2.decrypt(ciphertext), BLOCKSIZE)


    return plaintext2.decode()