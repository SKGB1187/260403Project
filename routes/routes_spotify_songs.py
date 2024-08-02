from flask import Blueprint
from flask import current_app, g, request, session
from flask import flash, render_template

from ..forms import AddSongForm

from ..models import db
from ..models import User

from .routes_decorators import check_token_expiry, login_required, spotify_link_required, spotify_allowlist_required

from ..utils import CURR_USER_KEY
from ..utils import add_song_to_spotify_playlist, add_user_playlist_to_db, add_user_tracks_to_db, get_spotify_song, get_user_playlists, populate_user_playlists

songs_spotify = Blueprint('songs_spotify', __name__)

@songs_spotify.before_request
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

@songs_spotify.before_request
def load_csrf_token():
    """"Load CSRF token stored in database into the session for the user"""
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user:
            session['_csrf_token'] = user.csrf_token

@songs_spotify.context_processor
def inject_csrf_token():
    """This function is used to pass the CSRF token to the rendering context, making it available in templates."""
    return dict(csrf_token=session.get('_csrf_token'))

@songs_spotify.route('/song_search', methods=['GET', 'POST'])
@login_required
@spotify_allowlist_required
@spotify_link_required
@check_token_expiry
def song_search():
    form = AddSongForm()
    
    if request.method == 'POST':
        song_id = form.song_id.data
        playlist_id = form.playlist_id.data
        response = add_song_to_spotify_playlist(song_id, playlist_id)
        populate_user_playlists(playlist_id)
        if response.status_code == 201:
            flash('Song added to playlist successfully!', 'success')
        else:
            flash('Sorry, could not add song to playlist, please try again', 'error')
            return render_template('redirects/redirect_to_home.html')
        return render_template('redirects/redirect_to_user_playlists.html', id = playlist_id)

    song_name = request.args.get('q')
    song = get_spotify_song(song_name)
    playlists = get_user_playlists()
    add_user_playlist_to_db(playlists)

    if isinstance(playlists, list) and all(isinstance(p, dict) for p in playlists):
        form.playlist_id.choices = [(playlist['id'], playlist['name']) for playlist in playlists]
    else:
        form.playlist_id.choices = []

    return render_template('User/song_search_return.html', form=form, song=song, playlists=playlists)

@songs_spotify.route('/add_to_playlist', methods=['POST'])
@login_required
@spotify_allowlist_required
@spotify_link_required
@check_token_expiry
def add_to_playlist():
    """Route to add a song to a playlist using the Spotify API"""

    try:
        song_id = request.form.get('song_id')
        playlist_id = request.form.get('playlist_id')

        if song_id and playlist_id:
            response = add_song_to_spotify_playlist(song_id, playlist_id)
            if response.status_code == 201:
                flash('Song added to playlist successfully!', 'success')
                tracks = populate_user_playlists(playlist_id)
                add_user_tracks_to_db(tracks, playlist_id)
                
                return render_template('redirects/redirect_to_user_playlists.html', id = playlist_id) 
            else:
                flash('Sorry, failed to add song to playlist, please try again.', 'error')
        else:
            flash('The Song is or playlist id is missing, please try again.', 'error')

    except Exception as e:
        flash('Sorry, an unknown error occurred, please try again.', 'error')