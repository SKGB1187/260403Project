from . import db

class UserPlayListDisplay(db.Model):
    """User in the system."""

    __tablename__ = 'user_playlist_display'
    __table_args__ = {'info': dict(is_view=True)}

    user_id = db.Column(
        db.Integer()
        ,primary_key=True,
    )

    spotify_playlist_id = db.Column(
        db.String(256)
        ,primary_key=True,
    )

    spotify_playlist_name = db.Column(
        db.String(256)
    )

    spotify_song_id = db.Column(
        db.String(256)
        ,primary_key=True,
    )

    song_title = db.Column(
        db.String(256)
    )

    song_album = db.Column(
        db.String(256)
    )

    spotify_artist_name = db.Column(
        db.String(256)
        ,primary_key=True,
    )

    def __repr__(self):
        return f"<Song #{self.user_id}: {self.spotify_playlist_id}, {self.spotify_playlist_name}, {self.spotify_song_id}, {self.song_title}, {self.song_album}, {self.spotify_artist_name}>"