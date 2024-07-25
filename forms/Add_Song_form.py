from flask_wtf import FlaskForm
from wtforms import HiddenField, SelectField
from wtforms.validators import DataRequired

class AddSongForm(FlaskForm):
    """Form for adding a song to a playlist."""

    song_id = HiddenField('Song ID', validators=[DataRequired()])
    playlist_id = SelectField('Playlist ID', coerce=str, validators=[DataRequired()])
