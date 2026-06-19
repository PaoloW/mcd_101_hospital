from functools import wraps

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from app.extensions import db
from app.models.usuario import Usuario

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

def login_requerido(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if "usuario_id" not in session:
            flash("Debes iniciar sesión para continuar.", "warning")
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)

    return wrapped_view

def admin_requerido(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if "usuario_id" not in session:
            flash("Debes iniciar sesión para continuar.", "warning")
            return redirect(url_for("auth.login"))
        if session.get("rol_id") != Usuario.ADMIN_ROL_ID:
            flash("No tienes permisos para realizar esta acción.", "danger")
            return redirect(url_for("auth.home"))
        return view(*args, **kwargs)

    return wrapped_view

def personal_requerido(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if "usuario_id" not in session:
            flash("Debes iniciar sesión para continuar.", "warning")
            return redirect(url_for("auth.login"))
        if session.get("rol_id") not in [
            Usuario.ADMIN_ROL_ID,
            Usuario.DOCTOR_ROL_ID,
            Usuario.ENFERMERO_ROL_ID,
            Usuario.LABORATORISTA_ROL_ID,
        ]:
            flash("No tienes permisos para realizar esta acción.", "danger")
            return redirect(url_for("auth.home"))
        return view(*args, **kwargs)
    return wrapped_view

def personal_medico_requerido(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if "usuario_id" not in session:
            flash("Debes iniciar sesión para continuar.", "warning")
            return redirect(url_for("auth.login"))
        if session.get("rol_id") not in [
            Usuario.DOCTOR_ROL_ID,
            Usuario.ENFERMERO_ROL_ID,
            Usuario.LABORATORISTA_ROL_ID,
        ]:
            flash("No tienes permisos para realizar esta acción.", "danger")
            return redirect(url_for("auth.home"))
        return view(*args, **kwargs)
    return wrapped_view


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if session.get("usuario_id"):
        return redirect(url_for("auth.home"))

    if request.method == "POST":
        username = request.form.get("usuario", "").strip()
        password = request.form.get("password", "")

        usuario = Usuario.query.filter_by(username=username).first()

        if usuario is None or not usuario.check_password(password):
            flash("Usuario o contraseña incorrectos.", "danger")
            return render_template("auth/login.html")

        if not usuario.is_active:
            flash("Tu cuenta está inactiva.", "danger")
            return render_template("auth/login.html")

        session.clear()
        session["usuario_id"] = usuario.id
        session["username"] = usuario.username
        session["rol_id"] = usuario.rol_id

        flash(f"Bienvenido, {usuario.username}.", "success")
        return redirect(url_for("auth.home"))

    return render_template("auth/login.html")

@auth_bp.route("/logout")
@login_requerido
def logout():
    session.clear()
    flash("Sesión cerrada correctamente.", "info")
    return redirect(url_for("auth.login"))

@auth_bp.route("/home")
def home():
    return render_template("home.html")