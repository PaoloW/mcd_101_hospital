import csv
import io
import base64
from datetime import datetime, timedelta

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

from flask import Blueprint, render_template, request, session, flash, redirect, url_for, Response
from sqlalchemy import func, case

from app.extensions import db
from app.models.diagnostico import Diagnostico
from app.models.enfermedad import Enfermedad
from app.models.atencion_medica import AtencionMedica
from app.models.analisis import Analisis
from app.models.prescripcion import Prescripcion
from app.models.procedimiento_realizado import ProcedimientoRealizado
from app.models.medicamento import Medicamento
from app.models.parametro import Parametro
from app.models.procedimiento import Procedimiento
from app.models.persona import Persona
from app.models.usuario import Usuario
from app.controllers.auth_controller import admin_requerido

reportes_bp = Blueprint("reportes", __name__, url_prefix="/reportes")

# Age group definitions: (label, min_age, max_age)
AGE_GROUPS = [
    ("0-12 (Niño)", 0, 12),
    ("13-17 (Adolescente)", 13, 17),
    ("18-25 (Joven)", 18, 25),
    ("26-40 (Adulto joven)", 26, 40),
    ("41-60 (Adulto)", 41, 60),
    ("60+ (Adulto mayor)", 60, 999),
]

AGE_GROUP_COLORS = [
    "#4e79a7",  # Azul
    "#f28e2b",  # Naranja
    "#e15759",  # Rojo
    "#76b7b2",  # Verde azulado
    "#59a14f",  # Verde
    "#edc948",  # Amarillo
]


def _calcular_edad(fecha_nacimiento, fecha_referencia):
    """Calcula la edad en años a partir de dos fechas."""
    if not fecha_nacimiento or not fecha_referencia:
        return None
    # Ajuste por mes/día
    edad = fecha_referencia.year - fecha_nacimiento.year
    if (fecha_referencia.month, fecha_referencia.day) < (
        fecha_nacimiento.month,
        fecha_nacimiento.day,
    ):
        edad -= 1
    return edad


def _obtener_grupo_etario(edad):
    """Devuelve el índice del grupo etario al que pertenece la edad."""
    for idx, (_, min_age, max_age) in enumerate(AGE_GROUPS):
        if min_age <= edad <= max_age:
            return idx
    return None

@reportes_bp.route("/masivos", methods=["GET", "POST"])
@admin_requerido
def reporte_masivos():
    """Vista del reporte masivo con descarga CSV."""
    today = datetime.now().date()
    default_start = today - timedelta(days=30)
    total = None
    tipo_reporte = ""
    documento = ""

    fecha_inicio = default_start
    fecha_fin = today

    if request.method == "POST":
        tipo_reporte = request.form.get("tipo_reporte", "")
        fecha_inicio_str = request.form.get("fecha_inicio", "")
        fecha_fin_str = request.form.get("fecha_fin", "")
        documento = request.form.get("documento", "").strip()

        try:
            fecha_inicio = datetime.strptime(fecha_inicio_str, "%Y-%m-%d").date() if fecha_inicio_str else default_start
            fecha_fin = datetime.strptime(fecha_fin_str, "%Y-%m-%d").date() if fecha_fin_str else today
        except (ValueError, TypeError):
            fecha_inicio = default_start
            fecha_fin = today

        if fecha_inicio > fecha_fin:
            fecha_inicio, fecha_fin = fecha_fin, fecha_inicio

        if not tipo_reporte:
            flash("Debe seleccionar un tipo de reporte.", "warning")
        else:
            return _generar_csv(tipo_reporte, fecha_inicio, fecha_fin, documento)

    return render_template(
        "reportes/masivos.html",
        fecha_inicio=fecha_inicio.strftime("%Y-%m-%d"),
        fecha_fin=fecha_fin.strftime("%Y-%m-%d"),
        documento=documento,
        tipo_reporte=tipo_reporte,
        total=total,
    )


