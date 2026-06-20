import io
import base64
from datetime import datetime, timedelta

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

from flask import Blueprint, render_template, request, session, flash, redirect, url_for
from sqlalchemy import func, case

from app.extensions import db
from app.models.diagnostico import Diagnostico
from app.models.enfermedad import Enfermedad
from app.models.atencion_medica import AtencionMedica
from app.models.persona import Persona
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