from Crypto.Hash import SHA256
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Signature import pkcs1_15
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
import pickle

class docusign:
    def __init__(self, path=None, bin=None):
        if [path, bin].count(None) != 1:
            raise TypeError("Exactly 1 argument must be given.")
        if path is not None:
            self.path = path
            self.digital_envelope = None
            self.hash = SHA256.new()
            self.digital_sign = None
            with open(path, 'rb') as data:
                self.content = data.read()
            self.ciphered = None
            self.session_key = get_random_bytes(32)
            self.iv = get_random_bytes(16)
        else:
            self.digital_envelope = bin[16:272]
            self.ciphered = bin[272:]
            self.hash = SHA256.new()
            self.digital_sign = None
            self.content = None
            self.session_key = None
            self.iv = bin[:16]

    def generate_hash(self):
        self.hash.update(self.content)

    def get_digital_sign(self, private_key):
        self.generate_hash()
        self.digital_sign = pkcs1_15.new(private_key).sign(self.hash)

    def cipher(self, private_key):
        cipher_aes = AES.new(self.session_key,AES.MODE_CBC,iv=self.iv)
        binary = self.digital_sign + self.content
        self.ciphered=cipher_aes.encrypt(pad(binary, 16))

    def encrypt(self, public_key):
        cipher_aes = AES.new(self.session_key,AES.MODE_CBC,iv=self.iv)
        self.ciphered=cipher_aes.encrypt(pad(self.content, 16))

    def get_digital_envelope(self, public_key):
        cipher_rsa = PKCS1_OAEP.new(public_key)
        self.digital_envelope = cipher_rsa.encrypt(self.session_key)

    def prepare_upload(self):
        self.ciphered = self.iv + self.digital_envelope + self.ciphered

    def get_session_key(self, private_key):
        cipher_rsa = PKCS1_OAEP.new(private_key)
        self.session_key = cipher_rsa.decrypt(self.digital_envelope)

    def decipher(self):
        cipher_aes = AES.new(self.session_key, AES.MODE_CBC, iv=self.iv)
        binary = unpad(cipher_aes.decrypt(self.ciphered), 16)
        self.digital_sign = binary[:256]
        self.content = binary[256:]
        self.generate_hash()

    def verify_signature(self, public_key):
        try:
            pkcs1_15.new(public_key).verify(self.hash, self.digital_sign)
        except ValueError:
            return False
        return True
