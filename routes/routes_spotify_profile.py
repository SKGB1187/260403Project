from flask import Blueprint
from flask import current_app, g, session
from flask import flash, render_template

from ..models import db
from ..models import User, DBActionResult

from .routes_decorators import check_token_expiry, login_required, spotify_link_required, spotify_allowlist_required

from ..utils import CURR_USER_KEY
from ..utils import get_spotify_profile

profile = Blueprint('profile', __name__)

@profile.before_request
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

@profile.before_request
def load_csrf_token():
    """"Load CSRF token stored in database into the session for the user"""
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user:
            session['_csrf_token'] = user.csrf_token

@profile.context_processor
def inject_csrf_token():
    """This function is used to pass the CSRF token to the rendering context, making it available in templates."""
    return dict(csrf_token=session.get('_csrf_token'))

@profile.route('/update_profile')
@login_required
@spotify_allowlist_required
@spotify_link_required
@check_token_expiry
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
        print("profile data is")
        print(profile_data)
        if profile_data['id']:
            profile = {
                'id': profile_data['id'],
                'display_name': profile_data['display_name'],
                'email': profile_data['email']
            }
            user_result: DBActionResult[User] = User.profile_spotify(
                g.user.id,
                profile['id'],
                profile['display_name'],
                profile['email']
            )

            if (user_result.is_success):

                flash('Spotify profile pull successful')
                return render_template('User/spotify_profile.html', profile=profile)
            else:
                flash(user_result.message, "error")
        else:
            flash('Spotify API call has failed, please try again')
            return render_template('redirects/redirect_to_home.html')
    return render_template('User/spotify_profile.html', profile=profile)