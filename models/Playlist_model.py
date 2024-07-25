from . import db

class Playlist(db.Model):
    """User in the system."""

    __tablename__ = 'playlists'

    spotify_playlist_id = db.Column(
        db.String(256),
        primary_key=True,
    )

    spotify_playlist_name = db.Column(
        db.String(256), 
        nullable=False
    )

    spotify_playlist_description = db.Column(
        db.String(1000), 
        nullable=True
    )

    user_id = db.Column(
        db.Integer, 
        db.ForeignKey('users.id', ondelete='CASCADE'), 
        nullable=False
    )

    def __repr__(self):
        return f"<Playlist #{self.spotify_playlist_id}: {self.spotify_playlist_name}, {self.spotify_playlist_description}>"