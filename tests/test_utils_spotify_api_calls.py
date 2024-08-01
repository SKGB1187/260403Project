import unittest
from unittest.mock import patch, MagicMock
from utils.utils_spotify_api_calls import (
    add_song_to_spotify_playlist,
    create_spotify_playlist,
    get_spotify_profile,
    get_spotify_song,
    get_user_playlists,
    populate_user_playlists,
)

class TestUtilsSpotifyApiCalls(unittest.TestCase):

    @patch('utils.utils_spotify_api_calls.g')
    @patch('requests.post')
    def test_add_song_to_spotify_playlist(self, mock_post, mock_g):
        mock_g.user = MagicMock(spotify_access_token='access_token')
        mock_post.return_value.status_code = 201

        response = add_song_to_spotify_playlist('song_id', 'playlist_id')
        self.assertEqual(response.status_code, 201)

    @patch('utils.utils_spotify_api_calls.g')
    @patch('requests.post')
    @patch('utils.utils_spotify_api_calls.flash')
    @patch('utils.utils_spotify_api_calls.render_template')
    def test_create_spotify_playlist(self, mock_render_template, mock_flash, mock_post, mock_g):
        mock_g.user = MagicMock(spotify_access_token='access_token', spotify_user_id='user_id')
        mock_post.return_value.status_code = 201

        create_spotify_playlist('Test Playlist', 'Description')

        mock_flash.assert_called_once_with('Playlist creation successful!', 'success')
        mock_render_template.assert_called_once_with('redirects/redirect_to_user_playlists.html')

    @patch('utils.utils_spotify_api_calls.g')
    @patch('requests.get')
    def test_get_spotify_profile(self, mock_get, mock_g):
        mock_g.user = MagicMock(spotify_access_token='access_token')
        mock_response = MagicMock()
        mock_response.json.return_value = {'display_name': 'Test User'}
        mock_get.return_value = mock_response

        response = get_spotify_profile()
        self.assertEqual(response, {'display_name': 'Test User'})

    @patch('utils.utils_spotify_api_calls.g')
    @patch('requests.get')
    def test_get_spotify_song(self, mock_get, mock_g):
        mock_g.user = MagicMock(spotify_access_token='access_token')
        mock_response = MagicMock()
        mock_response.json.return_value = {'tracks': []}
        mock_get.return_value = mock_response

        response = get_spotify_song('Test Song')
        self.assertEqual(response, {'tracks': []})

    @patch('utils.utils_spotify_api_calls.g')
    @patch('requests.get')
    def test_get_user_playlists(self, mock_get, mock_g):
        mock_g.user = MagicMock(spotify_access_token='access_token')
        mock_response = MagicMock()
        mock_response.json.return_value = {'items': []}
        mock_get.return_value = mock_response
        mock_get.return_value.status_code = 200

        response = get_user_playlists()
        self.assertEqual(response, [])

    @patch('utils.utils_spotify_api_calls.g')
    @patch('requests.get')
    def test_populate_user_playlists(self, mock_get, mock_g):
        mock_g.user = MagicMock(spotify_access_token='access_token')
        mock_response = MagicMock()
        mock_response.json.return_value = {'items': []}
        mock_get.return_value = mock_response
        mock_get.return_value.status_code = 200

        tracks = populate_user_playlists('playlist_id')
        self.assertEqual(tracks, [])

if __name__ == '__main__':
    unittest.main()