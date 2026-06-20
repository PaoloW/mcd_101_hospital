from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.controllers.auth_controller import personal_medico_requerido
from app.extensions import db
from app.models.analisis import Analisis
from app.models.diagnostico import Diagnostico
from app.models.prescripcion import Prescripcion
from app.models.procedimiento_realizado import ProcedimientoRealizado
from app.models.parametro import Parametro
from app.models.enfermedad import Enfermedad
from app.models.medicamento import Medicamento
from app.models.procedimiento import Procedimiento

analisis_bp = Blueprint("analisis", __name__, url_prefix="/atenciones/<int:atencion_id>/analisis")
diagnosticos_bp = Blueprint("diagnosticos", __name__, url_prefix="/atenciones/<int:atencion_id>/diagnosticos")
prescripciones_bp = Blueprint("prescripciones", __name__, url_prefix="/atenciones/<int:atencion_id>/prescripciones")
procedimientos_realizados_bp = Blueprint("procedimientos_realizados", __name__, url_prefix="/atenciones/<int:atencion_id>/procedimientos_realizados")

PER_PAGE = 20


def _datos_formulario_analisis():
    return {
        "parametro_id": request.form.get("parametro_id", "") or None,
        "resultado": request.form.get("resultado", "").strip(),
        "observacion": request.form.get("observacion", "") or None,
    }


def _datos_formulario_diagnostico():
    return {
        "enfermedad_id": request.form.get("enfermedad_id", "") or None,
        "observacion": request.form.get("observacion", "") or None,
    }


def _datos_formulario_prescripcion():
    return {
        "medicamento_id": request.form.get("medicamento_id", "") or None,
        "cantidad": request.form.get("cantidad", "").strip(),
        "frecuencia": request.form.get("frecuencia", "").strip(),
        "via_administracion": request.form.get("via_administracion", "") or None,
        "observacion": request.form.get("observacion", "") or None,
    }


def _datos_formulario_procedimiento_realizado():
    return {
        "procedimiento_id": request.form.get("procedimiento_id", "") or None,
        "resultado": request.form.get("resultado", "").strip(),
        "observacion": request.form.get("observacion", "") or None,
    }


@analisis_bp.route("/")
@personal_medico_requerido
def listar_analisis(atencion_id):
    from app.models.atencion_medica import AtencionMedica
    atencion = AtencionMedica.query.get_or_404(atencion_id)
    page = request.args.get("page", 1, type=int)
    busqueda = request.args.get("busqueda", "").strip()
    query = Analisis.query.filter_by(atencion_medica_id=atencion_id).order_by(Analisis.id.desc())
    if busqueda:
        query = query.filter(Analisis.resultado.ilike(f"%{busqueda}%"))
    pagination = query.paginate(page=page, per_page=PER_PAGE, error_out=False)
    parametros = Parametro.query.all()
    return render_template(
        "atenciones/analisis/listar.html",
        pagination=pagination,
        analisis=pagination.items,
        busqueda=busqueda,
        atencion=atencion,
        parametros=parametros,
    )


@analisis_bp.route("/create", methods=["GET", "POST"])
@personal_medico_requerido
def crear_analisis(atencion_id):
    from app.models.atencion_medica import AtencionMedica
    atencion = AtencionMedica.query.get_or_404(atencion_id)
    parametros = Parametro.query.all()

    if request.method == "POST":
        datos = _datos_formulario_analisis()

        if not datos["parametro_id"]:
            flash("El parámetro es obligatorio.", "danger")
            return render_template(
                "atenciones/analisis/form.html", analisis=None, atencion=atencion, parametros=parametros
            )

        if not datos["resultado"]:
            flash("El resultado es obligatorio.", "danger")
            return render_template(
                "atenciones/analisis/form.html", analisis=None, atencion=atencion, parametros=parametros
            )

        analisis = Analisis(atencion_medica_id=atencion_id, **datos)
        db.session.add(analisis)
        db.session.commit()

        flash("Análisis registrado correctamente.", "success")
        return redirect(url_for("analisis.listar_analisis", atencion_id=atencion_id))

    return render_template(
        "atenciones/analisis/form.html", analisis=None, atencion=atencion, parametros=parametros
    )


