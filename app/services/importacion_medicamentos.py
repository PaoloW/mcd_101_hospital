import pandas as pd
import io
from typing import Any

from app.extensions import db
from app.models.medicamento import Medicamento


COLUMNAS_REQUERIDAS = ["codigo", "denominacion", "unidad_medida"]
COLUMNAS_OPCIONALES = ["especificaciones_tecnicas"]
COLUMNAS_ESPERADAS = COLUMNAS_REQUERIDAS + COLUMNAS_OPCIONALES


def _generar_plantilla_bytes() -> bytes:
    """Genera un archivo XLSX en memoria con las columnas esperadas y una fila de ejemplo."""
    df = pd.DataFrame(
        [
            {
                "codigo": "MED001",
                "denominacion": "Paracetamol 500 mg",
                "unidad_medida": "mg",
                "especificaciones_tecnicas": "TB",
            }
        ]
    )
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Medicamentos")
    buffer.seek(0)
    return buffer.getvalue()


def _validar_dataframe(df: pd.DataFrame) -> list[dict[str, Any]]:
    """
    Valida cada fila del DataFrame y devuelve una lista de diccionarios con:
      - fila: número de fila (1‑based, sin contar el encabezado)
      - datos: dict con los valores de la fila
      - observaciones: lista de strings con los problemas encontrados
    """
    invalidos: list[dict[str, Any]] = []

    # --- 1. Validar columnas faltantes ---
    columnas_presentes = [c.strip().lower() for c in df.columns]
    for col in COLUMNAS_REQUERIDAS:
        if col not in columnas_presentes:
            raise ValueError(
                f"Falta la columna obligatoria '{col}'. "
                f"Columnas esperadas: {', '.join(COLUMNAS_ESPERADAS)}"
            )

    # Normalizar nombres de columnas del DataFrame
    df_renamed = df.rename(columns=lambda c: c.strip().lower())

    # --- 2. Obtener datos existentes para detectar duplicados ---
    existentes = Medicamento.query.with_entities(
        Medicamento.codigo, Medicamento.denominacion, Medicamento.unidad_medida
    ).all()
    codigos_existentes = {r.codigo for r in existentes if r.codigo}

    # Para duplicados dentro del mismo archivo
    codigos_en_archivo: set[str] = set()
    denominaciones_en_archivo: set[str] = set()
    unidades_en_archivo: set[str] = set()

    for idx, row in df_renamed.iterrows():
        fila_num = idx + 2  # +1 por 0‑based, +1 por encabezado
        observaciones: list[str] = []

        codigo = str(row.get("codigo", "")).strip() if pd.notna(row.get("codigo")) else ""
        denominacion = str(row.get("denominacion", "")).strip() if pd.notna(row.get("denominacion")) else ""
        unidad = str(row.get("unidad_medida", "")).strip() if pd.notna(row.get("unidad_medida")) else ""

        # --- Validar campos obligatorios vacíos ---
        if not codigo:
            observaciones.append("Código vacío")
        if not denominacion:
            observaciones.append("Denominación vacía")
        if not unidad:
            observaciones.append("Unidad de medida vacía")

        # --- Validar duplicados contra BD ---
        if codigo and codigo in codigos_existentes:
            observaciones.append(f"Código '{codigo}' ya existe en la base de datos")

        # --- Validar duplicados dentro del mismo archivo ---
        if codigo and codigo in codigos_en_archivo:
            observaciones.append(f"Código '{codigo}' duplicado en el archivo (fila {fila_num})")
        if denominacion and denominacion in denominaciones_en_archivo:
            observaciones.append(f"Denominación '{denominacion}' duplicada en el archivo (fila {fila_num})")

        # Acumular para detectar duplicados intra‑archivo
        if codigo:
            codigos_en_archivo.add(codigo)
        if denominacion:
            denominaciones_en_archivo.add(denominacion)
        if unidad:
            unidades_en_archivo.add(unidad)

        datos = {
            "codigo": codigo,
            "denominacion": denominacion,
            "unidad_medida": unidad,
            "especificaciones_tecnicas": str(row.get("especificaciones_tecnicas", "")).strip()
            if pd.notna(row.get("especificaciones_tecnicas"))
            else "",
        }

        if observaciones:
            invalidos.append(
                {
                    "fila": fila_num,
                    "datos": datos,
                    "observaciones": observaciones,
                }
            )

    return invalidos


def importar_medicamentos_desde_xlsx(contenido: bytes) -> dict[str, Any]:
    """
    Lee un archivo XLSX, valida los datos y registra los medicamentos válidos.

    Retorna un dict con:
      - insertados: cantidad de registros insertados correctamente
      - invalidos: lista de dicts con fila, datos y observaciones
    """
    buffer = io.BytesIO(contenido)
    df = pd.read_excel(buffer, engine="openpyxl")

    if df.empty:
        return {"insertados": 0, "invalidos": []}

    invalidos = _validar_dataframe(df)

    # Filtrar filas válidas (las que NO están en invalidos)
    filas_invalidas = {inv["fila"] for inv in invalidos}
    # Las filas en el DataFrame original son 0‑based; la fila 1 del excel es fila 2 (encabezado = 1)
    # En _validar_dataframe usamos idx+2 como número de fila.
    # Para obtener las filas válidas, iteramos sobre el DataFrame y excluimos las inválidas.
    columnas_presentes = [c.strip().lower() for c in df.columns]
    df_renamed = df.rename(columns=lambda c: c.strip().lower())

    insertados = 0
    for idx, row in df_renamed.iterrows():
        fila_num = idx + 2
        if fila_num in filas_invalidas:
            continue

        codigo = str(row.get("codigo", "")).strip() if pd.notna(row.get("codigo")) else ""
        denominacion = str(row.get("denominacion", "")).strip() if pd.notna(row.get("denominacion")) else ""
        unidad = str(row.get("unidad_medida", "")).strip() if pd.notna(row.get("unidad_medida")) else ""
        especificaciones = str(row.get("especificaciones_tecnicas", "")).strip() if pd.notna(row.get("especificaciones_tecnicas")) else ""

        # Doble validación por si acaso
        if not codigo or not denominacion or not unidad:
            continue

        medicamento = Medicamento(
            codigo=codigo,
            denominacion=denominacion or None,
            unidad_medida=unidad or None,
            especificaciones_tecnicas=especificaciones or None,
        )
        db.session.add(medicamento)
        insertados += 1

    if insertados > 0:
        db.session.commit()

    return {
        "insertados": insertados,
        "invalidos": invalidos,
    }