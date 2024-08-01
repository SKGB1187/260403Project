import os

from flask import Flask

from flask_wtf.csrf import CSRFProtect

from .models import db

from .config import Config

csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)
    app.secret_key = os.urandom(32)

    app.config.from_object(Config())

    csrf.init_app(app)
    db.init_app(app)

    with app.app_context():
        db.create_all()

    from .routes.routes_auth_spotify import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .routes.routes_main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .routes.routes_spotify_playlists import playlists_spotify as playlists_spotify_blueprint
    app.register_blueprint(playlists_spotify_blueprint)

    from .routes.routes_spotify_profile import profile as profile_blueprint
    app.register_blueprint(profile_blueprint)

    from .routes.routes_spotify_songs import songs_spotify as songs_spotify_blueprint
    app.register_blueprint(songs_spotify_blueprint)

    return app

app = create_app()

print(app.url_map)

if __name__ == "__main__":
    app.run()