from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.controllers.auth_controller import personal_medico_requerido
from app.extensions import db
from app.models.campana_salud import CampanaSalud

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