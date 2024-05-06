import os
from base64 import urlsafe_b64encode, urlsafe_b64decode
from cryptography.fernet import Fernet


def int_to_bytes(value, length=None):
    if length is None:
        length = (value.bit_length() + 7) // 8
    return value.to_bytes(length, byteorder='little')

def bytes_to_int(byte_array):
    return int.from_bytes(byte_array, byteorder='little')

def rol(value, shift):
    return ((value << shift) & 0xFFFFFFFF) | (value >> (32 - shift))

def ror(value, shift):
    return (value >> shift) | ((value << (32 - shift)) & 0xFFFFFFFF)

class RC6:
    def __init__(self, key):
        self.key = key
        self.w = 32
        self.r = 20
        self.s = self.generate_round_keys()

    def generate_round_keys(self):
        key_len = len(self.key)
        key = [bytes_to_int(self.key[i:i+4]) for i in range(0, key_len, 4)]
        c = key_len // 4
        L = [0] * c
        for i in range(c):
            L[i] = key[i]

        P = 0xB7E15163
        Q = 0x9E3779B9
        S = [0] * (2 * (self.r + 1) + 2)
        S[0] = P
        for i in range(1, 2 * (self.r + 1) + 2):
            S[i] = (S[i-1] + Q) & 0xFFFFFFFF

        i = j = A = B = 0
        for k in range(3 * max(c, 2 * (self.r + 1))):
            S[i] = A = rol((S[i] + A + B) & 0xFFFFFFFF, 3)
            L[j] = B = rol((L[j] + A + B) & 0xFFFFFFFF, (A + B) & 31)
            i = (i + 1) % (2 * (self.r + 1) + 2)
            j = (j + 1) % c

        return S

    def encrypt_block(self, plaintext):
        A = bytes_to_int(plaintext[0:4]) + self.s[0]
        B = bytes_to_int(plaintext[4:8]) + self.s[1]
        C = bytes_to_int(plaintext[8:12]) + self.s[2]
        D = bytes_to_int(plaintext[12:16]) + self.s[3]

        for i in range(1, self.r + 1):
            t = rol(B * (2 * B + 1), 5)
            u = rol(D * (2 * D + 1), 5)
            A = rol(A ^ t, u % 32) + self.s[2 * i]
            C = rol(C ^ u, t % 32) + self.s[2 * i + 1]
            A, B, C, D = B, C, D, A

        B = B + self.s[2 * self.r + 2]
        D = D + self.s[2 * self.r + 3]

        return int_to_bytes(A) + int_to_bytes(B) + int_to_bytes(C) + int_to_bytes(D)


    def decrypt_block(self, ciphertext):
        A = bytes_to_int(ciphertext[0:4])
        B = bytes_to_int(ciphertext[4:8]) - self.s[2 * self.r + 4]
        C = bytes_to_int(ciphertext[8:12])
        D = bytes_to_int(ciphertext[12:16]) - self.s[2 * self.r + 5]

        for i in range(self.r, 0, -1):
            A, B, C, D = D, A, B, C
            u = rol(D * (2 * D + 1), 5)
            t = rol(B * (2 * B + 1), 5)
            C = ror(C - self.s[2 * i + 1], t % 32) ^ u
            A = ror(A - self.s[2 * i], u % 32) ^ t

        D = D - self.s[3]
        C = C - self.s[2]
        B = B - self.s[1]
        A = A - self.s[0]

        return int_to_bytes(A) + int_to_bytes(B) + int_to_bytes(C) + int_to_bytes(D)



import os
from base64 import urlsafe_b64encode, urlsafe_b64decode

# ... RC6 class with encrypt_block and decrypt_block ...

class RC6_CFB:
    def __init__(self, key, iv):
        self.iv = iv
        self.rc6 = RC6(key)

    def encrypt(self, plaintext):
        blocks = [plaintext[i:i+16] for i in range(0, len(plaintext), 16)]
        ciphertext = b''
        prev_block = self.iv

        for block in blocks:
            encrypted_iv = self.rc6.encrypt_block(prev_block)
            cipher_block = bytes([a ^ b for a, b in zip(encrypted_iv, block)])
            ciphertext += cipher_block
            prev_block = cipher_block

        return ciphertext

    def decrypt(self, ciphertext):
        blocks = [ciphertext[i:i+16] for i in range(0, len(ciphertext), 16)]
        plaintext = b''
        prev_block = self.iv

        for block in blocks:
            encrypted_iv = self.rc6.encrypt_block(prev_block)
            plain_block = bytes([a ^ b for a, b in zip(encrypted_iv, block)])
            plaintext += plain_block
            prev_block = block

        return plaintext

def main():
    # key = os.urandom(16)
    fernet_key = Fernet.generate_key()
    key = fernet_key[:16]
    iv = os.urandom(16)
    rc6_cfb = RC6_CFB(key, iv)

    plaintext = b'This is a test message.'
    print('Original plaintext:', plaintext)

    encrypted = rc6_cfb.encrypt(plaintext)
    print('Encrypted ciphertext:', encrypted)

    decrypted = rc6_cfb.decrypt(encrypted)
    print('Decrypted plaintext:', decrypted)

if __name__ == '__main__':
    main()