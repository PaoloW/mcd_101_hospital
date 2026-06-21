from datetime import datetime

from flask import Blueprint, flash, session, jsonify, redirect, render_template, request, url_for

from app.controllers.auth_controller import personal_medico_requerido, login_requerido
from app.extensions import db
from app.models.atencion_medica import AtencionMedica
from app.models.persona import Persona
from app.models.usuario import Usuario
from app.models.tipo_atencion import TipoAtencion
from app.models.estado_atencion import EstadoAtencion
from app.models.campana_salud import CampanaSalud
from app.models.participante import Participante
from sqlalchemy import or_, cast, String

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
    busqueda = request.args.get("busqueda", "").strip()
    query = AtencionMedica.query.order_by(AtencionMedica.id.desc())
    query = query.join(AtencionMedica.paciente).join(AtencionMedica.tipo_atencion).join(AtencionMedica.estado_atencion)
    if busqueda:
        filtro = or_(
            AtencionMedica.observacion.ilike(f"%{busqueda}%"),
            Persona.nombre_completo.ilike(f"%{busqueda}%"),
            cast(AtencionMedica.fecha_hora, String).ilike(f"%{busqueda}%"),
            TipoAtencion.nombre.ilike(f"%{busqueda}%"),
            EstadoAtencion.nombre.ilike(f"%{busqueda}%"),
        )
        query = query.filter(filtro)
    pagination = query.paginate(page=page, per_page=PER_PAGE, error_out=False)
    return render_template("atenciones/listar.html", pagination=pagination, atenciones=pagination.items, busqueda=busqueda)


@atenciones_bp.route("/create", methods=["GET", "POST"])
@personal_medico_requerido
def guardar_atencion():
    tipos_atenciones = TipoAtencion.query.all()
    estados_atenciones = EstadoAtencion.query.all()
    responsables = Usuario.query.filter_by(rol_id=2).all()
    campanas = CampanaSalud.query.all()

    usuario_rol = session.get("rol_id")
    tipo_presencial = next((t for t in tipos_atenciones if t.nombre.lower() == "presencial"), None)
    tipo_cita_online = next((t for t in tipos_atenciones if t.nombre.lower() == "cita online"), None)
    tipo_campana = next((t for t in tipos_atenciones if t.nombre.lower() == "campaña"), None)

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
                campanas=campanas,
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
                campanas=campanas,
                ahora=datetime.now(),
            )

        tipo_atencion_id = datos.get("tipo_atencion_id")
        campana_id = datos.get("campana_id")

        if campana_id:
            tipo_atencion_id = tipo_campana.id if tipo_campana else tipo_atencion_id
        elif usuario_rol == Usuario.PACIENTE_ROL_ID:
            tipo_atencion_id = tipo_cita_online.id if tipo_cita_online else tipo_atencion_id
        elif usuario_rol in [Usuario.DOCTOR_ROL_ID, Usuario.ENFERMERO_ROL_ID, Usuario.LABORATORISTA_ROL_ID]:
            tipo_atencion_id = tipo_presencial.id if tipo_presencial else tipo_atencion_id

        atencion = AtencionMedica(
            fecha_hora=datos["fecha_hora"],
            estado_atencion_id=datos["estado_atencion_id"],
            paciente_id=datos["paciente_id"],
            responsable_id=datos["responsable_id"],
            tipo_atencion_id=tipo_atencion_id,
            observacion=datos["observacion"],
        )
        db.session.add(atencion)
        db.session.commit()

        if campana_id:
            participante = Participante(
                campana_id=campana_id,
                atencion_id=atencion.id,
                observacion="Atención registrada desde campaña",
            )
            db.session.add(participante)
            db.session.commit()

        flash("Atención registrada correctamente.", "success")
        return redirect(url_for("atenciones.listar_atenciones"))

    return render_template(
        "atenciones/form.html",
        atencion=None,
        tipos=tipos_atenciones,
        estados=estados_atenciones,
        responsables=responsables,
        campanas=campanas,
        ahora=datetime.now(),
    )


@atenciones_bp.route("/<int:atencion_id>/ver")
@personal_medico_requerido
def ver_atencion(atencion_id):
    atencion = AtencionMedica.query.get_or_404(atencion_id)
    tipos_atenciones = TipoAtencion.query.all()
    estados_atenciones = EstadoAtencion.query.all()
    responsables = Usuario.query.filter_by(rol_id=2).all()
    return render_template(
        "atenciones/form.html",
        atencion=atencion,
        tipos=tipos_atenciones,
        estados=estados_atenciones,
        responsables=responsables,
        solo_lectura=True,
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


# --- RUTAS PARA PACIENTES ---

@atenciones_bp.route("/mis-atenciones")
@login_requerido
def listar_mis_atenciones():
    paciente_id = session.get("persona_id")
    if not paciente_id:
        flash("No se encontró el perfil de paciente.", "warning")
        return redirect(url_for("auth.home"))

    page = request.args.get("page", 1, type=int)
    query = AtencionMedica.query.filter_by(paciente_id=paciente_id).order_by(AtencionMedica.fecha_hora.desc())
    pagination = query.paginate(page=page, per_page=PER_PAGE, error_out=False)
    return render_template("atenciones/listar_mis_atenciones.html", atenciones=pagination.items, pagination=pagination)


@atenciones_bp.route("/mis-atenciones/nueva", methods=["GET", "POST"])
@login_requerido
def crear_mi_atencion():
    paciente_id = session.get("persona_id")
    if not paciente_id:
        flash("No se encontró el perfil de paciente.", "warning")
        return redirect(url_for("auth.home"))

    from app.models.persona import Persona
    paciente = Persona.query.get_or_404(paciente_id)
    responsables = Usuario.query.filter_by(rol_id=2).all()

    if request.method == "POST":
        fecha_hora = request.form.get("fecha_hora", "")
        responsable_id = request.form.get("responsable_id", "") or None

        if not fecha_hora:
            flash("La fecha y hora son obligatorias.", "danger")
            return render_template(
                "atenciones/form_paciente.html",
                atencion=None,
                paciente=paciente,
                responsables=responsables,
            )

        tipo_cita_online = next((t for t in TipoAtencion.query.all() if t.nombre.lower() == "cita online"), None)
        estado_reservada = next((e for e in EstadoAtencion.query.all() if e.nombre.lower() == "reservada"), None)

        if not tipo_cita_online:
            flash("Error: No existe el tipo de atención 'cita online'.", "danger")
            return render_template(
                "atenciones/form_paciente.html",
                atencion=None,
                paciente=paciente,
                responsables=responsables,
            )

        if not estado_reservada:
            flash("Error: No existe el estado 'reservada'.", "danger")
            return render_template(
                "atenciones/form_paciente.html",
                atencion=None,
                paciente=paciente,
                responsables=responsables,
            )

        atencion = AtencionMedica(
            fecha_hora=fecha_hora,
            estado_atencion_id=estado_reservada.id,
            paciente_id=paciente_id,
            responsable_id=responsable_id,
            tipo_atencion_id=tipo_cita_online.id,
        )
        db.session.add(atencion)
        db.session.commit()

        flash("Cita registrada correctamente.", "success")
        return redirect(url_for("atenciones.listar_mis_atenciones"))

    return render_template(
        "atenciones/form_paciente.html",
        atencion=None,
        paciente=paciente,
        responsables=responsables,
        ahora=datetime.now(),
    )
