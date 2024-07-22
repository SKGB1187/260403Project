from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Boolean

db = SQLAlchemy()

from .Artist_model import Artist
from .Artist_Song_model import Artist_Song

from .Playlist_model import Playlist
from .Playlist_Song_model import Playlist_Song

from .Song_model import Song

from .User_model import User