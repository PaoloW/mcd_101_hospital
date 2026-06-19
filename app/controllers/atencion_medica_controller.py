from datetime import datetime

from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for

from app.controllers.auth_controller import personal_medico_requerido
from app.extensions import db
from app.models.atencion_medica import AtencionMedica
from app.models.persona import Persona
from app.models.usuario import Usuario
from app.models.tipo_atencion import TipoAtencion
from app.models.estado_atencion import EstadoAtencion

atenciones_bp = Blueprint("atenciones", __name__, url_prefix="/atenciones")

PER_PAGE = 20


def _datos_formulario_atencion():
    return {
        "fecha_hora": request.form.get("fecha_hora", ""),
        "estado_atencion_id": request.form.get("estado_atencion_id", "") or None,
        "paciente_id": request.form.get("paciente_id", "") or None,
        "responsable_id": request.form.get("responsable_id", "") or None,
        "tipo_atencion_id": request.form.get("tipo_atencion_id", "") or None,
        "observacion": request.form.get("observacion", "") or None,
    }


@atenciones_bp.route("/")
@personal_medico_requerido
def listar_atenciones():
    page = request.args.get("page", 1, type=int)
    query = AtencionMedica.query.order_by(AtencionMedica.id.desc())
    pagination = query.paginate(page=page, per_page=PER_PAGE, error_out=False)
    return render_template("atenciones/listar.html", pagination=pagination, atenciones=pagination.items)


@atenciones_bp.route("/create", methods=["GET", "POST"])
@personal_medico_requerido
def guardar_atencion():
    tipos_atenciones = TipoAtencion.query.all()
    estados_atenciones = EstadoAtencion.query.all()
    responsables = Usuario.query.filter_by(rol_id=2).all()

    if request.method == "POST":
        datos = _datos_formulario_atencion()

        if not datos["fecha_hora"]:
            flash("La fecha es obligatoria.", "danger")
            return render_template(
                "atenciones/form.html",
                atencion=None,
                tipos=tipos_atenciones,
                estados=estados_atenciones,
                responsables=responsables,
                ahora=datetime.now(),
            )

        if not datos["paciente_id"]:
            flash("El paciente es obligatorio.", "danger")
            return render_template(
                "atenciones/form.html",
                atencion=None,
                tipos=tipos_atenciones,
                estados=estados_atenciones,
                responsables=responsables,
                ahora=datetime.now(),
            )

        atencion = AtencionMedica(**datos)
        db.session.add(atencion)
        db.session.commit()

        flash("Atención registrada correctamente.", "success")
        return redirect(url_for("atenciones.listar_atenciones"))

    return render_template(
        "atenciones/form.html",
        atencion=None,
        tipos=tipos_atenciones,
        estados=estados_atenciones,
        responsables=responsables,
        ahora=datetime.now(),
    )


@atenciones_bp.route("/<int:atencion_id>/edit", methods=["GET", "POST"])
@personal_medico_requerido
def actualizar_atencion(atencion_id):
    atencion = AtencionMedica.query.get_or_404(atencion_id)

    tipos_atenciones = TipoAtencion.query.all()
    estados_atenciones = EstadoAtencion.query.all()
    responsables = Usuario.query.filter_by(rol_id=2).all()

    if request.method == "POST":
        datos = _datos_formulario_atencion()

        if not datos["fecha_hora"]:
            flash("La fecha es obligatoria.", "danger")
            return render_template(
                "atenciones/form.html",
                atencion=atencion,
                tipos=tipos_atenciones,
                estados=estados_atenciones,
                responsables=responsables,
                ahora=datetime.now(),
            )

        if not datos["paciente_id"]:
            flash("El paciente es obligatorio.", "danger")
            return render_template(
                "atenciones/form.html",
                atencion=atencion,
                tipos=tipos_atenciones,
                estados=estados_atenciones,
                responsables=responsables,
                ahora=datetime.now(),
            )

        for campo, valor in datos.items():
            setattr(atencion, campo, valor)

        db.session.commit()

        flash("Atención actualizada correctamente.", "success")
        return redirect(url_for("atenciones.listar_atenciones"))

    return render_template(
        "atenciones/form.html",
        atencion=atencion,
        tipos=tipos_atenciones,
        estados=estados_atenciones,
        responsables=responsables,
        ahora=datetime.now(),
    )


@atenciones_bp.route("/<int:atencion_id>/delete", methods=["POST"])
@personal_medico_requerido
def eliminar_atencion(atencion_id):
    atencion = AtencionMedica.query.get_or_404(atencion_id)

    db.session.delete(atencion)
    db.session.commit()

    flash("Atención eliminada correctamente.", "success")
    return redirect(url_for("atenciones.listar_atenciones"))