def _generar_csv(tipo_reporte, fecha_inicio, fecha_fin, documento):
    """Genera y descarga un CSV con los datos filtrados."""
    output = io.StringIO()
    writer = csv.writer(output, delimiter=";")
    rows = []

    if tipo_reporte == "atencion":
        paciente_persona = db.aliased(Persona)
        responsable_persona = db.aliased(Persona)
        responsable_usuario = db.aliased(Usuario)

        writer.writerow([
            "ID Atención", "Fecha/Hora", "Paciente", "Documento Paciente",
            "Responsable", "Documento Responsable", "Observación"
        ])
        query = (
            db.session.query(
                AtencionMedica.id,
                AtencionMedica.fecha_hora,
                paciente_persona.nombre_completo.label("paciente_nombre"),
                paciente_persona.numero_documento.label("paciente_documento"),
                responsable_persona.nombre_completo.label("responsable_nombre"),
                responsable_persona.numero_documento.label("responsable_documento"),
                AtencionMedica.observacion,
            )
            .join(paciente_persona, AtencionMedica.paciente_id == paciente_persona.id)
            .join(responsable_usuario, AtencionMedica.responsable_id == responsable_usuario.id)
            .join(responsable_persona, responsable_usuario.persona_id == responsable_persona.id)
            .filter(AtencionMedica.fecha_hora.between(
                datetime.combine(fecha_inicio, datetime.min.time()),
                datetime.combine(fecha_fin, datetime.max.time()),
            ))
        )
        if documento:
            query = query.filter(
                db.or_(
                    paciente_persona.numero_documento.ilike(f"%{documento}%"),
                    responsable_persona.numero_documento.ilike(f"%{documento}%"),
                )
            )
        for row in query.all():
            writer.writerow([
                row.id,
                row.fecha_hora.strftime("%Y-%m-%d %H:%M") if row.fecha_hora else "",
                row.paciente_nombre,
                row.paciente_documento,
                row.responsable_nombre,
                row.responsable_documento,
                row.observacion or "",
            ])

    elif tipo_reporte == "analisis":
        paciente_persona = db.aliased(Persona)
        responsable_persona = db.aliased(Persona)
        responsable_usuario = db.aliased(Usuario)

        writer.writerow([
            "ID Análisis", "Fecha Muestra", "Fecha Análisis",
            "Paciente", "Documento Paciente",
            "Responsable", "Documento Responsable",
            "Parámetro", "Valor Resultado", "Observación"
        ])
        query = (
            db.session.query(
                Analisis.id,
                Analisis.fechahora_muestra,
                Analisis.fechahora_analisis,
                paciente_persona.nombre_completo.label("paciente_nombre"),
                paciente_persona.numero_documento.label("paciente_documento"),
                responsable_persona.nombre_completo.label("responsable_nombre"),
                responsable_persona.numero_documento.label("responsable_documento"),
                Parametro.nombre.label("parametro_nombre"),
                Analisis.valor_resultado,
                Analisis.observacion,
            )
            .join(AtencionMedica, Analisis.atencion_id == AtencionMedica.id)
            .join(paciente_persona, AtencionMedica.paciente_id == paciente_persona.id)
            .join(responsable_usuario, Analisis.responsable_id == responsable_usuario.id)
            .join(responsable_persona, responsable_usuario.persona_id == responsable_persona.id)
            .join(Parametro, Analisis.parametro_id == Parametro.id)
            .filter(Analisis.fechahora_analisis.between(
                datetime.combine(fecha_inicio, datetime.min.time()),
                datetime.combine(fecha_fin, datetime.max.time()),
            ))
        )
        if documento:
            query = query.filter(
                db.or_(
                    paciente_persona.numero_documento.ilike(f"%{documento}%"),
                    responsable_persona.numero_documento.ilike(f"%{documento}%"),
                )
            )
        for row in query.all():
            writer.writerow([
                row.id,
                row.fechahora_muestra.strftime("%Y-%m-%d %H:%M") if row.fechahora_muestra else "",
                row.fechahora_analisis.strftime("%Y-%m-%d %H:%M") if row.fechahora_analisis else "",
                row.paciente_nombre,
                row.paciente_documento,
                row.responsable_nombre,
                row.responsable_documento,
                row.parametro_nombre,
                str(row.valor_resultado) if row.valor_resultado is not None else "",
                row.observacion or "",
            ])

    elif tipo_reporte == "diagnosticos":
        paciente_persona = db.aliased(Persona)
        responsable_persona = db.aliased(Persona)
        responsable_usuario = db.aliased(Usuario)

        writer.writerow([
            "ID Diagnóstico", "Fecha", "Paciente", "Documento Paciente",
            "Responsable", "Documento Responsable",
            "Enfermedad", "Descripción"
        ])
        query = (
            db.session.query(
                Diagnostico.id,
                Diagnostico.fecha,
                paciente_persona.nombre_completo.label("paciente_nombre"),
                paciente_persona.numero_documento.label("paciente_documento"),
                responsable_persona.nombre_completo.label("responsable_nombre"),
                responsable_persona.numero_documento.label("responsable_documento"),
                Enfermedad.nombre.label("enfermedad_nombre"),
                Diagnostico.descripcion,
            )
            .join(AtencionMedica, Diagnostico.atencion_id == AtencionMedica.id)
            .join(paciente_persona, AtencionMedica.paciente_id == paciente_persona.id)
            .join(responsable_usuario, Diagnostico.responsable_id == responsable_usuario.id)
            .join(responsable_persona, responsable_usuario.persona_id == responsable_persona.id)
            .join(Enfermedad, Diagnostico.enfermedad_id == Enfermedad.id, isouter=True)
            .filter(Diagnostico.fecha.between(fecha_inicio, fecha_fin))
        )
        if documento:
            query = query.filter(
                db.or_(
                    paciente_persona.numero_documento.ilike(f"%{documento}%"),
                    responsable_persona.numero_documento.ilike(f"%{documento}%"),
                )
            )
        for row in query.all():
            writer.writerow([
                row.id,
                row.fecha.strftime("%Y-%m-%d") if row.fecha else "",
                row.paciente_nombre,
                row.paciente_documento,
                row.responsable_nombre,
                row.responsable_documento,
                row.enfermedad_nombre or "",
                row.descripcion or "",
            ])

    elif tipo_reporte == "procedimientos":
        paciente_persona = db.aliased(Persona)
        responsable_persona = db.aliased(Persona)
        responsable_usuario = db.aliased(Usuario)

        writer.writerow([
            "ID Procedimiento Realizado", "Fecha",
            "Paciente", "Documento Paciente",
            "Responsable", "Documento Responsable",
            "Procedimiento", "Código CPMS", "Observación"
        ])
        query = (
            db.session.query(
                ProcedimientoRealizado.id,
                ProcedimientoRealizado.fecha,
                paciente_persona.nombre_completo.label("paciente_nombre"),
                paciente_persona.numero_documento.label("paciente_documento"),
                responsable_persona.nombre_completo.label("responsable_nombre"),
                responsable_persona.numero_documento.label("responsable_documento"),
                Procedimiento.nombre.label("procedimiento_nombre"),
                Procedimiento.codigo_cpms,
                ProcedimientoRealizado.observacion,
            )
            .join(AtencionMedica, ProcedimientoRealizado.atencion_id == AtencionMedica.id)
            .join(paciente_persona, AtencionMedica.paciente_id == paciente_persona.id)
            .join(responsable_usuario, ProcedimientoRealizado.responsable_id == responsable_usuario.id)
            .join(responsable_persona, responsable_usuario.persona_id == responsable_persona.id)
            .join(Procedimiento, ProcedimientoRealizado.procedimiento_id == Procedimiento.id)
            .filter(ProcedimientoRealizado.fecha.between(fecha_inicio, fecha_fin))
        )
        if documento:
            query = query.filter(
                db.or_(
                    paciente_persona.numero_documento.ilike(f"%{documento}%"),
                    responsable_persona.numero_documento.ilike(f"%{documento}%"),
                )
            )
        for row in query.all():
            writer.writerow([
                row.id,
                row.fecha.strftime("%Y-%m-%d") if row.fecha else "",
                row.paciente_nombre,
                row.paciente_documento,
                row.responsable_nombre,
                row.responsable_documento,
                row.procedimiento_nombre,
                row.codigo_cpms or "",
                row.observacion or "",
            ])

    elif tipo_reporte == "prescripciones":
        paciente_persona = db.aliased(Persona)
        responsable_persona = db.aliased(Persona)
        responsable_usuario = db.aliased(Usuario)

        writer.writerow([
            "ID Prescripción", "Fecha",
            "Paciente", "Documento Paciente",
            "Responsable", "Documento Responsable",
            "Medicamento", "Dosis", "Cantidad"
        ])
        query = (
            db.session.query(
                Prescripcion.id,
                Prescripcion.fecha,
                paciente_persona.nombre_completo.label("paciente_nombre"),
                paciente_persona.numero_documento.label("paciente_documento"),
                responsable_persona.nombre_completo.label("responsable_nombre"),
                responsable_persona.numero_documento.label("responsable_documento"),
                Medicamento.denominacion.label("medicamento_nombre"),
                Prescripcion.dosis,
                Prescripcion.cantidad,
            )
            .join(AtencionMedica, Prescripcion.atencion_id == AtencionMedica.id)
            .join(paciente_persona, AtencionMedica.paciente_id == paciente_persona.id)
            .join(responsable_usuario, Prescripcion.responsable_id == responsable_usuario.id)
            .join(responsable_persona, responsable_usuario.persona_id == responsable_persona.id)
            .join(Medicamento, Prescripcion.medicamento_id == Medicamento.id)
            .filter(Prescripcion.fecha.between(fecha_inicio, fecha_fin))
        )
        if documento:
            query = query.filter(
                db.or_(
                    paciente_persona.numero_documento.ilike(f"%{documento}%"),
                    responsable_persona.numero_documento.ilike(f"%{documento}%"),
                )
            )
        for row in query.all():
            writer.writerow([
                row.id,
                row.fecha.strftime("%Y-%m-%d") if row.fecha else "",
                row.paciente_nombre,
                row.paciente_documento,
                row.responsable_nombre,
                row.responsable_documento,
                row.medicamento_nombre,
                row.dosis or "",
                str(row.cantidad) if row.cantidad is not None else "",
            ])

    else:
        flash("Tipo de reporte no válido.", "danger")
        return redirect(url_for("reportes.reporte_masivos"))

    csv_content = output.getvalue()
    output.close()

    filename = f"reporte_{tipo_reporte}_{fecha_inicio.strftime('%Y%m%d')}_{fecha_fin.strftime('%Y%m%d')}.csv"
    return Response(
        csv_content,
        mimetype="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Type": "text/csv; charset=utf-8-sig",
        },
    )


