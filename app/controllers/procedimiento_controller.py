from flask import Blueprint, flash, redirect, render_template, request, url_for
from sqlalchemy import text

from app.controllers.auth_controller import personal_requerido
from app.extensions import db
from app.models.procedimiento import Procedimiento
from app.models.seccion_procedimiento import SeccionProcedimiento

procedimientos_bp = Blueprint("procedimientos", __name__, url_prefix="/procedimientos")

PER_PAGE = 20


def _datos_formulario_procedimiento():
    return {
        "codigo_cpms": request.form.get("codigo_cpms", "").strip(),
        "nombre": request.form.get("nombre", "").strip(),
        "seccion_procedimiento_id": request.form.get("seccion_procedimiento_id", type=int),
    }


@procedimientos_bp.route("/")
@personal_requerido
def listar_procedimientos():
    page = request.args.get("page", 1, type=int)
    query = Procedimiento.query.order_by(Procedimiento.id.desc())
    pagination = query.paginate(page=page, per_page=PER_PAGE, error_out=False)
    return render_template("procedimientos/listar.html", pagination=pagination, procedimientos=pagination.items)


@procedimientos_bp.route("/create", methods=["GET", "POST"])
@personal_requerido
def guardar_procedimiento():
    secciones = SeccionProcedimiento.query.order_by(SeccionProcedimiento.nombre).all()

    if request.method == "POST":
        datos = _datos_formulario_procedimiento()

        if not datos["codigo_cpms"] or not datos["nombre"]:
            flash("El código CPMS y el nombre son obligatorios.", "danger")
            return render_template(
                "procedimientos/form.html",
                procedimiento=None,
                secciones=secciones,
            )

        if not datos["seccion_procedimiento_id"]:
            flash("Debe seleccionar una sección.", "danger")
            return render_template(
                "procedimientos/form.html",
                procedimiento=None,
                secciones=secciones,
            )

        if not SeccionProcedimiento.query.get(datos["seccion_procedimiento_id"]):
            flash("La sección seleccionada no existe.", "danger")
            return render_template(
                "procedimientos/form.html",
                procedimiento=None,
                secciones=secciones,
            )

        procedimiento = Procedimiento(**datos)
        db.session.add(procedimiento)
        db.session.commit()

        flash("Procedimiento registrado correctamente.", "success")
        return redirect(url_for("procedimientos.listar_procedimientos"))

    return render_template(
        "procedimientos/form.html",
        procedimiento=None,
        secciones=secciones,
    )


@procedimientos_bp.route("/<int:procedimiento_id>/edit", methods=["GET", "POST"])
@personal_requerido
def actualizar_procedimiento(procedimiento_id):
    procedimiento = Procedimiento.query.get_or_404(procedimiento_id)
    secciones = SeccionProcedimiento.query.order_by(SeccionProcedimiento.nombre).all()

    if request.method == "POST":
        datos = _datos_formulario_procedimiento()

        if not datos["codigo_cpms"] or not datos["nombre"]:
            flash("El código CPMS y el nombre son obligatorios.", "danger")
            return render_template(
                "procedimientos/form.html",
                procedimiento=procedimiento,
                secciones=secciones,
            )

        if not datos["seccion_procedimiento_id"]:
            flash("Debe seleccionar una sección.", "danger")
            return render_template(
                "procedimientos/form.html",
                procedimiento=procedimiento,
                secciones=secciones,
            )

        for campo, valor in datos.items():
            setattr(procedimiento, campo, valor)

        db.session.commit()

        flash("Procedimiento actualizado correctamente.", "success")
        return redirect(url_for("procedimientos.listar_procedimientos"))

    return render_template(
        "procedimientos/form.html",
        procedimiento=procedimiento,
        secciones=secciones,
    )


@procedimientos_bp.route("/<int:procedimiento_id>/delete", methods=["POST"])
@personal_requerido
def eliminar_procedimiento(procedimiento_id):
    procedimiento = Procedimiento.query.get_or_404(procedimiento_id)

    en_uso = db.session.execute(
        text("SELECT id FROM procedimiento_realizado WHERE procedimiento_id = :id LIMIT 1"),
        {"id": procedimiento_id},
    ).first()
    if en_uso:
        flash("No se puede eliminar: el procedimiento está registrado en atenciones.", "danger")
        return redirect(url_for("procedimientos.listar_procedimientos"))

    db.session.delete(procedimiento)
    db.session.commit()

    flash("Procedimiento eliminado correctamente.", "success")
    return redirect(url_for("procedimientos.listar_procedimientos"))