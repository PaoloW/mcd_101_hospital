from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.controllers.auth_controller import personal_medico_requerido
from app.extensions import db
from app.models.analisis import Analisis
from app.models.parametro import Parametro
from app.models.usuario import Usuario

analisis_bp = Blueprint("analisis", __name__, url_prefix="/atenciones/<int:atencion_id>/analisis")

PER_PAGE = 20


def _datos_formulario_analisis():
    return {
        "parametro_id": request.form.get("parametro_id", "") or None,
        "valor_resultado": request.form.get("valor_resultado", "") or None,
        "observacion": request.form.get("observacion", "") or None,
        "fechahora_muestra": request.form.get("fechahora_muestra", "") or None,
        "fechahora_analisis": request.form.get("fechahora_analisis", "") or None,
        "responsable_id": request.form.get("responsable_id", "") or None,
    }


@analisis_bp.route("/")
@personal_medico_requerido
def listar_analisis(atencion_id):
    from app.models.atencion_medica import AtencionMedica
    atencion = AtencionMedica.query.get_or_404(atencion_id)
    page = request.args.get("page", 1, type=int)
    busqueda = request.args.get("busqueda", "").strip()
    query = Analisis.query.filter_by(atencion_id=atencion_id).order_by(Analisis.id.desc())
    if busqueda:
        query = query.filter(Analisis.observacion.ilike(f"%{busqueda}%"))
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
    parametros = [
        {
            "id": p.id,
            "tipo_parametro": p.tipo_parametro.nombre if p.tipo_parametro else "",
            "nombre": p.nombre,
            "unidad_medida": p.unidad_medida or "",
        }
        for p in Parametro.query.all()
    ]
    responsables = Usuario.query.filter_by(rol_id=2).all()

    if request.method == "POST":
        datos = _datos_formulario_analisis()

        if not datos["parametro_id"]:
            flash("El parámetro es obligatorio.", "danger")
            return render_template(
                "atenciones/analisis/form.html", analisis=None, atencion=atencion, parametros=parametros, responsables=responsables
            )

        if not datos["fechahora_muestra"]:
            flash("La fecha y hora de la muestra es obligatoria.", "danger")
            return render_template(
                "atenciones/analisis/form.html", analisis=None, atencion=atencion, parametros=parametros, responsables=responsables
            )

        if not datos["fechahora_analisis"]:
            flash("La fecha y hora del análisis es obligatoria.", "danger")
            return render_template(
                "atenciones/analisis/form.html", analisis=None, atencion=atencion, parametros=parametros, responsables=responsables
            )

        if not datos["responsable_id"]:
            flash("El responsable es obligatorio.", "danger")
            return render_template(
                "atenciones/analisis/form.html", analisis=None, atencion=atencion, parametros=parametros, responsables=responsables
            )

        analisis = Analisis(atencion_id=atencion_id, **datos)
        db.session.add(analisis)
        db.session.commit()

        flash("Análisis registrado correctamente.", "success")
        return redirect(url_for("analisis.listar_analisis", atencion_id=atencion_id))

    return render_template(
        "atenciones/analisis/form.html", analisis=None, atencion=atencion, parametros=parametros, responsables=responsables
    )


@analisis_bp.route("/<int:analisis_id>/ver")
@personal_medico_requerido
def ver_analisis(atencion_id, analisis_id):
    from app.models.atencion_medica import AtencionMedica
    atencion = AtencionMedica.query.get_or_404(atencion_id)
    analisis = Analisis.query.filter_by(id=analisis_id, atencion_id=atencion_id).first_or_404()
    parametros = Parametro.query.all()
    responsables = Usuario.query.filter_by(rol_id=2).all()
    return render_template(
        "atenciones/analisis/form.html", analisis=analisis, atencion=atencion, parametros=parametros, responsables=responsables, solo_lectura=True
    )


@analisis_bp.route("/<int:analisis_id>/edit", methods=["GET", "POST"])
@personal_medico_requerido
def editar_analisis(atencion_id, analisis_id):
    from app.models.atencion_medica import AtencionMedica
    atencion = AtencionMedica.query.get_or_404(atencion_id)
    analisis = Analisis.query.filter_by(id=analisis_id, atencion_id=atencion_id).first_or_404()
    parametros = Parametro.query.all()
    responsables = Usuario.query.filter_by(rol_id=2).all()

    if request.method == "POST":
        datos = _datos_formulario_analisis()

        if not datos["parametro_id"]:
            flash("El parámetro es obligatorio.", "danger")
            return render_template(
                "atenciones/analisis/form.html", analisis=analisis, atencion=atencion, parametros=parametros, responsables=responsables
            )

        if not datos["fechahora_muestra"]:
            flash("La fecha y hora de la muestra es obligatoria.", "danger")
            return render_template(
                "atenciones/analisis/form.html", analisis=analisis, atencion=atencion, parametros=parametros, responsables=responsables
            )

        if not datos["fechahora_analisis"]:
            flash("La fecha y hora del análisis es obligatoria.", "danger")
            return render_template(
                "atenciones/analisis/form.html", analisis=analisis, atencion=atencion, parametros=parametros, responsables=responsables
            )

        if not datos["responsable_id"]:
            flash("El responsable es obligatorio.", "danger")
            return render_template(
                "atenciones/analisis/form.html", analisis=analisis, atencion=atencion, parametros=parametros, responsables=responsables
            )

        for campo, valor in datos.items():
            setattr(analisis, campo, valor)

        db.session.commit()

        flash("Análisis actualizado correctamente.", "success")
        return redirect(url_for("analisis.listar_analisis", atencion_id=atencion_id))

    return render_template(
        "atenciones/analisis/form.html", analisis=analisis, atencion=atencion, parametros=parametros, responsables=responsables
    )


@analisis_bp.route("/<int:analisis_id>/delete", methods=["POST"])
@personal_medico_requerido
def eliminar_analisis(atencion_id, analisis_id):
    from app.models.atencion_medica import AtencionMedica
    AtencionMedica.query.get_or_404(atencion_id)
    analisis = Analisis.query.filter_by(id=analisis_id, atencion_id=atencion_id).first_or_404()

    db.session.delete(analisis)
    db.session.commit()

    flash("Análisis eliminado correctamente.", "success")
    return redirect(url_for("analisis.listar_analisis", atencion_id=atencion_id))