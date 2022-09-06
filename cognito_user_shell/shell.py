import cmd
import getpass
import os

from cognito_user_shell.client import (
    UserClient,
    AuthUserNotFoundException,
    AuthIncorrectUsernameOrPasswordException,
    AuthInvalidPasswordException,
)
from cognito_user_shell.utils import C

# Get login details from env vars (if they exist)
DEFAULT_USER = os.environ.get("DEFAULT_USER", None)
DEFAULT_USER_PASSWORD = os.environ.get("DEFAULT_USER_PASSWORD", None)


class Shell(cmd.Cmd):
    intro = f"{C.CGREEN}Welcome to Cognito User Shell.{C.CEND} Type help or ? to list commands.\n"
    doc_header = "Commands (type help <topic>)"
    prompt = "> "

    def __init__(self, cognito_client_id, api_url, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = UserClient(cognito_client_id, api_url)
        self.cognito_client_id = cognito_client_id
        self.api_url = api_url
        self.username = "anonymous"
        self.logged_in = False

    def preloop(self):
        """Do automatic login if we have stored credentials."""
        if DEFAULT_USER is not None and DEFAULT_USER_PASSWORD is not None:
            return self.do_login("{} {}".format(DEFAULT_USER, DEFAULT_USER_PASSWORD))

    def emptyline(self):
        """By default when an empty line is entered, the last command is repeated."""
        pass

    @staticmethod
    def do_exit(_):
        """Exit application."""
        print("Thank you, bye!")
        return True

    def do_login(self, line):
        """Log in with username and password."""
        if self.logged_in:
            print(
                "You are already logged in.\nIf you want to login as a different user, type 'logout' first."
            )
            return
        arg = line.split()
        if len(arg) > 0:
            username = arg[0]
        else:
            username = input("Username: ")
        if len(arg) == 2:
            password = arg[1]
        else:
            password = getpass.getpass("Password: ")
        try:
            self.client.login(username, password)
        except AuthUserNotFoundException:
            print("Error. User does not exist.")
            return
        except AuthIncorrectUsernameOrPasswordException:
            print("Error. Incorrect username or password.")
            return
        except AuthInvalidPasswordException:
            print("Error. Invalid password.")
            return
        self.logged_in = True
        self.username = username
        print(f"{C.CVIOLET}You are now logged in ({username}).{C.CEND}")

    def do_logout(self, _):
        """Log out as user."""
        if not self.logged_in:
            print("You're already logged out.")
            return
        self.client = UserClient(self.cognito_client_id, self.api_url)
        self.logged_in = False
        self.username = "anonymous"
        print("Logged out.")
