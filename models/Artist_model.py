from . import db

class Artist(db.Model):
    """Artists user listens to."""

    __tablename__ = 'artists'

    spotify_artist_id = db.Column(
        db.String(256),
        primary_key=True,
    )

    spotify_artist_name = db.Column(
        db.String(256), 
        nullable=False
    )

    def __repr__(self):
        return f"<Artist #{self.spotify_artist_id}: {self.spotify_artist_name}"