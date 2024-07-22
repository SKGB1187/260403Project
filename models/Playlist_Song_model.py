from . import db

class Playlist_Song(db.Model):
    """User in the system."""

    __tablename__ = 'playlist_song_join'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    spotify_song_id = db.Column(
        db.String(256), 
        db.ForeignKey('songs.spotify_song_id'), 
        nullable=False
    )

    songs = db.relationship('Song', backref=db.backref('playlist_song_join', lazy=True))

    spotify_playlist_id = db.Column(
        db.String(256), 
        db.ForeignKey('artists.spotify_artist_id'), 
        nullable=False
    )

    playlists = db.relationship('Playlist', backref=db.backref('playlist_song_join', lazy=True))

    def __repr__(self):
        return f"<User #{self.id}: {self.spotify_song_id}, {self.spotify_playlist_id}>"