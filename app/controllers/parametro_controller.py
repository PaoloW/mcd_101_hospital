from decimal import Decimal, InvalidOperation

from flask import Blueprint, flash, redirect, render_template, request, url_for
from sqlalchemy import text

from app.controllers.auth_controller import personal_requerido
from app.extensions import db
from app.models.parametro import Parametro
from app.models.tipo_parametro import TipoParametro

parametros_bp = Blueprint("parametros", __name__, url_prefix="/parametros")

PER_PAGE = 20


def _parsear_decimal(valor: str):
    if not valor or not valor.strip():
        return None
    try:
        return Decimal(valor.strip().replace(",", "."))
    except InvalidOperation:
        return None


def _datos_formulario_parametro():
    return {
        "tipo_parametro_id": request.form.get("tipo_parametro_id", type=int),
        "nombre": request.form.get("nombre", "").strip(),
        "valor_referencia_min": _parsear_decimal(request.form.get("valor_referencia_min", "")),
        "valor_referencia_max": _parsear_decimal(request.form.get("valor_referencia_max", "")),
        "unidad_medida": request.form.get("unidad_medida", "").strip() or None,
        "observacion": request.form.get("observacion", "").strip() or None,
    }


@parametros_bp.route("/")
@personal_requerido
def listar_parametros():
    page = request.args.get("page", 1, type=int)
    busqueda = request.args.get("busqueda", "").strip()
    query = Parametro.query.order_by(Parametro.id.desc())
    if busqueda:
        filtro = (
            Parametro.nombre.ilike(f"%{busqueda}%")
            | Parametro.unidad_medida.ilike(f"%{busqueda}%")
            | Parametro.observacion.ilike(f"%{busqueda}%")
        )
        query = query.filter(filtro)
    pagination = query.paginate(page=page, per_page=PER_PAGE, error_out=False)
    return render_template("parametros/listar.html", pagination=pagination, parametros=pagination.items, busqueda=busqueda)


@parametros_bp.route("/create", methods=["GET", "POST"])
@personal_requerido
def guardar_parametro():
    tipos = TipoParametro.query.order_by(TipoParametro.nombre).all()

    if request.method == "POST":
        datos = _datos_formulario_parametro()

        if not datos["nombre"]:
            flash("El nombre del parámetro es obligatorio.", "danger")
            return render_template("parametros/form.html", parametro=None, tipos=tipos)

        if not datos["tipo_parametro_id"]:
            flash("Debe seleccionar un tipo de parámetro.", "danger")
            return render_template("parametros/form.html", parametro=None, tipos=tipos)

        if not TipoParametro.query.get(datos["tipo_parametro_id"]):
            flash("El tipo de parámetro seleccionado no existe.", "danger")
            return render_template("parametros/form.html", parametro=None, tipos=tipos)

        parametro = Parametro(**datos)
        db.session.add(parametro)
        db.session.commit()

        flash("Parámetro registrado correctamente.", "success")
        return redirect(url_for("parametros.listar_parametros"))

    return render_template("parametros/form.html", parametro=None, tipos=tipos)


@parametros_bp.route("/<int:parametro_id>/edit", methods=["GET", "POST"])
@personal_requerido
def actualizar_parametro(parametro_id):
    parametro = Parametro.query.get_or_404(parametro_id)
    tipos = TipoParametro.query.order_by(TipoParametro.nombre).all()

    if request.method == "POST":
        datos = _datos_formulario_parametro()

        if not datos["nombre"]:
            flash("El nombre del parámetro es obligatorio.", "danger")
            return render_template("parametros/form.html", parametro=parametro, tipos=tipos)

        if not datos["tipo_parametro_id"]:
            flash("Debe seleccionar un tipo de parámetro.", "danger")
            return render_template("parametros/form.html", parametro=parametro, tipos=tipos)

        for campo, valor in datos.items():
            setattr(parametro, campo, valor)

        db.session.commit()

        flash("Parámetro actualizado correctamente.", "success")
        return redirect(url_for("parametros.listar_parametros"))

    return render_template("parametros/form.html", parametro=parametro, tipos=tipos)


@parametros_bp.route("/<int:parametro_id>/delete", methods=["POST"])
@personal_requerido
def eliminar_parametro(parametro_id):
    parametro = Parametro.query.get_or_404(parametro_id)

    en_uso = db.session.execute(
        text("SELECT id FROM analisis WHERE parametro_id = :id LIMIT 1"),
        {"id": parametro_id},
    ).first()
    if en_uso:
        flash("No se puede eliminar: el parámetro está asociado a análisis.", "danger")
        return redirect(url_for("parametros.listar_parametros"))

    db.session.delete(parametro)
    db.session.commit()

    flash("Parámetro eliminado correctamente.", "success")
    return redirect(url_for("parametros.listar_parametros"))