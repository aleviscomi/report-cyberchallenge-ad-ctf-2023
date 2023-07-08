from interface import *
import utils
import users
import crypto
import json
import base64

def login_menu():
    print(login_menu_string)
    ch = int(input())

    if ch < 0 or ch > 3:
        print("Unrecognized command")

    elif ch == 0:
        raise SystemExit()

    elif ch == 3:
        username = input("Enter your username: ")
        recovery_token = input("Enter your password recovery token: ")

        if not utils.validate_string(username) or not utils.validate_string(recovery_token) or len(recovery_token) != 16:
            print("It seems that this username or this token are not valid!")
        else:
            recovered_pw = users.recover_password(username, recovery_token)

            if recovered_pw is None or not utils.validate_string(recovered_pw):
                print("Username or token are wrong!")
            else:
                print(f"Here is your password: {recovered_pw.decode()}")

    else:
        username = input("Enter your username: ")
        password = input("Enter your password: ")
        if not utils.validate_string(username) or not utils.validate_string(password):
            print("It seems that this username or this password are not valid! Remember: only letters and digits with length between 8 and 64.")
        else:
            if ch == 1:
                if users.add_new_user(username, password):
                    print(f"User {username} registered successfully!")
                    return username
                else:
                    print("Registration failed.")
            else:
                if users.login(username, password):
                    print(f"Logged in as {username}")
                    return username
                else:
                    print("Login failed")
    return None

def manager_menu(user):
    print(manager_menu_string)
    ch = int(input())

    if ch < 0 or ch > 6:
        print("Unrecognized command")

    elif ch == 0:
        raise SystemExit()

    elif ch == 6:
        print("Logged out.")
        return None

    elif ch == 1:
        srv = input("Enter the service for which you want to store the password: ")
        psw = input("Enter the password you want to store: ")

        if not utils.validate_string(srv) or not utils.validate_string(psw):
            print("It seems that this service or this password are not valid! Remember: only letters and digits with length between 8 and 64.")
        else:
            chk = users.add_password_to_vault(user, srv, psw)

            if not chk:
                print("An error occurred. Password was not added.")
            else:
                print("Password added successfully.")

    elif ch == 2:
        vault = users.retrieve_vault(user)

        if vault is None:
            print("There is no saved password here.")
        else:
            print("Your saved passwords:")
            for srv in vault:
                print(f"\t{srv}: {vault[srv]}")

    elif ch == 3:
        shared_with_me = users.get_shared_entries(user)

        if shared_with_me is None:
            print("There are no passwords shared with you")
        else:
            to_print = []
            for u, p in shared_with_me:
                rec = users.retrieve_password_from_user(u, p)
                to_print.append((u,p,rec))

            if len(to_print) > 0:
                print("Passwords shared with you:")
                for u, p, rec in to_print:
                    print(f"\t{p}: {rec} from user {u}")
            else:
                print("There are no passwords shared with you")

    elif ch == 4:
        password_name = input("Enter the name of the service corresponding to the password you want to share: ")
        receiver = input("Enter the username of the user you want to share it with: ")

        if not utils.validate_string(receiver) or not utils.validate_string(password_name):
            print("It seems that this user or this service name are not valid.")
        else:
            chk = users.retrieve_password_from_user(user, password_name)

            if chk is None:
                print("It seems that you don't have this password")
            else:
                token = {"sender": user, "to": receiver, "what": password_name}
                key = users.retrieve_signing_key(user)
                to_sign = '-'.join([x for x in token.values()])
                token = json.dumps(token)
                signature = crypto.sign_token(key, to_sign)

                if signature is None:
                    print("Something went wrong computing the signature. Please try again.")
                else:
                    final_token = base64.b64encode(token.encode() + b"|" + signature.encode()).decode()
                    print(f"Here is your token {final_token}")

    elif ch == 5:
        token = input("Insert your token: ")

        try:
            decoded_token = base64.b64decode(token)
            js, signature = decoded_token.split(b"|")

            assert len(js) > 0 and len(signature) > 0

            js = js.decode()
            signature = signature.decode()
            js = json.loads(js)

            assert js["to"] == user

            key = users.retrieve_verification_key(js["sender"])
            ver = crypto.verify_token_signature(signature, key, **js)

            if not ver:
                print("Signature verification failed.")
            else:
                to_add = js["sender"] + ":" + js["what"]
                users.add_shared_password(user, to_add)

            print("Password added successfully.")
        except:
            print("An error occurred in parsing your token.")
    return user

def main():
    user = None
    print(banner_string)

    while True:
        try:
            if user is None:
                user = login_menu()
            else:
                user = manager_menu(user)
        except SystemExit:
            print("Bye!")
            exit()
        except:
            print(f"Something bad happened...")
            exit()

if __name__ == '__main__':
    main()
