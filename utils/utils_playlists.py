import requests

from flask import g

from models import db
from models import Artist, Artist_Song, Playlist, Playlist_Song, Song, DBActionResult

from utils import add_user_playlist

def get_user_playlists():
    """Function to call Spotify API and return user playlists"""
    bearer = g.user.spotify_access_token
    url = 'https://api.spotify.com/v1/me/playlists'
    headers = {
        "Authorization": f"Bearer {bearer}"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        playlists = response.json().get('items', {})
    else:
        print(f"Failed to fetch playlists: {response.status_code}")
        return {}
    
def add_user_playlist_to_db():
    

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
    
    
def populate_user_playlists(playlist_id):
    """ Function to populate user playlists with song data """
    bearer = g.user.spotify_access_token
    url = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'
    headers = {
        "Authorization": f"Bearer {bearer}"
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        tracks = response.json().get('items', [])
        for track in tracks:
            track_info = track['track']
            song_id = track_info['id']
            song_title = track_info['name']
            song_album = track_info['album']['name']
            song_artists = track_info['artists']

            existing_song = Song.query.filter_by(spotify_song_id=song_id).first()
            if not existing_song:
                new_song = Song(
                    spotify_song_id=song_id,
                    song_title=song_title,
                    song_album=song_album
                )
                db.session.add(new_song)
                db.session.commit()

            for artist in song_artists:
                artist_id = artist['id']
                artist_name = artist['name']

                existing_artist = Artist.query.filter_by(spotify_artist_id=artist_id).first()
                if not existing_artist:
                    new_artist = Artist(
                        spotify_artist_id=artist_id,
                        spotify_artist_name=artist_name
                    )
                    db.session.add(new_artist)
                    db.session.commit()

            playlist_song = Playlist_Song(
                spotify_song_id=song_id,
                spotify_playlist_id=playlist_id
            )
            db.session.add(playlist_song)
            db.session.commit()

            artist_song = Artist_Song(
                spotify_song_id=song_id,
                spotify_artist_id=artist_id
            )
            db.session.add(artist_song)
            db.session.commit()
    db.session.commit()
