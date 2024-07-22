#Spotify Client ID: d3bf0a271cf7472c90b736a912177481
#Spotify Client Secret: 6c8d7a98aa634391955c3cc7c538b38c

#API calls Base URL: https://api.spotify.com

#scopes needed?: playlist-modify-private playlist-modify-public playlist-read-private user-library-modify user-library-read
#scopes: https://developer.spotify.com/documentation/web-api/concepts/scopes

import os
import requests

from datetime import datetime, timedelta

from flask import Flask, render_template, flash, request, session, g, current_app, send_from_directory
from flask_wtf.csrf import CSRFProtect

from forms import LoginForm, AddUserForm, CreatePlaylistForm

from models import db, User, Song, Playlist

from spotify_auth import auth as auth_blueprint, refresh_token

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
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user:
            session['_csrf_token'] = user.csrf_token

@app.context_processor
def inject_csrf_token():
    return dict(csrf_token=session.get('_csrf_token'))

@app.route('/favicon.ico', methods=["GET"])
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon_static.ico', mimetype='favicon.ico')

@app.route("/")
def index():
    if not g.user:
        return render_template('index.html')
    else:
        return render_template('user/home_logged_in.html')


@app.route('/sign_up', methods=["GET", "POST"])
def signup():
    print("start of signup")
    form = AddUserForm()

    if form.validate_on_submit():
        print("validating form")
        try:
            print("signing up user")
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
            print("user added correctly, redirecting to spotify")
            return render_template('redirects/redirect_to_auth_link_spotify.html')
        
        except IntegrityError:
            print("user already exists")
            db.session.rollback()
            flash("Username already taken", 'danger')
        
        except Exception as e:
            print("other exception")
            print(str(e))
            db.session.rollback()
            flash(str(e), 'danger')
    
    print("rendering signup form")

    return render_template('user/sign_up.html', form=form)

@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data, form.password.data)

        if user:
            session[CURR_USER_KEY] = user.id
            return render_template('redirects/redirect_to_home.html')

    return render_template('user/login_form.html', form=form)

@app.route('/logout')
def logout():
    if g.user:
        g.pop("user")

    session.clear()

    return render_template('index.html')

@app.route('/update_profile')
def profile_view_change():
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
        return render_template('user/spotify_profile.html', profile=profile)
    return render_template('redirects/redirect_to_login.html')

def get_spotify_profile():
    if g.user:
        bearer = g.user.spotify_access_token
        profile_request = requests.get("https://api.spotify.com/v1/me", headers={"Authorization": "Bearer " + bearer})
        response = profile_request.json()
        
        return response
    return 'No tokens found.'

@app.route('/create_playlist', methods=['GET', 'POST'])
def create_new_spotify_playlist():
    form = CreatePlaylistForm()
    
    if form.validate_on_submit():
        print("validating form")
        try:
            if g.user:
                bearer = g.user.spotify_access_token
                user_id = g.user.spotify_user_id
                playlist_name = form.playlist_name.data
                description = form.description.data
                public_or_private = form.public_or_private.data
                
                payload = {
                    "name": playlist_name,
                    "description": description,
                    "public": public_or_private
                }
                
                headers = {
                    "Authorization": "Bearer " + bearer,
                    "Content-Type": "application/json"
                }
                
                response = requests.post(f"https://api.spotify.com/v1/users/{user_id}/playlists", headers=headers, json=payload)
                
                if response.status_code == 201:
                    return render_template('redirects/redirect_to_user_playlists.html')

        except Exception as e:
            print("other exception")
            print(str(e))
            db.session.rollback()
            flash(str(e), 'danger')
    
    return render_template('create_playlist.html', form=form)
 
@app.route('/song_search')
def song_search():
    if g.user:
        check_token_expiry()
        
        song_name = request.args.get('q')
        song = get_spotify_song(song_name)

        playlists = get_user_playlists()
        
        return render_template('user/song_search_return.html', song=song, playlists=playlists)
    
    return render_template('redirects/redirect_to_login.html')

@app.route("/playlist/<playlist_id>")
def view_specific_playlist(playlist_id):
    if g.user:
        playlist = Playlist.query.filter_by(spotify_playlist_id=playlist_id, user_id=g.user.id).first()
        if playlist:
            return render_template('view_playlist.html', playlist=playlist)
        else:
            return "Playlist not found", 404
    else:
        return render_template('redirects/redirect_to_login.html')


