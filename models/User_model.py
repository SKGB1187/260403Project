"""SQLAlchemy models for Warbler."""
from . import db

from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

class User(db.Model):
    """User in the system."""

    __tablename__ = 'users'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

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

    def __repr__(self):
        return f"<User #{self.id}: {self.username}, {self.email}, {self.password}>"

    @classmethod
    def signup(cls, username, email, password):
        """Sign up user.

        Hashes password and adds user to system.
        """
        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = cls(
            username=username,
            email=email,
            password=hashed_pwd,
        )

        db.session.add(user)
        return user

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

        return False


