from flask import Blueprint
from flask import g
from flask import flash, render_template

from forms import CreatePlaylistForm

from models import UserPlayListDisplay

from routes_decorators import check_token_expiry, login_required, spotify_link_required

from utils import create_spotify_playlist, get_user_playlists, add_user_playlist_to_db

playlists_spotify = Blueprint('playlists_spotify', __name__)

@playlists_spotify.route('/playlists', methods=['GET'])
@login_required
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
@spotify_link_required
@check_token_expiry
def view_specific_playlist(playlist_id):
    """ Route to retrieve an indivual playlist's content """

    playlist_content = UserPlayListDisplay.query.filter_by(spotify_playlist_id=playlist_id, user_id=g.user.id).all()
    if playlist_content:
        return render_template('Playlists/singular_user_playlist.html', playlist_content=playlist_content)
    else:
        flash('Sorry, could not find playlist, please try again', 'error')
        return "Playlist not found", 404
