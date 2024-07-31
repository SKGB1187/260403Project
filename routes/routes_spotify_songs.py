from routes_decorators import check_token_expiry, login_required, spotify_link_required

from flask import Blueprint
from flask import request
from flask import flash, render_template

from forms import AddSongForm

from utils import get_user_playlists, populate_user_playlists
from utils import add_song_to_spotify_playlist, get_spotify_song

songs_spotify = Blueprint('songs_spotify', __name__)

@songs_spotify.route('/song_search', methods=['GET', 'POST'])
@login_required
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

    if isinstance(playlists, list) and all(isinstance(p, dict) for p in playlists):
        form.playlist_id.choices = [(playlist['id'], playlist['name']) for playlist in playlists]
    else:
        form.playlist_id.choices = []

    return render_template('User/song_search_return.html', form=form, song=song, playlists=playlists)

@songs_spotify.route('/add_to_playlist', methods=['POST'])
@login_required
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
            else:
                flash('Sorry, failed to add song to playlist, please try again.', 'error')
        else:
            flash('The Song is or playlist id is missing, please try again.', 'error')

    except Exception as e:
        flash('Sorry, an unknown error occurred, please try again.', 'error')