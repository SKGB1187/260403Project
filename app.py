#Spotify Client ID: d3bf0a271cf7472c90b736a912177481
#Spotify Client Secret: 6c8d7a98aa634391955c3cc7c538b38c

#API calls Base URL: https://api.spotify.com

#scopes needed?: playlist-modify-private playlist-modify-public playlist-read-private user-library-modify user-library-read
#scopes: https://developer.spotify.com/documentation/web-api/concepts/scopes

import os

from flask import Flask, render_template, request, flash, redirect, session, g, url_for, current_app
from flask_session import Session

from sqlalchemy.exc import IntegrityError
#from flask_sqlalchemy import SQLAlchemy

from models import db, User, Song, List

from forms import LoginForm, AddUserForm

from spotify_auth import auth as auth_blueprint



#db = SQLAlchemy()

    


#def create_app():
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('playspotplay_connection', 'postgresql:///playspotplay')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SESSION_TYPE'] = 'sqlalchemy'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True

db.app = app
db.init_app(app)

#server_session = Session(app)

with app.app_context():
    db.create_all()
    

app.register_blueprint(auth_blueprint, url_prefix='/auth')

#    return app

#app = create_app()

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

@app.route("/")
def index():
    if not g.user:
        return render_template('index.html')
    else:
        return render_template('home_logged_in.html')

@app.route('/sign_up', methods=["GET", "POST"])
def signup():
    form = AddUserForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                email=form.email.data,
                password=form.password.data,
            )
            db.session.commit()

            session[CURR_USER_KEY] = user.id
            return redirect("/")

        except IntegrityError:
            db.session.rollback()
            flash("Username already taken", 'danger')
            return render_template('user/sign_up.html', form=form)
    else:
        return render_template('user/sign_up.html', form=form)

@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data, form.password.data)

        if user:
            session[CURR_USER_KEY] = user.id
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('users/home_logged_in.html', form=form)

@app.route('/logout')
def logout():
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

    flash("You have successfully logged out!", 'success')
    return render_template('index.html')