from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.controllers.auth_controller import personal_medico_requerido
from app.extensions import db
from app.models.atencion_medica import AtencionMedica
from app.models.campana_salud import CampanaSalud
from app.models.participante import Participante
from app.models.tipo_atencion import TipoAtencion
from app.models.estado_atencion import EstadoAtencion
from app.models.usuario import Usuario

campanas_bp = Blueprint("campanas", __name__, url_prefix="/campanas")

PER_PAGE = 20


@campanas_bp.route("/")
@personal_medico_requerido
def listar_campanas():
    page = request.args.get("page", 1, type=int)
    busqueda = request.args.get("busqueda", "").strip()
    query = CampanaSalud.query.order_by(CampanaSalud.desde.desc())
    if busqueda:
        query = query.filter(CampanaSalud.nombre.ilike(f"%{busqueda}%"))
    pagination = query.paginate(page=page, per_page=PER_PAGE, error_out=False)
    return render_template("campanas/listar.html", pagination=pagination, campanas=pagination.items, busqueda=busqueda)


@campanas_bp.route("/create", methods=["GET", "POST"])
@personal_medico_requerido
def crear_campana():
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        objetivo = request.form.get("objetivo", "")
        desde = request.form.get("desde", "")
        hasta = request.form.get("hasta", "")

        if not nombre:
            flash("El nombre de la campaña es obligatorio.", "danger")
            return render_template("campanas/form.html", campana=None)

        if not desde or not hasta:
            flash("Las fechas son obligatorias.", "danger")
            return render_template("campanas/form.html", campana=None)

        campana = CampanaSalud(
            nombre=nombre,
            objetivo=objetivo,
            desde=desde,
            hasta=hasta,
        )
        db.session.add(campana)
        db.session.commit()

        flash("Campaña registrada correctamente.", "success")
        return redirect(url_for("campanas.listar_campanas"))

    return render_template("campanas/form.html", campana=None)


@campanas_bp.route("/<int:campana_id>/ver")
@personal_medico_requerido
def ver_campana(campana_id):
    campana = CampanaSalud.query.get_or_404(campana_id)
    return render_template("campanas/form.html", campana=campana, solo_lectura=True)


@campanas_bp.route("/<int:campana_id>/edit", methods=["GET", "POST"])
@personal_medico_requerido
def editar_campana(campana_id):
    campana = CampanaSalud.query.get_or_404(campana_id)

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        objetivo = request.form.get("objetivo", "")
        desde = request.form.get("desde", "")
        hasta = request.form.get("hasta", "")

        if not nombre:
            flash("El nombre de la campaña es obligatorio.", "danger")
            return render_template("campanas/form.html", campana=campana)

        if not desde or not hasta:
            flash("Las fechas son obligatorias.", "danger")
            return render_template("campanas/form.html", campana=campana)

        campana.nombre = nombre
        campana.objetivo = objetivo
        campana.desde = desde
        campana.hasta = hasta

        db.session.commit()

        flash("Campaña actualizada correctamente.", "success")
        return redirect(url_for("campanas.listar_campanas"))

    return render_template("campanas/form.html", campana=campana)


@campanas_bp.route("/<int:campana_id>/delete", methods=["POST"])
@personal_medico_requerido
def eliminar_campana(campana_id):
    campana = CampanaSalud.query.get_or_404(campana_id)

    db.session.delete(campana)
    db.session.commit()

    flash("Campaña eliminada correctamente.", "success")
    return redirect(url_for("campanas.listar_campanas"))


@campanas_bp.route("/<int:campana_id>/atenciones")
@personal_medico_requerido
def listar_atenciones_campana(campana_id):
    campana = CampanaSalud.query.get_or_404(campana_id)
    page = request.args.get("page", 1, type=int)
    query = (
        AtencionMedica.query.join(Participante)
        .filter(Participante.campana_id == campana_id)
        .order_by(AtencionMedica.fecha_hora.desc())
    )
    pagination = query.paginate(page=page, per_page=20, error_out=False)
    return render_template(
        "campanas/atenciones.html",
        campana=campana,
        atenciones=pagination.items,
        pagination=pagination,
    )


@campanas_bp.route("/<int:campana_id>/atenciones/create", methods=["GET", "POST"])
@personal_medico_requerido
def crear_atencion_campana(campana_id):
    campana = CampanaSalud.query.get_or_404(campana_id)
    ahora = datetime.now()

    if ahora.date() < campana.desde or ahora.date() > campana.hasta:
        flash("Solo puede registrar atenciones durante el periodo de la campaña.", "warning")
        return redirect(url_for("campanas.ver_campana", campana_id=campana.id))

    if request.method == "POST":
        fecha_hora = request.form.get("fecha_hora", "")
        paciente_id = request.form.get("paciente_id", "") or None
        responsable_id = request.form.get("responsable_id", "") or None
        observacion = request.form.get("observacion", "")

        if not fecha_hora:
            flash("La fecha y hora son obligatorias.", "danger")
            return render_template(
                "campanas/atencion_form.html",
                campana=campana,
                ahora=ahora,
                responsables=Usuario.query.filter_by(rol_id=2).all(),
            )

        if not paciente_id:
            flash("El paciente es obligatorio.", "danger")
            return render_template(
                "campanas/atencion_form.html",
                campana=campana,
                ahora=ahora,
                responsables=Usuario.query.filter_by(rol_id=2).all(),
            )

        tipo_campana = next(
            (t for t in TipoAtencion.query.all() if t.nombre.lower() == "campaña"), None
        )
        estado_atencion = next(
            (e for e in EstadoAtencion.query.all() if e.nombre.lower() == "reservada"),
            None,
        )

        if not tipo_campana or not estado_atencion:
            flash(
                "Error: No existe el tipo de atención 'campaña' o estado 'reservada'.",
                "danger",
            )
            return render_template(
                "campanas/atencion_form.html",
                campana=campana,
                ahora=ahora,
                responsables=Usuario.query.filter_by(rol_id=2).all(),
            )

        atencion = AtencionMedica(
            fecha_hora=fecha_hora,
            estado_atencion_id=estado_atencion.id,
            paciente_id=paciente_id,
            responsable_id=responsable_id,
            tipo_atencion_id=tipo_campana.id,
            observacion=observacion,
        )
        db.session.add(atencion)
        db.session.commit()

        participante = Participante(
            campana_id=campana.id,
            atencion_id=atencion.id,
            observacion="Atención registrada desde campaña",
        )
        db.session.add(participante)
        db.session.commit()

        flash("Atención registrada correctamente.", "success")
        return redirect(url_for("campanas.listar_atenciones_campana", campana_id=campana.id))

    responsables = Usuario.query.filter_by(rol_id=2).all()
    return render_template(
        "campanas/atencion_form.html",
        campana=campana,
        ahora=ahora,
        responsables=responsables,
    )
