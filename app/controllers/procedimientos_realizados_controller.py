from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.controllers.auth_controller import personal_medico_requerido
from app.extensions import db
from app.models.procedimiento_realizado import ProcedimientoRealizado
from app.models.procedimiento import Procedimiento
from app.models.usuario import Usuario

procedimientos_realizados_bp = Blueprint("procedimientos_realizados", __name__, url_prefix="/atenciones/<int:atencion_id>/procedimientos_realizados")

PER_PAGE = 20


def _datos_formulario_procedimiento_realizado():
    return {
        "procedimiento_id": request.form.get("procedimiento_id", "") or None,
        "atencion_id": request.form.get("atencion_id", "") or None,
        "fecha": request.form.get("fecha", "") or None,
        "observacion": request.form.get("observacion", "") or None,
        "responsable_id": request.form.get("responsable_id", "") or None,
    }


@procedimientos_realizados_bp.route("/")
@personal_medico_requerido
def listar_procedimientos_realizados(atencion_id):
    from app.models.atencion_medica import AtencionMedica
    atencion = AtencionMedica.query.get_or_404(atencion_id)
    page = request.args.get("page", 1, type=int)
    busqueda = request.args.get("busqueda", "").strip()
    query = ProcedimientoRealizado.query.filter_by(atencion_id=atencion_id).order_by(ProcedimientoRealizado.id.desc())
    if busqueda:
        query = query.join(Procedimiento).filter(Procedimiento.nombre.ilike(f"%{busqueda}%"))
    pagination = query.paginate(page=page, per_page=PER_PAGE, error_out=False)
    procedimientos = Procedimiento.query.all()
    return render_template(
        "atenciones/procedimientos_realizados/listar.html",
        pagination=pagination,
        procedimientos_realizados=pagination.items,
        busqueda=busqueda,
        atencion=atencion,
        procedimientos=procedimientos,
    )


@procedimientos_realizados_bp.route("/create", methods=["GET", "POST"])
@personal_medico_requerido
def crear_procedimiento_realizado(atencion_id):
    from app.models.atencion_medica import AtencionMedica
    atencion = AtencionMedica.query.get_or_404(atencion_id)
    procedimientos = [
        {
            "id": p.id,
            "codigo_cpms": p.codigo_cpms,
            "nombre": p.nombre,
            "seccion": p.seccion.nombre,
        }
        for p in Procedimiento.query.all()
    ]
    responsables = Usuario.query.filter_by(rol_id=2).all()

    if request.method == "POST":
        datos = _datos_formulario_procedimiento_realizado()

        if not datos["procedimiento_id"]:
            flash("El procedimiento es obligatorio.", "danger")
            return render_template(
                "atenciones/procedimientos_realizados/form.html",
                procedimiento_realizado=None,
                atencion=atencion,
                procedimientos=procedimientos,
                responsables=responsables,
            )

        if not datos["fecha"]:
            flash("La fecha es obligatoria.", "danger")
            return render_template(
                "atenciones/procedimientos_realizados/form.html",
                procedimiento_realizado=None,
                atencion=atencion,
                procedimientos=procedimientos,
                responsables=responsables,
            )

        if not datos["responsable_id"]:
            flash("El responsable es obligatorio.", "danger")
            return render_template(
                "atenciones/procedimientos_realizados/form.html",
                procedimiento_realizado=None,
                atencion=atencion,
                procedimientos=procedimientos,
                responsables=responsables,
            )

        procedimiento_realizado = ProcedimientoRealizado(atencion_id=atencion_id, **datos)
        db.session.add(procedimiento_realizado)
        db.session.commit()

        flash("Procedimiento registrado correctamente.", "success")
        return redirect(url_for("procedimientos_realizados.listar_procedimientos_realizados", atencion_id=atencion_id))

    return render_template(
        "atenciones/procedimientos_realizados/form.html",
        procedimiento_realizado=None,
        atencion=atencion,
        procedimientos=procedimientos,
        responsables=responsables,
    )


@procedimientos_realizados_bp.route("/<int:procedimiento_id>/ver")
@personal_medico_requerido
def ver_procedimiento_realizado(atencion_id, procedimiento_id):
    from app.models.atencion_medica import AtencionMedica
    atencion = AtencionMedica.query.get_or_404(atencion_id)
    procedimiento_realizado = ProcedimientoRealizado.query.filter_by(id=procedimiento_id, atencion_id=atencion_id).first_or_404()
    procedimientos = Procedimiento.query.all()
    responsables = Usuario.query.filter_by(rol_id=2).all()
    return render_template(
        "atenciones/procedimientos_realizados/form.html",
        procedimiento_realizado=procedimiento_realizado,
        atencion=atencion,
        procedimientos=procedimientos,
        responsables=responsables,
        solo_lectura=True,
    )


@procedimientos_realizados_bp.route("/<int:procedimiento_id>/edit", methods=["GET", "POST"])
@personal_medico_requerido
def editar_procedimiento_realizado(atencion_id, procedimiento_id):
    from app.models.atencion_medica import AtencionMedica
    atencion = AtencionMedica.query.get_or_404(atencion_id)
    procedimiento_realizado = ProcedimientoRealizado.query.filter_by(id=procedimiento_id, atencion_id=atencion_id).first_or_404()
    procedimientos = Procedimiento.query.all()
    responsables = Usuario.query.filter_by(rol_id=2).all()

    if request.method == "POST":
        datos = _datos_formulario_procedimiento_realizado()

        if not datos["procedimiento_id"]:
            flash("El procedimiento es obligatorio.", "danger")
            return render_template(
                "atenciones/procedimientos_realizados/form.html",
                procedimiento_realizado=procedimiento_realizado,
                atencion=atencion,
                procedimientos=procedimientos,
                responsables=responsables,
            )

        if not datos["fecha"]:
            flash("La fecha es obligatoria.", "danger")
            return render_template(
                "atenciones/procedimientos_realizados/form.html",
                procedimiento_realizado=procedimiento_realizado,
                atencion=atencion,
                procedimientos=procedimientos,
                responsables=responsables,
            )

        for campo, valor in datos.items():
            setattr(procedimiento_realizado, campo, valor)

        db.session.commit()

        flash("Procedimiento actualizado correctamente.", "success")
        return redirect(url_for("procedimientos_realizados.listar_procedimientos_realizados", atencion_id=atencion_id))

    return render_template(
        "atenciones/procedimientos_realizados/form.html",
        procedimiento_realizado=procedimiento_realizado,
        atencion=atencion,
        procedimientos=procedimientos,
        responsables=responsables,
    )


@procedimientos_realizados_bp.route("/<int:procedimiento_id>/delete", methods=["POST"])
@personal_medico_requerido
def eliminar_procedimiento_realizado(atencion_id, procedimiento_id):
    from app.models.atencion_medica import AtencionMedica
    AtencionMedica.query.get_or_404(atencion_id)
    procedimiento_realizado = ProcedimientoRealizado.query.filter_by(id=procedimiento_id, atencion_id=atencion_id).first_or_404()

    db.session.delete(procedimiento_realizado)
    db.session.commit()

    flash("Procedimiento eliminado correctamente.", "success")
    return redirect(url_for("procedimientos_realizados.listar_procedimientos_realizados", atencion_id=atencion_id))