from . import db

from .DBActionResult import DBActionResult

class Artist_Song(db.Model):
    """User in the system."""

    __tablename__ = 'artist_song_join'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    spotify_song_id = db.Column(
        db.String(256), 
        db.ForeignKey('songs.spotify_song_id', ondelete='CASCADE'), 
        nullable=False
    )

    spotify_artist_id = db.Column(
        db.String(256), 
        db.ForeignKey('artists.spotify_artist_id', ondelete='CASCADE'), 
        nullable=False,

    )

    def __repr__(self):
        return f"<Artist_Song #{self.id}: {self.spotify_song_id}, {self.spotify_artist_id}>"
    
    @classmethod
    def add_artist_song_entry(cls, spotify_song_id, spotify_artist_id):
        """Add user playlists to database from Spotify API query"""
        ret: DBActionResult[Artist_Song] = DBActionResult(None, False, "")
        if not Artist_Song.is_existing_artist_song_combination(spotify_song_id, spotify_artist_id):
            try:
                new_artist_song = cls(
                    spotify_song_id = spotify_song_id,
                    spotify_artist_id = spotify_artist_id
                    )
                db.session.add(new_artist_song)
                db.session.commit()

                ret.value = new_artist_song
                ret.is_success = True
                ret.message = "Artist_Song successfully added!"
            
            except Exception as e:
                print("Exception:", str(e))
                db.session.rollback()
                ret.message = 'Sorry, an error occurred during artist add, please try again.'

            return ret

    @classmethod
    def is_existing_artist_song_combination(cls, spotify_song_id, spotify_artist_id):
        ret = False
        existing = Artist_Song.query.filter_by(spotify_song_id=spotify_song_id, spotify_artist_id = spotify_artist_id).first()
        if existing:
            ret = True
                 
        return ret