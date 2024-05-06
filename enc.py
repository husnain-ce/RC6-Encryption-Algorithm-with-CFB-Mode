import base64
from Crypto.Cipher import ARC6
from Crypto.Cipher import ARC4
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
from cryptography.fernet import Fernet

def generate_fernet_key():
    return Fernet.generate_key()

def encrypt_rc6_cfb_fernet_key(message, fernet_key):
    f = Fernet(fernet_key)
    key = f.decrypt(fernet_key)
    iv = get_random_bytes(16)
    cipher = ARC6.new(key, ARC6.MODE_CFB, iv)
    encrypted_message = cipher.encrypt(pad(message.encode(), 32))
    return iv + encrypted_message

def decrypt_rc6_cfb_fernet_key(encrypted_data, fernet_key):
    f = Fernet(fernet_key)
    key = f.decrypt(fernet_key)
    iv = encrypted_data[:16]
    encrypted_message = encrypted_data[16:]
    cipher = ARC6.new(key, ARC6.MODE_CFB, iv)
    decrypted_message = unpad(cipher.decrypt(encrypted_message), 32).decode()
    return decrypted_message

# Example usage
fernet_key = generate_fernet_key()
message = "This is a secret message."

encrypted_data = encrypt_rc6_cfb_fernet_key(message, fernet_key)
print(f"Encrypted data: {base64.b64encode(encrypted_data).decode()}")

decrypted_message = decrypt_rc6_cfb_fernet_key(encrypted_data, fernet_key)
print(f"Decrypted message: {decrypted_message}")