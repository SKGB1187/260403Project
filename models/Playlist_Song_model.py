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
        db.ForeignKey('songs.spotify_song_id', ondelete='CASCADE'), 
        nullable=False
    )

    spotify_playlist_id = db.Column(
        db.String(256), 
        db.ForeignKey('playlists.spotify_playlist_id', ondelete='CASCADE'), 
        nullable=False
    )

    def __repr__(self):
        return f"<Playlist_Song #{self.id}: {self.spotify_song_id}, {self.spotify_playlist_id}>"