@analisis_bp.route("/<int:analisis_id>/ver")
@personal_medico_requerido
def ver_analisis(atencion_id, analisis_id):
    from app.models.atencion_medica import AtencionMedica
    atencion = AtencionMedica.query.get_or_404(atencion_id)
    analisis = Analisis.query.filter_by(id=analisis_id, atencion_medica_id=atencion_id).first_or_404()
    parametros = Parametro.query.all()
    return render_template(
        "atenciones/analisis/form.html", analisis=analisis, atencion=atencion, parametros=parametros, solo_lectura=True
    )


@analisis_bp.route("/<int:analisis_id>/edit", methods=["GET", "POST"])
@personal_medico_requerido
def editar_analisis(atencion_id, analisis_id):
    from app.models.atencion_medica import AtencionMedica
    atencion = AtencionMedica.query.get_or_404(atencion_id)
    analisis = Analisis.query.filter_by(id=analisis_id, atencion_medica_id=atencion_id).first_or_404()
    parametros = Parametro.query.all()

    if request.method == "POST":
        datos = _datos_formulario_analisis()

        if not datos["parametro_id"]:
            flash("El parámetro es obligatorio.", "danger")
            return render_template(
                "atenciones/analisis/form.html", analisis=analisis, atencion=atencion, parametros=parametros
            )

        if not datos["resultado"]:
            flash("El resultado es obligatorio.", "danger")
            return render_template(
                "atenciones/analisis/form.html", analisis=analisis, atencion=atencion, parametros=parametros
            )

        for campo, valor in datos.items():
            setattr(analisis, campo, valor)

        db.session.commit()

        flash("Análisis actualizado correctamente.", "success")
        return redirect(url_for("analisis.listar_analisis", atencion_id=atencion_id))

    return render_template(
        "atenciones/analisis/form.html", analisis=analisis, atencion=atencion, parametros=parametros
    )


@analisis_bp.route("/<int:analisis_id>/delete", methods=["POST"])
@personal_medico_requerido
def eliminar_analisis(atencion_id, analisis_id):
    from app.models.atencion_medica import AtencionMedica
    AtencionMedica.query.get_or_404(atencion_id)
    analisis = Analisis.query.filter_by(id=analisis_id, atencion_medica_id=atencion_id).first_or_404()

    db.session.delete(analisis)
    db.session.commit()

    flash("Análisis eliminado correctamente.", "success")
    return redirect(url_for("analisis.listar_analisis", atencion_id=atencion_id))


# --- DIAGNOSTICOS ---

@diagnosticos_bp.route("/")
@personal_medico_requerido
def listar_diagnosticos(atencion_id):
    from app.models.atencion_medica import AtencionMedica
    atencion = AtencionMedica.query.get_or_404(atencion_id)
    page = request.args.get("page", 1, type=int)
    busqueda = request.args.get("busqueda", "").strip()
    query = Diagnostico.query.filter_by(atencion_medica_id=atencion_id).order_by(Diagnostico.id.desc())
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
    enfermedades = Enfermedad.query.all()

    if request.method == "POST":
        datos = _datos_formulario_diagnostico()

        if not datos["enfermedad_id"]:
            flash("La enfermedad es obligatoria.", "danger")
            return render_template(
                "atenciones/diagnosticos/form.html", diagnostico=None, atencion=atencion, enfermedades=enfermedades
            )

        diagnostico = Diagnostico(atencion_medica_id=atencion_id, **datos)
        db.session.add(diagnostico)
        db.session.commit()

        flash("Diagnóstico registrado correctamente.", "success")
        return redirect(url_for("diagnosticos.listar_diagnosticos", atencion_id=atencion_id))

    return render_template(
        "atenciones/diagnosticos/form.html", diagnostico=None, atencion=atencion, enfermedades=enfermedades
    )


@diagnosticos_bp.route("/<int:diagnostico_id>/ver")
@personal_medico_requerido
def ver_diagnostico(atencion_id, diagnostico_id):
    from app.models.atencion_medica import AtencionMedica
    atencion = AtencionMedica.query.get_or_404(atencion_id)
    diagnostico = Diagnostico.query.filter_by(id=diagnostico_id, atencion_medica_id=atencion_id).first_or_404()
    enfermedades = Enfermedad.query.all()
    return render_template(
        "atenciones/diagnosticos/form.html",
        diagnostico=diagnostico,
        atencion=atencion,
        enfermedades=enfermedades,
        solo_lectura=True,
    )


