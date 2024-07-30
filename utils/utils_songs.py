import requests

from flask import g

def get_spotify_song(song_name):
    """Function to make API call for searched song"""
    if g.user:
        bearer = g.user.spotify_access_token
        song_search_url = f'https://api.spotify.com/v1/search?q={song_name}&type=track&include_external=audio'
        song_search = requests.get(song_search_url, headers={"Authorization": "Bearer " + bearer})
        response = song_search.json()
        return response
    else:
        return 'No tokens found.'


def add_song_to_spotify_playlist(song_id, playlist_id):
    """Function to add a song to a Spotify playlist"""
    if g.user:
        bearer = g.user.spotify_access_token
        add_to_playlist_url = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'
        payload = {'uris': [f'spotify:track:{song_id}']}
        response = requests.post(add_to_playlist_url, headers={"Authorization": "Bearer " + bearer, "Content-Type": "application/json"}, json=payload)
        return response
    else:
        return 'No tokens found.'