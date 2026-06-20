from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.controllers.auth_controller import personal_medico_requerido
from app.extensions import db
from app.models.prescripcion import Prescripcion
from app.models.medicamento import Medicamento

prescripciones_bp = Blueprint("prescripciones", __name__, url_prefix="/atenciones/<int:atencion_id>/prescripciones")

PER_PAGE = 20


def _datos_formulario_prescripcion():
    return {
        "medicamento_id": request.form.get("medicamento_id", "") or None,
        "atencion_id": request.form.get("atencion_id", "") or None,
        "dosis": request.form.get("dosis", "").strip(),
        "fecha": request.form.get("fecha", "") or None,
        "cantidad": request.form.get("cantidad", "") or None,
        "responsable_id": request.form.get("responsable_id", "") or None,
    }


@prescripciones_bp.route("/")
@personal_medico_requerido
def listar_prescripciones(atencion_id):
    from app.models.atencion_medica import AtencionMedica
    atencion = AtencionMedica.query.get_or_404(atencion_id)
    page = request.args.get("page", 1, type=int)
    busqueda = request.args.get("busqueda", "").strip()
    query = Prescripcion.query.filter_by(atencion_id=atencion_id).order_by(Prescripcion.id.desc())
    if busqueda:
        query = query.join(Medicamento).filter(Medicamento.nombre.ilike(f"%{busqueda}%"))
    pagination = query.paginate(page=page, per_page=PER_PAGE, error_out=False)
    medicamentos = Medicamento.query.all()
    return render_template(
        "atenciones/prescripciones/listar.html",
        pagination=pagination,
        prescripciones=pagination.items,
        busqueda=busqueda,
        atencion=atencion,
        medicamentos=medicamentos,
    )


@prescripciones_bp.route("/create", methods=["GET", "POST"])
@personal_medico_requerido
def crear_prescripcion(atencion_id):
    from app.models.atencion_medica import AtencionMedica
    atencion = AtencionMedica.query.get_or_404(atencion_id)
    medicamentos = [
        {
            "id": m.id,
            "codigo": m.codigo,
            "denominacion": m.denominacion,
            "unidad_medida": m.unidad_medida,
        }
        for m in Medicamento.query.all()
    ]

    if request.method == "POST":
        datos = _datos_formulario_prescripcion()

        if not datos["medicamento_id"]:
            flash("El medicamento es obligatorio.", "danger")
            return render_template(
                "atenciones/prescripciones/form.html",
                prescripcion=None,
                atencion=atencion,
                medicamentos=medicamentos,
            )

        if not datos["dosis"]:
            flash("La dosis es obligatoria.", "danger")
            return render_template(
                "atenciones/prescripciones/form.html",
                prescripcion=None,
                atencion=atencion,
                medicamentos=medicamentos,
            )

        if not datos["fecha"]:
            flash("La fecha es obligatoria.", "danger")
            return render_template(
                "atenciones/prescripciones/form.html",
                prescripcion=None,
                atencion=atencion,
                medicamentos=medicamentos,
            )

        prescripcion = Prescripcion(atencion_id=atencion_id, **datos)
        db.session.add(prescripcion)
        db.session.commit()

        flash("Prescripción registrada correctamente.", "success")
        return redirect(url_for("prescripciones.listar_prescripciones", atencion_id=atencion_id))

    return render_template(
        "atenciones/prescripciones/form.html",
        prescripcion=None,
        atencion=atencion,
        medicamentos=medicamentos,
    )


@prescripciones_bp.route("/<int:prescripcion_id>/ver")
@personal_medico_requerido
def ver_prescripcion(atencion_id, prescripcion_id):
    from app.models.atencion_medica import AtencionMedica
    atencion = AtencionMedica.query.get_or_404(atencion_id)
    prescripcion = Prescripcion.query.filter_by(id=prescripcion_id, atencion_id=atencion_id).first_or_404()
    medicamentos = Medicamento.query.all()
    return render_template(
        "atenciones/prescripciones/form.html",
        prescripcion=prescripcion,
        atencion=atencion,
        medicamentos=medicamentos,
        solo_lectura=True,
    )


@prescripciones_bp.route("/<int:prescripcion_id>/edit", methods=["GET", "POST"])
@personal_medico_requerido
def editar_prescripcion(atencion_id, prescripcion_id):
    from app.models.atencion_medica import AtencionMedica
    atencion = AtencionMedica.query.get_or_404(atencion_id)
    prescripcion = Prescripcion.query.filter_by(id=prescripcion_id, atencion_id=atencion_id).first_or_404()
    medicamentos = Medicamento.query.all()

    if request.method == "POST":
        datos = _datos_formulario_prescripcion()

        if not datos["medicamento_id"]:
            flash("El medicamento es obligatorio.", "danger")
            return render_template(
                "atenciones/prescripciones/form.html",
                prescripcion=prescripcion,
                atencion=atencion,
                medicamentos=medicamentos,
            )

        if not datos["dosis"]:
            flash("La dosis es obligatoria.", "danger")
            return render_template(
                "atenciones/prescripciones/form.html",
                prescripcion=prescripcion,
                atencion=atencion,
                medicamentos=medicamentos,
            )

        if not datos["fecha"]:
            flash("La fecha es obligatoria.", "danger")
            return render_template(
                "atenciones/prescripciones/form.html",
                prescripcion=prescripcion,
                atencion=atencion,
                medicamentos=medicamentos,
            )

        for campo, valor in datos.items():
            setattr(prescripcion, campo, valor)

        db.session.commit()

        flash("Prescripción actualizada correctamente.", "success")
        return redirect(url_for("prescripciones.listar_prescripciones", atencion_id=atencion_id))

    return render_template(
        "atenciones/prescripciones/form.html",
        prescripcion=prescripcion,
        atencion=atencion,
        medicamentos=medicamentos,
    )


@prescripciones_bp.route("/<int:prescripcion_id>/delete", methods=["POST"])
@personal_medico_requerido
def eliminar_prescripcion(atencion_id, prescripcion_id):
    from app.models.atencion_medica import AtencionMedica
    AtencionMedica.query.get_or_404(atencion_id)
    prescripcion = Prescripcion.query.filter_by(id=prescripcion_id, atencion_id=atencion_id).first_or_404()

    db.session.delete(prescripcion)
    db.session.commit()

    flash("Prescripción eliminada correctamente.", "success")
    return redirect(url_for("prescripciones.listar_prescripciones", atencion_id=atencion_id))