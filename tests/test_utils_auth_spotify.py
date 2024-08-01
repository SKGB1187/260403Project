import unittest
from unittest.mock import patch, MagicMock
from utils.utils_auth_spotify import (
    generate_random_string,
    sha256,
    base64encode,
    run_refresh_token,
    get_token,
    get_refresh_token,
)
from flask import Flask, g
from models import User

app = Flask(__name__)

class TestUtilsAuthSpotify(unittest.TestCase):

    def test_generate_random_string(self):
        result = generate_random_string(10)
        self.assertEqual(len(result), 10)

    def test_sha256(self):
        hashed = sha256("test")
        self.assertEqual(type(hashed), bytes)
        self.assertEqual(len(hashed), 32) 

    def test_base64encode(self):
        encoded = base64encode(b'test')
        self.assertEqual(encoded, 'dGVzdA')

    @patch('utils.utils_auth_spotify.g')
    @patch('utils.utils_auth_spotify.User')
    def test_run_refresh_token(self, mock_user, mock_g):
        mock_g.user = MagicMock(spotify_refresh_token="mock_refresh_token")
        mock_user.link_spotify_to_database.return_value = None

        with patch('utils.utils_auth_spotify.get_refresh_token') as mock_get_refresh_token, \
             patch('utils.utils_auth_spotify.render_template') as mock_render_template, \
             app.app_context():
            mock_get_refresh_token.return_value = {
                'access_token': 'new_access_token',
                'refresh_token': 'new_refresh_token'
            }

            result = run_refresh_token()
            self.assertTrue(result)
            mock_user.link_spotify_to_database.assert_called_once()

    @patch('requests.post')
    def test_get_token(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {'access_token': 'test_access_token'}
        mock_post.return_value = mock_response

        result = get_token('code', 'code_verifier')
        self.assertEqual(result, {'access_token': 'test_access_token'})

    @patch('requests.post')
    def test_get_refresh_token(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {'access_token': 'new_access_token'}
        mock_post.return_value = mock_response

        result = get_refresh_token('refresh_token')
        self.assertEqual(result, {'access_token': 'new_access_token'})

if __name__ == '__main__':
    unittest.main()
