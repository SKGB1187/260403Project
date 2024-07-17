from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Boolean

db = SQLAlchemy()

from .User_model import User
from .Song_model import Song
from .List_model import List