import unittest
from flask import session
from __init__ import app, db, CURR_USER_KEY
from models import User, Playlist, Song

class FlaskAppTests(unittest.TestCase):
    
    def setUp(self):
        """Setup test client and database"""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = app.test_client()
        
        with app.app_context():
            db.create_all()
            self.add_sample_data()
    
    def tearDown(self):
        """Teardown database"""
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def add_sample_data(self):
        """Add sample data for testing"""
        user = User.signup(username='testuser', email='test@test.com', password='password')
        db.session.add(user)
        db.session.commit()
        
        self.user_id = user.id

    def login(self):
        """Login helper method"""
        return self.client.post('/login', data=dict(
            username='testuser',
            password='password'
        ), follow_redirects=True)
    
    def test_signup(self):
        """Test user signup"""
        response = self.client.post('/sign_up', data=dict(
            username='newuser',
            email='newuser@test.com',
            password='password',
            csrf_token=session['_csrf_token']
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Account created successfully!', response.data)
    
    def test_login(self):
        """Test user login"""
        response = self.login()
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Logged in successfully!', response.data)
        with self.client.session_transaction() as sess:
            self.assertEqual(sess[CURR_USER_KEY], self.user_id)
    
    def test_logout(self):
        """Test user logout"""
        self.login()
        response = self.client.get('/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'You have been logged out.', response.data)
        with self.client.session_transaction() as sess:
            self.assertNotIn(CURR_USER_KEY, sess)
    
    def test_profile_update(self):
        """Test profile update"""
        self.login()
        with self.client.session_transaction() as sess:
            sess['user_id'] = self.user_id
        response = self.client.get('/update_profile')
        self.assertEqual(response.status_code, 200)
    
    def test_playlist_retrieval(self):
        """Test playlist retrieval"""
        self.login()
        response = self.client.get('/playlists')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'playlists', response.data)
    
    def test_create_playlist(self):
        """Test create playlist"""
        self.login()
        response = self.client.post('/create_playlist', data=dict(
            playlist_name='Test Playlist',
            playlist_description='This is a test playlist.',
            csrf_token=session['_csrf_token']
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Playlist created successfully!', response.data)
    
    def test_view_specific_playlist(self):
        """Test view specific playlist"""
        self.login()
        playlist = Playlist(spotify_playlist_id='1', spotify_playlist_name='Test Playlist', user_id=self.user_id)
        db.session.add(playlist)
        db.session.commit()
        response = self.client.get(f'/playlist/{playlist.spotify_playlist_id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Playlist', response.data)
    
    def test_add_song_to_playlist(self):
        """Test add song to playlist"""
        self.login()
        playlist = Playlist(spotify_playlist_id='1', spotify_playlist_name='Test Playlist', user_id=self.user_id)
        db.session.add(playlist)
        db.session.commit()
        song = Song(spotify_song_id='1', song_title='Test Song', song_album='Test Album')
        db.session.add(song)
        db.session.commit()
        response = self.client.post('/add_to_playlist', data=dict(
            song_id=song.spotify_song_id,
            playlist_id=playlist.spotify_playlist_id
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Song added to playlist successfully!', response.data)