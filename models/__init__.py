from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .User_model import User
from .Song_model import Song
from .List_model import List