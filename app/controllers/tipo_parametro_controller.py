from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.controllers.auth_controller import personal_requerido
from app.extensions import db
from app.models.parametro import Parametro
from app.models.tipo_parametro import TipoParametro

tipos_parametros_bp = Blueprint("tipos_parametros", __name__, url_prefix="/tipos-parametros")

PER_PAGE = 20


def _datos_formulario_tipo_parametro():
    return {
        "nombre": request.form.get("nombre", "").strip(),
    }


@tipos_parametros_bp.route("/")
@personal_requerido
def listar_tipos_parametros():
    page = request.args.get("page", 1, type=int)
    busqueda = request.args.get("busqueda", "").strip()
    query = TipoParametro.query.order_by(TipoParametro.id.desc())
    if busqueda:
        filtro = TipoParametro.nombre.ilike(f"%{busqueda}%")
        query = query.filter(filtro)
    pagination = query.paginate(page=page, per_page=PER_PAGE, error_out=False)
    return render_template("tipos_parametros/listar.html", pagination=pagination, tipos=pagination.items, busqueda=busqueda)


@tipos_parametros_bp.route("/create", methods=["GET", "POST"])
@personal_requerido
def guardar_tipo_parametro():
    if request.method == "POST":
        datos = _datos_formulario_tipo_parametro()

        if not datos["nombre"]:
            flash("El nombre del tipo de parámetro es obligatorio.", "danger")
            return render_template("tipos_parametros/form.html", tipo=None)

        tipo = TipoParametro(**datos)
        db.session.add(tipo)
        db.session.commit()

        flash("Tipo de parámetro registrado correctamente.", "success")
        return redirect(url_for("tipos_parametros.listar_tipos_parametros"))

    return render_template("tipos_parametros/form.html", tipo=None)


@tipos_parametros_bp.route("/<int:tipo_id>/ver")
@personal_requerido
def ver_tipo_parametro(tipo_id):
    tipo = TipoParametro.query.get_or_404(tipo_id)
    return render_template("tipos_parametros/form.html", tipo=tipo, solo_lectura=True)


@tipos_parametros_bp.route("/<int:tipo_id>/edit", methods=["GET", "POST"])
@personal_requerido
def actualizar_tipo_parametro(tipo_id):
    tipo = TipoParametro.query.get_or_404(tipo_id)

    if request.method == "POST":
        datos = _datos_formulario_tipo_parametro()

        if not datos["nombre"]:
            flash("El nombre del tipo de parámetro es obligatorio.", "danger")
            return render_template("tipos_parametros/form.html", tipo=tipo)

        tipo.nombre = datos["nombre"]
        db.session.commit()

        flash("Tipo de parámetro actualizado correctamente.", "success")
        return redirect(url_for("tipos_parametros.listar_tipos_parametros"))

    return render_template("tipos_parametros/form.html", tipo=tipo)


@tipos_parametros_bp.route("/<int:tipo_id>/delete", methods=["POST"])
@personal_requerido
def eliminar_tipo_parametro(tipo_id):
    tipo = TipoParametro.query.get_or_404(tipo_id)

    if Parametro.query.filter_by(tipo_parametro_id=tipo_id).first():
        flash("No se puede eliminar: el tipo tiene parámetros asociados.", "danger")
        return redirect(url_for("tipos_parametros.listar_tipos_parametros"))

    db.session.delete(tipo)
    db.session.commit()

    flash("Tipo de parámetro eliminado correctamente.", "success")
    return redirect(url_for("tipos_parametros.listar_tipos_parametros"))