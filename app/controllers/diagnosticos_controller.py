from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.controllers.auth_controller import personal_medico_requerido
from app.extensions import db
from app.models.diagnostico import Diagnostico
from app.models.enfermedad import Enfermedad
from app.models.usuario import Usuario

diagnosticos_bp = Blueprint("diagnosticos", __name__, url_prefix="/atenciones/<int:atencion_id>/diagnosticos")

PER_PAGE = 20


def _datos_formulario_diagnostico():
    return {
        "enfermedad_id": request.form.get("enfermedad_id", "") or None,
        "descripcion": request.form.get("descripcion", "") or None,
        "fecha": request.form.get("fecha", "") or None,
        "responsable_id": request.form.get("responsable_id", "") or None,
    }


@diagnosticos_bp.route("/")
@personal_medico_requerido
def listar_diagnosticos(atencion_id):
    from app.models.atencion_medica import AtencionMedica
    atencion = AtencionMedica.query.get_or_404(atencion_id)
    page = request.args.get("page", 1, type=int)
    busqueda = request.args.get("busqueda", "").strip()
    query = Diagnostico.query.filter_by(atencion_id=atencion_id).order_by(Diagnostico.id.desc())
    if busqueda:
        query = query.join(Enfermedad).filter(Enfermedad.nombre.ilike(f"%{busqueda}%"))
    pagination = query.paginate(page=page, per_page=PER_PAGE, error_out=False)
    enfermedades = Enfermedad.query.all()
    return render_template(
        "atenciones/diagnosticos/listar.html",
        pagination=pagination,
        diagnosticos=pagination.items,
        busqueda=busqueda,
        atencion=atencion,
        enfermedades=enfermedades,
    )


@diagnosticos_bp.route("/create", methods=["GET", "POST"])
@personal_medico_requerido
def crear_diagnostico(atencion_id):
    from app.models.atencion_medica import AtencionMedica
    atencion = AtencionMedica.query.get_or_404(atencion_id)
    enfermedades = [
        {
            "id": e.id,
            "nombre": e.nombre,
            "codigo_cie10": e.codigo_cie10,
        }
        for e in Enfermedad.query.all()
    ]
    responsables = Usuario.query.filter_by(rol_id=2).all()

    if request.method == "POST":
        datos = _datos_formulario_diagnostico()

        if not datos["enfermedad_id"]:
            flash("La enfermedad es obligatoria.", "danger")
            return render_template(
                "atenciones/diagnosticos/form.html", diagnostico=None, atencion=atencion, enfermedades=enfermedades, responsables=responsables
            )

        if not datos["fecha"]:
            flash("La fecha es obligatoria.", "danger")
            return render_template(
                "atenciones/diagnosticos/form.html", diagnostico=None, atencion=atencion, enfermedades=enfermedades, responsables=responsables
            )

        if not datos["responsable_id"]:
            flash("El responsable es obligatorio.", "danger")
            return render_template(
                "atenciones/diagnosticos/form.html", diagnostico=None, atencion=atencion, enfermedades=enfermedades, responsables=responsables
            )

        diagnostico = Diagnostico(atencion_id=atencion_id, **datos)
        db.session.add(diagnostico)
        db.session.commit()

        flash("Diagnóstico registrado correctamente.", "success")
        return redirect(url_for("diagnosticos.listar_diagnosticos", atencion_id=atencion_id))

    return render_template(
        "atenciones/diagnosticos/form.html", diagnostico=None, atencion=atencion, enfermedades=enfermedades, responsables=responsables
    )


@diagnosticos_bp.route("/<int:diagnostico_id>/ver")
@personal_medico_requerido
def ver_diagnostico(atencion_id, diagnostico_id):
    from app.models.atencion_medica import AtencionMedica
    atencion = AtencionMedica.query.get_or_404(atencion_id)
    diagnostico = Diagnostico.query.filter_by(id=diagnostico_id, atencion_id=atencion_id).first_or_404()
    enfermedades = [
        {
            "id": e.id,
            "nombre": e.nombre,
            "codigo_cie10": e.codigo_cie10,
        }
        for e in Enfermedad.query.all()
    ]
    responsables = Usuario.query.filter_by(rol_id=2).all()
    return render_template(
        "atenciones/diagnosticos/form.html",
        diagnostico=diagnostico,
        atencion=atencion,
        enfermedades=enfermedades,
        responsables=responsables,
        solo_lectura=True,
    )


@diagnosticos_bp.route("/<int:diagnostico_id>/edit", methods=["GET", "POST"])
@personal_medico_requerido
def editar_diagnostico(atencion_id, diagnostico_id):
    from app.models.atencion_medica import AtencionMedica
    atencion = AtencionMedica.query.get_or_404(atencion_id)
    diagnostico = Diagnostico.query.filter_by(id=diagnostico_id, atencion_id=atencion_id).first_or_404()
    enfermedades = [
        {
            "id": e.id,
            "nombre": e.nombre,
            "codigo_cie10": e.codigo_cie10,
        }
        for e in Enfermedad.query.all()
    ]
    responsables = Usuario.query.filter_by(rol_id=2).all()

    if request.method == "POST":
        datos = _datos_formulario_diagnostico()

        if not datos["enfermedad_id"]:
            flash("La enfermedad es obligatoria.", "danger")
            return render_template(
                "atenciones/diagnosticos/form.html",
                diagnostico=diagnostico,
                atencion=atencion,
                enfermedades=enfermedades,
                responsables=responsables,
            )

        if not datos["fecha"]:
            flash("La fecha es obligatoria.", "danger")
            return render_template(
                "atenciones/diagnosticos/form.html",
                diagnostico=diagnostico,
                atencion=atencion,
                enfermedades=enfermedades,
                responsables=responsables,
            )

        for campo, valor in datos.items():
            setattr(diagnostico, campo, valor)

        db.session.commit()

        flash("Diagnóstico actualizado correctamente.", "success")
        return redirect(url_for("diagnosticos.listar_diagnosticos", atencion_id=atencion_id))

    return render_template(
        "atenciones/diagnosticos/form.html",
        diagnostico=diagnostico,
        atencion=atencion,
        enfermedades=enfermedades,
        responsables=responsables,
    )


@diagnosticos_bp.route("/<int:diagnostico_id>/delete", methods=["POST"])
@personal_medico_requerido
def eliminar_diagnostico(atencion_id, diagnostico_id):
    from app.models.atencion_medica import AtencionMedica
    AtencionMedica.query.get_or_404(atencion_id)
    diagnostico = Diagnostico.query.filter_by(id=diagnostico_id, atencion_id=atencion_id).first_or_404()

    db.session.delete(diagnostico)
    db.session.commit()

    flash("Diagnóstico eliminado correctamente.", "success")
    return redirect(url_for("diagnosticos.listar_diagnosticos", atencion_id=atencion_id))