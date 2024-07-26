#Spotify Client ID: d3bf0a271cf7472c90b736a912177481
#Spotify Client Secret: 6c8d7a98aa634391955c3cc7c538b38c

#API calls Base URL: https://api.spotify.com

#scopes needed?: playlist-modify-private playlist-modify-public playlist-read-private user-library-modify user-library-read
#scopes: https://developer.spotify.com/documentation/web-api/concepts/scopes
import logging
import os
import requests

from datetime import datetime, timedelta

from flask import Flask, render_template, flash, request, session, g, current_app, send_from_directory, jsonify
from flask_wtf.csrf import CSRFProtect

from forms import LoginForm, AddSongForm, AddUserForm, CreatePlaylistForm

from models import db, Artist, Artist_Song, Playlist, Playlist_Song, Song, User, UserPlayListDisplay

from spotify_auth import auth as auth_blueprint, run_refresh_token

from sqlalchemy.exc import IntegrityError

app = Flask(__name__)

app.secret_key = os.urandom(32)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('playspotplay_connection', 'postgresql:///playspotplay')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SESSION_TYPE'] = 'sqlalchemy'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax'
)

csrf = CSRFProtect(app)

db.app = app
db.init_app(app)

with app.app_context():
    db.create_all()  

app.register_blueprint(auth_blueprint, url_prefix='/auth')

CURR_USER_KEY = "curr_user_id"

@app.before_request
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

@app.before_request
def load_csrf_token():
    """"Load CSRF token stored in database into the session for the user"""
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user:
            session['_csrf_token'] = user.csrf_token

@app.context_processor
def inject_csrf_token():
    """This function is used to pass the CSRF token to the rendering context, making it available in templates."""
    return dict(csrf_token=session.get('_csrf_token'))

@app.route('/favicon.ico', methods=["GET"])
def favicon():
    """ Used to generate the favicon route for displaying the application icon on the website tab """
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon_static.ico', mimetype='favicon.ico')

@app.route("/")
def index():
    """ Defines the different templates to be used for a logged in user verses an unknown visitor """
    if not g.user:
        return render_template('index.html')
    else:
        if not g.user.spotify_access_token:
            flash('Sorry, but you have to link your Spotify Account to use this app.')
            return render_template('redirects/redirect_to_auth_link_spotify.html')
        return render_template('User/home_logged_in.html')
    
### Sign up, Login and Logout ###

@app.route('/sign_up', methods=["GET", "POST"])
def signup():
    """ Route for signing up a new user, add them to the database and do an initial link to Spotify API for user """
    form = AddUserForm()
    valid_form = form.validate_on_submit()

    if valid_form:
        try:
            user = User.signup(
                username=form.username.data,
                email=form.email.data,
                password=form.password.data,
            )
            
            print(user)
            db.session.add(user)
            db.session.commit()

            session[CURR_USER_KEY] = user.id
            session['_csrf_token'] = user.csrf_token
            flash("Account creation successful!", 'success')
            return render_template('redirects/redirect_to_auth_link_spotify.html')
        
        except IntegrityError:
            print("user already exists")
            db.session.rollback()
            flash('Sorry that username is already taken, please pick another', 'error')
        
        except Exception as e:
            print("other exception")
            print(str(e))
            db.session.rollback()
            flash('Sorry, an error occurred during sign-up, please try again.', 'error')

    return render_template('User/sign_up.html', form=form)

@app.route('/login', methods=["GET", "POST"])
def login():
    """ Route to login an existing user """
    form = LoginForm()

    form_valid = form.validate_on_submit()

    if form_valid:
        user = User.authenticate(form.username.data, form.password.data)

        if user:
            session[CURR_USER_KEY] = user.id
            flash('Login successful!', 'success')
            return render_template('redirects/redirect_to_home.html')
        else:
            flash('Username or password invalid, please login again.', 'error')

    return render_template('User/login_form.html', form=form)

