from . import db

class Song(db.Model):
    """User in the system."""

    __tablename__ = 'songs'

    spotify_song_id = db.Column(
        db.String(256),
        primary_key=True,
    )

    song_title = db.Column(
        db.String(256), 
        nullable=False
    )
    
    song_artist = db.Column(
        db.String(256), 
        nullable=False
    )

    song_album = db.Column(
        db.String(256), 
        nullable=False
    )

    def __repr__(self):
        return f"<User #{self.spotify_song_id}: {self.song_title}, {self.song_artist}, {self.song_album}>"