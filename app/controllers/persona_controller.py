from datetime import datetime

from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for

from app.controllers.auth_controller import personal_requerido
from app.extensions import db
from app.models.persona import Persona
from app.models.usuario import Usuario

personas_bp = Blueprint("personas", __name__, url_prefix="/personas")

PER_PAGE = 20


def _parsear_fecha(valor: str):
    if not valor:
        return None
    try:
        return datetime.strptime(valor, "%Y-%m-%d").date()
    except ValueError:
        return None


def _datos_formulario_persona():
    return {
        "numero_documento": request.form.get("numero_documento", "").strip(),
        "primer_apellido": request.form.get("primer_apellido", "").strip() or None,
        "segundo_apellido": request.form.get("segundo_apellido", "").strip() or None,
        "nombres": request.form.get("nombres", "").strip() or None,
        "fecha_nacimiento": _parsear_fecha(request.form.get("fecha_nacimiento", "")),
        "sexo": request.form.get("sexo", "").strip() or None,
        "direccion": request.form.get("direccion", "").strip() or None,
        "telefono": request.form.get("telefono", "").strip() or None,
        "correo": request.form.get("correo", "").strip() or None,
    }


@personas_bp.route("/")
@personal_requerido
def listar_personas():
    page = request.args.get("page", 1, type=int)
    query = Persona.query.order_by(Persona.id.desc())
    pagination = query.paginate(page=page, per_page=PER_PAGE, error_out=False)
    return render_template("personas/listar.html", pagination=pagination, personas=pagination.items)


@personas_bp.route("/create", methods=["GET", "POST"])
@personal_requerido
def guardar_persona():
    if request.method == "POST":
        datos = _datos_formulario_persona()

        if not datos["numero_documento"]:
            flash("El número de documento es obligatorio.", "danger")
            return render_template("personas/form.html", persona=None)

        if Persona.query.filter_by(numero_documento=datos["numero_documento"]).first():
            flash("Ya existe una persona con ese número de documento.", "danger")
            return render_template("personas/form.html", persona=None)

        persona = Persona(**datos)
        db.session.add(persona)
        db.session.commit()

        flash("Persona registrada correctamente.", "success")
        return redirect(url_for("personas.listar_personas"))

    return render_template("personas/form.html", persona=None)


@personas_bp.route("/<int:persona_id>/edit", methods=["GET", "POST"])
@personal_requerido
def actualizar_persona(persona_id):
    persona = Persona.query.get_or_404(persona_id)

    if request.method == "POST":
        datos = _datos_formulario_persona()

        if not datos["numero_documento"]:
            flash("El número de documento es obligatorio.", "danger")
            return render_template("personas/form.html", persona=persona)

        existente = Persona.query.filter(
            Persona.numero_documento == datos["numero_documento"],
            Persona.id != persona_id,
        ).first()
        if existente:
            flash("Ya existe otra persona con ese número de documento.", "danger")
            return render_template("personas/form.html", persona=persona)

        for campo, valor in datos.items():
            setattr(persona, campo, valor)

        db.session.commit()

        flash("Persona actualizada correctamente.", "success")
        return redirect(url_for("personas.listar_personas"))

    return render_template("personas/form.html", persona=persona)


@personas_bp.route("/<int:persona_id>/delete", methods=["POST"])
@personal_requerido
def eliminar_persona(persona_id):
    persona = Persona.query.get_or_404(persona_id)

    if Usuario.query.filter_by(persona_id=persona_id).first():
        flash("No se puede eliminar: la persona tiene usuarios asociados.", "danger")
        return redirect(url_for("personas.listar_personas"))

    db.session.delete(persona)
    db.session.commit()

    flash("Persona eliminada correctamente.", "success")
    return redirect(url_for("personas.listar_personas"))


@personas_bp.route("/buscar-documento")
@personal_requerido
def buscar_por_documento():
    documento = request.args.get("documento", "").strip()

    if not documento:
        return jsonify({"encontrado": False, "mensaje": "Ingrese un número de documento."}), 400

    persona = Persona.query.filter_by(numero_documento=documento).first()
    if persona is None:
        return jsonify(
            {"encontrado": False, "mensaje": "No se encontró una persona con ese documento."}
        )

    return jsonify(
        {
            "encontrado": True,
            "id": persona.id,
            "numero_documento": persona.numero_documento,
            "nombre_completo": persona.nombre_completo,
        }
    )