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
        else:
            (self.path, self.ciphered) = pickle.load(bin)
            self.digital_envelope = self.ciphered[:2048]
            self.ciphered = self.ciphered[2048:]
            self.hash = None
            self.digital_sign = None
            self.content = None
            self.session_key = None

    def get_digital_sign(self, private_key):
        self.hash.update(self.content);
        self.digital_sign = pkcs1_15.new(private_key).sign(self.hash)

    def cipher(self, private_key):
        iv = get_random_bytes(16)
        cipher_aes = AES.new(self.session_key,AES.MODE_CBC,iv=iv)
        binary = self.digital_sign + self.content
        self.ciphered=cipher_aes.encrypt(pad(binary, 16))
        self.ciphered = iv + self.ciphered

    def get_digital_envelope(self, public_key):
        cipher_rsa = PKCS1_OAEP.new(public_key)
        self.digital_envelope = cipher_rsa.encrypt(self.session_key)

    def prepare_upload(self):
        self.ciphered = self.digital_envelope + self.ciphered

    def get_session_key(self, public_key):
        cipher_rsa = PKCS1_OAEP.new(public_key)
        self.session_key = cipher_rsa.decrypt(self.digital_envelope)

    def decipher(self):
        iv = self.ciphered[:16]
        cipher_aes = AES.new(self.session_key, AES.MODE_CBC, iv=iv)
        binary = unpad(cipher_aes.decrypt(self.ciphered))
        self.digital_sign = binary[:256]
        self.content = binary[256:]
