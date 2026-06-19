from flask import Blueprint, flash, redirect, render_template, request, url_for
from sqlalchemy import text

from app.controllers.auth_controller import personal_requerido
from app.extensions import db
from app.models.medicamento import Medicamento

medicamentos_bp = Blueprint("medicamentos", __name__, url_prefix="/medicamentos")

PER_PAGE = 20


def _datos_formulario_medicamento():
    return {
        "codigo": request.form.get("codigo", "").strip(),
        "denominacion": request.form.get("denominacion", "").strip() or None,
        "especificaciones_tecnicas": request.form.get("especificaciones_tecnicas", "").strip() or None,
        "unidad_medida": request.form.get("unidad_medida", "").strip() or None,
    }


@medicamentos_bp.route("/")
@personal_requerido
def listar_medicamentos():
    page = request.args.get("page", 1, type=int)
    busqueda = request.args.get("busqueda", "").strip()
    query = Medicamento.query.order_by(Medicamento.id.desc())
    if busqueda:
        filtro = (
            Medicamento.codigo.ilike(f"%{busqueda}%")
            | Medicamento.denominacion.ilike(f"%{busqueda}%")
            | Medicamento.especificaciones_tecnicas.ilike(f"%{busqueda}%")
            | Medicamento.unidad_medida.ilike(f"%{busqueda}%")
        )
        query = query.filter(filtro)
    pagination = query.paginate(page=page, per_page=PER_PAGE, error_out=False)
    return render_template("medicamentos/listar.html", pagination=pagination, medicamentos=pagination.items, busqueda=busqueda)


@medicamentos_bp.route("/create", methods=["GET", "POST"])
@personal_requerido
def guardar_medicamento():
    if request.method == "POST":
        datos = _datos_formulario_medicamento()

        if not datos["codigo"]:
            flash("El código del medicamento es obligatorio.", "danger")
            return render_template("medicamentos/form.html", medicamento=None)

        medicamento = Medicamento(**datos)
        db.session.add(medicamento)
        db.session.commit()

        flash("Medicamento registrado correctamente.", "success")
        return redirect(url_for("medicamentos.listar_medicamentos"))

    return render_template("medicamentos/form.html", medicamento=None)


@medicamentos_bp.route("/<int:medicamento_id>/ver")
@personal_requerido
def ver_medicamento(medicamento_id):
    medicamento = Medicamento.query.get_or_404(medicamento_id)
    return render_template("medicamentos/form.html", medicamento=medicamento, solo_lectura=True)


@medicamentos_bp.route("/<int:medicamento_id>/edit", methods=["GET", "POST"])
@personal_requerido
def actualizar_medicamento(medicamento_id):
    medicamento = Medicamento.query.get_or_404(medicamento_id)

    if request.method == "POST":
        datos = _datos_formulario_medicamento()

        if not datos["codigo"]:
            flash("El código del medicamento es obligatorio.", "danger")
            return render_template("medicamentos/form.html", medicamento=medicamento)

        for campo, valor in datos.items():
            setattr(medicamento, campo, valor)

        db.session.commit()

        flash("Medicamento actualizado correctamente.", "success")
        return redirect(url_for("medicamentos.listar_medicamentos"))

    return render_template("medicamentos/form.html", medicamento=medicamento)


@medicamentos_bp.route("/<int:medicamento_id>/delete", methods=["POST"])
@personal_requerido
def eliminar_medicamento(medicamento_id):
    medicamento = Medicamento.query.get_or_404(medicamento_id)

    en_prescripcion = db.session.execute(
        text("SELECT id FROM prescripciones WHERE medicamento_id = :id LIMIT 1"),
        {"id": medicamento_id},
    ).first()
    en_vacunacion = db.session.execute(
        text("SELECT id FROM vacunaciones WHERE medicamento_id = :id LIMIT 1"),
        {"id": medicamento_id},
    ).first()
    if en_prescripcion or en_vacunacion:
        flash("No se puede eliminar: el medicamento está asociado a prescripciones o vacunaciones.", "danger")
        return redirect(url_for("medicamentos.listar_medicamentos"))

    db.session.delete(medicamento)
    db.session.commit()

    flash("Medicamento eliminado correctamente.", "success")
    return redirect(url_for("medicamentos.listar_medicamentos"))