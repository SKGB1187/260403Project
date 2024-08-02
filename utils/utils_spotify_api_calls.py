import requests
from requests import HTTPError

from flask import g
from flask import flash, render_template

from ..models import db, DBActionResult

def add_song_to_spotify_playlist(song_id, playlist_id):
    """Function to add a song to a Spotify playlist"""
    try:
        bearer = g.user.spotify_access_token
        add_to_playlist_url = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'
        payload = {'uris': [f'spotify:track:{song_id}']}
        response = requests.post(add_to_playlist_url, headers={"Authorization": "Bearer " + bearer, "Content-Type": "application/json"}, json=payload)
    
        if response.status_code == 200:
            return response
    
    except Exception as e:
        print("other exception")
        print(str(e))
        flash('Sorry, an error occurred calling Spotify API, please try again.')
    
def create_spotify_playlist(playlist_name, description):
    try:    
        bearer = g.user.spotify_access_token
        user_id = g.user.spotify_user_id
        payload = {
                    "name": playlist_name,
                    "description": description,
                }
        
        headers = {
            "Authorization": "Bearer " + bearer,
            "Content-Type": "application/json"
        }
        
        response = requests.post(f"https://api.spotify.com/v1/users/{user_id}/playlists", headers=headers, json=payload)
        
        if response.status_code == 201:
            flash('Playlist creation successful!', 'success')            
            return render_template('redirects/redirect_to_user_playlists.html')
        else:
            flash('Sorry, failed to create playlist, please try again.', 'error')
    
    except Exception as e:
        print("other exception")
        print(str(e))
        db.session.rollback()
        flash(str(e), 'danger')
   
def get_spotify_profile() -> DBActionResult[dict]:
    """ Support function for /update_profile route, makes get request from Spotify API """
    ret = DBActionResult({}, False, "default return")

    try:
        bearer = g.user.spotify_access_token
        profile_request = requests.get("https://api.spotify.com/v1/me", headers={"Authorization": "Bearer " + bearer})
        
        if profile_request.status_code == 403:
            ret.message = 'Sorry you are not added to the application allowlist, required by Spotify to utilize their API. Please contact the developer to be added.'
            
        else:
            response = profile_request.json()

            if response.status_code == 200:
                ret.value = response
                ret.message = ""
                ret.is_success = True

    except Exception as e:
        print("other exception")
        print(str(e))
        ret.message = 'Sorry, an error occurred calling Spotify API, please try again.'
    
    return ret

def get_spotify_song(song_name):
    """Function to make API call for searched song"""
    try:
        bearer = g.user.spotify_access_token
        song_search_url = f'https://api.spotify.com/v1/search?q={song_name}&type=track&include_external=audio'
        song_search = requests.get(song_search_url, headers={"Authorization": "Bearer " + bearer})
        response = song_search.json()

        if response.status_code == 200:
            return response

    except Exception as e:
            print("other exception")
            print(str(e))
            db.session.rollback()
            flash(str(e), 'danger')


def get_user_playlists():
    """Function to call Spotify API and return user playlists"""
    try:
        bearer = g.user.spotify_access_token
        url = 'https://api.spotify.com/v1/me/playlists'
        headers = {
            "Authorization": f"Bearer {bearer}"
        }
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json().get('items', {})
        else:
            print(f"Failed to fetch playlists: {response.status_code}")

    except Exception as e:
            print("other exception")
            print(str(e))
            db.session.rollback()
            flash(str(e), 'danger')

def populate_user_playlists(playlist_id):
    """ Function to populate user playlists with song data """
    try:
        bearer = g.user.spotify_access_token
        url = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'
        headers = {
            "Authorization": f"Bearer {bearer}"
        }
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            tracks = response.json().get('items', [])
            return tracks
        else:
             flash('API call for tracks failed')

    except Exception as e:
            print("other exception")
            print(str(e))
            db.session.rollback()
            flash(str(e), 'danger')