import boto3
import requests
import getpass

from botocore import UNSIGNED
from botocore.client import Config

from datetime import datetime, timedelta


class AuthUserNotFoundException(BaseException):
    """User does not exist."""


class AuthIncorrectUsernameOrPasswordException(BaseException):
    """Incorrect username or password."""


class AuthInvalidPasswordException(BaseException):
    """Invalid password."""


class UserClient:
    """Contains tokens and user credentials. Methods for login etc."""

    def __init__(self, cognito_client_id, api_url):
        self.access_token = None
        self.refresh_token = None
        self.id_token = None
        self.expires = datetime.now()
        # Anonymous client connection without credentials
        self.aws_client = boto3.client(
            "cognito-idp", config=Config(signature_version=UNSIGNED)
        )
        self.cognito_client_id = cognito_client_id
        self.api_url = api_url

    def _update_tokens(self, access_token=None, refresh_token=None, id_token=None):
        if access_token is not None:
            self.access_token = access_token
        if refresh_token is not None:
            self.refresh_token = refresh_token
        if id_token is not None:
            self.id_token = id_token

    def _update_expiration(self, expires_seconds=3600):
        self.expires = datetime.now() + timedelta(seconds=expires_seconds)

    def check_auth(self):
        """Check if we need to get new tokens."""
        now = datetime.now()
        duration = self.expires - now
        if duration.total_seconds() < 0:
            self.refresh_tokens()

    def login(self, username, password):
        """Login user with username and password."""
        try:
            response = self.aws_client.initiate_auth(
                ClientId=self.cognito_client_id,
                AuthFlow="USER_PASSWORD_AUTH",
                AuthParameters={"USERNAME": username, "PASSWORD": password},
            )
        except self.aws_client.exceptions.UserNotFoundException:
            raise AuthUserNotFoundException
        except self.aws_client.exceptions.NotAuthorizedException:
            raise AuthIncorrectUsernameOrPasswordException
        except self.aws_client.exceptions.InvalidParameterException:
            raise AuthIncorrectUsernameOrPasswordException
        if response.get("ChallengeName", None) == "NEW_PASSWORD_REQUIRED":
            session = response.get("Session", None)
            print("New password required.\n")
            new_password = getpass.getpass("Enter new password: ")
            new_password2 = getpass.getpass("Type password again: ")
            if new_password != new_password2:
                print("Error. Passwords did not match.")
                return
            try:
                response = self.aws_client.respond_to_auth_challenge(
                    ClientId=self.cognito_client_id,
                    ChallengeName="NEW_PASSWORD_REQUIRED",
                    Session=session,
                    ChallengeResponses={
                        "USERNAME": username,
                        "NEW_PASSWORD": new_password,
                    },
                )
            except self.aws_client.exceptions.UserNotFoundException:
                raise AuthUserNotFoundException
            except self.aws_client.exceptions.NotAuthorizedException:
                raise AuthIncorrectUsernameOrPasswordException
            except (
                self.aws_client.exceptions.InvalidPasswordException,
                self.aws_client.exceptions.InvalidParameterException,
            ):
                raise AuthInvalidPasswordException
        elif response.get("ChallengeName", None) == "SOFTWARE_TOKEN_MFA":
            session = response.get("Session", None)
            otp = getpass.getpass("Enter one-time password: ")
            try:
                response = self.aws_client.respond_to_auth_challenge(
                    ClientId=self.cognito_client_id,
                    ChallengeName="SOFTWARE_TOKEN_MFA",
                    Session=session,
                    ChallengeResponses={
                        "USERNAME": username,
                        "SOFTWARE_TOKEN_MFA_CODE": otp,
                    },
                )
            except self.aws_client.exceptions.UserNotFoundException:
                raise AuthUserNotFoundException
            except self.aws_client.exceptions.NotAuthorizedException:
                raise AuthIncorrectUsernameOrPasswordException
            except (
                self.aws_client.exceptions.CodeMismatchException,
                self.aws_client.exceptions.InvalidParameterException,
            ):
                raise AuthInvalidPasswordException
        authentication_result = response.get("AuthenticationResult", None)
        if authentication_result is not None:
            access_token = authentication_result.get("AccessToken", None)
            refresh_token = authentication_result.get("RefreshToken", None)
            id_token = authentication_result.get("IdToken", None)
            self._update_tokens(
                access_token=access_token,
                refresh_token=refresh_token,
                id_token=id_token,
            )
            expires = authentication_result.get("ExpiresIn", 3600)
            self._update_expiration(expires)

    def refresh_tokens(self):
        """Refresh tokens."""
        response = self.aws_client.initiate_auth(
            ClientId=self.cognito_client_id,
            AuthFlow="REFRESH_TOKEN_AUTH",
            AuthParameters={"REFRESH_TOKEN": self.refresh_token},
        )
        print("Refresh token used.")
        authentication_result = response.get("AuthenticationResult", None)
        if authentication_result is not None:
            access_token = authentication_result.get("AccessToken", None)
            refresh_token = authentication_result.get("RefreshToken", None)
            id_token = authentication_result.get("IdToken", None)
            self._update_tokens(
                access_token=access_token,
                refresh_token=refresh_token,
                id_token=id_token,
            )
            expires = authentication_result.get("ExpiresIn", 3600)
            self._update_expiration(expires)

    def _call(
        self,
        method="GET",
        endpoint=None,
        data=None,
        json=None,
        callback=None,
        callback_kwargs=None,
    ):
        """Unified method for calling REST APIs, contains Authorization header with Cognito tokens."""
        if endpoint is None:
            return
        self.check_auth()
        headers = {"Authorization": f"Bearer {self.id_token}"}
        api_kwargs = {"headers": headers}
        if method == "GET":
            api_call = requests.get
            api_kwargs.update({"params": data})
        elif method == "POST":
            api_call = requests.post
            api_kwargs.update({"data": data, "json": json})
        elif method == "PUT":
            api_call = requests.put
            api_kwargs.update({"data": data, "json": json})
        elif method == "PATCH":
            api_call = requests.patch
            api_kwargs.update({"data": data, "json": json})
        elif method == "DELETE":
            api_call = requests.delete
            api_kwargs.update({"data": data, "json": json})
        else:
            print("Illegal API method.")
            return
        try:
            r = api_call(f"{self.api_url}/{endpoint}", **api_kwargs)
        except requests.exceptions.ConnectionError:
            print("Connection Error!")
            return
        if r.status_code == 404:
            print("API did not respond.")
            return
        if callable(callback):
            if isinstance(callback_kwargs, dict):
                return callback(r, **callback_kwargs)
            else:
                return callback(r)
        else:
            return r

    def get(self, endpoint=None, data=None, callback=None, callback_kwargs=None):
        """Call api (GET) and send response to callback."""
        return self._call(
            "GET",
            endpoint=endpoint,
            data=data,
            callback=callback,
            callback_kwargs=callback_kwargs,
        )

    def post(
        self, endpoint=None, data=None, json=None, callback=None, callback_kwargs=None
    ):
        """Call api (POST) and send response to callback."""
        return self._call(
            "POST",
            endpoint=endpoint,
            data=data,
            json=json,
            callback=callback,
            callback_kwargs=callback_kwargs,
        )

    def put(
        self, endpoint=None, data=None, json=None, callback=None, callback_kwargs=None
    ):
        """Call api (PUT) and send response to callback."""
        return self._call(
            "PUT",
            endpoint=endpoint,
            data=data,
            json=json,
            callback=callback,
            callback_kwargs=callback_kwargs,
        )

    def patch(
        self, endpoint=None, data=None, json=None, callback=None, callback_kwargs=None
    ):
        """Call api (PATCH) and send response to callback."""
        return self._call(
            "PATCH",
            endpoint=endpoint,
            data=data,
            json=json,
            callback=callback,
            callback_kwargs=callback_kwargs,
        )

    def delete(
        self, endpoint=None, data=None, json=None, callback=None, callback_kwargs=None
    ):
        """Call api (DELETE) and send response to callback."""
        return self._call(
            "DELETE",
            endpoint=endpoint,
            data=data,
            json=json,
            callback=callback,
            callback_kwargs=callback_kwargs,
        )
