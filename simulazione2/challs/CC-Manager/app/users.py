import os
import json
import crypto
import base64
import utils

data_path = "data"

def add_new_user(username, password):
    try:
        os.makedirs(os.path.join(data_path, username))

        with open(os.path.join(data_path, username, "vault"), "x") as f:
            f.write(json.dumps({}))

        sharing_key, recovery_token = crypto.get_secret_tokens(username)
        encrypted_psw = crypto.encrypt_psw(recovery_token, password)

        with open(os.path.join(data_path, username, "sharing_key"), "x") as f:
            f.write(str(sharing_key))

        with open(os.path.join(data_path, username, "pw_recovery"), "x") as f:
            f.write(str(encrypted_psw))

        phash = crypto.hash_pw(password)

        with open(os.path.join(data_path, username, "pw_hash"), "x") as f:
            f.write(str(phash))

        open(os.path.join(data_path, username, "shared"), "x").close()

        print(f"Here is your password recovery token: {recovery_token}.")
        print("Be sure to memorize it, you will not see it again!")
        return True
    except FileExistsError:
        print("User already registered!")
        return False
    except:
        return False

def login(username, password):
    try:
        if not os.path.isfile(os.path.join(data_path, username, "pw_hash")):
            print("User does not exist")
            return False

        phash = crypto.hash_pw(password)

        with open(os.path.join(data_path, username, "pw_hash"), "r") as f:
            loaded_hash = f.read().strip()

        if phash != loaded_hash:
            print("Wrong password")
            return False
        return True
    except:
        return False

def recover_password(username, token):
    try:
        if not os.path.isfile(os.path.join(data_path, username, "pw_recovery")):
            return None

        with open(os.path.join(data_path, username, "pw_recovery"), "r") as f:
            pw_recovery = f.read().strip()

        to_decrypt = bytes.fromhex(pw_recovery)
        recovered_pw = crypto.decrypt_psw(token, to_decrypt)
        return recovered_pw
    except:
        return None

def retrieve_vault(username):
    try:
        if not os.path.isfile(os.path.join(data_path, username, "vault")):
            return None

        with open(os.path.join(data_path, username, "vault"), "r") as f:
            vault = json.loads(f.read().strip())

        if len(vault) == 0:
            return None

        return vault
    except:
        return None

def add_password_to_vault(username, service, password):
    try:
        if not os.path.isfile(os.path.join(data_path, username, "vault")):
            return False

        with open(os.path.join(data_path, username, "vault"), "r") as f:
            vault = json.loads(f.read().strip())

        if service in vault:
            return False

        vault[service] = password

        with open(os.path.join(data_path, username, "vault"), "w") as f:
            f.write(json.dumps(vault))

        return True
    except:
        return False

def get_shared_entries(username):
    try:
        if not os.path.isfile(os.path.join(data_path, username, "shared")):
            return None

        to_ret = []

        with open(os.path.join(data_path, username, "shared"), "r") as f:
            shared_passwords = f.readlines()

        shared_passwords = [x.strip() for x in shared_passwords]

        for el in shared_passwords:
            u, p = el.split(":")
            assert len(u) > 0 and len(p) > 0
            to_ret.append((u, p))

        if len(to_ret) == 0:
            return None

        return to_ret
    except:
        return None

def retrieve_password_from_user(username, password_name):
    try:
        if not os.path.isfile(os.path.join(data_path, username, "vault")):
            return False

        with open(os.path.join(data_path, username, "vault"), "r") as f:
            vault = json.loads(f.read().strip())

        if password_name not in vault:
            return None

        return vault[password_name]
    except:
        return None

def retrieve_signing_key(username):
    try:
        if not os.path.isfile(os.path.join(data_path, username, "sharing_key")):
            return False

        with open(os.path.join(data_path, username, "sharing_key"), "r") as f:
            key = int(f.read().strip())

        return key
    except:
        return None

def retrieve_verification_key(username):
    try:
        signing_key = retrieve_signing_key(username)
        key = crypto.verification_from_signing_key(signing_key)
        return key
    except:
        return None

def add_shared_password(username, to_add):
    try:
        if not os.path.isfile(os.path.join(data_path, username, "shared")):
            return None

        to_ret = []

        with open(os.path.join(data_path, username, "shared"), "a") as f:
            f.write(to_add + "\n")
    except:
        return None