@app.route('/logout')
def logout():
    """ Route to logout a user """
    if g.user:
        g.pop("user")

    session.clear()
    flash('Logout successful, see you again soon!', 'success')

    return render_template('index.html')

### Spotify Profile Request/Route ###

@app.route('/update_profile')
def profile_view_change():
    """ Route for viewing profile information for the linked Spotify Account of a user, also button to re-link Spotify """
    if g.user:
        if g.user.spotify_user_id:
            profile = {
                'id': g.user.spotify_user_id,
                'display_name': g.user.spotify_user_display_name,
                'email': g.user.spotify_acct_email
            }
        else:
            check_token_expiry()
            profile_data = get_spotify_profile()
            profile = {
                'id': profile_data['id'],
                'display_name': profile_data['display_name'],
                'email': profile_data['email']
            }
            User.profile_spotify(
                g.user.id,
                spotify_user_id=profile['id'],
                spotify_user_display_name=profile['display_name'],
                spotify_acct_email=profile['email']
            )
        return render_template('User/spotify_profile.html', profile=profile)
    return render_template('redirects/redirect_to_login.html')

def get_spotify_profile():
    """ Support function for /update_profile route, makes get request from Spotify API """
    if g.user:
        bearer = g.user.spotify_access_token
        profile_request = requests.get("https://api.spotify.com/v1/me", headers={"Authorization": "Bearer " + bearer})
        response = profile_request.json()
        
        return response
    return 'No tokens found.'

### Playlist retrieval, populate and create ###

@app.route('/playlists', methods=['GET'])
def retrieve_playlists():
    """ Route to retrieve user's Spotify playlists """
    if g.user:
        check_token_expiry()

        playlists = get_user_playlists()

        if playlists is not None:
            return render_template('Playlists/show_user_playlists.html', playlists=playlists)
        else:
            print('playlists is returning none for retrieve_playlists')
            print('redirecting to error.html for retrieve_playlists')
            flash('Unexpected error retrieving playlists, please try again.', 'error')
            return render_template('errors/retrieve_playlists_error.html', message="Could not retrieve playlists")
    
    return render_template('redirects/redirect_to_login.html')

@app.route('/create_playlist', methods=['GET', 'POST'])
def create_new_spotify_playlist():
    """ Route to create a new Spotify playlist through the Spotify API """
    form = CreatePlaylistForm()
    
    if form.validate_on_submit():
        print("validating form")
        try:
            if g.user:
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

@app.route("/playlist/<playlist_id>")
def view_specific_playlist(playlist_id):
    """ Route to retrieve an indivual playlist's content """
    if g.user:
        playlist_content = UserPlayListDisplay.query.filter_by(spotify_playlist_id=playlist_id, user_id=g.user.id).all()
        if playlist_content:
            return render_template('Playlists/singular_user_playlist.html', playlist_content=playlist_content)
        else:
            flash('Sorry, could not find playlist, please try again', 'error')
            return "Playlist not found", 404
    else:
        flash('Please log in to use the playlist functionality of the app.', 'error')
        return render_template('redirects/redirect_to_login.html')

def get_user_playlists():
    """ Function to call Spotify API and return user playlists """
    if g.user:
        bearer = g.user.spotify_access_token
        url = 'https://api.spotify.com/v1/me/playlists'
        headers = {
            "Authorization": f"Bearer {bearer}"
        }
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            playlists = response.json().get('items', [])

            for playlist in playlists:
                playlist_id = playlist['id']
                playlist_name = playlist['name']
                playlist_description = playlist.get('description', '')

                existing_playlist = Playlist.query.filter_by(spotify_playlist_id=playlist_id).first()

                if not existing_playlist:
                    new_playlist = Playlist(
                        spotify_playlist_id=playlist_id,
                        spotify_playlist_name=playlist_name,
                        spotify_playlist_description=playlist_description,
                        user_id=g.user.id
                    )

                    db.session.add(new_playlist)

            db.session.commit()

            return playlists
        else:
            return []
    else:
        flash('Sorry, failed to get your playlist from Spotify, please try again.', 'error')
        return render_template('redirects/redirect_to_login.html')

