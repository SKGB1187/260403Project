import os
import base64
import hashlib
import asyncio
import requests
from datetime import datetime

from urllib.parse import urlencode
from flask import Blueprint, session, redirect, request, render_template, g
from models import db, User

auth = Blueprint('auth', __name__)

def generate_random_string(length):
    possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    values = os.urandom(length)
    return ''.join(possible[b % len(possible)] for b in values)

async def sha256(random_string):
    return hashlib.sha256(random_string.encode()).digest()

def base64encode(hashed_input):
    return base64.urlsafe_b64encode(hashed_input).rstrip(b'=').decode('ascii')

client_id = os.environ.get('spotify_client_id','')
redirect_uri = 'http://localhost:5000/auth/redirect_to_playspotplay'
scope = 'playlist-modify-private playlist-modify-public playlist-read-private user-library-modify user-library-read user-read-private user-read-email'
auth_url = 'https://accounts.spotify.com/authorize'

@auth.route('/link_spotify')
def login():
    """ Route for linking the spotify API to the application """
    code_verifier = generate_random_string(64)
    session['code_verifier'] = code_verifier
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    code_challenge = loop.run_until_complete(sha256(code_verifier))
    code_challenge = base64encode(code_challenge)
    
    params = {
        'response_type': 'code',
        'client_id': client_id,
        'scope': scope,
        'code_challenge_method': 'S256',
        'code_challenge': code_challenge,
        'redirect_uri': redirect_uri,
    }
    
    auth_url_with_params = f"{auth_url}?{urlencode(params)}"
    session.modifed = True
    return redirect(auth_url_with_params)

@auth.route('/redirect_to_playspotplay')
async def callback():
    """ Callback function for redirct from Spotify authorization linkage back to the application """
    code = request.args.get('code')
    code_verifier = session.get('code_verifier')

    if code and code_verifier:
        token_response = get_token(code, code_verifier)
        now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        if g.user:
            User.link_spotify_to_database(
                        g.user.id,
                        token_response['access_token'],
                        now,
                        token_response['refresh_token'])

        return render_template('redirects/redirect_to_home.html')
    else:
        return 'Error: Authorization failed'

def run_refresh_token():
    """ Function to refresh the access token for the Spotify API """
    if g.user:
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

    return False

def get_token(code, code_verifier):
    """ Function to initially get an access token from the Spotify API """
    redirect_uri = 'http://localhost:5000/auth/redirect_to_playspotplay'

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