@diagnosticos_bp.route("/<int:diagnostico_id>/edit", methods=["GET", "POST"])
@personal_medico_requerido
def editar_diagnostico(atencion_id, diagnostico_id):
    from app.models.atencion_medica import AtencionMedica
    atencion = AtencionMedica.query.get_or_404(atencion_id)
    diagnostico = Diagnostico.query.filter_by(id=diagnostico_id, atencion_medica_id=atencion_id).first_or_404()
    enfermedades = Enfermedad.query.all()

    if request.method == "POST":
        datos = _datos_formulario_diagnostico()

        if not datos["enfermedad_id"]:
            flash("La enfermedad es obligatoria.", "danger")
            return render_template(
                "atenciones/diagnosticos/form.html",
                diagnostico=diagnostico,
                atencion=atencion,
                enfermedades=enfermedades,
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
    )


@diagnosticos_bp.route("/<int:diagnostico_id>/delete", methods=["POST"])
@personal_medico_requerido
def eliminar_diagnostico(atencion_id, diagnostico_id):
    from app.models.atencion_medica import AtencionMedica
    AtencionMedica.query.get_or_404(atencion_id)
    diagnostico = Diagnostico.query.filter_by(id=diagnostico_id, atencion_medica_id=atencion_id).first_or_404()

    db.session.delete(diagnostico)
    db.session.commit()

    flash("Diagnóstico eliminado correctamente.", "success")
    return redirect(url_for("diagnosticos.listar_diagnosticos", atencion_id=atencion_id))


# --- PRESCRIPCIONES ---

@prescripciones_bp.route("/")
@personal_medico_requerido
def listar_prescripciones(atencion_id):
    from app.models.atencion_medica import AtencionMedica
    atencion = AtencionMedica.query.get_or_404(atencion_id)
    page = request.args.get("page", 1, type=int)
    busqueda = request.args.get("busqueda", "").strip()
    query = Prescripcion.query.filter_by(atencion_medica_id=atencion_id).order_by(Prescripcion.id.desc())
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
    medicamentos = Medicamento.query.all()

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

        if not datos["cantidad"]:
            flash("La cantidad es obligatoria.", "danger")
            return render_template(
                "atenciones/prescripciones/form.html",
                prescripcion=None,
                atencion=atencion,
                medicamentos=medicamentos,
            )

        if not datos["frecuencia"]:
            flash("La frecuencia es obligatoria.", "danger")
            return render_template(
                "atenciones/prescripciones/form.html",
                prescripcion=None,
                atencion=atencion,
                medicamentos=medicamentos,
            )

        prescripcion = Prescripcion(atencion_medica_id=atencion_id, **datos)
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
    prescripcion = Prescripcion.query.filter_by(id=prescripcion_id, atencion_medica_id=atencion_id).first_or_404()
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
    prescripcion = Prescripcion.query.filter_by(id=prescripcion_id, atencion_medica_id=atencion_id).first_or_404()
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

        if not datos["cantidad"]:
            flash("La cantidad es obligatoria.", "danger")
            return render_template(
                "atenciones/prescripciones/form.html",
                prescripcion=prescripcion,
                atencion=atencion,
                medicamentos=medicamentos,
            )

        if not datos["frecuencia"]:
            flash("La frecuencia es obligatoria.", "danger")
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
    prescripcion = Prescripcion.query.filter_by(id=prescripcion_id, atencion_medica_id=atencion_id).first_or_404()

    db.session.delete(prescripcion)
    db.session.commit()

    flash("Prescripción eliminada correctamente.", "success")
    return redirect(url_for("prescripciones.listar_prescripciones", atencion_id=atencion_id))


# --- PROCEDIMIENTOS REALIZADOS ---

