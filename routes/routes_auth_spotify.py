import asyncio

from datetime import datetime

from flask import Blueprint
from flask import g, request, session
from flask import render_template, redirect  

from models import User

from urllib.parse import urlencode

from utils import auth_url, client_id, redirect_uri, scope
from utils import base64encode, generate_random_string, get_token, sha256

auth = Blueprint('auth', __name__)

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