def get_user_playlists():
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
                # Extract playlist details
                playlist_id = playlist['id']
                playlist_name = playlist['name']
                playlist_description = playlist.get('description', '')

                # Check if the playlist already exists in the database
                existing_playlist = Playlist.query.filter_by(spotify_playlist_id=playlist_id).first()
                if not existing_playlist:
                    # Create a new Playlist object
                    new_playlist = Playlist(
                        spotify_playlist_id=playlist_id,
                        spotify_playlist_name=playlist_name,
                        spotify_playlist_description=playlist_description,
                        user_id=g.user.id
                    )

                    # Add to the session
                    db.session.add(new_playlist)

                # Save songs and artists from the playlist
                tracks_url = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'
                tracks_response = requests.get(tracks_url, headers=headers)
                if tracks_response.status_code == 200:
                    tracks = tracks_response.json().get('items', [])
                    for track in tracks:
                        track_info = track['track']
                        song_id = track_info['id']
                        song_title = track_info['name']
                        song_album = track_info['album']['name']
                        song_artists = track_info['artists']

                        # Check if the song already exists in the database
                        existing_song = Song.query.filter_by(spotify_song_id=song_id).first()
                        if not existing_song:
                            # Create a new Song object
                            new_song = Song(
                                spotify_song_id=song_id,
                                song_title=song_title,
                                song_artist=', '.join([artist['name'] for artist in song_artists]),
                                song_album=song_album
                            )

                            # Add to the session
                            db.session.add(new_song)

                        # Create a Playlist_Song association
                        playlist_song = Playlist_Song(
                            spotify_song_id=song_id,
                            spotify_playlist_id=playlist_id
                        )
                        db.session.add(playlist_song)

                        for artist in song_artists:
                            artist_id = artist['id']
                            artist_name = artist['name']

                            # Check if the artist already exists in the database
                            existing_artist = Artist.query.filter_by(spotify_artist_id=artist_id).first()
                            if not existing_artist:
                                # Create a new Artist object
                                new_artist = Artist(
                                    spotify_artist_id=artist_id,
                                    spotify_artist_name=artist_name
                                )

                                # Add to the session
                                db.session.add(new_artist)

                            # Create an Artist_Song association
                            artist_song = Artist_Song(
                                spotify_song_id=song_id,
                                spotify_artist_id=artist_id
                            )
                            db.session.add(artist_song)

            # Commit the session to save the playlists, songs, and artists
            db.session.commit()
            
            return playlists
        else:
            return []
    else:
        return []

def get_spotify_song(song_name):
    if g.user:
        bearer = g.user.spotify_access_token
        song_search_url = f'https://api.spotify.com/v1/search?q={song_name}&type=track&include_external=audio'
        song_search = requests.get(song_search_url, headers={"Authorization": "Bearer " + bearer})
        response = song_search.json()
        
        return response
    else:
        return 'No tokens found.'
    
@app.route('/add_to_playlist', methods=['POST'])
def add_to_playlist():
    if g.user:
        song_id = request.args.get('song_id')
        playlist_id = request.args.get('playlist_id')
        
        result = add_song_to_spotify_playlist(song_id, playlist_id)
        
        if result:
            return 'Song added to playlist successfully!', 200
        else:
            return 'Failed to add song to playlist.', 400
    return 'User not authenticated.', 401

def add_song_to_spotify_playlist(song_id, playlist_id):
    if g.user:
        bearer = g.user.spotify_access_token
        url = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'
        headers = {
            "Authorization": f"Bearer {bearer}",
            "Content-Type": "application/json"
        }
        data = {
            "uris": [f"spotify:track:{song_id}"]
        }

        response = requests.post(url, headers=headers, json=data)
        
        return response.status_code == 201
    else:
        return False

def check_token_expiry():
    if g.user:
        token_time = datetime.strptime(g.user.spotify_access_token_set_time, "%d/%m/%Y %H:%M:%S")
        expiration_time = token_time + timedelta(minutes=55)
        now = datetime.now()
        
        if now > expiration_time:
            refresh_token()
