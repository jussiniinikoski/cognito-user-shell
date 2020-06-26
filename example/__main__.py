import os
import sys
# noinspection PyUnresolvedReferences
from shell import ExampleShell

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