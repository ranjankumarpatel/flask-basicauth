# gateway = JavaGateway(
#   gateway_parameters=GatewayParameters(address="tracker.thinktalentws48.click", auto_field=True))
# gateway = JavaGateway(
#   gateway_parameters=GatewayParameters(auto_field=True))


import binascii

from Crypto.Cipher import AES

bs = 16
key = "TheBestSecretKey".encode("utf8")
cipher = AES.new(key, AES.MODE_ECB)


def encrypt_aes(text):
    raw = _pad(str(text).strip())
    raw = raw.encode("utf8")
    encrypted = cipher.encrypt(raw)
    encoded = binascii.hexlify(encrypted)
    return encoded.decode("utf-8").upper()


def decrypt_aes(encrypted):
    decoded = binascii.unhexlify(encrypted.strip())
    decrypted = cipher.decrypt(decoded)
    return _unpad(decrypted).decode("utf-8")


def _pad(s):
    return s + (bs - len(s) % bs) * chr(bs - len(s) % bs)


def _unpad(s):
    return s[:-ord(s[len(s) - 1:])]


# auth = "61646d696e3a313233343536"
# print(binascii.unhexlify(auth.strip()).decode("utf-8"))

# plaintext = 'admin:123456'
# encrypted = encrypt_aes(plaintext)
# print('Encrypted: %s' % encrypted)

# from java
# decrypted = decrypt_aes("A097D3B5C86933D582FF83AAA6EEC565")
# print('Decrypted: %s' % decrypted)

# print(encrypt_text("123456"))
