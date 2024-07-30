import requests

from flask import Blueprint
from flask import g
from flask import flash, render_template

from forms import CreatePlaylistForm

from models import db
from models import UserPlayListDisplay

from routes_decorators import check_token_expiry, login_required, spotify_link_required

from utils import get_user_playlists, populate_user_playlists

playlists_spotify = Blueprint('playlists_spotify', __name__)

@playlists_spotify.route('/playlists', methods=['GET'])
@login_required
@spotify_link_required
@check_token_expiry
def retrieve_playlists():
    """ Route to retrieve user's Spotify playlists """
    playlists = get_user_playlists()

    if playlists is not None:
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
    
    if form.validate_on_submit():
        try:

            bearer = g.user.spotify_access_token
            user_id = g.user.spotify_user_id
            playlist_name = form.playlist_name.data
            description = form.playlist_description.data
            
            payload = {
                "name": playlist_name,
                "description": description,
            }
            
            headers = {
                "Authorization": "Bearer " + bearer,
                "Content-Type": "application/json"
            }
            
            response = requests.post(f"https://api.spotify.com/v1/users/{user_id}/playlists", headers=headers, json=payload)
            
            if response.status_code == 201:
                flash('Playlist creation successful!', 'success')
                return render_template('redirects/redirect_to_user_playlists.html')
            else:
                flash('Sorry, failed to create playlist, please try again.', 'error')

        except Exception as e:
            print("other exception")
            print(str(e))
            db.session.rollback()
            flash(str(e), 'danger')
    
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
