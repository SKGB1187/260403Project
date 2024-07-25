from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField
from wtforms.validators import DataRequired

class CreatePlaylistForm(FlaskForm):
    """Form for creating anew playlist for a user"""

    playlist_name = StringField('Playlist Name', validators=[DataRequired()])
    playlist_description = StringField('Playlist Description', validators=[DataRequired()])