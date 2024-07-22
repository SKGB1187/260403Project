from . import db

class Artist_Song(db.Model):
    """User in the system."""

    __tablename__ = 'artist_song_join'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    spotify_song_id = db.Column(
        db.String(256), 
        db.ForeignKey('songs.spotify_song_id'), 
        nullable=False
    )

    songs = db.relationship('Song', backref=db.backref('artist_song_join', lazy=True))

    spotify_artist_id = db.Column(
        db.String(256), 
        db.ForeignKey('artists.spotify_artist_id'), 
        nullable=False
    )

    artists = db.relationship('Artist', backref=db.backref('artist_song_join', lazy=True))

    def __repr__(self):
        return f"<User #{self.id}: {self.spotify_song_id}, {self.spotify_artist_id}>"