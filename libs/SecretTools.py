# coding:utf8
import base64
from Crypto.Cipher import AES
import rsa

__author__ = 'cyh'

RSA_Bits = 512
RSA_textMax = RSA_Bits / 8 - 11

"""
AES 加密专用
"""
BS = AES.block_size
pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
unpad = lambda s: s[0:-ord(s[-1])]


def _splitStr(message, length):
    return [message[i * length:(i + 1) * length] for i in xrange(len(message) / length + 1)]


def deRSA(input, privkey):
    return ''.join([rsa.decrypt(base64.b64decode(str(etext)), privkey) for etext in input.split('|')])


def enRSA(input, public):
    return '|'.join([base64.b64encode(rsa.encrypt(text, public)) for text in _splitStr(input, RSA_textMax)])


def createRSA():
    (pubkey, privkey) = rsa.newkeys(RSA_Bits)
    pubkeyStr = hex(pubkey.n)[2:-1] + "|" + str(hex(pubkey.e))[2:]
    return pubkeyStr, privkey


def sha2key(key):
    key = base64.b64encode(key)
    if len(key) > 32:
        key = key[:32]
    return key.zfill(32)


def deAES(key, text):
    cipher = AES.new(sha2key(key))
    return unpad(cipher.decrypt(base64.b64decode(text)))


def enAES(key, text):
    cipher = AES.new(sha2key(key))
    return base64.b64encode(cipher.encrypt(pad(text)))