from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Email, Length

class AddUserForm(FlaskForm):
    """Form for adding users."""

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])

# user_test_1
# User_test@email.com
# user_test_1_password

# user_test_2
# User_test_2@email.com
# user_test_2_password

# user_test_3
# User_test_3@email.com
# user_test_3_password

# user_test_4
# User_test_4@email.com
# user_test_4_password

# user_test_5
# User_test_5@email.com
# user_test_5_password