import unittest
from unittest.mock import patch, MagicMock
from utils.utils_playlists import add_user_playlist_to_db, add_user_tracks_to_db

class TestUtilsPlaylists(unittest.TestCase):

    @patch('utils.utils_playlists.Playlist')
    @patch('utils.utils_playlists.g')
    def test_add_user_playlist_to_db(self, mock_g, mock_playlist):
        mock_g.user = MagicMock(id=1)
        mock_playlist.is_existing_playlist.return_value = False
        mock_playlist.add_user_playlist.return_value = None

        playlists = [{'id': '1', 'name': 'Test Playlist'}]
        result = add_user_playlist_to_db(playlists)

        self.assertEqual(result, playlists)
        mock_playlist.is_existing_playlist.assert_called_once_with('1')
        mock_playlist.add_user_playlist.assert_called_once()

    @patch('utils.utils_playlists.db')
    @patch('utils.utils_playlists.Artist_Song')
    @patch('utils.utils_playlists.Playlist_Song')
    @patch('utils.utils_playlists.Song')
    @patch('utils.utils_playlists.Artist')
    def test_add_user_tracks_to_db(self, mock_artist, mock_song, mock_playlist_song, mock_artist_song, mock_db):
        mock_artist.is_existing_artist.return_value = False
        mock_artist.add_song_artist.return_value = None
        mock_song.is_existing_song.return_value = False
        mock_song.add_playlist_songs.return_value = None
        mock_playlist_song.add_playlist_song_entry.return_value = None
        mock_artist_song.add_artist_song_entry.return_value = None

        tracks = [{
            'track': {
                'id': '1',
                'name': 'Test Song',
                'album': {'name': 'Test Album'},
                'artists': [{'id': '2', 'name': 'Test Artist'}]
            }
        }]

        add_user_tracks_to_db(tracks, 'playlist_id')

        mock_song.is_existing_song.assert_called_once_with('1')
        mock_song.add_playlist_songs.assert_called_once_with(spotify_song_id='1', song_title='Test Song', song_album='Test Album')
        mock_artist.is_existing_artist.assert_called_once_with('2')
        mock_artist.add_song_artist.assert_called_once_with(spotify_artist_id='2', spotify_artist_name='Test Artist')
        mock_playlist_song.add_playlist_song_entry.assert_called_once_with('playlist_id', '1')
        mock_artist_song.add_artist_song_entry.assert_called_once_with('1', '2')

if __name__ == '__main__':
    unittest.main()