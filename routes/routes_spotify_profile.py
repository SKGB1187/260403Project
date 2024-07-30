from flask import Blueprint
from flask import g
from flask import flash, render_template

from models import User, DBActionResult

from routes_decorators import check_token_expiry, login_required, spotify_link_required

from utils import get_spotify_profile

profile = Blueprint('profile', __name__)

@profile.route('/update_profile')
@login_required
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
        if profile_data.id:
            profile = {
                'id': profile_data['id'],
                'display_name': profile_data['display_name'],
                'email': profile_data['email']
            }
            user_result: DBActionResult[User] = User.profile_spotify(
                g.user.id,
                spotify_user_id=profile['id'],
                spotify_user_display_name=profile['display_name'],
                spotify_acct_email=profile['email']
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