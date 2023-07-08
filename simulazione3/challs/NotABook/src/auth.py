import os
import json
import string
import subprocess
from Crypto.Cipher import AES
from abc import ABC, abstractmethod


class UserNotFound(Exception):
    pass


class UserExists(Exception):
    pass


class BadUsername(Exception):
    pass


class UserStorage:
    def __init__(self, path):
        self.path = path

    def add_user(self, username, data):
        """Adds a user. May raise BadUsername, UserExists."""
        self._check_username(username)
        try:
            with open(os.path.join(self.path, username), "x") as f:
                json.dump(data, f)
        except FileExistsError:
            raise UserExists()

    def get_user_data(self, username):
        """Gets a user's data. May raise BadUsername, UserNotFound."""
        self._check_username(username)
        try:
            with open(os.path.join(self.path, username), "r") as f:
                return json.load(f)
        except FileNotFoundError:
            raise UserNotFound()

    @staticmethod
    def _check_username(username):
        if len(username) > 100:
            raise BadUsername()
        alphabet = set(string.ascii_letters + string.digits + '-._')
        if any(c not in alphabet for c in username):
            raise BadUsername()


class WrongAuth(Exception):
    pass


class RegistrationError(Exception):
    pass


class Auth(ABC):
    @abstractmethod
    def login(self):
        """Performs authentication.
        Returns the username on success, or None on failure.
        May raise BadUsername, UserNotFound, WrongAuth."""
        pass

    @abstractmethod
    def register(self, username):
        """Performs registration of the given username.
        May raise BadUsername, UserExists, RegistrationError."""
        pass


class SimpleAuth(Auth):
    def __init__(self, user_storage):
        self.user_storage = user_storage

    def login(self):
        username = input("Username: ")

        user_data = self.user_storage.get_user_data(username)
        if user_data["auth"] != "simple":
            raise WrongAuth()

        result = subprocess.run([
            "./bin/simple_auth",
            "login",
            user_data["data"],
        ])
        return username if result.returncode == 0 else None


    def register(self, username):
        password = input("Password: ")

        result = subprocess.run([
            "./bin/simple_auth",
            "register",
            password,
        ], capture_output=True)
        if result.returncode != 0:
            raise RegistrationError()

        self.user_storage.add_user(username, {
            "auth": "simple",
            "data": result.stdout.decode(),
        })


class TokenAuth(Auth):
    def __init__(self, user_storage, secret_key):
        self.user_storage = user_storage
        self.secret_key = secret_key

    def login(self):
        token = input("Give me your login token: ")
        try:
            token = bytes.fromhex(token)
        except ValueError:
            return None
        if len(token) < 16:
            return None

        iv = token[:16]
        ct = token[16:]

        cipher = AES.new(self.secret_key, AES.MODE_OFB, iv)
        data = cipher.decrypt(ct)
        try:
            data = json.loads(data)
        except json.decoder.JSONDecodeError:
            return None

        username = data["username"]
        user_data = self.user_storage.get_user_data(username)
        if user_data["auth"] != "token":
            raise WrongAuth()

        return username

    def register(self, username):
        iv = os.urandom(16)
        cipher = AES.new(self.secret_key, AES.MODE_OFB, iv)
        token = {"username": username}
        ct = iv + cipher.encrypt(json.dumps(token).encode())

        self.user_storage.add_user(username, {'auth': 'token'})

        print(f"You can login with your encrypted token: {ct.hex()}")
