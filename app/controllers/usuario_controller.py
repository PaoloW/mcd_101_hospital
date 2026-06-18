from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.controllers.auth_controller import admin_requerido, login_requerido
from app.extensions import db
from app.models.usuario import Usuario

usuarios_bp = Blueprint("usuarios", __name__, url_prefix="/usuarios")


@usuarios_bp.route("/")
@login_requerido
def listar_usuarios():
    usuarios = Usuario.query.order_by(Usuario.id).all()
    return render_template("usuarios/listar.html", usuarios=usuarios)


@usuarios_bp.route("/create", methods=["GET", "POST"])
@admin_requerido
def crear_usuario():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        rol_id = request.form.get("rol_id", type=int, default=2)
        estado = request.form.get("estado", type=int, default=1)

        if not username or not password:
            flash("Usuario y contraseña son obligatorios.", "danger")
            return render_template("usuarios/form.html", usuario=None)

        if Usuario.query.filter_by(username=username).first():
            flash("Ese nombre de usuario ya existe.", "danger")
            return render_template("usuarios/form.html", usuario=None)

        usuario = Usuario(username=username, rol_id=rol_id, estado=estado)
        usuario.set_password(password)

        db.session.add(usuario)
        db.session.commit()

        flash("Usuario creado correctamente.", "success")
        return redirect(url_for("usuarios.listar_usuarios"))

    return render_template("usuarios/form.html", usuario=None)


@usuarios_bp.route("/<int:usuario_id>/edit", methods=["GET", "POST"])
@admin_requerido
def editar_usuario(usuario_id):
    usuario = Usuario.query.get_or_404(usuario_id)

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        rol_id = request.form.get("rol_id", type=int)
        estado = request.form.get("estado", type=int)

        if not username:
            flash("El nombre de usuario es obligatorio.", "danger")
            return render_template("usuarios/form.html", usuario=usuario)

        existing = Usuario.query.filter(
            Usuario.username == username, Usuario.id != usuario_id
        ).first()
        if existing:
            flash("Ese nombre de usuario ya existe.", "danger")
            return render_template("usuarios/form.html", usuario=usuario)

        usuario.username = username
        usuario.rol_id = rol_id
        usuario.estado = estado

        if password:
            usuario.set_password(password)

        db.session.commit()

        flash("Usuario actualizado correctamente.", "success")
        return redirect(url_for("usuarios.listar_usuarios"))

    return render_template("usuarios/form.html", usuario=usuario)


@usuarios_bp.route("/<int:usuario_id>/delete", methods=["POST"])
@admin_requerido
def borrar_usuario(usuario_id):
    usuario = Usuario.query.get_or_404(usuario_id)
    db.session.delete(usuario)
    db.session.commit()

    flash("Usuario eliminado correctamente.", "success")
    return redirect(url_for("usuarios.listar_usuarios"))
