from . import db

from .DBActionResult import DBActionResult

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
    
    @classmethod
    def add_song_artist(cls, spotify_artist_id, spotify_artist_name):
        """Add user playlists to database from Spotify API query"""
        ret: DBActionResult[Artist] = DBActionResult(None, False, "")
        
        try:
            new_artist = cls(
                spotify_artist_id=spotify_artist_id,
                spotify_artist_name=spotify_artist_name
                )
            db.session.add(new_artist)
            db.session.commit()

            ret.value = new_artist
            ret.is_success = True
            ret.message = "Artist successfully added!"
        
        except Exception as e:
            print("Exception:", str(e))
            db.session.rollback()
            ret.message = 'Sorry, an error occurred during artist add, please try again.'

        return ret

    @classmethod
    def is_existing_artist(cls, spotify_artist_id):
        ret = False
        existing = Artist.query.filter_by(spotify_artist_id=spotify_artist_id).first()
        if existing:
            ret = True

        return ret