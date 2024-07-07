from . import db

class Song(db.Model):
    """User in the system."""

    __tablename__ = 'songs'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    title = db.Column(
        db.String(80), 
        nullable=False
    )
    
    artist = db.Column(
        db.String(120), 
        nullable=False
    )

    album = db.Column(
        db.String(120), 
        nullable=False
    )

    release_date = db.Column(
        db.Date, 
        nullable=True
    )

    def __repr__(self):
        return f"<User #{self.id}: {self.title}, {self.artist}, {self.album}, {self.release_date}>"