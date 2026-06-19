from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.controllers.auth_controller import admin_requerido
from app.extensions import db
from app.models.persona import Persona
from app.models.usuario import Usuario

usuarios_bp = Blueprint("usuarios", __name__, url_prefix="/usuarios")

PER_PAGE = 20


@usuarios_bp.route("/")
@admin_requerido
def listar_usuarios():
    page = request.args.get("page", 1, type=int)
    busqueda = request.args.get("busqueda", "").strip()
    query = Usuario.query.order_by(Usuario.id.desc())
    if busqueda:
        filtro = (
            Usuario.username.ilike(f"%{busqueda}%")
        )
        query = query.filter(filtro)
    pagination = query.paginate(page=page, per_page=PER_PAGE, error_out=False)
    return render_template("usuarios/listar.html", pagination=pagination, usuarios=pagination.items, busqueda=busqueda)


@usuarios_bp.route("/create", methods=["GET", "POST"])
@admin_requerido
def guardar_usuario():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        rol_id = request.form.get("rol_id", type=int, default=2)
        estado = request.form.get("estado", type=int, default=1)
        persona_id = request.form.get("persona_id", type=int)

        if not username or not password:
            flash("Usuario y contraseña son obligatorios.", "danger")
            return render_template("usuarios/form.html", usuario=None)

        if not persona_id:
            flash("Debe buscar y seleccionar una persona por documento.", "danger")
            return render_template("usuarios/form.html", usuario=None)

        persona = Persona.query.get(persona_id)
        if persona is None:
            flash("La persona seleccionada no existe.", "danger")
            return render_template("usuarios/form.html", usuario=None)

        if Usuario.query.filter_by(persona_id=persona_id).first():
            flash("Esa persona ya tiene un usuario asociado.", "danger")
            return render_template("usuarios/form.html", usuario=None)

        if Usuario.query.filter_by(username=username).first():
            flash("Ese nombre de usuario ya existe.", "danger")
            return render_template("usuarios/form.html", usuario=None)

        usuario = Usuario(
            persona_id=persona_id,
            username=username,
            rol_id=rol_id,
            estado=estado,
        )
        usuario.set_password(password)

        db.session.add(usuario)
        db.session.commit()

        flash("Usuario creado correctamente.", "success")
        return redirect(url_for("usuarios.listar_usuarios"))

    return render_template("usuarios/form.html", usuario=None)


@usuarios_bp.route("/<int:usuario_id>/edit", methods=["GET", "POST"])
@admin_requerido
def actualizar_usuario(usuario_id):
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