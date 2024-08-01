from . import db

from flask import g

from .DBActionResult import DBActionResult

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
    
    @classmethod
    def add_user_playlist(cls, spotify_playlist_id, spotify_playlist_name, spotify_playlist_description, user_id):
        """Add user playlists to database from Spotify API query"""
        ret: DBActionResult[Playlist] = DBActionResult(None, False, "")
        
        try:
            new_playlist = cls(
                spotify_playlist_id=spotify_playlist_id,
                spotify_playlist_name=spotify_playlist_name,
                spotify_playlist_description=spotify_playlist_description,
                user_id=user_id)
            db.session.add(new_playlist)
            db.session.commit()

            ret.value = new_playlist
            ret.is_success = True
            ret.message = "Playlist successfully added!"
        
        except Exception as e:
            print("Exception:", str(e))
            db.session.rollback()
            ret.message = 'Sorry, an error occurred during playlist add, please try again.'

        return ret

    @classmethod
    def is_existing_playlist(cls, spotify_playlist_id):
        ret = False
        existing = Playlist.query.filter_by(spotify_playlist_id=spotify_playlist_id).first()
        if existing:
            ret = True

        return ret