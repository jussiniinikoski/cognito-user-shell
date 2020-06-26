from cognito_user_shell.shell import Shell
from cognito_user_shell.utils import C

# noinspection PyUnresolvedReferences
from api.user import change_password

_USER_CMDS = ('changepasswd', )


class ExampleShell(Shell):

    intro = f'{C.CGREEN}Welcome to Example Shell.{C.CEND} Type help or ? to list commands.\n'

    def do_user(self, line):
        """User related commands. Type 'user' to view subcommands."""
        if not self.logged_in:
            print("Log in first (type: login).")
            return
        args = line.split()
        if len(args) == 0:
            print(f"Logged in as {C.CVIOLET}{self.username}{C.CEND}")
            print(f"Available commands: {', '.join(_USER_CMDS)}")
            return
        if args[0] == _USER_CMDS[0]:
            change_password(self.client)
        else:
            print(f"Unknown command: {args[0]}")

    @staticmethod
    def complete_user(text, *_args):
        return [i for i in _USER_CMDS if i.startswith(text)]

    def do_hello(self, _):
        """Call your REST API with authentication header."""
        def output_response(resp):
            print(resp.json())
        self.client.get('hello/', callback=output_response)


if __name__ == '__main__':
    import os
    import sys
    # Get default settings from env vars (if they exist)
    DEFAULT_USER = os.environ.get("DEFAULT_USER", None)
    DEFAULT_USER_PASSWORD = os.environ.get("DEFAULT_USER_PASSWORD", None)
    COGNITO_CLIENT_ID = os.environ.get("COGNITO_CLIENT_ID", None)
    API_URL = os.environ.get("API_URL", None)
    if COGNITO_CLIENT_ID is not None and API_URL is not None:
        try:
            ExampleShell(cognito_client_id=COGNITO_CLIENT_ID, api_url=API_URL).cmdloop()
        except KeyboardInterrupt:
            sys.stdout.write('\n')
