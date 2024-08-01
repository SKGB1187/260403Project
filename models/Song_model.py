from . import db

from .DBActionResult import DBActionResult

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

    song_album = db.Column(
        db.String(256), 
        nullable=False
    )

    def __repr__(self):
        return f"<Song #{self.spotify_song_id}: {self.song_title}, {self.song_album}>"
    
    @classmethod
    def add_playlist_songs(cls, spotify_song_id, song_title, song_album):
        """Add user playlists to database from Spotify API query"""
        ret: DBActionResult[Song] = DBActionResult(None, False, "")
        
        try:
            new_song = cls(
                spotify_song_id=spotify_song_id,
                song_title=song_title,
                song_album=song_album,
                )
            db.session.add(new_song)
            db.session.commit()

            ret.value = new_song
            ret.is_success = True
            ret.message = "Song successfully added!"
        
        except Exception as e:
            print("Exception:", str(e))
            db.session.rollback()
            ret.message = 'Sorry, an error occurred during song add, please try again.'

        return ret

    @classmethod
    def is_existing_song(cls, spotify_song_id):
        ret = False
        existing = Song.query.filter_by(spotify_song_id=spotify_song_id).first()
        if existing:
            ret = True

        return ret