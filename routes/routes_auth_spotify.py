from datetime import datetime

from flask import Blueprint
from flask import g, request, session, flash
from flask import render_template, redirect  

from ..models import User, DBActionResult

from urllib.parse import urlencode

from ..utils import auth_url, client_id, redirect_uri, scope, CURR_USER_KEY
from ..utils import base64encode, generate_random_string, get_token, sha256, get_spotify_profile

auth = Blueprint('auth', __name__)

@auth.context_processor
def inject_csrf_token():
    """This function is used to pass the CSRF token to the rendering context, making it available in templates."""
    return dict(csrf_token=session.get('_csrf_token'))

@auth.route('/link_spotify')
def login():
    """ Route for linking the spotify API to the application """
    code_verifier = generate_random_string(64)
    session['code_verifier'] = code_verifier
    code_challenge = sha256(code_verifier)
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
def callback():
    """ Callback function for redirct from Spotify authorization linkage back to the application """
    code = request.args.get('code')
    code_verifier = session.get('code_verifier')

    if code and code_verifier:
        token_response = get_token(code, code_verifier)
        now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        if session[CURR_USER_KEY]:
            res = User.link_spotify_to_database(
                        session[CURR_USER_KEY],
                        token_response['access_token'],
                        now,
                        token_response['refresh_token'])
            
            g.user = res
            
            profile_data_res = get_spotify_profile()

            if not profile_data_res.is_success:
                if g.user:
                    g.pop("user")

                session.clear()
                flash(profile_data_res.message)
                return render_template('index.html')

            profile_data = profile_data_res.value
            linked_spotify_id = profile_data['id']
            user_spotify_id = User.query.filter(User.spotify_user_id == linked_spotify_id).first()

            if user_spotify_id:
                User.link_spotify_to_database(
                        session[CURR_USER_KEY],
                        None,
                        None,
                        None)

                if g.user:
                    g.pop("user")

                session.clear()
                flash('Sorry you can only link a Spotify account to one user account, please link a different Spotify Account')
                return render_template('index.html')
            
            else:
                User.profile_spotify(
                    session[CURR_USER_KEY],
                    spotify_user_id=profile_data['id'],
                    spotify_user_display_name=profile_data['display_name'],
                    spotify_acct_email=profile_data['email']
                )

        return render_template('redirects/redirect_to_home.html')
    else:
        return 'Error: Authorization failed'