import os

from flask import Blueprint
from flask import current_app, g, session
from flask import flash, render_template, send_from_directory

from ..forms import AddUserForm, LoginForm

from ..models import db
from ..models import User, DBActionResult

from ..utils import CURR_USER_KEY

main = Blueprint('main', __name__)

@main.before_request
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

@main.before_request
def load_csrf_token():
    """"Load CSRF token stored in database into the session for the user"""
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user:
            session['_csrf_token'] = user.csrf_token

@main.context_processor
def inject_csrf_token():
    """This function is used to pass the CSRF token to the rendering context, making it available in templates."""
    return dict(csrf_token=session.get('_csrf_token'))

@main.route('/favicon.ico', methods=["GET"])
def favicon():
    """ Used to generate the favicon route for displaying the application icon on the website tab """
    return send_from_directory(os.path.join(main.root_path, 'static'),
                               'favicon_static.ico', mimetype='favicon.ico')

@main.route("/")
def index():
    """ Defines the different templates to be used for a logged in user verses an unknown visitor """
    if g.user:
        return render_template('User/home_logged_in.html')
    return render_template('index.html')

@main.route('/sign_up', methods=["GET", "POST"])
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

@main.route('/login', methods=["GET", "POST"])
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

@main.route('/logout')
def logout():
    """ Route to logout a user """
    if g.user:
        g.pop("user")

    session.clear()
    flash('Logout successful, see you again soon!', 'success')

    return render_template('index.html')
