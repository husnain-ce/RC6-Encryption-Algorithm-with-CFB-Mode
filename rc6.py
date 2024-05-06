import struct
import os

def _left_rotate(n, b):
    return ((n << b) | (n >> (32 - b))) & 0xffffffff

def _right_rotate(n, b):
    return ((n >> b) | (n << (32 - b))) & 0xffffffff

def rc6_setup(key, r=20):
    key_words = len(key) // 4
    key = struct.unpack('>%dI' % key_words, key)
    
    L = [key[i] for i in range(key_words)]
    S = [0x00000000] * (2 * r + 4)
    S[0] = 0xB7E15163
    
    for i in range(1, 2 * r + 4):
        S[i] = (S[i - 1] + 0x9E3779B9) & 0xffffffff
    
    i = j = A = B = 0
    
    for k in range(3 * max(key_words, 2 * r + 4)):
        S[i] = _left_rotate((S[i] + A + B) & 0xffffffff, 3)
        A = S[i]
        i = (i + 1) % (2 * r + 4)
        L[j] = _left_rotate((L[j] + A + B) & 0xffffffff, (A + B) & 31)
        B = L[j]
        j = (j + 1) % key_words
    
    return S

def rc6_block_encrypt(block, S, r=20):
    A, B, C, D = struct.unpack('>4I', block)
    B = (B + S[0]) & 0xffffffff
    D = (D + S[1]) & 0xffffffff
    
    for i in range(1, r + 1):
        t = _left_rotate(B * (2 * B + 1), 5)
        u = _left_rotate(D * (2 * D + 1), 5)
        A = _left_rotate((A ^ t) + S[2 * i], u) & 0xffffffff
        C = _left_rotate((C ^ u) + S[2 * i + 1], t) & 0xffffffff
        A, B, C, D = B, C, D, A
    
    A = (A + S[2 * r + 2]) & 0xffffffff
    C = (C + S[2 * r + 3]) & 0xffffffff
    
    return struct.pack('>4I', A, B, C, D)

def rc6_block_decrypt(block, S, r=20):
    A, B, C, D = struct.unpack('>4I', block)
    C = (C - S[2 * r + 3]) & 0xffffffff
    A = (A - S[2 * r + 2]) & 0xffffffff
    
    for i in range(r, 0, -1):
        A, B, C, D = D, A, B, C
        u = _left_rotate(D * (2 * D + 1), 5)
        t = _left_rotate(B * (2 * B + 1), 5)
       

def pad(data, block_size=16):
    padding_length = block_size - (len(data) % block_size)
    return data + bytes([padding_length] * padding_length)

def unpad(data, block_size=16):
    padding_length = data[-1]
    return data[:-padding_length]

def encrypt_rc6_text(text, key):
    S = rc6_setup(key)
    padded_text = pad(text.encode('utf-8'))
    encrypted_blocks = [rc6_block_encrypt(padded_text[i:i+16], S) for i in range(0, len(padded_text), 16)]
    return b''.join(encrypted_blocks)

def decrypt_rc6_text(encrypted_data, key):
    S = rc6_setup(key)
    decrypted_blocks = [rc6_block_decrypt(encrypted_data[i:i+16], S) for i in range(0, len(encrypted_data), 16)]
    decrypted_text = unpad(b''.join(decrypted_blocks))
    return decrypted_text.decode('utf-8')

# Example usage
key = os.urandom(32)
text = "This is a secret message."

encrypted_data = encrypt_rc6_text(text, key)
print(f"Encrypted data: {encrypted_data.hex()}")

decrypted_text = decrypt_rc6_text(encrypted_data, key)
print(f"Decrypted text: {decrypted_text}")