@procedimientos_realizados_bp.route("/")
@personal_medico_requerido
def listar_procedimientos_realizados(atencion_id):
    from app.models.atencion_medica import AtencionMedica
    atencion = AtencionMedica.query.get_or_404(atencion_id)
    page = request.args.get("page", 1, type=int)
    busqueda = request.args.get("busqueda", "").strip()
    query = ProcedimientoRealizado.query.filter_by(atencion_medica_id=atencion_id).order_by(ProcedimientoRealizado.id.desc())
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
    procedimientos = Procedimiento.query.all()

    if request.method == "POST":
        datos = _datos_formulario_procedimiento_realizado()

        if not datos["procedimiento_id"]:
            flash("El procedimiento es obligatorio.", "danger")
            return render_template(
                "atenciones/procedimientos_realizados/form.html",
                procedimiento_realizado=None,
                atencion=atencion,
                procedimientos=procedimientos,
            )

        if not datos["resultado"]:
            flash("El resultado es obligatorio.", "danger")
            return render_template(
                "atenciones/procedimientos_realizados/form.html",
                procedimiento_realizado=None,
                atencion=atencion,
                procedimientos=procedimientos,
            )

        procedimiento_realizado = ProcedimientoRealizado(atencion_medica_id=atencion_id, **datos)
        db.session.add(procedimiento_realizado)
        db.session.commit()

        flash("Procedimiento registrado correctamente.", "success")
        return redirect(url_for("procedimientos_realizados.listar_procedimientos_realizados", atencion_id=atencion_id))

    return render_template(
        "atenciones/procedimientos_realizados/form.html",
        procedimiento_realizado=None,
        atencion=atencion,
        procedimientos=procedimientos,
    )


@procedimientos_realizados_bp.route("/<int:procedimiento_id>/ver")
@personal_medico_requerido
def ver_procedimiento_realizado(atencion_id, procedimiento_id):
    from app.models.atencion_medica import AtencionMedica
    atencion = AtencionMedica.query.get_or_404(atencion_id)
    procedimiento_realizado = ProcedimientoRealizado.query.filter_by(id=procedimiento_id, atencion_medica_id=atencion_id).first_or_404()
    procedimientos = Procedimiento.query.all()
    return render_template(
        "atenciones/procedimientos_realizados/form.html",
        procedimiento_realizado=procedimiento_realizado,
        atencion=atencion,
        procedimientos=procedimientos,
        solo_lectura=True,
    )


@procedimientos_realizados_bp.route("/<int:procedimiento_id>/edit", methods=["GET", "POST"])
@personal_medico_requerido
def editar_procedimiento_realizado(atencion_id, procedimiento_id):
    from app.models.atencion_medica import AtencionMedica
    atencion = AtencionMedica.query.get_or_404(atencion_id)
    procedimiento_realizado = ProcedimientoRealizado.query.filter_by(id=procedimiento_id, atencion_medica_id=atencion_id).first_or_404()
    procedimientos = Procedimiento.query.all()

    if request.method == "POST":
        datos = _datos_formulario_procedimiento_realizado()

        if not datos["procedimiento_id"]:
            flash("El procedimiento es obligatorio.", "danger")
            return render_template(
                "atenciones/procedimientos_realizados/form.html",
                procedimiento_realizado=procedimiento_realizado,
                atencion=atencion,
                procedimientos=procedimientos,
            )

        if not datos["resultado"]:
            flash("El resultado es obligatorio.", "danger")
            return render_template(
                "atenciones/procedimientos_realizados/form.html",
                procedimiento_realizado=procedimiento_realizado,
                atencion=atencion,
                procedimientos=procedimientos,
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
    )


@procedimientos_realizados_bp.route("/<int:procedimiento_id>/delete", methods=["POST"])
@personal_medico_requerido
def eliminar_procedimiento_realizado(atencion_id, procedimiento_id):
    from app.models.atencion_medica import AtencionMedica
    AtencionMedica.query.get_or_404(atencion_id)
    procedimiento_realizado = ProcedimientoRealizado.query.filter_by(id=procedimiento_id, atencion_medica_id=atencion_id).first_or_404()

    db.session.delete(procedimiento_realizado)
    db.session.commit()

    flash("Procedimiento eliminado correctamente.", "success")
    return redirect(url_for("procedimientos_realizados.listar_procedimientos_realizados", atencion_id=atencion_id))