def populate_user_playlists(playlist_id):
    """ Function to populate user playlists with song data """
    if g.user:
        bearer = g.user.spotify_access_token
        url = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'
        headers = {
            "Authorization": f"Bearer {bearer}"
        }
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            tracks = response.json().get('items', [])
            for track in tracks:
                track_info = track['track']
                song_id = track_info['id']
                song_title = track_info['name']
                song_album = track_info['album']['name']
                song_artists = track_info['artists']

                existing_song = Song.query.filter_by(spotify_song_id=song_id).first()
                if not existing_song:
                    new_song = Song(
                        spotify_song_id=song_id,
                        song_title=song_title,
                        song_album=song_album
                    )
                    db.session.add(new_song)
                    db.session.commit()

                for artist in song_artists:
                    artist_id = artist['id']
                    artist_name = artist['name']

                    existing_artist = Artist.query.filter_by(spotify_artist_id=artist_id).first()
                    if not existing_artist:
                        new_artist = Artist(
                            spotify_artist_id=artist_id,
                            spotify_artist_name=artist_name
                        )
                        db.session.add(new_artist)
                        db.session.commit()

                playlist_song = Playlist_Song(
                    spotify_song_id=song_id,
                    spotify_playlist_id=playlist_id
                )
                db.session.add(playlist_song)
                db.session.commit()

                artist_song = Artist_Song(
                    spotify_song_id=song_id,
                    spotify_artist_id=artist_id
                )
                db.session.add(artist_song)
                db.session.commit()
        db.session.commit()
    else:
        flash('Please log in to use the playlist functionality of the app.', 'error')
        return render_template('redirects/redirect_to_login.html')

### Song retrieval and populate routes and functions ###

@app.route('/song_search', methods=['GET', 'POST'])
def song_search():
    form = AddSongForm()
    if request.method == 'POST':
        song_id = form.song_id.data
        playlist_id = form.playlist_id.data
        print(song_id, playlist_id)
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

@app.route('/add_to_playlist', methods=['POST'])
def add_to_playlist():
    """Route to add a song to a playlist using the Spotify API"""
    if g.user:
        check_token_expiry()
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

    else:
        flash('Please log in to use the add song to playlist functionality of the app.', 'error')
        return render_template('redirects/redirect_to_login.html')

    return render_template('redirects/redirect_to_home.html')

def get_spotify_song(song_name):
    """Function to make API call for searched song"""
    if g.user:
        bearer = g.user.spotify_access_token
        song_search_url = f'https://api.spotify.com/v1/search?q={song_name}&type=track&include_external=audio'
        song_search = requests.get(song_search_url, headers={"Authorization": "Bearer " + bearer})
        response = song_search.json()
        return response
    else:
        return 'No tokens found.'


def add_song_to_spotify_playlist(song_id, playlist_id):
    """Function to add a song to a Spotify playlist"""
    if g.user:
        bearer = g.user.spotify_access_token
        add_to_playlist_url = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'
        payload = {'uris': [f'spotify:track:{song_id}']}
        response = requests.post(add_to_playlist_url, headers={"Authorization": "Bearer " + bearer, "Content-Type": "application/json"}, json=payload)
        return response
    else:
        return 'No tokens found.'

### Oath 2 helper functions ###

def check_token_expiry():
    """ Function to check if access token is expired and needs to be refreshed """
    if g.user:
        token_time = datetime.strptime(g.user.spotify_access_token_set_time, "%d/%m/%Y %H:%M:%S")
        expiration_time = token_time + timedelta(minutes=55)
        now = datetime.now()
        
        if now > expiration_time:
            run_refresh_token()
