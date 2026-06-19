from flask import Blueprint, flash, redirect, render_template, request, url_for
from sqlalchemy import text

from app.controllers.auth_controller import personal_requerido
from app.extensions import db
from app.models.enfermedad import Enfermedad

enfermedades_bp = Blueprint("enfermedades", __name__, url_prefix="/enfermedades")

PER_PAGE = 20


def _datos_formulario_enfermedad():
    return {
        "nombre": request.form.get("nombre", "").strip(),
        "codigo_cie10": request.form.get("codigo_cie10", "").strip() or None,
    }


@enfermedades_bp.route("/")
@personal_requerido
def listar_enfermedades():
    page = request.args.get("page", 1, type=int)
    query = Enfermedad.query.order_by(Enfermedad.id.desc())
    pagination = query.paginate(page=page, per_page=PER_PAGE, error_out=False)
    return render_template("enfermedades/listar.html", pagination=pagination, enfermedades=pagination.items)


@enfermedades_bp.route("/create", methods=["GET", "POST"])
@personal_requerido
def guardar_enfermedad():
    if request.method == "POST":
        datos = _datos_formulario_enfermedad()

        if not datos["nombre"]:
            flash("El nombre de la enfermedad es obligatorio.", "danger")
            return render_template("enfermedades/form.html", enfermedad=None)

        enfermedad = Enfermedad(**datos)
        db.session.add(enfermedad)
        db.session.commit()

        flash("Enfermedad registrada correctamente.", "success")
        return redirect(url_for("enfermedades.listar_enfermedades"))

    return render_template("enfermedades/form.html", enfermedad=None)


@enfermedades_bp.route("/<int:enfermedad_id>/edit", methods=["GET", "POST"])
@personal_requerido
def actualizar_enfermedad(enfermedad_id):
    enfermedad = Enfermedad.query.get_or_404(enfermedad_id)

    if request.method == "POST":
        datos = _datos_formulario_enfermedad()

        if not datos["nombre"]:
            flash("El nombre de la enfermedad es obligatorio.", "danger")
            return render_template("enfermedades/form.html", enfermedad=enfermedad)

        for campo, valor in datos.items():
            setattr(enfermedad, campo, valor)

        db.session.commit()

        flash("Enfermedad actualizada correctamente.", "success")
        return redirect(url_for("enfermedades.listar_enfermedades"))

    return render_template("enfermedades/form.html", enfermedad=enfermedad)


@enfermedades_bp.route("/<int:enfermedad_id>/delete", methods=["POST"])
@personal_requerido
def eliminar_enfermedad(enfermedad_id):
    enfermedad = Enfermedad.query.get_or_404(enfermedad_id)

    en_uso = db.session.execute(
        text("SELECT id FROM diagnosticos WHERE enfermedad_id = :id LIMIT 1"),
        {"id": enfermedad_id},
    ).first()
    if en_uso:
        flash("No se puede eliminar: la enfermedad está asociada a diagnósticos.", "danger")
        return redirect(url_for("enfermedades.listar_enfermedades"))

    db.session.delete(enfermedad)
    db.session.commit()

    flash("Enfermedad eliminada correctamente.", "success")
    return redirect(url_for("enfermedades.listar_enfermedades"))