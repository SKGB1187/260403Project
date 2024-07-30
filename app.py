import os
import requests

from decorators import check_token_expiry, login_required, spotify_link_required

from flask import current_app, g, request, session
from flask import flash, render_template, send_from_directory

from forms import AddSongForm, AddUserForm, CreatePlaylistForm, LoginForm

from models import db
from models import User, UserPlayListDisplay
from models import DBActionResult

from auth_spotify import auth as auth_blueprint

from sqlalchemy.exc import IntegrityError

from utils import get_user_playlists, populate_user_playlists
from utils import add_song_to_spotify_playlist, get_spotify_song
from utils import get_spotify_profile

#app = Flask(__name__)

#app.secret_key = os.urandom(32)

#app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('playspotplay_connection', 'postgresql:///playspotplay')
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#app.config['SQLALCHEMY_ECHO'] = False
#app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
#app.config['SESSION_TYPE'] = 'sqlalchemy'
#app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
#app.config.update(
#    SESSION_COOKIE_SECURE=True,
#    SESSION_COOKIE_HTTPONLY=True,
#    SESSION_COOKIE_SAMESITE='Lax'
#)

#csrf = CSRFProtect(app)

#db.app = app
#db.init_app(app)

#with app.app_context():
#    db.create_all()  

#app.register_blueprint(auth_blueprint, url_prefix='/auth')

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
@login_required
@spotify_link_required
def index():
    """ Defines the different templates to be used for a logged in user verses an unknown visitor """

    return render_template('User/home_logged_in.html')
    
### Sign up, Login and Logout ###

@app.route('/sign_up', methods=["GET", "POST"])
def signup():
    """ Route for signing up a new user, add them to the database and do an initial link to Spotify API for user """
    form = AddUserForm()
    valid_form = form.validate_on_submit()

    if valid_form:

        user_result: DBActionResult[User] = User.signup(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data,
        )

        if (user_result.is_success):
            user = user_result.value 
            
            session[CURR_USER_KEY] = user.id
            session['_csrf_token'] = user.csrf_token
            flash("Account creation successful!", 'success')
            return render_template('redirects/redirect_to_auth_link_spotify.html')
        
        else:
            flash(user_result.message, "error")

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
@login_required
@spotify_link_required
def profile_view_change():
    """ Route for viewing profile information for the linked Spotify Account of a user, also button to re-link Spotify """

    if g.user.spotify_user_id:
        profile = {
            'id': g.user.spotify_user_id,
            'display_name': g.user.spotify_user_display_name,
            'email': g.user.spotify_acct_email
        }
    else:
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

@app.route('/playlists', methods=['GET'])
@login_required
@spotify_link_required
def retrieve_playlists():
    """ Route to retrieve user's Spotify playlists """
    playlists = get_user_playlists()

    if playlists is not None:
        return render_template('Playlists/show_user_playlists.html', playlists=playlists)
    else:
        print('playlists is returning none for retrieve_playlists')
        print('redirecting to error.html for retrieve_playlists')
        flash('Unexpected error retrieving playlists, please try again.', 'error')
        return render_template('errors/retrieve_playlists_error.html', message="Could not retrieve playlists")

@app.route('/create_playlist', methods=['GET', 'POST'])
@login_required
@spotify_link_required
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

@app.route("/playlist/<playlist_id>")
@login_required
@spotify_link_required
def view_specific_playlist(playlist_id):
    """ Route to retrieve an indivual playlist's content """

    playlist_content = UserPlayListDisplay.query.filter_by(spotify_playlist_id=playlist_id, user_id=g.user.id).all()
    if playlist_content:
        return render_template('Playlists/singular_user_playlist.html', playlist_content=playlist_content)
    else:
        flash('Sorry, could not find playlist, please try again', 'error')
        return "Playlist not found", 404





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

