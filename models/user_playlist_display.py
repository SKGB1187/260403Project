from . import db

### Note this is a view model for displaying the playlist information for a user, to
### get around the issues with SQLalchemy and to avoid many many calls to the database
### this was created and implemented. For a production server the following will need 
### to be done on the database for proper application functionality.

    # Create View from Database using the following Query

    #create or replace view user_playlist_display as

    #select distinct
    #       a.user_id,
    #       a.spotify_playlist_id,
    #	   a.spotify_playlist_name,
    #       b.spotify_song_id,
    #	   b.song_title,
    #	   b.song_album,
    #	   e.spotify_artist_name
    #from playlists a
    #     join playlist_song_join c on (a.spotify_playlist_id = c.spotify_playlist_id)
    #     join songs b on (c.spotify_song_id = b.spotify_song_id)
    #	 join artist_song_join d on (c.spotify_song_id = d.spotify_song_id)
    #	 join artists e on (d.spotify_artist_id = e.spotify_artist_id) 

# Regrant permissions to database user using the following grant command

    #grant all privileges on all tables in schema public to playspotplay

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