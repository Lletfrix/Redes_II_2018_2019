from Crypto.Hash import SHA256
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Signature import pkcs1_15
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

class docusign:
    def __init__(self, path):
        self.path = path
        self.digital_envelope = None
        self.hash = SHA256.new()
        self.digital_sign = None
        with open(path, 'rb') as data:
            self.content = data.read()
        self.ciphered = None
        self.session_key = get_random_bytes(32)

    def digital_sign(self, private_key):
        self.hash.update(self.content);
        self.digital_sign = pkcs1_15.new(private_key).sign(self.hash)

    def cipher(self, private_key):
        iv = get_random_bytes(16)
        cipher_aes = AES_new(self.session_key,AES.MODE_CBC,iv=iv)
        binary = self.digital_sign + self.content
        self.ciphered=pad(binary, 16)
        self.ciphered=cipher_aes.encrypt(self.ciphered)
        #self.ciphered = iv + self.chipered
    def digital_envelope(self, public_key):
        cipher_rsa = PKCS1_OAEP.new(public_key)
        self.digital_envelope = cipher_rsa.encrypt(self.session_key)
