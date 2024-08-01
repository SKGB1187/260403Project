from flask import g
from flask import flash

from ..models import db
from ..models import Artist, Artist_Song, Playlist, Playlist_Song, Song
    
def add_user_playlist_to_db(playlists):
    """Function to determine if playlist needs to be added to database"""
    for playlist in playlists:
        playlist_id = playlist['id']
        playlist_name = playlist['name']
        playlist_description = playlist.get('description', '')

        exists = Playlist.is_existing_playlist(playlist_id)
        if not exists:
            Playlist.add_user_playlist(
                spotify_playlist_id=playlist_id,
                spotify_playlist_name=playlist_name,
                spotify_playlist_description=playlist_description,
                user_id=g.user.id
            )

    return playlists 
            
def add_user_tracks_to_db(tracks, playlist_id):
    try:
        for track in tracks:
            track_info = track['track']
            song_id = track_info['id']
            song_title = track_info['name']
            song_album = track_info['album']['name']
            song_artists = track_info['artists']

            song_exists = Song.is_existing_song(song_id)
            if not song_exists:
                Song.add_playlist_songs(
                    spotify_song_id=song_id,
                    song_title=song_title,
                    song_album=song_album
                )

            for artist in song_artists:
                artist_id = artist['id']
                artist_name = artist['name']

                existing_artist = Artist.is_existing_artist(artist_id)
                if not existing_artist:
                    Artist.add_song_artist(
                        spotify_artist_id=artist_id,
                        spotify_artist_name=artist_name
                    )
            Playlist_Song.add_playlist_song_entry(playlist_id, song_id)

            Artist_Song.add_artist_song_entry(song_id, artist_id)

    except Exception as e:
            print("other exception")
            print(str(e))
            db.session.rollback()
            flash(str(e), 'danger')