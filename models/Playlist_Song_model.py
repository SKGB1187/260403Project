from . import db

from models import DBActionResult

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
    
    @classmethod
    def add_playlist_song_entry(cls, spotify_playlist_id, spotify_song_id):
        """Add user playlists to database from Spotify API query"""
        ret: DBActionResult[Playlist_Song] = DBActionResult(None, False, "")
        if not Playlist_Song.is_existing_playlist_song_combination():
            try:
                new_playlist_song = cls(
                    spotify_playlist_id=spotify_playlist_id,
                    spotify_song_id=spotify_song_id
                    )
                db.session.add(new_playlist_song)
                db.session.commit()

                ret.value = new_playlist_song
                ret.is_success = True
                ret.message = "Artist_Song successfully added!"
            
            except Exception as e:
                print("Exception:", str(e))
                db.session.rollback()
                ret.message = 'Sorry, an error occurred during artist add, please try again.'

            return ret

    @classmethod
    def is_existing_playlist_song_combination(cls, spotify_playlist_id, spotify_song_id):
        ret = False
        existing = Playlist_Song.query.filter_by(spotify_playlist_id=spotify_playlist_id).first()
        for spotify_song_id in existing:
            if spotify_song_id == spotify_song_id:
                ret = True
                return ret
                
        return ret