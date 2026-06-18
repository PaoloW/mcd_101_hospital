from flask import Flask, redirect, url_for

from app.config import Config
from app.controllers import auth_bp, usuarios_bp
from app.extensions import db


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(usuarios_bp)

    @app.route("/")
    def index():
        return redirect(url_for("auth.login"))

    return app
