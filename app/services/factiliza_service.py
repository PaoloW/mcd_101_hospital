import logging

import requests
from flask import current_app

logger = logging.getLogger(__name__)

FACTILIZA_BASE_URL = "https://api.factiliza.com/v1"


def consultar_dni(dni: str) -> dict | None:
    """Consulta los datos de una persona por DNI usando la API de Factiliza.

    Args:
        dni: Número de documento a consultar.

    Returns:
        Diccionario con los datos de la persona si la consulta fue exitosa,
        o None si ocurrió algún error.
    """
    token = current_app.config.get("FACTILIZA_TOKEN", "")
    if not token:
        logger.error("FACTILIZA_TOKEN no está configurado en el entorno.")
        return None

    url = f"{FACTILIZA_BASE_URL}/dni/info/{dni}"
    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.Timeout:
        logger.error("Timeout al consultar Factiliza para DNI %s", dni)
        return None
    except requests.exceptions.RequestException as e:
        logger.error("Error de conexión al consultar Factiliza para DNI %s: %s", dni, e)
        return None
    except ValueError as e:
        logger.error("Respuesta JSON inválida de Factiliza para DNI %s: %s", dni, e)
        return None

    if not data.get("success") or data.get("status") != 200:
        mensaje = data.get("message", "Error desconocido")
        logger.warning("Factiliza respondió con error para DNI %s: %s", dni, mensaje)
        return None

    info = data.get("data")
    if not info:
        logger.warning("Factiliza no devolvió datos para DNI %s", dni)
        return None

    return info


def mapear_datos_factiliza(info: dict) -> dict:
    """Mapea los datos de Factiliza al formato de la tabla Persona.

    Args:
        info: Diccionario con los datos devueltos por Factiliza.

    Returns:
        Diccionario con los campos mapeados para crear/actualizar una Persona.
    """
    return {
        "numero_documento": info.get("numero", ""),
        "nombres": info.get("nombres", "").strip() or None,
        "primer_apellido": info.get("apellido_paterno", "").strip() or None,
        "segundo_apellido": info.get("apellido_materno", "").strip() or None,
        "direccion": info.get("direccion_completa", "").strip() or None,
        # Factiliza puede devolver fecha_nacimiento en formato "YYYY-MM-DD" o vacío
        "fecha_nacimiento": info.get("fecha_nacimiento") or None,
        "sexo": info.get("sexo", "").strip().upper() or None,
    }