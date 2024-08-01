import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User, Artist, Artist_Song, Playlist, Playlist_Song, Song

class TestModels(unittest.TestCase):

    def setUp(self):
        """Set up a test database and session."""
        self.engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

    def tearDown(self):
        """Clean up the session and database after each test."""
        self.session.close()
        Base.metadata.drop_all(self.engine)

class TestUserModel(TestModels):

    def test_signup(self):
        """Test user signup."""
        result = User.signup(username="testuser", email="test@test.com", password="password")
        self.assertTrue(result.is_success)
        self.assertEqual(result.value.username, "testuser")

    def test_authenticate(self):
        """Test user authentication."""
        User.signup(username="testuser", email="test@test.com", password="password")
        user = User.authenticate(username="testuser", password="password")
        self.assertIsNotNone(user)
        self.assertEqual(user.username, "testuser")

    def test_link_spotify_to_database(self):
        """Test linking Spotify to user account."""
        user = User.signup(username="testuser", email="test@test.com", password="password").value
        linked_user = User.link_spotify_to_database(user_id=user.id, spotify_access_token="access_token", spotify_access_token_set_time="01/08/2024", spotify_refresh_token="refresh_token")
        self.assertEqual(linked_user.spotify_access_token, "access_token")

class TestArtistModel(TestModels):

    def test_add_song_artist(self):
        """Test adding an artist to the database."""
        result = Artist.add_song_artist(spotify_artist_id="artist_123", spotify_artist_name="Test Artist")
        self.assertTrue(result.is_success)
        self.assertEqual(result.value.spotify_artist_name, "Test Artist")

    def test_is_existing_artist(self):
        """Test checking if an artist exists."""
        Artist.add_song_artist(spotify_artist_id="artist_123", spotify_artist_name="Test Artist")
        exists = Artist.is_existing_artist("artist_123")
        self.assertTrue(exists)

class TestSongModel(TestModels):

    def test_add_playlist_songs(self):
        """Test adding a song to the database."""
        result = Song.add_playlist_songs(spotify_song_id="song_123", song_title="Test Song", song_album="Test Album")
        self.assertTrue(result.is_success)
        self.assertEqual(result.value.song_title, "Test Song")

    def test_is_existing_song(self):
        """Test checking if a song exists."""
        Song.add_playlist_songs(spotify_song_id="song_123", song_title="Test Song", song_album="Test Album")
        exists = Song.is_existing_song("song_123")
        self.assertTrue(exists)

class TestPlaylistModel(TestModels):

    def test_add_user_playlist(self):
        """Test adding a playlist to the database."""
        result = Playlist.add_user_playlist(spotify_playlist_id="playlist_123", spotify_playlist_name="Test Playlist", spotify_playlist_description="A test playlist", user_id=1)
        self.assertTrue(result.is_success)
        self.assertEqual(result.value.spotify_playlist_name, "Test Playlist")

    def test_is_existing_playlist(self):
        """Test checking if a playlist exists."""
        Playlist.add_user_playlist(spotify_playlist_id="playlist_123", spotify_playlist_name="Test Playlist", spotify_playlist_description="A test playlist", user_id=1)
        exists = Playlist.is_existing_playlist("playlist_123")
        self.assertTrue(exists)

class TestArtistSongModel(TestModels):

    def test_add_artist_song_entry(self):
        """Test adding an artist-song entry."""
        artist = Artist.add_song_artist(spotify_artist_id="artist_123", spotify_artist_name="Test Artist").value
        song = Song.add_playlist_songs(spotify_song_id="song_123", song_title="Test Song", song_album="Test Album").value
        result = Artist_Song.add_artist_song_entry(spotify_song_id=song.spotify_song_id, spotify_artist_id=artist.spotify_artist_id)
        self.assertTrue(result.is_success)
        self.assertEqual(result.value.spotify_song_id, song.spotify_song_id)

    def test_is_existing_artist_song_combination(self):
        """Test checking if an artist-song combination exists."""
        artist = Artist.add_song_artist(spotify_artist_id="artist_123", spotify_artist_name="Test Artist").value
        song = Song.add_playlist_songs(spotify_song_id="song_123", song_title="Test Song", song_album="Test Album").value
        Artist_Song.add_artist_song_entry(spotify_song_id=song.spotify_song_id, spotify_artist_id=artist.spotify_artist_id)
        exists = Artist_Song.is_existing_artist_song_combination(song.spotify_song_id, artist.spotify_artist_id)
        self.assertTrue(exists)

class TestPlaylistSongModel(TestModels):

    def test_add_playlist_song_entry(self):
        """Test adding a playlist-song entry."""
        playlist = Playlist.add_user_playlist(spotify_playlist_id="playlist_123", spotify_playlist_name="Test Playlist", spotify_playlist_description="A test playlist", user_id=1).value
        song = Song.add_playlist_songs(spotify_song_id="song_123", song_title="Test Song", song_album="Test Album").value
        result = Playlist_Song.add_playlist_song_entry(spotify_playlist_id=playlist.spotify_playlist_id, spotify_song_id=song.spotify_song_id)
        self.assertTrue(result.is_success)
        self.assertEqual(result.value.spotify_playlist_id, playlist.spotify_playlist_id)

    def test_is_existing_playlist_song_combination(self):
        """Test checking if a playlist-song combination exists."""
        playlist = Playlist.add_user_playlist(spotify_playlist_id="playlist_123", spotify_playlist_name="Test Playlist", spotify_playlist_description="A test playlist", user_id=1).value
        song = Song.add_playlist_songs(spotify_song_id="song_123", song_title="Test Song", song_album="Test Album").value
        Playlist_Song.add_playlist_song_entry(spotify_playlist_id=playlist.spotify_playlist_id, spotify_song_id=song.spotify_song_id)
        exists = Playlist_Song.is_existing_playlist_song_combination(playlist.spotify_playlist_id, song.spotify_song_id)
        self.assertTrue(exists)

