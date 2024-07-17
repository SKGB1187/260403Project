#Spotify Client ID: d3bf0a271cf7472c90b736a912177481
#Spotify Client Secret: 6c8d7a98aa634391955c3cc7c538b38c

#API calls Base URL: https://api.spotify.com

#scopes needed?: playlist-modify-private playlist-modify-public playlist-read-private user-library-modify user-library-read
#scopes: https://developer.spotify.com/documentation/web-api/concepts/scopes

import json
import os
import requests

from datetime import datetime, timedelta

from flask import Flask, render_template, flash, redirect, session, g, current_app, send_from_directory

from forms import LoginForm, AddUserForm

from models import db, User

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
        else:
            g.user = None
    except Exception as e:
        current_app.logger.error(f"Error in add_user_to_g: {e}")
        g.user = None

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
        print('user is:')
        print(user)
        if user:
            print('entered if user statement')
            session[CURR_USER_KEY] = user.id
            print('session should have session[CURR_USER_KEY] set')
            return render_template('redirects/redirect_to_home.html')

        flash("Invalid credentials.", 'danger')

    return render_template('user/login_form.html', form=form)

@app.route('/logout')
def logout():
    if g.user:
        g.pop("user")

    session.clear()

    flash("You have successfully logged out!", 'success')
    return render_template('index.html')

@app.route('/update_profile')
def profile_view_change():
    print('entered profile_view_change')
    if g.user:
        print('entered profile_view_change as g.user')
        check_token_expiry()
        print('check token ran')
        profile = get_spotify_profile()
        print('spotify profile retrieved successfully')
        return render_template('user/spotify_profile.html', profile = profile)
    return render_template('redirects/redirect_to_login.html')

def get_spotify_profile():
    tokens = session.get('tokens')
    print(str(tokens))
    if tokens:
        bearer = tokens['access_token']
        print(bearer)
        profile_request = requests.get("https://api.spotify.com/v1/me", headers = {"Authorization": "Bearer " + bearer})
        response = profile_request.json()
        return response
    else:
        return 'No tokens found.'

def check_token_expiry():
    view = session.get('token_set_time')
    print('view is:')
    print(view)
    token_time = datetime.strptime(view, "%d/%m/%Y %H:%M:%S")
    print('token_time is:')
    print(token_time)
    time_change = timedelta(minutes=55)
    print('time_change is:')
    print(time_change)
    expiration_time = token_time + time_change
    print('expiration_time is:')
    print(expiration_time)
    now = datetime.now()
    print('now time is:')
    print(now)
    if now > expiration_time:
        print('inside if statement for redirect to refresh token')
        return refresh_token()
    