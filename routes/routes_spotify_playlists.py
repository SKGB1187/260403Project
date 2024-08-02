from flask import Blueprint
from flask import current_app, g, session
from flask import flash, render_template

from ..forms import CreatePlaylistForm

from ..models import db
from ..models import UserPlayListDisplay, User

from .routes_decorators import check_token_expiry, login_required, spotify_link_required, spotify_allowlist_required

from ..utils import CURR_USER_KEY
from ..utils import add_user_tracks_to_db, create_spotify_playlist, get_user_playlists, add_user_playlist_to_db, populate_user_playlists

playlists_spotify = Blueprint('playlists_spotify', __name__)

@playlists_spotify.before_request
def add_user_to_g():
    """ Run before a request to check that the logged in user is added to the session and to pull user_id and CSRF_token from database """
    try:
        if CURR_USER_KEY in session:
            user_id = session[CURR_USER_KEY]
            g.user = db.session.get(User, user_id)
            session['_csrf_token'] = g.user.csrf_token
        else:
            g.user = None
    except Exception as e:
        current_app.logger.error(f"Error in add_user_to_g: {e}")
        g.user = None

@playlists_spotify.before_request
def load_csrf_token():
    """"Load CSRF token stored in database into the session for the user"""
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user:
            session['_csrf_token'] = user.csrf_token

@playlists_spotify.context_processor
def inject_csrf_token():
    """This function is used to pass the CSRF token to the rendering context, making it available in templates."""
    return dict(csrf_token=session.get('_csrf_token'))

@playlists_spotify.route('/playlists', methods=['GET'])
@login_required
@spotify_allowlist_required
@spotify_link_required
@check_token_expiry
def retrieve_playlists():
    """ Route to retrieve user's Spotify playlists """
    playlists = get_user_playlists()

    if playlists is not None:
        add_user_playlist_to_db(playlists)
        return render_template('Playlists/show_user_playlists.html', playlists=playlists)
    else:
        return render_template('errors/retrieve_playlists_error.html', message="Could not retrieve playlists")

@playlists_spotify.route('/create_playlist', methods=['GET', 'POST'])
@login_required
@spotify_allowlist_required
@spotify_link_required
@check_token_expiry
def create_new_spotify_playlist():
    """ Route to create a new Spotify playlist through the Spotify API """
    form = CreatePlaylistForm()
    valid_form = form.validate_on_submit()

    if valid_form:
            
            playlist_name = form.playlist_name.data
            description = form.playlist_description.data
            
            create_spotify_playlist(playlist_name, description)
    
    return render_template('Playlists/create_playlist_form.html', form=form)

@playlists_spotify.route("/playlist/<playlist_id>")
@login_required
@spotify_allowlist_required
@spotify_link_required
@check_token_expiry
def view_specific_playlist(playlist_id):
    """ Route to retrieve an indivual playlist's content """
    tracks = populate_user_playlists(playlist_id)
    add_user_tracks_to_db(tracks, playlist_id)

    playlist_content = UserPlayListDisplay.query.filter_by(spotify_playlist_id=playlist_id, user_id=g.user.id).all()
    if playlist_content:
        return render_template('Playlists/singular_user_playlist.html', playlist_content=playlist_content)
    else:
        flash('Sorry, could not find playlist, please try again', 'error')
        return render_template('redirects/redirect_to_home.html')
