import requests

from flask import g
from flask import flash

from models import db

def get_spotify_profile():
    """ Support function for /update_profile route, makes get request from Spotify API """
    try:
        bearer = g.user.spotify_access_token
        profile_request = requests.get("https://api.spotify.com/v1/me", headers={"Authorization": "Bearer " + bearer})
        response = profile_request.json()
        
        return response
    
    except Exception as e:
        print("other exception")
        print(str(e))
        flash('Sorry, an error occurred calling Spotify API, please try again.')
    
    return 'No tokens found.'