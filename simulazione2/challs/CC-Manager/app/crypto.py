from hashlib import sha256, sha1
from Crypto.Util.number import getPrime
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Util.number import inverse
import random

p = 0x80000000000001cda6f403d8a752a4e7976173ebfcd2acf69a29f4bada1ca3178b56131c2c1f00cf7875a2e7c497b10fea66b26436e40b7b73952081319e26603810a558f871d6d256fddbec5933b77fa7d1d0d75267dcae1f24ea7cc57b3a30f8ea09310772440f016c13e08b56b1196a687d6a5e5de864068f3fd936a361c5
q = 0x926c99d24bd4d5b47adb75bd9933de8be5932f4b
g = 0x35ab31321f46491040d6519a2a5c9d3d0eeee368a86c9b3545dc1357daf8ae25b5ddc4f9a369c7e9e4598cc2959731f5dab12516f2033b4fd564b44de99ed499d19a1d7714013cbe114bce8b0b89ddefda903197cda7f8f08c64164207428196dcb9170786017d1009945c465b27eb096cfd44548a7bf7f650d8e21ec3c27502

def hash_pw(s):
    if isinstance(s, str):
        s = s.encode()

    hashed_pw = sha256(s).hexdigest()
    return hashed_pw

def get_secret_tokens(username):
    mask = (1 << 768) - 1
    p, q = getPrime(768), getPrime(768)

    user_secret = p^q
    username_int = int.from_bytes(username.encode(), byteorder = "big")
    base_value = username_int

    for _ in range(250):
        base_value = base_value * user_secret
        base_value = base_value & mask

    recovery_token_int = (base_value & ((1 << 256) - 1)) ^ username_int
    sharing_key = (base_value >> 256) ^ user_secret
    recovery_token = sha256(recovery_token_int.to_bytes(32, byteorder = "big")).hexdigest()[:16]

    return sharing_key, recovery_token

def encrypt_psw(key, password):
    assert len(key) == 16

    if isinstance(key, str):
        key = key.encode()

    if isinstance(password, str):
        password = password.encode()

    cipher = AES.new(key = key, mode = AES.MODE_ECB)
    encrypted_psw = cipher.encrypt(pad(password, 16)).hex()
    return encrypted_psw

def decrypt_psw(key, enc_password):
    assert len(key) == 16

    if isinstance(key, str):
        key = key.encode()

    if isinstance(enc_password, str):
        enc_password = enc_password.encode()

    cipher = AES.new(key = key, mode = AES.MODE_ECB)
    password = cipher.decrypt(enc_password)
    password = unpad(password, 16)
    return password

def verification_from_signing_key(key, params = (p, q, g)):
    g = params[2]
    p = params[0]
    return pow(g, key, p)

def sign_token(key, token, params = (p,q,g)):
    p = params[0]
    q = params[1]
    g = params[2]

    if isinstance(token, str):
        token = token.encode()

    k = random.randint(1,q)
    H = int.from_bytes(sha1(token).digest(), byteorder = "big")
    r = pow(g, k, p) % q
    s = (inverse(k, q) * (H + key * r)) % q

    return hex(r)[2:].rjust(40,'0') + hex(s)[2:].rjust(40,'0')

def verify_token_signature(signature, key, sender, to, what, params = (p,q,g)):
    try:
        p = params[0]
        q = params[1]
        g = params[2]

        r, s = int(signature[:40], 16), int(signature[40:], 16)

        assert r > 0
        assert s > 0

        message = f"{sender}-{to}-{what}"
        message_int = int.from_bytes(sha1(message.encode()).digest(), byteorder = "big")
        a = pow(g, (message_int * inverse(s, q)) % q, p)
        b = pow(key, (r * inverse(s, q)) % q, p)
        return (a*b % p) % q == r % p
    except:
        return False
