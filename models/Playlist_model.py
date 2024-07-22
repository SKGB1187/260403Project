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
        db.ForeignKey('users.id'), 
        nullable=False
    )

    user = db.relationship('User', backref=db.backref('playlists', lazy=True))

    def __repr__(self):
        return f"<User #{self.spotify_playlist_id}: {self.spotify_playlist_name}, {self.spotify_playlist_description}>"