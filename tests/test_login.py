import unittest

from botocore.stub import Stubber

from cognito_user_shell.client import UserClient


class TestLogin(unittest.TestCase):

    def test_login(self):
        user_client = UserClient(cognito_client_id='client_id', api_url='http://localhost')
        client = user_client.aws_client
        stubber = Stubber(client)
        login_response = {
            'AuthenticationResult': {
                'AccessToken': 'access_token',
                'ExpiresIn': 123,
                'TokenType': 'Bearer',
                'RefreshToken': 'refresh_token',
                'IdToken': 'id_token',
            }
        }
        expected_params = {
            'AuthFlow': 'USER_PASSWORD_AUTH',
            'ClientId': 'client_id',
            'AuthParameters': {
                'USERNAME': 'testuser',
                'PASSWORD': 'testpass'
            }

        }
        stubber.add_response('initiate_auth', login_response, expected_params)
        with stubber:
            user_client.login('testuser', 'testpass')
        self.assertEqual(user_client.access_token, 'access_token')
        self.assertEqual(user_client.refresh_token, 'refresh_token')
        self.assertEqual(user_client.id_token, 'id_token')


if __name__ == '__main__':
    unittest.main()
