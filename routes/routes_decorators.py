from datetime import datetime, timedelta

from flask import g, session
from flask import render_template

from functools import wraps

from ..utils import run_refresh_token, CURR_USER_KEY

def login_required(f):
    @wraps(f)
    def ensure_login(*args, **kwargs):
        if not g.user:
            return render_template('redirects/redirect_to_login.html')
        return f(*args, **kwargs)
    return ensure_login

def spotify_link_required(f):
    @wraps(f)
    def ensure_spotify_link(*args, **kwargs):
        if not g.user.spotify_access_token:
            return render_template('redirects/redirect_to_auth_link_spotify.html')
        return f(*args, **kwargs)
    return ensure_spotify_link

def spotify_allowlist_required(f):
    @wraps(f)
    def allowlist_required(*args, **kwargs):
        if not g.user.spotify_user_id:
            return render_template('redirects/redirect_to_auth_link_spotify.html')
        return f(*args, **kwargs)
    return allowlist_required

def check_token_expiry(f):
    @wraps(f)
    def ensure_valid_token(*args, **kwargs):
        if g.user:
            token_time = datetime.strptime(g.user.spotify_access_token_set_time, "%d/%m/%Y %H:%M:%S")
            expiration_time = token_time + timedelta(minutes=55)
            now = datetime.now()
            
            if now > expiration_time:
                run_refresh_token()
        return f(*args, **kwargs)
    return ensure_valid_token