@reportes_bp.route("/diagnosticos", methods=["GET", "POST"])
@admin_requerido
def reporte_diagnosticos():
    """Vista del reporte de diagnósticos con filtro por rango de fechas."""
    today = datetime.now().date()
    default_start = today - timedelta(days=30)

    if request.method == "POST":
        fecha_inicio_str = request.form.get("fecha_inicio", "")
        fecha_fin_str = request.form.get("fecha_fin", "")
        try:
            fecha_inicio = datetime.strptime(fecha_inicio_str, "%Y-%m-%d").date() if fecha_inicio_str else default_start
            fecha_fin = datetime.strptime(fecha_fin_str, "%Y-%m-%d").date() if fecha_fin_str else today
        except (ValueError, TypeError):
            fecha_inicio = default_start
            fecha_fin = today
    else:
        fecha_inicio = default_start
        fecha_fin = today

    # Ensure fecha_inicio <= fecha_fin
    if fecha_inicio > fecha_fin:
        fecha_inicio, fecha_fin = fecha_fin, fecha_inicio

    # ─── 1. Get top 10 enfermedades by diagnostic count in date range ───
    top_enfermedades = (
        db.session.query(
            Diagnostico.enfermedad_id,
            func.count(Diagnostico.id).label("total"),
        )
        .filter(Diagnostico.fecha.between(fecha_inicio, fecha_fin))
        .filter(Diagnostico.enfermedad_id.isnot(None))
        .group_by(Diagnostico.enfermedad_id)
        .order_by(func.count(Diagnostico.id).desc())
        .limit(10)
        .all()
    )

    if not top_enfermedades:
        chart_b64 = None
        return render_template(
            "reportes/diagnosticos.html",
            chart_b64=chart_b64,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
        )

    top_enfermedad_ids = [e.enfermedad_id for e in top_enfermedades]

    # Map enfermedad_id -> nombre
    enfermedades_map = {
        e.id: e.nombre
        for e in Enfermedad.query.filter(Enfermedad.id.in_(top_enfermedad_ids)).all()
    }

    # ─── 2. Query diagnósticos with join → atencion → persona → fecha_nacimiento ───
    rows = (
        db.session.query(
            Diagnostico.enfermedad_id,
            Persona.fecha_nacimiento,
            Diagnostico.fecha,
        )
        .join(AtencionMedica, Diagnostico.atencion_id == AtencionMedica.id)
        .join(Persona, AtencionMedica.paciente_id == Persona.id)
        .filter(Diagnostico.fecha.between(fecha_inicio, fecha_fin))
        .filter(Diagnostico.enfermedad_id.in_(top_enfermedad_ids))
        .all()
    )

    # ─── 3. Build matrix: [enfermedad_idx][age_group_idx] = count ───
    n_enfermedades = len(top_enfermedad_ids)
    n_grupos = len(AGE_GROUPS)
    data_matrix = np.zeros((n_enfermedades, n_grupos), dtype=int)

    enfermedad_index_map = {eid: idx for idx, eid in enumerate(top_enfermedad_ids)}

    for enfermedad_id, fecha_nacimiento, fecha_diag in rows:
        edad = _calcular_edad(fecha_nacimiento, fecha_diag)
        if edad is None:
            continue
        grupo_idx = _obtener_grupo_etario(edad)
        if grupo_idx is None:
            continue
        enf_idx = enfermedad_index_map.get(enfermedad_id)
        if enf_idx is None:
            continue
        data_matrix[enf_idx, grupo_idx] += 1

    # ─── 4. Build sorted labels ───
    enfermedad_labels = [
        enfermedades_map.get(eid, f"ID {eid}")[:40]
        for eid in top_enfermedad_ids
    ]
    age_group_labels = [label for label, _, _ in AGE_GROUPS]

    # ─── 5. Generate stacked bar chart ───
    fig, ax = plt.subplots(figsize=(14, 7))

    x = np.arange(n_enfermedades)
    bar_width = 0.55
    bottom = np.zeros(n_enfermedades, dtype=int)

    for g_idx in range(n_grupos):
        counts = data_matrix[:, g_idx]
        bars = ax.bar(
            x,
            counts,
            bar_width,
            bottom=bottom,
            label=age_group_labels[g_idx],
            color=AGE_GROUP_COLORS[g_idx],
            edgecolor="white",
            linewidth=0.5,
        )
        # Add count labels on each segment if > 0
        for xi, (count, b) in enumerate(zip(counts, bottom)):
            if count > 0:
                ax.text(
                    xi,
                    b + count / 2,
                    str(int(count)),
                    ha="center",
                    va="center",
                    fontsize=7,
                    fontweight="bold",
                    color="white",
                )
        bottom += counts

    ax.set_xlabel("Diagnósticos más frecuentes", fontsize=12)
    ax.set_ylabel("Cantidad de diagnósticos por grupo etario", fontsize=12)
    ax.set_title(
        f"Top 10 diagnósticos más frecuentes\n"
        f"({fecha_inicio.strftime('%d/%m/%Y')} - {fecha_fin.strftime('%d/%m/%Y')})",
        fontsize=14,
        fontweight="bold",
    )
    ax.set_xticks(x)
    ax.set_xticklabels(enfermedad_labels, rotation=30, ha="right", fontsize=9)
    ax.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))
    ax.legend(
        title="Grupo etario",
        loc="upper right",
        fontsize=9,
        title_fontsize=10,
    )
    ax.set_axisbelow(True)
    ax.grid(axis="y", alpha=0.4)
    fig.tight_layout()

    # ─── 6. Convert to base64 for inline display ───
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=120)
    buf.seek(0)
    chart_b64 = base64.b64encode(buf.read()).decode("utf-8")
    plt.close(fig)

    return render_template(
        "reportes/diagnosticos.html",
        chart_b64=chart_b64,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
    )