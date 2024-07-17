import os
import base64
import hashlib
import aiohttp
import asyncio
from datetime import datetime

from urllib.parse import urlencode
from flask import Blueprint, session, redirect, request, render_template

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

client_id = 'd3bf0a271cf7472c90b736a912177481'
redirect_uri = 'http://localhost:5000/auth/redirect_to_playspotplay'
scope = 'playlist-modify-private playlist-modify-public playlist-read-private user-library-modify user-library-read user-read-private user-read-email'
auth_url = 'https://accounts.spotify.com/authorize'

@auth.route('/link_spotify')
def login():
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
    code = request.args.get('code')
    #print("code is: " + code)
    code_verifier = session.get('code_verifier')
    #print("code_verifier is:" + code_verifier)

    if code and code_verifier:
        token_response = await get_token(code, code_verifier)
        #print("Token reponse is:")
        #print(token_response)
        session['tokens'] = token_response
        #print('Session[tokens] is:')
        #print(session['tokens'])
        now = datetime.now()
        session['token_set_time'] = now.strftime("%d/%m/%Y %H:%M:%S")
        #print("Session[token_set_time] is set to: ")
        #print(session['token_set_time'])
        session.modified = True
        return render_template('redirects/redirect_to_home.html')
    else:
        return 'Error: Authorization failed'

async def refresh_token():
    tokens = session.get('tokens')
    if not tokens:
        return render_template('redirects/redirect_to_auth_link_spotify.html')

    refresh_token = session.get('refresh_token')
    if not refresh_token:
        return render_template('redirects/redirect_to_auth_link_spotify.html')

    new_access_token = await get_refresh_token(refresh_token)
    tokens['access_token'] = new_access_token
    session['tokens'] = tokens
    now = datetime.now()
    session['token_set_time'] = now.strftime("%d/%m/%Y %H:%M:%S")
    session.modified = True

async def get_token(code, code_verifier):
    client_id = 'd3bf0a271cf7472c90b736a912177481'
    redirect_uri = 'http://localhost:5000/auth/redirect_to_playspotplay'

    payload = {
        'client_id': client_id,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': redirect_uri,
        'code_verifier': code_verifier,
    }

    async with aiohttp.ClientSession() as session:
        async with session.post('https://accounts.spotify.com/api/token', data=payload) as response:
            token_response = await response.json()
            return token_response


async def get_refresh_token(refresh_token):
    client_id = 'd3bf0a271cf7472c90b736a912177481'

    payload = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': client_id,
    }

    async with aiohttp.ClientSession() as session:
        async with session.post('https://accounts.spotify.com/api/token', data=payload) as response:
            token_response = await response.json()
            return token_response['access_token']
        
