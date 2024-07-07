from . import db

class List(db.Model):
    """User in the system."""

    __tablename__ = 'playlists'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    name = db.Column(
        db.String(80), 
        nullable=False
    )

    description = db.Column(
        db.String(200), 
        nullable=True
    )

    user_id = db.Column(
        db.Integer, 
        db.ForeignKey('users.id'), 
        nullable=False
    )

    user = db.relationship('User', backref=db.backref('lists', lazy=True))

    def __repr__(self):
        return f"<User #{self.id}: {self.name}, {self.description}>"