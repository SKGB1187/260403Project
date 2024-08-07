"""SQLAlchemy models for Warbler."""
import os

from . import db

from sqlalchemy.exc import IntegrityError

from flask_bcrypt import Bcrypt
from .DBActionResult import DBActionResult

bcrypt = Bcrypt()

class User(db.Model):
    """User in the system."""

    __tablename__ = 'users'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )
    
    csrf_token = db.Column(
        db.String(64), 
        unique=True, 
        nullable=False, 
        default=lambda: 
        os.urandom(24).hex())

    username = db.Column(
        db.String(80), 
        unique=True, 
        nullable=False
    )

    email = db.Column(
        db.String(120), 
        unique=True, 
        nullable=False
    )
    
    password = db.Column(
        db.String(128), 
        nullable=False
    )

    spotify_user_id = db.Column(
        db.String(120),
        unique = True,
        nullable = True
    )

    spotify_user_display_name = db.Column(
        db.String(120),
        unique = False,
        nullable = True
    )

    spotify_acct_email = db.Column(
        db.String(1000),
        nullable = True
    )

    spotify_access_token = db.Column(
        db.String(1000),
        unique = True,
        nullable = True
    )

    spotify_access_token_set_time = db.Column(
        db.String(128),
        nullable = True
    )

    spotify_refresh_token = db.Column(
        db.String(1000),
        nullable = True
    )

    def __repr__(self):
        return f"<User #{self.id}: {self.username}, {self.email}, {self.password}, {self.spotify_access_token}, {self.spotify_refresh_token}>"

    @classmethod
    def signup(cls, username, email, password):
        """Sign up user.

        Hashes password and adds user to system.
        """
        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')
        ret: DBActionResult[User] = DBActionResult(None, False, "")

        try:
            user = cls(
                username=username,
                email=email,
                password=hashed_pwd,
            )

            db.session.add(user)
            db.session.commit()

            ret.value = user
            ret.is_success = True
            ret.message = "Account creation successful!"

        except IntegrityError:
            print("user already exists")
            db.session.rollback()
            ret.message = 'Sorry that username is already taken, please pick another'
        
        except Exception as e:
            print("other exception")
            print(str(e))
            db.session.rollback()
            ret.message = 'Sorry, an error occurred during sign-up, please try again.'

        return ret
    
    @classmethod
    def link_spotify_to_database(cls, user_id, spotify_access_token, spotify_access_token_set_time, spotify_refresh_token):
        """
        Add Spotify access token and refresh token information to the user
        so it can be accessed beyond the session.
        """
        
        user = cls.query.get(user_id)
        if user:
            user.spotify_access_token = spotify_access_token
            user.spotify_access_token_set_time = spotify_access_token_set_time
            user.spotify_refresh_token = spotify_refresh_token
            
            db.session.add(user)
            db.session.commit()

            return user
        return None
    
    @classmethod
    def profile_spotify(cls, user_id, spotify_user_id, spotify_user_display_name, spotify_acct_email):
        """
        Add spotify Account Information to the User class
        """
        ret: DBActionResult[User] = DBActionResult(None, False, "")
        
        try:
            user = cls.query.get(user_id)
            if user:
                user.spotify_user_id = spotify_user_id,
                user.spotify_user_display_name = spotify_user_display_name,
                user.spotify_acct_email = spotify_acct_email
            
                db.session.commit()

                ret.value = user
                ret.is_success = True
                ret.message = "Spotify profile pull successful!"
               
            else:
                ret.message = "User not found"

        except IntegrityError:
            print("spotify account already linked to other user")
            db.session.rollback()
            ret.message = 'Sorry you can only link a Spotify account to one user account, please link a different Spotify Account'

        except Exception as e:
            print("other exception")
            print(str(e))
            db.session.rollback()
            ret.message = 'Sorry, an error occurred pulling Spotify profile, please try again.'
        
        return ret

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.

        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.

        If can't find matching user (or if password is wrong), returns False.
        """
        user = cls.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            return user
        else:
            print('user and bcrypt of password failed')
            return False


