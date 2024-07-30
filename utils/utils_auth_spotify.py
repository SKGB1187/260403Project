import os
import base64
import hashlib
import requests

from datetime import datetime

from flask import g
from flask import render_template

from models import db
from models import User

auth_url = 'https://accounts.spotify.com/authorize'
client_id = os.environ.get('spotify_client_id','d3bf0a271cf7472c90b736a912177481')
redirect_uri = 'http://localhost:5000/auth/redirect_to_playspotplay' 
# For Render
#client_id = os.environ.get('spotify_client_id','')
#redirect_uri = 'https://playspotplay.onrender.com/auth/redirect_to_playspotplay' 
scope = 'playlist-modify-private playlist-modify-public playlist-read-private user-library-modify user-library-read user-read-private user-read-email'

def generate_random_string(length):
    possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    values = os.urandom(length)
    return ''.join(possible[b % len(possible)] for b in values)

def sha256(random_string):
    return hashlib.sha256(random_string.encode()).digest()

def base64encode(hashed_input):
    return base64.urlsafe_b64encode(hashed_input).rstrip(b'=').decode('ascii')

def run_refresh_token():
    """ Function to refresh the access token for the Spotify API """

    refresh_token = g.user.spotify_refresh_token

    if not refresh_token:

        return render_template('redirects/redirect_to_auth_link_spotify.html')

    new_access_token = get_refresh_token(refresh_token)
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    User.link_spotify_to_database(
                    g.user.id,
                    new_access_token['access_token'],
                    now,
                    new_access_token['refresh_token'])

    db.session.commit()

    return True

def get_token(code, code_verifier):
    """ Function to initially get an access token from the Spotify API """
    
    payload = {
        'client_id': client_id,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': redirect_uri,
        'code_verifier': code_verifier,
    }

    token_response = requests.post("https://accounts.spotify.com/api/token", data = payload).json()

    return token_response 

def get_refresh_token(refresh_token):
    """ Function to initially get a refresh token from the Spotify API """
    
    payload = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': client_id,
    }

    new_access_token = requests.post("https://accounts.spotify.com/api/token", data = payload).json()

    return new_access_token   