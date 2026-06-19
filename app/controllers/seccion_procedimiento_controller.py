from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.controllers.auth_controller import personal_requerido
from app.extensions import db
from app.models.procedimiento import Procedimiento
from app.models.seccion_procedimiento import SeccionProcedimiento

secciones_procedimientos_bp = Blueprint(
    "secciones_procedimientos",
    __name__,
    url_prefix="/secciones-procedimientos",
)

PER_PAGE = 20


def _datos_formulario_seccion():
    return {
        "nombre": request.form.get("nombre", "").strip(),
        "codigo": request.form.get("codigo", "").strip() or None,
    }


@secciones_procedimientos_bp.route("/")
@personal_requerido
def listar_secciones():
    page = request.args.get("page", 1, type=int)
    query = SeccionProcedimiento.query.order_by(SeccionProcedimiento.id.desc())
    pagination = query.paginate(page=page, per_page=PER_PAGE, error_out=False)
    return render_template("secciones_procedimientos/listar.html", pagination=pagination, secciones=pagination.items)


@secciones_procedimientos_bp.route("/create", methods=["GET", "POST"])
@personal_requerido
def guardar_seccion():
    if request.method == "POST":
        datos = _datos_formulario_seccion()

        if not datos["nombre"]:
            flash("El nombre de la sección es obligatorio.", "danger")
            return render_template("secciones_procedimientos/form.html", seccion=None)

        seccion = SeccionProcedimiento(**datos)
        db.session.add(seccion)
        db.session.commit()

        flash("Sección registrada correctamente.", "success")
        return redirect(url_for("secciones_procedimientos.listar_secciones"))

    return render_template("secciones_procedimientos/form.html", seccion=None)


@secciones_procedimientos_bp.route("/<int:seccion_id>/edit", methods=["GET", "POST"])
@personal_requerido
def actualizar_seccion(seccion_id):
    seccion = SeccionProcedimiento.query.get_or_404(seccion_id)

    if request.method == "POST":
        datos = _datos_formulario_seccion()

        if not datos["nombre"]:
            flash("El nombre de la sección es obligatorio.", "danger")
            return render_template("secciones_procedimientos/form.html", seccion=seccion)

        for campo, valor in datos.items():
            setattr(seccion, campo, valor)

        db.session.commit()

        flash("Sección actualizada correctamente.", "success")
        return redirect(url_for("secciones_procedimientos.listar_secciones"))

    return render_template("secciones_procedimientos/form.html", seccion=seccion)


@secciones_procedimientos_bp.route("/<int:seccion_id>/delete", methods=["POST"])
@personal_requerido
def eliminar_seccion(seccion_id):
    seccion = SeccionProcedimiento.query.get_or_404(seccion_id)

    if Procedimiento.query.filter_by(seccion_procedimiento_id=seccion_id).first():
        flash("No se puede eliminar: la sección tiene procedimientos asociados.", "danger")
        return redirect(url_for("secciones_procedimientos.listar_secciones"))

    db.session.delete(seccion)
    db.session.commit()

    flash("Sección eliminada correctamente.", "success")
    return redirect(url_for("secciones_procedimientos.listar_secciones"))