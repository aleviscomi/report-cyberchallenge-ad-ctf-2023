#!/usr/bin/env python3

import os
import sys
import pathlib
import subprocess

from auth import UserStorage, SimpleAuth, TokenAuth, UserNotFound, UserExists, BadUsername, WrongAuth, RegistrationError


SUBDIR_NOTES = 'notes'
SUBDIR_USERS = 'users'

SECRET_KEY = os.environ["SECRET_KEY"].encode()

def banner():
    banner = """===================================================================================
||   NotABook - A simple application for your notes. But definitely not a book.   ||
===================================================================================
||                           ,..........   ..........,                           ||
||                       ,..,'          '.'          ',..,                       ||
||                      ,' ,'            :            ', ',                      ||
||                     ,' ,'             :             ', ',                     ||
||                    ,' ,'              :              ', ',                    ||
||                   ,' ,'............., : ,.............', ',                   ||
||                  ,'  '............   '.'   ............'  ',                  ||
||                   '''''''''''''''''';''';''''''''''''''''''                   ||
||                                      '''                                      ||
===================================================================================
    """
    print()
    print(banner)


def choose_auth(user_storage):
    print()
    print("Choose the authentication provider:")
    print("[1] Simple authentication")
    print("[2] Token authentication")
    print("[0] Exit")
    try:
        choice = int(input("> "))
    except ValueError:
        print("Invalid choice!")
        exit(1)
    if choice < 0 or choice > 2:
        print("Invalid choice!")
        exit(1)

    if choice == 0:
        exit(0)
    if choice == 1:
        return SimpleAuth(user_storage)
    if choice == 2:
        return TokenAuth(user_storage, SECRET_KEY)


def authenticate(auth):
    print()
    print("What do you want to do?")
    print("[1] Login")
    print("[2] Register")
    print("[0] Exit")

    try:
        choice = int(input("> "))
    except ValueError:
        print("Invalid choice!")
        exit(1)
    if choice < 0 or choice > 2:
        print("Invalid choice!")
        exit(1)

    if choice == 0:
        exit(0)

    if choice == 1:
        try:
            return auth.login()
        except BadUsername:
            print("Invalid username!")
        except UserNotFound:
            print("User not found!")
        except WrongAuth:
            print("Wrong authentication method!")
        exit(1)

    if choice == 2:
        username = input("Username: ")
        try:
            auth.register(username)
            return username
        except BadUsername:
            print("Invalid username!")
        except UserExists:
            print("User already exists!")
        except RegistrationError:
            print("Registration failed!")
        exit(1)


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <data root>", file=sys.stderr)
        exit(1)

    data_root = sys.argv[1]

    notes_path = os.path.join(data_root, SUBDIR_NOTES)
    pathlib.Path(notes_path).mkdir(parents=True, exist_ok=True)

    users_path = os.path.join(data_root, SUBDIR_USERS)
    pathlib.Path(users_path).mkdir(parents=True, exist_ok=True)

    user_storage = UserStorage(users_path)

    banner()

    auth = choose_auth(user_storage)

    username = authenticate(auth)
    if username is None:
        print("Authentication failed!")
        exit(1)
    print("Authentication successful.")

    pathlib.Path(os.path.join(notes_path, username)).touch()

    result = subprocess.run(["./bin/notes", notes_path, username])
    exit(result.returncode)


if __name__ == "__main__":
    main()
