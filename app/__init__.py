from flask import Flask, redirect, url_for

from app.config import Config
from app.controllers import (
    auth_bp,
    personas_bp,
    usuarios_bp,
    atenciones_bp,
    enfermedades_bp,
    secciones_procedimientos_bp,
    procedimientos_bp,
    medicamentos_bp,
    tipos_parametros_bp,
    parametros_bp,
    analisis_bp,
    diagnosticos_bp,
    prescripciones_bp,
    procedimientos_realizados_bp,
    campanas_bp,
)
from app.extensions import db, migrate


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(auth_bp)
    app.register_blueprint(personas_bp)
    app.register_blueprint(usuarios_bp)
    app.register_blueprint(atenciones_bp)
    app.register_blueprint(enfermedades_bp)
    app.register_blueprint(secciones_procedimientos_bp)
    app.register_blueprint(procedimientos_bp)
    app.register_blueprint(medicamentos_bp)
    app.register_blueprint(tipos_parametros_bp)
    app.register_blueprint(parametros_bp)
    app.register_blueprint(analisis_bp)
    app.register_blueprint(diagnosticos_bp)
    app.register_blueprint(prescripciones_bp)
    app.register_blueprint(procedimientos_realizados_bp)
    app.register_blueprint(campanas_bp)

    @app.route("/")
    def index():
        return redirect(url_for("auth.login"))

    return app
