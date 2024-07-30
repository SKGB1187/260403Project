import os

from datetime import timedelta

class Config:
    SECRET_KEY = os.urandom(32)
    SQLALCHEMY_DATABASE_URI = os.environ.get('playspotplay_connection', 'postgresql:///playspotplay')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO  = False
    DEBUG_TB_INTERCEPT_REDIRECTS = True
    SESSION_TYPE = 'sqlalchemy'
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax'
